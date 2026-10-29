"""Offline support for a *Fast site: writes offline.json (every file the site needs, with a content hash,
plus the CDN scripts and stylesheets index.html loads) and copies tools/sw.js next to index.html.

Usage: python3 tools/offline.py <site dir>   — run by the pre-commit hook of every *Fast repo."""
import hashlib, json, os, re, shutil, sys

root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.')
SKIP_DIRS = {'tools', 'node_modules'}
SKIP_FILES = re.compile(r'(^|/)(offline\.json|sw\.js|.*\.(md|py|har|txt|log))$|(^|/)DeepSeek', re.I)

files = {}
for d, dirs, names in os.walk(root):
    dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS and not x.startswith('.') and not x.endswith('_files'))
    for n in sorted(names):
        rel = os.path.relpath(os.path.join(d, n), root).replace(os.sep, '/')
        if n.startswith('.') or SKIP_FILES.search(rel):
            continue
        with open(os.path.join(d, n), 'rb') as f:
            files[rel] = hashlib.sha1(f.read()).hexdigest()[:12]

html = open(os.path.join(root, 'index.html'), encoding='utf8').read()
external = set(re.findall(r'<script\b[^>]*\bsrc="(https://[^"]+)"', html))
for tag in re.findall(r'<link\b[^>]*>', html):
    m = re.search(r'\bhref="(https://[^"]+)"', tag)
    if m and re.search(r'\brel="stylesheet"', tag):
        external.add(m.group(1))
external = sorted(u for u in external if not re.search(r'googletagmanager|google-analytics', u))

core = ['index.html'] + [p for p in files if re.match(r'(favicon|apple-touch-icon)', p)]
version = hashlib.sha1(json.dumps([files, external], sort_keys=True).encode()).hexdigest()[:12]
with open(os.path.join(root, 'offline.json'), 'w') as f:
    json.dump({'version': version, 'core': core, 'external': external, 'files': files}, f, separators=(',', ':'), sort_keys=True)

here = os.path.dirname(os.path.abspath(__file__))
if os.path.abspath(os.path.join(here, 'sw.js')) != os.path.join(root, 'sw.js'):
    shutil.copyfile(os.path.join(here, 'sw.js'), os.path.join(root, 'sw.js'))
print(f'offline.json: {len(files)} files, {len(external)} external, version {version}')
