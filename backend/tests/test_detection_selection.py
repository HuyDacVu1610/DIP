"""Ranking, polygon NMS and honest unconfirmed proposals."""
from dataclasses import replace

import cv2
import numpy as np
import pytest

from app.processing.detection import (
    ContourCandidate, DetectionValidationError, EdgeTrial, RegionTrial,
    deduplicate_candidates, describe_candidate,
)
from app.processing.geometry import pixel_to_normalized


SIZE = (201, 201)
SQUARE = ((20,20),(120,20),(120,120),(20,120))


def description(points=SQUARE, *, score=.7, kernel=5, region=False):
    edges = np.zeros(SIZE[::-1], dtype=np.uint8)
    cv2.polylines(edges, [np.array(points, dtype=np.int32)], True, 255, 1)
    prefix = 'canny' if kernel == 5 else 'canny_g3'
    support_id = f'{prefix}_20_60'
    trial = (RegionTrial(f'region_otsu_g{kernel}_{support_id}', (20,60), edges,
                        edges.copy(), 102., support_id, kernel) if region else
             EdgeTrial(support_id, (20,60), edges, edges.copy(), kernel))
    candidate = ContourCandidate(trial.trial_id, trial.thresholds, SIZE, SIZE, 0,
        tuple(points), .015, tuple(points),
        tuple(pixel_to_normalized(p, *SIZE) for p in points), None,
        trial.method, kernel, 102. if region else None, support_id if region else None)
    measured = describe_candidate(candidate, trial)
    return replace(measured, heuristic_score=score) if score is not None else measured


def test_nms_keeps_highest_scored_description_with_its_original_provenance():
    canny = description(score=.7)
    region = description(score=.8, kernel=3, region=True)
    kept = deduplicate_candidates((canny, region, canny))
    assert len(kept) == 1 and kept[0] is region
    assert kept[0].candidate.method == 'region_otsu'
    assert kept[0].candidate.gaussian_kernel == 3
    assert kept[0].candidate.otsu_threshold == 102.
    assert kept[0].candidate.trial_id == 'region_otsu_g3_canny_g3_20_60'
    assert kept[0].candidate.support_trial_id == 'canny_g3_20_60'
    assert kept[0].edge_supported_counts == region.edge_supported_counts
    assert canny.heuristic_score == .7  # no mutation or merging score/evidence


def test_nms_uses_strict_greater_than_point_95_and_sorts_survivors():
    first = description(score=.9)
    at_boundary = description(((20,20),(115,20),(115,120),(20,120)), score=.8)
    above_boundary = description(((20,20),(116,20),(116,120),(20,120)), score=.7)
    other = description(((130,130),(190,130),(190,190),(130,190)), score=.6)
    kept = deduplicate_candidates((other, above_boundary, at_boundary, first))
    assert len(kept) == 3
    assert all(a is b for a,b in zip(kept, (first,at_boundary,other)))


def test_equal_scores_keep_stable_input_order_and_empty_input_is_empty():
    first, second = description(), description(region=True)
    assert deduplicate_candidates(()) == ()
    assert deduplicate_candidates((first, second))[0] is first
    assert deduplicate_candidates((second, first))[0] is second


def test_nms_is_greedy_against_survivors_not_transitive_clustering():
    def shifted(dx, score):
        return description(tuple((x+dx,y) for x,y in SQUARE), score=score)
    a,b,c = shifted(0,.9), shifted(2,.8), shifted(4,.7)
    kept = deduplicate_candidates((b,c,a))
    assert len(kept) == 2 and kept[0] is a and kept[1] is c


@pytest.mark.parametrize('score', [float('nan'),float('inf'),-.1,1.1,True,'0.7'])
def test_nms_rejects_invalid_scores_even_for_a_singleton(score):
    with pytest.raises(DetectionValidationError) as error:
        deduplicate_candidates((description(score=score),))
    assert error.value.code == 'INVALID_CANDIDATE'


@pytest.mark.parametrize('change', [
    {'source_size':(402,402)}, {'analysis_size':(200,201)},
    {'corners':None}, {'rejection_reason':'NOT_QUADRILATERAL'},
])
def test_nms_refuses_mixed_coordinate_context_or_rejected_candidates(change):
    valid = description()
    invalid = replace(valid, candidate=replace(valid.candidate, **change))
    with pytest.raises(DetectionValidationError):
        deduplicate_candidates((valid, invalid))


