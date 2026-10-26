"""Histogram of the full uint8 gray actually consumed by thresholding."""
import cv2
import numpy as np
from numpy.typing import NDArray

from .geometry import MAX_WARP_LONG_EDGE


class HistogramValidationError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def compute_histogram(gray: NDArray[np.uint8]) -> tuple[int, ...]:
    """256 raw counts h[k] = number of pixels equal to k, k=0..255.

    Full-warp HxW uint8, each side 2..2400; no resize/mask/normalization or
    mutation. OpenCV uses float32 counts, exact here because N<=5,760,000<2**24.
    The [0,256) range includes 255. Return Python integers for JSON consumers.
    https://docs.opencv.org/4.x/d1/db7/tutorial_py_histogram_begins.html
    """
    if (not isinstance(gray, np.ndarray) or gray.dtype != np.uint8 or gray.ndim != 2
            or min(gray.shape) < 2 or max(gray.shape) > MAX_WARP_LONG_EDGE):
        raise HistogramValidationError('INVALID_HISTOGRAM_INPUT',
            'Histogram yêu cầu full gray uint8 HxW, mỗi chiều trong [2,2400].')
    try:
        counts = cv2.calcHist([gray], [0], None, [256], [0,256])
    except cv2.error as error:
        raise HistogramValidationError('HISTOGRAM_FAILED', 'Không tính được histogram ảnh xám.') from error
    return tuple(int(count) for count in counts.ravel())
