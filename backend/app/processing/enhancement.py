"""Staged enhancement on the full warp; never detection derivatives or previews."""

import cv2
import numpy as np
from dataclasses import dataclass
from numpy.typing import NDArray
from pydantic import ValidationError

from .config import ConfigValidationError, ContrastConfig, DenoiseConfig, PageConfig, ThresholdConfig, parse_config
from .geometry import MAX_WARP_LONG_EDGE
from .histogram import compute_histogram


class EnhancementValidationError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True, slots=True)
class EnhancementStages:
    filtered_bgr: NDArray[np.uint8]
    prepared_gray: NDArray[np.uint8] | None  # actual post-contrast gray; null for Color
    before_rotation: NDArray[np.uint8]


@dataclass(frozen=True, slots=True)
class EnhancementResult:
    image: NDArray[np.uint8]
    effective_config: PageConfig
    otsu_threshold: float | None
    stages: EnhancementStages | None = None
    histogram: tuple[int, ...] | None = None  # 256 counts of BW threshold input; not output/preview


def _validate_full_bgr(warped_bgr: NDArray[np.uint8]) -> None:
    if (not isinstance(warped_bgr, np.ndarray) or warped_bgr.dtype != np.uint8
            or warped_bgr.ndim != 3 or warped_bgr.shape[2] != 3):
        raise EnhancementValidationError('INVALID_RENDER', 'Ảnh sau warp phải là BGR uint8, shape (H,W,3).')
    height, width = warped_bgr.shape[:2]
    if min(width, height) < 2 or max(width, height) > MAX_WARP_LONG_EDGE:
        raise EnhancementValidationError('INVALID_RENDER', 'Mỗi chiều ảnh sau warp phải trong [2,2400].')


def apply_denoise(warped_bgr: NDArray[np.uint8], config: DenoiseConfig) -> NDArray[np.uint8]:
    """Return an independent BGR uint8 image with unchanged dimensions.

    Input follows the full-warp contract (HWC3, each side 2..2400). None copies;
    Median uses OpenCV's replicate border; Gaussian uses sigma=0 and reflect101.
    Kernels are the validated 3/5 preset choices. No mode conversion, CLAHE,
    threshold, EXIF, resize, HTTP or DB here; never mutate the input/config.
    https://docs.opencv.org/4.x/d4/d86/group__imgproc__filter.html
    """
    _validate_full_bgr(warped_bgr)
    try:
        selected = DenoiseConfig.model_validate(config)
    except ValidationError as error:
        reason = error.errors(include_url=False, include_input=False, include_context=False)[0]['msg']
        raise ConfigValidationError(f'Tham số lọc không hợp lệ: {reason}') from error
    if selected.method == 'none':
        return warped_bgr.copy()
    try:
        if selected.method == 'median':
            return cv2.medianBlur(warped_bgr, selected.kernel)
        return cv2.GaussianBlur(warped_bgr, (selected.kernel, selected.kernel), sigmaX=0,
                                borderType=cv2.BORDER_REFLECT_101)
    except cv2.error as error:
        raise EnhancementValidationError('FILTER_FAILED', 'Không lọc được ảnh sau warp.') from error


def render_color(filtered_bgr: NDArray[np.uint8]) -> NDArray[np.uint8]:
    """Copy filtered full-warp BGR unchanged, including colored highlights.

    Color has no active contrast fields in the MVP. Denoising is a separate,
    preceding step; this function never applies CLAHE to color channels.
    """
    _validate_full_bgr(filtered_bgr)
    return filtered_bgr.copy()


def render_gray(filtered_bgr: NDArray[np.uint8], config: ContrastConfig) -> NDArray[np.uint8]:
    """Convert filtered full-warp BGR to independent HxW uint8; optional CLAHE.

    BGR2GRAY uses luminance, not a channel average. CLAHE runs on that grayscale
    image only, with clip_limit 1..4 and an 8x8 tile grid (tile counts, not pixels).
    None keeps the raw grayscale; no threshold, resize or rotation here.
    https://docs.opencv.org/4.x/de/d25/imgproc_color_conversions.html
    https://docs.opencv.org/4.x/d5/daf/tutorial_py_histogram_equalization.html
    """
    _validate_full_bgr(filtered_bgr)
    try:
        selected = ContrastConfig.model_validate(config)
    except ValidationError as error:
        reason = error.errors(include_url=False, include_input=False, include_context=False)[0]['msg']
        raise ConfigValidationError(f'Tham số tương phản không hợp lệ: {reason}') from error
    try:
        gray = cv2.cvtColor(filtered_bgr, cv2.COLOR_BGR2GRAY)
        if selected.method == 'clahe':
            return cv2.createCLAHE(clipLimit=selected.clip_limit, tileGridSize=selected.tile_grid).apply(gray)
        return gray
    except cv2.error as error:
        raise EnhancementValidationError('MODE_FAILED', 'Không tạo được ảnh xám sau warp.') from error


