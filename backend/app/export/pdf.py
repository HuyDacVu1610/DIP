"""A4 placement from already-rotated full pixels; no crop, resize, or extra rotation."""
from dataclasses import dataclass
from io import BytesIO
from math import isfinite
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas
from .images import encode_image


def mm_to_points(value: float) -> float:
    if type(value) not in (int,float) or not isfinite(value) or value<0:
        raise ValueError('Kích thước mm phải hữu hạn và không âm.')
    return value/25.4*72


@dataclass(frozen=True,slots=True)
class PdfPageLayout:
    orientation: str
    page_width: float
    page_height: float
    x: float
    y: float
    draw_width: float
    draw_height: float


def layout_a4(width: int,height: int,*,orientation: str='auto',margin_mm: float=5) -> PdfPageLayout:
    if type(width) is not int or type(height) is not int or not (2<=width<=2400 and 2<=height<=2400):
        raise ValueError('Kích thước full render phải là số nguyên2..2400pixel.')
    if orientation not in ('auto','portrait','landscape'):
        raise ValueError('Hướng trang PDF không hợp lệ.')
    if type(margin_mm) not in (int,float) or not isfinite(margin_mm) or not 0<=margin_mm<=30:
        raise ValueError('Lề A4 phải hữu hạn, trong0..30mm.')
    selected=('landscape' if width>height else 'portrait') if orientation=='auto' else orientation
    page_width,page_height=mm_to_points(210),mm_to_points(297)
    if selected=='landscape':page_width,page_height=page_height,page_width
    margin=mm_to_points(margin_mm)
    scale=min((page_width-2*margin)/width,(page_height-2*margin)/height)
    draw_width,draw_height=width*scale,height*scale
    return PdfPageLayout(selected,page_width,page_height,(page_width-draw_width)/2,(page_height-draw_height)/2,draw_width,draw_height)


def append_pdf_page(canvas,full_bgr,*,orientation: str='auto',margin_mm: float=5,image_encoding: str='png') -> PdfPageLayout:
    if image_encoding not in ('png','jpeg'):
        raise ValueError('PDF chỉ nhúng ảnh PNG/JPEG.')
    image=encode_image(full_bgr,'png' if image_encoding=='png' else 'jpg')
    layout=layout_a4(image.width,image.height,orientation=orientation,margin_mm=margin_mm)
    canvas.setPageSize((layout.page_width,layout.page_height))
    canvas.drawImage(ImageReader(BytesIO(image.payload)),layout.x,layout.y,
        width=layout.draw_width,height=layout.draw_height)
    canvas.showPage()
    return layout


def encode_pdf_page(full_bgr,*,orientation: str='auto',margin_mm: float=5,image_encoding: str='png') -> bytes:
    stream=BytesIO()
    canvas=Canvas(stream,pageCompression=1)
    append_pdf_page(canvas,full_bgr,orientation=orientation,margin_mm=margin_mm,image_encoding=image_encoding)
    canvas.save()
    return stream.getvalue()
