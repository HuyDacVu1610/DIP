"""Regression checks for input validation and source normalization."""

import json
import hashlib
import struct
import zlib
from io import BytesIO
from pathlib import Path

import numpy as np
import pytest
from PIL import Image, ImageFile, PngImagePlugin

from app.processing.normalize import ImageValidationError, encode_normalized_png, normalize_image, validate_image
from app.settings import MAX_IMAGE_PIXELS, MAX_UPLOAD_BYTES

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"
MANIFEST = json.loads((FIXTURES / "manifest.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("entry", MANIFEST["fixtures"], ids=lambda entry: entry["path"])
def test_manifest_validation_cases(entry):
    data = (FIXTURES / entry["path"]).read_bytes()
    expected = entry["expected"]
    if expected["validation"] == "reject":
        with pytest.raises(ImageValidationError) as error:
            validate_image(data)
        assert error.value.code == expected["error_code"]
        assert str(error.value)
    else:
        info = validate_image(data)
        assert info.format == expected["format"]
        assert (info.width, info.height) == tuple(expected["size"])
        assert info.mode == expected["mode"]
        assert info.frame_count == expected["frames"]
        assert info.byte_count == len(data)
    assert data == (FIXTURES / entry["path"]).read_bytes()


def test_empty_input_has_a_clear_error():
    with pytest.raises(ImageValidationError) as error:
        validate_image(b"")
    assert error.value.code == "EMPTY_FILE"


def test_byte_quota_accepts_exactly_15_mib():
    data = (FIXTURES / "minimum.png").read_bytes()
    padded = data + b"\0" * (MAX_UPLOAD_BYTES - len(data))
    assert validate_image(padded).byte_count == MAX_UPLOAD_BYTES


def test_byte_quota_rejects_one_extra_byte_before_open(monkeypatch):
    def forbidden_open(*args, **kwargs):
        pytest.fail("Oversized input reached the image parser")

    monkeypatch.setattr(Image, "open", forbidden_open)
    with pytest.raises(ImageValidationError) as error:
        validate_image(b"\0" * (MAX_UPLOAD_BYTES + 1))
    assert error.value.code == "FILE_TOO_LARGE"


@pytest.mark.parametrize("filename", ["pixel_over.png", "bomb_warning.png", "bomb_error.png"])
def test_large_header_rejected_before_verify_or_decode(filename, monkeypatch):
    def forbidden_decode(*args, **kwargs):
        pytest.fail("Oversized header reached verify/load")

    monkeypatch.setattr(Image.Image, "load", forbidden_decode)
    monkeypatch.setattr(ImageFile.ImageFile, "load", forbidden_decode)
    monkeypatch.setattr(PngImagePlugin.PngImageFile, "verify", forbidden_decode)
    with pytest.raises(ImageValidationError) as error:
        validate_image((FIXTURES / filename).read_bytes())
    assert error.value.code == "TOO_MANY_PIXELS"


@pytest.mark.parametrize("filename", ["corners_rgb.png", "exif_6.jpg", "alpha_rgba.png", "pixel_limit.png"])
def test_header_validation_does_not_decode_or_apply_exif(filename, monkeypatch):
    def forbidden_load(*args, **kwargs):
        pytest.fail("Header validation decoded a raster")

    monkeypatch.setattr(Image.Image, "load", forbidden_load)
    monkeypatch.setattr(ImageFile.ImageFile, "load", forbidden_load)
    info = validate_image((FIXTURES / filename).read_bytes())
    if filename == "exif_6.jpg":
        assert (info.width, info.height) == (96, 64)
    if filename == "pixel_limit.png":
        assert info.width * info.height == MAX_IMAGE_PIXELS


def test_pillow_safety_threshold_is_preserved_after_a_rejection():
    threshold = Image.MAX_IMAGE_PIXELS
    with pytest.raises(ImageValidationError):
        validate_image((FIXTURES / "bomb_warning.png").read_bytes())
    assert Image.MAX_IMAGE_PIXELS == threshold
    assert validate_image((FIXTURES / "minimum.png").read_bytes()).width == 2


@pytest.mark.parametrize(
    "entry", [entry for entry in MANIFEST["fixtures"] if entry["expected"]["validation"] == "accept"],
    ids=lambda entry: entry["path"],
)
def test_normalized_fixture_matches_known_pixels_and_dimensions(entry):
    data = (FIXTURES / entry["path"]).read_bytes()
    expected = entry["expected"]
    source = normalize_image(data)
    width, height = expected.get("normalized_size", expected["size"])
    assert source.shape == (height, width, 3)
    assert source.dtype == np.uint8
    assert source.flags.c_contiguous and source.flags.writeable
    colors = expected.get("normalized_corners_rgb", expected.get("corners_rgb"))
    if colors:
        points = [(12, 12), (width - 13, 12), (width - 13, height - 13), (12, height - 13)]
        tolerance = MANIFEST["jpeg_rgb_tolerance"] if expected["format"] == "JPEG" else 0
        for (x, y), color in zip(points, colors):
            np.testing.assert_allclose(source[y, x], color[::-1], atol=tolerance, rtol=0)
    if "white_background_rgb_row" in expected:
        assert source[0].tolist() == [color[::-1] for color in expected["white_background_rgb_row"]]
    if "gray_value" in expected:
        assert np.all(source == expected["gray_value"])
    source[0, 0] = 0
    assert data == (FIXTURES / entry["path"]).read_bytes()


@pytest.mark.parametrize("orientation,corner_order", [
    (1, [0, 1, 2, 3]), (2, [1, 0, 3, 2]), (3, [2, 3, 0, 1]), (4, [3, 2, 1, 0]),
    (5, [0, 3, 2, 1]), (6, [3, 0, 1, 2]), (7, [2, 1, 0, 3]), (8, [1, 2, 3, 0]),
])
def test_all_eight_exif_orientations_have_the_expected_corner_mapping(orientation, corner_order):
    with Image.open(FIXTURES / "corners_rgb.png") as image:
        exif = Image.Exif()
        exif[274] = orientation
        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=95, subsampling=0, exif=exif)
    source = normalize_image(buffer.getvalue())
    width, height = (64, 96) if orientation >= 5 else (96, 64)
    assert source.shape == (height, width, 3)
    points = [(12, 12), (width - 13, 12), (width - 13, height - 13), (12, height - 13)]
    for (x, y), index in zip(points, corner_order):
        expected = MANIFEST["fixtures"][0]["expected"]["corners_rgb"][index][::-1]
        np.testing.assert_allclose(source[y, x], expected, atol=3, rtol=0)


@pytest.mark.parametrize("mode,color,transparency,expected", [
    ("LA", (50, 128), None, [152, 152, 152]),
    ("L", 50, 50, [255, 255, 255]),
    ("RGB", (255, 0, 0), (255, 0, 0), [255, 255, 255]),
])
def test_alpha_and_transparency_key_are_composited_on_white(mode, color, transparency, expected):
    image = Image.new(mode, (2, 2), color)
    buffer = BytesIO()
    options = {"transparency": transparency} if transparency is not None else {}
    image.save(buffer, format="PNG", **options)
    source = normalize_image(buffer.getvalue())
    assert np.all(source == np.array(expected, dtype=np.uint8))


def test_cmyk_jpeg_is_converted_to_bgr():
    image = Image.new("CMYK", (2, 2), (0, 255, 255, 0))
    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=100)
    source = normalize_image(buffer.getvalue())
    np.testing.assert_allclose(source[0, 0], [0, 0, 255], atol=1, rtol=0)


