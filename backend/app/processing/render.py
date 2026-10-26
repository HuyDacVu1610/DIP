"""Offline page rendering from normalized source, independent of HTTP/DB/I/O."""
from dataclasses import dataclass
from hashlib import sha256
from io import BytesIO
from time import perf_counter_ns
from typing import Literal

import numpy as np
from numpy.typing import NDArray
from PIL import Image

from ..settings import MAX_IMAGE_PIXELS
from .config import PageConfig, parse_config
from .detection import DetectionResult, DetectionValidationError, detect_document
from .enhancement import EnhancementResult, enhance_document
from .geometry import GeometryValidationError, compute_homography, warp_document
from .image_sizes import resize_to_max_edge

MAX_PREVIEW_LONG_EDGE = 1000


class RenderValidationError(ValueError):
    def __init__(self,code: str,message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True, slots=True)
class EncodedRaster:
    png_bytes: bytes
    width: int
    height: int
    png_mode: Literal['RGB','L']
    sha256: str


@dataclass(frozen=True, slots=True)
class RenderImages:
    full: EncodedRaster
    preview: EncodedRaster


def _validate_raster(image: NDArray[np.uint8], minimum: int) -> None:
    if (not isinstance(image,np.ndarray) or image.dtype!=np.uint8 or image.ndim not in (2,3)
            or (image.ndim==3 and image.shape[2]!=3) or min(image.shape[:2])<minimum
            or max(image.shape[:2])>2400):
        raise RenderValidationError('INVALID_RENDER','Ảnh phải là gray/BGR uint8, dimensions trong giới hạn render.')


def encode_stage_png(image: NDArray[np.uint8]) -> EncodedRaster:
    """Fresh RGB/L PNG for bounded render/debug/preview; display side1 allowed.

    No inherited EXIF/ICC, channel reversal only for BGR. This internal encoder
    has no upload byte limit; source encoding still uses encode_normalized_png.
    """
    _validate_raster(image,1)
    mode = 'RGB' if image.ndim==3 else 'L'
    pixels = image[:,:,::-1] if image.ndim==3 else image
    try:
        stream = BytesIO()
        with Image.fromarray(pixels) as encoded:
            encoded.save(stream,format='PNG',compress_level=6)
        payload = stream.getvalue()
    except (OSError,ValueError) as error:
        raise RenderValidationError('ENCODE_FAILED','Không encode được PNG kết quả.') from error
    return EncodedRaster(payload,image.shape[1],image.shape[0],mode,sha256(payload).hexdigest())


def encode_render_images(full_render: NDArray[np.uint8]) -> RenderImages:
    """Encode full output and INTER_AREA preview from those exact final pixels.

    Preview max1000, half-up/no upscale, no filters or repeated thresholding.
    Full BW stays binary; resized BW preview may contain gray edge pixels.
    """
    _validate_raster(full_render,2)
    return RenderImages(encode_stage_png(full_render),
        encode_stage_png(resize_to_max_edge(full_render,MAX_PREVIEW_LONG_EDGE)))


@dataclass(frozen=True, slots=True)
class RenderTimings:
    validate: float
    detect: float
    warp: float
    enhance: float
    total: float


@dataclass(frozen=True, slots=True)
class RenderResult:
    status: Literal['rendered','manual_required']
    corners_origin: Literal['manual','detected','none']
    effective_config: PageConfig
    detection: DetectionResult | None
    warped_bgr: NDArray[np.uint8] | None
    enhancement: EnhancementResult | None
    homography: NDArray[np.float64] | None
    timings_ms: RenderTimings


def render_document(source_bgr: NDArray[np.uint8], config: object, *, debug: bool = False) -> RenderResult:
    """Validate -> manual corners or detect -> source warp -> mode -> rotation.

    An offline render may be a draft. Keep explicit confirmation from config;
    never infer it from detection or rendering. Manual corners skip detection so
    valid sources too thin for analysis can still use source-based geometry.
    API/service confirmation and revision gates belong to their later layer.
    """
    start = perf_counter_ns()
    if (not isinstance(source_bgr,np.ndarray) or source_bgr.dtype!=np.uint8
            or source_bgr.ndim!=3 or source_bgr.shape[2]!=3 or min(source_bgr.shape[:2])<2):
        raise GeometryValidationError('INVALID_SOURCE','Nguồn render phải là BGR uint8, mỗi chiều từ2pixel.')
    height,width = source_bgr.shape[:2]
    if width*height > MAX_IMAGE_PIXELS:
        raise GeometryValidationError('TOO_MANY_PIXELS','Nguồn render vượt16triệu pixel.')
    if type(debug) is not bool:
        raise DetectionValidationError('INVALID_ANALYSIS_CONFIG','debug phải là bool.')
    selected = parse_config(config,source_size=(width,height))
    validated = perf_counter_ns()
    detection = None
    detected = validated
    origin = 'manual'
    if selected.corners is None:
        origin = 'detected'
        try:
            detection = detect_document(source_bgr,debug=debug)
        except DetectionValidationError as error:
            if error.code!='ANALYSIS_TOO_SMALL':
                raise
            detection = DetectionResult('manual_required',None,None,('ANALYSIS_TOO_SMALL',),None,())
        detected = perf_counter_ns()
        if detection.corners is None:
            timings = RenderTimings((validated-start)/1e6,(detected-validated)/1e6,0.,0.,(detected-start)/1e6)
            return RenderResult('manual_required','none',selected,detection,None,None,None,timings)
        data = selected.model_dump(mode='json')
        data['corners'] = detection.corners
        selected = parse_config(data,source_size=(width,height))
    matrix,_ = compute_homography(selected.corners,width,height)
    warped = warp_document(source_bgr,selected.corners)
    warped_at = perf_counter_ns()
    enhancement = enhance_document(warped,selected,source_size=(width,height),debug=debug)
    finished = perf_counter_ns()
    timings = RenderTimings((validated-start)/1e6,(detected-validated)/1e6,
        (warped_at-detected)/1e6,(finished-warped_at)/1e6,(finished-start)/1e6)
    return RenderResult('rendered',origin,enhancement.effective_config,detection,warped,enhancement,matrix,timings)
