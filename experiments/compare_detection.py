"""Compare candidate generation on one local image; never confirm or warp it."""
import argparse
import json
import sys
from dataclasses import asdict
from hashlib import sha256
from io import BytesIO
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

PROJECT_ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PROJECT_ROOT/'backend'))
from app.processing.detection import DetectionValidationError, RegionTrial, collect_candidates, describe_candidate, prepare_analysis
from app.processing.geometry import normalized_to_pixel
from app.processing.image_sizes import resize_to_max_edge
from app.processing.normalize import ImageValidationError, encode_normalized_png, normalize_image
from app.settings import MAX_UPLOAD_BYTES


def _png(image):
    stream=BytesIO()
    Image.fromarray(image[:,:,::-1] if image.ndim==3 else image).save(stream,format='PNG')
    return stream.getvalue()


def _overlay(analysis,description,attempts,title):
    image=analysis.bgr.copy()
    examples=[description.candidate] if description is not None else attempts[:3]
    for candidate in examples:
        cv2.polylines(image,[np.rint(candidate.contour_px).astype(np.int32)],True,(255,120,0),1)
        if candidate.corners is not None:
            quad=np.array([normalized_to_pixel(p,*analysis.analysis_size) for p in candidate.corners])
            cv2.polylines(image,[np.rint(quad).astype(np.int32)],True,(0,0,255),2)
            for i,point in enumerate(quad):
                x,y=np.rint(point).astype(int)
                cv2.putText(image,str(i),(max(0,min(x+4,image.shape[1]-14)),max(14,min(y+14,image.shape[0]-2))),
                    cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,255),1)
    image=cv2.copyMakeBorder(image,32,30,0,0,cv2.BORDER_CONSTANT,value=(255,255,255))
    cv2.putText(image,title,(4,21),cv2.FONT_HERSHEY_SIMPLEX,.46,(0,0,0),1)
    caption='No valid quad' if description is None else f'Example S={description.heuristic_score:.6f}; {description.candidate.method}; unconfirmed'
    cv2.putText(image,caption,(4,image.shape[0]-10),cv2.FONT_HERSHEY_SIMPLEX,.4,(0,0,0),1)
    return image


def _profile(source,preset,kernel):
    analysis=prepare_analysis(source,gaussian_kernel=kernel)
    images={f'{preset}_gray':analysis.gray,f'{preset}_blurred':analysis.blurred}
    records=[]
    descriptions=[]
    runs=collect_candidates(analysis,preset=preset)
    for run in runs:
        trial,batch=run.trial,run.batch
        measured=sorted((describe_candidate(c,trial) for c in batch.candidates),key=lambda d:-d.heuristic_score)
        descriptions.extend(measured)
        prefix=f'{preset}_{trial.trial_id}'
        images[prefix+'_edges']=trial.edges
        images[prefix+('_mask' if isinstance(trial,RegionTrial) else '_closed')]=trial.mask if isinstance(trial,RegionTrial) else trial.closed
        images[prefix+'_overlay']=_overlay(analysis,measured[0] if measured else None,batch.attempts,prefix)
        record={'trial_id':trial.trial_id,'method':trial.method,'gaussian_kernel':trial.gaussian_kernel,
            'edge_thresholds':trial.thresholds,'batch':asdict(batch),'descriptions':[asdict(d) for d in measured]}
        if isinstance(trial,RegionTrial):
            record.update(otsu_threshold=trial.otsu_threshold,support_trial_id=trial.support_trial_id)
        records.append(record)
    descriptions.sort(key=lambda d:-d.heuristic_score)
    example=descriptions[0] if descriptions else None
    images[preset+'_example']=_overlay(analysis,example,runs[0].batch.attempts,f'{preset}: {len(descriptions)} candidate attempts, Gaussian{kernel}')
    return images,{'gaussian_kernel':kernel,'analysis_size':analysis.analysis_size,
        'candidate_count':len(descriptions),'example':asdict(example) if example else None,'trials':records}


def main(argv: list[str] | None = None) -> int:
    parser=argparse.ArgumentParser(description='So sánh baseline/revised candidate generation; không tự xác nhận trang.')
    parser.add_argument('input',type=Path)
    parser.add_argument('--output-dir',type=Path,required=True,help='Thư mục mới, không ghi đè.')
    parser.add_argument('--gaussian-kernel',type=int,choices=(3,5),default=5,
        help='Kernel của revised để ablation; baseline luôn Gaussian5.')
    args=parser.parse_args(argv)
    try:
        output=args.output_dir.resolve()
        if output.exists():
            raise FileExistsError(output)
        with args.input.open('rb') as stream:
            original=stream.read(MAX_UPLOAD_BYTES+1)
        source=normalize_image(original)
        before=source.copy()
        source.setflags(write=False)
        normalized=encode_normalized_png(source)
        images={'source':source}
        info={'input':{'sha256':sha256(original).hexdigest(),'byte_count':len(original)},
            'source_size':[normalized.width,normalized.height],'confirmed':False,
            'purpose':'Candidate examples by heuristic score; no NMS/proposal/fallback UI/warp or accuracy claim.',
            'score':'clip(.45a+.35e+.20f-.15b,0,1); raw Canny support only',
            'sampling':'n=max(2,ceil(L/2)+1), inclusive endpoints, Euclidean radius2, border<=2px',
            'opencv_version':cv2.__version__,'profiles':{},'artifacts':{}}
        for preset,kernel in [('baseline',5),('revised',args.gaussian_kernel)]:
            stages,profile=_profile(source,preset,kernel)
            images.update(stages)
            info['profiles'][preset]=profile
        panels=[resize_to_max_edge(images[preset+'_example'],720) for preset in ('baseline','revised')]
        cell_h=max(p.shape[0] for p in panels)
        cell_w=max(p.shape[1] for p in panels)
        comparison=np.full((cell_h,cell_w*2,3),255,dtype=np.uint8)
        for i,panel in enumerate(panels):
            comparison[:panel.shape[0],i*cell_w:i*cell_w+panel.shape[1]]=panel
        images['comparison']=comparison
        info['source_unchanged']=bool(np.array_equal(source,before))
        if not info['source_unchanged']:
            raise DetectionValidationError('SOURCE_CHANGED','Ảnh nguồn đã bị thay đổi khi phân tích.')
        payloads=[]
        for name,image in images.items():
            payload=normalized.png_bytes if name=='source' else _png(image)
            height,width=image.shape[:2]
            info['artifacts'][name]={'file':name+'.png','width':width,'height':height,
                'png_mode':'RGB' if image.ndim==3 else 'L','sha256':sha256(payload).hexdigest(),'byte_count':len(payload)}
            payloads.append((name+'.png',payload))
        payloads.append(('metadata.json',(json.dumps(info,ensure_ascii=False,indent=2)+'\n').encode('utf-8')))
        output.mkdir(parents=True)
        for name,payload in payloads:
            with (output/name).open('xb') as stream:
                stream.write(payload)
    except (ImageValidationError,DetectionValidationError) as error:
        print(f'Lỗi [{error.code}]: {error}',file=sys.stderr)
        return 1
    except FileExistsError:
        print('Lỗi [OUTPUT_EXISTS]: Hãy chọn thư mục đầu ra mới.',file=sys.stderr)
        return 1
    except OSError as error:
        print(f'Lỗi [IO_ERROR]: {error}',file=sys.stderr)
        return 1
    print(f'Đã ghi so sánh candidate baseline/revised và metadata tại: {output}')
    return 0


if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    raise SystemExit(main())
