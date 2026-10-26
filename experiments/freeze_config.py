"""Freeze local algorithm/config/environment identity before held-out evaluation."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
from importlib.metadata import distributions
import inspect
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys

import cv2

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'backend')]
from app.processing import detection
from app.processing.config import get_preset
from experiments.detection_artifacts import write_json


def _hash(path):
    return sha256(path.read_bytes()).hexdigest()


def _version(command):
    return subprocess.check_output(command,cwd=ROOT,text=True,timeout=15).strip()


def capture_snapshot():
    """Read source/config metadata and dependencies; never open dataset pixels."""
    sources=[]
    for directory in ['backend/app','frontend/src']:
        sources.extend(p for p in (ROOT/directory).rglob('*') if p.suffix in ('.py','.ts','.tsx','.mjs','.css'))
    # Bind existing processing/evaluation helpers; a future benchmark runner
    # records its own hash without changing these frozen implementations.
    sources.extend(ROOT/'experiments'/name for name in (
        'normalize_one.py','geometry_demo.py','enhancement_demo.py','compare_detection.py',
        'detect_batch.py','detection_artifacts.py','scan_one.py','validate_dataset.py',
        'validate_annotations.py','metrics.py','evaluate_detection.py',
        'evaluate_enhancement.py','freeze_config.py'))
    inputs=['backend/requirements.txt','backend/pyproject.toml','frontend/package.json',
            'frontend/package-lock.json','frontend/vite.config.ts','frontend/tsconfig.json',
            'experiments/dataset_manifest.csv','experiments/annotations.json','experiments/configs/detection_trials.json']
    canonical=lambda s:re.sub(r'[-_.]+','-',s).lower()
    packages={canonical(d.metadata['Name']):d.version for d in distributions()}
    for line in (ROOT/'backend/requirements.txt').read_text(encoding='utf-8').splitlines():
        if not line.strip() or line.startswith('#'):continue
        name,version=line.strip().split('==')
        if packages.get(canonical(name))!=version:
            raise ValueError('Dependency Python lệch requirements: '+name)
    package=json.loads((ROOT/'frontend/package.json').read_text())
    frontend={}
    for name,version in {**package['dependencies'],**package['devDependencies']}.items():
        installed=json.loads((ROOT/'frontend/node_modules'/name/'package.json').read_text(encoding='utf-8'))['version']
        if installed!=version:raise ValueError('Dependency frontend lệch package.json: '+name)
        frontend[name]=installed
    signature=lambda fn,key:inspect.signature(fn).parameters[key].default
    return {'freeze_id':'mvp13-freeze-v1',
        'algorithms':{'pipeline_version':'scan-v1','detection':{
            'version':detection.DETECTION_ALGORITHM_VERSION,'preset':signature(detection.detect_document,'preset'),
            'analysis_max_edge':detection.MAX_ANALYSIS_LONG_EDGE,
            'gaussian_kernel':signature(detection.prepare_analysis,'gaussian_kernel'),
            'closing':signature(detection.collect_candidates,'closing'),
            'canny_pairs':[list(p) for p in detection.REVISED_CANNY_THRESHOLD_PAIRS],
            'epsilon_ratios':list(detection.APPROX_EPSILON_RATIOS),'max_contours':detection.MAX_CONTOURS_PER_TRIAL,
            'min_area_ratio':.1,'min_side_ratio':.05,'score_weights':{'a':.45,'e':.35,'f':.20,'b':-.15},
            'nms_iou_strict_gt':.95,'proposal_threshold':.60,'warning_threshold':.40,
            'support':'raw Canny, radius 2 analysis pixels, sample spacing <=2 pixels',
            'region_fallback':'Otsu bright external component only if all Canny trials lack quads'},
            'enhancement_comparison':'enhancement-comparison-v1','detection_ablation':'detection-ablation-v1'},
        'presets':{mode:get_preset(mode).model_dump(mode='json') for mode in ('color','gray','bw')},
        'source_sha256':{p.relative_to(ROOT).as_posix():_hash(p) for p in sorted(sources)},
        'input_sha256':{name:_hash(ROOT/name) for name in inputs},
        'python_dependencies':dict(sorted(packages.items())),
        'frontend_dependencies':frontend,
        'environment':{'python':platform.python_version(),'implementation':platform.python_implementation(),
            'platform':platform.platform(),'machine':platform.machine(),'processor':platform.processor(),
            'logical_cpus':os.cpu_count(),'node':_version(['node','--version']),
            'npm':_version(['npm.cmd' if os.name=='nt' else 'npm','--version']),
            'opencv':cv2.__version__,'opencv_threads':cv2.getNumThreads(),
            'opencv_optimized':cv2.useOptimized(),'opencv_opencl':cv2.ocl.useOpenCL(),
            'opencv_build_sha256':sha256(cv2.getBuildInformation().encode()).hexdigest()},
        'data_policy':{'images':13,'documents':2,'development_images':6,'test_images':7,
            'development_documents':1,'test_documents':1,'test_images_processed_before_freeze':0,
            'tuning':'development only; keep failed cases; do not overwrite this freeze after test',
            'future_runner':'verify_frozen before held-out runs; hash new benchmark script separately'}}


def freeze(output,regression_proof):
    """Write once after the explicitly requested regression gate passes."""
    if output.exists():raise FileExistsError(output)
    proof=json.loads(regression_proof.read_text(encoding='utf-8'))
    if (not isinstance(proof,dict) or proof.get('status')!='passed'
            or any(proof.get(key) is not True for key in ('frontend_build_typecheck','browser_smoke','route_checks'))
            or any(type(proof.get(key)) is not int or proof[key]<1 for key in ('backend_experiments_tests','frontend_tests'))):
        raise ValueError('Cần bằng chứng hồi quy đạt trước khi khóa.')
    value={'schema_version':1,'frozen_at_utc':datetime.now(timezone.utc).isoformat(),
           'snapshot':capture_snapshot(),'regression':{'sha256':_hash(regression_proof),'summary':proof}}
    write_json(output,value)
    return value


def verify_frozen(path):
    """Fail closed on code, config, data metadata or environment drift."""
    value=json.loads(path.read_text(encoding='utf-8'))
    if (not isinstance(value,dict) or type(value.get('schema_version')) is not int
            or value['schema_version']!=1 or value.get('snapshot')!=capture_snapshot()):
        raise ValueError('Frozen snapshot không khớp mã nguồn/cấu hình/dữ liệu/môi trường hiện tại.')
    return value


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'experiments/configs/frozen.json')
    parser.add_argument('--regression-proof',type=Path)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args(argv)
    try:
        if args.check:verify_frozen(args.output)
        else:
            if args.regression_proof is None:raise ValueError('Cần --regression-proof.')
            freeze(args.output,args.regression_proof)
        print(json.dumps({'status':'verified' if args.check else 'frozen','sha256':_hash(args.output)}))
        return 0
    except (ValueError,OSError,subprocess.SubprocessError) as error:
        print('Lỗi freeze: '+str(error),file=sys.stderr);return 1


if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8');sys.stderr.reconfigure(encoding='utf-8')
    raise SystemExit(main())
