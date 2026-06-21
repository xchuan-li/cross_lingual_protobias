/* Progress Report II deck — Cross-lingual Prototypicality Bias in VLMs.
   Bullet-only slides, figures embedded, mapped to the 10-pt rubric.
   Build:  NODE_PATH=$(npm root -g) node build_pr2_deck.js  */
const pptxgen = require("pptxgenjs");
const path = require("path");

const ROOT = "/Users/xiaochuan/Desktop/Projects/P5_Multi_linguistic_histoBias";
const F = (p) => path.join(ROOT, p);

// ---- palette (indigo academic; coral/blue match the matplotlib figures) ----
const INK = "1B1F3B", INK2 = "2A3057";
const PAPER = "FFFFFF", TXT = "23262F", MUTE = "5A6072", DIM = "9AA0B0";
const CORAL = "C44E52", BLUE = "4C72B0", GREEN = "55A868";
const ICE = "C9D2EC", CARD = "F5F6FA", CLINE = "E4E6EF";
const HEAD = "Georgia", BODY = "Calibri";
const W = 13.333, H = 7.5, M = 0.75;

const pres = new pptxgen();
pres.defineLayout({ name: "W", width: W, height: H });
pres.layout = "W";
pres.author = "Xiaochuan Li";
pres.title = "Cross-lingual Prototypicality Bias — Progress Report II";

// ---------- helpers ----------
function kicker(s, t, { y = 0.55, color = CORAL, x = M } = {}) {
  s.addText(t.toUpperCase(), { x, y, w: W - 2 * M, h: 0.3, fontFace: BODY,
    fontSize: 12, bold: true, color, charSpacing: 3, margin: 0 });
}
function title(s, t, { y = 0.92, w = W - 2 * M, color = TXT, fontSize = 32, x = M } = {}) {
  s.addText(t, { x, y, w, h: 0.95, fontFace: HEAD, fontSize, bold: true,
    color, margin: 0, lineSpacing: fontSize * 1.08 });
}
function bullets(s, items, { x = M, y = 2.15, w = 6.6, h = 4.6, fontSize = 17,
  color = TXT, gap = 11 } = {}) {
  s.addText(items.map((it) => ({
    text: it, options: { bullet: { indent: 16 }, breakLine: true,
      paraSpaceAfter: gap, color, fontSize },
  })), { x, y, w, h, fontFace: BODY, valign: "top", margin: 0, lineSpacingMultiple: 1.0 });
}
function fig(s, p, { x, y, w, ratio }) {
  // exact aspect ratio (h derived) so it renders identically in PowerPoint and
  // LibreOffice — avoids the contain-crop artifact some renderers apply.
  s.addImage({ path: F(p), x, y, w, h: w / ratio });
}
function caption(s, t, { x, y, w, color = DIM } = {}) {
  s.addText(t, { x, y, w, h: 0.3, fontFace: BODY, fontSize: 10.5, italic: true,
    color, align: "center", margin: 0 });
}
let _pg = 1;  // title is page 1; pageNo() auto-increments for each content slide
function pageNo(s) {
  _pg += 1;
  s.addText(String(_pg), { x: W - 0.7, y: H - 0.5, w: 0.4, h: 0.3, fontFace: BODY,
    fontSize: 10, color: DIM, align: "right", margin: 0 });
}
// clickable nav button: visual rounded rect + a hyperlinked text box covering it.
function navbtn(s, x, label, target, active) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 6.5, w: 3.4, h: 0.66,
    fill: { color: active ? INK : CARD }, line: { color: active ? INK : CLINE, width: 1 },
    rectRadius: 0.08 });
  const opt = { x, y: 6.5, w: 3.4, h: 0.66, fontFace: BODY, fontSize: 14, bold: true,
    color: active ? "FFFFFF" : INK, align: "center", valign: "middle", margin: 0 };
  if (!active) opt.hyperlink = { slide: target };
  s.addText(label, opt);
}
function dot(s, x, y, c = CORAL, d = 0.12) {
  s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: c }, line: { type: "none" } });
}

