const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const FA = require("react-icons/fa6");

// ---------- palette (academic) ----------
const INK = "1A2433";     // text / dark slides
const ACCENT = "1F4E79";  // academic deep blue (chrome)
const HI = "C0392B";      // red — marks high-bias bars only (meaningful)
const MID = "9AA5B1";     // gray bars
const MUTED = "667085";
const LIGHT = "F2F4F7";
const DARK = "1A2433";
const W = 13.33, H = 7.5, MX = 0.75;
const F = "Arial";
const ASSET = "/Users/xiaochuan/Desktop/Projects/P5_Multi_linguistic_histoBias/code/experiments/assets";

async function icon(IconComponent, color = "#1F4E79", size = 256) {
  const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(IconComponent, { color, size: String(size) }));
  const png = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + png.toString("base64");
}

(async () => {
  const p = new pptxgen();
  p.layout = "LAYOUT_WIDE";
  p.author = "Xiaochuan Li";
  p.title = "Multilingual Prototypicality Bias in MLLM Judges";

  const ic = {
    paw: await icon(FA.FaPaw, "#1F4E79"),
    cube: await icon(FA.FaCube, "#1F4E79"),
    users: await icon(FA.FaUsers, "#1F4E79"),
    globe: await icon(FA.FaGlobe, "#1F4E79"),
    image: await icon(FA.FaImage, "#1F4E79"),
    scale: await icon(FA.FaScaleBalanced, "#FFFFFF"),
    arrow: await icon(FA.FaArrowRightLong, "#9AA5B1"),
    chart: await icon(FA.FaChartColumn, "#FFFFFF"),
  };

  // assertion-style header: small tag + full-sentence headline
  function head(s, tag, assertion) {
    s.addShape(p.shapes.RECTANGLE, { x: MX, y: 0.5, w: 0.16, h: 0.16, fill: { color: ACCENT } });
    s.addText(tag.toUpperCase(), { x: MX + 0.3, y: 0.4, w: W - 2 * MX, h: 0.3, fontFace: F, fontSize: 11, color: ACCENT, bold: true, charSpacing: 2, margin: 0 });
    s.addText(assertion, { x: MX, y: 0.72, w: W - 2 * MX, h: 1.05, fontFace: F, fontSize: 24, bold: true, color: INK, margin: 0, lineSpacingMultiple: 1.0 });
  }
  function foot(s, n) {
    s.addText("Multilingual Prototypicality Bias  ·  Progress Report I", { x: MX, y: H - 0.4, w: 9, h: 0.3, fontFace: F, fontSize: 9, color: MUTED, margin: 0 });
    s.addText(String(n), { x: W - 1.1, y: H - 0.4, w: 0.5, h: 0.3, fontFace: F, fontSize: 9, color: MUTED, align: "right", margin: 0 });
  }
  function cap(s, x, y, w, text) { // evidence caption (one short line)
    s.addText(text, { x, y, w, h: 0.5, fontFace: F, fontSize: 13, italic: true, color: MUTED, margin: 0, valign: "top" });
  }

  // ============ 1 — TITLE ============
  let s = p.addSlide();
  s.background = { color: DARK };
  s.addShape(p.shapes.RECTANGLE, { x: 0, y: 0, w: 0.22, h: H, fill: { color: ACCENT } });
  s.addText("CROSS-LINGUAL PROTOTYPICALITY BIAS IN MULTIMODAL AI EVALUATION", { x: 1.0, y: 2.1, w: 11.5, h: 0.4, fontFace: F, fontSize: 13, color: "8FA9C4", bold: true, charSpacing: 2, margin: 0 });
  s.addText("Does a vision–language judge change its mind\nwhen we switch the language?", { x: 1.0, y: 2.6, w: 11.5, h: 1.6, fontFace: F, fontSize: 34, bold: true, color: "FFFFFF", margin: 0, lineSpacingMultiple: 1.05 });
  s.addText("English · Chinese · Arabic · Hindi", { x: 1.0, y: 4.4, w: 11, h: 0.5, fontFace: F, fontSize: 17, color: "CFE0F0", margin: 0 });
  s.addText([
    { text: "Progress Report I", options: { bold: true, color: "FFFFFF", breakLine: true } },
    { text: "Xiaochuan Li   ·   Mentor: Subhadeep Roy   ·   2026", options: { color: "8FA9C4" } },
  ], { x: 1.0, y: 5.7, w: 11, h: 1, fontFace: F, fontSize: 13 });

  // ============ 2 — PROBLEM (real figure) ============
  s = p.addSlide(); foot(s, 2);
  head(s, "The problem", "Evaluation metrics can prefer a wrong image just because it looks typical");
  s.addImage({ path: `${ASSET}/protobias_examples.png`, x: MX, y: 2.0, w: 6.9, h: 4.78 });
  cap(s, MX, 6.78, 6.9, "ProtoBias (Roy et al., 2026), Fig. 1 — three domains, each pairing SC vs PA.");
  // right explanation
  s.addText([
    { text: "SC", options: { bold: true, color: ACCENT } }, { text: "  semantically correct, but non-prototypical\n\n", options: { color: INK, breakLine: true } },
    { text: "PA", options: { bold: true, color: HI } }, { text: "  prototypical / stereotypical, but wrong\n\n", options: { color: INK, breakLine: true } },
    { text: "Right column: most metrics (CLIP, Pick, VQA, GPT) rank ", options: { color: MUTED } },
    { text: "PA above SC", options: { color: HI, bold: true } }, { text: " — the failure we study.", options: { color: MUTED } },
  ], { x: 8.1, y: 2.6, w: 4.5, h: 3.5, fontFace: F, fontSize: 16, valign: "top", paraSpaceAfter: 4 });

  // ============ 3 — RQ / TASK ============
  s = p.addSlide(); foot(s, 3);
  head(s, "Our project", "We test whether this bias is consistent across languages — and where it is strongest");
  // pipeline
  const px = 0.9, py = 2.0, bw = 2.62, bh = 1.0, gp = 0.5;
  const steps = [["Image pair", "SC vs PA"], ["Prompt in language L", "en / zh / ar / hi"], ["Qwen2.5-VL-7B judge", "2-AFC"], ["Pick 1 or 2", "PA = bias"]];
  steps.forEach((st, i) => {
    const x = px + i * (bw + gp);
    s.addShape(p.shapes.RECTANGLE, { x, y: py, w: bw, h: bh, fill: { color: i === 3 ? ACCENT : LIGHT } });
    s.addText([{ text: st[0], options: { bold: true, color: i === 3 ? "FFFFFF" : INK, fontSize: 13, breakLine: true } }, { text: st[1], options: { color: i === 3 ? "CFE0F0" : MUTED, fontSize: 11 } }], { x: x + 0.1, y: py + 0.14, w: bw - 0.2, h: bh - 0.28, fontFace: F, valign: "middle", align: "center" });
    if (i < 3) s.addImage({ data: ic.arrow, x: x + bw + 0.08, y: py + bh / 2 - 0.13, w: 0.34, h: 0.26 });
  });
  // RQ cards
  function rq(x, label, text) {
    s.addShape(p.shapes.RECTANGLE, { x, y: 3.55, w: 5.75, h: 2.7, fill: { color: "FFFFFF" }, line: { color: "D6DCE4", width: 1 } });
    s.addShape(p.shapes.RECTANGLE, { x, y: 3.55, w: 5.75, h: 0.62, fill: { color: ACCENT } });
    s.addText(label, { x: x + 0.25, y: 3.55, w: 5.3, h: 0.62, fontFace: F, fontSize: 15, bold: true, color: "FFFFFF", valign: "middle", margin: 0 });
    s.addText(text, { x: x + 0.25, y: 4.35, w: 5.3, h: 1.7, fontFace: F, fontSize: 15, color: INK, valign: "top", margin: 0 });
  }
  rq(MX, "RQ1 — Consistency", "Does prototypicality bias persist, or do the judge's decisions change, when the same prompt is asked in another language?");
  rq(MX + 6.08, "RQ2 — Sensitivity", "Are cross-lingual differences stronger in socially sensitive contexts (wealth, intellect, …) than in neutral domains (animals, objects)?");

  // ============ 4 — RELATED 1 ============
  function card(x, y, w, h, tag, title, venue, take) {
    s.addShape(p.shapes.RECTANGLE, { x, y, w, h, fill: { color: LIGHT } });
    s.addShape(p.shapes.RECTANGLE, { x, y, w: 0.1, h, fill: { color: ACCENT } });
    s.addText(tag.toUpperCase(), { x: x + 0.3, y: y + 0.22, w: w - 0.55, h: 0.3, fontFace: F, fontSize: 10, bold: true, color: ACCENT, charSpacing: 1, margin: 0 });
    s.addText(title, { x: x + 0.3, y: y + 0.52, w: w - 0.55, h: 0.75, fontFace: F, fontSize: 15, bold: true, color: INK, margin: 0 });
    s.addText(venue, { x: x + 0.3, y: y + 1.22, w: w - 0.55, h: 0.3, fontFace: F, fontSize: 11, italic: true, color: MUTED, margin: 0 });
    s.addText([{ text: "→ ", options: { bold: true, color: ACCENT } }, { text: take, options: { color: INK } }], { x: x + 0.3, y: y + 1.6, w: w - 0.55, h: h - 1.75, fontFace: F, fontSize: 13, margin: 0, valign: "top" });
  }
  s = p.addSlide(); foot(s, 4);
  head(s, "Related work  ·  1 / 2", "Both the judges and the way we measure bias are known to be fragile");
  card(MX, 2.1, 5.85, 3.9, "Chen et al., 2024 · EMNLP [2]", "Humans or LLMs as the Judge?", "A Study on Judgement Bias", "LLM judges carry gender, authority and beauty biases. We use an MLLM as judge — its biases are exactly what we probe.");
  card(MX + 6.1, 2.1, 5.85, 3.9, "Akyurek et al., 2022 · GeBNLP [3]", "Challenges in Measuring Bias via Open-Ended Generation", "Workshop on Gender Bias in NLP", "Bias estimates flip with the prompts, metrics and sampling chosen. Motivates our finding that how you aggregate decides the result.");

  // ============ 5 — RELATED 2 ============
  s = p.addSlide(); foot(s, 5);
  head(s, "Related work  ·  2 / 2", "Measured bias also shifts with the language and the exact prompt");
  card(MX, 2.1, 5.85, 3.4, "Jin et al., 2025 · ACL Findings [1]", "Social Bias Benchmark for Generation (BBG)", "English + Korean", "Cross-lingual social-bias evaluation; generation vs QA disagree. A precedent for evaluating bias across languages.");
  card(MX + 6.1, 2.1, 5.85, 3.4, "Hida, Kaneko & Okazaki, 2025 · EMNLP Findings [4]", "Social Bias Evaluation Requires Prompt Variations", "EMNLP Findings", "Bias rankings fluctuate across prompts. Our cross-lingual prompts ARE prompt variation — and flag translation quality as a confound.");
  s.addText([{ text: "Our gap:  ", options: { bold: true, color: ACCENT } }, { text: "no prior work tests visual prototypicality bias across languages. That is RQ1–RQ2.", options: { color: INK } }], { x: MX, y: 5.85, w: W - 2 * MX, h: 0.6, fontFace: F, fontSize: 15, italic: true, valign: "middle", margin: 0 });

  // ============ 6 — METHOD ============
  s = p.addSlide(); foot(s, 6);
  head(s, "Method", "We score bias as how often the judge picks the prototypical-but-wrong image");
  // two image frames
  function frame(x, label, col) {
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y: 2.2, w: 2.5, h: 1.9, fill: { color: LIGHT }, line: { color: "D6DCE4", width: 1 }, rectRadius: 0.06 });
    s.addImage({ data: ic.image, x: x + 1.0, y: 2.55, w: 0.5, h: 0.5 });
    s.addText(label, { x, y: 3.25, w: 2.5, h: 0.5, fontFace: F, fontSize: 14, bold: true, color: col, align: "center", margin: 0 });
  }
  frame(MX, "Image 1", INK);
  frame(MX + 2.75, "Image 2", INK);
  s.addText('"Which image matches the description?  Answer 1 or 2."', { x: MX, y: 4.35, w: 5.25, h: 0.8, fontFace: F, fontSize: 14, italic: true, color: INK, align: "center", margin: 0 });
  cap(s, MX, 5.25, 5.25, "Left/right order randomized — controls for position bias.");
  // metric card
  s.addShape(p.shapes.RECTANGLE, { x: 7.4, y: 2.2, w: 5.2, h: 3.5, fill: { color: DARK } });
  s.addImage({ data: ic.scale, x: 7.75, y: 2.55, w: 0.55, h: 0.55 });
  s.addText("Error rate", { x: 8.45, y: 2.5, w: 4, h: 0.65, fontFace: F, fontSize: 24, bold: true, color: "FFFFFF", valign: "middle", margin: 0 });
  s.addText("share of trials where the judge chooses the prototypical-but-wrong image (PA)", { x: 7.75, y: 3.35, w: 4.6, h: 0.9, fontFace: F, fontSize: 14, color: "CFE0F0", margin: 0 });
  s.addText([{ text: "0.50", options: { bold: true, color: "FFFFFF" } }, { text: "  no bias        ", options: { color: "8FA9C4" } }, { text: "> 0.50", options: { bold: true, color: "E8918C" } }, { text: "  bias", options: { color: "8FA9C4" } }], { x: 7.75, y: 4.55, w: 4.6, h: 0.6, fontFace: F, fontSize: 16, margin: 0 });

  // ============ 7 — SETUP ============
  s = p.addSlide(); foot(s, 7);
  head(s, "Data & setup", "We collected 3,600 judgments across four languages and three domains");
  // domain icons row
  const doms = [[ic.paw, "Animals", "neutral"], [ic.cube, "Objects", "neutral"], [ic.users, "Demography", "socially sensitive"]];
  doms.forEach((d, i) => {
    const x = MX + i * 2.55;
    s.addShape(p.shapes.OVAL, { x: x + 0.75, y: 1.95, w: 0.95, h: 0.95, fill: { color: LIGHT } });
    s.addImage({ data: d[0], x: x + 0.98, y: 2.18, w: 0.48, h: 0.48 });
    s.addText(d[1], { x, y: 3.0, w: 2.5, h: 0.33, fontFace: F, fontSize: 15, bold: true, color: INK, align: "center", margin: 0 });
    s.addText(d[2], { x, y: 3.33, w: 2.5, h: 0.3, fontFace: F, fontSize: 12, italic: true, color: d[2][0] === "s" ? HI : MUTED, align: "center", margin: 0 });
  });
  // language chips
  s.addImage({ data: ic.globe, x: MX + 0.05, y: 4.05, w: 0.4, h: 0.4 });
  s.addText("4 languages:", { x: MX + 0.55, y: 4.02, w: 2.2, h: 0.45, fontFace: F, fontSize: 15, bold: true, color: INK, valign: "middle", margin: 0 });
  ["English", "Chinese", "Arabic", "Hindi"].forEach((l, i) => {
    const x = MX + 2.7 + i * 1.35;
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y: 4.02, w: 1.2, h: 0.45, fill: { color: ACCENT }, rectRadius: 0.08 });
    s.addText(l, { x, y: 4.02, w: 1.2, h: 0.45, fontFace: F, fontSize: 12, color: "FFFFFF", align: "center", valign: "middle", margin: 0 });
  });
  // facts
  s.addText([
    { text: "300 rows/domain × 3 × 4 languages = 3,600 2-AFC judgments\n", options: { breakLine: true } },
    { text: "Model: Qwen2.5-VL-7B-Instruct   ·   Translation: Google (deep-translator)\n", options: { breakLine: true } },
    { text: "Demography rows carry a socio_attr label: wealth · power · civility · morality · intellect\n", options: { breakLine: true } },
    { text: "Compute: NHR@FAU Alex, 1× A40 GPU", options: {} },
  ], { x: MX, y: 4.85, w: 11.8, h: 1.7, fontFace: F, fontSize: 14, color: INK, paraSpaceAfter: 5 });

  // ============ 8 — RQ1 result (table) ============
  s = p.addSlide(); foot(s, 8);
  head(s, "RQ1 — result", "Aggregated by language, the bias barely moves: the judge is language-stable");
  const hdr = { fill: { color: DARK }, color: "FFFFFF", bold: true, fontFace: F, fontSize: 14, align: "center", valign: "middle" };
  const cell = { fontFace: F, fontSize: 14, align: "center", valign: "middle", color: INK };
  const rh = { fontFace: F, fontSize: 14, bold: true, color: INK, valign: "middle" };
  const t1 = [
    [{ text: "", options: hdr }, { text: "English", options: hdr }, { text: "Chinese", options: hdr }, { text: "Arabic", options: hdr }, { text: "Hindi", options: hdr }, { text: "spread", options: { ...hdr, fill: { color: ACCENT } } }],
    [{ text: "Animals", options: rh }, { text: ".523", options: cell }, { text: ".575", options: cell }, { text: ".570", options: cell }, { text: ".573", options: cell }, { text: ".05", options: { ...cell, color: MUTED } }],
    [{ text: "Objects", options: rh }, { text: ".467", options: cell }, { text: ".470", options: cell }, { text: ".463", options: cell }, { text: ".553", options: cell }, { text: ".09", options: { ...cell, color: MUTED } }],
    [{ text: "Demography", options: rh }, { text: ".560", options: cell }, { text: ".577", options: cell }, { text: ".573", options: cell }, { text: ".553", options: cell }, { text: ".02", options: { ...cell, color: MUTED } }],
  ];
  s.addTable(t1, { x: MX, y: 2.2, w: 8.0, rowH: [0.55, 0.72, 0.72, 0.72], border: { pt: 1, color: "D9DEE3" }, fill: { color: "FFFFFF" } });
  s.addText([
    { text: "Within every domain, the four languages differ by only ~0.02–0.09.\n\n", options: { color: INK, bold: true, breakLine: true } },
    { text: "→ RQ1: switching language does not flip the judge. The bias is largely language-invariant.", options: { color: ACCENT } },
  ], { x: 9.0, y: 2.3, w: 3.6, h: 3.5, fontFace: F, fontSize: 15, valign: "top" });

  // ============ 9 — the catch ============
  s = p.addSlide(); foot(s, 9);
  head(s, "Look closer", "Averaging over the stereotype label hides the real structure");
  s.addShape(p.shapes.RECTANGLE, { x: 1.4, y: 3.4, w: 3.0, h: 1.7, fill: { color: LIGHT } });
  s.addText([{ text: "Demography\n", options: { fontSize: 14, color: MUTED, breakLine: true } }, { text: ".56", options: { fontSize: 40, bold: true, color: MUTED } }], { x: 1.4, y: 3.55, w: 3.0, h: 1.4, fontFace: F, align: "center", valign: "middle", margin: 0 });
  s.addImage({ data: ic.arrow, x: 4.6, y: 4.05, w: 0.7, h: 0.5 });
  s.addText("split by socio_attr", { x: 4.35, y: 3.55, w: 1.2, h: 0.5, fontFace: F, fontSize: 12, italic: true, color: ACCENT, align: "center", margin: 0 });
  s.addShape(p.shapes.RECTANGLE, { x: 6.0, y: 3.4, w: 6.4, h: 1.7, fill: { color: "FFFFFF" }, line: { color: ACCENT, width: 1.5 } });
  s.addText([{ text: "Wealth .77   Power .67\n", options: { fontSize: 20, bold: true, color: HI, breakLine: true } }, { text: "Civility .54    Morality .49    Intellect .48", options: { fontSize: 16, color: ACCENT } }], { x: 6.1, y: 3.55, w: 6.2, h: 1.4, fontFace: F, align: "center", valign: "middle", margin: 0 });
  s.addText("The single .56 number hides a 0.30 spread between attributes.", { x: MX, y: 5.6, w: 11.8, h: 0.5, fontFace: F, fontSize: 16, bold: true, color: INK, align: "center", margin: 0 });

  // ============ 10 — headline chart ============
  s = p.addSlide(); foot(s, 10);
  head(s, "Main finding", "The bias is concentrated on social-status attributes: wealth and power");
  s.addChart(p.charts.BAR, [{ name: "Error rate", labels: ["Wealth", "Power", "Civility", "Morality", "Intellect"], values: [0.774, 0.672, 0.539, 0.487, 0.479] }], {
    x: MX, y: 2.05, w: 7.2, h: 4.5, barDir: "col",
    chartColors: [HI, HI, MID, ACCENT, ACCENT],
    valAxisMinVal: 0, valAxisMaxVal: 1, valAxisMajorUnit: 0.25,
    showValue: true, dataLabelPosition: "outEnd", dataLabelColor: INK, dataLabelFontFace: F, dataLabelFontSize: 12, dataLabelFormatCode: "0.00",
    catAxisLabelColor: INK, catAxisLabelFontFace: F, catAxisLabelFontSize: 13,
    valAxisLabelColor: MUTED, valAxisLabelFontFace: F, valAxisLabelFontSize: 10,
    valGridLine: { color: "E8EBEE", size: 0.5 }, catGridLine: { style: "none" }, showLegend: false, showTitle: false,
  });
  s.addText("0.50 = chance", { x: MX + 0.15, y: 4.18, w: 1.7, h: 0.3, fontFace: F, fontSize: 10, italic: true, color: MUTED, margin: 0 });
  s.addText([
    { text: "Wealth & power: a strong judge-by-looks effect.\n\n", options: { color: INK, bold: true, breakLine: true } },
    { text: "Morality & intellect: essentially no bias.\n\n", options: { color: INK, breakLine: true } },
    { text: "Web data encodes what rich/powerful people look like — but has no stable visual prototype for moral or intelligent.", options: { color: MUTED } },
  ], { x: 8.3, y: 2.3, w: 4.3, h: 4, fontFace: F, fontSize: 15, valign: "top" });

  // ============ 11 — cross-lingual chart ============
  s = p.addSlide(); foot(s, 11);
  head(s, "RQ1 — refined", "The same attribute pattern appears in all four languages");
  const cats = ["Wealth", "Power", "Civility", "Morality", "Intellect"];
  s.addChart(p.charts.BAR, [
    { name: "English", labels: cats, values: [0.774, 0.703, 0.547, 0.473, 0.417] },
    { name: "Chinese", labels: cats, values: [0.774, 0.672, 0.484, 0.559, 0.479] },
    { name: "Arabic", labels: cats, values: [0.839, 0.594, 0.547, 0.505, 0.542] },
    { name: "Hindi", labels: cats, values: [0.710, 0.719, 0.578, 0.409, 0.479] },
  ], {
    x: MX, y: 2.05, w: 8.3, h: 4.45, barDir: "col", barGrouping: "clustered",
    chartColors: ["1A2433", HI, "3F7CAD", "9AA5B1"],
    valAxisMinVal: 0, valAxisMaxVal: 1, valAxisMajorUnit: 0.25,
    catAxisLabelColor: INK, catAxisLabelFontFace: F, catAxisLabelFontSize: 12,
    valAxisLabelColor: MUTED, valAxisLabelFontFace: F, valAxisLabelFontSize: 10,
    valGridLine: { color: "E8EBEE", size: 0.5 }, catGridLine: { style: "none" },
    showLegend: true, legendPos: "b", legendFontFace: F, legendFontSize: 11, showTitle: false,
  });
  s.addText([{ text: "Wealth & power high, morality & intellect near chance — in every language.\n\n", options: { color: INK, bold: true, breakLine: true } }, { text: "→ The bias lives in the visual representation, not in the language of the prompt.", options: { color: ACCENT } }], { x: 9.3, y: 2.4, w: 3.3, h: 4, fontFace: F, fontSize: 14, valign: "top" });

  // ============ 12 — RQ2 (spread chart) ============
  s = p.addSlide(); foot(s, 12);
  head(s, "RQ2 — result", "Language matters more for sensitive attributes than for neutral domains");
  s.addChart(p.charts.BAR, [{ name: "Cross-lingual SD", labels: ["Animals", "Objects", "Demogr.\n(avg)", "Wealth", "Power", "Morality"], values: [0.022, 0.038, 0.010, 0.046, 0.048, 0.054] }], {
    x: MX, y: 2.05, w: 7.2, h: 4.5, barDir: "col",
    chartColors: [MID, MID, MID, HI, HI, HI],
    valAxisMinVal: 0, valAxisMaxVal: 0.06, valAxisMajorUnit: 0.02,
    showValue: true, dataLabelPosition: "outEnd", dataLabelColor: INK, dataLabelFontFace: F, dataLabelFontSize: 11, dataLabelFormatCode: "0.000",
    catAxisLabelColor: INK, catAxisLabelFontFace: F, catAxisLabelFontSize: 12,
    valAxisLabelColor: MUTED, valAxisLabelFontFace: F, valAxisLabelFontSize: 10,
    valGridLine: { color: "E8EBEE", size: 0.5 }, catGridLine: { style: "none" }, showLegend: false, showTitle: false,
  });
  cap(s, MX, 6.6, 7.2, "SD of error rate across the 4 languages (higher = language matters more).");
  s.addText([
    { text: "Neutral domains (gray) vary little across languages.\n\n", options: { color: INK, breakLine: true } },
    { text: "Sensitive attributes (red) vary 2–3× more.\n\n", options: { color: INK, bold: true, breakLine: true } },
    { text: "→ RQ2: suggestive YES — but n = 31–93/cell, so part of this is noise. Exp2 must confirm it.", options: { color: ACCENT } },
  ], { x: 8.3, y: 2.3, w: 4.3, h: 4, fontFace: F, fontSize: 14, valign: "top" });

  // ============ 13 — answers (dark) ============
  s = p.addSlide(); s.background = { color: DARK }; foot(s, 13);
  s.addShape(p.shapes.RECTANGLE, { x: MX, y: 0.55, w: 0.16, h: 0.16, fill: { color: "E8918C" } });
  s.addText("WHAT THE DATA SAYS", { x: MX + 0.3, y: 0.45, w: 10, h: 0.35, fontFace: F, fontSize: 12, bold: true, color: "8FA9C4", charSpacing: 2, margin: 0 });
  s.addText([
    { text: "RQ1   ", options: { bold: true, color: "E8918C" } }, { text: "The bias is largely language-invariant.", options: { bold: true, color: "FFFFFF" } },
    { text: "\n          Switching language does not flip the judge's decisions.\n\n\n", options: { color: "8FA9C4", fontSize: 15 } },
    { text: "RQ2   ", options: { bold: true, color: "E8918C" } }, { text: "What little variation exists concentrates in sensitive attributes.", options: { bold: true, color: "FFFFFF" } },
    { text: "\n          Wealth, power, morality vary 2–3× more across languages than neutral domains.", options: { color: "8FA9C4", fontSize: 15 } },
  ], { x: MX, y: 1.7, w: 12, h: 3.3, fontFace: F, fontSize: 23, valign: "top", lineSpacingMultiple: 1.05 });
  s.addShape(p.shapes.RECTANGLE, { x: MX, y: 5.6, w: 11.83, h: 1.1, fill: { color: "26344A" } });
  s.addText([{ text: "Bias is structural and cross-lingual — ", options: { color: "FFFFFF" } }, { text: "a multilingual result that reinforces the original paper.", options: { color: "E8918C", bold: true } }], { x: MX + 0.3, y: 5.6, w: 11.2, h: 1.1, fontFace: F, fontSize: 16, italic: true, valign: "middle" });

  // ============ 14 — limitations ============
  s = p.addSlide(); foot(s, 14);
  head(s, "Limitations", "Our cross-lingual conclusions are still underpowered and unvalidated");
  s.addText([
    { text: "Small effects vs. confidence intervals; sensitive-attribute cells hold only ~31–93 items per language.", options: { bullet: { indent: 18 }, breakLine: true } },
    { text: "Single model, single seed, single translation backend.", options: { bullet: { indent: 18 }, breakLine: true } },
    { text: "Arabic / Hindi translation quality not yet validated — a confound for any language claim.", options: { bullet: { indent: 18 }, breakLine: true } },
    { text: "Position bias and per-language answer-parse failures not yet audited.", options: { bullet: { indent: 18 } } },
  ], { x: MX, y: 2.2, w: 11.8, h: 4, fontFace: F, fontSize: 17, color: INK, paraSpaceAfter: 16, valign: "top" });

  // ============ 15 — outlook ============
  s = p.addSlide(); foot(s, 15);
  head(s, "Outlook", "Exp2 will confirm the effect statistically and widen the language spectrum");
  const o = [
    ["1", "Confirm statistically", "Mixed-effects logistic regression (no GPU): is the attribute effect significantly larger than the language effect?", true],
    ["2", "Tighten estimates", "Enlarge / balance Demography sampling to ≥150 per cell."],
    ["3", "Test low-resource", "Add languages across the resource spectrum to test the “low-resource = worse” hypothesis head-on."],
    ["4", "Validate translation", "Back-translation drift + per-language parse-failure rates."],
  ];
  o.forEach((st, i) => {
    const y = 2.15 + i * 1.07;
    s.addShape(p.shapes.OVAL, { x: MX, y, w: 0.66, h: 0.66, fill: { color: st[3] ? ACCENT : LIGHT } });
    s.addText(st[0], { x: MX, y, w: 0.66, h: 0.66, fontFace: F, fontSize: 20, bold: true, color: st[3] ? "FFFFFF" : INK, align: "center", valign: "middle", margin: 0 });
    s.addText([{ text: st[1] + "   ", options: { bold: true, color: INK, fontSize: 16 } }, { text: st[2], options: { color: MUTED, fontSize: 13 } }], { x: MX + 0.9, y: y - 0.05, w: 11.0, h: 0.85, fontFace: F, valign: "middle" });
  });
  s.addText([{ text: "Either outcome is a result:  ", options: { bold: true, color: ACCENT } }, { text: "flat confirms language-invariance; a low-resource spike recovers the original hypothesis.", options: { color: INK, italic: true } }], { x: MX, y: 6.55, w: 12, h: 0.5, fontFace: F, fontSize: 14, margin: 0 });

  // ============ 16 — summary ============
  s = p.addSlide(); foot(s, 16);
  head(s, "Summary", "We built the first multilingual ProtoBias study and found an attribute-specific, language-stable bias");
  const sm = [
    ["Pipeline", "First multilingual ProtoBias run — 3,600 judgments, 4 languages, on Qwen2.5-VL-7B."],
    ["Finding", "Bias is concentrated on wealth & power and is consistent across languages — the standard aggregation had hidden it."],
    ["Next", "A concrete, powered Exp2: statistical confirmation, balanced sampling, low-resource languages."],
  ];
  sm.forEach((it, i) => {
    const y = 2.35 + i * 1.35;
    s.addShape(p.shapes.RECTANGLE, { x: MX, y, w: 0.1, h: 1.1, fill: { color: ACCENT } });
    s.addText(it[0], { x: MX + 0.32, y, w: 11.6, h: 0.45, fontFace: F, fontSize: 17, bold: true, color: ACCENT, valign: "middle", margin: 0 });
    s.addText(it[1], { x: MX + 0.32, y: y + 0.5, w: 11.6, h: 0.6, fontFace: F, fontSize: 15, color: INK, valign: "top", margin: 0 });
  });

  // ============ 17 — thanks ============
  s = p.addSlide(); s.background = { color: DARK };
  s.addShape(p.shapes.RECTANGLE, { x: 0, y: 0, w: 0.22, h: H, fill: { color: ACCENT } });
  s.addText("Thank you", { x: 1.0, y: 2.7, w: 11, h: 1.0, fontFace: F, fontSize: 42, bold: true, color: "FFFFFF", margin: 0 });
  s.addText("Questions & discussion", { x: 1.0, y: 3.8, w: 11, h: 0.6, fontFace: F, fontSize: 19, color: "E8918C", margin: 0 });
  s.addText("Repo: P5_Multi_linguistic_histoBias  ·  experiments/exp1_900x4lang · exp2_attribute_bias", { x: 1.0, y: 5.7, w: 11, h: 0.5, fontFace: F, fontSize: 12, color: "8FA9C4", margin: 0 });

  // ============ backup ============
  s = p.addSlide(); s.background = { color: LIGHT };
  s.addText("Appendix — backup slides", { x: MX, y: 3.3, w: 11, h: 0.8, fontFace: F, fontSize: 26, bold: true, color: INK, margin: 0 });
  s.addText("Pulled up only during Q&A", { x: MX, y: 4.1, w: 11, h: 0.4, fontFace: F, fontSize: 14, italic: true, color: MUTED, margin: 0 });

  s = p.addSlide(); foot(s, "B1");
  head(s, "Backup", "Bias by socio-attribute, pooled over languages");
  const h2 = { fill: { color: DARK }, color: "FFFFFF", bold: true, fontFace: F, fontSize: 14, align: "center", valign: "middle" };
  const c2 = { fontFace: F, fontSize: 14, align: "center", valign: "middle", color: INK };
  const b1 = [
    [{ text: "socio_attr", options: { ...h2, align: "left" } }, { text: "Error rate", options: h2 }, { text: "n", options: h2 }, { text: "95% CI", options: h2 }],
    [{ text: "Wealth", options: { ...c2, align: "left", bold: true, color: HI } }, { text: ".774", options: c2 }, { text: "124", options: c2 }, { text: "[.69, .84]", options: c2 }],
    [{ text: "Power", options: { ...c2, align: "left", bold: true, color: HI } }, { text: ".672", options: c2 }, { text: "256", options: c2 }, { text: "[.61, .73]", options: c2 }],
    [{ text: "Civility", options: { ...c2, align: "left" } }, { text: ".539", options: c2 }, { text: "256", options: c2 }, { text: "[.48, .60]", options: c2 }],
    [{ text: "Morality", options: { ...c2, align: "left" } }, { text: ".487", options: c2 }, { text: "372", options: c2 }, { text: "[.44, .54]", options: c2 }],
    [{ text: "Intellect", options: { ...c2, align: "left" } }, { text: ".479", options: c2 }, { text: "192", options: c2 }, { text: "[.41, .55]", options: c2 }],
  ];
  s.addTable(b1, { x: MX, y: 2.2, w: 8.0, rowH: [0.5, 0.55, 0.55, 0.55, 0.55, 0.55], border: { pt: 1, color: "D9DEE3" } });
  s.addText("Gender (not yet tested): male .573 (n=648) · female .558 (n=552).", { x: MX, y: 5.7, w: 11, h: 0.4, fontFace: F, fontSize: 13, italic: true, color: MUTED, margin: 0 });

  await p.writeFile({ fileName: "/Users/xiaochuan/Desktop/Projects/P5_Multi_linguistic_histoBias/code/experiments/ProgressReport.pptx" });
  console.log("WROTE ProgressReport.pptx");
})();
