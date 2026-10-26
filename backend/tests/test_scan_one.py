"""One offline scan command, real source/render stages and honest fallback."""
import json
import subprocess
import sys
from hashlib import sha256
from pathlib import Path

import cv2
import numpy as np
import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT/'experiments/scan_one.py'
FULL = '[[0,0],[1,0],[1,1],[0,1]]'


def run_cli(source,out,cwd,*options):
    return subprocess.run([sys.executable,str(SCRIPT),str(source),'--output-dir',str(out),*options],
        cwd=cwd,capture_output=True,text=True,encoding='utf-8',timeout=60)


def read_artifacts(folder,info):
    arrays = {}
    for name,record in info['artifacts'].items():
        path = folder/record['file']
        assert sha256(path.read_bytes()).hexdigest()==record['sha256']
        with Image.open(path) as image:
            image.load()
            assert image.size==(record['width'],record['height']) and image.mode==record['png_mode']
            assert not image.getexif()
            arrays[name] = np.array(image)
    return arrays


def test_scan_auto_records_one_actual_detection_and_draft_source_based_render(tmp_path):
    source = np.full((240,320,3),25,dtype=np.uint8)
    source[25:216,30:291]=240
    input_file = tmp_path/'ảnh.png'
    Image.fromarray(source).save(input_file)
    original = input_file.read_bytes()
    output = tmp_path/'auto'
    process = run_cli(input_file,output,tmp_path)
    assert process.returncode==0,process.stderr
    info = json.loads((output/'metadata.json').read_text(encoding='utf-8'))
    assert info['status']=='rendered' and info['corners_origin']=='detected'
    assert info['effective_config']['confirmed'] is False
    detection = json.loads((output/'detection/metadata.json').read_text(encoding='utf-8'))
    assert detection['result']['corners']==info['effective_config']['corners']
    assert detection['source']['normalized_png_sha256']==info['source']['normalized_png_sha256']
    assert detection['source']['bgr_sha256']==info['source']['bgr_sha256']
    assert detection['run_id']==info['run_id']
    assert detection['entry_point']==info['entry_point']=='scan_one'
    arrays = read_artifacts(output,info)
    assert np.array_equal(arrays['source'],source)
    assert np.array_equal(arrays['full'],arrays['preview'])
    assert np.array_equal(arrays['full'],arrays['before_rotation'])
    assert not any('prepared_gray' in key for key in arrays)  # Color has no fake gray render stage
    assert info['histogram'] is None
    assert json.loads((output/'config.json').read_text())==info['effective_config']
    assert info['config_sha256']==sha256((output/'config.json').read_bytes()).hexdigest()
    assert input_file.read_bytes()==original


def test_no_quad_saves_diagnostic_then_manual_corners_complete_the_scan(tmp_path):
    source = tmp_path/'blank.png'
    Image.fromarray(np.full((100,140,3),200,dtype=np.uint8)).save(source)
    process = run_cli(source,tmp_path/'failed',tmp_path)
    assert process.returncode==2 and 'Traceback' not in process.stderr
    info = json.loads((tmp_path/'failed/metadata.json').read_text())
    assert info['status']=='manual_required' and info['effective_config']['corners'] is None
    assert info['histogram'] is None
    assert 'full' not in info['artifacts'] and not (tmp_path/'failed/render').exists()
    process = run_cli(source,tmp_path/'manual',tmp_path,'--corners',FULL)
    assert process.returncode==0,process.stderr
    manual = json.loads((tmp_path/'manual/metadata.json').read_text())
    assert manual['corners_origin']=='manual' and manual['detection_status']=='skipped_manual'
    assert not (tmp_path/'manual/detection').exists()
    assert manual['source']==info['source'] and not manual['effective_config']['confirmed']
    assert np.all(read_artifacts(tmp_path/'manual',manual)['full']==200)


