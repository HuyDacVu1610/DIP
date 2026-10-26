"""Counts belong to the full prepared gray, never analysis/preview or BW."""
import json

import cv2
import numpy as np
import pytest

from app.processing.config import parse_config
from app.processing.enhancement import enhance_document
from app.processing.histogram import HistogramValidationError, compute_histogram


@pytest.mark.parametrize('image',[
    np.zeros((2,3),dtype=np.uint8),
    np.full((2,3),255,dtype=np.uint8),
    np.array([[0,1,1],[127,254,255]],dtype=np.uint8),
    np.tile(np.arange(256,dtype=np.uint8),(3,1))[:,::-1],
    np.full((2400,2400),255,dtype=np.uint8),
])
def test_counts_are_exact_python_integers_include_255_and_leave_input_unchanged(image):
    image.setflags(write=False)
    original = image.copy()
    counts = compute_histogram(image)
    expected = np.bincount(image.ravel(),minlength=256).tolist()
    assert isinstance(counts,tuple) and len(counts)==256
    assert all(type(count) is int and count>=0 for count in counts)
    assert list(counts)==expected and sum(counts)==image.size
    assert json.loads(json.dumps(counts))==expected
    assert np.array_equal(image,original)


@pytest.mark.parametrize('image',[
    None, [[0,255],[0,255]], np.zeros((3,4,3),dtype=np.uint8),
    np.zeros((3,4),dtype=np.float32), np.zeros((0,4),dtype=np.uint8),
    np.zeros((1,4),dtype=np.uint8), np.zeros((2,2401),dtype=np.uint8),
])
def test_histogram_rejects_non_full_gray_without_coercion(image):
    with pytest.raises(HistogramValidationError) as caught:
        compute_histogram(image)
    assert caught.value.code=='INVALID_HISTOGRAM_INPUT'


@pytest.mark.parametrize('method',['otsu','adaptive_gaussian'])
def test_bw_histogram_matches_actual_post_filter_clahe_threshold_input_with_or_without_debug(method):
    gray = np.tile(np.arange(64,dtype=np.uint8)*4,(40,1))
    source = np.repeat(gray[:,:,None],3,axis=2)
    config = parse_config({'mode':'bw','rotation':90,'denoise':{'method':'gaussian'},
        'contrast':{'method':'clahe'},'threshold':{'method':method}})
    observed = enhance_document(source,config,debug=True)
    plain = enhance_document(source,config)
    prepared = observed.stages.prepared_gray
    expected = tuple(np.bincount(prepared.ravel(),minlength=256).tolist())
    assert observed.histogram==plain.histogram==expected
    assert sum(expected)==source.shape[0]*source.shape[1]
    assert observed.histogram!=tuple(np.bincount(gray.ravel(),minlength=256).tolist())
    assert observed.histogram!=tuple(np.bincount(observed.image.ravel(),minlength=256).tolist())
    assert plain.stages is None and np.array_equal(plain.image,observed.image)
    if method=='otsu':
        threshold,bw = cv2.threshold(prepared,0,255,cv2.THRESH_BINARY|cv2.THRESH_OTSU)
        assert observed.otsu_threshold==plain.otsu_threshold==threshold
        assert np.array_equal(observed.stages.before_rotation,bw)
    else:
        assert observed.otsu_threshold is plain.otsu_threshold is None


@pytest.mark.parametrize('mode',['color','gray'])
def test_modes_without_threshold_have_no_threshold_histogram(mode):
    result = enhance_document(np.full((40,64,3),180,dtype=np.uint8),parse_config({'mode':mode}),debug=True)
    assert result.histogram is None and result.otsu_threshold is None
