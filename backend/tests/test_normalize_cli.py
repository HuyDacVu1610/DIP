"""Exercise the real command, its saved artifacts and failure behavior."""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from app.processing.image_sizes import resize_to_max_edge
from app.processing.normalize import normalize_image
from app.settings import MAX_UPLOAD_BYTES

PROJECT = Path(__file__).resolve().parents[2]
SCRIPT = PROJECT / "experiments" / "normalize_one.py"
FIXTURES = PROJECT / "fixtures"


def run_cli(input_path, output_path, cwd, *options):
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(input_path), "--output-dir", str(output_path), *options],
        cwd=cwd, capture_output=True, text=True, encoding="utf-8", timeout=30,
    )


@pytest.mark.parametrize("filename", ["exif_6.jpg", "alpha_rgba.png", "minimum.png", "pixel_limit.png"])
def test_cli_saved_outputs_have_correct_pixels_dimensions_and_hashes(filename, tmp_path):
    original = (FIXTURES / filename).read_bytes()
    # Unicode and spaces should work; the script must not depend on cwd.
    input_path = tmp_path / "ảnh đầu vào.jpg"
    input_path.write_bytes(original)
    output = tmp_path / "kết quả"
    result = run_cli(input_path, output, tmp_path, "--thumbnail-max-edge", "32")
    assert result.returncode == 0, result.stderr
    assert not result.stderr
    metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
    assert metadata["input"]["byte_count"] == len(original)
    assert metadata["input"]["sha256"] == hashlib.sha256(original).hexdigest()
    source = normalize_image(original)
    with Image.open(output / "source.png") as image:
        image.load()
        np.testing.assert_array_equal(np.asarray(image)[:, :, ::-1], source)
        assert not image.getexif()
    with Image.open(output / "thumbnail.png") as image:
        np.testing.assert_array_equal(np.asarray(image)[:, :, ::-1], resize_to_max_edge(source, 32))
    for key in ("source", "thumbnail"):
        info = metadata[key]
        data = (output / info["file"]).read_bytes()
        assert info["sha256"] == hashlib.sha256(data).hexdigest()
        with Image.open(output / info["file"]) as image:
            image.load()
            assert image.size == (info["width"], info["height"])
            assert image.format == "PNG" and image.mode == "RGB"
    thumb = metadata["thumbnail"]
    assert max(thumb["width"], thumb["height"]) <= 32
    assert thumb["width"] <= metadata["source"]["width"]
    assert thumb["height"] <= metadata["source"]["height"]
    assert input_path.read_bytes() == original


@pytest.mark.parametrize("filename,code", [
    ("fake.jpg", "UNSUPPORTED_FORMAT"), ("broken_crc.png", "INVALID_IMAGE"),
    ("pixel_over.png", "TOO_MANY_PIXELS"), ("animated.png", "MULTI_FRAME_IMAGE"),
])
def test_cli_rejects_bad_inputs_with_clear_errors_and_no_success_artifacts(filename, code, tmp_path):
    output = tmp_path / "output"
    result = run_cli(FIXTURES / filename, output, tmp_path)
    assert result.returncode == 1
    assert code in result.stderr and "Traceback" not in result.stderr
    assert not result.stdout and not output.exists()


def test_cli_rejects_an_input_over_byte_quota(tmp_path):
    path = tmp_path / "too_large.jpg"
    with path.open("wb") as file:
        file.truncate(MAX_UPLOAD_BYTES + 1)
    output = tmp_path / "output"
    result = run_cli(path, output, tmp_path)
    assert result.returncode == 1 and "FILE_TOO_LARGE" in result.stderr
    assert not output.exists()


def test_cli_does_not_overwrite_an_existing_output_or_input_file(tmp_path):
    input_path = tmp_path / "source.png"
    original = (FIXTURES / "corners_rgb.png").read_bytes()
    input_path.write_bytes(original)
    result = run_cli(input_path, tmp_path, tmp_path)
    assert result.returncode == 1 and "OUTPUT_EXISTS" in result.stderr
    assert input_path.read_bytes() == original
    assert not (tmp_path / "metadata.json").exists()


def test_cli_reports_a_missing_input_without_a_traceback(tmp_path):
    result = run_cli(tmp_path / "missing.jpg", tmp_path / "output", tmp_path)
    assert result.returncode == 1 and "IO_ERROR" in result.stderr
    assert "Traceback" not in result.stderr


@pytest.mark.parametrize("edge", ["0", "-1", "1.5"])
def test_cli_rejects_bad_thumbnail_arguments(edge, tmp_path):
    result = run_cli(FIXTURES / "minimum.png", tmp_path / "output", tmp_path, "--thumbnail-max-edge", edge)
    assert result.returncode == 2 and "--thumbnail-max-edge" in result.stderr
    assert not (tmp_path / "output").exists()


def test_cli_can_save_a_one_pixel_wide_thumbnail(tmp_path):
    path = tmp_path / "thin.png"
    Image.new("RGB", (2, 4000), "white").save(path)
    output = tmp_path / "output"
    result = run_cli(path, output, tmp_path)
    assert result.returncode == 0, result.stderr
    metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
    assert (metadata["thumbnail"]["width"], metadata["thumbnail"]["height"]) == (1, 320)


def test_cli_help_documents_the_required_output_directory(tmp_path):
    result = subprocess.run([sys.executable, str(SCRIPT), "--help"], cwd=tmp_path,
                            capture_output=True, text=True, encoding="utf-8", timeout=30)
    assert result.returncode == 0
    assert "--output-dir" in result.stdout and "--thumbnail-max-edge" in result.stdout
