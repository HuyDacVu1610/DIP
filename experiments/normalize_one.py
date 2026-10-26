"""Normalize one local image into a new output directory; no server required."""

import argparse
import json
import sys
from hashlib import sha256
from io import BytesIO
from pathlib import Path

from PIL import Image

# Direct script execution should work from outside the repository as well.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.processing.image_sizes import resize_to_max_edge
from app.processing.normalize import ImageValidationError, encode_normalized_png, normalize_image
from app.settings import MAX_UPLOAD_BYTES


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Chuẩn hóa JPEG/PNG và tạo thumbnail cục bộ.")
    parser.add_argument("input", type=Path, help="Đường dẫn ảnh JPEG/PNG đầu vào.")
    parser.add_argument("--output-dir", type=Path, required=True,
                        help="Thư mục đầu ra mới; không ghi đè thư mục đã tồn tại.")
    parser.add_argument("--thumbnail-max-edge", type=int, default=320,
                        help="Cạnh dài thumbnail tối đa, mặc định 320 pixel; không upscale.")
    args = parser.parse_args(argv)
    if args.thumbnail_max_edge < 1:
        parser.error("--thumbnail-max-edge phải là số nguyên dương.")

    try:
        # Bound the initial read too, rather than loading a huge file and then
        # discovering its size. The validator rejects the extra byte.
        with args.input.open("rb") as file:
            data = file.read(MAX_UPLOAD_BYTES + 1)
        source = normalize_image(data)
        encoded = encode_normalized_png(source)
        thumbnail = resize_to_max_edge(source, args.thumbnail_max_edge)
        buffer = BytesIO()
        # Display thumbnails may have a one-pixel side, so they do not use
        # encode_normalized_png's >=2 source/geometry constraint.
        with Image.fromarray(thumbnail[:, :, ::-1]) as image:
            image.save(buffer, format="PNG", compress_level=6)
        thumbnail_bytes = buffer.getvalue()
        metadata = {
            "input": {"path": str(args.input.resolve()), "byte_count": len(data),
                      "sha256": sha256(data).hexdigest()},
            "source": {"file": "source.png", "width": encoded.width, "height": encoded.height,
                       "byte_count": len(encoded.png_bytes), "sha256": encoded.sha256},
            "thumbnail": {"file": "thumbnail.png", "width": thumbnail.shape[1],
                          "height": thumbnail.shape[0], "max_edge": args.thumbnail_max_edge,
                          "byte_count": len(thumbnail_bytes), "sha256": sha256(thumbnail_bytes).hexdigest()},
        }
        # Prepare all artifacts before touching output; metadata is written last.
        artifacts = [
            ("source.png", encoded.png_bytes), ("thumbnail.png", thumbnail_bytes),
            ("metadata.json", (json.dumps(metadata, ensure_ascii=False, indent=2) + "\n").encode("utf-8")),
        ]
        output = args.output_dir.resolve()
        output.mkdir(parents=True)
        for name, payload in artifacts:
            with (output / name).open("xb") as file:
                file.write(payload)
    except ImageValidationError as error:
        print(f"Lỗi [{error.code}]: {error}", file=sys.stderr)
        return 1
    except FileExistsError:
        print("Lỗi [OUTPUT_EXISTS]: Thư mục/tệp đầu ra đã tồn tại; hãy chọn thư mục mới.", file=sys.stderr)
        return 1
    except OSError as error:
        print(f"Lỗi [IO_ERROR]: Không đọc hoặc ghi được tệp: {error}", file=sys.stderr)
        return 1

    print(f"Đã chuẩn hóa; xem source.png, thumbnail.png và metadata.json tại: {output}")
    return 0


if __name__ == "__main__":
    # Keep Vietnamese paths/messages readable in Windows pipes and terminals.
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
