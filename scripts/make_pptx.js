// PowerPoint master for the AV brand kit: a 16:9 deck with a title slide on green
// and a content slide on cream, converted to .potx by scripts/office_templates.py.
const fs = require('fs');
const path = require('path');
const pptxgen = require('pptxgenjs');

const ROOT = path.resolve(__dirname, '..');
const KIT = path.join(ROOT, 'AV-Brand-Kit');
const TOK = JSON.parse(fs.readFileSync(path.join(KIT, '00_Master/tokens.json'), 'utf8'));
const C = Object.fromEntries(
  Object.entries(TOK.colors).map(([k, v]) => [k, v.hex.replace('#', '')]));

const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE';              // 13.3 x 7.5 in — set before any slide
pres.author = 'Auguste Viktoria Immobilien';
pres.company = 'Auguste Viktoria Immobilien';
pres.title = 'Auguste Viktoria Immobilien — Präsentationsvorlage';

const W = 13.3, H = 7.5;
const b64 = (p) => fs.readFileSync(p).toString('base64');
const stackedCream = 'image/png;base64,'
  + b64(path.join(KIT, '01_Logo/PNG/AV_stacked_1c-cream_3000px.png'));
const horizLight = 'image/png;base64,'
  + b64(path.join(KIT, '01_Logo/PNG/AV_horizontal_full-light_3000px.png'));
const monoGold = 'image/png;base64,'
  + b64(path.join(KIT, '01_Logo/PNG/AV_monogram_simple_1c-gold_3000px.png'));

function aspect(stem) {
  const svg = fs.readFileSync(path.join(KIT, `01_Logo/SVG/${stem}.svg`), 'utf8');
  const vb = svg.match(/viewBox="([-\d.]+) ([-\d.]+) ([-\d.]+) ([-\d.]+)"/);
  return parseFloat(vb[4]) / parseFloat(vb[3]);
}

// ---------------------------------------------------------------- slide masters
pres.defineSlideMaster({
  title: 'AV_TITLE',
  background: { color: C.green },
  objects: [
    { image: { x: (W - 4.6) / 2, y: 1.45, w: 4.6,
               h: 4.6 * aspect('AV_stacked_1c-cream'), data: stackedCream } },
    { line: { x: W / 2 - 1.1, y: 5.34, w: 2.2, h: 0,
              line: { color: C.gold, width: 1 } } },
    { text: {
        text: 'MEHR ALS NUR EIN ZUHAUSE',
        options: { x: 0, y: 5.52, w: W, h: 0.4, align: 'center', isTextBox: true,
                   fontFace: 'Montserrat', fontSize: 11, color: C.gold,
                   charSpacing: 4, margin: 0 },
    } },
    { placeholder: {
        options: { name: 'title', type: 'title', x: 1.0, y: 6.05, w: W - 2.0, h: 0.7,
                   align: 'center', fontFace: 'Cinzel', fontSize: 26, color: C.cream },
        text: '[TITEL DER PRÄSENTATION]',
    } },
  ],
});

pres.defineSlideMaster({
  title: 'AV_CONTENT',
  background: { color: C.cream },
  objects: [
    { image: { x: 0.62, y: 0.42, w: 2.15,
               h: 2.15 * aspect('AV_horizontal_full-light'), data: horizLight } },
    { line: { x: 0.62, y: 1.24, w: W - 1.24, h: 0,
              line: { color: C.gold, width: 0.75 } } },
    { placeholder: {
        options: { name: 'title', type: 'title', x: 0.62, y: 1.48, w: W - 1.24,
                   h: 0.8, fontFace: 'Cinzel', fontSize: 24, color: C.green,
                   margin: 0 },
        text: '[ABSCHNITTSÜBERSCHRIFT]',
    } },
    { placeholder: {
        options: { name: 'body', type: 'body', x: 0.62, y: 2.42, w: W - 1.24,
                   h: 4.1, fontFace: 'Montserrat', fontSize: 15, color: C.green,
                   margin: 0 },
        text: '[INHALT]',
    } },
    { image: { x: W - 1.05, y: H - 0.86, w: 0.42,
               h: 0.42 * aspect('AV_monogram_simple_1c-gold'), data: monoGold } },
    { text: {
        text: 'Auguste Viktoria Immobilien',
        options: { x: 0.62, y: H - 0.72, w: 5.0, h: 0.3, isTextBox: true,
                   fontFace: 'Montserrat', fontSize: 9, color: '6B7A70',
                   charSpacing: 1.2, margin: 0 },
    } },
    { placeholder: {
        options: { name: 'slideNumber', type: 'sldNum', x: W - 1.9, y: H - 0.72,
                   w: 0.7, h: 0.3, align: 'right', fontFace: 'Montserrat',
                   fontSize: 9, color: '6B7A70' },
    } },
  ],
});

// Two example slides so the template opens with something to look at.
pres.addSlide({ masterName: 'AV_TITLE' });

const s2 = pres.addSlide({ masterName: 'AV_CONTENT' });
s2.addText('[ABSCHNITTSÜBERSCHRIFT]', {
  x: 0.62, y: 1.48, w: W - 1.24, h: 0.8, isTextBox: true,
  fontFace: 'Cinzel', fontSize: 24, color: C.green, margin: 0,
});
s2.addText(
  [
    { text: '[Erster Punkt]', options: { bullet: true, breakLine: true } },
    { text: '[Zweiter Punkt]', options: { bullet: true, breakLine: true } },
    { text: '[Dritter Punkt]', options: { bullet: true } },
  ],
  { x: 0.62, y: 2.42, w: W - 1.24, h: 4.1, isTextBox: true,
    fontFace: 'Montserrat', fontSize: 15, color: C.green,
    paraSpaceAfter: 10, margin: 0 });
s2.addNotes('Replace every [PLACEHOLDER]. Body copy is Montserrat, headings Cinzel.');

const out = path.join(KIT, '05_Templates/Praesentation_Vorlage.pptx');
fs.mkdirSync(path.dirname(out), { recursive: true });
pres.writeFile({ fileName: out }).then(() => {
  console.log(`  Praesentation_Vorlage.pptx  ${Math.round(fs.statSync(out).size / 1024)} KB`);
});
