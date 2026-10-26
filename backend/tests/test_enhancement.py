"""Configuration, staged enhancement, dispatcher and clockwise rotation contracts."""

from copy import deepcopy
from itertools import permutations

import pytest
import numpy as np
from pydantic import ValidationError

from app.processing.config import ConfigValidationError, ContrastConfig, DenoiseConfig, ThresholdConfig, get_preset, parse_config
from app.processing.enhancement import EnhancementValidationError, apply_adaptive_gaussian, apply_denoise, apply_otsu, enhance_document, render_color, render_gray


@pytest.mark.parametrize('mode,denoise,contrast', [('color','none','none'),('gray','none','clahe'),('bw','median','none')])
def test_presets_match_the_full_contract_and_start_unconfirmed(mode,denoise,contrast):
    config=get_preset(mode)
    assert config.model_dump(mode='json') == {
        'mode':mode,'corners':None,'confirmed':False,'rotation':0,
        'denoise':{'method':denoise,'kernel':3},
        'contrast':{'method':contrast,'clip_limit':2.0,'tile_grid':[8,8]},
        'threshold':{'method':'adaptive_gaussian','block_size':31,'c':10},
        'geometry':{'aspect_policy':'estimated','max_long_edge':2400},
    }
    assert parse_config({'mode':mode}) == config


def test_partial_nested_fields_get_requested_mode_defaults_without_mutating_input():
    raw={'mode':'bw','denoise':{'kernel':5},'threshold':{'c':-5}}
    before=deepcopy(raw)
    config=parse_config(raw)
    assert config.denoise.method == 'median' and config.denoise.kernel == 5
    assert config.threshold.block_size == 31 and config.threshold.c == -5
    assert config.contrast.method == 'none'
    assert raw == before
    assert parse_config({}) == get_preset('color')


def test_full_mode_change_retains_inactive_values_but_partial_input_uses_preset():
    old=parse_config({'mode':'bw','denoise':{'method':'gaussian','kernel':5},
                      'contrast':{'method':'clahe','clip_limit':3},
                      'threshold':{'block_size':51,'c':-3}})
    data=old.model_dump(mode='json')
    data['mode']='color'
    new=parse_config(data)
    assert new.denoise == old.denoise
    assert new.threshold == old.threshold and new.contrast == old.contrast
    assert set(new.inactive_fields) == {'contrast.method','contrast.clip_limit','contrast.tile_grid',
                                      'threshold.method','threshold.block_size','threshold.c'}
    assert parse_config({'mode':'color'}).denoise.method == 'none'
    assert old.mode == 'bw'


def test_default_and_otsu_inactive_fields_are_explicit_and_not_serialized_as_config():
    assert set(get_preset('color').inactive_fields) == {
        'denoise.kernel','contrast.method','contrast.clip_limit','contrast.tile_grid',
        'threshold.method','threshold.block_size','threshold.c',
    }
    assert set(get_preset('gray').inactive_fields) == {
        'denoise.kernel','threshold.method','threshold.block_size','threshold.c',
    }
    assert set(parse_config({'mode':'bw','threshold':{'method':'otsu'}}).inactive_fields) == {
        'contrast.clip_limit','contrast.tile_grid','threshold.block_size','threshold.c',
    }
    assert 'inactive_fields' not in get_preset('bw').model_dump()


@pytest.mark.parametrize('raw', [
    None, [], 'color', {'mode':None}, {'mode':'BW'}, {'mode':False}, {'confirmed':1},
    {'rotation':True}, {'rotation':'90'}, {'rotation':90.0}, {'rotation':45},
    {'denoise':None}, {'denoise':{'method':'bilateral'}},
    {'denoise':{'kernel':True}}, {'denoise':{'kernel':'3'}}, {'denoise':{'kernel':3.0}},
    {'denoise':{'kernel':4}}, {'denoise':{'kernel':7}},
    {'contrast':{'method':'lab'}}, {'contrast':{'clip_limit':'2'}},
    {'contrast':{'clip_limit':True}}, {'contrast':{'clip_limit':float('nan')}},
    {'contrast':{'clip_limit':float('inf')}}, {'contrast':{'clip_limit':0.9}},
    {'contrast':{'clip_limit':4.1}}, {'contrast':{'tile_grid':[4,4]}},
    {'contrast':{'tile_grid':[8.0,8]}}, {'threshold':{'method':'adaptive_mean'}},
    {'threshold':{'block_size':2}}, {'threshold':{'block_size':4}},
    {'threshold':{'block_size':153}}, {'threshold':{'block_size':'31'}},
    {'threshold':{'c':True}}, {'threshold':{'c':1.5}},
    {'threshold':{'c':-21}}, {'threshold':{'c':31}},
    {'geometry':{'aspect_policy':'a4'}}, {'geometry':{'max_long_edge':3000}},
    {'geometry':{'max_long_edge':2400.0}}, {'illumination':{'enabled':True}},
    {'revision':1}, {'denoise':{'sigma':1}}, {'threshold':{'c':None}},
])
def test_wrong_fields_types_ranges_and_inactive_values_are_rejected(raw):
    with pytest.raises(ConfigValidationError) as error:
        parse_config(raw)
    assert error.value.code == 'INVALID_CONFIG'
    assert str(error.value)


