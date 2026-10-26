"""Create five deterministic synthetic teaching scenes, outside the measured dataset."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def create_samples(output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=False)
    corners = np.array([[140, 100], [720, 145], [755, 970], [95, 940]], np.float32)
    matrix = cv2.getPerspectiveTransform(np.array([[0, 0], [599, 0], [599, 849], [0, 849]], np.float32), corners)
    records = []
    for name in ['01-clean', '02-shadow', '03-no-boundary', '04-highlight', '05-fold-light-simulation']:
        page = Image.new('RGB', (600, 850), (244, 242, 232))
        draw = ImageDraw.Draw(page)
        if name == '04-highlight':
            draw.rectangle((40, 220, 560, 255), fill=(255, 230, 50))
        draw.text((40, 45), 'SCANNER DEMO ' + name[:2], font=ImageFont.load_default(size=36), fill=(25, 25, 25))
        draw.text((40, 100), 'Synthetic teaching sample', font=ImageFont.load_default(size=24), fill=(30, 30, 30))
        for index in range(14):
            draw.text((40, 175 + 39 * index), f'Line {index + 1:02}: keep details and page order.',
                      font=ImageFont.load_default(size=22), fill=(35, 35, 35))
        pixels = np.array(page, dtype=np.float32)
        if name == '02-shadow':
            factor = .32 + .68 / (1 + np.exp(-(np.arange(600) - 285) / 24))
            pixels *= factor[None, :, None]
        if name == '05-fold-light-simulation':
            # Illumination stripe only: this does not simulate a 3D curved sheet.
            factor = 1 - .30 * np.exp(-((np.arange(600) - 315) / 11) ** 2)
            pixels *= factor[None, :, None]
        image = cv2.warpPerspective(pixels.astype(np.uint8), matrix, (900, 1100),
                                    flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(49, 65, 60))
        quad = (corners / np.array([899, 1099])).tolist()
        if name == '03-no-boundary':
            image.fill(210)
            quad = [[0, 0], [1, 0], [1, 1], [0, 1]]
        path = output / (name + '.png')
        Image.fromarray(image).save(path)
        records.append({'file':path.name, 'width':900, 'height':1100,
                        'sha256':sha256(path.read_bytes()).hexdigest(), 'construction_corners':quad})
    manifest = {'schema_version':1, 'synthetic':True, 'measured_dataset':False,
                'purpose':'UI rehearsal and algorithm explanation, no accuracy or robustness claim',
                'no_boundary_note':'Uniform image; use whole-image manual selection. Not a photographed page.',
                'fold_note':'Brightness stripe on a planar polygon only; not physical folds or dewarping evidence.',
                'files':records}
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=Path(__file__).resolve().parents[1] / 'fixtures/demo')
    args = parser.parse_args()
    print(json.dumps(create_samples(args.output_dir)))
