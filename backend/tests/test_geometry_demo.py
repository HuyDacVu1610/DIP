"""Run the actual demo command and inspect its saved artifacts."""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

PROJECT = Path(__file__).resolve().parents[2]
SCRIPT = PROJECT / 'experiments' / 'geometry_demo.py'


def run_demo(input_path, output, cwd, *options):
    return subprocess.run([sys.executable, str(SCRIPT), str(input_path), '--output-dir', str(output), *options],
                          cwd=cwd, capture_output=True, text=True, encoding='utf-8', timeout=30)


def test_full_image_demo_is_reproducible_preserves_input_and_records_geometry(tmp_path):
    source = PROJECT/'fixtures'/'corners_rgb.png'
    original = source.read_bytes()
    output = tmp_path/'kết quả demo'
    result = run_demo(source, output, tmp_path)
    assert result.returncode == 0, result.stderr
    metadata = json.loads((output/'metadata.json').read_text(encoding='utf-8'))
    assert metadata['corners_normalized'] == [[0,0],[1,0],[1,1],[0,1]]
    assert metadata['source']['width'] == 96 and metadata['source']['height'] == 64
    assert metadata['warp']['width'] == 95 and metadata['warp']['height'] == 63
    assert metadata['input']['sha256'] == hashlib.sha256(original).hexdigest()
    for key in ['source','overlay','warp']:
        artifact = metadata[key]
        payload = (output/artifact['file']).read_bytes()
        assert artifact['sha256'] == hashlib.sha256(payload).hexdigest()
        with Image.open(output/artifact['file']) as image:
            assert image.size == (artifact['width'],artifact['height'])
            assert image.mode == 'RGB' and not image.getexif()
    with Image.open(source) as image:
        source_pixels = np.asarray(image)
    with Image.open(output/'source.png') as image:
        np.testing.assert_array_equal(np.asarray(image), source_pixels)
    with Image.open(output/'overlay.png') as image:
        assert not np.array_equal(np.asarray(image), source_pixels)
    with Image.open(output/'warp.png') as image:
        warped = np.asarray(image)
    for y,x in [(12,12),(12,82),(50,82),(50,12)]:
        np.testing.assert_array_equal(warped[y,x], source_pixels[y,x])
    assert source.read_bytes() == original


def test_demo_uses_supplied_normalized_quad_and_post_exif_dimensions(tmp_path):
    corners = [[0.1,0.1],[0.9,0.15],[0.8,0.9],[0.15,0.85]]
    output = tmp_path/'tilted'
    result = run_demo(PROJECT/'fixtures'/'exif_6.jpg', output, tmp_path, '--corners', json.dumps(corners))
    assert result.returncode == 0, result.stderr
    info = json.loads((output/'metadata.json').read_text(encoding='utf-8'))
    assert info['corners_normalized'] == corners
    assert (info['source']['width'],info['source']['height']) == (64,96)
    points = np.array(info['corners_source_px'])
    np.testing.assert_allclose(points, np.array(corners)*[63,95])
    matrix = np.array(info['homography_source_to_warp'])
    assert matrix.shape == (3,3) and np.all(np.isfinite(matrix))


@pytest.mark.parametrize('corners,code', [
    ('[[0,0],[1,1],[1,0],[0,1]]','SELF_INTERSECTION'),
    ('[[0,0],[0,1],[1,1],[1,0]]','INVALID_WINDING'),
    ('[[0,0],[1,0],[0.2,0.2],[0,1]]','NON_CONVEX_QUAD'),
])
def test_demo_invalid_quad_has_reason_and_no_success_directory(tmp_path,corners,code):
    output = tmp_path/'bad'
    result = run_demo(PROJECT/'fixtures'/'corners_rgb.png',output,tmp_path,'--corners',corners)
    assert result.returncode == 1 and code in result.stderr
    assert 'Traceback' not in result.stderr and not output.exists()


def test_demo_invalid_json_is_usage_error(tmp_path):
    result = run_demo(PROJECT/'fixtures'/'corners_rgb.png',tmp_path/'out',tmp_path,'--corners','oops')
    assert result.returncode == 2 and '--corners' in result.stderr and 'JSON' in result.stderr
    assert 'Traceback' not in result.stderr and not (tmp_path/'out').exists()


def test_demo_does_not_overwrite_existing_directory(tmp_path):
    output=tmp_path/'existing'
    output.mkdir()
    marker=output/'keep.txt'
    marker.write_text('keep',encoding='utf-8')
    result=run_demo(PROJECT/'fixtures'/'corners_rgb.png',output,tmp_path)
    assert result.returncode == 1 and 'OUTPUT_EXISTS' in result.stderr
    assert marker.read_text(encoding='utf-8') == 'keep'
    assert list(output.iterdir()) == [marker]


def test_demo_bad_image_is_rejected_before_artifacts(tmp_path):
    result=run_demo(PROJECT/'fixtures'/'fake.jpg',tmp_path/'out',tmp_path)
    assert result.returncode == 1 and 'UNSUPPORTED_FORMAT' in result.stderr
    assert not (tmp_path/'out').exists()