@pytest.mark.parametrize('raw', [
    {'rotation':90}, {'rotation':180}, {'rotation':270},
    {'contrast':{'clip_limit':1}}, {'contrast':{'clip_limit':4}},
    {'threshold':{'block_size':3,'c':-20}}, {'threshold':{'block_size':151,'c':30}},
    {'denoise':{'method':'median','kernel':5}}, {'denoise':{'method':'gaussian','kernel':3}},
])
def test_parameter_boundaries_are_accepted(raw):
    assert parse_config(raw).model_dump()


def test_preset_snapshots_are_independent_and_nested_fields_are_frozen():
    first=get_preset('bw')
    second=get_preset('bw')
    with pytest.raises(ValidationError):
        first.threshold.c=20
    with pytest.raises(ValidationError):
        first.mode='color'
    payload=first.model_dump(mode='json')
    payload['threshold']['c']=30
    assert first.threshold.c == second.threshold.c == 10


def test_confirmed_and_draft_corners_use_full_source_geometry_and_preserve_handles():
    corners=[[0.15,0.05],[0.95,0.3],[0.7,0.95],[0.1,0.65]]
    for confirmed in [False,True]:
        config=parse_config({'corners':corners,'confirmed':confirmed},source_size=(1536,2048))
        assert config.corners == tuple(tuple(p) for p in corners)
        assert config.confirmed is confirmed
    with pytest.raises(ConfigValidationError):
        parse_config({'confirmed':True})
    with pytest.raises(ConfigValidationError):
        parse_config({'corners':corners})  # Actual source dimensions required.
    valid_cycles=[corners[i:]+corners[:i] for i in range(4)]
    for proposed in permutations(corners):
        data={'corners':list(proposed)}
        if list(proposed) in valid_cycles:
            assert parse_config(data,source_size=(1536,2048)).corners
        else:
            with pytest.raises(ConfigValidationError):
                parse_config(data,source_size=(1536,2048))


@pytest.mark.parametrize('corners', [
    [[0,0],[1,0],[1,1]], [[0,0],[1,0],[1,1],[0,0]],
    [[0,0],[1,0],[0.2,0.2],[0,1]], [[0,0],[1,0],[1,1],[0,float('nan')]],
    [[0,0],[1,0],[1,1],[False,1]], [[0,0],[1,0],[1,1],[0,1.01]],
])
def test_bad_corners_are_rejected_even_when_unconfirmed(corners):
    with pytest.raises(ConfigValidationError):
        parse_config({'corners':corners},source_size=(101,101))


def test_adaptive_dimension_dependency_only_applies_when_active():
    with pytest.raises(ConfigValidationError):
        parse_config({'mode':'bw'},warp_size=(20,30))
    assert parse_config({'mode':'bw','threshold':{'block_size':19}},warp_size=(20,30))
    assert parse_config({'mode':'bw','threshold':{'method':'otsu'}},warp_size=(2,2))
    assert parse_config({'mode':'gray'},warp_size=(2,2))
    assert parse_config({'mode':'color'},warp_size=(2,2))
    assert parse_config({'mode':'bw'},warp_size=(31,31))


@pytest.mark.parametrize('size', [(1,10),(10,1),(0,10),(True,10),(10.5,20),(2401,20)])
def test_invalid_warp_dimensions_are_not_ignored(size):
    with pytest.raises(ConfigValidationError):
        parse_config({},warp_size=size)


