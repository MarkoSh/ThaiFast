"""Generate audio/<m|f>/<fnv1a>.mp3 for every string from texts.js.
Needs: pip install edge-tts.  Usage: node tools/texts.js > /tmp/t.json && python tools/gen_audio.py /tmp/t.json
Skips files that already exist, so re-run after adding phrases."""
import asyncio, json, os, re, sys
import edge_tts

VOICES = {'m': 'th-TH-NiwatNeural', 'f': 'th-TH-PremwadeeNeural'}
RATE = '-15%'  # a bit slower for learners
ROOT = os.path.join(os.path.dirname(__file__), '..', 'audio')

# What the voice is given differs from the page text where the engine misreads it:
# ๆ (repeat the word) is spoken as the whole previous phrase (ใจเย็นๆ -> "jai yen jai yen"), so it is written out;
# single digits become words. The file name still comes from the page text.
MAIYAMOK = re.compile(r'(ใจเย็น|เยอะ|ช้า|สู้|ชัด|ดี) ?ๆ')
DIGITS = dict(zip('0123456789', ['ศูนย์', 'หนึ่ง', 'สอง', 'สาม', 'สี่', 'ห้า', 'หก', 'เจ็ด', 'แปด', 'เก้า']))
def tts_text(t):
    out = MAIYAMOK.sub(lambda m: m[1] + ' ' + ('เย็น' if m[1] == 'ใจเย็น' else m[1]) + ' ', t).replace('  ', ' ').strip()
    out = re.sub(r'(?<![0-9])[0-9](?![0-9])', lambda m: DIGITS[m[0]], out)
    if 'ๆ' in out and out != 'ๆ': print('UNHANDLED ๆ:', t)
    return out

def fnv(s):
    h = 0x811c9dc5
    for b in s.encode('utf8'):
        h = ((h ^ b) * 0x01000193) & 0xffffffff
    return f'{h:08x}'

async def main(path):
    texts = json.load(open(path, encoding='utf8'))
    sem = asyncio.Semaphore(8)
    jobs = []
    for g, items in texts.items():
        os.makedirs(os.path.join(ROOT, g), exist_ok=True)
        for t in items:
            out = os.path.join(ROOT, g, fnv(t) + '.mp3')
            if not os.path.exists(out):
                jobs.append((g, t, out))
    print(len(jobs), 'files to generate')

    async def one(g, t, out):
        async with sem:
            for attempt in range(3):
                try:
                    await edge_tts.Communicate(tts_text(t), VOICES[g], rate=RATE).save(out)
                    return
                except Exception as e:
                    if attempt == 2:
                        print('FAIL', g, t, e)
                    await asyncio.sleep(2)
    await asyncio.gather(*(one(*j) for j in jobs))

asyncio.run(main(sys.argv[1]))
