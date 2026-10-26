"""Describe and encode the exact buffers returned by one core render, without replay."""
import platform

import cv2
import numpy as np
import PIL

from ..processing.render import encode_stage_png


def describe_render(result,source,run_id,revision,debug):
    config=result.effective_config
    enhancement=result.enhancement
    encoded={}
    if debug:
        stages=enhancement.stages
        if stages is None:raise ValueError('Missing actual render stages')
        arrays={'warp':result.warped_bgr,'filtered_bgr':stages.filtered_bgr,'before_rotation':stages.before_rotation}
        if stages.prepared_gray is not None:arrays['prepared_gray']=stages.prepared_gray
        encoded={name:encode_stage_png(array) for name,array in arrays.items()}
    histogram=None
    if debug and enhancement.histogram is not None:
        gray=encoded['prepared_gray']
        histogram={'counts':enhancement.histogram,'width':gray.width,'height':gray.height,
            'pixel_count':gray.width*gray.height,'source_artifact':'prepared_gray','source_png_sha256':gray.sha256,
            'threshold_method':config.threshold.method,
            'threshold_scope':'global' if config.threshold.method=='otsu' else 'local',
            'otsu_threshold':enhancement.otsu_threshold}
    metadata={'run_id':str(run_id),'pipeline_version':'scan-v1','revision':revision,'debug_persisted':debug,
        'source':{'artifact_id':str(source.id),'sha256':source.sha256,'width':source.width,'height':source.height},
        'effective_config':config.model_dump(mode='json'),'inactive_fields':config.inactive_fields,
        'corners_origin':result.corners_origin,'homography_source_to_warp':result.homography.tolist(),
        'otsu_threshold':enhancement.otsu_threshold if debug else None,'histogram':histogram,
        'histogram_unavailable_reason':None if histogram is not None else ('debug_not_requested' if not debug else 'mode_has_no_threshold'),
        'stage_status':{name:('stored' if name in encoded else 'not_applicable' if name=='prepared_gray' and config.mode=='color' else 'not_requested')
            for name in ('warp','filtered_bgr','prepared_gray','before_rotation')},
        'units':{'corners':'normalized source after EXIF; W-1/H-1','warp':'source pixels; INTER_LINEAR/BORDER_REPLICATE',
            'stages':'full warp before rotation','rotation':'clockwise degrees',
            'histogram':'256 raw counts of prepared_gray before threshold/rotation; levels0..255',
            'preview':'INTER_AREA from final full render; max1000/no upscale'},
        'environment':{'python':platform.python_version(),'opencv':cv2.__version__,'numpy':np.__version__,'pillow':PIL.__version__},
        'timings_scope':'core.*: validation/warp/enhance including histogram; source_load: verify/read/decode; encode: full/preview/debug PNG; excludes publication/DB commit',
        'artifacts':{}}
    return metadata,encoded
