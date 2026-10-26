"""Detection derivatives, contour candidates and measured heuristic descriptors."""
from dataclasses import replace
from math import ceil, pi

import cv2
import numpy as np
import pytest

from app.processing.detection import DetectionValidationError, EdgeTrial, create_edge_trials, describe_candidate, generate_candidates, prepare_analysis
from app.processing.geometry import GeometryValidationError


@pytest.mark.parametrize('shape,expected', [((2048,1536), (1200,900)), ((1536,2048), (900,1200)),
    ((1001,2000), (601,1200)), ((63,95), (63,95)), ((2,2), (2,2))])
def test_analysis_uses_actual_resize_dimensions_without_upscale_or_mutating_source(shape, expected):
    source = np.full((*shape,3), [17,83,201], dtype=np.uint8)
    source.setflags(write=False)
    result = prepare_analysis(source)
    assert result.source_size == (shape[1],shape[0])
    assert result.analysis_size == (expected[1],expected[0])
    assert result.bgr.shape == (*expected,3)
    assert result.gray.shape == result.blurred.shape == expected
    assert np.all(result.bgr == [17,83,201])
    assert np.all(result.gray == 111) and np.all(result.blurred == 111)
    for array in [result.bgr,result.gray,result.blurred]:
        assert array.dtype == np.uint8 and array.flags.c_contiguous and array.flags.writeable
        assert not np.shares_memory(source,array)
    result.bgr[:] = 0
    result.gray[:] = 0
    assert np.all(result.blurred == 111) and np.all(source == [17,83,201])


def test_analysis_explicit_gaussian5_sigma0_reflect101_smooths_impulse_after_gray(monkeypatch):
    import cv2
    real_gaussian = cv2.GaussianBlur
    calls = []
    def checked(gray, kernel, sigmaX, *, borderType):
        assert gray.ndim == 2 and gray.dtype == np.uint8
        calls.append((kernel,sigmaX,borderType))
        return real_gaussian(gray,kernel,sigmaX,borderType=borderType)
    monkeypatch.setattr('app.processing.detection.cv2.GaussianBlur',checked)
    source = np.zeros((9,9,3),dtype=np.uint8)
    source[4,4] = 255
    result = prepare_analysis(source[:,::-1])
    assert calls == [((5,5),0,cv2.BORDER_REFLECT_101)]
    assert result.gray[4,4] == 255
    assert result.blurred[4,4] == 36 and result.blurred[4,3] > 0
    assert result.gray[4,3] == 0 and source[4,4,0] == 255


def test_analysis_to_source_uses_w_minus_1_h_minus_1_instead_of_theoretical_resize_ratio():
    result = prepare_analysis(np.zeros((1001,2000,3),dtype=np.uint8))
    assert result.analysis_size == (1200,601)
    assert result.to_source((0,0)) == (0.0,0.0)
    assert result.to_source((1199,600)) == (1999.0,1000.0)
    assert result.to_source((599.5,300)) == (999.5,500.0)
    point = result.to_source((100.25,150.5))
    assert point == pytest.approx((100.25/1199*1999,150.5/600*1000))
    assert point[0] != pytest.approx(100.25/0.6)  # actual W-1 differs from dividing by r


@pytest.mark.parametrize('point', [(-1,0),(1200,0),(0,601),(float('nan'),1)])
def test_analysis_mapping_keeps_shared_geometry_bounds(point):
    result = prepare_analysis(np.zeros((1001,2000,3),dtype=np.uint8))
    with pytest.raises(GeometryValidationError):
        result.to_source(point)


@pytest.mark.parametrize('source', [None, np.zeros((2,2),dtype=np.uint8),
    np.zeros((2,2,4),dtype=np.uint8), np.zeros((2,2,3),dtype=np.float32),
    np.zeros((1,2,3),dtype=np.uint8), np.zeros((0,2,3),dtype=np.uint8)])
def test_analysis_rejects_inputs_outside_normalized_source_contract(source):
    with pytest.raises(DetectionValidationError) as error:
        prepare_analysis(source)
    assert error.value.code == 'INVALID_SOURCE'


