/* Progress Report III deck — Cross-lingual Prototypicality Bias in VLMs.
   Extends the PR-II deck: adds the animal/object subcategory breakdown (exp3g)
   and the T2I-metric representational result (exp3h), both requested in the
   PR-II feedback. Same visual system as build_pr2_deck.js.
   Build:  NODE_PATH=$(npm root -g) node build_pr3_deck.js  */
const pptxgen = require("pptxgenjs");
const path = require("path");

const ROOT = "/Users/xiaochuan/Desktop/Projects/ProtoBias";
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
pres.title = "Cross-lingual Prototypicality Bias — Progress Report III";

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
  // Each bullet is its OWN text box, stacked vertically, so every bullet is a
  // separate animation target in PowerPoint (add "Appear" on click per box).
  // Box heights are estimated from the wrapped line count.
  const cpl = Math.max(8, Math.floor((w * 72) / (fontSize * 0.50)));  // chars/line
  const lineH = (fontSize * 1.22) / 72;                                // inch per line
  const gapIn = gap / 72 + 0.05;                                       // gap between boxes
  let cy = y;
  items.forEach((it) => {
    const lines = Math.max(1, Math.ceil(it.length / cpl));
    const bh = lines * lineH + 0.05;
    s.addText(it, { x, y: cy, w, h: bh, fontFace: BODY, fontSize, color,
      valign: "top", margin: 0, lineSpacingMultiple: 1.0, bullet: { indent: 16 } });
    cy += bh + gapIn;
  });
}
function fig(s, p, { x, y, w, ratio }) {
  s.addImage({ path: F(p), x, y, w, h: w / ratio });
}
function caption(s, t, { x, y, w, color = DIM } = {}) {
  s.addText(t, { x, y, w, h: 0.3, fontFace: BODY, fontSize: 10.5, italic: true,
    color, align: "center", margin: 0 });
}
let _pg = 1;
function pageNo(s) {
  _pg += 1;
  s.addText(String(_pg), { x: W - 0.7, y: H - 0.5, w: 0.4, h: 0.3, fontFace: BODY,
    fontSize: 10, color: DIM, align: "right", margin: 0 });
}
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
s.addText("PROGRESS REPORT III", { x: M, y: 2.05, w: 11, h: 0.4, fontFace: BODY,
  fontSize: 14, bold: true, color: ICE, charSpacing: 4, margin: 0 });
s.addText("Cross-lingual Prototypicality Bias\nin Vision-Language Models", {
  x: M, y: 2.5, w: 11.6, h: 1.9, fontFace: HEAD, fontSize: 44, bold: true,
  color: "FFFFFF", margin: 0, lineSpacing: 50 });
s.addText("A behavioural bias that turns out to live in the image–text representation itself.",
  { x: M, y: 4.55, w: 10.8, h: 0.7, fontFace: HEAD, fontSize: 18, italic: true,
    color: ICE, margin: 0 });
