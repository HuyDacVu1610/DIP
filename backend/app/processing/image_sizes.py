"""Display resizing; source/full render remain the geometry and export inputs."""

import cv2
import numpy as np
from numpy.typing import NDArray


def resize_to_max_edge(image: NDArray[np.uint8], max_edge: int) -> NDArray[np.uint8]:
    """Return an independent gray/BGR uint8 image, never upscaling.

    Dimensions use round-half-up, clamped to one pixel for display only.
    Analysis callers must handle a one-pixel side before geometry mapping.
    https://docs.opencv.org/4.x/da/d54/group__imgproc__transform.html
    """
    if isinstance(max_edge, bool) or not isinstance(max_edge, int) or max_edge < 1:
        raise ValueError("Cạnh dài tối đa phải là số nguyên dương.")
    if image.dtype != np.uint8 or image.ndim not in (2, 3):
        raise ValueError("Ảnh phải là uint8, shape (H, W) hoặc (H, W, 3).")
    if image.ndim == 3 and image.shape[2] != 3:
        raise ValueError("Ảnh màu phải có đúng ba kênh BGR.")
    height, width = image.shape[:2]
    if min(width, height) < 1:
        raise ValueError("Ảnh không được có chiều rỗng.")
    longest = max(width, height)
    if longest <= max_edge:
        return image.copy()
    # Exact floor(dimension * max_edge / longest + 0.5), using integers so
    # a mathematical 62.5 cannot become 62.49999999999999 and round down.
    new_width = max(1, (2 * width * max_edge + longest) // (2 * longest))
    new_height = max(1, (2 * height * max_edge + longest) // (2 * longest))
    return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
