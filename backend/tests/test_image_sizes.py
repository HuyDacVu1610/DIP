"""Resize rules for display derivatives, independent of source geometry."""

import numpy as np
import pytest

from app.processing.image_sizes import resize_to_max_edge


@pytest.mark.parametrize("shape,max_edge,expected", [
    ((800, 400, 3), 320, (320, 160, 3)),
    ((400, 800, 3), 320, (160, 320, 3)),
    ((1200, 2400, 3), 1000, (500, 1000, 3)),
    ((40, 21, 3), 20, (20, 11, 3)),
    ((21, 40, 3), 20, (11, 20, 3)),
    ((2, 16000, 3), 320, (1, 320, 3)),
    ((16000, 2, 3), 320, (320, 1, 3)),
    ((4, 4), 2, (2, 2)),
    ((9856, 77, 3), 320, (320, 3, 3)),
    ((1216, 76, 3), 1000, (1000, 63, 3)),
    ((1760, 11, 3), 1200, (1200, 8, 3)),
])
def test_resize_returns_actual_dimensions_after_half_up_rounding(shape, max_edge, expected):
    source = np.full(shape, 73, dtype=np.uint8)
    resized = resize_to_max_edge(source, max_edge)
    assert resized.shape == expected
    assert resized.dtype == np.uint8
    assert resized.flags.c_contiguous
    assert np.all(resized == 73)
    assert not np.shares_memory(resized, source)


@pytest.mark.parametrize("shape,max_edge", [((2, 2, 3), 320), ((3, 5), 320), ((32, 64, 3), 64)])
def test_small_images_are_not_upscaled_and_the_result_does_not_alias_source(shape, max_edge):
    source = np.full(shape, 91, dtype=np.uint8)
    resized = resize_to_max_edge(source, max_edge)
    np.testing.assert_array_equal(resized, source)
    assert not np.shares_memory(resized, source)
    resized[...] = 0
    assert np.all(source == 91)


def test_binary_preview_uses_area_average_without_rethresholding():
    source = np.array([[0, 255], [255, 0]], dtype=np.uint8)
    resized = resize_to_max_edge(source, 1)
    assert resized.shape == (1, 1)
    assert resized[0, 0] == 128
    np.testing.assert_array_equal(source, [[0, 255], [255, 0]])


def test_resize_handles_non_contiguous_color_input_without_swapping_channels():
    source = np.zeros((8, 16, 3), dtype=np.uint8)
    source[:] = [10, 20, 30]
    view = source[:, ::2, :]
    resized = resize_to_max_edge(view, 4)
    assert resized.shape == (4, 4, 3)
    assert np.all(resized == [10, 20, 30])


@pytest.mark.parametrize("max_edge", [0, -1, 2.5, float("nan"), float("inf"), True, "320"])
def test_resize_rejects_invalid_edge_limits(max_edge):
    with pytest.raises(ValueError):
        resize_to_max_edge(np.zeros((2, 2, 3), dtype=np.uint8), max_edge)


@pytest.mark.parametrize("source", [
    np.zeros((0, 2, 3), dtype=np.uint8), np.zeros((2, 0), dtype=np.uint8),
    np.zeros((2, 2, 1), dtype=np.uint8), np.zeros((2, 2, 4), dtype=np.uint8),
    np.zeros((2, 2, 3), dtype=np.float32), np.zeros((2,), dtype=np.uint8),
])
def test_resize_rejects_empty_or_unsupported_image_arrays(source):
    with pytest.raises(ValueError):
        resize_to_max_edge(source, 320)
