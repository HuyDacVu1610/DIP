"""Compare actual baseline/revised detectors on development; no auto warp or GT."""
import argparse
import csv
import json
import sys
from hashlib import sha256
from pathlib import Path
from uuid import uuid4

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT/'backend'))
from app.processing.detection import DetectionValidationError, detect_document
from app.processing.normalize import encode_normalized_png, normalize_image
from app.settings import MAX_UPLOAD_BYTES
from validate_dataset import validate_manifest
from detection_artifacts import write_detection_artifacts, save_png, write_json


def _run(argv=None):
    parser = argparse.ArgumentParser(description='Chạy detector baseline/revised trên development, không xuất accuracy.')
    parser.add_argument('--project-root',type=Path,default=PROJECT_ROOT)
    parser.add_argument('--manifest',type=Path,default=PROJECT_ROOT/'experiments/dataset_manifest.csv')
    parser.add_argument('--input',type=Path,action='append',default=[],help='Ảnh bổ sung chưa gán document_id/split; có thể lặp cờ.')
    parser.add_argument('--output-dir',type=Path,required=True,help='Thư mục mới; không ghi đè.')
    args = parser.parse_args(argv)
    try:
        output = args.output_dir.resolve()
        if output.exists():
            raise DetectionValidationError('OUTPUT_EXISTS','Chọn thư mục kết quả mới.')
        validate_manifest(args.manifest,args.project_root,check_files=False)
        with args.manifest.open(encoding='utf-8-sig',newline='') as file:
            cases = [row for row in csv.DictReader(file) if row['split']=='development']
        for index, path in enumerate(args.input,1):
            cases.append({'image_id':f'supplemental_{index:03}','document_id':None,
                'split':'supplemental_unassigned','source_path':str(path.resolve())})
        if not cases:
            raise DetectionValidationError('INPUTS_REQUIRED','Cần ảnh development hoặc --input.')
        if len({c['image_id'] for c in cases})!=len(cases):
            raise DetectionValidationError('DUPLICATE_ID','ID ảnh bổ sung trùng manifest.')
        output.mkdir(parents=True)
    except (ValueError,OSError,csv.Error) as error:
        print(f'Lỗi [{getattr(error,"code","DATASET_INVALID")}]: {error}',file=sys.stderr)
        return 1
    run_id, records, rows = str(uuid4()), [], []
    for case in cases:
        folder = output/case['image_id']
        folder.mkdir()
        identity = {key:case[key] for key in ('image_id','document_id','split')}
        try:
            path = args.project_root/case['source_path']
            with path.open('rb') as stream:
                raw = stream.read(MAX_UPLOAD_BYTES+1)
            raw_hash = sha256(raw).hexdigest()
            if case.get('source_sha256') and raw_hash!=case['source_sha256']:
                raise DetectionValidationError('SOURCE_HASH_MISMATCH','Nguồn khác manifest.')
            source = normalize_image(raw)
            normalized = encode_normalized_png(source)
            if case.get('normalized_sha256') and normalized.sha256!=case['normalized_sha256']:
                raise DetectionValidationError('NORMALIZED_HASH_MISMATCH','PNG chuẩn hóa khác manifest.')
            source.setflags(write=False)
            before = sha256(source.tobytes()).hexdigest()
            with (folder/'source.png').open('xb') as file:
                file.write(normalized.png_bytes)
            source_info = {'width':normalized.width,'height':normalized.height,
                'raw_sha256':raw_hash,'normalized_png_sha256':normalized.sha256}
            panels = []
            for preset in ('baseline','revised'):
                detected = detect_document(source,debug=True,preset=preset)
                row,panel = write_detection_artifacts(detected,source_info,folder/preset,run_id,entry_point='detect_batch')
                rows.append(identity|row)
                panels.append(panel)
            if sha256(source.tobytes()).hexdigest()!=before:
                raise DetectionValidationError('SOURCE_CHANGED','Detector làm thay đổi nguồn.')
            comparison = np.concatenate(panels,axis=1)  # same source and analysis dimensions
            comparison_info = save_png(folder/'comparison.png',comparison)
            record = identity|{'input':str(path),'source':source_info,'source_unchanged':True,
                'profiles':{'baseline':'baseline/metadata.json','revised':'revised/metadata.json'},
                'comparison':comparison_info}
            write_json(folder/'metadata.json',record)
        except (ValueError,OSError) as error:
            detail = {'code':getattr(error,'code','IO_ERROR'),'message':str(error)}
            write_json(folder/'error.json',detail)
            record = identity|{'error':detail}
        records.append(record)
    fields = ['image_id','document_id','split','preset','status','heuristic_score','warnings','method',
        'before_nms','after_nms','total_ms','area_ratio','edge_support','fit_area_ratio','border_penalty','error_code']
    with (output/'results.csv').open('x',encoding='utf-8',newline='') as stream:
        writer = csv.DictWriter(stream,fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
        for record in records:
            if 'error' in record:
                writer.writerow({key:record[key] for key in ('image_id','document_id','split')}|
                    {'status':'error','error_code':record['error']['code']})
    errors = sum('error' in record for record in records)
    summary = {'entry_point':'detect_batch','run_id':run_id,'images':len(cases),'profile_runs':len(rows),
        'errors':errors,'manifest_sha256':sha256(args.manifest.read_bytes()).hexdigest(),
        'purpose':'Development observations only; scores/statuses are not accuracy or ground truth.', 'cases':records}
    write_json(output/'summary.json',summary)  # completion marker, including explicit case errors
    print(json.dumps({'output':str(output),'images':len(cases),'profile_runs':len(rows),'errors':errors}))
    return 1 if errors else 0


def main(argv=None):
    try:
        return _run(argv)
    except OSError as error:
        print(f'Lỗi [IO_ERROR]: {error}',file=sys.stderr)
        return 1


if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    raise SystemExit(main())
