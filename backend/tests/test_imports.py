"""Import use case with actual images, files, SQLite and commit failures."""
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from uuid import uuid4

import numpy as np
from PIL import Image
import pytest
from sqlalchemy import event, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.processing.normalize import ImageValidationError, encode_normalized_png, normalize_image
from app.services.imports import PageLimitError, import_page
from app.services.sessions import SessionNotFoundError, get_document
from app.storage.database import initialize_database, open_database
from app.storage.files import ArtifactStore
from app.storage.models import Artifact, PageConfigRecord, ScanPage, ScanSession
from app.storage.repository import create_session, transaction

FIXTURES = Path(__file__).resolve().parents[2]/'fixtures'


@pytest.fixture
def context(tmp_path):
    engine = open_database(tmp_path/'data/scanner.sqlite3')
    initialize_database(engine)
    store = ArtifactStore(tmp_path/'data')
    with transaction(engine) as db:
        sid = create_session(db).id
    yield engine,store,sid
    engine.dispose()


@pytest.mark.parametrize('name',['exif_6.jpg','alpha_rgba.png','png_named_jpeg.jpg'])
def test_import_preserves_bytes_source_pixels_config_and_reopens(context,name):
    engine,store,sid = context
    payload = (FIXTURES/name).read_bytes()
    expected = normalize_image(payload)
    encoded = encode_normalized_png(expected)
    page = import_page(engine,store,sid,payload)
    assert (page.width,page.height)==(encoded.width,encoded.height)
    assert page.position==0 and page.revision==0 and page.render_revision is None
    assert not page.effective_config.confirmed and page.effective_config.corners is None
    with transaction(engine) as db:
        artifacts = {a.kind:a for a in db.scalars(select(Artifact)).all()}
        assert len(artifacts)==3 and all(a.page_id==page.id and a.session_id==sid for a in artifacts.values())
        for a in artifacts.values():
            saved = (store.root/a.path).read_bytes()
            assert len(saved)==a.byte_size and sha256(saved).hexdigest()==a.sha256
        assert (store.root/artifacts['original'].path).read_bytes()==payload
        assert artifacts['original'].mime==('image/jpeg' if payload.startswith(b'\xff\xd8') else 'image/png')
        assert (store.root/artifacts['normalized'].path).read_bytes()==encoded.png_bytes
        with Image.open(store.root/artifacts['normalized'].path) as image:
            assert image.mode=='RGB' and not image.getexif()
            assert np.array_equal(np.asarray(image)[:,:,::-1],expected)
        assert max(artifacts['thumbnail'].width,artifacts['thumbnail'].height)<=320
        assert db.get(PageConfigRecord,page.id).revision==0
        session = db.get(ScanSession,sid)
        assert session.updated_at>session.created_at
    engine.dispose()
    assert get_document(engine,sid).pages==(page,)


@pytest.mark.parametrize('failure',['encode','second_write','commit'])
def test_import_failure_keeps_old_page_and_cleans_only_new_files(context,monkeypatch,failure):
    engine,store,sid = context
    payload = (FIXTURES/'corners_rgb.png').read_bytes()
    old = import_page(engine,store,sid,payload)
    before = {p:sha256(p.read_bytes()).hexdigest() for p in (store.root/'sessions').rglob('*') if p.is_file()}
    if failure=='encode':
        def fail(*args):
            raise OSError('controlled encoder failure')
        monkeypatch.setattr('app.services.imports.encode_stage_png',fail)
    elif failure=='second_write':
        original = store.write_bytes
        def fail(**kwargs):
            if kwargs['kind']=='normalized':
                raise OSError('controlled disk failure')
            return original(**kwargs)
        monkeypatch.setattr(store,'write_bytes',fail)
    else:
        # Mark actual flushes so read-only precheck/cleanup can still commit.
        def mark(db,flush_context):
            db.info['import_wrote'] = True
        def fail(db):
            if db.info.get('import_wrote'):
                raise OperationalError('controlled commit fault',{},Exception('private'))
        event.listen(Session,'after_flush',mark)
        event.listen(Session,'before_commit',fail)
    try:
        with pytest.raises((OSError,OperationalError)):
            import_page(engine,store,sid,payload)
    finally:
        if failure=='commit':
            event.remove(Session,'after_flush',mark)
            event.remove(Session,'before_commit',fail)
    after = {p:sha256(p.read_bytes()).hexdigest() for p in (store.root/'sessions').rglob('*') if p.is_file()}
    assert after==before and get_document(engine,sid).pages==(old,)
    with transaction(engine) as db:
        assert len(db.scalars(select(Artifact)).all())==3
        assert len(db.scalars(select(PageConfigRecord)).all())==1


