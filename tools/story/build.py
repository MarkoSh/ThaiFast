"""Story trainer, step 3: clean.json + lexicon.tsv + events.tsv -> ../../story-data.js
Run: ~/.venv/bin/uv run --quiet --no-project --with tltk --with 'numpy<2' --with 'pandas<2.3' --with requests --with nltk \\
       --with python-crfsuite --with scikit-learn --with pymorphy3 --with pymorphy3-dicts-ru --with lemminflect python -W ignore tools/story/build.py
Output: const STORY_DATA = {lex: [[th, roman]], ev: [...], p: [{ru: [seg], en: [seg]}]}
seg: a plain string, or [surface, id, kind]  kind 0 = word of the lexicon (lex[id]), 1 = the hand-made insert of the first version
(lex[id]), 2 = a reordered phrase of mode 3 (ev[id])."""
import collections, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pymorphy3, lemminflect
from roman import roman

WORD = re.compile(r"[A-Za-zА-Яа-яЁё]+(?:[-’'][A-Za-zА-Яа-яЁё]+)*")
morph = pymorphy3.MorphAnalyzer()

def ru_keys(w):
    p = morph.parse(w.lower())[0]
    return [f'{p.normal_form}/{p.tag.POS}', p.normal_form]

def en_keys(w):
    w = w.lower().replace('’', "'")
    base = w.split("'")[0] if "'" in w else w
    got = lemminflect.getAllLemmas(base)
    for up in ('VERB', 'NOUN', 'AUX', 'ADJ', 'ADV'):
        if up in got:
            return [got[up][0], base]
    return [base]
KEYS = {'ru': ru_keys, 'en': en_keys}

cache_path = os.path.join(HERE, 'roman_cache.json')
cache = json.load(open(cache_path, encoding='utf8')) if os.path.exists(cache_path) else {}
def rom(th):
    if th not in cache:
        cache[th] = roman(th)
    return cache[th]

LEX, LEXID = [], {}
def lex_id(th, r=None):
    if (th, r) not in LEXID:
        LEXID[th, r] = len(LEX); LEX.append([th, r or rom(th)])
    return LEXID[th, r]

# lexicon.tsv: th, ru lemmas, en lemmas, roman override
look = {'ru': {}, 'en': {}}
for line in open(os.path.join(HERE, 'lexicon.tsv'), encoding='utf8'):
    if line.startswith('#') or not line.strip():
        continue
    f = (line.rstrip('\n').split('\t') + ['', '', '', ''])[:4]
    th, ru, en, over = [x.strip() for x in f]
    for lang, lemmas in (('ru', ru), ('en', en)):
        for l in [x.strip() for x in lemmas.split(',') if x.strip()]:
            look[lang].setdefault(l, (th, over or None))

clean = json.load(open(os.path.join(HERE, 'clean.json'), encoding='utf8'))
events = []
evp = os.path.join(HERE, 'events.tsv')
if os.path.exists(evp):
    for line in open(evp, encoding='utf8'):
        if line.startswith('#') or not line.strip():
            continue
        f = (line.rstrip('\n').split('\t') + [''] * 9)[:9]
        events.append(dict(zip(['para', 'ru', 'en', 'th', 'lit_ru', 'lit_en', 'why_ru', 'why_en', 'roman'], f)))
EV = []
WHY = {
    'ADJ': ('В тайском определение (прилагательное) ставится после существительного: сначала предмет, потом какой он.',
            'In Thai the describing word comes after the noun: the thing first, then what it is like.'),
    'POSS': ('Принадлежность ставится после вещи: «планета наша», а не «наша планета» (часто со словом ของ — «принадлежащий»).',
             'Ownership goes after the thing: “planet our”, not “our planet” (often with ของ, “belonging to”).'),
    'NUM': ('Число стоит после существительного, вместе со счётным словом (классификатором): «планеты две-штуки».',
            'A number goes after the noun together with a counting word (classifier): “planets two-pieces”.'),
    'ORD': ('Порядковое число: существительное + счётное слово + ที่ + число: «планета-тело-третья».',
            'An ordinal number: noun + counting word + ที่ + number: “planet-body-third”.'),
    'DEM': ('Указательное слово («этот») идёт в конце, после существительного и счётного слова: «планета-тело-эта».',
            'The pointing word (“this”) comes last, after the noun and its counting word: “planet-body-this”.'),
    'NUMDEM': ('Две перестановки сразу: порядковое число идёт после существительного и счётного слова (ที่สาม), а «этот» — в самом конце (นี้).',
               'Two swaps at once: the ordinal follows the noun and its counting word (ที่สาม), and “this” comes last (นี้).'),
}

def spans(text, lang, ins, evs):
    """claimed spans [(start, end, kind, id)]: events first, then the hand-made inserts (found in order), never overlapping"""
    taken = []
    free = lambda a, b: all(b <= s or a >= e for s, e, _, _ in taken)
    for ev in evs:
        sp = ev[lang]
        if not sp:
            continue
        i = text.find(sp)
        if i < 0 or not free(i, i + len(sp)):
            print(f'  event span not found ({lang}): {sp!r}'); continue
        EV.append({'th': ev['th'], 'rom': ev['roman'] or rom(ev['th']), 'lit': [ev['lit_ru'], ev['lit_en']], 'why': list(WHY.get(ev['why_ru'], [ev['why_ru'], ev['why_en']])), 'sp': sp})
        taken.append((i, i + len(sp), 2, len(EV) - 1))
    pos = 0
    for surface, th, r in ins:
        i = text.find(surface, pos)
        if i < 0:
            print(f'  insert not found ({lang}): {surface!r}'); continue
        pos = i + len(surface)
        if free(i, pos):
            taken.append((i, pos, 1, lex_id(th, r)))
    return sorted(taken)

