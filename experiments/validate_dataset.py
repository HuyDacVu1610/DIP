"""Check local dataset identity/splits and optional file hashes; no tuning."""

import argparse
import csv
import json
import re
import sys
from hashlib import sha256
from pathlib import Path, PurePosixPath

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIELDS = ("image_id", "document_id", "condition", "split", "source_path",
          "source_sha256", "normalized_path", "normalized_sha256")
CONDITIONS = {"even_light", "perspective", "shadow_light", "shadow_strong", "fold_light",
              "complex_background", "blur", "glare", "occlusion", "highlight", "wrinkled", "cropped"}


def _local_path(value: str, root: Path) -> Path:
    relative = PurePosixPath(value)
    if ("\\" in value or ":" in value or relative.is_absolute() or ".." in relative.parts
            or relative.parts[:2] not in (("experiments", "data"), ("experiments", "results"))):
        raise ValueError("Đường dẫn phải nằm trong experiments/data hoặc experiments/results, dùng dấu /.")
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Đường dẫn thoát khỏi project root.")
    return path


def _file_hash(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_manifest(path: Path, project_root: Path = PROJECT_ROOT, *, check_files: bool = False) -> dict:
    """Report actual row/document counts; this does not certify image quality."""
    with path.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("Header CSV không khớp schema dataset.")
        rows = list(reader)
    image_ids, source_paths, source_hashes = set(), set(), set()
    normalized_paths, normalized_hashes = set(), set()
    document_splits = {}
    counts = {"development": 0, "test": 0}
    for line, row in enumerate(rows, start=2):
        if None in row or any(value is None for value in row.values()):
            raise ValueError(f"Dòng {line}: số cột CSV không đúng.")
        if any(not re.fullmatch(r"[a-z][a-z0-9_-]*", row[key]) for key in ("image_id", "document_id")):
            raise ValueError(f"Dòng {line}: ID rỗng hoặc không đúng quy ước.")
        tags = row["condition"].split(";")
        if not set(tags) <= CONDITIONS or len(tags) != len(set(tags)):
            raise ValueError(f"Dòng {line}: condition không hợp lệ/trùng.")
        split, document = row["split"], row["document_id"]
        if split not in counts:
            raise ValueError(f"Dòng {line}: split phải là development hoặc test.")
        if document in document_splits and document_splits[document] != split:
            raise ValueError(f"Dòng {line}: cùng document_id xuất hiện ở hai split.")
        document_splits[document] = split
        source = _local_path(row["source_path"], project_root)
        if source.suffix.lower() not in (".jpg", ".jpeg", ".png"):
            raise ValueError(f"Dòng {line}: source phải là JPEG/PNG.")
        if not re.fullmatch(r"[0-9a-f]{64}", row["source_sha256"]):
            raise ValueError(f"Dòng {line}: source_sha256 không hợp lệ.")
        for value, seen in ((row["image_id"], image_ids), (source, source_paths),
                            (row["source_sha256"], source_hashes)):
            if value in seen:
                raise ValueError(f"Dòng {line}: ID/path/hash nguồn trùng; không đếm bản sao như ảnh mới.")
            seen.add(value)
        if check_files and _file_hash(source) != row["source_sha256"]:
            raise ValueError(f"Dòng {line}: hash nguồn không khớp tệp.")
        if bool(row["normalized_path"]) != bool(row["normalized_sha256"]):
            raise ValueError(f"Dòng {line}: normalized_path và normalized_sha256 phải đi cùng nhau.")
        if row["normalized_path"]:
            normalized = _local_path(row["normalized_path"], project_root)
            digest = row["normalized_sha256"]
            if normalized.suffix.lower() != ".png" or not re.fullmatch(r"[0-9a-f]{64}", digest):
                raise ValueError(f"Dòng {line}: nguồn chuẩn hóa phải là PNG với SHA-256 hợp lệ.")
            if normalized in normalized_paths or digest in normalized_hashes:
                raise ValueError(f"Dòng {line}: path/hash chuẩn hóa trùng.")
            normalized_paths.add(normalized)
            normalized_hashes.add(digest)
            if check_files and _file_hash(normalized) != digest:
                raise ValueError(f"Dòng {line}: hash chuẩn hóa không khớp tệp.")
        counts[split] += 1
    documents = {split: sum(value == split for value in document_splits.values()) for split in counts}
    return {"images": counts, "documents": documents, "files_checked": check_files}


def main() -> int:
    parser = argparse.ArgumentParser(description="Kiểm tra manifest/split/hash dataset cục bộ.")
    parser.add_argument("manifest", nargs="?", type=Path, default=PROJECT_ROOT / "experiments/dataset_manifest.csv")
    parser.add_argument("--check-files", action="store_true", help="Kiểm tra tệp tồn tại và hash, không dùng pixel để tune.")
    args = parser.parse_args()
    try:
        report = validate_manifest(args.manifest, check_files=args.check_files)
    except (ValueError, OSError, csv.Error) as error:
        print(f"Lỗi dataset: {error}", file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
