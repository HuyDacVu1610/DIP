"""Run the real offline mode demo and inspect full renders and provenance."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

PROJECT = Path(__file__).resolve().parents[2]
SCRIPT = PROJECT / 'experiments/enhancement_demo.py'


def run_demo(source, output, cwd, *options):
    return subprocess.run([sys.executable, str(SCRIPT), str(source), '--output-dir', str(output), *options],
                          cwd=cwd, capture_output=True, text=True, encoding='utf-8', timeout=30)


def test_demo_exports_full_modes_and_replayable_config_without_modifying_input(tmp_path):
    source = PROJECT / 'fixtures/corners_rgb.png'
    before = source.read_bytes()
    output = tmp_path / 'so sánh'
    process = run_demo(source, output, tmp_path)
    assert process.returncode == 0, process.stderr
    info = json.loads((output / 'metadata.json').read_text(encoding='utf-8'))
    assert info['corners_selection'] == 'full_image_default'
    assert info['input']['sha256'] == hashlib.sha256(before).hexdigest()
    assert set(info['renders']) == {'color', 'gray', 'bw_adaptive', 'bw_otsu'}
    for key, artifact in info['artifacts'].items():
        payload = (output / artifact['file']).read_bytes()
        assert artifact['sha256'] == hashlib.sha256(payload).hexdigest()
        assert artifact['byte_count'] == len(payload)
        with Image.open(output / artifact['file']) as image:
            assert image.size == (artifact['width'], artifact['height'])
            assert not image.getexif()
            if key in info['renders']:
                assert image.size == (95, 63)  # full warp, not the comparison thumbnail
                assert image.mode == ('RGB' if key == 'color' else 'L')
                if key.startswith('bw_'):
                    assert set(np.unique(image)) <= {0, 255}
    for key, render in info['renders'].items():
        config = render['effective_config']
        assert config['corners'] == [[0,0],[1,0],[1,1],[0,1]]
        assert config['confirmed'] is False
        assert config['mode'] == (key if key in ['color','gray'] else 'bw')
        assert render['otsu_threshold'] is None if key != 'bw_otsu' else 0 <= render['otsu_threshold'] <= 255
    assert 'contrast.method' in info['renders']['color']['inactive_fields']
    assert source.read_bytes() == before


def test_demo_manual_quad_exif_and_rotation_keep_original_corner_coordinates(tmp_path):
    corners = [[0.1,0.1],[0.9,0.15],[0.8,0.9],[0.15,0.85]]
    output = tmp_path / 'manual'
    process = run_demo(PROJECT / 'fixtures/exif_6.jpg', output, tmp_path,
                       '--corners', json.dumps(corners), '--rotation', '90', '--denoise', 'none', '--no-gray-clahe')
    assert process.returncode == 0, process.stderr
    info = json.loads((output / 'metadata.json').read_text(encoding='utf-8'))
    assert (info['artifacts']['source']['width'], info['artifacts']['source']['height']) == (64, 96)
    assert info['corners_normalized'] == corners and info['corners_selection'] == 'manual'
    warp = info['artifacts']['warp']
    for render in info['renders'].values():
        config = render['effective_config']
        assert config['corners'] == corners and config['rotation'] == 90 and config['denoise']['method'] == 'none'
    for key in info['renders']:
        image = info['artifacts'][key]
        assert (image['width'], image['height']) == (warp['height'], warp['width'])
    assert info['renders']['gray']['effective_config']['contrast']['method'] == 'none'


@pytest.mark.parametrize('options,code', [
    (['--corners', 'bad-json'], 'JSON'),
    (['--corners', '[[0,0],[1,1],[1,0],[0,1]]'], 'SELF_INTERSECTION'),
    (['--rotation', '45'], 'invalid choice'),
])
def test_demo_rejects_bad_geometry_or_arguments_without_success_directory(tmp_path, options, code):
    output = tmp_path / 'bad'
    process = run_demo(PROJECT / 'fixtures/corners_rgb.png', output, tmp_path, *options)
    assert process.returncode != 0 and code in process.stderr
    assert 'Traceback' not in process.stderr and not output.exists()


def test_demo_small_image_does_not_silently_switch_adaptive_to_otsu(tmp_path):
    source = tmp_path / 'tiny.png'
    Image.new('RGB', (8, 8), 'white').save(source)
    output = tmp_path / 'bad'
    process = run_demo(source, output, tmp_path)
    assert process.returncode == 1 and 'INVALID_CONFIG' in process.stderr
    assert not output.exists()


def test_demo_preserves_existing_output_and_rejects_bad_image(tmp_path):
    existing = tmp_path / 'keep'
    existing.mkdir()
    marker = existing / 'keep.txt'
    marker.write_text('keep', encoding='utf-8')
    process = run_demo(PROJECT / 'fixtures/corners_rgb.png', existing, tmp_path)
    assert process.returncode == 1 and 'OUTPUT_EXISTS' in process.stderr
    assert list(existing.iterdir()) == [marker] and marker.read_text(encoding='utf-8') == 'keep'
    output = tmp_path / 'invalid'
    process = run_demo(PROJECT / 'fixtures/fake.jpg', output, tmp_path)
    assert process.returncode == 1 and 'UNSUPPORTED_FORMAT' in process.stderr
    assert 'Traceback' not in process.stderr and not output.exists()
