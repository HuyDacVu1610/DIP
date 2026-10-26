"""Source coordinates, cyclic topology and automatic corner ordering."""

from itertools import permutations

import numpy as np
import pytest
import cv2
import app.processing.geometry as geometry

from app.processing.geometry import (
    GeometryValidationError,
    normalized_to_pixel,
    pixel_to_normalized,
    validate_quad_points,
    validate_quad,
    order_auto_corners,
    estimate_warp_size,
    compute_homography,
    warp_document,
)


@pytest.mark.parametrize("width,height", [
    (2, 2), (101, 51), (1536, 2048), (8000, 2000), (2, 8_000_000), (9856, 77),
])
def test_source_pixel_endpoints_and_fractional_round_trip(width, height):
    cases = [
        ((0, 0), (0, 0)),
        ((width - 1, 0), (1, 0)),
        ((width - 1, height - 1), (1, 1)),
        ((0, height - 1), (0, 1)),
        (((width - 1) / 2, (height - 1) / 4), (0.5, 0.25)),
    ]
    for pixel, normalized in cases:
        assert pixel_to_normalized(pixel, width, height) == normalized
        assert normalized_to_pixel(normalized, width, height) == pixel
    for normalized in [(0.123456789, 0.987654321), (1e-12, 1 - 1e-12)]:
        pixel = normalized_to_pixel(normalized, width, height)
        assert pixel_to_normalized(pixel, width, height) == pytest.approx(normalized, abs=1e-15)


def test_mapping_uses_actual_analysis_dimensions_and_keeps_subpixel_values():
    # Resize 21x40 to max-edge 20 gives 11x20 (not nominal 10.5x20).
    normalized = pixel_to_normalized((5, 9.5), 11, 20)
    assert normalized == (0.5, 0.5)
    assert normalized_to_pixel(normalized, 21, 40) == (10, 19.5)
    assert normalized_to_pixel((0.5, 0.5), 1536, 2048) == (767.5, 1023.5)


def test_coordinate_helpers_accept_numpy_scalars_without_mutating_input():
    point = np.array([np.float32(0.25), np.float32(0.5)])
    before = point.copy()
    assert normalized_to_pixel(point, np.int64(101), np.int64(51)) == (25, 25)
    np.testing.assert_array_equal(point, before)


@pytest.mark.parametrize("convert,point", [
    (normalized_to_pixel, (-1e-12, 0)),
    (normalized_to_pixel, (0, 1 + 1e-12)),
    (pixel_to_normalized, (-1e-12, 0)),
    (pixel_to_normalized, (100 + 1e-12, 50)),
    (pixel_to_normalized, (100, 50 + 1e-12)),
])
def test_coordinates_outside_source_are_rejected_without_clamping(convert, point):
    with pytest.raises(GeometryValidationError) as error:
        convert(point, 101, 51)
    assert error.value.code == "POINT_OUT_OF_BOUNDS"


@pytest.mark.parametrize("point", [
    None, 0, [], [0], [0, 0, 0], ["0", 0], [True, 0],
    [float("nan"), 0], [0, float("inf")], [float("-inf"), 0], [0j, 0],
])
@pytest.mark.parametrize("convert", [pixel_to_normalized, normalized_to_pixel])
def test_malformed_or_nonfinite_points_have_a_geometry_error(convert, point):
    with pytest.raises(GeometryValidationError) as error:
        convert(point, 101, 51)
    assert error.value.code == "INVALID_POINT"


@pytest.mark.parametrize("width,height", [
    (1, 20), (20, 1), (0, 20), (-1, 20), (2.5, 20), (True, 20),
    (20, False), ("101", 51), (float("inf"), 20), (float("nan"), 20),
])
@pytest.mark.parametrize("convert", [pixel_to_normalized, normalized_to_pixel])
def test_invalid_dimensions_cannot_enter_coordinate_math(convert, width, height):
    with pytest.raises(GeometryValidationError) as error:
        convert((0, 0), width, height)
    assert error.value.code == "INVALID_DIMENSIONS"