s.addText([
  { text: "Xiaochuan Li · Rishav Chandra", options: { breakLine: true, color: "FFFFFF", bold: true } },
  { text: "Mentor: Subhadeep Roy   ·   Extending ProtoBias (Roy, Bhatia & Eger 2026)   ·   July 2026", options: { color: DIM } },
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
pageNo(s);

// ============================================================ S2b · EXAMPLE PAIRS
s = pres.addSlide(); s.background = { color: PAPER };
kicker(s, "The data · one pair per domain");
title(s, "Semantically-correct (SC) vs prototypical-adversarial (PA)", { fontSize: 26 });
{
  const imgW = 1.92, ratio = 1.5, scX = 1.85, paX = 4.05, judgeX = 6.35, hY = 1.68;
  // column headers
  const colhdr = (t, x, w) => s.addText(t.toUpperCase(), { x, y: hY, w, h: 0.3,
    fontFace: BODY, fontSize: 10.5, bold: true, color: MUTE, charSpacing: 1.5, align: "center", margin: 0 });
  colhdr("Correct (SC)", scX, imgW);
  colhdr("Typical (PA)", paX, imgW);
  s.addText("WHO PREFERS THE CORRECT IMAGE?", { x: judgeX, y: hY, w: 6.0, h: 0.3, fontFace: BODY,
    fontSize: 10.5, bold: true, color: MUTE, charSpacing: 1.5, margin: 0 });
  const EX = [
    ["Animals", "“An animal by a pond with exactly two bamboo stalks.”", "animal_sc.png", "animal_pa.png"],
    ["Demography", "“The surgeon in the operating room.”", "demography_sc.png", "demography_pa.png"],
    ["Objects", "“A vehicle on a street with exactly two traffic cones.”", "object_sc.png", "object_pa.png"],
  ];
  EX.forEach((r, i) => {
    const yr = 2.05 + i * 1.62;
    s.addText(r[0], { x: 0.45, y: yr + 0.5, w: 1.35, h: 0.5, fontFace: HEAD, fontSize: 13,
      bold: true, color: INK, align: "center", margin: 0 });
    s.addText(r[1], { x: scX, y: yr, w: 8.4, h: 0.28, fontFace: BODY, fontSize: 11.5,
      italic: true, color: TXT, margin: 0 });
    fig(s, "v3/paper/assets/examples/" + r[2], { x: scX, y: yr + 0.3, w: imgW, ratio });
    fig(s, "v3/paper/assets/examples/" + r[3], { x: paX, y: yr + 0.3, w: imgW, ratio });
    s.addText([
      { text: "✓ Human    ✓ ProtoScore", options: { color: GREEN, bold: true, breakLine: true } },
      { text: "✗ CLIP    ✗ Pick    ✗ VQA", options: { color: CORAL, bold: true } },
    ], { x: judgeX, y: yr + 0.5, w: 6.0, h: 1.0, fontFace: BODY, fontSize: 12.5,
      valign: "top", margin: 0, paraSpaceAfter: 6 });
  });
}
caption(s, "Illustrative examples. Most automatic judges prefer the typical-but-wrong (PA) image; humans & ProtoScore prefer the correct (SC) one.",
   { x: 1.4, y: 7.02, w: 10.5 });
pageNo(s);

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
pageNo(s);

// ============================================================ S4 · STORY SO FAR
s = pres.addSlide(); s.background = { color: PAPER };
kicker(s, "The story so far  ·  Reports I–II");
title(s, "Where we were after Report II");
const so = [
  ["I", "Looked flat", "Overall error hugged 0.50 — bias seemed weak and language-invariant.", DIM],
  ["II", "The average was hiding it", "Split by socio-attribute, bias is strong for wealth/power, near-chance for morality/intellect.", CORAL],
  ["II", "Two model families, 7 languages", "The attribute pattern replicates across Qwen & InternVL (p≈2×10⁻¹⁴); Bengali/Greek lift the level.", BLUE],
];
so.forEach((r, i) => {
  const y = 2.3 + i * 1.4;
  s.addShape(pres.shapes.OVAL, { x: M, y: y + 0.05, w: 0.7, h: 0.7, fill: { color: r[3] }, line: { type: "none" } });
  s.addText(r[0], { x: M, y: y + 0.05, w: 0.7, h: 0.7, fontFace: HEAD, fontSize: 18, bold: true, color: "FFFFFF", align: "center", valign: "middle", margin: 0 });
  s.addText(r[1], { x: M + 1.0, y: y - 0.02, w: 11.2, h: 0.5, fontFace: HEAD, fontSize: 19, bold: true, color: TXT, margin: 0 });
  s.addText(r[2], { x: M + 1.0, y: y + 0.52, w: 11.2, h: 0.7, fontFace: BODY, fontSize: 15, color: MUTE, margin: 0 });
});
s.addText("Report III asks the next question: WHERE does this bias live — in the model's answer, or deeper?",
  { x: M, y: 6.6, w: 11.8, h: 0.5, fontFace: HEAD, fontSize: 15, italic: true, color: CORAL, margin: 0 });
pageNo(s);

// ============================================================ S5 · FEEDBACK → ACTION
s = pres.addSlide(); s.background = { color: PAPER };
kicker(s, "Acting on Report II feedback");
title(s, "What the mentor asked for — and where it is");
const hdr = (t) => ({ text: t, options: { fill: { color: INK }, color: "FFFFFF", bold: true, fontSize: 13.5, valign: "middle" } });
const cel = (t, c = TXT, b = false) => ({ text: t, options: { color: c, bold: b, fontSize: 13.5, valign: "middle" } });
s.addTable([
  [hdr("Feedback on Report II"), hdr("What we did"), hdr("Slide")],
  [cel("“Check the other categories\n(animal & object)”", TXT, true),
   cel("Broke both down by subcategory + visual knob — they are structured too", MUTE), cel("7", CORAL, true)],
  [cel("“Add T2I metrics —\nVQAScore, CLIPScore, PickScore”", TXT, true),
   cel("All three done (10–11): CLIPScore, PickScore & VQAScore; also on the translated prompts (13).", MUTE), cel("10–13", CORAL, true)],
  [cel("“Add image examples & animation”", TXT, true),
   cel("Example pairs added (3); click-through explorer in backup; click-builds noted", MUTE), cel("3", CORAL, true)],
], { x: M, y: 2.3, w: W - 2 * M, colW: [4.3, 5.65, 1.9], rowH: [0.5, 1.1, 1.1, 0.8],
  border: { pt: 0.5, color: CLINE }, fill: { color: PAPER }, fontFace: BODY, valign: "middle", margin: [5, 8, 5, 8] });
s.addText("The two substantive asks became the two new results in this report.",
  { x: M, y: 6.55, w: W - 2 * M, h: 0.5, fontFace: BODY, fontSize: 13, italic: true, color: MUTE, margin: 0 });
pageNo(s);

// ============================================================ S6 · ANIMAL/OBJECT BREAKDOWN (exp3g)
s = pres.addSlide(); s.background = { color: PAPER };
kicker(s, "New · answering “check animal & object”");
title(s, "Animals & objects are structured too");
bullets(s, [
  "Their flat ~0.5 average hid the same kind of structure demography showed.",
  "Biased: birds & the generic-animal class; vehicles.",
  "Near / below chance: mammals; furniture.",
  "The ordering replicates across BOTH model families — so “structural, not uniform” holds in every domain, not just demography.",
], { y: 2.15, w: 5.3, fontSize: 15.5 });
fig(s, "v3/experiments/exp3g_domain_breakdown/figures/figH_subcategory_breakdown.png", { x: 6.35, y: 2.7, w: 6.4, ratio: 2.5 });
caption(s, "Error rate by subcategory — animal & object, both models (Wilson 95% CIs).", { x: 6.35, y: 5.5, w: 6.4 });
pageNo(s);

// ============================================================ S7 · RESULT 1 (attribute)
s = pres.addSlide(); s.background = { color: PAPER };
kicker(s, "Recap result · the attribute axis");
title(s, "The bias follows the attribute");
bullets(s, [
  "Demography's flat ~0.58 average hides a ~0.28 spread across attributes.",
  "Strong bias for social-status attributes — Wealth, Power.",
  "Near-chance for Morality and Intellect.",
  "Web data encodes what “rich / powerful” looks like; there is no stable visual prototype for “moral” or “smart.”",
], { y: 2.15, w: 5.7, fontSize: 17 });
fig(s, "v3/experiments/exp3a_mixed_effects/figures/figA7_attribute_qwen7lang.png", { x: 6.95, y: 2.3, w: 5.6, ratio: 1.625 });
caption(s, "Prototypicality error rate by socio-attribute — Qwen2.5-VL-7B, all 7 languages.", { x: 6.95, y: 5.95, w: 5.6 });
pageNo(s);

// ============================================================ S8 · REPLICATION
s = pres.addSlide(); s.background = { color: PAPER };
kicker(s, "Recap result · replication");
title(s, "…and it replicates across model families");
fig(s, "v3/experiments/exp3a_mixed_effects/figures/figE_cross_model_OR.png", { x: 2.17, y: 1.95, w: 9.0, ratio: 2.609 });
const stat = (x, big, lab) => {
  s.addText(big, { x, y: 5.65, w: 3.9, h: 0.7, fontFace: HEAD, fontSize: 30, bold: true, color: CORAL, align: "center", margin: 0 });
  s.addText(lab, { x, y: 6.35, w: 3.9, h: 0.6, fontFace: BODY, fontSize: 12.5, color: MUTE, align: "center", margin: 0 });
};
stat(0.85, "OR ≈ 3.7 / 3.1", "Wealth bias vs morality\nQwen / InternVL");
stat(4.85, "p ≈ 2×10⁻¹⁴", "attribute effect\nin both families");
stat(8.7, "not a quirk", "same structure across\ntwo independent VLMs");
pageNo(s);

// ============================================================ S9 · T2I METRICS (exp3h) — HEADLINE
s = pres.addSlide(); s.background = { color: PAPER };
kicker(s, "New headline · answering “add T2I metrics”");
title(s, "The bias lives in the representation, not the answer");
s.addNotes(`Thanks, Rishav. So far we've seen the bias is attribute-specific and shows up in both models. Now I want to ask a deeper question: where does this bias actually live? Is it just how the model answers, or is it baked in deeper? To test this, we dropped the VLM entirely and used three text-to-image metrics — CLIPScore, PickScore, and VQAScore — that just measure how well an image matches the text. And look: CLIPScore and PickScore fall for the typical-but-wrong image on about 70% of items. VQAScore, the strongest one, is more robust — it's near chance overall — but all three keep the exact same shape: the bias peaks on wealth and fades out toward morality and intellect. So the shortcut isn't something the model invents when answering; it's already sitting in the image-text representation.

[中文参考] 谢谢 Rishav。目前看到偏见是属性特异的、两个模型都有。现在问更深一层:它到底住在哪儿——是答题时才产生,还是更底层烙进去了?我们把 VLM 拿掉,用三个图文对齐指标 CLIP、Pick、VQAScore,只衡量图文匹配度。CLIP 和 Pick 约七成选了典型但错的图;VQAScore 最强、最抗骗(整体接近随机),但三者形状一样:财富最高、往道德智力衰减。所以捷径不是答题时编出来的,它本来就在图文表征里。`);
bullets(s, [
  "New angle: score each pair with CLIPScore, PickScore & VQAScore — no VLM asked, just image–text alignment.",
  "CLIP & Pick prefer the typical-but-wrong image on ~70% of items; VQAScore (clip-flant5-xxl) is more robust (~0.47).",
  "But all three keep the SAME attribute signature: strongest on wealth, fading to morality/intellect.",
  "So the shortcut is baked into the image–text embedding — not produced at answer time.",
], { y: 2.1, w: 5.3, fontSize: 15 });
fig(s, "v3/experiments/exp3h_t2i_metrics/figures/figI_metric_bias_by_attr.png", { x: 6.5, y: 2.35, w: 6.2, ratio: 1.674 });
caption(s, "Metric bias rate by socio-attribute — CLIPScore / PickScore / VQAScore (0.5 = no representational bias).", { x: 6.5, y: 6.1, w: 6.2 });
pageNo(s);

// ============================================================ S10 · VLM TRACKS METRIC (exp3h)
s = pres.addSlide(); s.background = { color: PAPER };
kicker(s, "New headline · the link");
title(s, "The VLM's choice tracks the metric");
s.addNotes(`And here's the link that ties it together. For every image pair, we asked: does the VLM pick the same image the metric scores higher? When the metric prefers the correct image, the VLM picks correct about 65 to 70 percent of the time. But when the metric leans toward the typical image, the VLM only gets it right about 35 to 40 percent. That's a gap of roughly 0.3, and it holds across both models and all three metrics. So the behavioural bias and the representational bias aren't two separate things — they're the same phenomenon showing up at two levels.

[中文参考] 这一页把两者串起来。对每一对图我们问:VLM 选的是不是指标打分更高的那张?指标偏向正确图时,VLM 有 65–70% 选对;指标偏向典型图时,只有 35–40% 选对。差距约 0.3,两个模型、三个指标都成立。所以行为偏见和表征偏见不是两回事,是同一个现象在两个层面上的体现。`);
bullets(s, [
  "For each pair: does the VLM pick the image the metric also scores higher?",
  "When the metric prefers the correct image, the VLM picks it ~0.65–0.70 of the time.",
  "When the metric prefers the typical image, the VLM picks correct only ~0.35–0.40.",
  "A +0.26 to +0.34 gap, consistent across both models × both metrics — behaviour and representation are one phenomenon at two levels.",
], { y: 2.1, w: 5.3, fontSize: 15 });
fig(s, "v3/experiments/exp3h_t2i_metrics/figures/figJ_vlm_tracks_metric.png", { x: 6.75, y: 2.5, w: 5.85, ratio: 1.488 });
caption(s, "VLM correct-pick rate, split by which image the T2I metric scores higher.", { x: 6.75, y: 6.6, w: 5.85 });
pageNo(s);

// ============================================================ S11 · RESULT 2 (language)
s = pres.addSlide(); s.background = { color: PAPER };
kicker(s, "Recap result · the language axis");
title(s, "Language is not flat after all");
s.addNotes(`Okay, now the language question — our original motivation. With four languages, the bias looked totally flat across languages. But once we added Bengali and Greek — lower-resource, different scripts — a real effect showed up: prompts in Bengali and Greek trigger significantly more bias than English, and again, in both models. Importantly, the attribute pattern stays the same in every language; it's the overall level that shifts up. So language doesn't change what the model is biased about — it changes how strongly.

[中文参考] 现在讲语言,这是我们最初的出发点。四种语言时偏见看着跨语言持平;一旦加上孟加拉语和希腊语(更低资源、不同文字),真效应就出来了:用这两种语言问,偏见显著比英语强,还是两个模型都这样。关键是属性模式每种语言都一样,变的是整体水平往上抬。所以语言不改变"偏什么",改变"偏多少"。`);
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
pageNo(s);

// ============================================================ S11b · T2I ON TRANSLATED PROMPTS
s = pres.addSlide(); s.background = { color: PAPER };
kicker(s, "New · T2I metrics on the translated prompts");
title(s, "The language effect is NOT in the representation");
s.addNotes(`But then we did something the mentor suggested — we ran the metrics on the translated prompts too, using a multilingual CLIP. And this gave us a really clean split. The representation is biased in every single language — all above chance. But it's flat across languages: no Bengali or Greek spike at all; if anything Bengali is slightly lower. So put these two slides together: the attribute bias lives in the representation, but the language effect does not — that one comes from how the VLM itself handles less-familiar languages, not from the image-text alignment.

[中文参考] 然后我们做了导师建议的事:把指标也在翻译后的 prompt 上跑,用多语版 CLIP。这给了一个很干净的分离。表征在每一种语言里都有偏见,全超过随机;但跨语言是平的,完全没有孟加拉/希腊那个抬升,孟加拉语甚至略低。所以两页放一起:属性偏见住在表征里,语言效应不在——语言效应来自 VLM 自己怎么处理不熟悉的语言,不是图文对齐本身。`);
bullets(s, [
  "We scored the translated prompts with a multilingual CLIP (mentor request).",
  "The representation is biased in every language (0.58–0.66, all above chance).",
  "But it is flat across languages — no Bengali/Greek lift (Bengali is if anything lower).",
  "A clean split: the attribute bias is representational; the language effect comes from the VLM's own language handling, not image–text alignment.",
], { y: 2.1, w: 5.4, fontSize: 15.5 });
fig(s, "v3/experiments/exp3h_t2i_metrics/figures/figK_xlingual_bias_mclip.png", { x: 6.35, y: 2.5, w: 6.3, ratio: 1.767 });
caption(s, "Multilingual-CLIP bias rate by language; grey = English reference.", { x: 6.35, y: 6.2, w: 6.3 });
pageNo(s);

// ============================================================ S12 · TRANSLATION QA
s = pres.addSlide(); s.background = { color: PAPER };
kicker(s, "Language result · rigor");
title(s, "Is it just bad translation? No.");
s.addNotes(`Now, the obvious pushback: maybe Bengali and Greek just get worse translations, and that's the whole effect. So we back-translated every prompt and measured the drift. And it's actually the opposite of what you'd expect: the most-biased languages, Greek and Bengali, have the highest translation fidelity. The least-biased ones, Hindi and Russian, drift the most. If bad translation were driving the bias, that relationship would go the other way. So it's not a translation artifact.

[中文参考] 一个很自然的质疑:会不会就是孟加拉语和希腊语翻得差,整个效应就这么来的?所以我们把每条 prompt 回译、量漂移。结果恰恰相反:偏见最强的希腊语、孟加拉语,翻译保真度最高;偏见最弱的印地语、俄语,反而漂得最多。要是翻译差导致偏见,这关系应该反过来。所以不是翻译伪影。`);
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
pageNo(s);

// ============================================================ S13 · KNOB CONFOUND
s = pres.addSlide(); s.background = { color: PAPER };
kicker(s, "Going deeper · the confound");
title(s, "Is it just a low-level visual cue? No.");
s.addNotes(`Another confound: every adversarial image also tweaks one visual knob — count, colour, scale, layout, spatial. Maybe the model isn't reacting to prototypes at all, just to, say, colour. But if it were a colour artifact, colour would spike — and instead colour is the lowest. The bias is actually highest when the cue is hard to perceive, like count or scale. And critically, wealth still beats morality within every single knob. So the attribute effect isn't a knob artifact either.

[中文参考] 另一个混杂:每张对抗图还改了一个视觉旋钮——数量、颜色、大小、布局、空间。也许模型不是在反应原型,只是在反应颜色?但若是颜色伪影,颜色应该最高——结果它最低。偏见反而在难察觉的线索上最高,比如数量、大小。而且最关键:每一个旋钮内部,财富都还是高于道德。所以属性效应也不是旋钮造成的假象。`);
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
s.addNotes(`One more check. Do the two models fail on the same image pairs, or different ones? We correlated their per-item error rates, and it's 0.68. So the trap is largely item-intrinsic — it's an objective property of the image pair itself, not just one model's quirk. It's not a perfect one, though — about half is still model-specific, strongest agreement on demography, weakest on objects.

[中文参考] 再一个检验:两个模型是在同一批图对上翻车,还是各翻各的?把逐项错误率做相关,是 0.68。所以陷阱很大程度是"图对本身"的客观属性,不是某个模型的怪癖。不过也不完美——约一半仍是模型特有的,人物上最一致、物体上最弱。`);
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
s.addNotes(`So let me pull it all together. The bias is a shortcut with three parts. First, a source — the attribute: a visual prototype exists for wealth and status, but not for morality or intellect, and that map is largely item-intrinsic. Second, a trigger — signal weakness: the model falls back on the prototype when the real cue is hard to perceive, or when the prompt language is unfamiliar. And third, a home — the representation: all three metrics carry the same signature, and the VLM's choice tracks them. So: the attribute decides whether a shortcut exists, signal-weakness decides how much it's taken, and the shared representation is where it lives.

[中文参考] 收一下整个故事。这个偏见是有三部分的捷径。第一,来源——属性:财富、地位有视觉原型,道德、智力没有,而且这映射很大程度是图对本身固有的。第二,触发——信号弱:真线索难察觉、或语言不熟悉时,模型退回原型。第三,归宿——表征:三个指标都带同款签名,VLM 又跟着它们走。所以:属性决定"有没有捷径",信号弱决定"走多少",共享表征就是它住的地方。`);
s.addText("A shortcut with a source, a trigger, and a home", { x: M, y: 0.95, w: 12.0, h: 0.9,
  fontFace: HEAD, fontSize: 28, bold: true, color: "FFFFFF", margin: 0 });
const tk = (y, n, head, body, c) => {
  s.addText(n, { x: M, y, w: 0.8, h: 1.0, fontFace: HEAD, fontSize: 40, bold: true, color: c, margin: 0 });
  s.addText(head, { x: M + 0.95, y: y + 0.02, w: 11.2, h: 0.5, fontFace: HEAD, fontSize: 18, bold: true, color: "FFFFFF", margin: 0 });
  s.addText(body, { x: M + 0.95, y: y + 0.52, w: 11.2, h: 0.85, fontFace: BODY, fontSize: 14, color: ICE, margin: 0 });
};
tk(1.95, "1", "Source — the attribute", "A visual prototype exists for wealth and status, not for morality or intellect. That map replicates across both families and is largely item-intrinsic (r = 0.68).", CORAL);
tk(3.5, "2", "Trigger — signal weakness", "The model falls back on the prototype when the discriminating cue is hard to perceive (count, scale) OR the prompt language is unfamiliar (Bengali, Greek).", BLUE);
tk(5.05, "3", "Home — the representation", "CLIPScore, PickScore & VQAScore all carry the same attribute signature, and the VLM's choice tracks them. The bias sits in the shared image–text embedding, not in one model's decoding.", GREEN);
s.addText("Attribute sets whether a shortcut exists · weakness sets how much it's taken · the representation is where it lives.",
  { x: M, y: 6.55, w: 12.0, h: 0.5, fontFace: HEAD, fontSize: 14, italic: true, color: CORAL, margin: 0 });
pageNo(s);

// ============================================================ S16 · LIMITATIONS
s = pres.addSlide(); s.background = { color: PAPER };
kicker(s, "Limitations");
title(s, "What we are not yet claiming");
s.addNotes(`A few honest caveats. This is one seed and one translation backend. The adversarial knob co-varies with the prototype, so it's not a fully clean manipulation. Our demography cells are small — wealth is only about 31 items per language — so we lean on confidence intervals. The T2I metrics were mainly on the English prompt, though we've started extending them. And we had to drop Qwen-32B — it was just too slow on the hardware we had.

[中文参考] 几个诚实的局限。单个随机种子、单个翻译后端。对抗旋钮和原型共变,不是完全干净的操纵。人物格子样本小——财富每种语言只有约 31 条——所以靠置信区间。T2I 指标主要用英文 prompt,不过已开始往多语言扩。还有 Qwen-32B 只能砍——现有硬件上太慢。`);
bullets(s, [
  "Single seed, single translation backend; the adversarial “knob” (color / scale) is a co-varying confound.",
  "Demography cells are small (Wealth ≈ 31 / language) — mixed-effects pools, but power is limited.",
  "T2I metrics are scored on English text only — a clean representation probe, but not yet cross-lingual.",
  "Qwen-32B was dropped — infeasible runtime (≈280 s/item) on the available 2×A40 sharding.",
], { y: 2.15, w: 11.6, fontSize: 17, h: 4.4 });
pageNo(s);

// ============================================================ S17 · OUTLOOK
s = pres.addSlide(); s.background = { color: PAPER };
kicker(s, "Outlook");
title(s, "Next steps");
s.addNotes(`And where we're going. First, extend VQAScore to the translated prompts, the way we did for CLIP. Second, the scale axis — Qwen-32B in 4-bit — does the bias shrink as models get bigger? Third, more model families, to see how general the language effect is. And finally, pinning down the language effect itself — disentangling how much is resource, how much is script, and how much is cultural loading behind that Arabic-Bengali-Greek spike.

[中文参考] 下一步方向。第一,把 VQAScore 扩到翻译后的 prompt,像对 CLIP 那样。第二,规模轴——4-bit 的 Qwen-32B——模型变大偏见会不会缩小?第三,加更多模型家族,看语言效应多普遍。最后,把语言效应本身搞清楚——在阿拉伯/孟加拉/希腊那个抬升背后,拆开多少是资源、多少是文字、多少是文化负载。`);
const ol = [
  ["Multilingual VQAScore", "VQAScore (clip-flant5-xxl) is done in English; extend it to the translated prompts, as we did for CLIP."],
  ["Scale axis", "Qwen-32B in 4-bit on a single GPU — does the bias shrink with model size?"],
  ["More model families", "Gemma-3, LLaVA-OneVision — how general is the language effect?"],
  ["Pin down language", "Disentangle resource vs script vs cultural loading behind the ar / bn / el spike."],
];
ol.forEach((r, i) => {
  const y = 2.25 + i * 1.12;
  s.addShape(pres.shapes.OVAL, { x: M, y: y + 0.05, w: 0.42, h: 0.42, fill: { color: INK }, line: { type: "none" } });
  s.addText(String(i + 1), { x: M, y: y + 0.05, w: 0.42, h: 0.42, fontFace: HEAD, fontSize: 16, bold: true, color: "FFFFFF", align: "center", valign: "middle", margin: 0 });
  s.addText(r[0], { x: M + 0.7, y: y - 0.02, w: 3.2, h: 0.5, fontFace: HEAD, fontSize: 17, bold: true, color: CORAL, margin: 0 });
  s.addText(r[1], { x: M + 4.0, y: y - 0.02, w: 8.5, h: 0.7, fontFace: BODY, fontSize: 15, color: TXT, valign: "top", margin: 0 });
});
pageNo(s);

// ============================================================ S18 · THANKS (dark)
s = pres.addSlide(); s.background = { color: INK };
dot(s, M, 2.5, CORAL); dot(s, M + 0.22, 2.5, BLUE); dot(s, M + 0.44, 2.5, GREEN);
s.addNotes(`And that's it — we built the first multilingual, multi-model ProtoBias pipeline, across seven languages and two model families, and traced the bias all the way down to the shared image-text representation. Thanks for listening, and we're happy to take any questions.

[中文参考] 就到这里——我们搭了第一个多语言、多模型的 ProtoBias 流程,覆盖七种语言、两个模型家族,并把这个偏见一路追到共享的图文表征。谢谢大家,欢迎提问。`);
s.addText("Thank you — questions?", { x: M, y: 2.9, w: 11.8, h: 1.2, fontFace: HEAD,
  fontSize: 40, bold: true, color: "FFFFFF", margin: 0 });
s.addText([
  { text: "A behavioural bias, traced to the shared image–text representation — across 7 languages & 2 model families.", options: { breakLine: true, color: ICE } },
  { text: "github.com/xchuan-li/cross_lingual_protobias", options: { color: CORAL, bold: true } },
], { x: M, y: 4.5, w: 11.8, h: 1.0, fontFace: BODY, fontSize: 15, margin: 0, paraSpaceAfter: 8 });
pageNo(s);

// ============================================================ BACKUP · SUMMARY
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
  [bc("T2I metric bias (CLIP / Pick)", TXT, true), bc("0.71 / 0.67", GREEN), bc("shared backbone", GREEN)],
  [bc("VLM–metric tracking gap", TXT, true), bc("+0.28 / +0.31"), bc("+0.26 / +0.34")],
], { x: 2.2, y: 2.05, w: 8.9, colW: [3.7, 2.6, 2.6], rowH: 0.48,
  border: { pt: 0.5, color: CLINE }, fontFace: BODY, valign: "middle", margin: [3, 6, 3, 6] });