def test_analysis_rejects_over_16mp_before_resize(monkeypatch):
    source = np.broadcast_to(np.zeros((1,1,3),dtype=np.uint8),(4001,4000,3))
    def forbidden(*args,**kwargs):
        pytest.fail('Source quota must be checked before resizing')
    monkeypatch.setattr('app.processing.detection.resize_to_max_edge',forbidden)
    with pytest.raises(DetectionValidationError) as error:
        prepare_analysis(source)
    assert error.value.code == 'TOO_MANY_PIXELS'


def test_analysis_rejects_one_pixel_short_side_after_resize_without_distorting_aspect():
    with pytest.raises(DetectionValidationError) as error:
        prepare_analysis(np.zeros((2,4800,3),dtype=np.uint8))
    assert error.value.code == 'ANALYSIS_TOO_SMALL'


def test_analysis_wraps_opencv_failure(monkeypatch):
    import cv2
    def fail(*args,**kwargs):
        raise cv2.error('simulated preprocessing failure')
    monkeypatch.setattr('app.processing.detection.cv2.cvtColor',fail)
    with pytest.raises(DetectionValidationError) as error:
        prepare_analysis(np.zeros((5,7,3),dtype=np.uint8))
    assert error.value.code == 'ANALYSIS_FAILED'


def test_trials_use_exactly_three_fixed_pairs_aperture3_l2_and_one_closing(monkeypatch):
    import cv2
    real_canny, real_morph = cv2.Canny, cv2.morphologyEx
    calls, closes = [], []
    def canny(gray, low, high, *, apertureSize, L2gradient):
        calls.append((low,high,apertureSize,L2gradient))
        return real_canny(gray,low,high,apertureSize=apertureSize,L2gradient=L2gradient)
    def morphology(edges, operation, kernel, *, iterations, borderType):
        closes.append((operation,kernel.copy(),iterations,borderType))
        return real_morph(edges,operation,kernel,iterations=iterations,borderType=borderType)
    def forbidden(*args,**kwargs):
        pytest.fail('Edge trials must consume the already prepared blur without extra Gaussian')
    monkeypatch.setattr('app.processing.detection.cv2.Canny',canny)
    monkeypatch.setattr('app.processing.detection.cv2.morphologyEx',morphology)
    monkeypatch.setattr('app.processing.detection.cv2.GaussianBlur',forbidden)
    trials = create_edge_trials(np.zeros((8,12),dtype=np.uint8))
    assert isinstance(trials,tuple) and len(trials) == 3
    assert calls == [(50,150,3,True),(75,200,3,True),(100,250,3,True)]
    assert [trial.trial_id for trial in trials] == ['canny_50_150','canny_75_200','canny_100_250']
    assert [trial.thresholds for trial in trials] == [(50,150),(75,200),(100,250)]
    assert len(closes) == 3
    for operation,kernel,iterations,border in closes:
        assert operation == cv2.MORPH_CLOSE and np.array_equal(kernel,np.ones((3,3),dtype=np.uint8))
        assert iterations == 1 and border == cv2.BORDER_CONSTANT
    assert all(not trial.edges.any() and not trial.closed.any() for trial in trials)


def test_canny_rectangle_has_white_boundary_on_black_and_independent_stages():
    source = np.zeros((80,100,3),dtype=np.uint8)
    source[20:60,30:70] = 255
    analysis = prepare_analysis(source)
    before = analysis.blurred.copy()
    analysis.blurred.setflags(write=False)
    trials = create_edge_trials(analysis.blurred[:,::-1])  # readonly, strided
    all_arrays = [trial.edges for trial in trials] + [trial.closed for trial in trials]
    for trial in trials:
        assert trial.edges[40,28:32].max() == 255
        assert not trial.edges[:10].any() and trial.edges[40,50] == 0
        for array in [trial.edges,trial.closed]:
            assert array.shape == (80,100) and array.dtype == np.uint8
            assert set(np.unique(array)) == {0,255}
            assert array.flags.c_contiguous and array.flags.writeable
            assert not np.shares_memory(array,analysis.blurred)
    for index,array in enumerate(all_arrays):
        assert all(not np.shares_memory(array,other) for other in all_arrays[index+1:])
    trials[0].closed[:] = 17
    assert set(np.unique(trials[0].edges)) == {0,255}
    assert np.array_equal(analysis.blurred,before)
    assert source[40,50,0] == 255


