import cv2
import numpy as np
import pytest
from app.processing.detection import prepare_analysis,create_edge_trials,collect_candidates

def test_zero_gaussian_is_explicit_identity_copy_not_a_default_change():
    source=np.zeros((21,21,3),dtype=np.uint8);source[10,10]=255
    default=prepare_analysis(source)
    identity=prepare_analysis(source,gaussian_kernel=0)
    assert default.gaussian_kernel==5 and default.blurred[10,10]<255
    assert identity.gaussian_kernel==0 and np.array_equal(identity.blurred,identity.gray)
    assert not np.shares_memory(identity.blurred,identity.gray)
    runs=collect_candidates(identity)
    assert all(r.trial.gaussian_kernel==0 for r in runs)
    assert runs[0].trial.trial_id=='canny_g0_20_60'

def test_closing_opt_out_keeps_the_exact_raw_canny_and_default_closing():
    gray=np.zeros((80,100),dtype=np.uint8);gray[20:60,20:80]=255
    normal=create_edge_trials(gray)
    off=create_edge_trials(gray,closing=False)
    for a,b in zip(normal,off):
        assert np.array_equal(a.edges,b.edges) and np.array_equal(b.closed,b.edges)
        assert not np.shares_memory(b.edges,b.closed)
        assert np.array_equal(a.closed,cv2.morphologyEx(a.edges,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8),borderType=cv2.BORDER_CONSTANT))
    with pytest.raises(ValueError):create_edge_trials(gray,closing=1)