caption(s, "Item-clustered mixed-effects logistic regression; back-translation QA; CLIPScore/PickScore; numpy/scipy.", { x: 2.2, y: 6.5, w: 8.9 });
pageNo(s);

// ============================================================ BACKUP · T2I METRICS DEFINED (new)
s = pres.addSlide(); s.background = { color: PAPER };
kicker(s, "Backup · methods", { color: DIM });
title(s, "The T2I metrics, defined", { fontSize: 26 });
s.addText("Each metric scores how well an image matches the text. We score BOTH images and take the margin.",
  { x: M, y: 1.8, w: W - 2 * M, h: 0.4, fontFace: BODY, fontSize: 15, italic: true, color: MUTE, margin: 0 });
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: M, y: 2.35, w: W - 2 * M, h: 0.95, fill: { color: INK }, line: { type: "none" }, rectRadius: 0.08 });
s.addText("margin = score(correct image, text) − score(typical image, text)\nmargin < 0  →  the metric itself is prototypicality-biased",
  { x: M, y: 2.35, w: W - 2 * M, h: 0.95, fontFace: "Courier New", fontSize: 12.5, color: "FFFFFF", align: "center", valign: "middle", margin: 4, lineSpacingMultiple: 1.15 });
const t2 = [
  ["CLIPScore", "cosine(image, text) in CLIP's embedding space — the standard image–text alignment score.", CORAL],
  ["PickScore", "a CLIP fine-tuned on human image-preference data — “which image would a person pick?”", BLUE],
  ["VQAScore (outlook)", "P(“yes” | image, “does this show <text>?”) from a VQA model — a generative scorer.", GREEN],
];
t2.forEach((d, i) => {
  const y = 3.55 + i * 0.82;
  s.addShape(pres.shapes.OVAL, { x: M, y: y + 0.08, w: 0.16, h: 0.16, fill: { color: d[2] }, line: { type: "none" } });
  s.addText([{ text: d[0] + "  ", options: { bold: true, color: d[2] } }, { text: "— " + d[1], options: { color: TXT } }],
    { x: M + 0.35, y, w: W - 2 * M - 0.35, h: 0.6, fontFace: BODY, fontSize: 15, valign: "top", margin: 0 });
});
s.addText("Scored on the English prompt to isolate the representation question; run on the same 900 items as the VLM eval, so scores join 1:1 to model choices.",
  { x: M, y: 6.2, w: W - 2 * M, h: 0.7, fontFace: BODY, fontSize: 13, italic: true, color: MUTE, margin: 0 });
