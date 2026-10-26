"""Polygon overlap in one image coordinate system, independent of detection."""
from math import isfinite

import cv2
import numpy as np

from .geometry import GeometryValidationError, Quad, validate_quad


def polygon_iou(first: Quad, second: Quad, width: int, height: int) -> float:
    """Continuous intersection/union of validated normalized clockwise quads.

    Both polygons belong to the same image. Keep subpixels; no bounding boxes,
    rasterization or reordering. OpenCV requires convex float32 polygons and
    handleNested=True to include full containment; validate before calling it.
    https://docs.opencv.org/4.x/d3/dc0/group__imgproc__shape.html
    """
    a = np.array(validate_quad(first, width, height), dtype=np.float64)
    b = np.array(validate_quad(second, width, height), dtype=np.float64)
    if any(np.array_equal(a, np.roll(b, offset, axis=0)) for offset in range(4)):
        return 1.0  # exact same polygon, avoid float32 area rounding below one
    a, b = a.astype(np.float32), b.astype(np.float32)
    try:
        area_a, area_b = cv2.contourArea(a), cv2.contourArea(b)
        intersection, _ = cv2.intersectConvexConvex(a, b, handleNested=True)
    except cv2.error as error:
        raise GeometryValidationError('POLYGON_IOU_FAILED', 'Không tính được giao hai tứ giác.') from error
    if (not all(isfinite(value) for value in (intersection, area_a, area_b))
            or intersection < 0 or min(area_a, area_b) <= 0):
        raise GeometryValidationError('POLYGON_IOU_FAILED', 'Diện tích giao không hợp lệ.')
    # Float32 intersection can exceed the smaller area slightly through rounding.
    intersection = min(intersection, area_a, area_b)
    return intersection / (area_a + area_b - intersection)