def test_validated_config_json_round_trip_and_instances_are_revalidated():
    config=parse_config({'corners':[[0,0],[1,0],[1,1],[0,1]],'confirmed':True,'mode':'bw'},
                        source_size=(101,51),warp_size=(100,50))
    assert parse_config(config.model_dump(mode='json'),source_size=(101,51),warp_size=(100,50)) == config
    # Pydantic model_copy(update=...) bypasses validation: public parser must
    # not trust an instance built that way.
    unsafe=config.model_copy(update={'rotation':True})
    with pytest.raises(ConfigValidationError):
        parse_config(unsafe,source_size=(101,51))


@pytest.mark.parametrize('method,kernel', [('none',3),('median',3),('median',5),('gaussian',3),('gaussian',5)])
def test_denoise_preserves_shape_dtype_bgr_and_independent_source(method,kernel):
    source=np.empty((9,13,3),dtype=np.uint8)
    source[:]=[17,83,201]
    before=source.copy()
    source.flags.writeable=False
    result=apply_denoise(source,DenoiseConfig(method=method,kernel=kernel))
    assert result.shape == source.shape and result.dtype == np.uint8
    assert result.flags.c_contiguous and result.flags.writeable
    assert not np.shares_memory(result,source)
    np.testing.assert_array_equal(result,before)
    result[0,0]=0
    np.testing.assert_array_equal(source,before)


def test_none_keeps_every_pixel_of_noncontiguous_image_and_returns_copy():
    source=np.arange(8*12*3,dtype=np.uint8).reshape(8,12,3)[:,::2]
    result=apply_denoise(source,get_preset('color').denoise)
    np.testing.assert_array_equal(result,source)
    assert result.flags.c_contiguous and not np.shares_memory(result,source)


@pytest.mark.parametrize('kernel', [3,5])
def test_median_removes_isolated_salt_and_pepper_but_can_erase_thin_strokes(kernel):
    noisy=np.full((11,11,3),255,dtype=np.uint8)
    noisy[5,5]=0
    result=apply_denoise(noisy,DenoiseConfig(method='median',kernel=kernel))
    assert np.all(result == 255)
    noisy[:]=0
    noisy[5,5]=255
    assert np.all(apply_denoise(noisy,DenoiseConfig(method='median',kernel=kernel)) == 0)
    thin=np.full((11,11,3),255,dtype=np.uint8)
    thin[:,5]=0
    filtered=apply_denoise(thin,DenoiseConfig(method='median',kernel=kernel))
    assert np.all(filtered == 255)
    assert np.all(thin[:,5] == 0)


@pytest.mark.parametrize('kernel,expected_center', [(3,64),(5,36)])
def test_gaussian_uses_sigma_zero_kernel_weights_without_thresholding(kernel,expected_center):
    source=np.zeros((11,11,3),dtype=np.uint8)
    source[5,5]=255
    result=apply_denoise(source,DenoiseConfig(method='gaussian',kernel=kernel))
    np.testing.assert_array_equal(result[5,5],[expected_center]*3)
    assert 0 < result[5,4,0] < expected_center
    assert np.any((result > 0)&(result < 255))
    assert source[5,5,0] == 255 and source[5,4,0] == 0


def test_gaussian_softens_thin_stroke_while_none_preserves_it():
    source=np.full((11,11,3),255,dtype=np.uint8)
    source[:,5]=0
    none=apply_denoise(source,DenoiseConfig())
    blurred=apply_denoise(source,DenoiseConfig(method='gaussian'))
    assert np.all(none[:,5] == 0)
    assert np.all(blurred[:,5] == 128)
    assert np.all(blurred[:,4] == 191)


@pytest.mark.parametrize('method', ['none','median','gaussian'])
def test_filters_accept_two_pixel_warp_without_changing_kernel_policy(method):
    source=np.full((2,2,3),73,dtype=np.uint8)
    np.testing.assert_array_equal(apply_denoise(source,DenoiseConfig(method=method,kernel=5)),source)


@pytest.mark.parametrize('image', [
    None, np.zeros((3,3),dtype=np.uint8), np.zeros((3,3,1),dtype=np.uint8),
    np.zeros((3,3,4),dtype=np.uint8), np.zeros((3,3,3),dtype=np.float32),
    np.zeros((1,3,3),dtype=np.uint8), np.zeros((0,3,3),dtype=np.uint8),
    np.zeros((2401,2,3),dtype=np.uint8),
])
def test_filters_reject_inputs_outside_warp_contract(image):
    with pytest.raises(EnhancementValidationError) as error:
        apply_denoise(image,DenoiseConfig())
    assert error.value.code == 'INVALID_RENDER'


