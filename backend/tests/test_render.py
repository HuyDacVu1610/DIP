"""Source-based offline pipeline; no confirmation or display image reuse."""
from copy import deepcopy

import cv2
import numpy as np
import pytest

from app.processing.config import ConfigValidationError, parse_config
from app.processing.geometry import GeometryValidationError, warp_document
from app.processing.enhancement import enhance_document
from app.processing.render import render_document


FULL = [[0,0],[1,0],[1,1],[0,1]]


def rectangle(background=25,paper=240):
    source = np.full((240,320,3),background,dtype=np.uint8)
    source[25:216,30:291]=paper
    return source


@pytest.mark.parametrize('mode,rotation',[(m,r) for m in ('color','gray','bw') for r in (0,90)])
def test_manual_pipeline_uses_same_source_warp_and_mode_without_mutation(mode,rotation):
    source = rectangle()
    original = source.copy()
    source.setflags(write=False)
    data = {'mode':mode,'corners':FULL,'rotation':rotation}
    before = deepcopy(data)
    result = render_document(source,data)
    expected_warp = warp_document(source,FULL)
    expected = enhance_document(expected_warp,parse_config(data,source_size=(320,240)),source_size=(320,240))
    assert result.status=='rendered' and result.corners_origin=='manual'
    assert result.detection is None
    assert np.array_equal(result.warped_bgr,expected_warp)
    assert np.array_equal(result.enhancement.image,expected.image)
    assert result.effective_config==expected.effective_config
    assert result.enhancement.otsu_threshold==expected.otsu_threshold
    assert not result.effective_config.confirmed
    assert data==before and np.array_equal(source,original)
    assert result.timings_ms.detect==0


@pytest.mark.parametrize('background,paper,status',[(25,240,'proposed'),(235,243,'proposed_with_warning')])
def test_auto_uses_only_proposed_corners_and_keeps_unconfirmed_draft(background,paper,status):
    result = render_document(rectangle(background,paper),{'mode':'color'},debug=True)
    assert result.status=='rendered' and result.corners_origin=='detected'
    assert result.detection.status==status
    assert result.effective_config.corners==result.detection.corners
    assert result.detection.debug is not None
    assert result.effective_config.confirmed is result.detection.confirmed is False
    assert result.warped_bgr.shape[:2]==result.enhancement.image.shape[:2]


def test_no_quad_returns_manual_required_without_a_fake_full_render():
    source = np.full((100,140,3),200,dtype=np.uint8)
    result = render_document(source,{'mode':'color'},debug=True)
    assert result.status=='manual_required' and result.corners_origin=='none'
    assert result.detection.corners is None and result.effective_config.corners is None
    assert result.warped_bgr is None and result.enhancement is None and result.homography is None
    assert not result.effective_config.confirmed
    assert result.timings_ms.warp==result.timings_ms.enhance==0
    manual = render_document(source,{'corners':FULL})
    assert manual.status=='rendered' and np.all(manual.enhancement.image==200)


def test_low_score_diagnostic_corners_are_never_used_for_warp():
    source = np.full((240,320,3),235,dtype=np.uint8)
    source[60:181,85:236]=243
    result = render_document(source,{},debug=True)
    assert result.status=='manual_required' and result.detection.selected is not None
    assert result.detection.debug.overlay_kind=='diagnostic'
    assert result.effective_config.corners is None and result.warped_bgr is None


def test_pipeline_rejects_more_than_sixteen_megapixels_before_allocating_warp():
    source = np.broadcast_to(np.zeros((1,1,3),dtype=np.uint8),(4001,4000,3))
    with pytest.raises(GeometryValidationError) as error:
        render_document(source,{})
    assert error.value.code=='TOO_MANY_PIXELS'


def test_full_resolution_checkerboard_is_warped_from_source_not_analysis():
    pixels = ((np.indices((1300,1700)).sum(axis=0)%2)*255).astype(np.uint8)
    source = np.repeat(pixels[:,:,None],3,axis=2)
    result = render_document(source,{'corners':FULL})
    assert result.warped_bgr.shape==(1299,1699,3)
    assert np.array_equal(result.warped_bgr,warp_document(source,FULL))
    wrong = cv2.resize(source,(1200,918),interpolation=cv2.INTER_AREA)
    assert not np.array_equal(result.warped_bgr,cv2.resize(wrong,(1699,1299)))


def test_manual_corner_cycle_and_explicit_confirmation_are_preserved():
    corners = [[1,0],[1,1],[0,1],[0,0]]
    result = render_document(rectangle(),{'corners':corners,'confirmed':True})
    assert result.effective_config.corners==tuple(map(tuple,corners))
    assert result.effective_config.confirmed is True  # explicit input, never detector's doing


def test_valid_source_too_thin_for_analysis_returns_manual_and_still_warps_by_hand():
    # 42px source height passes the existing short-edge gate, but analysis
    # rounds to height1. A 2px source would correctly fail quad geometry too.
    source = np.full((42,40000,3),71,dtype=np.uint8)
    result = render_document(source,{})
    assert result.status=='manual_required' and result.detection.warnings==('ANALYSIS_TOO_SMALL',)
    assert result.detection.debug is None
    manual = render_document(source,{'corners':FULL})
    assert manual.status=='rendered' and manual.enhancement.image.shape==(2,2400,3)


@pytest.mark.parametrize('data',[{'mode':'invalid'},{'corners':[[0,0]]},
    {'corners':FULL,'mode':'bw','threshold':{'block_size':151}}])