@pytest.mark.parametrize("width,height", [(2, 2), (101, 51), (1536, 2048), (8000, 2000)])
@pytest.mark.parametrize("corners", [
    [(0, 0), (1, 0), (1, 1), (0, 1)],
    [(0.5, 0), (1, 0.5), (0.5, 1), (0, 0.5)],
    [(0.15, 0.05), (0.95, 0.3), (0.7, 0.95), (0.1, 0.65)],
    [(0.2, 0.2), (0.21, 0.2), (0.21, 0.21), (0.2, 0.21)],
])
def test_point_gate_accepts_perspective_diamond_and_small_manual_regions(width, height, corners):
    before = list(corners)
    pixels = validate_quad_points(corners, width, height)
    assert isinstance(pixels, tuple)
    assert len(pixels) == 4
    for actual, expected in zip(pixels, corners, strict=True):
        assert actual == pytest.approx((expected[0] * (width - 1), expected[1] * (height - 1)))
    assert corners == before


@pytest.mark.parametrize("corners", [None, [], [(0, 0)] * 3, [(0, 0)] * 5, "abcd"])
def test_point_gate_requires_exactly_four_points(corners):
    with pytest.raises(GeometryValidationError) as error:
        validate_quad_points(corners, 101, 51)
    assert error.value.code == "INVALID_CORNER_COUNT"


@pytest.mark.parametrize("bad_point,code", [
    ([0], "INVALID_POINT"), ([0, float("nan")], "INVALID_POINT"),
    ([0, float("inf")], "INVALID_POINT"), ([-0.01, 0], "POINT_OUT_OF_BOUNDS"),
    ([1.01, 0], "POINT_OUT_OF_BOUNDS"),
])
def test_point_gate_reuses_coordinate_validation(bad_point, code):
    with pytest.raises(GeometryValidationError) as error:
        validate_quad_points([(0, 0), (1, 0), (1, 1), bad_point], 101, 51)
    assert error.value.code == code


@pytest.mark.parametrize("i,j", [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)])
@pytest.mark.parametrize("offset", [0, 1e-7])
def test_duplicate_gate_checks_all_six_pairs_even_nonadjacent(i, j, offset):
    corners = [(0.1, 0.1), (0.9, 0.1), (0.9, 0.9), (0.1, 0.9)]
    corners[j] = (corners[i][0] + offset, corners[i][1])
    with pytest.raises(GeometryValidationError) as error:
        validate_quad_points(corners, 1536, 2048)
    assert error.value.code == "DUPLICATE_POINTS"
    assert str(error.value)


@pytest.mark.parametrize("width,height", [(101, 51), (1536, 2048), (8000, 4000)])
@pytest.mark.parametrize("shift", range(4))
def test_short_edge_gate_covers_every_edge_including_closing_edge(width, height, shift):
    corners = [(0.1, 0.1), (0.1001, 0.1), (0.9, 0.9), (0.1, 0.9)]
    corners = corners[shift:] + corners[:shift]
    with pytest.raises(GeometryValidationError) as error:
        validate_quad_points(corners, width, height)
    assert error.value.code == "SHORT_EDGE"


def test_distance_is_measured_in_pixels_not_in_anisotropic_normalized_axes():
    # On a 10001x101 image, this vertical edge is 5 px (<0.1% diagonal).
    corners = [(0, 0), (1, 0), (1, 0.05), (0, 1)]
    with pytest.raises(GeometryValidationError) as error:
        validate_quad_points(corners, 10001, 101)
    assert error.value.code == "SHORT_EDGE"


@pytest.mark.parametrize("width,height", [(101, 101), (1001, 1001), (4001, 4001)])
def test_tolerances_scale_with_resolution_for_equivalent_regions(width, height):
    close = [(0, 0), (1e-7, 0), (1, 1), (0, 1)]
    short = [(0, 0), (0.001, 0), (1, 1), (0, 1)]
    good = [(0, 0), (0.002, 0), (1, 1), (0, 1)]
    for corners, code in [(close, "DUPLICATE_POINTS"), (short, "SHORT_EDGE")]:
        with pytest.raises(GeometryValidationError) as error:
            validate_quad_points(corners, width, height)
        assert error.value.code == code
    assert len(validate_quad_points(good, width, height)) == 4