// ============================================================ S1 · TITLE
let s = pres.addSlide(); s.background = { color: INK };
dot(s, M, 1.7, CORAL); dot(s, M + 0.22, 1.7, BLUE); dot(s, M + 0.44, 1.7, GREEN);
s.addText("PROGRESS REPORT II", { x: M, y: 2.05, w: 11, h: 0.4, fontFace: BODY,
  fontSize: 14, bold: true, color: ICE, charSpacing: 4, margin: 0 });
s.addText("Cross-lingual Prototypicality Bias\nin Vision-Language Models", {
  x: M, y: 2.5, w: 11.6, h: 1.9, fontFace: HEAD, fontSize: 44, bold: true,
  color: "FFFFFF", margin: 0, lineSpacing: 50 });
s.addText("Does a vision-language model track meaning — or lean on language- and culture-specific prototypes?",
  { x: M, y: 4.55, w: 10.8, h: 0.7, fontFace: HEAD, fontSize: 18, italic: true,
    color: ICE, margin: 0 });
s.addText([
  { text: "Xiaochuan Li · Rishav Chandra", options: { breakLine: true, color: "FFFFFF", bold: true } },
  { text: "Mentor: Subhadeep Roy   ·   Extending ProtoBias (Roy, Bhatia & Eger 2026)   ·   June 2026", options: { color: DIM } },
], { x: M, y: 6.25, w: 11.8, h: 0.8, fontFace: BODY, fontSize: 13, margin: 0 });

// ============================================================ S2 · PROBLEM
s = pres.addSlide(); s.background = { color: PAPER };
kicker(s, "The problem");
title(s, "Prototypicality bias: judging by looks, not meaning");
bullets(s, [
  "Automatic metrics and VLMs increasingly replace humans for image–text evaluation.",
  "Failure mode: they reward the image that looks typical — even when it is wrong for the prompt.",
  "ProtoBias pairs a semantically-correct but atypical image with a prototypical but wrong one.",
  "A judge that prefers the typical-but-wrong image is riding a shortcut, not the meaning.",
], { y: 2.15, w: 6.5, fontSize: 17.5 });
fig(s, "v1/paper/assets/protobias_examples_animals_objects.png", { x: 7.35, y: 2.75, w: 5.45, ratio: 2.062 });
caption(s, "Correct-but-atypical (left) vs prototypical-but-wrong (right).", { x: 7.35, y: 5.55, w: 5.45 });
pageNo(s, 2);

// ============================================================ S3 · EXTENSION
s = pres.addSlide(); s.background = { color: PAPER };
kicker(s, "Our extension");
title(s, "Does the bias depend on the language you ask in?");
bullets(s, [
  "ProtoBias is English-only and studies evaluation metrics.",
  "Our turn: translate only the prompt, hold the image pair fixed.",
  "If the verdict moves with language, the model is importing language-specific expectations.",
  "RQ1 — is the bias consistent across languages?   RQ2 — worse in socially sensitive domains?",
], { y: 2.15, w: 6.7, fontSize: 17.5 });
// simple pipeline graphic
const px = 7.7, pw = 4.9;
const box = (x, y, w, h, t, fill, col) => {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, fill: { color: fill },
    line: { color: CLINE, width: 1 }, rectRadius: 0.08 });
  s.addText(t, { x, y, w, h, fontFace: BODY, fontSize: 12.5, bold: true, color: col,
    align: "center", valign: "middle", margin: 2 });
};
box(px, 2.5, pw, 0.85, "image pair  +  prompt in language L", CARD, TXT);
s.addShape(pres.shapes.LINE, { x: px + pw / 2, y: 3.35, w: 0, h: 0.5, line: { color: CORAL, width: 2, endArrowType: "triangle" } });
box(px + 0.7, 3.95, pw - 1.4, 0.85, "VLM judge", INK, "FFFFFF");
s.addShape(pres.shapes.LINE, { x: px + pw / 2, y: 4.8, w: 0, h: 0.5, line: { color: CORAL, width: 2, endArrowType: "triangle" } });
box(px, 5.4, pw, 0.85, "picks image 1 or 2  →  error rate", CARD, TXT);
caption(s, "Same images, language swapped — a controlled cross-lingual probe.", { x: px, y: 6.35, w: pw });
pageNo(s, 3);

