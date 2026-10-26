"""Continuous polygon area, never bounding boxes or raster pixel counts."""
import pytest

from app.processing.geometry import GeometryValidationError, pixel_to_normalized
from app.processing.polygon_metrics import polygon_iou


SIZE = (201, 201)


def quad(points):
    return tuple(pixel_to_normalized(p, *SIZE) for p in points)


SQUARE = quad(((20, 20), (120, 20), (120, 120), (20, 120)))


@pytest.mark.parametrize('shift', range(4))
def test_identical_polygon_has_unit_iou_regardless_of_cycle_start(shift):
    other = SQUARE[shift:] + SQUARE[:shift]
    assert polygon_iou(SQUARE, other, *SIZE) == 1


@pytest.mark.parametrize('other,expected', [
    (((70, 20), (170, 20), (170, 120), (70, 120)), 1/3),
    (((40, 40), (100, 40), (100, 100), (40, 100)), .36),
    (((120, 20), (180, 20), (180, 120), (120, 120)), 0),
    (((130, 130), (190, 130), (190, 190), (130, 190)), 0),
    (((20, 20), (115, 20), (115, 120), (20, 120)), .95),
])
def test_known_areas_include_nested_touching_disjoint_and_nms_boundary(other, expected):
    assert polygon_iou(SQUARE, quad(other), *SIZE) == pytest.approx(expected)
    assert polygon_iou(quad(other), SQUARE, *SIZE) == pytest.approx(expected)


def test_oblique_polygon_uses_polygon_intersection_instead_of_bounding_box():
    diamond = quad(((70, 20), (120, 70), (70, 120), (20, 70)))
    assert polygon_iou(SQUARE, diamond, *SIZE) == .5
    # Subpixel displacement is retained, not rounded to integer pixels.
    shifted = tuple((x+.25/200, y) for x,y in SQUARE)
    assert polygon_iou(SQUARE, shifted, *SIZE) == pytest.approx(9975/10025)


def test_skew_subpixel_polygon_identical_across_cycle_starts():
    skew = ((.12739560485559634,.09388784397520523),
            (.9358597919911382,.1197368029059364),
            (.8594177347887649,.9475622351636757),
            (.1261139701990353,.9286064305276954))
    for i in range(4):
        assert polygon_iou(skew, skew[i:]+skew[:i], 901, 1200) == 1


@pytest.mark.parametrize('bad', [
    ((.1,.1),)*4,
    ((.1,.1),(.6,.6),(.6,.1),(.1,.6)),
    ((.1,.1),(.6,.1),(.3,.3),(.1,.6)),
    ((float('nan'),.1),(.6,.1),(.6,.6),(.1,.6)),
    ((-.1,.1),(.6,.1),(.6,.6),(.1,.6)),
    SQUARE[::-1],
])
def test_invalid_geometry_is_rejected_before_intersection(bad):
    with pytest.raises(GeometryValidationError):
        polygon_iou(SQUARE, bad, *SIZE)


def test_bad_dimensions_and_opencv_failure_are_explicit(monkeypatch):
    with pytest.raises(GeometryValidationError):
        polygon_iou(SQUARE, SQUARE, 1, 201)
    import cv2
    def fail(*args, **kwargs):
        raise cv2.error('controlled failure')
    monkeypatch.setattr('app.processing.polygon_metrics.cv2.intersectConvexConvex', fail)
    with pytest.raises(GeometryValidationError) as error:
        polygon_iou(SQUARE, tuple((x+.01,y) for x,y in SQUARE), *SIZE)
    assert error.value.code == 'POLYGON_IOU_FAILED'
