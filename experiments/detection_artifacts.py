"""Shared offline artifact writer for one actual detection result."""
import json
from dataclasses import asdict
from hashlib import sha256
from io import BytesIO

import cv2
import numpy as np
from PIL import Image

from app.processing.detection import RegionTrial
from app.processing.image_sizes import resize_to_max_edge


def write_json(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


def save_png(path, array):
    stream = BytesIO()
    Image.fromarray(array[:,:,::-1] if array.ndim==3 else array).save(stream, format='PNG')
    payload = stream.getvalue()
    with path.open('xb') as file:
        file.write(payload)
    return {'file':path.name,'sha256':sha256(payload).hexdigest(),'byte_count':len(payload),
            'width':array.shape[1],'height':array.shape[0],'png_mode':'RGB' if array.ndim==3 else 'L'}


def write_detection_artifacts(result, source_info, folder, run_id, *, entry_point):
    """Persist the supplied run's actual debug; never rerun detection."""
    debug = result.debug
    if debug is None:
        raise ValueError('Detection debug is required for artifact persistence.')
    if (source_info['width'], source_info['height']) != debug.analysis.source_size:
        raise ValueError('Source dimensions do not match the supplied detection run.')
    preset = debug.preset
    folder.mkdir()
    images = {'analysis':debug.analysis.bgr,'gray':debug.analysis.gray,
              'blurred':debug.analysis.blurred,'contour_overlay':debug.overlay}
    trials = []
    for run in debug.trials:
        trial = run.trial
        images[trial.trial_id+'_edges'] = trial.edges
        is_region = isinstance(trial, RegionTrial)
        images[trial.trial_id+('_region_mask' if is_region else '_closed')] = trial.mask if is_region else trial.closed
        trials.append({'trial_id':trial.trial_id,'method':trial.method,'thresholds':trial.thresholds,
            'gaussian_kernel':trial.gaussian_kernel,'otsu_threshold':trial.otsu_threshold if is_region else None,
            'support_trial_id':trial.support_trial_id if is_region else None,'batch':asdict(run.batch)})
    selected = result.selected
    chosen_trial = next(({k:v for k,v in t.items() if k!='batch'}
        for t in trials if selected and t['trial_id']==selected.candidate.trial_id), None)
    info = {'entry_point':entry_point,'run_id':run_id,'algorithm_version':debug.algorithm_version,
        'preset':preset,'source':source_info|{'bgr_sha256':debug.source_bgr_sha256},
        'analysis_size':debug.analysis.analysis_size,'overlay_kind':debug.overlay_kind,
        'config':{'analysis_long_edge':1200,'gaussian_kernel':5,'sigma':0,'gaussian_border':'REFLECT_101',
            'canny_aperture':3,'l2_gradient':True,'closing_kernel':[3,3],'closing_iterations':1,
            'epsilon_ratios':[.015,.02,.03],'max_contours_per_trial':30,'min_area_ratio':.1,
            'min_side_ratio':.05,'score':'clip(.45a+.35e+.20f-.15b,0,1)',
            'nms_iou_strict_gt':.95,'proposal_threshold':.6,'warning_threshold':.4},
        'units':{'length':'analysis px','turn_angle':'radian','corners':'normalized W-1/H-1',
            'support':'raw Canny Euclidean radius2px; n=max(2,ceil(L/2)+1)', 'timings':'ms, excludes decode/encode/I/O'},
        'timings_ms':asdict(result.timings_ms),
        'result':{'status':result.status,'corners':result.corners,'heuristic_score':result.heuristic_score,
            'warnings':result.warnings,'confirmed':result.confirmed,
            'selected':asdict(selected) if selected else None,'candidates':[asdict(c) for c in result.candidates]},
        'selected_trial':chosen_trial,'trials':trials,'artifacts':{}}
    for name, array in images.items():
        info['artifacts'][name] = save_png(folder/(name+'.png'), array)
    write_json(folder/'metadata.json', info)
    panel = cv2.copyMakeBorder(debug.overlay,32,30,0,0,cv2.BORDER_CONSTANT,value=(255,255,255))
    cv2.putText(panel,f'{preset}: {result.status}',(4,21),cv2.FONT_HERSHEY_SIMPLEX,.45,(0,0,0),1)
    score = 'null' if result.heuristic_score is None else f'{result.heuristic_score:.6f}'
    cv2.putText(panel,f'S={score}; {debug.overlay_kind}; unconfirmed',(4,panel.shape[0]-10),
                cv2.FONT_HERSHEY_SIMPLEX,.4,(0,0,0),1)
    row = {'preset':preset,'status':result.status,'heuristic_score':result.heuristic_score,
        'warnings':';'.join(result.warnings),'method':selected.candidate.method if selected else '',
        'before_nms':sum(len(r.batch.candidates) for r in debug.trials),'after_nms':len(result.candidates),
        'total_ms':result.timings_ms.total,'error_code':''}
    for key in ('area_ratio','edge_support','fit_area_ratio','border_penalty'):
        row[key] = getattr(selected,key) if selected else None
    return row, resize_to_max_edge(panel,720)
