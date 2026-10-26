"""Source geometry only; independent of HTTP, storage and image decoding."""

from collections.abc import Mapping, Sequence
from itertools import combinations
from math import atan2, dist, floor, fsum, hypot, isfinite
from numbers import Integral, Real

import cv2
import numpy as np
from numpy.typing import NDArray

from ..settings import MAX_IMAGE_PIXELS

Point = tuple[float, float]
Quad = tuple[Point, Point, Point, Point]

# Implementation baselines, relative to the pixel diagonal; not detector accuracy.
POINT_DISTANCE_EPS_RATIO = 1e-6
MIN_EDGE_LENGTH_RATIO = 1e-3
MIN_QUAD_AREA_RATIO = 1e-6
MAX_WARP_LONG_EDGE = 2400
MAX_WARP_PIXELS = 5_760_000


class GeometryValidationError(ValueError):
    """Stable reason code and Vietnamese message, without an HTTP status."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def _scales(width: int, height: int) -> Point:
    if any(isinstance(d, bool) or not isinstance(d, Integral) or d < 2 for d in (width, height)):
        raise GeometryValidationError("INVALID_DIMENSIONS", "Kích thước ảnh phải là số nguyên từ 2 pixel.")
    try:
        scales = float(int(width) - 1), float(int(height) - 1)
    except OverflowError as error:
        raise GeometryValidationError("INVALID_DIMENSIONS", "Kích thước ảnh vượt phạm vi số thực.") from error
    if not isfinite(hypot(*scales)):
        raise GeometryValidationError("INVALID_DIMENSIONS", "Đường chéo ảnh vượt phạm vi số thực.")
    return scales


def _point(point: Sequence[Real]) -> Point:
    try:
        if isinstance(point, (str, bytes, Mapping)) or len(point) != 2:
            raise ValueError
        values = point[0], point[1]
        if any(isinstance(v, bool) or not isinstance(v, Real) for v in values):
            raise ValueError
        result = float(values[0]), float(values[1])
        if not all(isfinite(v) for v in result):
            raise ValueError
    except (TypeError, ValueError, OverflowError, IndexError, KeyError) as error:
        raise GeometryValidationError("INVALID_POINT", "Mỗi điểm phải có đúng hai tọa độ số thực hữu hạn.") from error
    return result


def _bounded_point(point: Sequence[Real], max_x: float, max_y: float) -> Point:
    x, y = _point(point)
    if not (0 <= x <= max_x and 0 <= y <= max_y):
        raise GeometryValidationError("POINT_OUT_OF_BOUNDS", "Tọa độ nằm ngoài phạm vi ảnh.")
    return x, y


def pixel_to_normalized(point: Sequence[Real], width: int, height: int) -> Point:
    """Map one source/analysis pixel point to [0,1] using its actual W−1/H−1.

    Dimensions are after EXIF, each >=2. Reject out-of-bounds/nonfinite
    coordinates; retain fractions and never clamp or mutate the input.
    """
    max_x, max_y = _scales(width, height)
    x, y = _bounded_point(point, max_x, max_y)
    return x / max_x, y / max_y


def normalized_to_pixel(point: Sequence[Real], width: int, height: int) -> Point:
    """Map one finite [u,v] in [0,1] to source pixels without rounding.

    GeometryValidationError carries INVALID_DIMENSIONS, INVALID_POINT or
    POINT_OUT_OF_BOUNDS. Use the dimensions of the normalized source.
    """
    max_x, max_y = _scales(width, height)
    u, v = _bounded_point(point, 1, 1)
    return u * max_x, v * max_y


def _quad_pixels(corners: Sequence[Sequence[Real]], width: int, height: int) -> Quad:
    _scales(width, height)
    try:
        if isinstance(corners, (str, bytes, Mapping)) or len(corners) != 4:
            raise ValueError
    except (TypeError, ValueError) as error:
        raise GeometryValidationError("INVALID_CORNER_COUNT", "Vùng chọn phải có đúng bốn điểm.") from error
    pixels = tuple(normalized_to_pixel(point, width, height) for point in corners)
    return pixels[0], pixels[1], pixels[2], pixels[3]


def validate_quad_points(corners: Sequence[Sequence[Real]], width: int, height: int) -> Quad:
    """Check four normalized points and return source pixel points in input order.

    This partial gate checks shape/range, all six point pairs and four cyclic
    edges (including 3→0). It does NOT certify area, convexity, winding or
    intersections; the later topology gate must run before any homography.
    Distances <=1e-6*diagonal are duplicates; edges <=1e-3*diagonal are too
    short. No rounding, sorting, clamping or detector minimum-area filter.
    Errors add INVALID_CORNER_COUNT, DUPLICATE_POINTS and SHORT_EDGE to the
    coordinate helper's reason codes.
    """
    pixels = _quad_pixels(corners, width, height)
    diagonal = hypot(*_scales(width, height))
    duplicate_epsilon = POINT_DISTANCE_EPS_RATIO * diagonal
    min_edge = MIN_EDGE_LENGTH_RATIO * diagonal
    for i, j in combinations(range(4), 2):
        if dist(pixels[i], pixels[j]) <= duplicate_epsilon:
            raise GeometryValidationError("DUPLICATE_POINTS", f"Điểm {i} và {j} trùng hoặc quá gần nhau.")
    for i in range(4):
        j = (i + 1) % 4
        if dist(pixels[i], pixels[j]) <= min_edge:
            raise GeometryValidationError("SHORT_EDGE", f"Cạnh {i}→{j} quá ngắn (ngưỡng {min_edge:.6g} pixel).")
    return pixels[0], pixels[1], pixels[2], pixels[3]


def _cross(a: Point, b: Point, c: Point) -> float:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def _signed_area(points: Quad) -> float:
    # Shoelace translated to p0, equivalent to two signed triangles. Avoid
    # subtracting large global products for a small crop near the image edge.
    return fsum(_cross(points[0], points[i], points[i + 1]) for i in (1, 2)) / 2


def _segments_intersect(a: Point, b: Point, c: Point, d: Point) -> bool:
    """Include endpoint touch/collinear overlap, in diagonal-scaled pixels."""
    epsilon = POINT_DISTANCE_EPS_RATIO

    def orientation(p: Point, q: Point, r: Point) -> int:
        cross = _cross(p, q, r)
        if abs(cross) <= epsilon * dist(p, q):
            return 0
        return 1 if cross > 0 else -1

    def on_segment(p: Point, q: Point, r: Point) -> bool:
        return all(min(p[k], q[k]) - epsilon <= r[k] <= max(p[k], q[k]) + epsilon for k in (0, 1))

    o1, o2 = orientation(a, b, c), orientation(a, b, d)
    o3, o4 = orientation(c, d, a), orientation(c, d, b)
    if o1 * o2 < 0 and o3 * o4 < 0:
        return True
    return (
        (o1 == 0 and on_segment(a, b, c)) or (o2 == 0 and on_segment(a, b, d))
        or (o3 == 0 and on_segment(c, d, a)) or (o4 == 0 and on_segment(c, d, b))
    )


def validate_quad(corners: Sequence[Sequence[Real]], width: int, height: int) -> Quad:
    """Return pixel corners only for a simple, strictly convex clockwise quad.

    Input is normalized and cyclic; keep its start/handle order unchanged.
    In y-down coordinates positive signed area means clockwise. After the
    point/edge gate, reject near-collinear turns, opposite-edge crossings or
    touches, area <=1e-6*D², concavity and reversed winding (in that order).
    GeometryValidationError adds DEGENERATE_QUAD, SELF_INTERSECTION,
    NON_CONVEX_QUAD and INVALID_WINDING. No right-angle or parallel test.
    """
    pixels = validate_quad_points(corners, width, height)
    diagonal = hypot(*_scales(width, height))
    scaled = tuple((x / diagonal, y / diagonal) for x, y in pixels)
    turns = []
    for i in range(4):
        a, b, c = scaled[i], scaled[(i + 1) % 4], scaled[(i + 2) % 4]
        turn = _cross(a, b, c)
        # Cross has area units: compare to a distance tolerance times edge
        # length, rather than comparing an area directly to a pixel epsilon.
        if abs(turn) <= POINT_DISTANCE_EPS_RATIO * max(dist(a, b), dist(b, c)):
            raise GeometryValidationError("DEGENERATE_QUAD", "Ba góc liên tiếp thẳng hàng hoặc quá gần thẳng hàng.")
        turns.append(turn)
    if _segments_intersect(scaled[0], scaled[1], scaled[2], scaled[3]) or _segments_intersect(
        scaled[1], scaled[2], scaled[3], scaled[0]
    ):
        raise GeometryValidationError("SELF_INTERSECTION", "Các cạnh đối của vùng chọn giao hoặc chạm nhau.")
    area = _signed_area(scaled)
    if abs(area) <= MIN_QUAD_AREA_RATIO:
        raise GeometryValidationError("DEGENERATE_QUAD", "Diện tích vùng chọn quá nhỏ hoặc gần suy biến.")
    if not (all(turn > 0 for turn in turns) or all(turn < 0 for turn in turns)):
        raise GeometryValidationError("NON_CONVEX_QUAD", "Vùng chọn phải là tứ giác lồi.")
    if area < 0:
        raise GeometryValidationError("INVALID_WINDING", "Các góc phải theo chiều kim đồng hồ trong ảnh.")
    return pixels


def order_auto_corners(corners: Sequence[Sequence[Real]], width: int, height: int) -> Quad:
    """Order an automatic four-point proposal; return normalized corners.

    Sort around the mean of the source pixel points using atan2, make signed
    area positive, then rotate the cycle to min(x+y), tie-break y then x in
    source pixels. Each original vertex appears exactly once, unchanged.
    Validate the final cycle; reject invalid sets rather than invent corners.
    Never call this for manual handles: use validate_quad to retain IDs/order.
    """
    pixels = _quad_pixels(corners, width, height)
    diagonal = hypot(*_scales(width, height))
    scaled = tuple((x / diagonal, y / diagonal) for x, y in pixels)
    cx, cy = (fsum(point[k] for point in scaled) / 4 for k in (0, 1))
    indices = sorted(range(4), key=lambda i: (
        atan2(scaled[i][1] - cy, scaled[i][0] - cx), scaled[i][1], scaled[i][0],
    ))
    cycle = tuple(scaled[i] for i in indices)
    if _signed_area(cycle) < 0:
        indices.reverse()
    start = min(range(4), key=lambda j: (
        sum(scaled[indices[j]]), scaled[indices[j]][1], scaled[indices[j]][0],
    ))
    indices = indices[start:] + indices[:start]
    ordered = tuple(_point(corners[i]) for i in indices)
    validate_quad(ordered, width, height)
    return ordered[0], ordered[1], ordered[2], ordered[3]


def _estimated_size(pixels: Quad) -> tuple[int, int]:
    p0, p1, p2, p3 = pixels
    width = max(2, floor(max(dist(p0, p1), dist(p2, p3)) + 0.5))
    height = max(2, floor(max(dist(p0, p3), dist(p1, p2)) + 0.5))
    longest = max(width, height)
    if longest > MAX_WARP_LONG_EDGE:
        # Same exact half-up scaling rule as display resizing, with a geometry
        # minimum of 2 instead of 1. Preserve the ratio of rounded estimates.
        width = max(2, (2 * width * MAX_WARP_LONG_EDGE + longest) // (2 * longest))
        height = max(2, (2 * height * MAX_WARP_LONG_EDGE + longest) // (2 * longest))
    if max(width, height) > MAX_WARP_LONG_EDGE or width * height > MAX_WARP_PIXELS:
        raise GeometryValidationError("INVALID_WARP_SIZE", "Kích thước warp vượt giới hạn đầu ra.")
    return width, height


def estimate_warp_size(corners: Sequence[Sequence[Real]], width: int, height: int) -> tuple[int, int]:
    """Validate normalized corners and return estimated output (W,H).

    Use the longer pair of opposite source-pixel edges on each axis, half-up
    round, minimum 2, then cap both axes together at 2400 (5,760,000 pixels).
    No upscale to the limit and no physical paper/A4 aspect inference.
    Edge lengths are spans: full 101x51 source estimates 100x50, per spec.
    """
    return _estimated_size(validate_quad(corners, width, height))


def compute_homography(
    corners: Sequence[Sequence[Real]], width: int, height: int,
) -> tuple[NDArray[np.float64], tuple[int, int]]:
    """Return source→destination H and estimated (W,H), after full validation.

    Match p0,p1,p2,p3 to (0,0),(W−1,0),(W−1,H−1),(0,H−1). Keep source
    fractions (OpenCV requires float32 point arrays), no sorting of handles.
    Reject a nonfinite or singular matrix before image allocation/sampling.
    https://docs.opencv.org/4.x/da/d54/group__imgproc__transform.html
    """
    pixels = validate_quad(corners, width, height)
    size = _estimated_size(pixels)
    w, h = size
    source_points = np.array(pixels, dtype=np.float32)
    destination_points = np.array([(0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1)], dtype=np.float32)
    try:
        matrix = cv2.getPerspectiveTransform(source_points, destination_points)
        if matrix.shape != (3, 3) or not np.all(np.isfinite(matrix)):
            raise GeometryValidationError("INVALID_HOMOGRAPHY", "Ma trận phối cảnh không hữu hạn hoặc sai kích thước.")
        sign, log_determinant = np.linalg.slogdet(matrix)
        if sign == 0 or not np.isfinite(log_determinant):
            raise GeometryValidationError("INVALID_HOMOGRAPHY", "Ma trận phối cảnh không khả nghịch.")
    except (cv2.error, np.linalg.LinAlgError) as error:
        raise GeometryValidationError("INVALID_HOMOGRAPHY", "Không tính được ma trận phối cảnh hợp lệ.") from error
    return matrix, size


def warp_document(source: NDArray[np.uint8], corners: Sequence[Sequence[Real]]) -> NDArray[np.uint8]:
    """Warp normalized-source BGR uint8 to an independent rectangular image.

    Input HWC3, dimensions >=2 and <=16 MP; normalized corners must pass
    full geometry validation. Estimated output <=2400 per side /5.76 MP.
    H is forward source→target; warpPerspective samples inversely using
    INTER_LINEAR, BORDER_REPLICATE. No EXIF, filters, rotation or preview here.
    Errors add INVALID_SOURCE, TOO_MANY_PIXELS and WARP_FAILED; no HTTP/DB.
    """
    if not isinstance(source, np.ndarray) or source.dtype != np.uint8 or source.ndim != 3 or source.shape[2] != 3:
        raise GeometryValidationError("INVALID_SOURCE", "Nguồn warp phải là BGR uint8, shape (H,W,3).")
    height, width = source.shape[:2]
    _scales(width, height)
    if width * height > MAX_IMAGE_PIXELS:
        raise GeometryValidationError("TOO_MANY_PIXELS", "Ảnh nguồn vượt giới hạn 16 triệu pixel.")
    matrix, size = compute_homography(corners, width, height)
    try:
        if max(width, height) >= 32767:
            return _warp_large_source(source, matrix, size)
        return cv2.warpPerspective(source, matrix, size, flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    except cv2.error as error:
        raise GeometryValidationError("WARP_FAILED", "Không lấy mẫu được ảnh sau biến đổi phối cảnh.") from error


def _warp_large_source(source: NDArray[np.uint8], matrix: NDArray[np.float64], size: tuple[int, int]) -> NDArray[np.uint8]:
    """Sample original source ROIs below OpenCV remap's SHRT_MAX limit.

    Split destination rectangles until each inverse-mapped source bounding
    box fits. A one-pixel halo retains all bilinear neighbors across seams.
    A projective map keeps straight edges straight, so four tile corners
    bound the donor region. No intermediate source resize or extra filtering.
    """
    width, height = size
    source_h, source_w = source.shape[:2]
    inverse = np.linalg.inv(matrix)
    output = np.empty((height, width, 3), dtype=np.uint8)
    pending = [(0, 0, width, height)]
    while pending:
        x0, y0, x1, y1 = pending.pop()
        target = np.array([[(x0,y0),(x1-1,y0),(x1-1,y1-1),(x0,y1-1)]], dtype=np.float64)
        donor = cv2.perspectiveTransform(target, inverse)[0]
        if not np.all(np.isfinite(donor)):
            raise GeometryValidationError("INVALID_HOMOGRAPHY", "Ánh xạ ngược không hữu hạn.")
        lo = np.floor(donor.min(axis=0)).astype(np.int64) - 1
        hi = np.ceil(donor.max(axis=0)).astype(np.int64) + 2
        sx0, sy0 = max(0, int(lo[0])), max(0, int(lo[1]))
        sx1, sy1 = min(source_w, int(hi[0])), min(source_h, int(hi[1]))
        if sx1 <= sx0 or sy1 <= sy0:
            raise GeometryValidationError("INVALID_HOMOGRAPHY", "Vùng lấy mẫu nằm ngoài ảnh nguồn.")
        if max(sx1-sx0, sy1-sy0) >= 32767:
            if x1-x0 >= y1-y0 and x1-x0 > 1:
                middle = (x0+x1)//2
                pending.extend([(x0,y0,middle,y1),(middle,y0,x1,y1)])
            else:
                middle = (y0+y1)//2
                pending.extend([(x0,y0,x1,middle),(x0,middle,x1,y1)])
            continue
        # H_local = translation(-target_origin) @ H @ translation(source_origin).
        local = matrix @ np.array([[1,0,sx0],[0,1,sy0],[0,0,1]], dtype=np.float64)
        local[0] -= x0 * local[2]
        local[1] -= y0 * local[2]
        output[y0:y1,x0:x1] = cv2.warpPerspective(
            source[sy0:sy1,sx0:sx1], local, (x1-x0,y1-y0),
            flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE,
        )
    return output
