from io import BytesIO
from math import isclose
import numpy as np
import pytest
from reportlab.pdfgen.canvas import Canvas
from app.export.pdf import layout_a4,mm_to_points,append_pdf_page,encode_pdf_page


def test_mm_points_and_a4_portrait_landscape_fit_exactly_without_stretch_or_crop():
    assert mm_to_points(25.4)==72
    for width,height,expected in [(600,800,'portrait'),(800,600,'landscape'),(500,500,'portrait')]:
        layout=layout_a4(width,height,orientation='auto',margin_mm=5)
        assert layout.orientation==expected
        assert sorted([layout.page_width,layout.page_height])==pytest.approx([mm_to_points(210),mm_to_points(297)])
        margin=mm_to_points(5)
        assert layout.x>=margin-1e-9 and layout.y>=margin-1e-9
        assert layout.x+layout.draw_width<=layout.page_width-margin+1e-9
        assert layout.y+layout.draw_height<=layout.page_height-margin+1e-9
        assert isclose(layout.draw_width/layout.draw_height,width/height,rel_tol=1e-12)
        assert layout.x==pytest.approx((layout.page_width-layout.draw_width)/2)
        assert layout.y==pytest.approx((layout.page_height-layout.draw_height)/2)


@pytest.mark.parametrize('orientation',['portrait','landscape'])
@pytest.mark.parametrize('margin',[0,5,30])
def test_explicit_orientation_is_respected_for_opposite_image_and_margins(orientation,margin):
    layout=layout_a4(2000,200,orientation=orientation,margin_mm=margin)
    assert layout.orientation==orientation
    assert (layout.page_width>layout.page_height)==(orientation=='landscape')
    assert layout.draw_width/layout.draw_height==pytest.approx(10)
    assert layout.x>=mm_to_points(margin)-1e-9 and layout.y>=mm_to_points(margin)-1e-9


@pytest.mark.parametrize('change',[
    {'width':1},{'width':True},{'height':2401},{'height':2.5},
    {'orientation':'sideways'},{'margin_mm':-1},{'margin_mm':31},{'margin_mm':True},
    {'margin_mm':'5'},{'margin_mm':float('nan')},{'margin_mm':float('inf')},
])
def test_bad_dimensions_and_options_are_rejected(change):
    with pytest.raises(ValueError):layout_a4(**({'width':600,'height':800}|change))


@pytest.mark.parametrize('gray',[False,True])
@pytest.mark.parametrize('encoding',['png','jpeg'])
def test_one_page_pdf_is_real_standalone_and_keeps_source(gray,encoding):
    image=np.full((80,120),255,np.uint8) if gray else np.full((80,120,3),255,np.uint8)
    image[:20,:20]=0 if gray else (0,0,255)
    before=image.copy();payload=encode_pdf_page(image,image_encoding=encoding)
    assert payload.startswith(b'%PDF-') and payload.rstrip().endswith(b'%%EOF')
    assert np.array_equal(image,before)
    assert b'/DCTDecode' in payload if encoding=='jpeg' else b'/DCTDecode' not in payload


def test_append_draws_one_complete_page_with_explicit_size_and_no_extra_rotation():
    stream=BytesIO();canvas=Canvas(stream);image=np.zeros((120,80,3),np.uint8)
    layout=append_pdf_page(canvas,image,orientation='landscape',margin_mm=30,image_encoding='png')
    assert canvas.getPageNumber()==2 and layout.orientation=='landscape'
    assert layout.draw_width/layout.draw_height==pytest.approx(80/120)
    canvas.save();assert stream.getvalue().startswith(b'%PDF-')
    with pytest.raises(ValueError):encode_pdf_page(image,image_encoding='webp')