def test_closing_bridges_only_small_white_edge_gap_and_keeps_raw_evidence(monkeypatch):
    raw = np.zeros((18,22),dtype=np.uint8)
    raw[5,3:8] = raw[5,10:18] = 255  # gap of two pixels
    raw[12,3:8] = raw[12,12:18] = 255  # gap of four pixels
    def canny(*args,**kwargs):
        return raw.copy()
    monkeypatch.setattr('app.processing.detection.cv2.Canny',canny)
    for trial in create_edge_trials(np.zeros(raw.shape,dtype=np.uint8)):
        assert np.array_equal(trial.edges,raw)
        assert np.all(trial.closed[5,8:10] == 255)
        assert np.all(trial.edges[5,8:10] == 0)
        assert np.all(trial.closed[12,8:12] == 0)
    assert np.all(raw[5,8:10] == 0)


@pytest.mark.parametrize('blurred', [None, np.zeros((2,2,3),dtype=np.uint8),
    np.zeros((2,2),dtype=np.float32), np.zeros((2,2),dtype=np.uint16),
    np.zeros((1,2),dtype=np.uint8), np.zeros((0,2),dtype=np.uint8),
    np.zeros((2,1201),dtype=np.uint8)])
def test_trials_reject_inputs_outside_analysis_gray_contract(blurred):
    with pytest.raises(DetectionValidationError) as error:
        create_edge_trials(blurred)
    assert error.value.code == 'INVALID_ANALYSIS'


def test_trials_accept_minimum_analysis_with_default_border_padding():
    trials = create_edge_trials(np.full((2,2),100,dtype=np.uint8))
    assert len(trials) == 3
    assert all(trial.edges.shape == (2,2) and not trial.edges.any() and not trial.closed.any() for trial in trials)


@pytest.mark.parametrize('function_name', ['Canny','morphologyEx'])
def test_trials_wrap_opencv_failure_without_returning_partial_success(monkeypatch,function_name):
    import cv2
    def fail(*args,**kwargs):
        raise cv2.error('simulated edge failure')
    monkeypatch.setattr('app.processing.detection.cv2.'+function_name,fail)
    with pytest.raises(DetectionValidationError) as error:
        create_edge_trials(np.zeros((8,12),dtype=np.uint8))
    assert error.value.code == 'EDGE_FAILED'


def candidate_fixture(points, *, size=(200,160)):
    """Controlled filled map; real contour tracing/approximation/geometry run."""
    import cv2
    analysis = prepare_analysis(np.zeros((size[1],size[0],3),dtype=np.uint8))
    mask = np.zeros((size[1],size[0]),dtype=np.uint8)
    cv2.fillPoly(mask,[np.array(points,dtype=np.int32)],255)
    trial = EdgeTrial('canny_50_150',(50,150),mask.copy(),mask)
    return analysis,trial


@pytest.mark.parametrize('points', [
    [(20,20),(180,20),(180,140),(20,140)],
    [(100,10),(190,80),(100,150),(10,80)],
    [(20,20),(175,35),(150,140),(40,120)],
])
def test_candidates_preserve_ordered_contour_polygon_and_valid_quads_without_right_angle_gate(points):
    from app.processing.geometry import validate_quad
    analysis,trial = candidate_fixture(points)
    before = trial.closed.copy()
    trial.closed.setflags(write=False)
    batch = generate_candidates(analysis,trial)
    assert batch.trial_id == trial.trial_id and batch.analysis_size == (200,160)
    assert batch.total_contours == batch.considered_contours == 1
    assert len(batch.candidates) == len(batch.attempts) == 3
    assert {c.epsilon_ratio for c in batch.candidates} == {0.015,0.02,0.03}
    for candidate in batch.candidates:
        assert candidate.polygon_vertex_count == 4 and candidate.rejection_reason is None
        assert candidate.analysis_size == (200,160) and candidate.source_size == (200,160)
        assert candidate.contour_index == 0 and len(candidate.contour_px) >= 4
        assert set(candidate.polygon_px) == set(map(tuple,points))
        assert len(validate_quad(candidate.corners,200,160)) == 4
    assert np.array_equal(trial.closed,before)