def test_short_edge_threshold_is_inclusive_and_fractional_points_stay_fractional():
    # W−1=3, H−1=4, diagonal=5: minimum edge is 0.005 px.
    corners = [(0, 0), (0.005 / 3, 0), (1, 1), (0, 1)]
    with pytest.raises(GeometryValidationError) as error:
        validate_quad_points(corners, 4, 5)
    assert error.value.code == "SHORT_EDGE"
    corners[1] = (0.0051 / 3, 0)
    assert validate_quad_points(corners, 4, 5)[1] == (0.0051, 0)


def test_point_gate_preserves_numpy_handle_order_and_does_not_validate_topology_yet():
    # Bow-tie/winding/convexity belong to MVP03.03. This is a partial gate.
    corners = np.array([(1, 1), (0, 0), (1, 0), (0, 1)], dtype=np.float64)
    before = corners.copy()
    assert validate_quad_points(corners, 101, 51) == ((100, 50), (0, 0), (100, 0), (0, 50))
    np.testing.assert_array_equal(corners, before)


@pytest.mark.parametrize("width,height", [(2, 2), (101, 51), (1536, 2048), (4001, 4001)])
@pytest.mark.parametrize("corners", [
    [(0, 0), (1, 0), (1, 1), (0, 1)],
    [(0.5, 0), (1, 0.5), (0.5, 1), (0, 0.5)],
    [(0.15, 0.05), (0.95, 0.3), (0.7, 0.95), (0.1, 0.65)],
    [(0.2, 0.2), (0.21, 0.2), (0.21, 0.21), (0.2, 0.21)],
])
def test_topology_gate_accepts_convex_clockwise_regions_and_preserves_start(width, height, corners):
    for shift in range(4):
        shifted = corners[shift:] + corners[:shift]
        assert validate_quad(shifted, width, height) == validate_quad_points(shifted, width, height)


@pytest.mark.parametrize("corners,code", [
    ([(0, 0), (1, 1), (1, 0), (0, 1)], "SELF_INTERSECTION"),
    ([(0, 0), (1, 0), (0, 1), (1, 1)], "SELF_INTERSECTION"),
    ([(0, 0), (1, 0), (0.2, 0.2), (0, 1)], "NON_CONVEX_QUAD"),
    ([(0, 0), (0.5, 0), (1, 0), (0, 1)], "DEGENERATE_QUAD"),
    ([(0.1, 0.1), (0.3, 0.3), (0.9, 0.9), (0.7, 0.7)], "DEGENERATE_QUAD"),
    ([(0, 0), (0.5, 1e-8), (1, 0), (0, 1)], "DEGENERATE_QUAD"),
    ([(0, 0), (0, 1), (1, 1), (1, 0)], "INVALID_WINDING"),
])
@pytest.mark.parametrize("width,height", [(101, 101), (1001, 1001), (4001, 4001)])
def test_topology_gate_rejects_invalid_region_with_stable_reason(corners, code, width, height):
    before = list(corners)
    for shift in range(4):
        shifted = corners[shift:] + corners[:shift]
        with pytest.raises(GeometryValidationError) as error:
            validate_quad(shifted, width, height)
        assert error.value.code == code
        assert str(error.value)
    assert corners == before


@pytest.mark.parametrize("corners,code", [
    ([(0, 0)] * 3, "INVALID_CORNER_COUNT"),
    ([(0, 0), (1, 0), (1, 1), (0, 0)], "DUPLICATE_POINTS"),
    ([(0, 0), (0.0001, 0), (1, 1), (0, 1)], "SHORT_EDGE"),
    ([(0, 0), (1, 0), (1, 1), (0, float('nan'))], "INVALID_POINT"),
    ([(0, 0), (1, 0), (1, 1), (0, 1.01)], "POINT_OUT_OF_BOUNDS"),
])
def test_topology_gate_reuses_point_edge_errors(corners, code):
    with pytest.raises(GeometryValidationError) as error:
        validate_quad(corners, 1536, 2048)
    assert error.value.code == code


def test_thin_convex_quad_is_rejected_by_area_even_with_long_edges_and_clear_turns():
    # A thin diamond: all edges ~0.283*D, but area/D² is only 4e-7.
    corners = [(0.1, 0.5), (0.5, 0.499999), (0.9, 0.5), (0.5, 0.500001)]
    assert len(validate_quad_points(corners, 1001, 1001)) == 4
    with pytest.raises(GeometryValidationError) as error:
        validate_quad(corners, 1001, 1001)
    assert error.value.code == "DEGENERATE_QUAD"