@pytest.mark.parametrize('changes', [{'method':'bilateral'},{'kernel':True},{'kernel':4},{'kernel':7}])
def test_filter_revalidates_unsafe_config_before_opencv(monkeypatch,changes):
    import cv2
    monkeypatch.setattr(cv2,'medianBlur',lambda *a,**k:pytest.fail('Invalid config reached filter'))
    monkeypatch.setattr(cv2,'GaussianBlur',lambda *a,**k:pytest.fail('Invalid config reached filter'))
    unsafe=DenoiseConfig(method='median').model_copy(update=changes)
    with pytest.raises(ConfigValidationError):
        apply_denoise(np.zeros((3,3,3),dtype=np.uint8),unsafe)


@pytest.mark.parametrize('method', ['none', 'clahe'])
def test_modes_preserve_dimensions_and_source_on_readonly_strided_input(method):
    source = np.tile(np.array([[[17, 83, 201], [210, 235, 255]]], dtype=np.uint8), (8, 12, 1))[:, ::2]
    source.setflags(write=False)
    before = source.copy()
    for output, shape in [(render_color(source), source.shape),
                          (render_gray(source, ContrastConfig(method=method)), source.shape[:2])]:
        assert output.shape == shape and output.dtype == np.uint8
        assert output.flags.c_contiguous and output.flags.writeable
        assert not np.shares_memory(output, source)
        output[:] = 0
        assert np.array_equal(source, before)


def test_color_keeps_every_pixel_including_highlight_without_using_clahe(monkeypatch):
    source = np.arange(180, dtype=np.uint8).reshape(6, 10, 3)
    source[2:4, 3:7] = [210, 235, 255]
    def forbidden(*args, **kwargs):
        pytest.fail('Color must not convert or equalize its channels')
    monkeypatch.setattr('app.processing.enhancement.cv2.cvtColor', forbidden)
    monkeypatch.setattr('app.processing.enhancement.cv2.createCLAHE', forbidden)
    assert np.array_equal(render_color(source), source)


def test_gray_uses_bgr_luminance_and_keeps_intermediate_levels_when_clahe_is_off(monkeypatch):
    source = np.array([[[255, 0, 0], [0, 255, 0], [0, 0, 255], [210, 235, 255]],
                       [[0, 0, 0], [255, 255, 255], [100, 100, 100], [17, 83, 201]]], dtype=np.uint8)
    def forbidden(*args, **kwargs):
        pytest.fail('CLAHE off must not create an equalizer')
    monkeypatch.setattr('app.processing.enhancement.cv2.createCLAHE', forbidden)
    gray = render_gray(source, ContrastConfig(method='none'))
    assert gray.tolist() == [[29, 150, 76, 238], [0, 255, 100, 111]]


@pytest.mark.parametrize('clip_limit', [1.0, 2.0, 4.0])
def test_gray_clahe_receives_only_gray_and_the_validated_settings(monkeypatch, clip_limit):
    import cv2
    real_create = cv2.createCLAHE
    calls = []
    class CheckedEqualizer:
        def apply(self, gray):
            assert gray.ndim == 2 and gray.dtype == np.uint8
            calls.append(gray.copy())
            return real_create(clipLimit=clip_limit, tileGridSize=(8, 8)).apply(gray)
    def checked_create(*, clipLimit, tileGridSize):
        assert clipLimit == clip_limit and tileGridSize == (8, 8)
        return CheckedEqualizer()
    monkeypatch.setattr('app.processing.enhancement.cv2.createCLAHE', checked_create)
    ramp = np.tile(np.arange(100, 132, dtype=np.uint8), (64, 2))
    source = np.repeat(ramp[:, :, None], 3, axis=2)
    before = source.copy()
    raw = render_gray(source, ContrastConfig(method='none'))
    enhanced = render_gray(source, ContrastConfig(method='clahe', clip_limit=clip_limit))
    assert len(calls) == 1 and np.array_equal(calls[0], raw)
    assert np.count_nonzero(enhanced != raw) > 0
    assert np.unique(enhanced).size > 2  # still grayscale, not thresholded BW
    assert np.array_equal(source, before)
    assert np.array_equal(render_gray(source, ContrastConfig(method='none')), raw)


