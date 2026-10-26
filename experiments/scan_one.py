"""One offline source -> detect/manual -> warp -> mode -> rotation -> PNG run."""
import argparse
import json
import platform
import sys
from dataclasses import asdict
from hashlib import sha256
from pathlib import Path
from uuid import uuid4

import cv2
import numpy as np
import PIL

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PROJECT_ROOT/'backend'))
from app.processing.config import ConfigValidationError, parse_config
from app.processing.geometry import normalized_to_pixel
from app.processing.normalize import encode_normalized_png, normalize_image
from app.processing.render import RenderValidationError, encode_render_images, encode_stage_png, render_document
from app.settings import MAX_UPLOAD_BYTES
from detection_artifacts import write_detection_artifacts, write_json


def _record(folder, relative, encoded):
    path = folder/relative
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb') as stream:
        stream.write(encoded.png_bytes)
    return {'file':relative,'width':encoded.width,'height':encoded.height,
        'png_mode':getattr(encoded,'png_mode','RGB'),'sha256':encoded.sha256,
        'byte_count':len(encoded.png_bytes)}


def _source_overlay(source, corners):
    height,width = source.shape[:2]
    points = np.array([normalized_to_pixel(p,width,height) for p in corners])
    drawn = np.rint(points).astype(np.int32)
    image = source.copy()
    thickness = max(1,min(width,height)//300)
    cv2.polylines(image,[drawn],True,(0,0,255),thickness)
    for i,(x,y) in enumerate(drawn):
        cv2.putText(image,str(i),(max(0,min(int(x)+5,width-16)),max(14,min(int(y)+18,height-2))),
            cv2.FONT_HERSHEY_SIMPLEX,.6,(0,0,255),thickness)
    return image


def _run(argv=None):
    parser = argparse.ArgumentParser(description='Quét một ảnh offline; auto/manual đều không tự confirmed.')
    parser.add_argument('input',type=Path,help='JPEG/PNG gốc, chuẩn hóa EXIF một lần.')
    parser.add_argument('--output-dir',type=Path,required=True,help='Thư mục mới, không ghi đè.')
    preset = parser.add_mutually_exclusive_group()
    preset.add_argument('--mode',choices=('color','gray','bw'),default=None,help='Preset khởi đầu; mặc định color.')
    preset.add_argument('--config',type=Path,help='JSON PageConfig; có thể dùng config.json của lần chạy trước.')
    parser.add_argument('--corners',help='JSON normalized sau EXIF, giữ thứ tự tay; ghi đè corners và chuyển draft.')
    args = parser.parse_args(argv)
    output = args.output_dir.resolve()
    if output.exists():
        raise RenderValidationError('OUTPUT_EXISTS','Chọn thư mục kết quả mới.')
    if args.config is None:
        config = {'mode':args.mode or 'color'}
    else:
        with args.config.open(encoding='utf-8-sig') as stream:
            config = json.load(stream)
        if not isinstance(config,dict):
            raise ConfigValidationError('Config JSON phải là object.')
    if args.corners is not None:
        config['corners'] = json.loads(args.corners)
        config['confirmed'] = False
    with args.input.open('rb') as stream:
        original = stream.read(MAX_UPLOAD_BYTES+1)
    source = normalize_image(original)
    source.setflags(write=False)
    before = sha256(source.tobytes(order='C')).hexdigest()
    height,width = source.shape[:2]
    requested = parse_config(config,source_size=(width,height))
    result = render_document(source,requested,debug=True)
    normalized = encode_normalized_png(source)
    encoded = encode_render_images(result.enhancement.image) if result.enhancement else None
    if sha256(source.tobytes(order='C')).hexdigest()!=before:
        raise RenderValidationError('SOURCE_CHANGED','Pipeline làm thay đổi nguồn.')
    info = {'entry_point':'scan_one','run_id':str(uuid4()),'pipeline_version':'scan-v1',
        'purpose':'Offline render; no UI confirmation/revision or accuracy claim.',
        'input':{'path':str(args.input.resolve()),'sha256':sha256(original).hexdigest(),'byte_count':len(original)},
        'source':{'width':width,'height':height,'raw_sha256':sha256(original).hexdigest(),
            'normalized_png_sha256':normalized.sha256,'bgr_sha256':before},
        'status':result.status,'corners_origin':result.corners_origin,
        'detection_status':result.detection.status if result.detection else 'skipped_manual',
        'warnings':result.detection.warnings if result.detection else (),
        'requested_config':requested.model_dump(mode='json'),
        'effective_config':result.effective_config.model_dump(mode='json'),
        'inactive_fields':result.effective_config.inactive_fields,
        'otsu_threshold':result.enhancement.otsu_threshold if result.enhancement else None,
        'histogram':None,
        'homography_source_to_warp':result.homography.tolist() if result.homography is not None else None,
        'timings_ms':asdict(result.timings_ms),'timings_scope':'Core validation/detect/warp/enhance; excludes normalize/encode/I/O.',
        'environment':{'python':platform.python_version(),'opencv':cv2.__version__,
            'numpy':np.__version__,'pillow':PIL.__version__},
        'units':{'corners':'normalized source after EXIF; W-1/H-1','warp':'full source pixels; INTER_LINEAR/BORDER_REPLICATE',
            'rotation':'clockwise degrees','preview':'INTER_AREA from final full render, max1000, no upscale'},
        'source_unchanged':True,'artifacts':{},'detection_metadata_file':None,
        'config_file':'config.json'}
    output.mkdir(parents=True)
    info['artifacts']['source'] = _record(output,'source.png',normalized)
    if result.detection is not None:
        if result.detection.debug is not None:
            write_detection_artifacts(result.detection,info['source'],output/'detection',info['run_id'],entry_point='scan_one')
            info['detection_metadata_file'] = 'detection/metadata.json'
        else:
            info['detection_without_stages'] = {'status':result.detection.status,
                'warnings':result.detection.warnings,'corners':result.detection.corners}
    if result.enhancement is not None:
        info['artifacts']['source_overlay'] = _record(output,'source_overlay.png',
            encode_normalized_png(_source_overlay(source,result.effective_config.corners)))
        stages = result.enhancement.stages
        images = {'warp':result.warped_bgr,'filtered_bgr':stages.filtered_bgr,'before_rotation':stages.before_rotation}
        if stages.prepared_gray is not None:
            images['prepared_gray'] = stages.prepared_gray
        for name,image in images.items():
            info['artifacts'][name] = _record(output,f'render/{name}.png',encode_stage_png(image))
        info['artifacts']['full'] = _record(output,'render/full.png',encoded.full)
        info['artifacts']['preview'] = _record(output,'render/preview.png',encoded.preview)
        if result.enhancement.histogram is not None:
            gray = info['artifacts']['prepared_gray']
            info['histogram'] = {'counts':result.enhancement.histogram,
                'pixel_count':gray['width']*gray['height'],'width':gray['width'],'height':gray['height'],
                'source_artifact':'prepared_gray','source_png_sha256':gray['sha256'],
                'threshold_method':result.effective_config.threshold.method,
                'threshold_scope':'global' if result.effective_config.threshold.method=='otsu' else 'local',
                'otsu_threshold':result.enhancement.otsu_threshold}
    write_json(output/'config.json',info['effective_config'])
    info['config_sha256'] = sha256((output/'config.json').read_bytes()).hexdigest()
    write_json(output/'metadata.json',info)  # completion marker; inspect status, not merely its presence
    print(json.dumps({'output':str(output),'status':result.status,
        'confirmed':result.effective_config.confirmed,'warnings':info['warnings']}))
    return 0 if result.status=='rendered' else 2


def main(argv=None):
    try:
        return _run(argv)
    except json.JSONDecodeError as error:
        print(f'Lỗi [INVALID_CONFIG]: JSON không hợp lệ: {error}',file=sys.stderr)
    except (ValueError,OSError) as error:
        print(f'Lỗi [{getattr(error,"code","IO_ERROR")}]: {error}',file=sys.stderr)
    except cv2.error as error:
        print(f'Lỗi [SCAN_FAILED]: {error}',file=sys.stderr)
    return 1


if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    raise SystemExit(main())