def test_area_computation_preserves_small_valid_region_near_bottom_right():
    corners = [(0.991, 0.991), (0.999, 0.991), (0.999, 0.999), (0.991, 0.999)]
    pixels = validate_quad(corners, 4001, 4001)
    assert pixels == ((3964, 3964), (3996, 3964), (3996, 3996), (3964, 3996))


@pytest.mark.parametrize("expected", [
    ((0, 0), (1, 0), (1, 1), (0, 1)),
    ((0.5, 0), (1, 0.5), (0.5, 1), (0, 0.5)),
    ((0.15, 0.05), (0.95, 0.3), (0.7, 0.95), (0.1, 0.65)),
    ((0.1, 0.3), (0.6, 0.1), (0.9, 0.7), (0.4, 0.9)),
    ((0.2, 0.2), (0.21, 0.2), (0.21, 0.21), (0.2, 0.21)),
])
def test_all_24_auto_permutations_produce_one_cyclic_quad_without_duplicate_vertices(expected):
    for proposed in permutations(expected):
        ordered = order_auto_corners(proposed, 1001, 1001)
        assert ordered == expected
        assert len(set(ordered)) == 4
        assert set(ordered) == set(proposed)
        assert len(validate_quad(ordered, 1001, 1001)) == 4


def test_auto_start_is_selected_in_source_pixels_not_normalized_anisotropic_axes():
    proposed = [(0.5, 0), (1, 0.5), (0.5, 1), (0, 0.5)]
    assert order_auto_corners(proposed, 201, 101) == ((0, 0.5), (0.5, 0), (1, 0.5), (0.5, 1))
    assert order_auto_corners(proposed, 101, 201) == ((0.5, 0), (1, 0.5), (0.5, 1), (0, 0.5))


def test_auto_can_order_valid_set_with_short_nonboundary_diagonal():
    # The short diagonal is not an edge: unordered candidates must not be
    # rejected by the cyclic edge gate before their cycle is established.
    proposed = [(0.1, 0.5), (0.9, 0.5), (0.5, 0.4995), (0.5, 0.5005)]
    expected = ((0.1, 0.5), (0.5, 0.4995), (0.9, 0.5), (0.5, 0.5005))
    assert order_auto_corners(proposed, 1001, 1001) == expected


@pytest.mark.parametrize("proposed,code", [
    ([(0, 0)] * 3, "INVALID_CORNER_COUNT"),
    ([(0, 0), (1, 0), (1, 1), (0, 0)], "DUPLICATE_POINTS"),
    ([(0, 0), (0.0001, 0), (1, 1), (0, 1)], "SHORT_EDGE"),
    ([(0, 0), (1, 0), (0.2, 0.2), (0, 1)], "NON_CONVEX_QUAD"),
    ([(0, 0), (0.5, 0), (1, 0), (0, 1)], "DEGENERATE_QUAD"),
    ([(0, 0), (1, 0), (1, 1), (0, float('inf'))], "INVALID_POINT"),
    ([(0, 0), (1, 0), (1, 1), (-0.01, 1)], "POINT_OUT_OF_BOUNDS"),
])
def test_auto_ordering_does_not_invent_corners_to_repair_invalid_point_set(proposed, code):
    with pytest.raises(GeometryValidationError) as error:
        order_auto_corners(proposed, 1001, 1001)
    assert error.value.code == code


def test_manual_validation_preserves_handle_identity_or_rejects_every_permutation():
    corners = ((0.15, 0.05), (0.95, 0.3), (0.7, 0.95), (0.1, 0.65))
    clockwise_cycles = [corners[i:] + corners[:i] for i in range(4)]
    for proposed in permutations(corners):
        original = np.array(proposed)
        before = original.copy()
        if proposed in clockwise_cycles:
            assert validate_quad(original, 1001, 1001) == validate_quad_points(original, 1001, 1001)
        else:
            with pytest.raises(GeometryValidationError):
                validate_quad(original, 1001, 1001)
        np.testing.assert_array_equal(original, before)