@pytest.mark.parametrize('method', ['none', 'clahe'])
def test_gray_accepts_minimum_full_warp_without_changing_grid_or_size(method):
    result = render_gray(np.full((2, 2, 3), 100, dtype=np.uint8), ContrastConfig(method=method))
    assert result.shape == (2, 2) and result.dtype == np.uint8


@pytest.mark.parametrize('renderer', ['color', 'gray'])
@pytest.mark.parametrize('source', [None, np.zeros((2, 2), dtype=np.uint8),
    np.zeros((2, 2, 4), dtype=np.uint8), np.zeros((2, 2, 3), dtype=np.float32),
    np.zeros((1, 2, 3), dtype=np.uint8), np.zeros((2, 2401, 3), dtype=np.uint8)])
def test_modes_reject_inputs_outside_full_warp_contract(renderer, source):
    with pytest.raises(EnhancementValidationError) as error:
        if renderer == 'color':
            render_color(source)
        else:
            render_gray(source, ContrastConfig())
    assert error.value.code == 'INVALID_RENDER'


@pytest.mark.parametrize('method', ['none', 'clahe'])
@pytest.mark.parametrize('update', [{'method': 'equalize'}, {'clip_limit': float('nan')},
    {'clip_limit': 0.5}, {'clip_limit': True}, {'tile_grid': (4, 4)}])
def test_gray_revalidates_even_inactive_contrast_fields_before_opencv(monkeypatch, method, update):
    unsafe = ContrastConfig(method=method).model_copy(update=update)
    def forbidden(*args, **kwargs):
        pytest.fail('Invalid contrast must fail before image processing')
    monkeypatch.setattr('app.processing.enhancement.cv2.cvtColor', forbidden)
    with pytest.raises(ConfigValidationError) as error:
        render_gray(np.zeros((4, 4, 3), dtype=np.uint8), unsafe)
    assert error.value.code == 'INVALID_CONFIG'


def test_gray_reports_opencv_failure_with_a_stable_reason(monkeypatch):
    import cv2
    def fail(*args, **kwargs):
        raise cv2.error('simulated conversion failure')
    monkeypatch.setattr('app.processing.enhancement.cv2.cvtColor', fail)
    with pytest.raises(EnhancementValidationError) as error:
        render_gray(np.zeros((4, 4, 3), dtype=np.uint8), ContrastConfig())
    assert error.value.code == 'MODE_FAILED'


def test_otsu_returns_the_actual_optimal_threshold_and_binary_polarity(monkeypatch):
    gray = np.tile(np.array([0, 30, 200, 240], dtype=np.uint8), (4, 1))
    def forbidden(*args, **kwargs):
        pytest.fail('Threshold must consume prepared gray, without extra preprocessing')
    monkeypatch.setattr('app.processing.enhancement.cv2.GaussianBlur', forbidden)
    monkeypatch.setattr('app.processing.enhancement.cv2.medianBlur', forbidden)
    monkeypatch.setattr('app.processing.enhancement.cv2.createCLAHE', forbidden)
    bw, threshold = apply_otsu(gray)
    assert threshold == 30.0 and isinstance(threshold, float)
    assert bw.tolist() == [[0, 0, 255, 255]] * 4
    assert bw.dtype == np.uint8 and bw.shape == gray.shape
    assert np.array_equal(bw, np.where(gray > threshold, 255, 0).astype(np.uint8))


@pytest.mark.parametrize('level,expected', [(0, 0), (100, 255), (255, 255)])
def test_otsu_constant_image_returns_degenerate_threshold_without_inventing_127(level, expected):
    bw, threshold = apply_otsu(np.full((2, 2), level, dtype=np.uint8))
    assert threshold == 0.0
    assert np.all(bw == expected)


def test_otsu_does_not_mutate_readonly_strided_gray_and_keeps_independent_output():
    gray = np.tile(np.arange(256, dtype=np.uint8), (4, 2))[:, ::2]
    gray.setflags(write=False)
    before = gray.copy()
    bw, threshold = apply_otsu(gray)
    assert 0 <= threshold <= 255
    assert set(np.unique(bw)) == {0, 255}
    assert not np.shares_memory(gray, bw)
    assert bw.flags.writeable and bw.flags.c_contiguous
    bw[:] = 17
    assert np.array_equal(gray, before)


