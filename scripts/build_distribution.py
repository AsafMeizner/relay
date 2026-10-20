"""Create an offline runnable source distribution from committed, allowlisted files."""
import hashlib
import io
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def build():
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip():
        raise SystemExit('Commit or remove working changes before building a distribution')
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    files = sorted(name for name in tracked if name and (
        name in {'README.md', 'LICENSE'} or name.startswith(('relay/', 'docs/', 'scripts/', 'tests/'))
    ) and '__pycache__' not in name and not name.endswith('.pyc'))
    output = ROOT / 'dist'
    output.mkdir(exist_ok=True)
    archive = output / ('relay-' + revision[:12] + '.zip')
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as bundle:
        for name in files:
            data = subprocess.check_output(['git', 'show', revision + ':' + name], cwd=ROOT)
            info = zipfile.ZipInfo('relay/' + name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            bundle.writestr(info, data)
        info = zipfile.ZipInfo('relay/BUILD.txt', date_time=(2026, 1, 1, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        bundle.writestr(info, 'Source commit: ' + revision + '\nOffline default; no provider credentials included.\n')
    archive.write_bytes(buffer.getvalue())
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    archive.with_suffix('.zip.sha256').write_text(digest + '  ' + archive.name + '\n')
    print(str(archive))
    print('SHA256 ' + digest)
    print(str(len(files)) + ' committed source/documentation files')


if __name__ == '__main__':
    build()