def test_auto_ordering_is_idempotent_and_does_not_mutate_numpy_input():
    proposed = np.array([(0.5, 1), (0, 0.5), (0.5, 0), (1, 0.5)])
    before = proposed.copy()
    ordered = order_auto_corners(proposed, 1001, 1001)
    assert ordered == ((0.5, 0), (1, 0.5), (0.5, 1), (0, 0.5))
    assert order_auto_corners(ordered, 1001, 1001) == ordered
    np.testing.assert_array_equal(proposed, before)


@pytest.mark.parametrize("width,height,expected", [
    (2, 2, (2, 2)), (101, 51, (100, 50)), (51, 101, (50, 100)),
    (2401, 1201, (2400, 1200)), (4001, 2001, (2400, 1200)),
    (2001, 4001, (1200, 2400)), (4001, 4001, (2400, 2400)),
])
def test_estimated_size_uses_opposite_edges_without_upscaling_to_limit(width, height, expected):
    assert estimate_warp_size([(0, 0), (1, 0), (1, 1), (0, 1)], width, height) == expected


def test_estimated_size_keeps_half_up_rounding_and_fractional_corners():
    assert estimate_warp_size([(0, 0), (0.105, 0), (0.105, 0.105), (0, 0.105)], 101, 101) == (11, 11)


def test_estimated_size_caps_both_axes_with_exact_integer_half_up():
    # 4864x6000 scales to 1945.6x2400, i.e. 1946x2400.
    assert estimate_warp_size([(0, 0), (1, 0), (1, 1), (0, 1)], 4865, 6001) == (1946, 2400)
    # 125/4800*2400 = 62.5, explicitly half-up, not bankers' round.
    assert estimate_warp_size([(0, 0), (1, 0), (1, 1), (0, 1)], 126, 4801) == (63, 2400)


def test_estimated_size_uses_longer_opposite_edge_on_perspective_quad():
    # Source pixels: (10,10),(90,10),(100,70),(0,70).
    corners = [(0.1, 0.1), (0.9, 0.1), (1, 0.7), (0, 0.7)]
    assert estimate_warp_size(corners, 101, 101) == (100, 61)


def test_estimated_size_diamond_is_not_a_bounding_box_or_a4_ratio():
    assert estimate_warp_size([(0.5, 0), (1, 0.5), (0.5, 1), (0, 0.5)], 101, 101) == (71, 71)


@pytest.mark.parametrize("corners,code", [
    ([(0, 0), (1, 1), (1, 0), (0, 1)], "SELF_INTERSECTION"),
    ([(0, 0), (0, 1), (1, 1), (1, 0)], "INVALID_WINDING"),
    ([(0, 0), (1, 0), (0.2, 0.2), (0, 1)], "NON_CONVEX_QUAD"),
])
def test_size_estimation_requires_full_geometry_validation(corners, code):
    with pytest.raises(GeometryValidationError) as error:
        estimate_warp_size(corners, 101, 101)
    assert error.value.code == code


def _perspective_color_source():
    source = np.full((80, 120, 3), 17, dtype=np.uint8)
    pixels = np.array([(20, 15), (95, 8), (105, 65), (12, 70)], dtype=np.int32)
    colors = [(10, 20, 230), (20, 210, 30), (220, 40, 50), (30, 200, 210)]
    cv2.fillConvexPoly(source, pixels, (240, 240, 240))
    for point, color in zip(pixels, colors, strict=True):
        cv2.circle(source, tuple(point), 5, color, thickness=-1)
    corners = [(float(x)/119, float(y)/79) for x,y in pixels]
    return source, corners, colors


def test_homography_maps_all_four_source_corners_to_exact_target_indices():
    source, corners, _ = _perspective_color_source()
    height, width = source.shape[:2]
    matrix, size = compute_homography(corners, width, height)
    assert matrix.shape == (3, 3)
    assert matrix.dtype == np.float64
    assert np.all(np.isfinite(matrix))
    assert np.linalg.det(matrix) != 0
    assert size == estimate_warp_size(corners, width, height)
    w, h = size
    source_points = np.array(validate_quad(corners, width, height)).reshape(1, 4, 2)
    mapped = cv2.perspectiveTransform(source_points, matrix)[0]
    np.testing.assert_allclose(mapped, [(0,0),(w-1,0),(w-1,h-1),(0,h-1)], atol=2e-4)