def test_otsu_uniform_light_separates_ink_but_global_threshold_can_blacken_shadow():
    uniform = np.full((8, 16), 230, dtype=np.uint8)
    uniform[2:4, 2:4] = 30
    bw, threshold = apply_otsu(uniform)
    assert threshold == 30 and bw[0, 0] == 255 and bw[2, 2] == 0
    shadow = uniform.copy()
    shadow[:, :8] = 80
    shadow[2:4, 2:4] = 30
    bw_shadow, threshold_shadow = apply_otsu(shadow)
    assert threshold_shadow == 80
    assert bw_shadow[0, 0] == 0 and bw_shadow[0, 15] == 255
    assert bw_shadow[2, 2] == 0


@pytest.mark.parametrize('gray', [None, np.zeros((2, 2, 3), dtype=np.uint8),
    np.zeros((2, 2), dtype=np.uint16), np.zeros((2, 2), dtype=np.float32),
    np.zeros((1, 2), dtype=np.uint8), np.zeros((0, 2), dtype=np.uint8),
    np.zeros((2, 2401), dtype=np.uint8)])
def test_otsu_rejects_non_full_warp_grayscale(gray):
    with pytest.raises(EnhancementValidationError) as error:
        apply_otsu(gray)
    assert error.value.code == 'INVALID_RENDER'


def test_otsu_opencv_failure_has_stable_reason(monkeypatch):
    import cv2
    def fail(*args, **kwargs):
        raise cv2.error('simulated threshold failure')
    monkeypatch.setattr('app.processing.enhancement.cv2.threshold', fail)
    with pytest.raises(EnhancementValidationError) as error:
        apply_otsu(np.zeros((2, 2), dtype=np.uint8))
    assert error.value.code == 'THRESHOLD_FAILED'


def test_adaptive_uses_gaussian_weights_instead_of_mean_threshold():
    gray = np.array([[240, 0, 240], [0, 100, 0], [240, 0, 240]], dtype=np.uint8)
    bw = apply_adaptive_gaussian(gray, ThresholdConfig(block_size=3, c=10))
    # At center, Gaussian3 weights give mean=85, so t=75, and 100 becomes white.
    # An unweighted mean would give t≈107.8 and incorrectly make this pixel black.
    assert bw[1, 1] == 255
    assert set(np.unique(bw)) == {0, 255}


@pytest.mark.parametrize('c,expected', [(-20, 0), (0, 0), (1, 255), (30, 255)])
def test_adaptive_c_is_subtracted_from_local_mean_and_binary_equality_is_black(c, expected):
    bw = apply_adaptive_gaussian(np.full((3, 4), 100, dtype=np.uint8), ThresholdConfig(block_size=3, c=c))
    assert np.all(bw == expected)


def test_large_c_can_erase_a_faint_stroke_without_changing_the_source():
    gray = np.full((64, 64), 200, dtype=np.uint8)
    gray[:, 32] = 190
    before = gray.copy()
    low_c = apply_adaptive_gaussian(gray, ThresholdConfig(c=5))
    high_c = apply_adaptive_gaussian(gray, ThresholdConfig(c=20))
    assert low_c[32, 32] == 0 and high_c[32, 32] == 255
    assert np.all(low_c <= high_c)
    assert np.array_equal(gray, before)


@pytest.mark.parametrize('block_size', [31, 51, 151])
def test_adaptive_passes_block_and_c_and_keeps_independent_binary_output(monkeypatch, block_size):
    import cv2
    real_adaptive = cv2.adaptiveThreshold
    calls = []
    def checked(gray, max_value, method, polarity, block, c):
        calls.append((max_value, method, polarity, block, c))
        return real_adaptive(gray, max_value, method, polarity, block, c)
    monkeypatch.setattr('app.processing.enhancement.cv2.adaptiveThreshold', checked)
    gray = np.tile(np.arange(152, dtype=np.uint8), (151, 2))[:, ::2]
    gray.setflags(write=False)
    before = gray.copy()
    config = ThresholdConfig(block_size=block_size, c=5)
    bw = apply_adaptive_gaussian(gray, config)
    assert calls == [(255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, 5)]
    assert bw.dtype == np.uint8 and bw.shape == gray.shape
    assert set(np.unique(bw)) <= {0, 255}
    assert not np.shares_memory(bw, gray)
    assert bw.flags.c_contiguous and bw.flags.writeable
    bw[:] = 17
    assert np.array_equal(gray, before)
    assert config.block_size == block_size and config.c == 5