def test_manual_config_exif_rotation_otsu_snapshot_can_be_reused(tmp_path):
    config = {'mode':'bw','rotation':90,'denoise':{'method':'none'},
        'threshold':{'method':'otsu','block_size':151,'c':-20}}
    path = tmp_path/'config.json'
    path.write_text(json.dumps(config))
    source = ROOT/'fixtures/exif_6.jpg'
    first,second = tmp_path/'first',tmp_path/'second'
    process = run_cli(source,first,tmp_path,'--config',str(path),'--corners',FULL)
    assert process.returncode==0,process.stderr
    info = json.loads((first/'metadata.json').read_text())
    assert (info['source']['width'],info['source']['height'])==(64,96)
    assert info['effective_config']['threshold']['block_size']==151
    assert 'threshold.block_size' in info['inactive_fields']
    assert info['otsu_threshold'] is not None and 0<=info['otsu_threshold']<=255
    arrays = read_artifacts(first,info)
    assert arrays['full'].shape==(63,95) and set(np.unique(arrays['full'])) <= {0,255}
    t,expected = cv2.threshold(arrays['prepared_gray'],0,255,cv2.THRESH_BINARY|cv2.THRESH_OTSU)
    assert t==info['otsu_threshold']
    histogram = info['histogram']
    assert histogram['counts']==np.bincount(arrays['prepared_gray'].ravel(),minlength=256).tolist()
    assert histogram['threshold_scope']=='global' and histogram['otsu_threshold']==t
    assert histogram['threshold_method']=='otsu'
    assert histogram['source_artifact']=='prepared_gray'
    assert histogram['source_png_sha256']==info['artifacts']['prepared_gray']['sha256']
    assert (histogram['width'],histogram['height'],histogram['pixel_count'])==(63,95,63*95)
    assert np.array_equal(arrays['before_rotation'],expected)
    assert np.array_equal(arrays['full'],cv2.rotate(expected,cv2.ROTATE_90_CLOCKWISE))
    process = run_cli(source,second,tmp_path,'--config',str(first/'config.json'))
    assert process.returncode==0,process.stderr
    replay = json.loads((second/'metadata.json').read_text())
    assert replay['effective_config']==info['effective_config']
    assert replay['artifacts']['full']['sha256']==info['artifacts']['full']['sha256']


def test_large_bw_preview_is_derived_after_rotation_without_rethreshold(tmp_path):
    source = tmp_path/'grid.png'
    image = ((np.indices((1301,2001)).sum(axis=0)%2)*255).astype(np.uint8)
    Image.fromarray(image).save(source)
    config = tmp_path/'bw.json'
    config.write_text(json.dumps({'mode':'bw','rotation':90,'denoise':{'method':'none'},'threshold':{'method':'otsu'}}))
    process = run_cli(source,tmp_path/'out',tmp_path,'--corners',FULL,'--config',str(config))
    assert process.returncode==0,process.stderr
    info = json.loads((tmp_path/'out/metadata.json').read_text())
    arrays = read_artifacts(tmp_path/'out',info)
    assert arrays['full'].shape==(2000,1300) and arrays['preview'].shape==(1000,650)
    assert np.array_equal(arrays['preview'],cv2.resize(arrays['full'],(650,1000),interpolation=cv2.INTER_AREA))
    assert np.any((arrays['preview']>0)&(arrays['preview']<255))
    histogram = info['histogram']
    assert sum(histogram['counts'])==histogram['pixel_count']==1300*2000
    assert histogram['counts']==np.bincount(arrays['prepared_gray'].ravel(),minlength=256).tolist()
    assert (histogram['width'],histogram['height'])==(2000,1300)  # Before rotation


def test_adaptive_histogram_describes_local_threshold_of_actual_filtered_clahe_gray(tmp_path):
    gray = np.tile(np.arange(64,dtype=np.uint8)*4,(40,1))
    source = tmp_path/'gradient.png'
    Image.fromarray(gray).save(source)
    config = tmp_path/'adaptive.json'
    config.write_text(json.dumps({'mode':'bw','rotation':90,'denoise':{'method':'gaussian'},
        'contrast':{'method':'clahe'},'threshold':{'method':'adaptive_gaussian','block_size':15,'c':7}}))
    out = tmp_path/'adaptive'
    process = run_cli(source,out,tmp_path,'--config',str(config),'--corners',FULL)
    assert process.returncode==0,process.stderr
    info = json.loads((out/'metadata.json').read_text())
    arrays = read_artifacts(out,info)
    histogram = info['histogram']
    expected_gray = cv2.createCLAHE(clipLimit=2,tileGridSize=(8,8)).apply(
        cv2.cvtColor(arrays['filtered_bgr'],cv2.COLOR_RGB2GRAY))
    assert np.array_equal(arrays['prepared_gray'],expected_gray)
    assert histogram['counts']==np.bincount(expected_gray.ravel(),minlength=256).tolist()
    assert histogram['threshold_method']=='adaptive_gaussian' and histogram['threshold_scope']=='local'
    assert histogram['otsu_threshold'] is info['otsu_threshold'] is None
    assert sum(histogram['counts'])==histogram['pixel_count']==39*63
    assert histogram['source_png_sha256']==info['artifacts']['prepared_gray']['sha256']
    bw = cv2.adaptiveThreshold(expected_gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,15,7)
    assert np.array_equal(arrays['full'],cv2.rotate(bw,cv2.ROTATE_90_CLOCKWISE))