def test_invalid_config_is_not_silently_clamped_or_changed(data):
    with pytest.raises(ConfigValidationError):
        render_document(np.zeros((40,50,3),dtype=np.uint8),data)


@pytest.mark.parametrize('source',[None,np.zeros((10,20),dtype=np.uint8),
    np.zeros((10,20,3),dtype=np.float32),np.zeros((1,20,3),dtype=np.uint8)])
def test_pipeline_rejects_invalid_source(source):
    with pytest.raises(GeometryValidationError):
        render_document(source,{})


def test_encoded_color_channels_hashes_and_clean_exif_preserve_source():
    from hashlib import sha256
    from io import BytesIO
    from PIL import Image
    from app.processing.render import encode_render_images
    source = np.full((4,6,3),(11,83,211),dtype=np.uint8)
    source.setflags(write=False)
    result = encode_render_images(source)
    for encoded in (result.full,result.preview):
        assert encoded.png_mode=='RGB' and (encoded.width,encoded.height)==(6,4)
        assert encoded.sha256==sha256(encoded.png_bytes).hexdigest()
        with Image.open(BytesIO(encoded.png_bytes)) as image:
            assert image.mode=='RGB' and not image.getexif()
            assert image.getpixel((2,1))==(211,83,11)
    assert result.full.png_bytes==result.preview.png_bytes
    assert np.all(source==[11,83,211])


def test_preview_is_inter_area_from_full_bw_without_rethresholding():
    from io import BytesIO
    from PIL import Image
    from app.processing.render import encode_render_images
    source = ((np.indices((1301,2001)).sum(axis=0)%2)*255).astype(np.uint8)
    result = encode_render_images(source)
    full = np.array(Image.open(BytesIO(result.full.png_bytes)))
    preview = np.array(Image.open(BytesIO(result.preview.png_bytes)))
    assert result.full.png_mode==result.preview.png_mode=='L'
    assert np.array_equal(full,source) and preview.shape==(650,1000)
    assert np.array_equal(preview,cv2.resize(full,(1000,650),interpolation=cv2.INTER_AREA))
    assert np.any((preview>0)&(preview<255))


def test_preview_can_have_one_pixel_short_edge_and_never_upscales():
    from io import BytesIO
    from PIL import Image
    from app.processing.render import encode_render_images
    source = np.full((2,2400),71,dtype=np.uint8)
    result = encode_render_images(source)
    assert (result.preview.width,result.preview.height)==(1000,1)
    assert np.all(np.array(Image.open(BytesIO(result.preview.png_bytes)))==71)


@pytest.mark.parametrize('source',[None,np.zeros((2,3),dtype=np.float32),
    np.zeros((2,3,4),dtype=np.uint8),np.zeros((1,5),dtype=np.uint8),
    np.zeros((3,2401),dtype=np.uint8)])
def test_render_encoding_rejects_invalid_full_dimensions_or_channels(source):
    from app.processing.render import RenderValidationError, encode_render_images
    with pytest.raises(RenderValidationError) as error:
        encode_render_images(source)
    assert error.value.code=='INVALID_RENDER'


def test_png_encoding_failure_is_explicit(monkeypatch):
    from app.processing.render import RenderValidationError, encode_render_images
    def fail(*args,**kwargs):
        raise OSError('controlled PNG failure')
    monkeypatch.setattr('PIL.Image.Image.save',fail)
    with pytest.raises(RenderValidationError) as error:
        encode_render_images(np.zeros((4,5,3),dtype=np.uint8))
    assert error.value.code=='ENCODE_FAILED'


@pytest.mark.parametrize('mode,method,rotation',[
    ('color','otsu',270),('gray','otsu',90),
    ('bw','otsu',180),('bw','adaptive_gaussian',90),
])
def test_repeated_source_and_serialized_config_keep_pixels_stages_and_histogram(mode,method,rotation):
    """A fresh render from a serialized snapshot must reproduce actual pixels."""
    import json
    from app.processing.render import encode_render_images
    source = np.random.default_rng(604).integers(0,256,(73,97,3),dtype=np.uint8)
    original = source.copy()
    source.setflags(write=False)
    requested = parse_config({'mode':mode,'corners':FULL,'rotation':rotation,
        'denoise':{'method':'gaussian','kernel':5},'contrast':{'method':'clahe'},
        'threshold':{'method':method,'block_size':15,'c':7}},source_size=(97,73))
    snapshot = requested.model_dump_json()
    first = render_document(source,requested,debug=True)
    second = render_document(source,json.loads(snapshot),debug=True)
    assert first.effective_config.model_dump_json()==second.effective_config.model_dump_json()==snapshot
    assert first.status==second.status=='rendered' and first.corners_origin==second.corners_origin=='manual'
    assert first.detection is second.detection is None
    assert np.array_equal(first.homography,second.homography)
    assert np.array_equal(first.warped_bgr,second.warped_bgr)
    for name in ('filtered_bgr','prepared_gray','before_rotation'):
        left,right = getattr(first.enhancement.stages,name),getattr(second.enhancement.stages,name)
        assert (left is None and right is None) or np.array_equal(left,right)
    assert first.enhancement.histogram==second.enhancement.histogram
    assert first.enhancement.otsu_threshold==second.enhancement.otsu_threshold
    assert np.array_equal(first.enhancement.image,second.enhancement.image)
    assert not np.shares_memory(first.enhancement.image,second.enhancement.image)
    assert encode_render_images(first.enhancement.image)==encode_render_images(second.enhancement.image)
    assert np.array_equal(source,original) and requested.model_dump_json()==snapshot
