"""Compare full Color/Gray/BW renders from one local manual warp, offline."""
import argparse
import json
import sys
from hashlib import sha256
from io import BytesIO
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / 'backend'))

from app.processing.config import ConfigValidationError, get_preset, parse_config
from app.processing.enhancement import EnhancementValidationError, enhance_document
from app.processing.geometry import GeometryValidationError, compute_homography, validate_quad, warp_document
from app.processing.image_sizes import resize_to_max_edge
from app.processing.normalize import ImageValidationError, normalize_image
from app.settings import MAX_UPLOAD_BYTES


def _png(image: np.ndarray) -> bytes:
    # Fresh Pillow image: RGB for BGR input, L for gray/BW, no source EXIF.
    rgb_or_gray = image[:, :, ::-1] if image.ndim == 3 else image
    stream = BytesIO()
    Image.fromarray(rgb_or_gray).save(stream, format='PNG')
    return stream.getvalue()


def _comparison(renders: dict) -> np.ndarray:
    panels = []
    for result in renders.values():
        image = result.image
        bgr = image if image.ndim == 3 else cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        panels.append(resize_to_max_edge(bgr, 800))
    cell_h = max(panel.shape[0] for panel in panels) + 40
    cell_w = max(panel.shape[1] for panel in panels)
    canvas = np.full((cell_h * 2, cell_w * 2, 3), 255, dtype=np.uint8)
    for i, ((name, _), panel) in enumerate(zip(renders.items(), panels, strict=True)):
        x, y = (i % 2) * cell_w, (i // 2) * cell_h
        canvas[y + 40:y + 40 + panel.shape[0], x:x + panel.shape[1]] = panel
        cv2.putText(canvas, name, (x + 6, y + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
    return canvas


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='So Color/Gray/BW trên cùng warp; không detector hoặc export tài liệu.')
    parser.add_argument('input', type=Path, help='JPEG/PNG gốc, chuẩn hóa EXIF một lần.')
    parser.add_argument('--output-dir', type=Path, required=True, help='Thư mục mới, không ghi đè.')
    parser.add_argument('--corners', help='JSON normalized theo nguồn sau EXIF; mặc định toàn ảnh, giữ thứ tự tay.')
    parser.add_argument('--rotation', type=int, choices=[0, 90, 180, 270], default=0, help='Độ theo chiều kim đồng hồ.')
    parser.add_argument('--denoise', choices=['none', 'median', 'gaussian'], help='Ghi đè lọc cả bốn nhánh; mặc định theo preset.')
    parser.add_argument('--no-gray-clahe', action='store_true', help='Tắt CLAHE cho nhánh Gray để so sánh.')
    args = parser.parse_args(argv)
    try:
        corners = json.loads(args.corners) if args.corners is not None else [[0,0],[1,0],[1,1],[0,1]]
    except json.JSONDecodeError:
        parser.error('--corners phải là JSON hợp lệ.')
    try:
        output = args.output_dir.resolve()
        if output.exists():
            raise FileExistsError(output)
        with args.input.open('rb') as stream:
            original = stream.read(MAX_UPLOAD_BYTES + 1)
        source = normalize_image(original)
        height, width = source.shape[:2]
        points = validate_quad(corners, width, height)
        matrix, warp_size = compute_homography(corners, width, height)
        warped = warp_document(source, corners)
        overlay = source.copy()
        drawn = np.floor(np.array(points) + 0.5).astype(np.int32)
        thickness = max(1, min(width, height) // 300)
        cv2.polylines(overlay, [drawn], True, (40, 210, 40), thickness)
        for i, (x, y) in enumerate(drawn):
            cv2.putText(overlay, str(i), (max(0, min(int(x) + 6, width - 16)), max(14, min(int(y) + 18, height - 2))),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), thickness)
        renders = {}
        info = {'input': {'sha256': sha256(original).hexdigest(), 'byte_count': len(original)},
                'corners_selection': 'manual' if args.corners is not None else 'full_image_default',
                'corners_normalized': corners, 'corners_source_px': points,
                'homography_source_to_warp': matrix.tolist(), 'aspect_policy': 'estimated',
                'comparison_from': 'full renders resized to max_edge=800 without upscaling',
                'opencv_version': cv2.__version__, 'artifacts': {}, 'renders': {}}
        for name, mode in [('color', 'color'), ('gray', 'gray'), ('bw_adaptive', 'bw'), ('bw_otsu', 'bw')]:
            raw = get_preset(mode).model_dump(mode='json')
            raw.update(corners=corners, rotation=args.rotation)  # still a draft experiment, never auto-confirm
            if args.denoise is not None:
                raw['denoise']['method'] = args.denoise
            if mode == 'gray' and args.no_gray_clahe:
                raw['contrast']['method'] = 'none'
            if name == 'bw_otsu':
                raw['threshold']['method'] = 'otsu'
            config = parse_config(raw, source_size=(width, height), warp_size=warp_size)
            result = enhance_document(warped, config, source_size=(width, height))
            renders[name] = result
            info['renders'][name] = {'effective_config': result.effective_config.model_dump(mode='json'),
                                     'inactive_fields': result.effective_config.inactive_fields,
                                     'otsu_threshold': result.otsu_threshold}
        images = {'source': source, 'overlay': overlay, 'warp': warped}
        images.update({name: result.image for name, result in renders.items()})
        images['comparison'] = _comparison(renders)
        payloads = []
        for name, image in images.items():
            payload = _png(image)
            image_h, image_w = image.shape[:2]
            info['artifacts'][name] = {'file': name + '.png', 'width': image_w, 'height': image_h,
                                       'png_mode': 'RGB' if image.ndim == 3 else 'L',
                                       'sha256': sha256(payload).hexdigest(), 'byte_count': len(payload)}
            payloads.append((name + '.png', payload))
        # All renders must succeed before writing; metadata last is the completion marker.
        payloads.append(('metadata.json', (json.dumps(info, ensure_ascii=False, indent=2) + '\n').encode('utf-8')))
        output.mkdir(parents=True)
        for name, payload in payloads:
            with (output / name).open('xb') as stream:
                stream.write(payload)
    except (ConfigValidationError, EnhancementValidationError, ImageValidationError, GeometryValidationError) as error:
        print(f'Lỗi [{error.code}]: {error}', file=sys.stderr)
        return 1
    except FileExistsError:
        print('Lỗi [OUTPUT_EXISTS]: Hãy chọn thư mục đầu ra mới.', file=sys.stderr)
        return 1
    except OSError as error:
        print(f'Lỗi [IO_ERROR]: {error}', file=sys.stderr)
        return 1
    print(f'Đã tạo bốn bản full render, source/overlay/warp, comparison và metadata tại: {output}')
    return 0


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    raise SystemExit(main())
