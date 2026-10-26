"""Offline quad metrics; cyclic/reversed order is equivalent only for evaluation."""
from math import dist,hypot
from statistics import mean

from app.processing.geometry import GeometryValidationError,validate_quad
from app.processing.polygon_metrics import polygon_iou


def _clockwise(quad,width,height):
    try:validate_quad(quad,width,height)
    except GeometryValidationError as error:
        if error.code!='INVALID_WINDING':raise
        quad=quad[::-1]
        validate_quad(quad,width,height)
    return tuple(tuple(p) for p in quad)


def evaluate_quad(prediction,truth,width,height):
    # Validate dimensions even when neither side has points.
    validate_quad(((0,0),(1,0),(1,1),(0,1)),width,height)
    prediction=_clockwise(prediction,width,height) if prediction is not None else None
    truth=_clockwise(truth,width,height) if truth is not None else None
    base={'has_proposal':prediction is not None,'has_ground_truth':truth is not None,
          'iou':None,'corner_error_px':None,'corner_error_normalized':None}
    if truth is None:return base
    if prediction is None:return {**base,'iou':0.0}
    predicted=validate_quad(prediction,width,height);target=validate_quad(truth,width,height)
    permutations=[cycle[i:]+cycle[:i] for cycle in (predicted,predicted[::-1]) for i in range(4)]
    error=min(mean(dist(a,b) for a,b in zip(cycle,target)) for cycle in permutations)
    return {**base,'iou':polygon_iou(prediction,truth,width,height),'corner_error_px':error,
            'corner_error_normalized':error/hypot(width-1,height-1)}


def aggregate_metrics(rows):
    rows=list(rows);labeled=[r for r in rows if r['has_ground_truth']]
    errors=[r['corner_error_px'] for r in labeled if r['corner_error_px'] is not None]
    hits=sum(r['iou']>=.90 for r in labeled)
    return {'images':len(rows),'labeled_images':len(labeled),'unlabelable_images':len(rows)-len(labeled),
            'proposals':sum(r['has_proposal'] for r in rows),
            'missing_proposals_labeled':sum(not r['has_proposal'] for r in labeled),
            'iou_ge_0_90_count':hits,'iou_ge_0_90_rate':hits/len(labeled) if labeled else None,
            'mean_iou_labeled':mean(r['iou'] for r in labeled) if labeled else None,
            'corner_error_samples':len(errors),'mean_corner_error_px_detected':mean(errors) if errors else None,
            'mean_corner_error_normalized_detected':mean(r['corner_error_normalized'] for r in labeled
                if r['corner_error_normalized'] is not None) if errors else None}
