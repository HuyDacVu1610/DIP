"""Render a local source, numbered quad overlay and warp; no detector or UI."""

import argparse
import json
import sys
from hashlib import sha256
from pathlib import Path

import cv2
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / 'backend'))

from app.processing.geometry import GeometryValidationError, compute_homography, validate_quad, warp_document
from app.processing.normalize import ImageValidationError, encode_normalized_png, normalize_image
from app.settings import MAX_UPLOAD_BYTES


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Minh họa quad và homography từ ảnh nguồn; không tự phát hiện góc.')
    parser.add_argument('input', type=Path, help='JPEG/PNG gốc, áp EXIF khi chuẩn hóa.')
    parser.add_argument('--output-dir', type=Path, required=True, help='Thư mục mới, không ghi đè.')
    parser.add_argument('--corners', default='[[0,0],[1,0],[1,1],[0,1]]',
                        help='JSON bốn [u,v] trên source sau EXIF, theo chiều kim đồng hồ; mặc định toàn ảnh.')
    args = parser.parse_args(argv)
    try:
        corners = json.loads(args.corners)
    except json.JSONDecodeError:
        parser.error('--corners phải là JSON hợp lệ.')
    try:
        with args.input.open('rb') as stream:
            original = stream.read(MAX_UPLOAD_BYTES + 1)
        source = normalize_image(original)
        height, width = source.shape[:2]
        pixels = validate_quad(corners, width, height)
        matrix, size = compute_homography(corners, width, height)
        warped = warp_document(source, corners)
        overlay = source.copy()
        # Only the visualization rounds points; metadata/warp retain subpixels.
        drawn = np.floor(np.array(pixels) + 0.5).astype(np.int32)
        thickness = max(1, min(width,height)//300)
        cv2.polylines(overlay, [drawn], True, (40,210,40), thickness)
        colors = [(0,0,255),(0,210,0),(255,0,0),(0,220,220)]
        for i, (point,color) in enumerate(zip(drawn, colors, strict=True)):
            x,y = map(int,point)
            cv2.circle(overlay,(x,y),max(3,thickness*2),color,-1)
            cv2.putText(overlay,str(i),(max(0,min(x+6,width-16)),max(14,min(y+18,height-2))),
                        cv2.FONT_HERSHEY_SIMPLEX,0.5,color,max(1,thickness))
        artifacts=[]
        info={'input':{'sha256':sha256(original).hexdigest(),'byte_count':len(original)},
              'corners_normalized':corners,'corners_source_px':pixels,
              'corners_warp_px':[(0,0),(size[0]-1,0),(size[0]-1,size[1]-1),(0,size[1]-1)],
              'homography_source_to_warp':matrix.tolist(),
              'aspect_policy':'estimated','interpolation':'INTER_LINEAR','border_mode':'BORDER_REPLICATE',
              'opencv_version':cv2.__version__}
        for name,image in [('source',source),('overlay',overlay),('warp',warped)]:
            encoded=encode_normalized_png(image)
            info[name]={'file':name+'.png','width':encoded.width,'height':encoded.height,
                        'sha256':encoded.sha256,'byte_count':len(encoded.png_bytes)}
            artifacts.append((name+'.png',encoded.png_bytes))
        # Metadata last: its presence indicates all three images were written.
        artifacts.append(('metadata.json',(json.dumps(info,ensure_ascii=False,indent=2)+'\n').encode('utf-8')))
        output=args.output_dir.resolve()
        output.mkdir(parents=True)
        for name,payload in artifacts:
            with (output/name).open('xb') as stream:
                stream.write(payload)
    except (ImageValidationError,GeometryValidationError) as error:
        print(f'Lỗi [{error.code}]: {error}',file=sys.stderr)
        return 1
    except FileExistsError:
        print('Lỗi [OUTPUT_EXISTS]: Hãy chọn thư mục đầu ra mới.',file=sys.stderr)
        return 1
    except OSError as error:
        print(f'Lỗi [IO_ERROR]: {error}',file=sys.stderr)
        return 1
    print(f'Đã tạo source.png, overlay.png, warp.png và metadata.json tại: {output}')
    return 0


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    raise SystemExit(main())
