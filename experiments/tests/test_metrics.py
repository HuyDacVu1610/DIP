import math
import pytest
from experiments.metrics import evaluate_quad, aggregate_metrics

QUAD=((.1,.1),(.8,.1),(.8,.8),(.1,.8))

@pytest.mark.parametrize('reverse',[False,True])
@pytest.mark.parametrize('shift',range(4))
def test_same_geometry_has_exact_iou_and_zero_corner_error_for_all_eight_cycles(reverse,shift):
    other=QUAD[::-1] if reverse else QUAD
    other=other[shift:]+other[:shift]
    value=evaluate_quad(other,QUAD,1001,501)
    assert value['iou']==1 and value['corner_error_px']==0
    assert value['corner_error_normalized']==0

def test_corner_error_uses_pixel_distance_and_one_source_diagonal():
    moved=tuple((x+.01,y+.02) for x,y in QUAD)
    result=evaluate_quad(moved,QUAD,1001,501)
    assert result['corner_error_px']==pytest.approx(math.hypot(10,10))
    assert result['corner_error_normalized']==pytest.approx(math.hypot(10,10)/math.hypot(1000,500))

def test_missing_proposal_is_failure_but_unlabelable_reference_is_separate():
    rows=[evaluate_quad(QUAD,QUAD,1001,501),evaluate_quad(None,QUAD,1001,501),
          evaluate_quad(QUAD,None,1001,501)]
    assert rows[1]['iou']==0 and rows[1]['corner_error_px'] is None
    assert rows[2]['iou'] is None
    result=aggregate_metrics(rows)
    assert result['images']==3 and result['labeled_images']==2 and result['unlabelable_images']==1
    assert result['proposals']==2 and result['iou_ge_0_90_count']==1
    assert result['iou_ge_0_90_rate']==.5 and result['mean_iou_labeled']==.5
    assert result['corner_error_samples']==1

def test_empty_aggregation_has_explicit_zero_denominators_and_no_nan():
    result=aggregate_metrics([])
    assert result['images']==0 and result['iou_ge_0_90_rate'] is None
    assert result['mean_iou_labeled'] is None and result['mean_corner_error_px_detected'] is None

@pytest.mark.parametrize('bad',[
    ((.1,.1),)*4,((.1,.1),(.8,.8),(.8,.1),(.1,.8)),
    ((float('nan'),.1),)+QUAD[1:],((1.5,.1),)+QUAD[1:],
])
def test_invalid_quads_are_rejected_instead_of_sorted_or_silently_counted_missing(bad):
    with pytest.raises(ValueError):evaluate_quad(bad,QUAD,1001,501)