pageNo(s);

// ============================================================ BACKUP · WHY INTERNVL3
s = pres.addSlide(); s.background = { color: PAPER };
kicker(s, "Backup · methods", { color: DIM });
title(s, "Why InternVL3-8B as the second model", { fontSize: 27 });
s.addText("Goal: rule out “it's just a Qwen quirk.” A second, independent family tests whether the finding generalizes.",
  { x: M, y: 1.8, w: W - 2 * M, h: 0.5, fontFace: BODY, fontSize: 15, italic: true, color: MUTE, margin: 0 });
const why = [
  ["Different family", "OpenGVLab, not Alibaba — independent architecture and training, not a Qwen variant."],
  ["Size-matched", "≈8B vs Qwen's 7B — controls for scale, so a difference isn't “one is far bigger.”"],
  ["Strong, standard baseline", "A top open VLM family widely used in papers — credible and representative."],
  ["Fits the pipeline", "Multi-image and multilingual; the HF-native checkpoint loads via the standard API."],
];
why.forEach((r, i) => {
  const y = 2.65 + i * 1.02; const c = [CORAL, BLUE, GREEN, INK][i];
  s.addShape(pres.shapes.OVAL, { x: M, y: y + 0.03, w: 0.42, h: 0.42, fill: { color: c }, line: { type: "none" } });
  s.addText(String(i + 1), { x: M, y: y + 0.03, w: 0.42, h: 0.42, fontFace: HEAD, fontSize: 15, bold: true, color: "FFFFFF", align: "center", valign: "middle", margin: 0 });
  s.addText(r[0], { x: M + 0.65, y: y - 0.02, w: 3.7, h: 0.5, fontFace: HEAD, fontSize: 16, bold: true, color: TXT, valign: "top", margin: 0 });
  s.addText(r[1], { x: M + 4.45, y: y - 0.02, w: 8.1, h: 0.85, fontFace: BODY, fontSize: 14, color: MUTE, valign: "top", margin: 0 });
});
pageNo(s);

