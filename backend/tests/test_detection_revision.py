"""Revision experiments become bounded, traceable candidate generation."""
from dataclasses import replace

import cv2
import numpy as np
import pytest

from app.processing.detection import (DetectionValidationError, RegionTrial, collect_candidates,
    create_edge_trials, create_region_trial, describe_candidate, generate_candidates, prepare_analysis)


def low_contrast_page(background=220, paper=248):
    source=np.full((240,320,3),background,dtype=np.uint8)
    source[25:216,30:291]=paper
    return source


def test_analysis_retains_gaussian5_baseline_and_allows_explicit_gaussian3_ablation():
    source=np.zeros((9,9,3),dtype=np.uint8)
    source[4,4]=255
    baseline=prepare_analysis(source)
    smaller=prepare_analysis(source,gaussian_kernel=3)
    assert baseline.gaussian_kernel==5 and baseline.blurred[4,4]==36
    assert smaller.gaussian_kernel==3 and smaller.blurred[4,4]==64
    assert np.array_equal(smaller.gray,baseline.gray)
    assert not np.shares_memory(smaller.blurred,source)
    assert source[4,4,0]==255


@pytest.mark.parametrize('kernel',[None,True,3.0,1,4,7])
def test_analysis_rejects_unknown_gaussian_presets(kernel):
    with pytest.raises(DetectionValidationError) as error:
        prepare_analysis(np.zeros((8,8,3),dtype=np.uint8),gaussian_kernel=kernel)
    assert error.value.code=='INVALID_ANALYSIS_CONFIG'


@pytest.mark.parametrize('kernel',[3,5])
def test_revised_edges_are_exactly_three_pairs_and_keep_raw_buffers_and_kernel_provenance(kernel):
    analysis=prepare_analysis(low_contrast_page(),gaussian_kernel=kernel)
    trials=create_edge_trials(analysis.blurred,preset='revised',gaussian_kernel=kernel)
    assert tuple(t.thresholds for t in trials)==((20,60),(50,150),(75,200))
    assert all(t.gaussian_kernel==kernel and t.method=='canny' for t in trials)
    assert trials[0].trial_id==('canny_20_60' if kernel==5 else 'canny_g3_20_60')
    for t in trials:
        expected=cv2.Canny(analysis.blurred,*t.thresholds,apertureSize=3,L2gradient=True)
        assert np.array_equal(t.edges,expected)
        assert not np.shares_memory(t.closed,t.edges)
    assert trials[0].edges.any() and not trials[1].edges.any()


def test_baseline_edge_preset_remains_reproducible():
    analysis=prepare_analysis(low_contrast_page())
    defaults=create_edge_trials(analysis.blurred)
    baseline=create_edge_trials(analysis.blurred,preset='baseline')
    assert tuple(t.thresholds for t in baseline)==((50,150),(75,200),(100,250))
    assert all(np.array_equal(a.edges,b.edges) and np.array_equal(a.closed,b.closed) for a,b in zip(defaults,baseline))


@pytest.mark.parametrize('preset,kernel',[('unknown',5),('revised',True),('revised',3.0),('baseline',7)])
def test_edge_trial_configuration_is_bounded(preset,kernel):
    with pytest.raises(DetectionValidationError) as error:
        create_edge_trials(np.zeros((8,8),dtype=np.uint8),preset=preset,gaussian_kernel=kernel)
    assert error.value.code=='INVALID_ANALYSIS_CONFIG'


def test_revised_collector_recovers_weak_page_and_does_not_run_region_when_canny_has_quad(monkeypatch):
    source=low_contrast_page()
    source.setflags(write=False)
    analysis=prepare_analysis(source)
    assert all(not result.batch.candidates for result in collect_candidates(analysis,preset='baseline'))
    def forbidden(*args):
        pytest.fail('Region is a bounded candidate fallback, not another unconditional competitor')
    monkeypatch.setattr('app.processing.detection.create_region_trial',forbidden)
    results=collect_candidates(analysis)
    assert len(results)==3 and all(result.trial.method=='canny' for result in results)
    recovered=results[0]
    assert recovered.trial.thresholds==(20,60) and recovered.batch.candidates
    candidate=recovered.batch.candidates[0]
    assert candidate.method=='canny' and candidate.gaussian_kernel==5 and candidate.otsu_threshold is None
    measured=describe_candidate(candidate,recovered.trial)
    assert measured.edge_support > .9 and .6 < measured.area_ratio < .7
    assert np.array_equal(source,low_contrast_page())


