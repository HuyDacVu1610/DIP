"""Controlled development-only detector ablation; never evaluate the test split here."""
import argparse
import csv
import json
import re
import sys
from dataclasses import asdict
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from time import perf_counter_ns

import cv2
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'backend'))
from app.processing.detection import (DETECTION_ALGORITHM_VERSION,RegionTrial,collect_candidates,
    describe_candidate,prepare_analysis,select_proposal)
from app.processing.geometry import normalized_to_pixel
from app.processing.image_sizes import resize_to_max_edge
from experiments.detection_artifacts import save_png,write_json
from experiments.metrics import aggregate_metrics,evaluate_quad
from experiments.validate_annotations import validate_annotations

CONFIG=ROOT/'experiments/configs/detection_trials.json'


def load_profiles(path=CONFIG):
    data=json.loads(Path(path).read_text(encoding='utf-8'))
    expected=[('scoring','scoring',5,True),('largest_contour','largest_contour',5,True),
              ('no_gaussian','scoring',0,True),('no_closing','scoring',5,False)]
    if (not isinstance(data,dict) or type(data.get('schema_version')) is not int
            or data['schema_version']!=1 or data.get('preset')!='revised'
            or data.get('reference')!='scoring' or data.get('experiment_version')!='detection-ablation-v1'
            or not isinstance(data.get('profiles'),list) or len(data['profiles'])!=4):
        raise ValueError('Cần bốn cấu hình đối chứng detection-ablation-v1/revised.')
    for profile,values in zip(data['profiles'],expected):
        if not isinstance(profile,dict) or set(profile)!=set(('id','selection','gaussian_kernel','closing')):
            raise ValueError('Trường cấu hình thí nghiệm không hợp lệ.')
        if tuple(profile[k] for k in ('id','selection','gaussian_kernel','closing'))!=values:
            raise ValueError('Mỗi đối chứng chỉ đổi đúng một yếu tố đã định.')
        if type(profile['gaussian_kernel']) is not int or type(profile['closing']) is not bool:
            raise ValueError('Kiểu cấu hình thí nghiệm không hợp lệ.')
    return data['profiles']


def choose_proposal(descriptions,selection):
    if selection=='scoring':return select_proposal(descriptions)
    if selection!='largest_contour':raise ValueError('Selection không hợp lệ.')
    # Same valid pool and score/status gates; only the choice before NMS changes.
    largest=max(descriptions,key=lambda d:cv2.contourArea(np.asarray(d.candidate.contour_px,np.float32)),default=None)
    return select_proposal((largest,) if largest else ())


def run_profile(source,profile):
    if (not isinstance(profile.get('id'),str) or not re.fullmatch('[a-z][a-z0-9_]*',profile['id'])
            or profile.get('selection') not in ('scoring','largest_contour')):
        raise ValueError('ID/selection không hợp lệ.')
    start=perf_counter_ns()
    analysis=prepare_analysis(source,gaussian_kernel=profile['gaussian_kernel'])
    preprocessed=perf_counter_ns()
    runs=collect_candidates(analysis,preset='revised',closing=profile['closing'])
    collected=perf_counter_ns()
    descriptions=tuple(describe_candidate(c,run.trial) for run in runs for c in run.batch.candidates)
    described=perf_counter_ns()
    result=choose_proposal(descriptions,profile['selection'])
    finished=perf_counter_ns()
    timings={key:(b-a)/1e6 for key,a,b in [('preprocess',start,preprocessed),
        ('candidates',preprocessed,collected),('describe',collected,described),
        ('select',described,finished),('total',start,finished)]}
    return result,analysis,runs,descriptions,timings


