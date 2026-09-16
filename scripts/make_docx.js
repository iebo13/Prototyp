// Word deliverables for the AV brand kit:
//   Briefpapier_Vorlage.docx   -> converted to .dotx by scripts/office_templates.py
//   Rechnungsvorlage.docx      -> A4 invoice on the same letterhead
//
// Client data in CLAUDE.md is unfilled, so every legal field is left as its literal
// [PLACEHOLDER]. Nothing here is invented.
const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell,
  WidthType, AlignmentType, BorderStyle, ShadingType, Header, Footer,
} = require('docx');

const ROOT = path.resolve(__dirname, '..');
const KIT = path.join(ROOT, 'AV-Brand-Kit');
const TOK = JSON.parse(fs.readFileSync(path.join(KIT, '00_Master/tokens.json'), 'utf8'));
const C = Object.fromEntries(
  Object.entries(TOK.colors).map(([k, v]) => [k, v.hex.replace('#', '')]));

const MM = 56.6929;                 // DXA per millimetre (1440 per inch)
const mm = (v) => Math.round(v * MM);

const CLIENT = {
  company: 'Auguste Viktoria Immobilien [RECHTSFORM]',
  street: '[STRASSE NR]',
  city: '[PLZ ORT]',
  phone: '[+49 ...]',
  email: '[info@...]',
  web: '[www....de]',
  gf: '[NAME]',
  registergericht: '[AMTSGERICHT ... HRB ...]',
  ust: '[DE...]',
  gewo: 'Erlaubnis nach §34c GewO, erteilt durch [BEHÖRDE, ORT]',
};

const FONT = 'Montserrat';

function logoHeader() {
  // Header logo: PNG at 3000 px scaled to 45 mm wide, as SKILL section 8 prescribes.
  const png = fs.readFileSync(
    path.join(KIT, '01_Logo/PNG/AV_horizontal_full-light_3000px.png'));
  // the horizontal layout's aspect, read from its viewBox
  const svg = fs.readFileSync(
    path.join(KIT, '01_Logo/SVG/AV_horizontal_full-light.svg'), 'utf8');
  const vb = svg.match(/viewBox="([-\d.]+) ([-\d.]+) ([-\d.]+) ([-\d.]+)"/);
  const ratio = parseFloat(vb[4]) / parseFloat(vb[3]);
  const wMm = 45, hMm = wMm * ratio;
  return new Header({
    children: [
      new Paragraph({
        children: [new ImageRun({
          type: 'png', data: png,
          transformation: { width: Math.round(wMm * 3.7795),
                            height: Math.round(hMm * 3.7795) },
        })],
      }),
    ],
  });
}

function legalFooter() {
  const line = (text, bold = false) => new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 0, line: 200 },
    children: [new TextRun({ text, font: FONT, size: 14, color: '5A6A60', bold })],
  });
  return new Footer({
    children: [
      new Paragraph({
        border: { top: { style: BorderStyle.SINGLE, size: 4, color: C.gold, space: 6 } },
        spacing: { after: 90 },
        children: [new TextRun({ text: '', font: FONT, size: 2 })],
      }),
      line(`${CLIENT.company} · ${CLIENT.street} · ${CLIENT.city}`),
      line(`Geschäftsführer: ${CLIENT.gf} · Registergericht: `
           + `${CLIENT.registergericht} · USt-IdNr.: ${CLIENT.ust}`),
      line(CLIENT.gewo),
      line(`T ${CLIENT.phone} · ${CLIENT.email} · ${CLIENT.web}`),
    ],
  });
}

const PAGE = {
  margin: { top: mm(34), right: mm(20), bottom: mm(30), left: mm(20),
            header: mm(12), footer: mm(10) },
};

function body(text, opts = {}) {
  return new Paragraph({
    spacing: { after: 140, line: 300 },
    alignment: opts.align || AlignmentType.LEFT,
    children: [new TextRun({
      text, font: FONT, size: opts.size || 20,
      color: opts.color || C.green, bold: !!opts.bold,
    })],
  });
}

function heading(text) {
  return new Paragraph({
    spacing: { before: 200, after: 180 },
    children: [new TextRun({
      text, font: 'Cinzel', size: 30, color: C.green, bold: true,
    })],
  });
}

// ------------------------------------------------------------------ letterhead
function letterhead() {
  return new Document({
    creator: 'Auguste Viktoria Immobilien',
    title: 'Briefpapier Auguste Viktoria Immobilien',
    description: 'Letterhead template. Replace every [PLACEHOLDER] before use.',
    styles: { default: { document: { run: { font: FONT, size: 20, color: C.green } } } },
    sections: [{
      properties: { page: PAGE },
      headers: { default: logoHeader() },
      footers: { default: legalFooter() },
      children: [
        new Paragraph({
          alignment: AlignmentType.RIGHT,
          spacing: { after: 320 },
          children: [new TextRun({
            text: `${CLIENT.street} · ${CLIENT.city} · T ${CLIENT.phone}`,
            font: FONT, size: 16, color: '4A5A50',
          })],
        }),
        body('[EMPFÄNGER NAME]'),
        body('[EMPFÄNGER STRASSE]'),
        body('[EMPFÄNGER PLZ ORT]'),
        new Paragraph({ spacing: { after: 400 }, children: [] }),
        new Paragraph({
          alignment: AlignmentType.RIGHT,
          spacing: { after: 320 },
          children: [new TextRun({ text: '[ORT], [DATUM]', font: FONT, size: 18,
                                   color: '4A5A50' })],
        }),
        heading('[BETREFF]'),
        body('Sehr geehrte Damen und Herren,'),
        body('[TEXT]'),
        new Paragraph({ spacing: { after: 400 }, children: [] }),
        body('Mit freundlichen Grüßen'),
        new Paragraph({ spacing: { after: 560 }, children: [] }),
        body(CLIENT.gf, { bold: true }),
        body('[POSITION]', { size: 18, color: '6B7A70' }),
      ],
    }],
  });
}