// ============================================================ S4 · RELATED WORK
s = pres.addSlide(); s.background = { color: PAPER };
kicker(s, "Related work · new since Report 1");
title(s, "Where this sits — bias structure & multilingual bias");
const rw = [
  ["FAccT 2025", "Hausladen et al. — Social Perception of Faces in a VLM", "Bias concentrates unevenly across social-trait dimensions — parallels our attribute-specific result.", CORAL],
  ["AACL 2025", "Al Sahili et al. — Breaking Language Barriers or Reinforcing Bias?", "Multilingual VLMs are more biased than English, worst in low-resource languages — the closest mirror.", BLUE],
  ["CoLM 2024", "Neplenbroek et al. — MBBQ", "Non-English stereotypes exceed English even controlling for culture; control parallels our back-translation check.", BLUE],
  ["ACL 2025", "Friedrich et al. — MAGBIG", "Cross-lingual bias variation in text-to-image generation — a contrasting modality.", GREEN],
];
const cw = 5.85, ch = 1.95, gx = 0.35, gy = 0.3, ox = M, oy = 2.25;
rw.forEach((r, i) => {
  const x = ox + (i % 2) * (cw + gx), y = oy + Math.floor(i / 2) * (ch + gy);
  s.addShape(pres.shapes.RECTANGLE, { x, y, w: cw, h: ch, fill: { color: CARD }, line: { color: CLINE, width: 1 } });
  s.addShape(pres.shapes.RECTANGLE, { x, y, w: 0.09, h: ch, fill: { color: r[3] }, line: { type: "none" } });
  s.addText(r[0].toUpperCase(), { x: x + 0.28, y: y + 0.18, w: cw - 0.5, h: 0.28, fontFace: BODY, fontSize: 10.5, bold: true, color: r[3], charSpacing: 2, margin: 0 });
  s.addText(r[1], { x: x + 0.28, y: y + 0.5, w: cw - 0.5, h: 0.6, fontFace: HEAD, fontSize: 14, bold: true, color: TXT, margin: 0 });
  s.addText(r[2], { x: x + 0.28, y: y + 1.08, w: cw - 0.5, h: 0.75, fontFace: BODY, fontSize: 12, color: MUTE, margin: 0 });
});
pageNo(s, 4);

// ============================================================ S5 · METHOD
s = pres.addSlide(); s.background = { color: PAPER };
kicker(s, "Method");
title(s, "A 2-alternative forced choice");
bullets(s, [
  "Show two images: correct (atypical) vs prototypical (wrong).",
  "Ask in the target language which image matches; answer is a single digit (1 or 2).",
  "Left/right randomized so image position cannot be a confound.",
  "Metric = error rate = how often the judge picks the prototypical-but-wrong image.",
], { y: 2.15, w: 6.7, fontSize: 17.5 });
// chance callout
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 8.0, y: 2.5, w: 4.4, h: 2.5, fill: { color: INK }, line: { type: "none" }, rectRadius: 0.1 });
s.addText("0.50", { x: 8.0, y: 2.85, w: 4.4, h: 1.0, fontFace: HEAD, fontSize: 54, bold: true, color: "FFFFFF", align: "center", margin: 0 });
s.addText("= chance · no bias", { x: 8.0, y: 3.9, w: 4.4, h: 0.4, fontFace: BODY, fontSize: 15, color: ICE, align: "center", margin: 0 });
s.addText("above 0.50  →  prototypicality bias", { x: 8.0, y: 4.35, w: 4.4, h: 0.4, fontFace: BODY, fontSize: 13, italic: true, color: CORAL, align: "center", margin: 0 });
pageNo(s, 5);

