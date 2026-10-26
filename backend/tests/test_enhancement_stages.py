"""Capture the actual full-warp stages, not a second reconstructed pipeline."""
import cv2
import numpy as np
import pytest

from app.processing.config import ConfigValidationError, parse_config
from app.processing.enhancement import apply_denoise, enhance_document, render_gray


@pytest.mark.parametrize('mode,threshold',[('color','otsu'),('gray','otsu'),
    ('bw','otsu'),('bw','adaptive_gaussian')])
def test_debug_returns_actual_stages_before_rotation_and_does_not_change_pixels(mode,threshold):
    gray = np.tile(np.arange(64,dtype=np.uint8)*4,(40,1))
    source = np.repeat(gray[:,:,None],3,axis=2)
    source.setflags(write=False)
    config = parse_config({'mode':mode,'rotation':90,'denoise':{'method':'gaussian','kernel':5},
        'contrast':{'method':'clahe'},'threshold':{'method':threshold}})
    original = source.copy()
    plain = enhance_document(source,config)
    observed = enhance_document(source,config,debug=True)
    stages = observed.stages
    assert plain.stages is None and stages is not None
    assert np.array_equal(observed.image,plain.image) and np.array_equal(source,original)
    assert np.array_equal(stages.filtered_bgr,apply_denoise(source,config.denoise))
    assert not np.shares_memory(stages.filtered_bgr,source)
    assert stages.before_rotation.shape[:2]==source.shape[:2]
    assert np.array_equal(observed.image,cv2.rotate(stages.before_rotation,cv2.ROTATE_90_CLOCKWISE))
    assert observed.effective_config==config
    if mode=='color':
        assert stages.prepared_gray is None
        assert np.array_equal(stages.before_rotation,stages.filtered_bgr)
    else:
        expected = render_gray(stages.filtered_bgr,config.contrast)
        assert np.array_equal(stages.prepared_gray,expected)
        if mode=='gray':
            assert np.array_equal(stages.before_rotation,expected)
        elif threshold=='otsu':
            t,bw = cv2.threshold(expected,0,255,cv2.THRESH_BINARY|cv2.THRESH_OTSU)
            assert observed.otsu_threshold==t and np.array_equal(stages.before_rotation,bw)
        else:
            assert observed.otsu_threshold is None


def test_capturing_debug_stages_calls_each_filter_only_once(monkeypatch):
    import app.processing.enhancement as module
    original = module.apply_denoise
    calls = []
    def traced(*args):
        calls.append(1)
        return original(*args)
    monkeypatch.setattr(module,'apply_denoise',traced)
    result = enhance_document(np.full((40,64,3),200,dtype=np.uint8),parse_config({'mode':'bw'}),debug=True)
    assert calls==[1] and result.stages is not None


def test_debug_option_is_strict_bool():
    with pytest.raises(ConfigValidationError):
        enhance_document(np.zeros((4,5,3),dtype=np.uint8),parse_config({}),debug='false')
