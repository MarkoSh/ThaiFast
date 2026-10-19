// Prints every Thai string the page can speak, as JSON {m: [...], f: [...]}.
// Usage: node tools/texts.js > texts.json
const src = require('fs').readFileSync(__dirname + '/../index.html', 'utf8');
const js = src.slice(src.indexOf('/* ================= PHRASES'), src.indexOf('/* ================= STATE'));
const out = new Function(js + `
  const res = { m: new Set(), f: new Set() };
  const both = x => { res.m.add(x); res.f.add(x) };
  for (const g of ['m', 'f']) {
    const P = PARTICLE[g], R = PRONOUN[g];
    PH.forEach(x => res[g].add(x.th + (x.np ? '' : P.th)));
    VERB.forEach(v => MODALS.forEach(m => res[g].add(R.th + m.th + v.th)));
  }
  SOUNDS.forEach(x => both(x.th)); TONES.forEach(x => both(x.th)); both('ไม้ใหม่ไม่ไหม้ไหม');
  CONS.forEach(c => both(c.ch + ' ' + c.word)); VOWELS.forEach(v => both(v[0]));
  VOWELS32.forEach(v => both(VSAY[v[0]] || v[0])); TONEMARKS.forEach(m => both(m[1]));
  NUM.forEach(x => both(x.th)); BODY.forEach(x => { both(x.th); if (!x.noPain) both('ปวด' + x.th) });
  VERB.forEach(x => both(x.th)); TOPV.forEach(x => { both(x.th); both(x.xth) });
  for (let n = 0; n < 100000; n++) thaiNum(n).parts.forEach(both);
  return { m: [...res.m], f: [...res.f] };
`)();
console.log(JSON.stringify(out));