// ============================================================ S6 · WHAT'S NEW
s = pres.addSlide(); s.background = { color: PAPER };
kicker(s, "What's new since Report 1");
title(s, "Acting on the feedback: more metrics, more models");
const hdr = (t) => ({ text: t, options: { fill: { color: INK }, color: "FFFFFF", bold: true, fontSize: 14, align: "left", valign: "middle" } });
const cell = (t, c = TXT, b = false) => ({ text: t, options: { color: c, bold: b, fontSize: 13.5, valign: "middle" } });
s.addTable([
  [hdr(""), hdr("Report 1"), hdr("Report 2  (now)")],
  [cell("Languages", TXT, true), cell("4  —  en · zh · ar · hi", MUTE), cell("7  —  + Russian · Bengali · Greek", CORAL, true)],
  [cell("Models", TXT, true), cell("1  —  Qwen2.5-VL-7B", MUTE), cell("2 families  —  + InternVL3-8B", CORAL, true)],
  [cell("Statistics", TXT, true), cell("point estimates", MUTE), cell("mixed-effects regression + LRT", CORAL, true)],
  [cell("Rigor checks", TXT, true), cell("—", MUTE), cell("back-translation QA · flip / stable-bias rates", CORAL, true)],
], { x: M, y: 2.3, w: W - 2 * M, colW: [2.6, 4.5, 4.75], rowH: [0.5, 0.72, 0.72, 0.72, 0.72],
  border: { pt: 0.5, color: CLINE }, fill: { color: PAPER }, fontFace: BODY, valign: "middle", margin: [4, 8, 4, 8] });
s.addText("The two items the mentor flagged after Report 1 — additional metrics and additional models — are exactly the two new columns.",
  { x: M, y: 6.5, w: W - 2 * M, h: 0.5, fontFace: BODY, fontSize: 13, italic: true, color: MUTE, margin: 0 });
pageNo(s, 6);

// ============================================================ S7 · DATA & SETUP
s = pres.addSlide(); s.background = { color: PAPER };
kicker(s, "Data & setup");
title(s, "ProtoBias across a resource × script design");
bullets(s, [
  "Domains: Animals / Objects (neutral) and Demography (socially sensitive).",
  "Demography rows carry a socio-attribute: Wealth · Power · Civility · Morality · Intellect.",
  "7 languages × 900 items × 2 models  ≈  12,500 judgments.",
  "Qwen2.5-VL-7B & InternVL3-8B on NHR@FAU Alex A40 GPUs.",
], { y: 2.15, w: 6.5, fontSize: 17 });
const lt = (t, c = TXT, b = false) => ({ text: t, options: { color: c, bold: b, fontSize: 12.5, valign: "middle" } });
s.addTable([
  [{ text: "Language", options: { fill: { color: INK }, color: "FFFFFF", bold: true, fontSize: 12.5 } },
   { text: "Script", options: { fill: { color: INK }, color: "FFFFFF", bold: true, fontSize: 12.5 } },
   { text: "Resource", options: { fill: { color: INK }, color: "FFFFFF", bold: true, fontSize: 12.5 } }],
  [lt("English / Chinese"), lt("Latin / Han"), lt("high")],
  [lt("Russian"), lt("Cyrillic"), lt("high")],
  [lt("Arabic / Hindi"), lt("Arabic / Devanagari"), lt("mid")],
  [lt("Bengali", CORAL, true), lt("Bengali", CORAL, true), lt("low", CORAL, true)],
  [lt("Greek", CORAL, true), lt("Greek", CORAL, true), lt("mid · distinct", CORAL, true)],
], { x: 7.7, y: 2.25, w: 4.9, colW: [2.0, 1.7, 1.2], rowH: 0.52,
  border: { pt: 0.5, color: CLINE }, fontFace: BODY, valign: "middle", margin: [3, 6, 3, 6] });
pageNo(s, 7);

// ============================================================ S8 · RESULT 1
s = pres.addSlide(); s.background = { color: PAPER };
kicker(s, "Result 1");
title(s, "The bias follows the attribute");
bullets(s, [
  "Demography's flat ~0.56 average hides a 0.30 spread.",
  "Strong bias for social-status attributes — Wealth, Power.",
  "Near-chance for Morality and Intellect.",
  "Web data encodes what “rich / powerful” looks like; there is no stable visual prototype for “moral” or “smart.”",
], { y: 2.15, w: 5.7, fontSize: 17 });
fig(s, "v2/experiments/exp2_attribute_bias/figures/figA_bias_by_attribute.png", { x: 6.95, y: 2.3, w: 5.6, ratio: 1.625 });
caption(s, "Prototypicality error rate by socio-attribute (Qwen2.5-VL-7B).", { x: 6.95, y: 5.95, w: 5.6 });
pageNo(s, 8);

