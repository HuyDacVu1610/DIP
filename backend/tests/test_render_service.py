"""Real source -> full/preview files, stale snapshots and failure cleanup."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import fields
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from threading import Event

import numpy as np
from PIL import Image
import pytest
from sqlalchemy import delete, event, select

from app.processing.normalize import normalize_image
from app.processing.render import render_document, encode_render_images
from app.schemas.pages import ConfigUpdateRequest
from app.services.imports import import_page
from app.services.page_config import update_page_config, RevisionConflictError, PageNotFoundError
from app.services.sessions import create_document, get_document, SessionDataError, SessionNotFoundError
from app.schemas.sessions import SessionCreate
from app.storage.database import open_database, initialize_database
from app.storage.files import ArtifactStore, StoredArtifact, ArtifactFileError
from app.storage.models import Artifact, ScanPage, ScanSession
from app.storage import repository
from app.services import renders

FIXTURES = Path(__file__).resolve().parents[2]/'fixtures'
QUAD = [[0.,0.],[1.,0.],[1.,1.],[0.,1.]]


@pytest.fixture
def setup(tmp_path):
    engine = open_database(tmp_path/'data/scanner.sqlite3')
    initialize_database(engine)
    store = ArtifactStore(tmp_path/'data/artifacts')
    sid = create_document(engine,SessionCreate(title='Render snapshot')).id
    payload = (FIXTURES/'exif_6.jpg').read_bytes()
    page = import_page(engine,store,sid,payload)
    yield engine,store,sid,page,payload
    engine.dispose()


def confirm(setup,**overrides):
    engine,store,sid,page,_ = setup
    current = get_document(engine,sid).pages[0]
    config = {'corners':QUAD,'confirmed':True}|overrides
    return update_page_config(engine,sid,page.id,ConfigUpdateRequest(
        expected_revision=current.revision,config=config))


def files(store):
    return {str(p.relative_to(store.root)):p.read_bytes() for p in store.root.rglob('*') if p.is_file()}


def descriptor(engine,sid,aid):
    with repository.transaction(engine) as db:
        record = repository.get_artifact(db,sid,aid)
        return StoredArtifact(**{f.name:getattr(record,f.name) for f in fields(StoredArtifact)})


@pytest.mark.parametrize('mode,rotation',[('color',0),('gray',90),('bw',270)])
def test_render_exact_pixels_metadata_and_preview_from_full(setup,mode,rotation):
    engine,store,sid,page,payload = setup
    saved = confirm(setup,mode=mode,rotation=rotation,threshold={'method':'otsu'})
    before = get_document(engine,sid)
    sources = files(store)
    result = renders.render_page(engine,store,sid,page.id,saved.revision)
    assert result.revision==1 and result.page_id==page.id
    assert result.warnings==() and all(t>=0 for t in result.timings_ms.values())
    oracle = render_document(normalize_image(payload),saved.effective_config)
    encoded = encode_render_images(oracle.enhancement.image)
    assert (result.width,result.height)==(encoded.full.width,encoded.full.height)
    for aid,kind,raster in ((result.render_artifact_id,'render',encoded.full),
                            (result.preview_artifact_id,'preview',encoded.preview)):
        stored = descriptor(engine,sid,aid)
        assert (stored.page_id,stored.revision,stored.kind)==(page.id,1,kind)
        assert store.verify(stored).read_bytes()==raster.png_bytes
        assert (stored.width,stored.height,stored.sha256)==(raster.width,raster.height,raster.sha256)
    after = get_document(engine,sid)
    assert after.pages[0].render_revision==1
    assert after.pages[0].effective_config==before.pages[0].effective_config
    assert after.pages[0].revision==1
    for path,blob in sources.items():
        assert (store.root/path).read_bytes()==blob
    # A second run starts from source, not a previous enhanced render.
    again = renders.render_page(engine,store,sid,page.id,1)
    assert again.render_artifact_id!=result.render_artifact_id
    assert store.verify(descriptor(engine,sid,again.render_artifact_id)).read_bytes()==encoded.full.png_bytes


def test_unconfirmed_and_stale_rejected_before_processing(setup,monkeypatch):
    engine,store,sid,page,_ = setup
    def forbidden(*args,**kwargs):
        pytest.fail('Unconfirmed/stale config must not enter the offline detector/render')
    monkeypatch.setattr(renders,'render_document',forbidden)
    before = files(store)
    with pytest.raises(renders.PageNotConfirmedError):
        renders.render_page(engine,store,sid,page.id,0)
    confirm(setup)
    with pytest.raises(RevisionConflictError):
        renders.render_page(engine,store,sid,page.id,0)
    assert files(store)==before


@pytest.mark.parametrize('mutation',['config','page','session'])
@pytest.mark.parametrize('debug',[False,True])
def test_change_during_processing_cannot_publish(setup,monkeypatch,mutation,debug):
    engine,store,sid,page,_ = setup
    confirm(setup)
    before = files(store)
    started,release = Event(),Event()
    original = renders.render_document
    def blocked(*args,**kwargs):
        started.set()
        assert release.wait(10)
        return original(*args,**kwargs)
    monkeypatch.setattr(renders,'render_document',blocked)
    def forbidden_write(**kwargs):
        pytest.fail('Stale result must be rejected before file publication')
    monkeypatch.setattr(store,'write_bytes',forbidden_write)
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(renders.render_page,engine,store,sid,page.id,1,debug)
        try:
            assert started.wait(10)
            if mutation=='config':
                confirm(setup,rotation=90)
                expected = RevisionConflictError
            else:
                with repository.transaction(engine) as db:
                    model,ident = (ScanPage,page.id) if mutation=='page' else (ScanSession,sid)
                    db.execute(delete(model).where(model.id==ident))
                expected = PageNotFoundError if mutation=='page' else SessionNotFoundError
        finally:
            release.set()
        with pytest.raises(expected):
            future.result(timeout=15)
    assert files(store)==before
    if mutation=='config':
        current = get_document(engine,sid).pages[0]
        assert current.revision==2 and current.render_revision is None


@pytest.mark.parametrize('fault',['process','encode','second_write','register','commit'])
def test_failure_keeps_source_config_and_existing_render(setup,monkeypatch,fault):
    engine,store,sid,page,_ = setup
    confirm(setup)
    renders.render_page(engine,store,sid,page.id,1)
    before_files = files(store)
    before_document = get_document(engine,sid)
    def fail(*args,**kwargs):
        raise RuntimeError('injected fault')
    if fault=='process':
        monkeypatch.setattr(renders,'render_document',fail)
    elif fault=='encode':
        monkeypatch.setattr(renders,'encode_render_images',fail)
    elif fault=='second_write':
        original = store.write_bytes
        calls = 0
        def second(**kwargs):
            nonlocal calls
            calls += 1
            return fail() if calls==2 else original(**kwargs)
        monkeypatch.setattr(store,'write_bytes',second)
    elif fault=='register':
        monkeypatch.setattr(repository,'register_artifact',fail)
    else:
        # Only fail the write transaction; snapshot reads and cleanup can commit.
        def commit_fault(conn):
            if conn.info.pop('render_write',False):
                raise RuntimeError('injected fault')
        original = repository.register_artifact
        def mark(db,*args):
            db.connection().info['render_write'] = True
            return original(db,*args)
        monkeypatch.setattr(repository,'register_artifact',mark)
        event.listen(engine,'commit',commit_fault)
    try:
        with pytest.raises((RuntimeError,renders.RenderProcessingError)):
            renders.render_page(engine,store,sid,page.id,1)
    finally:
        if fault=='commit':
            event.remove(engine,'commit',commit_fault)
    assert files(store)==before_files
    assert get_document(engine,sid)==before_document
    with repository.transaction(engine) as db:
        assert len(db.scalars(select(Artifact)).all())==5


def test_old_render_remains_stale_after_config_update(setup):
    engine,store,sid,page,_ = setup
    confirm(setup)
    old = renders.render_page(engine,store,sid,page.id,1)
    confirm(setup,rotation=90)
    current = get_document(engine,sid).pages[0]
    assert (current.revision,current.render_revision)==(2,1)
    assert store.verify(descriptor(engine,sid,old.render_artifact_id)).is_file()
    renders.render_page(engine,store,sid,page.id,2)
    assert get_document(engine,sid).pages[0].render_revision==2


def test_tampered_source_cannot_render(setup):
    engine,store,sid,page,_ = setup
    confirm(setup)
    source = descriptor(engine,sid,page.normalized_artifact_id)
    store.path_for(source).write_bytes(b'corrupt')
    before = files(store)
    with pytest.raises(ArtifactFileError):
        renders.render_page(engine,store,sid,page.id,1)
    assert files(store)==before
    assert get_document(engine,sid).pages[0].render_revision is None


@pytest.mark.parametrize('fault',['dimensions','mode','exif','decode'])
def test_invalid_internal_png_rejected_even_with_matching_hash(setup,fault):
    engine,store,sid,page,_ = setup
    confirm(setup)
    source = descriptor(engine,sid,page.normalized_artifact_id)
    stream = BytesIO()
    size = (page.width+1,page.height) if fault=='dimensions' else (page.width,page.height)
    with Image.new('L' if fault=='mode' else 'RGB',size) as im:
        options = {}
        if fault=='exif':
            exif = Image.Exif()
            exif[274] = 6
            options['exif'] = exif
        im.save(stream,format='PNG',**options)
    blob = b'not a PNG' if fault=='decode' else stream.getvalue()
    store.path_for(source).write_bytes(blob)
    with repository.transaction(engine) as db:
        row = repository.get_artifact(db,sid,source.id)
        row.byte_size,row.sha256 = len(blob),sha256(blob).hexdigest()
    with pytest.raises(ArtifactFileError):
        renders.render_page(engine,store,sid,page.id,1)
    assert get_document(engine,sid).pages[0].render_revision is None


def test_internal_normalized_png_above_upload_limit_and_preview_resize(setup):
    engine,store,sid,_,_ = setup
    pixels = np.random.default_rng(42).integers(0,256,(2000,3000,3),dtype=np.uint8)
    stream = BytesIO()
    with Image.fromarray(pixels) as im:
        im.save(stream,format='JPEG',quality=95)
    page = import_page(engine,store,sid,stream.getvalue())
    source = descriptor(engine,sid,page.normalized_artifact_id)
    assert source.byte_size>15*1024*1024
    update_page_config(engine,sid,page.id,ConfigUpdateRequest(expected_revision=0,
        config={'corners':QUAD,'confirmed':True}))
    result = renders.render_page(engine,store,sid,page.id,1)
    assert (result.width,result.height)==(2400,1600)
    preview = descriptor(engine,sid,result.preview_artifact_id)
    assert (preview.width,preview.height)==(1000,667)
    # Independent INTER_AREA resize of saved full pixels is the actual preview.
    full = descriptor(engine,sid,result.render_artifact_id)
    with Image.open(store.verify(full)) as im:
        bgr = np.asarray(im)[:,:,::-1].copy()
    assert store.verify(preview).read_bytes()==encode_render_images(bgr).preview.png_bytes


def test_bad_source_role_rejected_before_decode(setup):
    engine,store,sid,page,_ = setup
    confirm(setup)
    with repository.transaction(engine) as db:
        repository.get_artifact(db,sid,page.normalized_artifact_id).kind = 'original'
    before = files(store)
    with pytest.raises(SessionDataError):
        renders.render_page(engine,store,sid,page.id,1)
    assert files(store)==before


def test_core_processing_error_has_service_boundary_and_no_files(setup,monkeypatch):
    from app.processing.render import RenderValidationError
    engine,store,sid,page,_ = setup
    confirm(setup)
    before = files(store)
    def fail(*args,**kwargs):
        raise RenderValidationError('WARP_FAILED','Controlled core failure')
    monkeypatch.setattr(renders,'render_document',fail)
    with pytest.raises(renders.RenderProcessingError):
        renders.render_page(engine,store,sid,page.id,1)
    assert files(store)==before