// ============================================================ BACKUP · MIXED-EFFECTS + LRT
s = pres.addSlide(); s.background = { color: PAPER };
kicker(s, "Backup · methods", { color: DIM });
title(s, "Mixed-effects logistic regression & the LRT", { fontSize: 26 });
s.addText("The model", { x: M, y: 1.85, w: 5.8, h: 0.4, fontFace: HEAD, fontSize: 16, bold: true, color: CORAL, margin: 0 });
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: M, y: 2.3, w: 5.85, h: 0.7, fill: { color: INK }, line: { type: "none" }, rectRadius: 0.08 });
s.addText("picked_adv ~ socio_attr + lang + gender + (1 | item)",
  { x: M, y: 2.3, w: 5.85, h: 0.7, fontFace: "Courier New", fontSize: 12.5, color: "FFFFFF", align: "center", valign: "middle", margin: 4 });
bullets(s, [
  "Logistic → models P(pick prototype); coefficients exponentiate to odds ratios (OR).",
  "Fixed effects (socio_attr, lang, gender) = what we estimate.",
  "Random intercept (1 | item) = each image-pair gets its own baseline — the same item repeats in 7 languages, so those 7 views are not independent.",
], { x: M, y: 3.25, w: 5.85, h: 3.0, fontSize: 13.5, gap: 9 });
s.addText("The test  ·  LRT", { x: 7.2, y: 1.85, w: 5.4, h: 0.4, fontFace: HEAD, fontSize: 16, bold: true, color: BLUE, margin: 0 });
bullets(s, [
  "Fit two nested models (with vs without a factor); compare fit by likelihood.",
  "χ² = 2×(LL_big − LL_small); p from chi-squared → one p-value per whole factor.",
], { x: 7.2, y: 2.3, w: 5.4, h: 1.7, fontSize: 13.5, gap: 9 });
const bh2 = (t) => ({ text: t, options: { fill: { color: INK }, color: "FFFFFF", bold: true, fontSize: 11.5 } });
const bc2 = (t, c, b) => ({ text: t, options: { color: c || TXT, bold: !!b, fontSize: 12, valign: "middle" } });
s.addTable([
  [bh2("factor"), bh2("χ²"), bh2("p"), bh2("verdict")],
  [bc2("socio_attr", TXT, true), bc2("70.1"), bc2("2×10⁻¹⁴", CORAL, true), bc2("significant", CORAL)],
  [bc2("language", TXT, true), bc2("14.6"), bc2("0.024", CORAL, true), bc2("significant", CORAL)],
  [bc2("attr × lang", TXT, true), bc2("18.8"), bc2("0.76"), bc2("n.s.", MUTE)],
], { x: 7.2, y: 4.15, w: 5.4, colW: [1.7, 1.0, 1.4, 1.3], rowH: 0.46, border: { pt: 0.5, color: CLINE }, fontFace: BODY, valign: "middle", margin: [2, 5, 2, 5] });
caption(s, "Qwen-7B; same pattern in InternVL3-8B. Implemented with item-clustered robust SEs (no statsmodels on the cluster).", { x: 7.2, y: 6.35, w: 5.4 });
pageNo(s);

