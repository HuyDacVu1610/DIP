"""Validate manual ground truth against exact normalized sources; never run a detector."""
import argparse
import csv
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

PROJECT_ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PROJECT_ROOT))
sys.path.insert(0,str(PROJECT_ROOT/'backend'))
from experiments.validate_dataset import _file_hash, _local_path, validate_manifest
from app.processing.geometry import GeometryValidationError, validate_quad


def validate_annotations(path:Path,manifest:Path,project_root:Path=PROJECT_ROOT,*,require_review:bool=True,split:str|None=None)->dict:
    if split not in (None,'development','test'):raise ValueError('Split không hợp lệ.')
    validate_manifest(manifest,project_root,check_files=split is None)
    with manifest.open(encoding='utf-8-sig',newline='') as f:
        all_rows={r['image_id']:r for r in csv.DictReader(f)}
    rows={key:row for key,row in all_rows.items() if split is None or row['split']==split}
    data=json.loads(path.read_text(encoding='utf-8'))
    if (not isinstance(data,dict) or type(data.get('schema_version')) is not int
            or data['schema_version']!=1 or data.get('coordinates')!='normalized_w_minus_1_h_minus_1'
            or not isinstance(data.get('records'),list)):
        raise ValueError('Schema/coordinate convention không hợp lệ.')
    seen=set();counts={'labeled':0,'unlabelable':0,'reviewed':0}
    for item in data['records']:
        if not isinstance(item,dict) or not isinstance(item.get('image_id'),str):
            raise ValueError('Mỗi nhãn phải là object có image_id.')
        image_id=item['image_id']
        if image_id in all_rows and image_id not in rows:continue
        if image_id not in rows or image_id in seen:
            raise ValueError('image_id không có trong manifest hoặc bị trùng: '+image_id)
        seen.add(image_id);row=rows[image_id]
        if not row['normalized_path'] or item.get('normalized_sha256')!=row['normalized_sha256']:
            raise ValueError(image_id+': nhãn không khớp nguồn PNG sau EXIF.')
        if split is not None:
            for prefix in ('source','normalized'):
                if _file_hash(_local_path(row[prefix+'_path'],project_root))!=row[prefix+'_sha256']:
                    raise ValueError(image_id+': hash nguồn không khớp tệp.')
        with Image.open(_local_path(row['normalized_path'],project_root)) as im:
            im.load();width,height=im.size
            if im.format!='PNG' or im.getexif().get(274,1)!=1:
                raise ValueError(image_id+': nguồn phải là PNG đã chuẩn hóa EXIF.')
        if (type(item.get('width')) is not int or type(item.get('height')) is not int
                or item['width']!=width or item['height']!=height or min(width,height)<2):
            raise ValueError(image_id+': dimensions không khớp nguồn.')
        if (type(item.get('reviewed')) is not bool or (require_review and not item['reviewed'])
                or not isinstance(item.get('labeler'),str) or not item['labeler'].strip()
                or not isinstance(item.get('notes'),str)):
            raise ValueError(image_id+': thiếu người gán nhãn/kiểm tra overlay.')
        status=item.get('status');reason=item.get('reason')
        if not isinstance(reason,str):raise ValueError(image_id+': reason phải là chuỗi.')
        if status=='labeled':
            if reason or item.get('corners') is None:raise ValueError(image_id+': nhãn bốn góc không hợp lệ.')
            try:validate_quad(item['corners'],width,height)
            except GeometryValidationError as e:raise ValueError(image_id+': '+str(e)) from e
        elif status=='unlabelable':
            if item.get('corners') is not None or not reason.strip():
                raise ValueError(image_id+': thiếu góc phải để corners=null và nêu lý do.')
        else:raise ValueError(image_id+': status phải là labeled hoặc unlabelable.')
        counts[status]+=1;counts['reviewed']+=item['reviewed']
    if seen!=set(rows):raise ValueError('Thiếu nhãn cho: '+', '.join(sorted(set(rows)-seen)))
    return {'images':len(rows),**counts,'source_files_checked':True,'review_required':require_review}


def write_overlays(path:Path,manifest:Path,output:Path,project_root:Path=PROJECT_ROOT)->None:
    validate_annotations(path,manifest,project_root,require_review=False)
    with manifest.open(encoding='utf-8-sig',newline='') as f:
        rows={r['image_id']:r for r in csv.DictReader(f)}
    output.mkdir(parents=True)  # New directory only: never replace prior review evidence.
    for item in json.loads(path.read_text(encoding='utf-8'))['records']:
        with Image.open(_local_path(rows[item['image_id']]['normalized_path'],project_root)) as im:
            canvas=cv2.cvtColor(np.array(im.convert('RGB')),cv2.COLOR_RGB2BGR)
        width,height=item['width'],item['height'];thickness=max(1,min(width,height)//400)
        if item['corners'] is not None:
            pixels=validate_quad(item['corners'],width,height)
            points=np.floor(np.array(pixels)+.5).astype(np.int32)
            cv2.polylines(canvas,[points],True,(30,220,30),thickness)
            for i,(x,y) in enumerate(points):
                cv2.circle(canvas,(int(x),int(y)),max(2,thickness*2),(0,0,255),-1)
                cv2.putText(canvas,str(i),(int(max(0,min(x+8,width-30))),int(max(25,min(y+25,height-3)))),
                            cv2.FONT_HERSHEY_SIMPLEX,.8,(0,0,255),max(1,thickness))
        cv2.putText(canvas,item['image_id']+' '+item['status'],(8,30),
                    cv2.FONT_HERSHEY_SIMPLEX,.7,(0,0,255),max(1,thickness))
        ok,payload=cv2.imencode('.png',canvas)
        if not ok:raise ValueError('Không encode được overlay.')
        (output/(item['image_id']+'.png')).write_bytes(payload.tobytes())
    (output/'annotations-snapshot.json').write_bytes(path.read_bytes())


def main()->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('annotations',nargs='?',type=Path,default=PROJECT_ROOT/'experiments/annotations.json')
    parser.add_argument('--manifest',type=Path,default=PROJECT_ROOT/'experiments/dataset_manifest.csv')
    parser.add_argument('--allow-unreviewed',action='store_true',help='Chỉ chuẩn bị overlay, chưa nghiệm thu nhãn.')
    parser.add_argument('--output-dir',type=Path,help='Thư mục overlay mới, không ghi đè.')
    args=parser.parse_args()
    try:
        report=validate_annotations(args.annotations,args.manifest,require_review=not args.allow_unreviewed)
        if args.output_dir:write_overlays(args.annotations,args.manifest,args.output_dir)
        print(json.dumps(report,ensure_ascii=False));return 0
    except (ValueError,OSError,csv.Error) as error:
        print('Lỗi annotations: '+str(error),file=sys.stderr);return 1


if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8');sys.stderr.reconfigure(encoding='utf-8')
    raise SystemExit(main())