@pytest.mark.parametrize('options,code',[(['--corners','broken'],'INVALID_CONFIG'),
    (['--corners','[[0,0]]'],'INVALID_CONFIG')])
def test_bad_corner_input_has_reason_without_success_files(tmp_path,options,code):
    process = run_cli(ROOT/'fixtures/corners_rgb.png',tmp_path/'out',tmp_path,*options)
    assert process.returncode==1 and code in process.stderr and 'Traceback' not in process.stderr
    assert not (tmp_path/'out').exists()


def test_scan_rejects_invalid_image_and_never_overwrites_previous_run(tmp_path):
    process = run_cli(ROOT/'fixtures/fake.jpg',tmp_path/'bad',tmp_path)
    assert process.returncode==1 and 'UNSUPPORTED_FORMAT' in process.stderr
    assert not (tmp_path/'bad').exists()
    out = tmp_path/'keep'
    out.mkdir()
    marker = out/'marker.txt'
    marker.write_text('keep')
    process = run_cli(ROOT/'fixtures/corners_rgb.png',out,tmp_path)
    assert process.returncode==1 and 'OUTPUT_EXISTS' in process.stderr
    assert list(out.iterdir())==[marker] and marker.read_text()=='keep'


def test_invalid_active_adaptive_block_is_not_silently_changed(tmp_path):
    config = tmp_path/'config.json'
    config.write_text(json.dumps({'mode':'bw','threshold':{'block_size':151}}))
    source = ROOT/'fixtures/exif_6.jpg'
    original = source.read_bytes()
    process = run_cli(source,tmp_path/'out',tmp_path,'--config',str(config),'--corners',FULL)
    assert process.returncode==1 and 'INVALID_CONFIG' in process.stderr
    assert not (tmp_path/'out').exists() and source.read_bytes()==original


@pytest.mark.parametrize('blank',[False,True],ids=['auto-proposal','manual-required'])
def test_repeated_cli_requested_config_reproduces_detection_and_pixels_but_has_a_new_run_id(tmp_path,blank):
    source = np.full((240,320,3),25,dtype=np.uint8)
    if not blank:
        source[25:216,30:291]=240
    input_file = tmp_path/'source.png'
    Image.fromarray(source).save(input_file)
    original = input_file.read_bytes()
    requested = tmp_path/'requested.json'
    requested.write_text(json.dumps({'mode':'bw','threshold':{'method':'otsu'}}))
    runs = [tmp_path/'first',tmp_path/'second']
    infos,detections = [],[]
    for out in runs:
        process = run_cli(input_file,out,tmp_path,'--config',str(requested))
        assert process.returncode==(2 if blank else 0),process.stderr
        info = json.loads((out/'metadata.json').read_text())
        arrays = read_artifacts(out,info)
        detection = json.loads((out/info['detection_metadata_file']).read_text())
        read_artifacts(out/'detection',detection)
        assert detection['run_id']==info['run_id'] and detection['source']==info['source']
        assert info['requested_config']['corners'] is None and info['effective_config']['confirmed'] is False
        if blank:
            assert 'full' not in arrays and info['histogram'] is None
        else:
            assert info['histogram']['counts']==np.bincount(arrays['prepared_gray'].ravel(),minlength=256).tolist()
        infos.append(info)
        detections.append(detection)
    first,second = infos
    assert first['run_id']!=second['run_id']
    for key in ('pipeline_version','environment','source','input','requested_config','effective_config',
                'inactive_fields','otsu_threshold','histogram','homography_source_to_warp','status',
                'corners_origin','detection_status','warnings','artifacts','config_sha256'):
        assert first[key]==second[key],key
    for key in ('algorithm_version','preset','source','analysis_size','overlay_kind','config','units',
                'result','selected_trial','trials','artifacts'):
        assert detections[0][key]==detections[1][key],key
    assert input_file.read_bytes()==original
