import os
import sys
from pathlib import Path

print('Python:', sys.executable)

venv_site = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.venv') / 'Lib' / 'site-packages'
print('Checking site-packages:', venv_site)

broken = []
for p in venv_site.glob('*.dist-info'):
    ep = p / 'entry_points.txt'
    try:
        if ep.exists():
            with ep.open('r', encoding='utf-8') as f:
                data = f.read()
            print('OK:', p.name, 'size=', len(data))
        else:
            print('NO ENTRY_POINTS:', p.name)
    except Exception as e:
        print('ERROR reading', ep, '->', repr(e))
        broken.append((str(ep), repr(e)))

print('\nBroken count:', len(broken))
for ep, err in broken:
    print(ep, err)
