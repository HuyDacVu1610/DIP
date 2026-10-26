"""Generate small, synthetic fixtures locally; run from any working directory."""

import hashlib
import json
import struct
import zlib
from pathlib import Path

from PIL import Image, ImageDraw

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
COLORS = [[255, 0, 0], [0, 255, 0], [0, 0, 255], [255, 255, 0]]
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def png_chunk(name: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + name + data + struct.pack(
        ">I", zlib.crc32(name + data)
    )


def solid_png(width: int, height: int) -> bytes:
    """Compress one row at a time, without allocating a width*height raster."""
    compressor = zlib.compressobj(level=9)
    row = b"\0" + bytes([240, 240, 240]) * width
    compressed = bytearray()
    for _ in range(height):
        compressed.extend(compressor.compress(row))
    compressed.extend(compressor.flush())
    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return (
        PNG_SIGNATURE + png_chunk(b"IHDR", header)
        + png_chunk(b"IDAT", bytes(compressed)) + png_chunk(b"IEND", b"")
    )


def main() -> None:
    FIXTURES.mkdir(exist_ok=True)
    entries = []

    def record(filename: str, expected: dict, kind: str = "image") -> None:
        data = (FIXTURES / filename).read_bytes()
        entries.append({
            "path": filename, "kind": kind, "expected": expected,
            "byte_count": len(data), "sha256": hashlib.sha256(data).hexdigest(),
        })

    def save(filename: str, image: Image.Image, expected: dict, **options) -> None:
        image.save(FIXTURES / filename, **options)
        record(filename, {"validation": "accept", **expected})

    def reject(filename: str, data: bytes, code: str, kind: str = "invalid", **info) -> None:
        (FIXTURES / filename).write_bytes(data)
        record(filename, {"validation": "reject", "error_code": code, **info}, kind)

    corners = Image.new("RGB", (96, 64), "white")
    draw = ImageDraw.Draw(corners)
    for box, color in zip(
        [(0, 0, 23, 23), (72, 0, 95, 23), (72, 40, 95, 63), (0, 40, 23, 63)], COLORS
    ):
        draw.rectangle(box, fill=tuple(color))
    common = {"size": [96, 64], "mode": "RGB", "frames": 1, "corners_rgb": COLORS}
    save("corners_rgb.png", corners, {"format": "PNG", **common})
    save("corners_rgb.jpg", corners, {"format": "JPEG", **common}, quality=95, subsampling=0)
    for orientation, size, order in [(6, [64, 96], [3, 0, 1, 2]), (2, [96, 64], [1, 0, 3, 2])]:
        exif = Image.Exif()
        exif[274] = orientation
        save(f"exif_{orientation}.jpg", corners, {
            "format": "JPEG", **common, "exif_orientation": orientation,
            "normalized_size": size, "normalized_corners_rgb": [COLORS[i] for i in order],
        }, quality=95, subsampling=0, exif=exif)

    alpha = Image.new("RGBA", (4, 2), (255, 0, 0, 0))
    for x, color in enumerate([(255, 0, 0, 0), (255, 0, 0, 128), (0, 0, 255, 255), (0, 255, 0, 255)]):
        alpha.putpixel((x, 0), color)
        alpha.putpixel((x, 1), color)
    save("alpha_rgba.png", alpha, {
        "format": "PNG", "size": [4, 2], "mode": "RGBA", "frames": 1,
        "white_background_rgb_row": [[255, 255, 255], [255, 127, 127], [0, 0, 255], [0, 255, 0]],
    })
    palette = Image.new("P", (4, 2), 0)
    palette.putpalette([255, 0, 0, 0, 0, 255] + [0] * 762)
    palette.putpixel((3, 0), 1)
    save("alpha_palette.png", palette, {
        "format": "PNG", "size": [4, 2], "mode": "P", "frames": 1,
        "transparent_index": 0, "white_background_rgb_row": [[255, 255, 255]] * 3 + [[0, 0, 255]],
    }, transparency=0)
    save("gray.png", Image.new("L", (4, 2), 73), {
        "format": "PNG", "size": [4, 2], "mode": "L", "frames": 1, "gray_value": 73,
    })
    save("minimum.png", Image.new("RGB", (2, 2), "white"), {
        "format": "PNG", "size": [2, 2], "mode": "RGB", "frames": 1,
    })
    for name, size in [("too_narrow.png", (1, 4)), ("too_short.png", (4, 1))]:
        Image.new("RGB", size, "white").save(FIXTURES / name)
        record(name, {"validation": "reject", "error_code": "IMAGE_TOO_SMALL", "size": list(size)})

    good_png = (FIXTURES / "corners_rgb.png").read_bytes()
    (FIXTURES / "png_named_jpeg.jpg").write_bytes(good_png)
    record("png_named_jpeg.jpg", {"validation": "accept", "format": "PNG", **common})
    corners.save(FIXTURES / "animated.png", save_all=True,
                 append_images=[Image.new("RGB", corners.size, "black")], duration=100, loop=0)
    record("animated.png", {"validation": "reject", "error_code": "MULTI_FRAME_IMAGE", "frames": 2})
    corners.save(FIXTURES / "unsupported.bmp")
    record("unsupported.bmp", {"validation": "reject", "error_code": "UNSUPPORTED_FORMAT", "format": "BMP"})
    reject("fake.jpg", b"This is synthetic text, not a JPEG.\n", "UNSUPPORTED_FORMAT")
    reject("broken_header.png", PNG_SIGNATURE + b"broken header", "INVALID_IMAGE")
    reject("broken_header.jpg", b"\xff\xd8\xff\xe0\x00\x10short", "INVALID_IMAGE")
    corrupt = bytearray(good_png)
    # Flip the IDAT checksum, leaving a recognizable and correctly sized header.
    idat = good_png.index(b"IDAT")
    idat_length = struct.unpack(">I", good_png[idat - 4:idat])[0]
    corrupt[idat + 4 + idat_length] ^= 1
    reject("broken_crc.png", bytes(corrupt), "INVALID_IMAGE")
    reject("truncated.png", good_png[:-15], "INVALID_IMAGE")

    (FIXTURES / "pixel_limit.png").write_bytes(solid_png(4000, 4000))
    record("pixel_limit.png", {"validation": "accept", "format": "PNG", "size": [4000, 4000], "mode": "RGB", "frames": 1})
    # Deliberately keep the small IDAT: these are header-only quota probes,
    # not valid full rasters. The validator must reject before verify/load.
    for name, size in [("pixel_over.png", (4001, 4000)),
                       ("bomb_warning.png", (10000, 10000)), ("bomb_error.png", (20000, 20000))]:
        header = struct.pack(">IIBBBBB", *size, 8, 2, 0, 0, 0)
        reject(name, PNG_SIGNATURE + png_chunk(b"IHDR", header) + good_png[33:],
               "TOO_MANY_PIXELS", "header_only", size=list(size))

    manifest = {
        "schema_version": 1,
        "provenance": "Synthetic images generated locally by experiments/create_fixtures.py; no personal images or external downloads.",
        "corner_order": ["top_left", "top_right", "bottom_right", "bottom_left"],
        "corner_samples": [[12, 12], [83, 12], [83, 51], [12, 51]],
        "jpeg_rgb_tolerance": 3,
        "notes": [
            "size is the encoded raster size, before EXIF; normalized_* are expectations for MVP02.03, not current output.",
            "header_only probes intentionally have inconsistent pixel payloads; never load them.",
            "pixel_limit.png is a valid 16 MP solid raster compressed row by row without a large allocation.",
            "Byte-quota tests pad a small valid PNG in memory; no >15 MiB fixture is stored in Git.",
        ],
        "fixtures": entries,
    }
    (FIXTURES / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {len(entries)} fixtures, {sum(e['byte_count'] for e in entries)} bytes total, in {FIXTURES}")


if __name__ == "__main__":
    main()