@pytest.mark.parametrize("kind", ["jpeg", "png"])
def test_decode_errors_are_rejected_even_after_header_verification(kind):
    if kind == "jpeg":
        data = (FIXTURES / "corners_rgb.jpg").read_bytes()[:-100]
    else:
        # Valid PNG container/CRCs with an invalid compressed pixel stream.
        def chunk(name, payload):
            return struct.pack(">I", len(payload)) + name + payload + struct.pack(">I", zlib.crc32(name + payload))

        header = struct.pack(">IIBBBBB", 2, 2, 8, 2, 0, 0, 0)
        data = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", b"bad zlib") + chunk(b"IEND", b"")
    assert validate_image(data).width >= 2
    with pytest.raises(ImageValidationError) as error:
        normalize_image(data)
    assert error.value.code == "INVALID_IMAGE"
    assert ImageFile.LOAD_TRUNCATED_IMAGES is False


@pytest.mark.parametrize("filename", ["animated.png", "pixel_over.png", "bomb_warning.png", "bomb_error.png"])
def test_normalize_rejects_invalid_input_before_decoding(filename, monkeypatch):
    def forbidden_load(*args, **kwargs):
        pytest.fail("Rejected input was decoded by normalization")

    monkeypatch.setattr(Image.Image, "load", forbidden_load)
    monkeypatch.setattr(ImageFile.ImageFile, "load", forbidden_load)
    with pytest.raises(ImageValidationError):
        normalize_image((FIXTURES / filename).read_bytes())