@pytest.mark.parametrize('name',['fake.jpg','truncated.png','too_narrow.png'])
def test_invalid_image_never_creates_page_or_artifact(context,name):
    engine,store,sid = context
    with pytest.raises(ImageValidationError):
        import_page(engine,store,sid,(FIXTURES/name).read_bytes())
    assert get_document(engine,sid).pages==()
    assert not (store.root/'sessions').exists()


def test_missing_session_rejected_before_file_write(context):
    engine,store,sid = context
    with pytest.raises(SessionNotFoundError):
        import_page(engine,store,uuid4(),(FIXTURES/'corners_rgb.png').read_bytes())
    assert not (store.root/'sessions').exists()


def test_order_and_page_limit_checked_in_import_transaction(context):
    engine,store,sid = context
    payload = (FIXTURES/'minimum.png').read_bytes()
    pages = [import_page(engine,store,sid,payload) for _ in range(20)]
    assert [p.position for p in pages]==list(range(20))
    with pytest.raises(PageLimitError):
        import_page(engine,store,sid,payload)
    assert len(get_document(engine,sid).pages)==20
    assert len([p for p in (store.root/'sessions').rglob('*') if p.is_file()])==60


def test_skinny_valid_source_can_have_one_pixel_thumbnail(context):
    engine,store,sid = context
    stream = BytesIO()
    Image.new('RGB',(2,2000),'white').save(stream,format='PNG')
    page = import_page(engine,store,sid,stream.getvalue())
    with transaction(engine) as db:
        thumbnail = db.get(Artifact,page.thumbnail_artifact_id)
        assert (thumbnail.width,thumbnail.height)==(1,320)


def test_session_deleted_after_file_writes_cleans_new_files(context,monkeypatch):
    engine,store,sid = context
    original = store.write_bytes
    def write_then_delete(**kwargs):
        result = original(**kwargs)
        if kwargs['kind']=='thumbnail':
            with transaction(engine) as db:
                db.delete(db.get(ScanSession,sid))
        return result
    monkeypatch.setattr(store,'write_bytes',write_then_delete)
    with pytest.raises(SessionNotFoundError):
        import_page(engine,store,sid,(FIXTURES/'minimum.png').read_bytes())
    assert not any(p.is_file() for p in (store.root/'sessions').rglob('*'))
    with transaction(engine) as db:
        assert db.scalars(select(Artifact)).all()==[] and db.scalars(select(ScanPage)).all()==[]


def test_two_imports_competing_for_last_slot_commit_only_one_and_clean_loser(context,monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    engine,store,sid = context
    payload = (FIXTURES/'minimum.png').read_bytes()
    for _ in range(19):
        import_page(engine,store,sid,payload)
    original = store.write_bytes
    ready = Barrier(2)
    def synchronize(**kwargs):
        result = original(**kwargs)
        if kwargs['kind']=='thumbnail':
            ready.wait(timeout=5)
        return result
    monkeypatch.setattr(store,'write_bytes',synchronize)
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(import_page,engine,store,sid,payload) for _ in range(2)]
        winners,losers = [],[]
        for future in futures:
            try:
                winners.append(future.result(timeout=10))
            except PageLimitError as error:
                losers.append(error)
    assert len(winners)==len(losers)==1 and winners[0].position==19
    assert len(get_document(engine,sid).pages)==20
    assert len([p for p in (store.root/'sessions').rglob('*') if p.is_file()])==60
