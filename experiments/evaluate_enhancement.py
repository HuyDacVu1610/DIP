"""Development-only Otsu/Adaptive comparison on one ground-truth warp per image."""
import argparse
import csv
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import sys

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'backend')]
from app.processing.config import get_preset, parse_config
from app.processing.enhancement import enhance_document
from app.processing.geometry import compute_homography, warp_document
from app.processing.image_sizes import resize_to_max_edge
from experiments.detection_artifacts import save_png, write_json
from experiments.validate_annotations import validate_annotations

METHODS = ('otsu', 'adaptive_gaussian')


def compare_thresholds(source, corners):
    """Warp once; change only threshold.method between two production renders."""
    height, width = source.shape[:2]
    matrix, size = compute_homography(corners, width, height)
    warped = warp_document(source, corners)
    warped.setflags(write=False)
    renders = {}
    for method in METHODS:
        raw = get_preset('bw').model_dump(mode='json')
        raw.update(corners=corners, confirmed=False, rotation=0)
        raw['threshold']['method'] = method
        config = parse_config(raw, source_size=(width, height), warp_size=size)
        renders[method] = enhance_document(warped, config, source_size=(width, height), debug=True)
    if not np.array_equal(renders['otsu'].stages.prepared_gray, renders['adaptive_gaussian'].stages.prepared_gray):
        raise ValueError('Hai nhánh phải có cùng prepared_gray.')
    return warped, matrix, renders