@pytest.mark.parametrize(
    "filename", [entry["path"] for entry in MANIFEST["fixtures"] if entry["expected"]["validation"] == "accept"],
)
def test_saved_normalized_png_preserves_pixels_dimensions_and_file_hash(filename, tmp_path):
    source = normalize_image((FIXTURES / filename).read_bytes())
    original = source.copy()
    encoded = encode_normalized_png(source)
    path = tmp_path / "source.png"
    assert path.write_bytes(encoded.png_bytes) == len(encoded.png_bytes)
    stored = path.read_bytes()
    assert encoded.sha256 == hashlib.sha256(stored).hexdigest()
    assert encoded.width == source.shape[1] and encoded.height == source.shape[0]
    with Image.open(path) as image:
        image.load()
        assert image.format == "PNG" and image.mode == "RGB"
        assert image.size == (encoded.width, encoded.height)
        assert not image.getexif()
        assert "exif" not in image.info
        restored = np.asarray(image)[:, :, ::-1]
        np.testing.assert_array_equal(restored, source)
    np.testing.assert_array_equal(source, original)


@pytest.mark.parametrize("filename", ["exif_6.jpg", "exif_2.jpg"])
def test_reopening_normalized_png_does_not_apply_exif_again(filename):
    source = normalize_image((FIXTURES / filename).read_bytes())
    first = encode_normalized_png(source)
    reopened = normalize_image(first.png_bytes)
    second = encode_normalized_png(reopened)
    np.testing.assert_array_equal(reopened, source)
    assert (second.width, second.height) == (first.width, first.height)
    assert second.png_bytes == first.png_bytes
    assert second.sha256 == first.sha256


def test_png_hash_is_stable_for_same_pixels_and_changes_for_different_pixels():
    source = normalize_image((FIXTURES / "corners_rgb.png").read_bytes())
    first = encode_normalized_png(source)
    repeated = encode_normalized_png(source.copy())
    assert repeated.png_bytes == first.png_bytes
    assert repeated.sha256 == first.sha256
    source[0, 0, 0] ^= 1
    changed = encode_normalized_png(source)
    assert changed.sha256 != first.sha256
    assert first.sha256 == hashlib.sha256(first.png_bytes).hexdigest()


def test_png_encoder_preserves_pixels_from_a_non_contiguous_bgr_view():
    source = normalize_image((FIXTURES / "corners_rgb.png").read_bytes())[:, ::-1, :]
    assert not source.flags.c_contiguous
    encoded = encode_normalized_png(source)
    with Image.open(BytesIO(encoded.png_bytes)) as image:
        np.testing.assert_array_equal(np.asarray(image)[:, :, ::-1], source)


@pytest.mark.parametrize("array", [
    np.zeros((2, 2), dtype=np.uint8),
    np.zeros((2, 2, 1), dtype=np.uint8),
    np.zeros((2, 2, 4), dtype=np.uint8),
    np.zeros((2, 2, 3), dtype=np.float32),
    np.zeros((2, 2, 3), dtype=np.uint16),
])
def test_png_encoder_rejects_arrays_outside_the_bgr_uint8_contract(array):
    with pytest.raises(ImageValidationError) as error:
        encode_normalized_png(array)
    assert error.value.code == "INVALID_NORMALIZED_IMAGE"


@pytest.mark.parametrize("shape,code", [
    ((1, 2, 3), "IMAGE_TOO_SMALL"), ((2, 1, 3), "IMAGE_TOO_SMALL"),
    ((4000, 4001, 3), "TOO_MANY_PIXELS"),
])
def test_png_encoder_rejects_invalid_dimensions_before_allocating_an_image(shape, code, monkeypatch):
    def forbidden_fromarray(*args, **kwargs):
        pytest.fail("Invalid dimensions reached the PNG encoder")

    monkeypatch.setattr(Image, "fromarray", forbidden_fromarray)
    array = np.broadcast_to(np.zeros(3, dtype=np.uint8), shape)
    with pytest.raises(ImageValidationError) as error:
        encode_normalized_png(array)
    assert error.value.code == code
