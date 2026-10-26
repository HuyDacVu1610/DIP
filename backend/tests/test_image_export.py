from io import BytesIO
from pathlib import Path
import re
import numpy as np
from PIL import Image
import pytest
from app.export.images import encode_image,download_filename,decode_full_png
from app.services.exports import encode_snapshot_image,export_snapshot
from app.schemas.exports import ExportRequest
from app.schemas.pages import ConfigUpdateRequest
from app.services.imports import import_page
from app.services.page_config import update_page_config
from app.services.renders import render_page
from app.services.sessions import get_document
from test_render_service import setup,QUAD,files


@pytest.mark.parametrize('mode',['color','gray','bw'])
@pytest.mark.parametrize('format',['png','jpg'])
def test_encoder_preserves_dimensions_channels_and_source_without_exif(mode,format):
    pixels=np.full((80,120,3),255,np.uint8) if mode=='color' else np.full((80,120),255,np.uint8)
    if mode=='color':pixels[:40,:60]=(0,0,255);pixels[40:,60:]=(255,0,0)
    else:pixels[20:60,60]=0
    before=pixels.copy();encoded=encode_image(pixels,format,title='Bài tập xử lý ảnh')
    assert np.array_equal(pixels,before) and (encoded.width,encoded.height)==(120,80)
    assert encoded.mime==('image/png' if format=='png' else 'image/jpeg')
    assert encoded.filename.endswith('.'+format)
    with Image.open(BytesIO(encoded.payload)) as image:
        image.load();assert image.mode==('RGB' if mode=='color' else 'L')
        assert image.size==(120,80) and not image.getexif() and 'icc_profile' not in image.info
        decoded=np.array(image);expected=pixels[:,:,::-1] if mode=='color' else pixels
        if format=='png':assert np.array_equal(decoded,expected)
        elif mode=='color':
            assert np.max(np.abs(decoded[10,10].astype(int)-expected[10,10]))<=3
            assert np.max(np.abs(decoded[70,110].astype(int)-expected[70,110]))<=3
        else:assert np.abs(decoded.astype(int)-expected.astype(int)).mean()<1


def test_png_keeps_one_pixel_binary_strokes_exactly():
    pixels=np.full((101,99),255,np.uint8);pixels[:,50]=0;pixels[50,:]=0
    with Image.open(BytesIO(encode_image(pixels,'png').payload)) as image:
        assert set(np.unique(image))=={0,255} and np.array_equal(image,pixels)


@pytest.mark.parametrize('pixels',[
    np.zeros((1,20),np.uint8),np.zeros((20,2401),np.uint8),np.zeros((3,4,4),np.uint8),
    np.zeros((3,4,1),np.uint8),np.zeros((3,4),np.float32),np.zeros((3,4),np.uint16),[[0,255]],
])
def test_invalid_rasters_are_rejected(pixels):
    with pytest.raises(ValueError):encode_image(pixels,'png')


@pytest.mark.parametrize('title',['../../private\r\n"x"','CON','NUL.txt','...', 'đề tài rất dài '*100])
def test_download_filename_is_bounded_ascii_leaf_with_server_chosen_extension(title):
    name=download_filename(title,'png')
    assert re.fullmatch(r'[A-Za-z0-9_-]+\.png',name) and len(name)<=100
    assert Path(name).name==name and name.lower() not in ('con.png','nul.png')
    with pytest.raises(ValueError):download_filename(title,'../../exe')


def test_decoder_requires_exact_clean_rgb_or_l_png_and_preserves_bgr():
    bgr=np.zeros((11,21,3),np.uint8);bgr[:]=(9,87,221)
    payload=encode_image(bgr,'png').payload
    assert np.array_equal(decode_full_png(payload,(21,11)),bgr)
    for data,size in [(payload,(22,11)),(b'invalid',(21,11)),(encode_image(bgr,'jpg').payload,(21,11))]:
        with pytest.raises(ValueError):decode_full_png(data,size)


@pytest.mark.parametrize('mode,metadata',[
    ('P',{}),('RGBA',{}),('I;16',{}),('RGB',{'icc_profile':b'not-inherited'}),
    ('RGB',{'exif':b'Exif\x00\x00MM\x00*\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00'}),
])
def test_decoder_refuses_unexpected_internal_png_modes_and_metadata(mode,metadata):
    stream=BytesIO()
    if mode=='RGB' and 'exif' in metadata:
        exif=Image.Exif();exif[274]=6;metadata={'exif':exif}
    with Image.new(mode,(21,11)) as image:image.save(stream,format='PNG',**metadata)
    with pytest.raises(ValueError):decode_full_png(stream.getvalue(),(21,11))


@pytest.mark.parametrize('mode,rotation',[('color',0),('gray',90),('bw',270)])
def test_snapshot_encoder_uses_full_not_preview_and_does_not_write_db_or_files(setup,mode,rotation):
    engine,store,sid,_,_=setup
    pixels=np.full((1600,1200,3),255,np.uint8);pixels[:300,:300]=(255,0,0);pixels[400:1400:2,300:900]=0
    stream=BytesIO()
    with Image.fromarray(pixels) as original:original.save(stream,format='PNG')
    page=import_page(engine,store,sid,stream.getvalue())
    update_page_config(engine,sid,page.id,ConfigUpdateRequest(expected_revision=0,config={
        'mode':mode,'rotation':rotation,'corners':QUAD,'confirmed':True,'threshold':{'method':'otsu'}}))
    render=render_page(engine,store,sid,page.id,1)
    before=get_document(engine,sid);hashes=files(store)
    for format in ['png','jpg']:
        request=ExportRequest(format=format,pages=[{'page_id':page.id,'revision':1}])
        with export_snapshot(engine,store,sid,request) as snapshot:
            result=encode_snapshot_image(store,snapshot)
            assert (result.width,result.height)==(render.width,render.height) and max(result.width,result.height)>1000
            with Image.open(BytesIO(result.payload)) as actual:
                actual.load();assert actual.size==(render.width,render.height)
                if format=='png':
                    full=store.verify(snapshot.pages[0].full).read_bytes()
                    with Image.open(BytesIO(full)) as expected:assert np.array_equal(actual,expected)
    assert get_document(engine,sid)==before and files(store)==hashes