def write_comparison(folder, source_info, warped, matrix, renders):
    folder.mkdir()
    images = {'warp':warped, 'filtered':renders['otsu'].stages.filtered_bgr,
              'prepared_gray':renders['otsu'].stages.prepared_gray,
              **{key:result.image for key,result in renders.items()}}
    names = ['warp', *METHODS]
    panels = [resize_to_max_edge(images[name], 720) for name in names]
    panels = [im if im.ndim == 3 else cv2.cvtColor(im, cv2.COLOR_GRAY2BGR) for im in panels]
    for name, panel in zip(names, panels):
        cv2.putText(panel, name, (8,24), cv2.FONT_HERSHEY_SIMPLEX, .6, (0,0,255), 1)
    images['comparison'] = np.concatenate(panels, axis=1)
    h,w = warped.shape[:2]
    cw,ch = min(640,w),min(400,h)
    x,y = (w-cw)//2,(h-ch)//2
    # Same center crop, native pixels; inspect full outputs as well.
    crops = [images[name][y:y+ch,x:x+cw].copy() for name in names]
    crops = [im if im.ndim == 3 else cv2.cvtColor(im,cv2.COLOR_GRAY2BGR) for im in crops]
    images['detail_100pct'] = np.concatenate(crops,axis=1)
    metadata = {'experiment_version':'enhancement-comparison-v1','source':source_info,
        'corners_selection':'manual_ground_truth','confirmed_by_user':False,
        'homography_source_to_warp':matrix.tolist(),'warp_size':[w,h],
        'same_prepared_gray':True,'changed_field':'threshold.method',
        'detail_crop_xywh':[x,y,cw,ch], 'detail_order':names,
        'renders':{name:{'effective_config':r.effective_config.model_dump(mode='json'),
            'inactive_fields':r.effective_config.inactive_fields,'otsu_threshold':r.otsu_threshold,
            'threshold_scope':'global' if name=='otsu' else 'local',
            'black_pixel_ratio':float(np.count_nonzero(r.image==0)/r.image.size),
            'histogram':r.histogram} for name,r in renders.items()},
        'artifacts':{name:save_png(folder/(name+'.png'),im) for name,im in images.items()}}
    write_json(folder/'metadata.json',metadata)
    return metadata


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest',type=Path,default=ROOT/'experiments/dataset_manifest.csv')
    parser.add_argument('--annotations',type=Path,default=ROOT/'experiments/annotations.json')
    parser.add_argument('--project-root',type=Path,default=ROOT)
    parser.add_argument('--output-dir',type=Path,required=True)
    args = parser.parse_args(argv)
    try:
        validate_annotations(args.annotations,args.manifest,args.project_root,split='development')
        with args.manifest.open(encoding='utf-8-sig',newline='') as f:
            cases = [r for r in csv.DictReader(f) if r['split']=='development']
        labels = {r['image_id']:r for r in json.loads(args.annotations.read_text(encoding='utf-8'))['records']}
        if not cases: raise ValueError('Không có ảnh development.')
        args.output_dir.mkdir(parents=True)
        rows=[]; pairs=0; errors=0
        for case in cases:
            label=labels[case['image_id']]
            identity={k:case[k] for k in ('image_id','document_id','split','condition')}
            if label['status']=='unlabelable':
                rows.append({**identity,'method':'','status':'unlabelable','error':label['reason']})
                continue
            payload=(args.project_root/case['normalized_path']).read_bytes()
            if sha256(payload).hexdigest()!=case['normalized_sha256'] or label['normalized_sha256']!=case['normalized_sha256']:
                raise ValueError('Nguồn/nhãn thay đổi sau kiểm tra hash.')
            with Image.open(BytesIO(payload)) as im:
                if im.size!=(label['width'],label['height']): raise ValueError('Dimensions nguồn/nhãn không khớp.')
                source=cv2.cvtColor(np.array(im.convert('RGB')),cv2.COLOR_RGB2BGR)
            source.setflags(write=False); before=sha256(source.tobytes()).hexdigest()
            try:
                warped,matrix,renders=compare_thresholds(source,label['corners'])
                meta=write_comparison(args.output_dir/case['image_id'],
                    {**identity,'normalized_sha256':case['normalized_sha256'],
                     'width':label['width'],'height':label['height'],'corners':label['corners']},warped,matrix,renders)
                (args.output_dir/case['image_id']/'source.png').write_bytes(payload)
                for method,render in meta['renders'].items():
                    rows.append({**identity,'method':method,'status':'rendered','error':'',
                        'warp_width':warped.shape[1],'warp_height':warped.shape[0],
                        'otsu_threshold':render['otsu_threshold'],'threshold_scope':render['threshold_scope'],
                        'black_pixel_ratio':render['black_pixel_ratio'],
                        'prepared_gray_sha256':meta['artifacts']['prepared_gray']['sha256'],
                        'output_sha256':meta['artifacts'][method]['sha256']})
                pairs+=1
            except (ValueError,cv2.error) as error:
                errors+=1
                rows.append({**identity,'method':'','status':'error','error':str(error)})
                write_json(args.output_dir/(case['image_id']+'-error.json'),rows[-1])
            if before!=sha256(source.tobytes()).hexdigest(): raise ValueError('Nguồn bị thay đổi.')
        fields=['image_id','document_id','split','condition','method','status','error','warp_width','warp_height',
                'otsu_threshold','threshold_scope','black_pixel_ratio','prepared_gray_sha256','output_sha256']
        with (args.output_dir/'results.csv').open('x',encoding='utf-8',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
        write_json(args.output_dir/'summary.json',{'experiment_version':'enhancement-comparison-v1',
            'split':'development','images':len(cases),'pairs':pairs,
            'unlabelable':sum(r['status']=='unlabelable' for r in rows),'errors':errors,
            'test_images_processed':0,'methods':METHODS,'preset_bw':get_preset('bw').model_dump(mode='json'),
            'input_sha256':{p.name:sha256(p.read_bytes()).hexdigest() for p in (args.manifest,args.annotations)},
            'code_sha256':{name:sha256((ROOT/name).read_bytes()).hexdigest() for name in
                ['experiments/evaluate_enhancement.py','backend/app/processing/enhancement.py',
                 'backend/app/processing/config.py','backend/app/processing/geometry.py']},
            'limits':'One document; no real highlight case; black ratio is descriptive, not character accuracy.'})
        print(json.dumps({'images':len(cases),'pairs':pairs,'errors':errors}))
        return 1 if errors else 0
    except (ValueError,OSError,csv.Error) as error:
        print('Lỗi evaluate_enhancement: '+str(error),file=sys.stderr);return 1


if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8');sys.stderr.reconfigure(encoding='utf-8')
    raise SystemExit(main())