// ============================================================ S9 · MONEY SLIDE
s = pres.addSlide(); s.background = { color: PAPER };
kicker(s, "Result 1 · replication");
title(s, "…and it replicates across model families");
fig(s, "v3/experiments/exp3a_mixed_effects/figures/figE_cross_model_OR.png", { x: 2.17, y: 1.95, w: 9.0, ratio: 2.609 });
const stat = (x, big, lab) => {
  s.addText(big, { x, y: 5.65, w: 3.9, h: 0.7, fontFace: HEAD, fontSize: 30, bold: true, color: CORAL, align: "center", margin: 0 });
  s.addText(lab, { x, y: 6.35, w: 3.9, h: 0.6, fontFace: BODY, fontSize: 12.5, color: MUTE, align: "center", margin: 0 });
};
stat(0.85, "OR ≈ 3.7 / 3.1", "Wealth bias vs morality\nQwen / InternVL");
stat(4.85, "p ≈ 2×10⁻¹⁴", "attribute effect\nin both families");
stat(8.7, "not a quirk", "same structure across\ntwo independent VLMs");
pageNo(s, 9);

// ============================================================ S10 · RESULT 2
s = pres.addSlide(); s.background = { color: PAPER };
kicker(s, "Result 2");
title(s, "Language is not flat after all");
bullets(s, [
  "Four languages looked invariant; adding Bengali & Greek revealed a real effect.",
  "Bengali and Greek prompts → significantly more bias than English, in both models.",
  "The attribute pattern stays the same; the overall level shifts up (no interaction).",
], { y: 2.1, w: 5.5, fontSize: 16.5 });
s.addChart(pres.charts.BAR, [
  { name: "Qwen2.5-VL-7B", labels: ["zh", "ru", "ar", "hi", "bn", "el"], values: [1.13, 1.06, 1.31, 1.04, 1.60, 1.49] },
  { name: "InternVL3-8B", labels: ["zh", "ru", "ar", "hi", "bn", "el"], values: [0.96, 1.17, 1.12, 1.33, 1.41, 1.72] },
], { x: 6.5, y: 2.0, w: 6.2, h: 4.6, barDir: "col", chartColors: [BLUE, CORAL],
  showLegend: true, legendPos: "t", legendFontSize: 11, legendColor: MUTE,
  catAxisLabelColor: MUTE, valAxisLabelColor: MUTE, valAxisMinVal: 0, valAxisMaxVal: 2,
  valGridLine: { color: "ECEEF5", size: 0.5 }, catGridLine: { style: "none" },
  showTitle: true, title: "Odds ratio of bias vs English  (1.0 = same as English)",
  titleFontSize: 12, titleColor: TXT });
pageNo(s, 10);

// ============================================================ S11 · TRANSLATION QA
s = pres.addSlide(); s.background = { color: PAPER };
kicker(s, "Result 2 · rigor");
title(s, "Is it just bad translation? No.");
bullets(s, [
  "We back-translated every non-English prompt and measured drift.",
  "The most-biased languages (Greek, Bengali) have the highest translation fidelity.",
  "The least-biased (Hindi, Russian) have the lowest — the opposite of a translation artifact.",
], { y: 2.1, w: 5.7, fontSize: 16.5 });
const qh = (t) => ({ text: t, options: { fill: { color: INK }, color: "FFFFFF", bold: true, fontSize: 12.5 } });
const qc = (t, c, b) => ({ text: t, options: { color: c, bold: b, fontSize: 13, valign: "middle" } });
s.addTable([
  [qh("Language"), qh("Bias vs English"), qh("Back-translation fidelity")],
  [qc("Greek", CORAL, true), qc("+49%", CORAL, true), qc("0.88  (highest)", CORAL, true)],
  [qc("Bengali", CORAL, true), qc("+60%", CORAL, true), qc("0.86", CORAL, true)],
  [qc("Arabic", CORAL, true), qc("+31%", CORAL, true), qc("0.85", CORAL, true)],
  [qc("Chinese", MUTE), qc("—", MUTE), qc("0.84", MUTE)],
  [qc("Hindi", MUTE), qc("—", MUTE), qc("0.79", MUTE)],
  [qc("Russian", MUTE), qc("—", MUTE), qc("0.79  (lowest)", MUTE)],
], { x: 6.7, y: 2.15, w: 5.9, colW: [1.9, 1.9, 2.1], rowH: 0.5,
  border: { pt: 0.5, color: CLINE }, fontFace: BODY, valign: "middle", margin: [3, 7, 3, 7] });