def test_candidate_retrieval_uses_list_simple_and_exactly_three_perimeter_epsilons(monkeypatch):
    import cv2
    analysis,trial = candidate_fixture([(20,20),(180,20),(180,140),(20,140)])
    real_find,real_approx = cv2.findContours,cv2.approxPolyDP
    epsilons=[]
    def find(image,mode,method):
        assert np.array_equal(image,trial.closed)
        assert mode == cv2.RETR_LIST and method == cv2.CHAIN_APPROX_SIMPLE
        return real_find(image,mode,method)
    def approx(contour,epsilon,closed):
        assert closed is True
        epsilons.append(epsilon/cv2.arcLength(contour,True))
        return real_approx(contour,epsilon,closed)
    monkeypatch.setattr('app.processing.detection.cv2.findContours',find)
    monkeypatch.setattr('app.processing.detection.cv2.approxPolyDP',approx)
    generate_candidates(analysis,trial)
    assert epsilons == pytest.approx([0.015,0.02,0.03])


def test_candidate_limit_keeps_largest_thirty_contours_and_bounds_attempts(monkeypatch):
    contours=[]
    for side in range(30,70):
        contours.append(np.array([[[10,10]],[[10+side,10]],[[10+side,10+side]],[[10,10+side]]],dtype=np.int32))
    monkeypatch.setattr('app.processing.detection.cv2.findContours',lambda *args:(contours,None))
    analysis,trial = candidate_fixture([(5,5),(90,5),(90,90),(5,90)],size=(100,100))
    batch=generate_candidates(analysis,trial)
    assert batch.total_contours == 40 and batch.considered_contours == 30
    assert len(batch.attempts) == 90
    assert {item.contour_index for item in batch.attempts} == set(range(10,40))
    assert batch.attempts[0].contour_index == 39


@pytest.mark.parametrize('polygon,reason', [
    ([(20,20),(180,140),(180,20),(20,140)],'SELF_INTERSECTION'),
    ([(20,20),(180,20),(60,60),(20,140)],'NON_CONVEX_QUAD'),
    ([(20,20),(100,20),(180,20),(20,140)],'DEGENERATE_QUAD'),
    ([(20,20),(180,20),(180,20),(20,140)],'DUPLICATE_POINTS'),
    ([(20,20),(180,20),(100,140)],'NOT_QUADRILATERAL'),
    ([(20,20),(180,20),(180,140),(20,140),(10,80)],'NOT_QUADRILATERAL'),
])
def test_bad_approximations_keep_polygon_and_reason_without_sorting_them_into_valid_quads(monkeypatch,polygon,reason):
    analysis,trial=candidate_fixture([(20,20),(180,20),(180,140),(20,140)])
    monkeypatch.setattr('app.processing.detection.cv2.approxPolyDP',lambda *args:np.array(polygon,dtype=np.int32).reshape(-1,1,2))
    batch=generate_candidates(analysis,trial)
    assert not batch.candidates and len(batch.attempts) == 3
    assert all(item.rejection_reason == reason for item in batch.attempts)
    assert all(item.polygon_px == tuple(map(tuple,polygon)) and item.corners is None for item in batch.attempts)


def test_small_contour_is_rejected_before_approximation(monkeypatch):
    analysis,trial=candidate_fixture([(20,20),(30,20),(30,30),(20,30)])
    def forbidden(*args):
        pytest.fail('Area below ten percent must not consume epsilon attempts')
    monkeypatch.setattr('app.processing.detection.cv2.approxPolyDP',forbidden)
    batch=generate_candidates(analysis,trial)
    assert not batch.candidates and len(batch.attempts) == 1
    assert batch.attempts[0].rejection_reason == 'CONTOUR_AREA_TOO_SMALL'


def test_detector_short_edge_gate_is_stronger_than_general_geometry_gate(monkeypatch):
    polygon=[(20,20),(24,20),(180,140),(20,140)]
    analysis,trial=candidate_fixture([(20,20),(180,20),(180,140),(20,140)])
    monkeypatch.setattr('app.processing.detection.cv2.approxPolyDP',lambda *args:np.array(polygon,dtype=np.int32).reshape(-1,1,2))
    assert all(c.rejection_reason == 'QUAD_EDGE_TOO_SHORT' for c in generate_candidates(analysis,trial).attempts)