def _validate_full_gray(gray: NDArray[np.uint8]) -> None:
    if not isinstance(gray, np.ndarray) or gray.dtype != np.uint8 or gray.ndim != 2:
        raise EnhancementValidationError('INVALID_RENDER', 'Ảnh trước threshold phải là gray uint8, shape (H,W).')
    if min(gray.shape) < 2 or max(gray.shape) > MAX_WARP_LONG_EDGE:
        raise EnhancementValidationError('INVALID_RENDER', 'Mỗi chiều ảnh trước threshold phải trong [2,2400].')


def apply_otsu(gray: NDArray[np.uint8]) -> tuple[NDArray[np.uint8], float]:
    """Return independent BW uint8 and the actual global Otsu threshold.

    Consume prepared full-warp gray (after denoise/optional contrast). Dark
    pixels <= threshold become 0; brighter pixels become 255. No extra blur,
    resize, polarity detection or fallback. Constant images may yield t=0.
    https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html
    """
    _validate_full_gray(gray)
    try:
        threshold, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        return bw, float(threshold)
    except cv2.error as error:
        raise EnhancementValidationError('THRESHOLD_FAILED', 'Không phân ngưỡng Otsu được ảnh xám.') from error


def apply_adaptive_gaussian(gray: NDArray[np.uint8], config: ThresholdConfig) -> NDArray[np.uint8]:
    """Return independent BW from Gaussian-weighted local mean minus C.

    Prepared full-warp HxW uint8 only; block_size odd 3..151, <= short edge,
    C integer -20..30. OpenCV uses replicate/isolated borders. Oversized blocks
    fail; no automatic clamp, Otsu fallback, extra blur or global threshold.
    https://docs.opencv.org/4.x/d7/d1b/group__imgproc__misc.html
    """
    _validate_full_gray(gray)
    try:
        selected = ThresholdConfig.model_validate(config)
    except ValidationError as error:
        reason = error.errors(include_url=False, include_input=False, include_context=False)[0]['msg']
        raise ConfigValidationError(f'Tham số phân ngưỡng không hợp lệ: {reason}') from error
    if selected.method != 'adaptive_gaussian':
        raise ConfigValidationError('apply_adaptive_gaussian yêu cầu method=adaptive_gaussian.')
    if selected.block_size > min(gray.shape):
        raise ConfigValidationError('block_size phải nhỏ hơn hoặc bằng cạnh ngắn của ảnh trước threshold.')
    try:
        return cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY, selected.block_size, selected.c)
    except cv2.error as error:
        raise EnhancementValidationError('THRESHOLD_FAILED', 'Không phân ngưỡng Adaptive Gaussian được ảnh xám.') from error


def enhance_document(warped_bgr: NDArray[np.uint8], config: PageConfig, *,
                     source_size: tuple[int, int] | None = None, debug: bool = False) -> EnhancementResult:
    """Denoise -> mode/contrast/threshold -> clockwise right-angle rotation.

    Always start from the unmodified full warp, never a previous render. Validate
    the entire config with actual pre-rotation warp dimensions before filtering;
    non-null corners also require original normalized source_size, not warp size.
    Corners/confirmation are retained; HTTP/service owns confirmation/revision
    gating. This post-warp core does no geometry, EXIF, resize, I/O or caching.
    Otsu's actual t accompanies the config; other branches return None for t.
    Optional stages capture these exact buffers before rotation, without replay.
    https://docs.opencv.org/4.x/d2/de8/group__core__array.html
    """
    _validate_full_bgr(warped_bgr)
    if type(debug) is not bool:
        raise ConfigValidationError('debug phải là bool.')
    height, width = warped_bgr.shape[:2]
    selected = parse_config(config, source_size=source_size, warp_size=(width, height))
    filtered = apply_denoise(warped_bgr, selected.denoise)
    threshold = None
    histogram = None
    prepared_gray = None
    if selected.mode == 'color':
        image = render_color(filtered)
    else:
        image = render_gray(filtered, selected.contrast)
        prepared_gray = image
        if selected.mode == 'bw':
            histogram = compute_histogram(image)
            if selected.threshold.method == 'otsu':
                image, threshold = apply_otsu(image)
            else:
                image = apply_adaptive_gaussian(image, selected.threshold)
    stages = EnhancementStages(filtered, prepared_gray, image) if debug else None
    if selected.rotation:
        rotate_code = {90: cv2.ROTATE_90_CLOCKWISE, 180: cv2.ROTATE_180,
                       270: cv2.ROTATE_90_COUNTERCLOCKWISE}[selected.rotation]
        try:
            image = cv2.rotate(image, rotate_code)
        except cv2.error as error:
            raise EnhancementValidationError('ROTATION_FAILED', 'Không xoay được ảnh kết quả.') from error
    return EnhancementResult(image, selected, threshold, stages, histogram)
