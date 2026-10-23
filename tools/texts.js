// Prints every Thai string the page can speak, as JSON {m: [...], f: [...]}.
// Usage: node tools/texts.js > texts.json
const src = require('fs').readFileSync(__dirname + '/../index.html', 'utf8');
const js = src.slice(src.indexOf('/* ================= PHRASES'), src.indexOf('/* ================= STATE'));
const out = new Function('let gender;\n' + js + `
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
  // lines spoken by Thais — fixed speaker voice
  ANS.forEach(x => res[x.v].add(x.th));
  SCENES.forEach(sc => sc.steps.forEach(st => res[st.them.v].add(st.them.th)));
  both('ไหว้'); res.m.add(POLITE_YES.m.th); res.f.add(POLITE_YES.f.th);
  ADDR.forEach(x => both(x.th)); QWORDS.concat(QPARTS).forEach(x => both(x.th));
  CLS.forEach(x => both(x.th)); FOOD.forEach(g => g.items.forEach(x => both(x.th))); SIGNS.forEach(x => both(x.th));
  for (const g of ['m', 'f']) {
    const P = PARTICLE[g].th;
    SCENES.forEach(sc => sc.steps.forEach(st => st.you.forEach(o => res[g].add(o.th + P))));
    ADDR.filter(x => x.th !== 'คุณ').forEach(x => res[g].add(x.th + P));
    SMILE.forEach(x => res[g].add(x.th + P));
    QWORDS.concat(QPARTS).forEach(x => res[g].add(x.xth + P));
    ORDER.forEach(it => ORDER_N.forEach(([n]) => res[g].add(orderPhrase(it, n).th + P)));
  }
  for (const g of ['m', 'f']) { gender = g; SENT_TYPES.forEach(t => SENT_BASES.forEach((_, b) => res[g].add(sentText(t.k, b)))) }
  return { m: [...res.m], f: [...res.f] };
`)();
// Thai words inside notes and tips (tappable on the page, see sayThai)
const ui = src.slice(src.indexOf('/* ================= UI TEXT'), src.indexOf('/* ================= STATE'));
for (const [q] of ui.matchAll(/'(?:[^'\\\n]|\\.)*'/g))
  if (/[a-zA-Zа-яА-ЯёЁ]/.test(q)) (q.match(/[\u0E00-\u0E7F]+(?: [\u0E00-\u0E7F]+)*/g) || []).forEach(x => { out.m.includes(x) || out.m.push(x); out.f.includes(x) || out.f.push(x) });
console.log(JSON.stringify(out));