def test_auto_start_uses_original_source_pixel_metric_after_anisotropic_rounding(monkeypatch):
    import cv2
    analysis=prepare_analysis(np.zeros((1001,2000,3),dtype=np.uint8))
    polygon=[(600,0),(1100,300),(600,600),(100,500)]
    mask=np.zeros((601,1200),dtype=np.uint8)
    cv2.fillPoly(mask,[np.array(polygon)],255)
    trial=EdgeTrial('canny_50_150',(50,150),mask.copy(),mask)
    monkeypatch.setattr('app.processing.detection.cv2.approxPolyDP',lambda *args:np.array(polygon,dtype=np.int32).reshape(-1,1,2))
    batch=generate_candidates(analysis,trial)
    assert len(batch.candidates) == 3
    assert batch.candidates[0].corners[0] == pytest.approx((100/1199,500/600))


def test_blank_trial_returns_empty_batch_and_bad_trial_map_is_not_accepted():
    analysis=prepare_analysis(np.zeros((80,100,3),dtype=np.uint8))
    blank=np.zeros((80,100),dtype=np.uint8)
    batch=generate_candidates(analysis,EdgeTrial('canny_50_150',(50,150),blank,blank.copy()))
    assert batch.total_contours == 0 and batch.attempts == () and batch.candidates == ()
    with pytest.raises(DetectionValidationError):
        generate_candidates(analysis,EdgeTrial('canny_50_150',(50,150),blank,np.full((80,100),17,dtype=np.uint8)))


def scoring_fixture(points=None):
    points = points or [(20,20),(180,20),(180,140),(20,140)]
    analysis,trial = candidate_fixture(points)
    candidate = generate_candidates(analysis,trial).candidates[0]
    edges = np.zeros_like(trial.edges)
    cv2.polylines(edges,[np.array(points)],True,255,1)
    return candidate,replace(trial,edges=edges)


def brute_edge_counts(candidate,edges):
    """Independent small-fixture oracle: distances to every white pixel center."""
    from app.processing.geometry import validate_quad
    quad = np.array(validate_quad(candidate.corners,*candidate.analysis_size))
    white = np.argwhere(edges != 0)[:,::-1]
    counts,supported,border = [],[],0
    for start,end in zip(quad,np.roll(quad,-1,axis=0)):
        samples = np.linspace(start,end,max(2,ceil(np.linalg.norm(end-start)/2)+1))
        counts.append(len(samples))
        supported.append(sum(any(np.linalg.norm(pixel-p) <= 2 for pixel in white) for p in samples))
        width,height=candidate.analysis_size
        border += sum(min(p[0],p[1],width-1-p[0],height-1-p[1]) <= 2 for p in samples)
    return tuple(counts),tuple(supported),border


def test_rectangle_descriptors_have_analysis_units_and_exact_score_components():
    candidate,trial=scoring_fixture()
    trial.edges.setflags(write=False)
    trial.closed.setflags(write=False)
    result=describe_candidate(candidate,trial)
    assert result.candidate is candidate
    assert result.contour_perimeter_px == pytest.approx(560)
    assert result.polygon_vertex_count == 4
    assert result.quad_edge_lengths_px == pytest.approx((160,120,160,120))
    assert result.quad_turn_angles_rad == pytest.approx((pi/2,)*4)
    assert result.is_convex and not result.self_intersects
    assert result.area_ratio == pytest.approx(19200/32000)
    assert result.fit_area_ratio == 1
    assert result.edge_sample_counts == result.edge_supported_counts == (81,61,81,61)
    assert result.edge_support_per_side == (1,1,1,1) and result.edge_support == 1
    assert result.border_sample_count == 0 and result.border_penalty == 0
    assert result.heuristic_score == pytest.approx(0.82)


def test_missing_long_edge_changes_only_its_support_and_total_is_weighted_not_mean():
    candidate,trial=scoring_fixture()
    complete=describe_candidate(candidate,trial)
    raw=trial.edges.copy()
    raw[20,21:180]=0  # remove top edge, retain shared corners and the other sides
    incomplete=describe_candidate(candidate,replace(trial,edges=raw))
    assert incomplete.edge_supported_counts == (4,61,81,61)
    assert incomplete.edge_support_per_side[1:] == complete.edge_support_per_side[1:]
    assert incomplete.edge_support == pytest.approx(207/284)
    assert incomplete.edge_support != pytest.approx(np.mean(incomplete.edge_support_per_side))
    assert incomplete.heuristic_score == pytest.approx(complete.heuristic_score-0.35*(1-207/284))
    # Closed is still filled: it must not manufacture support on the missing raw edge.
    empty=describe_candidate(candidate,replace(trial,edges=np.zeros_like(raw)))
    assert empty.edge_support == 0 and empty.edge_supported_counts == (0,0,0,0)
    assert empty.heuristic_score == pytest.approx(0.47)