@pytest.mark.parametrize('score,status,has_corners,warnings', [
    (0., 'manual_required', False, ('LOW_HEURISTIC_SCORE',)),
    (np.nextafter(.4, 0), 'manual_required', False, ('LOW_HEURISTIC_SCORE',)),
    (.4, 'proposed_with_warning', True, ('LOW_HEURISTIC_SCORE',)),
    (np.nextafter(.6, 0), 'proposed_with_warning', True, ('LOW_HEURISTIC_SCORE',)),
    (.6, 'proposed', True, ()),
    (1., 'proposed', True, ()),
])
def test_proposal_threshold_boundaries_never_confirm_a_page(score,status,has_corners,warnings):
    from app.processing.detection import select_proposal
    best = description(score=float(score))
    result = select_proposal((best,))
    assert result.status == status and result.warnings == warnings
    assert (result.corners is not None) == has_corners
    if has_corners:
        assert result.corners is best.candidate.corners
    assert result.selected is best and result.candidates[0] is best
    assert result.heuristic_score == score and result.confirmed is False


def test_no_quad_returns_manual_with_null_score_and_no_fabricated_corners():
    from app.processing.detection import select_proposal
    result = select_proposal(())
    assert result.status == 'manual_required'
    assert result.corners is None and result.heuristic_score is None
    assert result.selected is None and result.candidates == ()
    assert result.warnings == ('NO_VALID_QUAD',) and result.confirmed is False


def test_proposal_selects_best_after_dedup_and_keeps_manual_diagnostic_separate():
    from app.processing.detection import select_proposal
    low,high = description(score=.2), description(score=.3,region=True)
    result = select_proposal((low,high))
    assert result.status == 'manual_required' and result.corners is None
    assert result.selected is high and len(result.candidates) == 1
    assert result.selected.candidate.corners is not None  # evidence, not a proposal


@pytest.mark.parametrize('kind,expected', [
    ('rectangle', 'proposed'), ('blank', 'manual_required'),
    ('open', 'manual_required'),
])
def test_detector_runs_real_stages_preserves_source_and_never_confirms(kind, expected):
    from app.processing.detection import detect_document
    source = np.full((300,420,3), 25, dtype=np.uint8)
    if kind == 'rectangle':
        cv2.rectangle(source,(45,40),(375,260),(240,240,240),-1)
    elif kind == 'open':
        cv2.polylines(source,[np.array([(50,40),(370,40),(370,260),(50,260)])],False,(240,240,240),2)
    before = source.copy()
    source.setflags(write=False)
    result = detect_document(source)
    assert result.status == expected and result.confirmed is False
    assert np.array_equal(source,before)
    if kind == 'rectangle':
        assert result.corners is not None and result.heuristic_score >= .6
        pixels = np.array(result.corners)*(419,299)
        assert np.max(np.linalg.norm(pixels-np.array([(45,40),(375,40),(375,260),(45,260)]),axis=1)) < 4
        assert len(result.candidates) == 1
    else:
        assert result.corners is None and result.warnings == ('NO_VALID_QUAD',)


def test_detector_propagates_invalid_input_instead_of_disguising_it_as_manual():
    from app.processing.detection import detect_document
    with pytest.raises(DetectionValidationError) as error:
        detect_document(np.zeros((30,40),dtype=np.uint8))
    assert error.value.code == 'INVALID_SOURCE'


def test_detector_region_with_no_raw_support_is_only_a_warned_draft():
    from app.processing.detection import detect_document
    source = np.full((240,320,3),235,dtype=np.uint8)
    cv2.rectangle(source,(30,25),(290,215),(243,243,243),-1)
    result = detect_document(source)
    assert result.status == 'proposed_with_warning' and not result.confirmed
    assert result.warnings == ('LOW_HEURISTIC_SCORE',)
    assert result.selected.candidate.method == 'region_otsu'
    assert result.selected.candidate.support_trial_id == 'canny_20_60'
    assert result.selected.edge_support == 0 and result.heuristic_score < .6


def test_candidate_support_provenance_is_checked_and_nms_failure_is_explicit(monkeypatch):
    from app.processing.geometry import GeometryValidationError
    from app.processing.detection import collect_candidates, prepare_analysis
    source = np.full((240,320,3),235,dtype=np.uint8)
    cv2.rectangle(source,(30,25),(290,215),(243,243,243),-1)
    run = collect_candidates(prepare_analysis(source))[-1]
    candidate = run.batch.candidates[0]
    with pytest.raises(DetectionValidationError) as error:
        describe_candidate(replace(candidate,support_trial_id='canny_75_200'),run.trial)
    assert error.value.code == 'INVALID_CANDIDATE'
    def fail(*args):
        raise GeometryValidationError('POLYGON_IOU_FAILED','controlled failure')
    monkeypatch.setattr('app.processing.detection.polygon_iou',fail)
    with pytest.raises(DetectionValidationError) as error:
        deduplicate_candidates((description(), description()))
    assert error.value.code == 'NMS_FAILED'
