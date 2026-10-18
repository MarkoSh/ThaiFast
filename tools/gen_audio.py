"""Generate audio/<m|f>/<fnv1a>.mp3 for every string from texts.js.
Needs: pip install edge-tts.  Usage: node tools/texts.js > /tmp/t.json && python tools/gen_audio.py /tmp/t.json
Skips files that already exist, so re-run after adding phrases."""
import asyncio, json, os, sys
import edge_tts

VOICES = {'m': 'th-TH-NiwatNeural', 'f': 'th-TH-PremwadeeNeural'}
RATE = '-15%'  # a bit slower for learners
ROOT = os.path.join(os.path.dirname(__file__), '..', 'audio')

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
                    await edge_tts.Communicate(t, VOICES[g], rate=RATE).save(out)
                    return
                except Exception as e:
                    if attempt == 2:
                        print('FAIL', g, t, e)
                    await asyncio.sleep(2)
    await asyncio.gather(*(one(*j) for j in jobs))

asyncio.run(main(sys.argv[1]))