pageNo(s, 11);

// ============================================================ S12 · NEW METRICS
s = pres.addSlide(); s.background = { color: PAPER };
kicker(s, "New behavioural metrics");
title(s, "Stable bias tracks the attribute");
bullets(s, [
  "Cross-lingual Flip Rate — does the choice change across languages?",
  "Stable Bias Rate — does the model pick the wrong image in ALL languages?",
  "Wealth has the highest stable-bias rate in both models — it is biased everywhere, not flip-flopping.",
], { y: 2.1, w: 5.5, fontSize: 16.5 });
s.addChart(pres.charts.BAR, [
  { name: "Qwen2.5-VL-7B", labels: ["Wealth", "Power", "Civility", "Morality", "Intellect"], values: [0.58, 0.28, 0.22, 0.18, 0.17] },
  { name: "InternVL3-8B", labels: ["Wealth", "Power", "Civility", "Morality", "Intellect"], values: [0.45, 0.36, 0.30, 0.23, 0.19] },
], { x: 6.5, y: 2.0, w: 6.2, h: 4.6, barDir: "col", chartColors: [BLUE, CORAL],
  showLegend: true, legendPos: "t", legendFontSize: 11, legendColor: MUTE,
  catAxisLabelColor: MUTE, valAxisLabelColor: MUTE, valAxisMinVal: 0, valAxisMaxVal: 0.7,
  valGridLine: { color: "ECEEF5", size: 0.5 }, catGridLine: { style: "none" },
  showTitle: true, title: "Stable Bias Rate by attribute  (chose wrong image in all 7 languages)",
  titleFontSize: 12, titleColor: TXT });
pageNo(s, 12);

// ============================================================ S13 · KNOB CONFOUND
s = pres.addSlide(); s.background = { color: PAPER };
kicker(s, "Going deeper · the confound");
title(s, "Is it just a low-level visual cue? No.");
bullets(s, [
  "Every adversarial image also tweaks one visual knob — count / colour / scale / layout / spatial.",
  "If the bias were a colour artifact, colour would spike. Instead colour is the LOWEST (≈0.40).",
  "Bias is highest when the cue is hard to perceive (count, scale) — a fallback when the detail can't be grounded.",
  "Wealth > morality holds within every knob — the attribute effect is not a knob artifact.",
], { y: 2.1, w: 5.6, fontSize: 16 });
fig(s, "v3/experiments/exp3e_knob_confound/figures/figF_error_by_knob.png", { x: 6.7, y: 2.6, w: 6.05, ratio: 1.848 });
pageNo(s);

// ============================================================ S14 · CROSS-MODEL AGREEMENT
s = pres.addSlide(); s.background = { color: PAPER };
kicker(s, "Going deeper · is the trap objective?");
title(s, "The same items fool both model families");
bullets(s, [
  "Two families judge the same 900 image pairs — do they err on the SAME ones?",
  "Per-item error rates correlate at r = 0.68 (Cohen's κ = 0.39).",
  "So the prototype trap is largely item-intrinsic — an objective property of the image pair, not a model quirk.",
  "(r is not 1.0: about half is still model-specific — strongest agreement on demography, weakest on objects.)",
], { y: 2.1, w: 6.0, fontSize: 16 });
fig(s, "v3/experiments/exp3f_cross_model_agreement/figures/figG_item_agreement.png", { x: 8.0, y: 2.05, w: 4.5, ratio: 1.038 });
pageNo(s);