def write_profile(folder,source_info,profile,output,truth):
    result,analysis,runs,descriptions,timings=output
    folder.mkdir()
    images={'analysis':analysis.bgr,'gray':analysis.gray,'preprocessed':analysis.blurred}
    overlay=analysis.bgr.copy()
    if truth is not None:
        points=np.array([normalized_to_pixel(p,*analysis.analysis_size) for p in truth])
        cv2.polylines(overlay,[np.rint(points).astype(np.int32)],True,(0,210,0),2)
    if result.selected:
        candidate=result.selected.candidate
        cv2.polylines(overlay,[np.rint(candidate.contour_px).astype(np.int32)],True,(255,160,0),1)
        points=np.array([normalized_to_pixel(p,*analysis.analysis_size) for p in candidate.corners])
        cv2.polylines(overlay,[np.rint(points).astype(np.int32)],True,
                      (0,0,255) if result.corners else (0,210,210),2)
    images['overlay']=overlay
    for run in runs:
        trial=run.trial
        images[trial.trial_id+'_edges']=trial.edges
        images[trial.trial_id+('_region_mask' if isinstance(trial,RegionTrial) else '_contour_map')]=(
            trial.mask if isinstance(trial,RegionTrial) else trial.closed)
    metrics=evaluate_quad(result.corners,truth,*analysis.source_size)
    metadata={'experiment_version':'detection-ablation-v1','production_algorithm_version':DETECTION_ALGORITHM_VERSION,
        'source':source_info,'profile':profile,'analysis_size':analysis.analysis_size,
        'fixed':{'preset':'revised','canny_pairs':[[20,60],[50,150],[75,200]],'analysis_max_edge':1200,
            'aperture':3,'L2gradient':True,'closing_kernel':[3,3],'conditional_otsu_fallback':True,
            'epsilon_ratios':[.015,.02,.03],'min_area_ratio':.1,'min_side_ratio':.05,
            'score':'clip(.45a+.35e+.20f-.15b,0,1)','nms_iou_strict_gt':.95,'status_gates':[.4,.6]},
        'units':{'corners':'normalized source W-1/H-1','lengths':'analysis pixels','angles':'radians',
            'corner_error':'source pixels / source diagonal','support':'raw Canny, inclusive samples <=2px, radius2px'},
        'selection_definition':'largest valid contour before score NMS; same status gates' if profile['selection']=='largest_contour'
            else 'score-ranked polygon NMS and first survivor',
        'result':{'status':result.status,'corners':result.corners,'heuristic_score':result.heuristic_score,
            'warnings':result.warnings,'confirmed':False,'selected':asdict(result.selected) if result.selected else None},
        'descriptions':[asdict(d) for d in descriptions],
        'trials':[{'trial_id':r.trial.trial_id,'method':r.trial.method,'batch':asdict(r.batch)} for r in runs],
        'metrics':metrics,'timings_ms':timings,
        'timing_scope':'one core observation, excludes PNG decode/encode/files; not a benchmark',
        'overlay_legend':{'green':'manual ground truth when labelable','red':'proposal',
            'yellow':'diagnostic only, never evaluated as a proposal','blue':'selected raw contour'},
        'artifacts':{name:save_png(folder/(name+'.png'),im) for name,im in images.items()}}
    write_json(folder/'metadata.json',metadata)
    panel=cv2.copyMakeBorder(overlay,30,0,0,0,cv2.BORDER_CONSTANT,value=(255,255,255))
    cv2.putText(panel,profile['id']+': '+result.status,(5,20),cv2.FONT_HERSHEY_SIMPLEX,.45,(0,0,0),1)
    selected=result.selected
    row={**metrics,'profile':profile['id'],'status':result.status,'core_ms':timings['total'],
         'method':selected.candidate.method if selected else '', 'candidate_count':len(descriptions),
         'heuristic_score':result.heuristic_score,'error':''}
    row.update({key:getattr(selected,key) if selected else None for key in
                ('area_ratio','edge_support','fit_area_ratio','border_penalty')})
    return row,resize_to_max_edge(panel,720)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest',type=Path,default=ROOT/'experiments/dataset_manifest.csv')
    parser.add_argument('--annotations',type=Path,default=ROOT/'experiments/annotations.json')
    parser.add_argument('--config',type=Path,default=CONFIG)
    parser.add_argument('--project-root',type=Path,default=ROOT)
    parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args(argv)
    try:
        profiles=load_profiles(args.config)
        validate_annotations(args.annotations,args.manifest,args.project_root,split='development')
        with args.manifest.open(encoding='utf-8-sig',newline='') as f:
            cases=[r for r in csv.DictReader(f) if r['split']=='development']
        labels={r['image_id']:r for r in json.loads(args.annotations.read_text(encoding='utf-8'))['records']}
        if not cases:raise ValueError('Không có ảnh development.')
        args.output_dir.mkdir(parents=True)
        rows=[]
        for case in cases:
            image_id=case['image_id'];label=labels[image_id];folder=args.output_dir/image_id;folder.mkdir()
            identity={k:case[k] for k in ('image_id','document_id','split')}
            payload=(args.project_root/case['normalized_path']).read_bytes()
            if (sha256(payload).hexdigest()!=case['normalized_sha256']
                    or case['normalized_sha256']!=label['normalized_sha256']):
                raise ValueError('Nguồn/nhãn thay đổi sau kiểm tra hash.')
            with Image.open(BytesIO(payload)) as im:
                if im.size!=(label['width'],label['height']):raise ValueError('Dimensions nguồn/nhãn không khớp.')
                source=cv2.cvtColor(np.array(im.convert('RGB')),cv2.COLOR_RGB2BGR)
            source.setflags(write=False);digest=sha256(source.tobytes()).hexdigest()
            (folder/'source.png').write_bytes(payload)
            source_info={**identity,'normalized_sha256':case['normalized_sha256'],
                'raw_sha256':case['source_sha256'],'width':label['width'],'height':label['height'],
                'ground_truth_status':label['status'],'ground_truth_corners':label['corners']}
            panels=[]
            for profile in profiles:
                try:
                    measured=run_profile(source,profile)
                    row,panel=write_profile(folder/profile['id'],source_info,profile,measured,label['corners'])
                    panels.append(panel)
                except (ValueError,cv2.error) as error:
                    row={**evaluate_quad(None,label['corners'],label['width'],label['height']),
                        'profile':profile['id'],'status':'error','error':str(error)}
                    write_json(folder/(profile['id']+'-error.json'),row)
                rows.append({**identity,'label_status':label['status'],**row})
            if sha256(source.tobytes()).hexdigest()!=digest:raise ValueError('Nguồn bị thay đổi trong detector.')
            if panels:save_png(folder/'comparison.png',np.concatenate(panels,axis=1))
        fields=['image_id','document_id','split','profile','label_status','status','has_proposal','has_ground_truth',
            'iou','corner_error_px','corner_error_normalized','core_ms','heuristic_score','area_ratio','edge_support',
            'fit_area_ratio','border_penalty','method','candidate_count','error']
        with (args.output_dir/'results.csv').open('x',encoding='utf-8',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
        names=['backend/app/processing/detection.py','backend/app/processing/polygon_metrics.py',
               'experiments/metrics.py','experiments/evaluate_detection.py','experiments/validate_annotations.py']
        summary={'experiment_version':'detection-ablation-v1','split':'development','images':len(cases),
            'documents':len({c['document_id'] for c in cases}),'profile_runs':len(rows),
            'errors':sum(r['status']=='error' for r in rows),'profiles':profiles,
            'metrics_by_profile':{p['id']:aggregate_metrics(r for r in rows if r['profile']==p['id']) for p in profiles},
            'denominators':'IoU rate/mean over all labeled references, missing proposal IoU=0; unlabelable separate; corner mean only detected labeled',
            'environment':{'python':sys.version,'opencv':cv2.__version__,'numpy':np.__version__},
            'input_sha256':{str(p.name):sha256(p.read_bytes()).hexdigest() for p in [args.manifest,args.annotations,args.config]},
            'code_sha256':{name:sha256((ROOT/name).read_bytes()).hexdigest() for name in names},
            'test_images_processed':0,'purpose':'Development observations; not test accuracy or repeated timing benchmark.'}
        write_json(args.output_dir/'summary.json',summary)
        print(json.dumps({'images':len(cases),'runs':len(rows),'errors':summary['errors']}))
        return 1 if summary['errors'] else 0
    except (ValueError,OSError,csv.Error) as error:
        print('Lỗi evaluate_detection: '+str(error),file=sys.stderr);return 1


if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8');sys.stderr.reconfigure(encoding='utf-8')
    raise SystemExit(main())
