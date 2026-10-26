"""Atomic file completion and DB registration, not the import use case."""
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.storage.database import initialize_database, open_database
from app.storage.files import ArtifactFileError, ArtifactStore
from app.storage.models import Artifact
from app.storage.repository import create_session, discard_unreferenced, register_artifact, transaction


def write(store, sid=None, **changes):
    return store.write_bytes(**({'session_id':sid or uuid4(),'page_id':None,'kind':'pdf',
        'mime':'application/pdf','payload':b'%PDF-synthetic-completed-payload'}|changes))


def test_file_is_completed_before_registration_and_never_reencoded(tmp_path):
    store = ArtifactStore(tmp_path/'data')
    from app.processing.normalize import encode_normalized_png, normalize_image
    fixture = Path(__file__).resolve().parents[2]/'fixtures/exif_6.jpg'
    normalized = encode_normalized_png(normalize_image(fixture.read_bytes()))
    stored = write(store,page_id=uuid4(),kind='normalized',mime='image/png',payload=normalized.png_bytes,
        width=normalized.width,height=normalized.height)
    path = store.path_for(stored)
    assert path.read_bytes()==normalized.png_bytes
    assert stored.sha256==normalized.sha256==sha256(path.read_bytes()).hexdigest()
    assert stored.byte_size==len(normalized.png_bytes)
    assert str(stored.id) in path.name and path.suffix=='.png'
    assert path.is_relative_to(store.root) and not list(store.root.rglob('*.tmp'))


@pytest.mark.parametrize('failure',['write','fsync','rename'])
def test_io_failure_preserves_old_file_removes_only_new_temp_and_registers_nothing(tmp_path,monkeypatch,failure):
    import app.storage.files as module
    store = ArtifactStore(tmp_path/'data')
    old = write(store)
    before = store.path_for(old).read_bytes()
    if failure=='write':
        from contextlib import contextmanager
        from types import SimpleNamespace
        original = module.os.fdopen
        @contextmanager
        def partial(fd,mode):
            with original(fd,mode) as stream:
                def fail(payload):
                    stream.write(payload[:8])
                    raise OSError('controlled partial write')
                yield SimpleNamespace(write=fail)
        monkeypatch.setattr(module.os,'fdopen',partial)
    elif failure=='fsync':
        def fail(fd):
            raise OSError('controlled flush/fsync failure')
        monkeypatch.setattr(module.os,'fsync',fail)
    else:
        def fail(*args):
            raise OSError('controlled rename failure')
        monkeypatch.setattr(module,'_publish',fail)
    with pytest.raises(ArtifactFileError):
        write(store,old.session_id)
    assert store.path_for(old).read_bytes()==before
    assert [p for p in store.root.rglob('*') if p.is_file()]==[store.path_for(old)]


def test_uuid_collision_cannot_replace_existing_artifact(tmp_path,monkeypatch):
    import app.storage.files as module
    store = ArtifactStore(tmp_path)
    old = write(store)
    monkeypatch.setattr(module,'uuid4',lambda:old.id)
    with pytest.raises(ArtifactFileError):
        write(store,old.session_id,payload=b'new')
    assert store.path_for(old).read_bytes()==b'%PDF-synthetic-completed-payload'


@pytest.mark.parametrize('change',[{'session_id':'../../outside'},{'kind':'../original'},
    {'mime':'text/html'},{'payload':b''},{'payload':bytearray(b'x')},
    {'page_id':uuid4()},{'revision':0},{'width':2,'height':None}])
def test_unsafe_or_inconsistent_write_request_fails_before_creating_files(tmp_path,change):
    store = ArtifactStore(tmp_path/'data')
    with pytest.raises(ArtifactFileError):
        write(store,**change)
    assert not list(store.root.rglob('*'))


def test_internal_encoded_payload_has_no_upload_byte_quota(tmp_path):
    store = ArtifactStore(tmp_path)
    payload = b'x'*(15*1024*1024+1)
    result = write(store,payload=payload)
    assert store.path_for(result).stat().st_size==len(payload)


def test_registration_verifies_complete_file_and_cleanup_respects_db_references(tmp_path):
    store = ArtifactStore(tmp_path/'data')
    engine = open_database(tmp_path/'data/scanner.sqlite3')
    initialize_database(engine)
    with transaction(engine) as db:
        sid = create_session(db).id
    stored = write(store,sid)
    with transaction(engine) as db:
        artifact = register_artifact(db,store,stored)
        assert artifact.id==stored.id and artifact.path==stored.path
    with transaction(engine) as db:
        assert discard_unreferenced(db,store,stored) is False
    assert store.path_for(stored).exists()
    orphan = write(store,sid)
    with transaction(engine) as db:
        assert discard_unreferenced(db,store,orphan) is True
    assert not store.path_for(orphan).exists()
    with pytest.raises(ArtifactFileError):
        with transaction(engine) as db:
            register_artifact(db,store,orphan)
    with pytest.raises(ArtifactFileError):
        store.path_for(replace(stored,path='../elsewhere'))
    with transaction(engine) as db:
        assert len(db.scalars(select(Artifact)).all())==1
    engine.dispose()


def test_failed_metadata_commit_can_cleanup_only_the_new_unreferenced_file(tmp_path):
    store = ArtifactStore(tmp_path/'data')
    engine = open_database(tmp_path/'metadata.sqlite3')
    initialize_database(engine)
    stored = write(store)  # unknown session makes the FK fail
    with pytest.raises(IntegrityError):
        with transaction(engine) as db:
            register_artifact(db,store,stored)
    with transaction(engine) as db:
        assert db.scalars(select(Artifact)).all()==[]
        assert discard_unreferenced(db,store,stored)
    assert not store.path_for(stored).exists()
    engine.dispose()


def test_changed_file_is_not_registered_or_deleted_by_a_stale_descriptor(tmp_path):
    store = ArtifactStore(tmp_path)
    stored = write(store)
    store.path_for(stored).write_bytes(b'changed independently')
    with pytest.raises(ArtifactFileError):
        store.verify(stored)
    with pytest.raises(ArtifactFileError):
        store._discard(stored)
    assert store.path_for(stored).read_bytes()==b'changed independently'


@pytest.mark.parametrize('inside',[False,True],ids=['outside-root','inside-root'])
def test_junction_or_symlink_cannot_redirect_writes(tmp_path,inside):
    import os
    import subprocess
    store = ArtifactStore(tmp_path/'data')
    sid = uuid4()
    outside = (store.root if inside else tmp_path)/'outside'
    outside.mkdir()
    marker = outside/'keep.txt'
    marker.write_text('keep')
    (store.root/'sessions').mkdir()
    link = store.root/'sessions'/str(sid)
    if os.name=='nt':
        # Native junctions don't need the symlink privilege on Windows.
        quote = lambda p: "'"+str(p).replace("'","''")+"'"
        subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',
            f'New-Item -ItemType Junction -Path {quote(link)} -Target {quote(outside)} -ErrorAction Stop | Out-Null'],
            check=True,capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        link.symlink_to(outside,target_is_directory=True)
    with pytest.raises(ArtifactFileError):
        write(store,sid)
    assert marker.read_text()=='keep' and list(outside.iterdir())==[marker]