@pytest.mark.parametrize("shift", range(4))
def test_warp_keeps_corner_color_order_and_source_pixels(shift):
    source, corners, colors = _perspective_color_source()
    before = source.copy()
    corners = corners[shift:] + corners[:shift]
    colors = colors[shift:] + colors[:shift]
    result = warp_document(source, corners)
    w, h = estimate_warp_size(corners, 120, 80)
    assert result.shape == (h, w, 3)
    assert result.dtype == np.uint8
    assert result.flags.c_contiguous
    assert not np.shares_memory(result, source)
    actual = [result[0,0], result[0,-1], result[-1,-1], result[-1,0]]
    np.testing.assert_array_equal(actual, colors)
    np.testing.assert_array_equal(source, before)


def test_warp_retains_fractional_corners_and_uses_bilinear_sampling():
    y, x = np.indices((4,4))
    source = np.repeat((40*x+8*y).astype(np.uint8)[...,None], 3, axis=2)
    corners = [(0.125,0.125),(0.875,0.125),(0.875,0.875),(0.125,0.875)]
    result = warp_document(source, corners)
    assert result.shape == (2,2,3)
    np.testing.assert_array_equal(result[...,0], [[18,108],[36,126]])


def test_warp_minimum_source_is_identity_and_strided_input_preserves_bgr():
    source = np.array([[[10,20,30],[40,50,60]],[[70,80,90],[100,110,120]]], dtype=np.uint8)
    corners = [(0,0),(1,0),(1,1),(0,1)]
    np.testing.assert_array_equal(warp_document(source, corners), source)
    view = source[:, ::-1, :]
    np.testing.assert_array_equal(warp_document(view, corners), view)


@pytest.mark.parametrize("corners,code", [
    ([(0,0),(1,1),(1,0),(0,1)], "SELF_INTERSECTION"),
    ([(0,0),(0,1),(1,1),(1,0)], "INVALID_WINDING"),
    ([(0,0),(1,0),(0.2,0.2),(0,1)], "NON_CONVEX_QUAD"),
    ([(0,0)]*4, "DUPLICATE_POINTS"),
])
def test_invalid_geometry_never_reaches_opencv(monkeypatch, corners, code):
    def unexpected(*args, **kwargs):
        pytest.fail('Invalid corners reached OpenCV')
    monkeypatch.setattr(cv2, 'getPerspectiveTransform', unexpected)
    monkeypatch.setattr(cv2, 'warpPerspective', unexpected)
    with pytest.raises(GeometryValidationError) as error:
        warp_document(np.zeros((101,101,3), dtype=np.uint8), corners)
    assert error.value.code == code


@pytest.mark.parametrize("source", [
    None, np.zeros((2,2), dtype=np.uint8), np.zeros((2,2,4), dtype=np.uint8),
    np.zeros((2,2,1), dtype=np.uint8), np.zeros((2,2,3), dtype=np.float32),
])
def test_warp_rejects_unsupported_sources_before_opencv(monkeypatch, source):
    monkeypatch.setattr(cv2, 'getPerspectiveTransform', lambda *a,**k: pytest.fail('Invalid source reached OpenCV'))
    with pytest.raises(GeometryValidationError) as error:
        warp_document(source, [(0,0),(1,0),(1,1),(0,1)])
    assert error.value.code == 'INVALID_SOURCE'


def test_warp_source_pixel_quota_is_checked_before_transform_or_output_allocation(monkeypatch):
    large = np.lib.stride_tricks.as_strided(np.zeros(3, dtype=np.uint8), (4001,4000,3), (0,0,1))
    monkeypatch.setattr(cv2, 'getPerspectiveTransform', lambda *a,**k: pytest.fail('Oversize source reached OpenCV'))
    with pytest.raises(GeometryValidationError) as error:
        warp_document(large, [(0,0),(1,0),(1,1),(0,1)])
    assert error.value.code == 'TOO_MANY_PIXELS'