// --------------------------------------------------------------------- invoice
function cell(text, opts = {}) {
  return new TableCell({
    width: { size: opts.w, type: WidthType.DXA },
    shading: opts.shade
      ? { type: ShadingType.CLEAR, fill: opts.shade, color: 'auto' } : undefined,
    margins: { top: 90, bottom: 90, left: 110, right: 110 },
    borders: {
      top: { style: BorderStyle.SINGLE, size: 2, color: 'D8DEDA' },
      bottom: { style: BorderStyle.SINGLE, size: 2, color: 'D8DEDA' },
      left: { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' },
      right: { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' },
    },
    children: [new Paragraph({
      alignment: opts.align || AlignmentType.LEFT,
      children: [new TextRun({
        text, font: FONT, size: opts.size || 18,
        color: opts.color || C.green, bold: !!opts.bold,
      })],
    })],
  });
}

function invoice() {
  const W = [mm(18), mm(82), mm(20), mm(30), mm(20)];
  const total = W.reduce((a, b) => a + b, 0);
  const head = new TableRow({
    children: [
      cell('Pos.', { w: W[0], bold: true, color: 'FFFFFF', shade: C.green }),
      cell('Leistung', { w: W[1], bold: true, color: 'FFFFFF', shade: C.green }),
      cell('Menge', { w: W[2], bold: true, color: 'FFFFFF', shade: C.green,
                      align: AlignmentType.RIGHT }),
      cell('Einzelpreis', { w: W[3], bold: true, color: 'FFFFFF', shade: C.green,
                            align: AlignmentType.RIGHT }),
      cell('Betrag', { w: W[4], bold: true, color: 'FFFFFF', shade: C.green,
                       align: AlignmentType.RIGHT }),
    ],
  });
  const rows = [1, 2, 3].map((i) => new TableRow({
    children: [
      cell(String(i), { w: W[0] }),
      cell('[LEISTUNG]', { w: W[1] }),
      cell('[MENGE]', { w: W[2], align: AlignmentType.RIGHT }),
      cell('[PREIS]', { w: W[3], align: AlignmentType.RIGHT }),
      cell('[BETRAG]', { w: W[4], align: AlignmentType.RIGHT }),
    ],
  }));
  const sum = (label, value, bold = false, shade = undefined) => new TableRow({
    children: [
      cell('', { w: W[0] + W[1] + W[2] }),
      cell(label, { w: W[3], bold, align: AlignmentType.RIGHT, shade }),
      cell(value, { w: W[4], bold, align: AlignmentType.RIGHT, shade }),
    ],
  });

  return new Document({
    creator: 'Auguste Viktoria Immobilien',
    title: 'Rechnungsvorlage Auguste Viktoria Immobilien',
    description: 'Invoice template. Replace every [PLACEHOLDER] before use.',
    styles: { default: { document: { run: { font: FONT, size: 20, color: C.green } } } },
    sections: [{
      properties: { page: PAGE },
      headers: { default: logoHeader() },
      footers: { default: legalFooter() },
      children: [
        new Paragraph({
          alignment: AlignmentType.RIGHT,
          spacing: { after: 280 },
          children: [new TextRun({
            text: `${CLIENT.street} · ${CLIENT.city} · T ${CLIENT.phone}`,
            font: FONT, size: 16, color: '4A5A50',
          })],
        }),
        body('[KUNDE NAME]'),
        body('[KUNDE STRASSE]'),
        body('[KUNDE PLZ ORT]'),
        new Paragraph({ spacing: { after: 320 }, children: [] }),
        heading('Rechnung [RECHNUNGSNUMMER]'),
        new Paragraph({
          spacing: { after: 300 },
          children: [new TextRun({
            text: `Rechnungsdatum: [DATUM]    ·    Leistungszeitraum: [ZEITRAUM]`
                  + `    ·    Kundennummer: [KUNDENNUMMER]`,
            font: FONT, size: 17, color: '4A5A50',
          })],
        }),
        new Table({ columnWidths: W, width: { size: total, type: WidthType.DXA },
                    rows: [head, ...rows,
                           sum('Netto', '[NETTO]'),
                           sum('zzgl. 19 % MwSt.', '[MWST]'),
                           sum('Brutto', '[BRUTTO]', true, 'EFEAE0')] }),
        new Paragraph({ spacing: { before: 340, after: 140 }, children: [] }),
        body('Zahlbar ohne Abzug innerhalb von [X] Tagen auf das unten genannte Konto.',
             { size: 18 }),
        body('IBAN [DE.. .... .... .... .... ..]  ·  BIC [........]  '
             + '·  Bank [BANKNAME]', { size: 18, color: '4A5A50' }),
      ],
    }],
  });
}

async function write(doc, name) {
  const out = path.join(KIT, '05_Templates', name);
  fs.mkdirSync(path.dirname(out), { recursive: true });
  fs.writeFileSync(out, await Packer.toBuffer(doc));
  console.log(`  ${name}  ${Math.round(fs.statSync(out).size / 1024)} KB`);
}

(async () => {
  await write(letterhead(), 'Briefpapier_Vorlage.docx');
  await write(invoice(), 'Rechnungsvorlage.docx');
})();
