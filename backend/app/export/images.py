"""Full render encoders: gray/BGR uint8 -> fresh RGB/L PNG or JPEG."""
from dataclasses import dataclass
from io import BytesIO
import re
import unicodedata
import numpy as np
from PIL import Image,UnidentifiedImageError
from ..processing.render import encode_stage_png


@dataclass(frozen=True,slots=True)
class EncodedImage:
    payload: bytes
    mime: str
    filename: str
    width: int
    height: int


def download_filename(title: str,format: str) -> str:
    if format not in ('png','jpg','pdf'):
        raise ValueError('Định dạng xuất không hợp lệ.')
    text=unicodedata.normalize('NFKD',title.replace('đ','d').replace('Đ','D'))
    slug=re.sub(r'[^A-Za-z0-9_-]+','-',text.encode('ascii','ignore').decode()).strip('-_')[:80] or 'document'
    if slug.upper() in {'CON','PRN','AUX','NUL',*(f'COM{i}' for i in range(1,10)),*(f'LPT{i}' for i in range(1,10))}:
        slug='document-'+slug
    return slug+'.'+format


def _validate(image):
    if (not isinstance(image,np.ndarray) or image.dtype!=np.uint8 or image.ndim not in (2,3)
            or (image.ndim==3 and image.shape[2]!=3) or min(image.shape[:2])<2 or max(image.shape[:2])>2400):
        raise ValueError('Ảnh xuất phải là gray/BGR uint8, mỗi chiều2..2400pixel.')


def encode_image(full_bgr,format: str,*,title: str='document') -> EncodedImage:
    _validate(full_bgr)
    filename=download_filename(title,format)
    if format not in ('png','jpg'):
        raise ValueError('Encoder ảnh chỉ nhận PNG/JPG.')
    if format=='png':
        payload=encode_stage_png(full_bgr).png_bytes
    else:
        pixels=full_bgr[:,:,::-1] if full_bgr.ndim==3 else full_bgr
        stream=BytesIO()
        with Image.fromarray(pixels) as image:
            image.save(stream,format='JPEG',quality=95,subsampling=0)
        payload=stream.getvalue()
    return EncodedImage(payload,'image/png' if format=='png' else 'image/jpeg',filename,full_bgr.shape[1],full_bgr.shape[0])


def decode_full_png(payload: bytes,expected_size: tuple[int,int]):
    try:
        with Image.open(BytesIO(payload)) as image:
            if (image.format!='PNG' or image.mode not in ('RGB','L') or image.n_frames!=1
                    or image.size!=expected_size or min(image.size)<2 or max(image.size)>2400
                    or image.getexif() or image.info.get('icc_profile')):
                raise ValueError('Full PNG không khớp kích thước/kênh/metadata đã lưu.')
            image.load()
            pixels=np.array(image)
    except (OSError,UnidentifiedImageError) as error:
        raise ValueError('Không giải mã được full PNG.') from error
    return pixels[:,:,::-1].copy() if pixels.ndim==3 else pixels