// ============================================================ BACKUP · BACK-TRANSLATION QA
s = pres.addSlide(); s.background = { color: PAPER };
kicker(s, "Backup · methods", { color: DIM });
title(s, "Back-translation translation-quality check", { fontSize: 26 });
s.addText("We can't read all 7 languages — so we round-trip each prompt back to English and measure how much it drifted.",
  { x: M, y: 1.8, w: W - 2 * M, h: 0.4, fontFace: BODY, fontSize: 15, italic: true, color: MUTE, margin: 0 });
const fb = (x, t1, t2t) => {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 2.5, w: 2.7, h: 0.95, fill: { color: CARD }, line: { color: CLINE, width: 1 }, rectRadius: 0.08 });
  s.addText([{ text: t1, options: { bold: true, breakLine: true, fontSize: 13 } }, { text: t2t, options: { fontSize: 10.5, color: MUTE } }],
    { x, y: 2.5, w: 2.7, h: 0.95, fontFace: BODY, color: TXT, align: "center", valign: "middle", margin: 2 });
};
const arr = (x, lab) => {
  s.addShape(pres.shapes.LINE, { x, y: 2.97, w: 0.55, h: 0, line: { color: CORAL, width: 2, endArrowType: "triangle" } });
  s.addText(lab, { x: x - 0.25, y: 2.55, w: 1.05, h: 0.3, fontFace: BODY, fontSize: 10, italic: true, color: CORAL, align: "center", margin: 0 });
};
fb(M, "English prompt", "original E");
arr(3.55, "translate");
fb(4.25, "Greek text", "shown to the model");
arr(7.05, "back-translate");
fb(7.75, "English again", "E′");
s.addText("compare  E vs E′  →  token-F1", { x: 10.65, y: 2.5, w: 2.3, h: 0.95, fontFace: HEAD, fontSize: 13, bold: true, color: INK, align: "center", valign: "middle", margin: 0 });
bullets(s, [
  "If the language effect were a translation artifact, the most-biased languages would drift the MOST.",
  "Instead the opposite: Greek (0.88) and Bengali (0.86) — the most biased — have the HIGHEST fidelity; Hindi / Russian (0.79) — not biased — the lowest.",
  "Caveat: a lexical check using the same MT system — a sanity check that rules out the obvious confound, not a proof.",
], { x: M, y: 4.0, w: W - 2 * M, h: 2.6, fontSize: 14.5, gap: 11 });
pageNo(s);

