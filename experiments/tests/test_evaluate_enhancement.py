import csv
from hashlib import sha256
import json

import cv2
import numpy as np
from PIL import Image
import pytest

from experiments.evaluate_enhancement import compare_thresholds, main
from experiments.validate_dataset import FIELDS


def test_pair_uses_identical_warp_gray_and_config_except_threshold():
    source = np.full((180, 240, 3), 220, np.uint8)
    source[:, :100] = 90
    cv2.putText(source, 'TEST', (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (15, 15, 15), 2)
    before = source.copy()
    warp, matrix, renders = compare_thresholds(source, ((0,0),(1,0),(1,1),(0,1)))
    assert warp.shape == (179, 239, 3) and matrix.shape == (3, 3)
    otsu, adaptive = renders['otsu'], renders['adaptive_gaussian']
    a, b = [r.effective_config.model_dump(mode='json') for r in (otsu, adaptive)]
    a['threshold']['method'] = b['threshold']['method']
    assert a == b and not a['confirmed']
    assert np.array_equal(otsu.stages.prepared_gray, adaptive.stages.prepared_gray)
    assert otsu.histogram == adaptive.histogram and sum(otsu.histogram) == 179 * 239
    assert otsu.otsu_threshold is not None and adaptive.otsu_threshold is None
    assert set(np.unique(otsu.image)) <= {0, 255} and set(np.unique(adaptive.image)) <= {0, 255}
    assert not np.array_equal(otsu.image, adaptive.image)
    assert np.array_equal(source, before)


def test_invalid_small_warp_fails_instead_of_clamping_block():
    with pytest.raises(ValueError):
        compare_thresholds(np.zeros((20, 20, 3), np.uint8), ((0,0),(1,0),(1,1),(0,1)))


def test_cli_keeps_unlabelable_and_never_opens_test_sources(tmp_path, monkeypatch):
    raw = tmp_path / 'experiments/data/source.png'; raw.parent.mkdir(parents=True)
    Image.new('RGB', (200, 140), 'white').save(raw)
    normalized = tmp_path / 'experiments/results/source.png'; normalized.parent.mkdir(parents=True)
    normalized.write_bytes(raw.read_bytes()); digest = sha256(raw.read_bytes()).hexdigest()
    row = dict(zip(FIELDS, ['dev', 'doc_01', 'even_light', 'development',
        'experiments/data/source.png', digest, 'experiments/results/source.png', digest]))
    skipped_raw=raw.with_name('skip.png'); Image.new('RGB',(200,140),'gray').save(skipped_raw)
    skipped_normalized=normalized.with_name('skip.png'); skipped_normalized.write_bytes(skipped_raw.read_bytes())
    skipped_digest=sha256(skipped_raw.read_bytes()).hexdigest()
    manifest = tmp_path / 'manifest.csv'
    with manifest.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS); writer.writeheader()
        writer.writerows([row, {**row, 'image_id':'skip','source_path':'experiments/data/skip.png',
            'normalized_path':'experiments/results/skip.png','source_sha256':skipped_digest,
            'normalized_sha256':skipped_digest}, {**row, 'image_id':'heldout',
            'document_id':'doc_02','split':'test','source_path':'experiments/data/missing.jpg',
            'normalized_path':'experiments/results/missing.png','source_sha256':'b'*64,'normalized_sha256':'b'*64}])
    record = {'image_id':'dev','normalized_sha256':digest,'width':200,'height':140,'status':'labeled',
        'corners':[[0,0],[1,0],[1,1],[0,1]],'reason':'','reviewed':True,'labeler':'fixture','notes':'Synthetic.'}
    annotations = tmp_path / 'annotations.json'
    annotations.write_text(json.dumps({'schema_version':1,'coordinates':'normalized_w_minus_1_h_minus_1',
        'records':[record,{**record,'image_id':'skip','normalized_sha256':skipped_digest,
                          'status':'unlabelable','corners':None,'reason':'cropped'},
                   {**record,'image_id':'heldout','normalized_sha256':'b'*64}]}),encoding='utf-8')
    out = tmp_path / 'pair'
    args = ['--project-root',str(tmp_path),'--manifest',str(manifest),'--annotations',str(annotations),'--output-dir',str(out)]
    assert main(args) == 0
    summary = json.loads((out/'summary.json').read_text())
    assert summary['images'] == 2 and summary['pairs'] == 1 and summary['unlabelable'] == 1
    assert summary['test_images_processed'] == 0
    meta = json.loads((out/'dev/metadata.json').read_text())
    assert meta['source']['normalized_sha256'] == digest and meta['same_prepared_gray']
    assert meta['renders']['otsu']['otsu_threshold'] == 0
    assert meta['renders']['adaptive_gaussian']['otsu_threshold'] is None
    with (out/'results.csv').open(newline='') as f: rows = list(csv.DictReader(f))
    assert len(rows) == 3 and rows[-1]['status'] == 'unlabelable'
    assert main(args) == 1
    import experiments.evaluate_enhancement as module
    validate = module.validate_annotations
    def changed(*args, **kwargs):
        result = validate(*args, **kwargs); normalized.write_bytes(b'changed'); return result
    monkeypatch.setattr(module, 'validate_annotations', changed)
    assert main(args[:-1]+[str(tmp_path/'changed')]) == 1
    assert not (tmp_path/'changed/results.csv').exists()
