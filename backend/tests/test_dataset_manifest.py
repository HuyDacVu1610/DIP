"""Dataset identity, split and file-integrity guards; no detector tuning."""

import csv
import hashlib
import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "experiments" / "validate_dataset.py"
spec = importlib.util.spec_from_file_location("validate_dataset", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def row(image_id="img_001", document_id="doc_01", split="development", **changes):
    values = dict(zip(module.FIELDS, [image_id, document_id, "even_light", split,
                                    f"experiments/data/{image_id}.jpg", "a" * 64, "", ""]))
    return {**values, **changes}


def manifest(tmp_path, rows, fields=None):
    path = tmp_path / "manifest.csv"
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields or module.FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return path


def test_empty_manifest_reports_zero_real_images_without_claiming_collection(tmp_path):
    report = module.validate_manifest(manifest(tmp_path, []), tmp_path)
    assert report["images"] == {"development": 0, "test": 0}
    assert report["documents"] == {"development": 0, "test": 0}
    assert report["files_checked"] is False


def test_multiple_photos_of_a_document_share_one_split(tmp_path):
    rows = [row(), row("img_002", source_sha256="b" * 64, condition="perspective;shadow_strong"),
            row("img_003", "doc_07", "test", source_sha256="c" * 64)]
    report = module.validate_manifest(manifest(tmp_path, rows), tmp_path)
    assert report["images"] == {"development": 2, "test": 1}
    assert report["documents"] == {"development": 1, "test": 1}


def test_real_wrinkled_and_cropped_cases_are_kept_as_conditions(tmp_path):
    report=module.validate_manifest(manifest(tmp_path,[row(condition='perspective;wrinkled;cropped')]),tmp_path)
    assert report['images']['development']==1


def test_same_document_cannot_cross_development_and_test(tmp_path):
    rows = [row(), row("img_002", split="test", source_sha256="b" * 64)]
    with pytest.raises(ValueError, match="hai split"):
        module.validate_manifest(manifest(tmp_path, rows), tmp_path)


@pytest.mark.parametrize("changes", [
    {"image_id": "img_001"}, {"source_path": "experiments/data/img_001.jpg"},
    {"source_sha256": "a" * 64},
])
def test_duplicate_id_path_or_file_hash_is_rejected(tmp_path, changes):
    second = {**row("img_002", "doc_07", "test", source_sha256="b" * 64), **changes}
    with pytest.raises(ValueError):
        module.validate_manifest(manifest(tmp_path, [row(), second]), tmp_path)


@pytest.mark.parametrize("changes", [
    {"condition": "unknown"}, {"condition": "even_light;even_light"}, {"split": "validation"},
    {"document_id": ""}, {"source_sha256": "bad"}, {"source_path": "../private.jpg"},
    {"source_path": "C:/private.jpg"}, {"source_path": "fixtures/exif_6.jpg"},
    {"normalized_path": "experiments/results/img_001/source.png"},
])
def test_invalid_record_metadata_is_rejected(tmp_path, changes):
    with pytest.raises(ValueError):
        module.validate_manifest(manifest(tmp_path, [row(**changes)]), tmp_path)


def test_header_must_match_the_documented_schema(tmp_path):
    with pytest.raises(ValueError):
        module.validate_manifest(manifest(tmp_path, [], ["image_id", "split"]), tmp_path)


def test_file_hash_check_detects_changed_source_and_missing_files(tmp_path):
    source = tmp_path / "experiments/data/img_001.jpg"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"local bytes used only for an integrity test")
    path = manifest(tmp_path, [row(source_sha256=hashlib.sha256(source.read_bytes()).hexdigest())])
    assert module.validate_manifest(path, tmp_path, check_files=True)["files_checked"] is True
    source.write_bytes(b"changed")
    with pytest.raises(ValueError, match="hash"):
        module.validate_manifest(path, tmp_path, check_files=True)
    source.unlink()
    with pytest.raises(OSError):
        module.validate_manifest(path, tmp_path, check_files=True)


def test_normalized_hash_duplicates_are_rejected_even_with_different_original_bytes(tmp_path):
    rows = [row(normalized_path="experiments/results/img_001/source.png", normalized_sha256="d" * 64),
            row("img_002", "doc_07", "test", source_sha256="b" * 64,
                normalized_path="experiments/results/img_002/source.png", normalized_sha256="d" * 64)]
    with pytest.raises(ValueError):
        module.validate_manifest(manifest(tmp_path, rows), tmp_path)
