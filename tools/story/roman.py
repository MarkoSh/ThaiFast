"""Thai word -> ThaiFast-style romanization with tone marks (jàk-grà-waan), from tltk's IPA with tone digits
(1 mid, 2 low, 3 falling, 4 high, 5 rising). Used by build.py; override single words in lexicon.tsv column 4."""
import re
from tltk.nlp import th2ipa

ONSET = {'kʰ': 'kh', 'k': 'g', 'cʰ': 'ch', 'c': 'j', 'tʰ': 'th', 't': 'dt', 'pʰ': 'ph', 'p': 'bp', 'b': 'b', 'd': 'd', 'f': 'f',
         's': 's', 'h': 'h', 'm': 'm', 'n': 'n', 'ŋ': 'ng', 'l': 'l', 'r': 'r', 'j': 'y', 'w': 'w', 'ʔ': ''}
# vowel nuclei, longest first (the part between onset and final consonant)
NUCLEUS = [('iːa', 'ia'), ('ɯːa', 'uea'), ('uːa', 'ua'), ('aːj', 'aai'), ('aːw', 'aao'), ('ɛːw', 'aeo'), ('eːw', 'eeo'), ('ɔːj', 'oi'),
           ('ᴐːj', 'oi'), ('ɤːj', 'oei'), ('oːj', 'ohi'), ('iːw', 'iao'), ('aj', 'ai'), ('aw', 'ao'), ('uj', 'ui'), ('iw', 'io'), ('ew', 'eo'),
           ('ɛw', 'aeo'), ('ᴐj', 'oi'), ('ɔj', 'oi'), ('ɤj', 'oei'), ('ɯː', 'ue'), ('ɯ', 'ue'), ('aː', 'aa'), ('iː', 'ii'), ('uː', 'uu'),
           ('eː', 'ee'), ('ɛː', 'ae'), ('oː', 'oh'), ('ɔː', 'or'), ('ᴐː', 'or'), ('ɤː', 'oe'), ('ɤ', 'oe'), ('ɛ', 'ae'), ('ɔ', 'o'), ('ᴐ', 'o'),
           ('a', 'a'), ('i', 'i'), ('u', 'u'), ('e', 'e'), ('o', 'o')]
FINAL = {'p': 'p', 't': 't', 'k': 'k', 'm': 'm', 'n': 'n', 'ŋ': 'ng', 'ʔ': ''}
MARK = {'2': '̀', '3': '̂', '4': '́', '5': '̌'}
ON = sorted(ONSET, key=lambda s: -len(s))

VOWELS = 'aeiouɛɤɯɔᴐ'

def syllable(s):
    tone = s[-1] if s[-1].isdigit() else '1'
    s = s.rstrip('0123456789')
    i = next((k for k, ch in enumerate(s) if ch in VOWELS), len(s))
    head, s = s[:i], s[i:]
    onset = ''
    while head:                                  # onset (maybe a cluster: kʰw, pr, kl ...)
        o = next((o for o in ON if head.startswith(o)), None)
        if o is None:
            onset += head; break
        onset += ONSET[o]; head = head[len(o):]
    nuc = next(((n, l) for n, l in NUCLEUS if s.startswith(n)), None)
    if not nuc:
        return onset + s
    rest = s[len(nuc[0]):]
    coda = ''.join(FINAL.get(ch, ch) for ch in rest)
    body = nuc[1]
    if body == 'or' and coda:                    # the site writes ɔɔ before a final consonant (rɔ́ɔn) and or in an open syllable (khǒr)
        body = 'ɔɔ'
    if tone in MARK:                             # the mark sits on the first vowel letter
        k = next((k for k, ch in enumerate(body) if ch in 'aeiouɔ'), 0)
        body = body[:k + 1] + MARK[tone] + body[k + 1:]
    return onset + body + coda

def roman(th):
    from tltk.nlp import word_segment
    out = []
    for w in [x for x in word_segment(th).replace('<s/>', '').split('|') if x.strip()]:
        ipa = th2ipa(w).replace('<s/>', '').strip()
        out.append('-'.join(syllable(s) for s in re.split(r'[.~ ]+', ipa) if s))
    words = []
    for w, t in zip(out, [x for x in word_segment(th).replace('<s/>', '').split('|') if x.strip()]):
        if words and words[-1][1] in ('ความ', 'การ'):          # khwaam-ngîap, gaan-...: the prefix is joined to its word
            words[-1] = (words[-1][0] + '-' + w, t)
        else:
            words.append((w, t))
    return ' '.join(w for w, _ in words)

if __name__ == '__main__':
    import sys
    for w in sys.argv[1:]:
        print(w, roman(w))