// ============================================================ BACKUP · CROSS-LINGUAL METRICS DEFINED
s = pres.addSlide(); s.background = { color: PAPER };
kicker(s, "Backup · methods", { color: DIM });
title(s, "The cross-lingual metrics, defined", { fontSize: 26 });
s.addText("For each image-pair we summarise its behaviour across all its languages (items judged in ≥ 2 languages).",
  { x: M, y: 1.8, w: W - 2 * M, h: 0.4, fontFace: BODY, fontSize: 15, italic: true, color: MUTE, margin: 0 });
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: M, y: 2.35, w: W - 2 * M, h: 0.9, fill: { color: INK }, line: { type: "none" }, rectRadius: 0.08 });
s.addText("per item, across languages:   all-wrong → SBR   ·   all-right → SCR   ·   mixed → CFR\nCFR + SBR + SCR = 1",
  { x: M, y: 2.35, w: W - 2 * M, h: 0.9, fontFace: "Courier New", fontSize: 12.5, color: "FFFFFF", align: "center", valign: "middle", margin: 4 });
const mdefs = [
  ["Cross-lingual Flip Rate (CFR)", "the model's choice changes across languages — the item is not stable.", CORAL],
  ["Stable Bias Rate (SBR)", "the model picks the prototypical-but-wrong image in every language.", BLUE],
  ["Stable Correct Rate (SCR)", "the model picks the correct image in every language.", GREEN],
];
mdefs.forEach((d, i) => {
  const y = 3.55 + i * 0.82;
  s.addShape(pres.shapes.OVAL, { x: M, y: y + 0.08, w: 0.16, h: 0.16, fill: { color: d[2] }, line: { type: "none" } });
  s.addText([{ text: d[0] + "  ", options: { bold: true, color: d[2] } }, { text: "— " + d[1], options: { color: TXT } }],
    { x: M + 0.35, y, w: W - 2 * M - 0.35, h: 0.6, fontFace: BODY, fontSize: 15.5, valign: "top", margin: 0 });
});
s.addText("Item-level summaries across languages, not per-judgment — which is why a flat aggregate error rate can still hide heavy item-level flipping (overall CFR ≈ 0.65).",
  { x: M, y: 6.2, w: W - 2 * M, h: 0.7, fontFace: BODY, fontSize: 13, italic: true, color: MUTE, margin: 0 });
pageNo(s);

// ====================================== INTERACTIVE · MODEL EXPLORER
const EXPQ = _pg + 1, EXPI = _pg + 2, EXPB = _pg + 3;  // computed from running page count
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

pres.writeFile({ fileName: F("v3/paper/ProgressReport_3.pptx") }).then((fn) =>
  console.log("WROTE " + fn));
