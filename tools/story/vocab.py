"""Story trainer, step 2: list the lemmas of the clean text (ru: pymorphy3, en: lemminflect) with their counts,
marking which ones already have a Thai word in the lexicon (tools/story/lexicon.tsv). Writes vocab_ru.txt / vocab_en.txt (todo only)."""
import collections, json, os, re
import pymorphy3, lemminflect
HERE = os.path.dirname(os.path.abspath(__file__))
morph = pymorphy3.MorphAnalyzer()
clean = json.load(open(os.path.join(HERE, 'clean.json'), encoding='utf8'))
WORD = re.compile(r"[A-Za-zА-Яа-яЁё]+(?:[-’'][A-Za-zА-Яа-яЁё]+)*")

def ru_lemma(w):
    p = morph.parse(w.lower())[0]
    return p.normal_form, str(p.tag.POS)

def en_lemma(w):
    """lemma of an English word form: the dictionary lemma (verb first), else the word itself"""
    w = w.lower().replace('’', "'")
    base = w.split("'")[0] if "'" in w else w
    got = lemminflect.getAllLemmas(base)
    for up in ('VERB', 'NOUN', 'AUX', 'ADJ', 'ADV'):
        if up in got:
            return got[up][0]
    return base

lex = {'ru': {}, 'en': {}}
path = os.path.join(HERE, 'lexicon.tsv')
if os.path.exists(path):
    for line in open(path, encoding='utf8'):
        if line.startswith('#') or not line.strip(): continue
        f = line.rstrip('\n').split('\t')
        for l in (f[1] if len(f) > 1 else '').split(','): lex['ru'][l.strip()] = 1
        for l in (f[2] if len(f) > 2 else '').split(','): lex['en'][l.strip()] = 1
for lang, fn in (('ru', ru_lemma), ('en', en_lemma)):
    cnt = collections.Counter(); pos = {}
    for p in clean['paras']:
        for w in WORD.findall(p[lang]):
            r = fn(w); l = r[0] if isinstance(r, tuple) else r
            cnt[l] += 1; pos[l] = r[1] if isinstance(r, tuple) else ''
    total = sum(cnt.values()); have = sum(c for l, c in cnt.items() if l in lex[lang])
    print(lang, 'tokens', total, 'lemmas', len(cnt), 'covered tokens', have, f'{have / total:.0%}')
    with open(os.path.join(HERE, f'vocab_{lang}.txt'), 'w', encoding='utf8') as f:
        for l, c in cnt.most_common():
            if l not in lex[lang]: f.write(f'{l}\t{pos[l]}\t{c}\n')