@pytest.mark.parametrize('shape,block', [((2, 2), 3), ((30, 64), 31), ((64, 50), 51)])
def test_adaptive_rejects_block_larger_than_actual_short_edge_before_opencv(monkeypatch, shape, block):
    def forbidden(*args, **kwargs):
        pytest.fail('Oversized block must not be silently clamped or processed')
    monkeypatch.setattr('app.processing.enhancement.cv2.adaptiveThreshold', forbidden)
    with pytest.raises(ConfigValidationError) as error:
        apply_adaptive_gaussian(np.full(shape, 200, dtype=np.uint8), ThresholdConfig(block_size=block))
    assert error.value.code == 'INVALID_CONFIG'
    assert 'block_size' in str(error.value)


@pytest.mark.parametrize('update', [{'method': 'otsu'}, {'method': 'adaptive_mean'},
    {'block_size': 4}, {'block_size': 153}, {'block_size': True}, {'block_size': '31'},
    {'c': True}, {'c': 10.0}, {'c': -21}, {'c': 31}])
def test_adaptive_revalidates_threshold_config_before_processing(monkeypatch, update):
    unsafe = ThresholdConfig().model_copy(update=update)
    def forbidden(*args, **kwargs):
        pytest.fail('Invalid/wrong-method config must fail before OpenCV')
    monkeypatch.setattr('app.processing.enhancement.cv2.adaptiveThreshold', forbidden)
    with pytest.raises(ConfigValidationError) as error:
        apply_adaptive_gaussian(np.zeros((64, 64), dtype=np.uint8), unsafe)
    assert error.value.code == 'INVALID_CONFIG'


@pytest.mark.parametrize('gray', [np.zeros((32, 32, 3), dtype=np.uint8), np.zeros((1, 32), dtype=np.uint8)])
def test_adaptive_checks_grayscale_before_block_fit(gray):
    with pytest.raises(EnhancementValidationError) as error:
        apply_adaptive_gaussian(gray, ThresholdConfig())
    assert error.value.code == 'INVALID_RENDER'


def test_adaptive_opencv_failure_has_stable_reason(monkeypatch):
    import cv2
    def fail(*args, **kwargs):
        raise cv2.error('simulated adaptive failure')
    monkeypatch.setattr('app.processing.enhancement.cv2.adaptiveThreshold', fail)
    with pytest.raises(EnhancementValidationError) as error:
        apply_adaptive_gaussian(np.zeros((32, 32), dtype=np.uint8), ThresholdConfig())
    assert error.value.code == 'THRESHOLD_FAILED'