def test_otsu_fallback_recovers_region_but_raw_missing_edges_are_not_invented():
    analysis=prepare_analysis(low_contrast_page(background=235,paper=243))
    results=collect_candidates(analysis)
    assert len(results)==4 and all(not r.batch.candidates for r in results[:3])
    region=results[-1]
    assert isinstance(region.trial,RegionTrial) and region.trial.method=='region_otsu'
    assert region.batch.candidates and region.trial.support_trial_id==results[0].trial.trial_id
    assert region.trial.thresholds==(20,60) and 235 <= region.trial.otsu_threshold <= 243
    assert not region.trial.edges.any()
    candidate=region.batch.candidates[0]
    assert candidate.method=='region_otsu' and candidate.otsu_threshold==region.trial.otsu_threshold
    measured=describe_candidate(candidate,region.trial)
    assert measured.edge_support==0 and measured.edge_supported_counts==(0,0,0,0)
    assert measured.heuristic_score==pytest.approx(.45*measured.area_ratio+.20*measured.fit_area_ratio)
    assert measured.heuristic_score < .6  # candidate existence is not automatic success


def test_region_uses_external_components_and_ignores_interior_holes_without_filling_mask():
    source=low_contrast_page(background=80,paper=220)
    source[65:100,90:140]=20
    analysis=prepare_analysis(source)
    edge=create_edge_trials(analysis.blurred,preset='revised')[0]
    before=edge.edges.copy()
    region=create_region_trial(analysis,edge)
    assert region.mask[80,110]==0 and region.mask[40,50]==255
    assert np.array_equal(region.edges,before) and not np.shares_memory(region.edges,edge.edges)
    batch=generate_candidates(analysis,region)
    assert batch.total_contours==1 and len(batch.candidates)==3
    assert all(c.polygon_vertex_count==4 and c.method=='region_otsu' for c in batch.candidates)
    assert region.otsu_threshold==cv2.threshold(analysis.blurred,0,255,cv2.THRESH_BINARY|cv2.THRESH_OTSU)[0]
    assert np.array_equal(edge.edges,before)


@pytest.mark.parametrize('value',[0,200,255])
def test_uniform_masks_remain_visible_but_never_turn_into_a_fake_page(value):
    results=collect_candidates(prepare_analysis(np.full((80,100,3),value,dtype=np.uint8)))
    assert len(results)==4 and not any(result.batch.candidates for result in results)
    region=results[-1]
    assert set(np.unique(region.trial.mask))==({0} if value==0 else {255})
    assert region.batch.rejection_reason=='UNIFORM_REGION_MASK' and region.batch.attempts==()


@pytest.mark.parametrize('kernel',[3,5])
def test_region_and_candidates_retain_matching_gaussian_provenance(kernel):
    analysis=prepare_analysis(low_contrast_page(),gaussian_kernel=kernel)
    edge=create_edge_trials(analysis.blurred,preset='revised',gaussian_kernel=kernel)[0]
    region=create_region_trial(analysis,edge)
    candidate=generate_candidates(analysis,region).candidates[0]
    assert candidate.gaussian_kernel==region.gaussian_kernel==analysis.gaussian_kernel==kernel
    assert region.trial_id==f'region_otsu_g{kernel}_{edge.trial_id}'
    assert describe_candidate(candidate,region).candidate is candidate
    with pytest.raises(DetectionValidationError):
        generate_candidates(replace(analysis,gaussian_kernel=3 if kernel==5 else 5),region)


@pytest.mark.parametrize('change',[{'method':'canny'},{'gaussian_kernel':3},{'otsu_threshold':0}])
def test_region_description_rejects_mixed_candidate_provenance(change):
    analysis=prepare_analysis(low_contrast_page())
    region=create_region_trial(analysis,create_edge_trials(analysis.blurred,preset='revised')[0])
    candidate=generate_candidates(analysis,region).candidates[0]
    with pytest.raises(DetectionValidationError) as error:
        describe_candidate(replace(candidate,**change),region)
    assert error.value.code=='INVALID_CANDIDATE'


@pytest.mark.parametrize('change',[{'otsu_threshold':float('nan')},{'trial_id':'canny_20_60'},
    {'mask':np.full((240,320),17,dtype=np.uint8)},{'support_trial_id':'canny_75_200'}])
def test_invalid_region_metadata_or_mask_is_rejected(change):
    analysis=prepare_analysis(low_contrast_page())
    region=create_region_trial(analysis,create_edge_trials(analysis.blurred,preset='revised')[0])
    with pytest.raises(DetectionValidationError) as error:
        generate_candidates(analysis,replace(region,**change))
    assert error.value.code=='INVALID_TRIAL'


def test_region_wraps_threshold_failure_and_rejects_mismatched_support(monkeypatch):
    analysis=prepare_analysis(low_contrast_page())
    edge=create_edge_trials(analysis.blurred,preset='revised')[0]
    with pytest.raises(DetectionValidationError):
        create_region_trial(analysis,replace(edge,gaussian_kernel=3))
    def fail(*args,**kwargs):
        raise cv2.error('simulated threshold failure')
    monkeypatch.setattr('app.processing.detection.cv2.threshold',fail)
    with pytest.raises(DetectionValidationError) as error:
        create_region_trial(analysis,edge)
    assert error.value.code=='REGION_FAILED'
