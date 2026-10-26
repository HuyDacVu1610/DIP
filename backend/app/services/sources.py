"""Shared verified normalized-PNG decode, with no upload quota or second EXIF pass."""
import warnings
import numpy as np
from PIL import Image, UnidentifiedImageError

from ..settings import MAX_IMAGE_PIXELS
from ..storage.files import ArtifactFileError, ArtifactStore, StoredArtifact


def load_normalized_source(store: ArtifactStore, source: StoredArtifact, size: tuple[int,int]):
    path = store.verify(source)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error',Image.DecompressionBombWarning)
            with Image.open(path,formats=('PNG',)) as image:
                if (image.size!=size or source.width!=size[0] or source.height!=size[1]
                        or min(size)<2 or size[0]*size[1]>MAX_IMAGE_PIXELS
                        or image.mode!='RGB' or getattr(image,'n_frames',1)!=1 or image.getexif()):
                    raise ArtifactFileError('Nguồn PNG không khớp hợp đồng chuẩn hóa.')
                image.load()
                return np.asarray(image)[:,:,::-1].copy()
    except (UnidentifiedImageError,OSError,SyntaxError,ValueError,EOFError,
            Image.DecompressionBombWarning,Image.DecompressionBombError) as error:
        raise ArtifactFileError('Không đọc được nguồn PNG chuẩn hóa.') from error