stats = collections.Counter(); missing = {'ru': collections.Counter(), 'en': collections.Counter()}
RU_SKIP = {'наш', 'мой', 'свой', 'твой', 'ваш', 'этот', 'тот', 'такой', 'весь', 'каждый', 'любой', 'другой', 'один', 'самый', 'какой', 'некоторый'}
EN_SKIP = {'my', 'our', 'your', 'his', 'her', 'their', 'its', 'this', 'that', 'these', 'those', 'every', 'each', 'some', 'any', 'all', 'whole', 'two', 'three',
           'the', 'a', 'an', 'such', 'another', 'other', 'more', 'most', 'very', 'one', 'first', 'second', 'third', 'last'}

def safe(lang, prev, w):
    """a single word that can be swapped in place without breaking Thai order: a noun or verb that no adjective, number or pointing word leans on"""
    if lang == 'ru':
        p = morph.parse(w.lower())[0]
        if p.tag.POS not in ('NOUN', 'VERB', 'INFN') or 'Name' in p.tag or 'Surn' in p.tag or p.normal_form in ('быть', 'иметь', 'стать', 'мочь', 'хотеть', 'уметь'):
            return False
        if prev:
            q = morph.parse(prev.lower())[0]
            if q.tag.POS in ('ADJF', 'ADJS', 'PRTF', 'PRTS', 'NUMR', 'COMP') or q.normal_form in RU_SKIP:
                return False
        return True
    got = lemminflect.getAllLemmas(w.lower().replace('’', "'").split("'")[0])
    if not ({'NOUN', 'VERB'} & set(got)) or 'ADJ' in got or got.get('VERB', got.get('AUX', ('',)))[0] in ('be', 'have', 'do', 'can', 'may', 'let', 'get', 'become', 'want'):
        return False
    if prev:
        pw = prev.lower().replace('’', "'").split("'")[0]
        if pw in EN_SKIP or 'ADJ' in lemminflect.getAllLemmas(pw):
            return False
    return True

def segments(text, lang, ins, evs, mode):
    """mode 'a' (modes 0-2: hand-made inserts + every lexicon word) or 'e' (mode 3: reordered phrases + inserts + safe single words)"""
    out, pos = [], 0
    def plain(a, b):
        if b > a:
            if out and isinstance(out[-1], str):
                out[-1] += text[a:b]
            else:
                out.append(text[a:b])
    claimed = spans(text, lang, ins, evs if mode == 'e' else [])
    prev = None
    for m in WORD.finditer(text):
        a, b = m.span()
        c = next((x for x in claimed if x[0] <= a < x[1]), None)
        if c:
            if a == c[0]:
                plain(pos, a); out.append([text[c[0]:c[1]], c[3], c[2]]); pos = c[1]
                if mode == 'a': stats[lang, 'words'] += 1; stats[lang, 'lex'] += 1
            prev = m[0]
            continue
        if mode == 'a': stats[lang, 'words'] += 1
        hit = next((look[lang][k] for k in KEYS[lang](m[0]) if k in look[lang]), None)
        if hit and (mode == 'a' or safe(lang, prev, m[0])):
            plain(pos, a); out.append([m[0], lex_id(*hit), 0]); pos = b
            if mode == 'a': stats[lang, 'lex'] += 1
        elif mode == 'a':
            missing[lang][KEYS[lang](m[0])[-1]] += 1
        prev = m[0]
    plain(pos, len(text))
    return out

paras = []
for i, p in enumerate(clean['paras']):
    evs = [e for e in events if e['para'] == str(i)]
    paras.append({'ru': segments(p['ru'], 'ru', p['ins_ru'], evs, 'a'), 'en': segments(p['en'], 'en', p['ins_en'], evs, 'a'),
                  'ru3': segments(p['ru'], 'ru', p['ins_ru'], evs, 'e'), 'en3': segments(p['en'], 'en', p['ins_en'], evs, 'e')})
for lang in ('ru', 'en'):
    w = stats[lang, 'words']; c = stats[lang, 'lex']
    print(lang, 'words', w, 'replaceable', c, f'{c / w:.0%}')
    print('  top missing:', ', '.join(f'{k}{v if v > 1 else ""}' for k, v in missing[lang].most_common(40)))
json.dump(cache, open(cache_path, 'w', encoding='utf8'), ensure_ascii=False, indent=0)
data = {'lex': LEX, 'ev': EV, 'p': paras}
open(os.path.join(ROOT, 'story-data.js'), 'w', encoding='utf8').write('// written by tools/story/build.py\nconst STORY_DATA = ' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n')
print('lex', len(LEX), 'events', len(EV), 'bytes', os.path.getsize(os.path.join(ROOT, 'story-data.js')))
