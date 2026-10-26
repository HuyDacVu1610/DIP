"""Image input and normalization, independent of HTTP, database and UI code."""

import struct
import warnings
from dataclasses import dataclass
from hashlib import sha256
from io import BytesIO
from typing import Literal

import numpy as np
from numpy.typing import NDArray
from PIL import Image, ImageOps, UnidentifiedImageError

from ..settings import MAX_IMAGE_PIXELS, MAX_UPLOAD_BYTES


@dataclass(frozen=True, slots=True)
class ImageInfo:
    """Encoded raster metadata, before EXIF rotation or alpha compositing."""

    format: Literal["JPEG", "PNG"]
    width: int
    height: int
    mode: str
    frame_count: int
    byte_count: int


@dataclass(frozen=True, slots=True)
class EncodedSource:
    """Exact PNG payload and metadata; the storage layer writes these bytes."""

    png_bytes: bytes
    width: int
    height: int
    sha256: str


class ImageValidationError(ValueError):
    """Stable error code and a user-facing message; no HTTP status here."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def _check_dimensions(width: int, height: int) -> None:
    if width < 2 or height < 2:
        raise ImageValidationError("IMAGE_TOO_SMALL", "Chiều rộng và chiều cao ảnh phải từ 2 pixel.")
    if width * height > MAX_IMAGE_PIXELS:
        raise ImageValidationError("TOO_MANY_PIXELS", "Ảnh vượt giới hạn 16 triệu pixel.")


def validate_image(data: bytes) -> ImageInfo:
    """Check bytes/header/container without decoding pixels or changing input.

    Pillow's open() is lazy and verify() is not a full decoder. A later
    normalization step must reopen and load(), rejecting decode failures too.
    https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.verify
    """
    if not data:
        raise ImageValidationError("EMPTY_FILE", "Tệp ảnh rỗng.")
    if len(data) > MAX_UPLOAD_BYTES:
        raise ImageValidationError("FILE_TOO_LARGE", "Tệp ảnh vượt giới hạn 15 MiB.")
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        image_format: Literal["JPEG", "PNG"] = "PNG"
    elif data.startswith(b"\xff\xd8\xff"):
        image_format = "JPEG"
    else:
        raise ImageValidationError("UNSUPPORTED_FORMAT", "Chỉ hỗ trợ ảnh JPEG hoặc PNG hợp lệ.")

    try:
        # Keep Pillow's global protection intact; map its warning/error to our
        # stricter 16 MP quota even if Pillow rejects during header parsing.
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(BytesIO(data), formats=("JPEG", "PNG")) as image:
                width, height = image.size
                _check_dimensions(width, height)
                frames = getattr(image, "n_frames", 1)
                if frames != 1:
                    raise ImageValidationError("MULTI_FRAME_IMAGE", "Chỉ hỗ trợ ảnh tĩnh có một frame.")
                info = ImageInfo(image_format, width, height, image.mode, frames, len(data))
                # Quotas come first; PNG CRC/truncation checks need no raster.
                image.verify()
                return info
    except ImageValidationError:
        raise
    except (Image.DecompressionBombWarning, Image.DecompressionBombError) as error:
        raise ImageValidationError("TOO_MANY_PIXELS", "Ảnh vượt giới hạn 16 triệu pixel.") from error
    except (UnidentifiedImageError, OSError, SyntaxError, ValueError, EOFError, struct.error) as error:
        raise ImageValidationError("INVALID_IMAGE", "Không đọc được ảnh: header hoặc dữ liệu tệp bị hỏng.") from error


def normalize_image(data: bytes) -> NDArray[np.uint8]:
    """Validate uploaded bytes and return an owned, contiguous H*W*3 BGR raster.

    EXIF is applied to a fresh decoder object, not to the original bytes.
    https://pillow.readthedocs.io/en/stable/reference/ImageOps.html#PIL.ImageOps.exif_transpose
    """
    validate_image(data)
    try:
        # verify() consumes the first decoder; reopen before loading pixels.
        with Image.open(BytesIO(data), formats=("JPEG", "PNG")) as image:
            image.load()
            ImageOps.exif_transpose(image, in_place=True)
            _check_dimensions(*image.size)
            if image.has_transparency_data:
                rgba = image.convert("RGBA")
                white = Image.new("RGBA", image.size, "white")
                rgb = Image.alpha_composite(white, rgba).convert("RGB")
            else:
                rgb = image if image.mode == "RGB" else image.convert("RGB")
            # Reverse RGB channels then copy: no negative stride or decoder
            # lifetime remains in the array consumed by OpenCV.
            return np.ascontiguousarray(np.asarray(rgb, dtype=np.uint8)[:, :, ::-1])
    except ImageValidationError:
        raise
    except (OSError, SyntaxError, ValueError, EOFError, struct.error) as error:
        raise ImageValidationError("INVALID_IMAGE", "Không giải mã được ảnh: dữ liệu pixel hoặc metadata bị hỏng.") from error


def encode_normalized_png(bgr: NDArray[np.uint8]) -> EncodedSource:
    """Encode BGR pixels losslessly, without inheriting the upload's EXIF.

    The 15 MiB quota applies to uploads, not to this internal PNG artifact.
    Hash the exact payload to be saved, not raw pixels or original file bytes.
    """
    if bgr.dtype != np.uint8 or bgr.ndim != 3 or bgr.shape[2] != 3:
        raise ImageValidationError("INVALID_NORMALIZED_IMAGE", "Nguồn chuẩn hóa phải là mảng BGR uint8 có shape (H, W, 3).")
    height, width = bgr.shape[:2]
    _check_dimensions(width, height)
    buffer = BytesIO()
    # A fresh RGB image has no inherited EXIF/ICC/XMP. Pillow interprets arrays
    # as RGB, so channel reversal is required even though the core uses BGR.
    with Image.fromarray(bgr[:, :, ::-1]) as image:
        image.save(buffer, format="PNG", compress_level=6)
    png_bytes = buffer.getvalue()
    return EncodedSource(png_bytes, width, height, sha256(png_bytes).hexdigest())