@pytest.mark.parametrize("bad_matrix", [np.full((3,3), np.nan), np.full((3,3), np.inf), np.zeros((3,3))])
def test_nonfinite_or_singular_homography_never_reaches_pixel_sampling(monkeypatch, bad_matrix):
    monkeypatch.setattr(cv2, 'getPerspectiveTransform', lambda *a,**k: bad_matrix)
    monkeypatch.setattr(cv2, 'warpPerspective', lambda *a,**k: pytest.fail('Invalid matrix reached sampler'))
    with pytest.raises(GeometryValidationError) as error:
        warp_document(np.zeros((101,101,3), dtype=np.uint8), [(0,0),(1,0),(1,1),(0,1)])
    assert error.value.code == 'INVALID_HOMOGRAPHY'


def test_warp_maximum_output_respects_size_and_pixel_limits():
    source = np.empty((3001,3001,3), dtype=np.uint8)
    source[:] = [13,27,91]
    result = warp_document(source, [(0,0),(1,0),(1,1),(0,1)])
    assert result.shape == (2400,2400,3)
    assert np.all(result == [13,27,91])


@pytest.mark.parametrize('shape', [(400,40000,3), (40000,400,3)])
def test_valid_16mp_long_source_is_warped_from_original_pixels_across_tile_seams(shape):
    source = np.empty(shape, dtype=np.uint8)
    source[:] = [10,20,30]
    if shape[1] > shape[0]:
        source[:,20000:]=[90,110,130]
    else:
        source[20000:]=[90,110,130]
    result = warp_document(source, [(0,0),(1,0),(1,1),(0,1)])
    assert max(result.shape[:2]) == 2400
    np.testing.assert_array_equal(result[0,0], [10,20,30])
    np.testing.assert_array_equal(result[-1,-1], [90,110,130])
    # The plateau on each side of the seam must stay exact, not source-resized.
    if shape[1] > shape[0]:
        assert np.all(result[:,:1199] == [10,20,30])
        assert np.all(result[:,1201:] == [90,110,130])
    else:
        assert np.all(result[:1199] == [10,20,30])
        assert np.all(result[1201:] == [90,110,130])


def test_diamond_all_auto_permutations_keep_distinct_corner_colors_after_warp():
    source=np.full((160,160,3),240,dtype=np.uint8)
    points=[(80,10),(150,80),(80,150),(10,80)]
    colors=[(10,20,230),(20,210,30),(220,40,50),(30,200,210)]
    for point,color in zip(points,colors,strict=True):
        cv2.circle(source,point,6,color,-1)
    normalized=[(x/159,y/159) for x,y in points]
    for proposed in permutations(normalized):
        ordered=order_auto_corners(proposed,160,160)
        result=warp_document(source,ordered)
        np.testing.assert_array_equal([result[0,0],result[0,-1],result[-1,-1],result[-1,0]],colors)


@pytest.mark.parametrize('a,b,c,d,expected', [
    ((0,0),(1,1),(0,1),(1,0),True),
    ((0,0),(1,0),(1,0),(1,1),True),
    ((0,0),(1,0),(0.2,0),(0.8,0),True),
    ((0,0),(0.2,0),(0.8,0),(1,0),False),
    ((0,0),(1,0),(0,0.1),(1,0.1),False),
    ((0,0),(0.4,0.4),(0.6,0.6),(1,1),False),
])
def test_segment_intersection_covers_touch_overlap_and_disjoint_collinear(a,b,c,d,expected):
    assert geometry._segments_intersect(a,b,c,d) is expected


def test_large_source_roi_warp_matches_equivalent_small_crop_without_source_resize():
    source=np.full((400,40000,3),127,dtype=np.uint8)
    source[100:350,35000:35501]=[13,29,83]
    points=[(35000,100),(35500,110),(35490,350),(35020,340)]
    colors=[(10,20,230),(20,210,30),(220,40,50),(30,200,210)]
    for point,color in zip(points,colors,strict=True):
        cv2.circle(source,point,8,color,-1)
    large_corners=[(x/39999,y/399) for x,y in points]
    crop=source[90:361,34990:35511]
    crop_corners=[((x-34990)/520,(y-90)/270) for x,y in points]
    large_result=warp_document(source,large_corners)
    crop_result=warp_document(crop,crop_corners)
    assert large_result.shape == crop_result.shape
    # For this fixed integer-corner fixture the translated mapping is exact.
    np.testing.assert_array_equal(large_result,crop_result)
    np.testing.assert_array_equal([large_result[0,0],large_result[0,-1],large_result[-1,-1],large_result[-1,0]],colors)