// ============================================================ S15 · TAKEAWAY (dark)
s = pres.addSlide(); s.background = { color: INK };
kicker(s, "What we found", { color: CORAL });
s.addText("One picture: a fallback with two factors", { x: M, y: 0.95, w: 11.8, h: 0.9,
  fontFace: HEAD, fontSize: 30, bold: true, color: "FFFFFF", margin: 0 });
const tk = (y, n, head, body, c) => {
  s.addText(n, { x: M, y, w: 0.8, h: 1.1, fontFace: HEAD, fontSize: 46, bold: true, color: c, margin: 0 });
  s.addText(head, { x: M + 1.0, y: y + 0.05, w: 11.4, h: 0.55, fontFace: HEAD, fontSize: 20, bold: true, color: "FFFFFF", margin: 0 });
  s.addText(body, { x: M + 1.0, y: y + 0.62, w: 11.4, h: 0.95, fontFace: BODY, fontSize: 15, color: ICE, margin: 0 });
};
tk(2.2, "1", "Is there a prototype to take?  →  the attribute", "A visual prototype exists for wealth and status, not for morality or intellect. That map replicates across both families, and the trap is largely item-intrinsic (the same items fool both, r = 0.68).", CORAL);
tk(4.15, "2", "How weak is the signal?  →  perception & language", "The model falls back on the prototype when the discriminating cue is hard to perceive (count, scale) OR the prompt language is unfamiliar (Bengali, Greek). Two routes, one mechanism.", BLUE);
s.addText("Attribute sets whether a shortcut exists; signal-weakness sets how much the model takes it.",
  { x: M, y: 6.4, w: 11.8, h: 0.6, fontFace: HEAD, fontSize: 16, italic: true, color: CORAL, margin: 0 });
pageNo(s);

// ============================================================ S14 · LIMITATIONS
s = pres.addSlide(); s.background = { color: PAPER };
kicker(s, "Limitations");
title(s, "What we are not yet claiming");
bullets(s, [
  "Single seed, single translation backend; the adversarial “knob” (color / scale) is a co-varying confound.",
  "Demography cells are small (Wealth ≈ 31 / language) — mixed-effects pools, but power is limited.",
  "Qwen-32B was dropped — infeasible runtime (≈280 s/item) on the available 2×A40 sharding.",
  "Why ar / bn / el specifically — not a clean resource gradient (Russian is non-Latin yet flat) — is open.",
], { y: 2.15, w: 11.6, fontSize: 17, h: 4.4 });
pageNo(s, 14);

// ============================================================ S15 · OUTLOOK
s = pres.addSlide(); s.background = { color: PAPER };
kicker(s, "Outlook");
title(s, "Next steps");
const ol = [
  ["Scale axis", "Qwen-32B in 4-bit on a single GPU — does the bias shrink with model size?"],
  ["More families", "Gemma-3, LLaVA-OneVision — map how general the language effect is."],
  ["Shortcut-severing", "Remove prototype cues — is stable correctness actually grounded?"],
  ["Pin down language", "Disentangle resource vs script vs cultural loading behind the ar / bn / el spike."],
];
ol.forEach((r, i) => {
  const y = 2.25 + i * 1.12;
  s.addShape(pres.shapes.OVAL, { x: M, y: y + 0.05, w: 0.42, h: 0.42, fill: { color: INK }, line: { type: "none" } });
  s.addText(String(i + 1), { x: M, y: y + 0.05, w: 0.42, h: 0.42, fontFace: HEAD, fontSize: 16, bold: true, color: "FFFFFF", align: "center", valign: "middle", margin: 0 });
  s.addText(r[0], { x: M + 0.7, y: y - 0.02, w: 3.2, h: 0.5, fontFace: HEAD, fontSize: 17, bold: true, color: CORAL, margin: 0 });
  s.addText(r[1], { x: M + 4.0, y: y - 0.02, w: 8.5, h: 0.7, fontFace: BODY, fontSize: 15, color: TXT, valign: "top", margin: 0 });
});
pageNo(s, 15);