@pytest.mark.parametrize('mode', ['color', 'gray', 'bw'])
@pytest.mark.parametrize('rotation', [0, 90, 180, 270])
def test_dispatcher_three_modes_four_clockwise_rotations_preserve_source_corners(mode, rotation):
    gray = np.array([[10, 20, 200, 220], [30, 40, 230, 240], [50, 60, 245, 250]], dtype=np.uint8)
    source = np.repeat(gray[:, :, None], 3, axis=2)
    source.setflags(write=False)
    corners = [[0.1, 0.1], [0.9, 0.15], [0.8, 0.9], [0.15, 0.85]]
    raw = {'mode': mode, 'rotation': rotation, 'corners': corners, 'confirmed': True,
           'denoise': {'method': 'none'}, 'contrast': {'method': 'none'}, 'threshold': {'method': 'otsu'}}
    config = parse_config(raw, source_size=(96, 64))
    before = config.model_dump(mode='json')
    result = enhance_document(source, config, source_size=(96, 64))
    expected = source if mode == 'color' else (gray if mode == 'gray' else np.where(gray > 60, 255, 0).astype(np.uint8))
    assert np.array_equal(result.image, np.rot90(expected, k=-(rotation // 90)))
    assert result.image.dtype == np.uint8 and result.image.flags.c_contiguous
    assert result.image.flags.writeable and not np.shares_memory(source, result.image)
    assert result.effective_config.model_dump(mode='json') == before
    assert config.model_dump(mode='json') == before
    assert result.otsu_threshold == (60.0 if mode == 'bw' else None)
    result.image[:] = 0
    assert np.array_equal(source[:, :, 0], gray)


@pytest.mark.parametrize('mode', ['color', 'gray'])
def test_inactive_contrast_or_threshold_never_runs_but_is_retained(mode, monkeypatch):
    raw = {'mode': mode, 'contrast': {'method': 'clahe' if mode == 'color' else 'none'},
           'threshold': {'block_size': 151, 'c': 30}}
    config = parse_config(raw)
    def forbidden(*args, **kwargs):
        pytest.fail('Inactive CLAHE/threshold must not run or enforce Adaptive fit')
    monkeypatch.setattr('app.processing.enhancement.cv2.createCLAHE', forbidden)
    monkeypatch.setattr('app.processing.enhancement.cv2.threshold', forbidden)
    monkeypatch.setattr('app.processing.enhancement.cv2.adaptiveThreshold', forbidden)
    result = enhance_document(np.full((2, 3, 3), 100, dtype=np.uint8), config)
    assert np.all(result.image == 100)
    assert result.effective_config.threshold.block_size == 151
    assert result.effective_config.contrast.method == config.contrast.method


@pytest.mark.parametrize('method', ['otsu', 'adaptive_gaussian'])
def test_dispatcher_orders_real_denoise_gray_clahe_threshold_and_rotation(method, monkeypatch):
    import app.processing.enhancement as module
    calls = []
    for name in ['apply_denoise', 'render_gray', 'apply_otsu', 'apply_adaptive_gaussian']:
        original = getattr(module, name)
        def traced(*args, _name=name, _original=original, **kwargs):
            calls.append(_name)
            return _original(*args, **kwargs)
        monkeypatch.setattr(module, name, traced)
    original_rotate = module.cv2.rotate
    def rotate(*args, **kwargs):
        calls.append('rotate')
        return original_rotate(*args, **kwargs)
    monkeypatch.setattr(module.cv2, 'rotate', rotate)
    gray = np.tile(np.arange(64, dtype=np.uint8), (40, 1))
    source = np.repeat(gray[:, :, None], 3, axis=2)
    config = parse_config({'mode': 'bw', 'rotation': 90, 'denoise': {'method': 'gaussian', 'kernel': 5},
                           'contrast': {'method': 'clahe'}, 'threshold': {'method': method}})
    result = enhance_document(source, config)
    assert calls == ['apply_denoise', 'render_gray', 'apply_' + method, 'rotate']
    assert result.image.shape == (64, 40) and set(np.unique(result.image)) <= {0, 255}
    assert (result.otsu_threshold is None) == (method != 'otsu')


@pytest.mark.parametrize('config', [
    get_preset().model_copy(update={'rotation': 45}),
    get_preset().model_copy(update={'contrast': ContrastConfig().model_copy(update={'clip_limit': float('nan')})}),
    get_preset('bw'),  # default Adaptive31 cannot fit actual 2x3 warp
])
def test_dispatcher_validates_full_config_and_actual_warp_before_filter(config, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail('Validation must finish before processing starts')
    monkeypatch.setattr('app.processing.enhancement.apply_denoise', forbidden)
    with pytest.raises(ConfigValidationError):
        enhance_document(np.zeros((2, 3, 3), dtype=np.uint8), config)


def test_dispatcher_requires_real_source_dimensions_for_nonnull_corners():
    config = parse_config({'corners': [[0, 0], [1, 0], [1, 1], [0, 1]]}, source_size=(200, 300))
    with pytest.raises(ConfigValidationError):
        enhance_document(np.zeros((3, 4, 3), dtype=np.uint8), config)


def test_dispatcher_repeated_renders_start_from_warp_instead_of_accumulating_filters():
    source = np.full((40, 64, 3), 230, dtype=np.uint8)
    source[8:12, 20:22] = 30
    before = source.copy()
    bw = enhance_document(source, get_preset('bw'))
    color1 = enhance_document(source, get_preset('color'))
    color2 = enhance_document(source, get_preset('color'))
    assert bw.image.ndim == 2
    assert np.array_equal(color1.image, before) and np.array_equal(color2.image, before)
    assert np.array_equal(source, before)


def test_dispatcher_rotation_failure_reports_reason(monkeypatch):
    import cv2
    def fail(*args, **kwargs):
        raise cv2.error('simulated rotate failure')
    monkeypatch.setattr('app.processing.enhancement.cv2.rotate', fail)
    with pytest.raises(EnhancementValidationError) as error:
        enhance_document(np.zeros((3, 4, 3), dtype=np.uint8), parse_config({'rotation': 90}))
    assert error.value.code == 'ROTATION_FAILED'
