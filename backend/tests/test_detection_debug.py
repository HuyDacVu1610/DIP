"""Actual trial provenance, opt-in images and measured detector timings."""
from dataclasses import FrozenInstanceError, asdict
from hashlib import sha256

import cv2
import numpy as np
import pytest

from app.processing.detection import DetectionValidationError, RegionTrial, detect_document


def page(background=25, paper=240, small=False):
    source = np.full((240,320,3),background,dtype=np.uint8)
    start,end = ((85,60),(235,180)) if small else ((30,25),(290,215))
    cv2.rectangle(source,start,end,(paper,paper,paper),-1)
    return source


@pytest.mark.parametrize('region', [False,True])
def test_debug_uses_actual_selected_trial_dimensions_and_raw_source_hash(region):
    source = page(235,243) if region else page()
    original = source.copy()
    source.setflags(write=False)
    result = detect_document(source,debug=True)
    debug = result.debug
    assert debug.algorithm_version == 'detect-v1'
    assert debug.preset == 'revised' and debug.source_bgr_sha256 == sha256(source.tobytes()).hexdigest()
    assert debug.analysis.source_size == (320,240) and debug.analysis.analysis_size == (320,240)
    selected = result.selected.candidate
    trial = debug.selected_trial
    assert trial is next(run.trial for run in debug.trials if run.trial.trial_id==selected.trial_id)
    assert (selected.thresholds,selected.method,selected.gaussian_kernel)==(trial.thresholds,trial.method,trial.gaussian_kernel)
    assert debug.overlay.shape == source.shape and debug.overlay.dtype==np.uint8
    assert not np.shares_memory(debug.overlay,source) and not np.shares_memory(debug.overlay,debug.analysis.bgr)
    assert debug.overlay_kind == 'proposal' and np.array_equal(source,original)
    if region:
        assert isinstance(trial,RegionTrial) and len(debug.trials)==4
        assert selected.otsu_threshold==trial.otsu_threshold
        assert selected.support_trial_id==trial.support_trial_id=='canny_20_60'
        assert np.any(trial.mask) and not trial.edges.any() and result.selected.edge_support==0
        assert np.array_equal(trial.mask,np.where(debug.analysis.blurred>trial.otsu_threshold,255,0).astype(np.uint8))
    else:
        assert len(debug.trials)==3
        assert np.array_equal(trial.edges,cv2.Canny(debug.analysis.blurred,*trial.thresholds,apertureSize=3,L2gradient=True))
    assert result.confirmed is False
    with pytest.raises(FrozenInstanceError):
        debug.preset='baseline'


def test_debug_for_no_quad_keeps_real_stages_without_a_fake_overlay():
    source = np.full((100,140,3),200,dtype=np.uint8)
    result = detect_document(source,debug=True)
    assert result.status=='manual_required' and result.corners is None and result.heuristic_score is None
    assert result.debug.selected_trial is None and result.debug.overlay_kind=='none'
    assert np.array_equal(result.debug.overlay,result.debug.analysis.bgr)
    assert len(result.debug.trials)==4
    assert result.debug.trials[-1].batch.rejection_reason=='UNIFORM_REGION_MASK'


def test_low_score_quad_overlay_is_diagnostic_only_and_never_proposed():
    result = detect_document(page(235,243,small=True),debug=True)
    assert result.status=='manual_required' and result.corners is None
    assert result.selected is not None and result.heuristic_score < .4
    assert result.debug.overlay_kind=='diagnostic' and result.debug.selected_trial is not None
    assert result.confirmed is False


@pytest.mark.parametrize('enabled',[False,True])
def test_timings_use_adjacent_monotonic_stamps_without_double_counting(monkeypatch,enabled):
    stamps = iter((0,1_000_000,3_000_000,6_000_000,10_000_000,15_000_000))
    monkeypatch.setattr('app.processing.detection.perf_counter_ns',lambda:next(stamps))
    result = detect_document(page(),debug=enabled)
    actual = asdict(result.timings_ms)
    assert actual=={'preprocess':1.,'candidates':2.,'describe':3.,'select':4.,
                    'debug':5. if enabled else 0.,'total':15. if enabled else 10.}
    assert actual['total']==sum(value for key,value in actual.items() if key!='total')
    assert (result.debug is not None)==enabled


def test_debug_does_not_change_decision_and_baseline_is_explicit():
    source = page()
    plain,observed = detect_document(source),detect_document(source,debug=True)
    assert (plain.status,plain.corners,plain.heuristic_score,plain.warnings)==(
        observed.status,observed.corners,observed.heuristic_score,observed.warnings)
    assert plain.debug is None
    values = asdict(observed.timings_ms)
    assert all(np.isfinite(v) and v>=0 for v in values.values())
    assert values['total']==pytest.approx(sum(v for k,v in values.items() if k!='total'))
    baseline = detect_document(source,debug=True,preset='baseline')
    assert baseline.debug.preset=='baseline'
    assert [r.trial.thresholds for r in baseline.debug.trials]==[(50,150),(75,200),(100,250)]
    assert all(not isinstance(r.trial,RegionTrial) for r in baseline.debug.trials)


@pytest.mark.parametrize('kwargs',[{'debug':'false'},{'preset':'unknown'}])
def test_invalid_debug_options_are_explicit(kwargs):
    with pytest.raises(DetectionValidationError) as error:
        detect_document(page(),**kwargs)
    assert error.value.code=='INVALID_ANALYSIS_CONFIG'


def test_overlay_failure_is_reported_instead_of_disguised_as_manual(monkeypatch):
    def fail(*args,**kwargs):
        raise cv2.error('controlled overlay failure')
    monkeypatch.setattr('app.processing.detection.cv2.polylines',fail)
    with pytest.raises(DetectionValidationError) as error:
        detect_document(page(),debug=True)
    assert error.value.code=='DEBUG_FAILED'