// ============================================================ S16 · THANKS (dark)
s = pres.addSlide(); s.background = { color: INK };
dot(s, M, 2.5, CORAL); dot(s, M + 0.22, 2.5, BLUE); dot(s, M + 0.44, 2.5, GREEN);
s.addText("Thank you — questions?", { x: M, y: 2.9, w: 11.8, h: 1.2, fontFace: HEAD,
  fontSize: 40, bold: true, color: "FFFFFF", margin: 0 });
s.addText([
  { text: "Built & ran the first multilingual, multi-model ProtoBias pipeline — 7 languages, 2 model families.", options: { breakLine: true, color: ICE } },
  { text: "github.com/xchuan-li/cross_lingual_protobias", options: { color: CORAL, bold: true } },
], { x: M, y: 4.5, w: 11.8, h: 1.0, fontFace: BODY, fontSize: 15, margin: 0, paraSpaceAfter: 8 });
pageNo(s, 16);

// ============================================================ BACKUP
s = pres.addSlide(); s.background = { color: PAPER };
kicker(s, "Backup", { color: DIM });
title(s, "Full cross-model summary", { fontSize: 26 });
const bh = (t) => ({ text: t, options: { fill: { color: INK }, color: "FFFFFF", bold: true, fontSize: 12 } });
const bc = (t, c = TXT, b = false) => ({ text: t, options: { color: c, bold: b, fontSize: 12.5, valign: "middle", align: "center" } });
s.addTable([
  [bh(""), bh("Qwen2.5-VL-7B"), bh("InternVL3-8B")],
  [bc("overall error rate", TXT, true), bc("0.547"), bc("0.585")],
  [bc("attribute effect (LRT p)", TXT, true), bc("2.1×10⁻¹⁴", CORAL), bc("2.7×10⁻¹⁴", CORAL)],
  [bc("Wealth odds ratio", TXT, true), bc("3.67"), bc("3.09")],
  [bc("language effect (LRT p)", TXT, true), bc("0.024", CORAL), bc("0.0085", CORAL)],
  [bc("Greek / Bengali OR", TXT, true), bc("1.49 / 1.60"), bc("1.72 / 1.41")],
  [bc("Wealth stable-bias rate", TXT, true), bc("0.58"), bc("0.45")],
  [bc("cross-lingual flip rate", TXT, true), bc("0.65"), bc("0.69")],
], { x: 2.2, y: 2.1, w: 8.9, colW: [3.5, 2.7, 2.7], rowH: 0.5,
  border: { pt: 0.5, color: CLINE }, fontFace: BODY, valign: "middle", margin: [3, 6, 3, 6] });
caption(s, "Item-clustered mixed-effects logistic regression; back-translation QA; numpy/scipy, no statsmodels.", { x: 2.2, y: 6.5, w: 8.9 });
pageNo(s, 17);

// ====================================== INTERACTIVE · MODEL EXPLORER (slides 20-22)
// Click a button -> hyperlink jumps to the twin slide showing a different model.
// Works in PowerPoint slideshow mode (Mac/Windows/online); no animations needed.
const EXPQ = 20, EXPI = 21, EXPB = 22;
function explorer(figpath, ratio, activeIdx) {
  const sl = pres.addSlide(); sl.background = { color: PAPER };
  kicker(sl, "Interactive · model explorer");
  title(sl, "Does it hold across models?  ▸ click a button", { fontSize: 25 });
  fig(sl, figpath, { x: 1.87, y: 1.9, w: 9.6, ratio });
  navbtn(sl, 1.45, "Qwen-7B", EXPQ, activeIdx === 0);
  navbtn(sl, 4.97, "InternVL3-8B", EXPI, activeIdx === 1);
  navbtn(sl, 8.49, "Both overlaid", EXPB, activeIdx === 2);
  pageNo(sl);
}
explorer("v3/experiments/exp3a_mixed_effects/figures/figC_attribute_OR_qwen7b.png", 2.619, 0);
explorer("v3/experiments/exp3a_mixed_effects/figures/figC_attribute_OR_internvl8b.png", 2.619, 1);
explorer("v3/experiments/exp3a_mixed_effects/figures/figE_cross_model_OR.png", 2.609, 2);

pres.writeFile({ fileName: F("v3/paper/ProgressReport_2.pptx") }).then((fn) =>
  console.log("WROTE " + fn));
