from concurrent.futures import ThreadPoolExecutor
from threading import Event
from sqlalchemy import select,func
import pytest
from app.services import renders,detection,imports
from app.services.deletions import delete_document_part
from app.services.sessions import SessionNotFoundError
from app.services.page_config import PageNotFoundError
from app.storage.models import Artifact,RenderRun,DetectionRun
from app.storage.repository import transaction
from test_render_service import setup,confirm

@pytest.mark.parametrize('operation,whole',[('render',False),('render',True),('detect',False),('detect',True),('import',True)])
def test_actual_delete_during_cpu_work_prevents_late_publication(setup,monkeypatch,operation,whole):
 engine,store,sid,page,payload=setup;confirm(setup)
 renders.render_page(engine,store,sid,page.id,1,True)
 started,release=Event(),Event()
 module,name={'render':(renders,'render_document'),'detect':(detection,'detect_document'),'import':(imports,'normalize_image')}[operation]
 original=getattr(module,name)
 def blocked(*args,**kwargs):
  started.set();assert release.wait(10);return original(*args,**kwargs)
 monkeypatch.setattr(module,name,blocked)
 work={'render':lambda:renders.render_page(engine,store,sid,page.id,1,True),
  'detect':lambda:detection.detect_page(engine,store,sid,page.id,True),
  'import':lambda:imports.import_page(engine,store,sid,payload)}[operation]
 with ThreadPoolExecutor(max_workers=1) as pool:
  future=pool.submit(work)
  try:
   assert started.wait(10)
   delete_document_part(engine,store,sid,None if whole else page.id)
  finally:release.set()
  with pytest.raises(SessionNotFoundError if whole else PageNotFoundError):future.result(timeout=15)
 with transaction(engine) as db:
  for model in [Artifact,RenderRun,DetectionRun]:assert db.scalar(select(func.count()).select_from(model))==0
 assert not any(p.is_file() for p in (store.root/'sessions').rglob('*'))
