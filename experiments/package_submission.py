"""Build a source-only submission ZIP from an explicit public-file allowlist."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
NUMERIC_RESULTS = [
    'experiments/results/mvp13-03-04-verified/final/results.csv',
    'experiments/results/mvp13-05-06-verified/enhancement/results.csv',
    'experiments/results/mvp13-07-08-verified/final/accuracy.csv',
    'experiments/results/mvp13-07-08-verified/final/samples.csv',
    'experiments/results/mvp13-07-08-verified/final/summary.json',
]


def package(output: Path) -> dict:
    names = {'README.md', 'AGENTS.md', '.gitignore', 'SUBMISSION.md',
             'Document_Scanner_Dac_Ta_Kien_Truc_Thuat_Toan.md',
             'Document_Scanner_Ke_Hoach_Trien_Khai_Chi_Tiet.md',
             'backend/requirements.txt', 'backend/pyproject.toml',
             'frontend/package.json', 'frontend/package-lock.json', 'frontend/index.html',
             'frontend/vite.config.ts', 'frontend/tsconfig.json',
             'experiments/dataset_manifest.csv', 'experiments/annotations.json'}
    for folder, extensions in [
        ('backend/app', {'.py'}), ('backend/tests', {'.py'}),
        ('frontend/src', {'.ts', '.tsx', '.mjs', '.css'}), ('experiments/tests', {'.py'}),
        ('experiments/configs', {'.json'}), ('fixtures', {'.png', '.jpg', '.bmp', '.json', '.md'}),
        ('docs/images/report', {'.png'}), ('docs/images/user-guide', {'.png'}),
        ('docs/images/demo', {'.png'}),
    ]:
        names.update(p.relative_to(ROOT).as_posix() for p in (ROOT / folder).rglob('*')
                     if p.is_file() and p.suffix in extensions and '__pycache__' not in p.parts)
    for folder, pattern in [('docs', '*.md'), ('tasks', '*.md'), ('experiments', '*.py')]:
        names.update(p.relative_to(ROOT).as_posix() for p in (ROOT / folder).glob(pattern))
    names.update(name for name in NUMERIC_RESULTS if (ROOT / name).is_file())
    if (ROOT / 'docs/submission-verification.json').exists():
        names.add('docs/submission-verification.json')
    payloads = {}
    for name in sorted(names):
        path = ROOT / name
        if path.is_symlink() or not path.resolve().is_relative_to(ROOT.resolve()):
            raise ValueError('Source must be a regular workspace file: ' + name)
        payloads[name] = path.read_bytes()
    manifest = {'version':'mvp14-submission-v1', 'archive_root':'DocumentScanner',
                'files':{n:{'bytes':len(b), 'sha256':sha256(b).hexdigest()} for n,b in payloads.items()},
                'policy':'Allowlisted source, docs, synthetic fixtures and numeric results only; no private photos, DB, credentials, dependencies, build or runtime artifacts.',
                'missing_optional_numeric_results':[n for n in NUMERIC_RESULTS if n not in names]}
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, 'x', compression=ZIP_DEFLATED) as archive:
        for name, payload in payloads.items():
            archive.writestr('DocumentScanner/' + name, payload)
        archive.writestr('DocumentScanner/SUBMISSION-MANIFEST.json', json.dumps(manifest, indent=2) + '\n')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='New ZIP path; never overwrites an existing file.')
    args = parser.parse_args()
    value = package(args.output)
    print(json.dumps({'files':len(value['files']), 'zip_sha256':sha256(args.output.read_bytes()).hexdigest(),
                      'missing_optional_numeric_results':value['missing_optional_numeric_results']}))