@pytest.mark.parametrize('points', [
    [(100,10),(190,80),(100,150),(10,80)],
    [(20,20),(175,35),(150,140),(40,120)],
])
def test_oblique_quad_descriptors_are_finite_and_match_euclidean_sampling_oracle(points):
    candidate,trial=scoring_fixture(points)
    # Remove a band to exercise fractional oblique samples, not only complete edges.
    raw=trial.edges.copy()
    raw[45:100,80:150]=0
    counts,supported,border=brute_edge_counts(candidate,raw)
    result=describe_candidate(candidate,replace(trial,edges=raw))
    assert result.edge_sample_counts == counts and result.edge_supported_counts == supported
    assert result.edge_support == pytest.approx(sum(supported)/sum(counts))
    assert result.border_sample_count == border
    assert sum(result.quad_turn_angles_rad) == pytest.approx(2*pi)
    assert not np.allclose(result.quad_turn_angles_rad,(pi/2,)*4)
    assert all(np.isfinite(value) for value in (*result.quad_edge_lengths_px,*result.quad_turn_angles_rad,result.contour_perimeter_px))
    assert all(0 <= value <= 1 for value in (*result.edge_support_per_side,result.area_ratio,result.fit_area_ratio,
        result.edge_support,result.border_penalty,result.heuristic_score))


@pytest.mark.parametrize('pixel', [(20,22),(22,22),(21,22),(19,19)])
def test_support_uses_euclidean_radius_two_not_square_neighborhood(pixel):
    candidate,trial=scoring_fixture()
    raw=np.zeros_like(trial.edges)
    raw[pixel[1],pixel[0]]=255
    counts,supported,_=brute_edge_counts(candidate,raw)
    result=describe_candidate(candidate,replace(trial,edges=raw))
    assert result.edge_sample_counts == counts and result.edge_supported_counts == supported


def test_border_penalty_compares_frame_and_inset_without_claiming_always_correct_ranking():
    frame,frame_trial=scoring_fixture([(0,0),(199,0),(199,159),(0,159)])
    inset,inset_trial=scoring_fixture([(4,4),(195,4),(195,155),(4,155)])
    paper,paper_trial=scoring_fixture()
    frame_result=describe_candidate(frame,frame_trial)
    inset_result=describe_candidate(inset,inset_trial)
    paper_result=describe_candidate(paper,paper_trial)
    assert frame_result.border_penalty == 1 and inset_result.border_penalty == 0
    assert frame_result.border_sample_count == sum(frame_result.edge_sample_counts)
    assert inset_result.heuristic_score > frame_result.heuristic_score
    # Baseline limitation: a much smaller page can still lose to an image frame.
    assert frame_result.heuristic_score > paper_result.heuristic_score


def test_fit_uses_contour_and_quad_areas_without_changing_boundary_descriptor_weights():
    candidate,trial=scoring_fixture()
    contour=((20.,20.),(180.,20.),(180.,140.),(100.,130.),(20.,140.))
    result=describe_candidate(replace(candidate,contour_px=contour),trial)
    assert result.fit_area_ratio == pytest.approx(18400/19200)
    assert result.heuristic_score == pytest.approx(.45*.6+.35+.20*18400/19200)


@pytest.mark.parametrize('change', [
    {'corners':None,'rejection_reason':'NOT_QUADRILATERAL'},
    {'analysis_size':(199,160)}, {'trial_id':'canny_75_200'},
    {'thresholds':(75,200)}, {'contour_px':((20.,20.),)*4},
    {'contour_px':((float('nan'),20.),(180.,20.),(180.,140.),(20.,140.))},
])
def test_descriptors_reject_invalid_candidate_or_mismatched_trial_before_division(change):
    candidate,trial=scoring_fixture()
    with pytest.raises(DetectionValidationError) as error:
        describe_candidate(replace(candidate,**change),trial)
    assert error.value.code == 'INVALID_CANDIDATE'
