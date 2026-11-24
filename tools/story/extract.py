"""Story trainer, step 1: read STORIES from index.html, split every paragraph into
clean text (the Thai inserts replaced by their meaning, as in the original) + the curated inserts.
Writes tools/story/clean.json: {"paras": [{"ru": str, "en": str, "ins_ru": [[surface, th, roman]], "ins_en": [...]}]}"""
import json, os, re, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
src = open(os.path.join(ROOT, 'index.html'), encoding='utf8').read()
a = src.index('const STORIES'); b = src.index('/* ================= ', a + 20)
js = 'const STORIES' + src[a + len('const STORIES'):b]
out = subprocess.run(['node', '-e', js + ';console.log(JSON.stringify(STORIES[0]))'], capture_output=True, text=True, check=True).stdout
story = json.loads(out)
INS = re.compile(r'([฀-๿][฀-๿!?]*) \(([^,()]+), ([^()]+)\)')
def clean(t):
    ins = []
    def rep(m):
        ins.append([m[3], m[1].rstrip('!?'), m[2]]); return m[3]
    return INS.sub(rep, t), ins
paras = []
for ru, en in story['paras']:
    r, ir = clean(ru); e, ie = clean(en)
    paras.append({'ru': r, 'en': e, 'ins_ru': ir, 'ins_en': ie})
json.dump({'meta': {k: story[k] for k in ('id', 'year', 'author', 'title')}, 'paras': paras}, open(os.path.join(HERE, 'clean.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
left = [p for p in paras if re.search(r'[฀-๿]', p['ru'] + p['en'])]
print(len(paras), 'paragraphs;', sum(len(p['ins_ru']) for p in paras), 'ru inserts,', sum(len(p['ins_en']) for p in paras), 'en inserts; leftover thai:', len(left))
