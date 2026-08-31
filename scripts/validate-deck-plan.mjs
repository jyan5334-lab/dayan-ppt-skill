#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const archetypes = {
  P01: 'hero', P02: 'chapter', P03: 'claim', P04: 'stat', P05: 'trend',
  P06: 'compare', P07: 'evidence', P08: 'path', P09: 'timeline', P10: 'map',
  P11: 'system', P12: 'scenario', P13: 'case', P14: 'matrix', P15: 'quote',
  P16: 'exercise', P17: 'decision', P18: 'close',
};
const motionNeedsFallback = new Set(['M05', 'M07', 'M08']);
const dataArchetypes = new Set(['P04', 'P05', 'P06', 'P10', 'P14']);

function fail(message) {
  console.error(`BLOCKER: ${message}`);
  return false;
}

function warn(message) {
  console.warn(`WARNING: ${message}`);
}

const file = process.argv[2];
if (!file) {
  console.error('Usage: node validate-deck-plan.mjs <deck-plan.json>');
  process.exit(2);
}

let plan;
try {
  plan = JSON.parse(fs.readFileSync(path.resolve(file), 'utf8'));
} catch (error) {
  console.error(`BLOCKER: Cannot read valid JSON: ${error.message}`);
  process.exit(2);
}

let blockers = 0;
let warnings = 0;
const block = (message) => { blockers += 1; fail(message); };
const note = (message) => { warnings += 1; warn(message); };

if (!plan.project || typeof plan.project !== 'object') block('Missing project object.');
for (const key of ['classification', 'audience', 'communication_job', 'motion_level']) {
  if (!plan.project?.[key]) block(`project.${key} is required.`);
}
if (!Array.isArray(plan.slides) || plan.slides.length < 5) {
  block('slides must be an array with at least 5 slides.');
}

const slides = Array.isArray(plan.slides) ? plan.slides : [];
slides.forEach((slide, index) => {
  const label = `Slide ${index + 1}`;
  for (const key of ['id', 'archetype', 'claim', 'evidence', 'visual_focus']) {
    if (!slide?.[key] || (Array.isArray(slide[key]) && slide[key].length === 0)) block(`${label}: ${key} is required.`);
  }
  if (slide?.archetype && !archetypes[slide.archetype]) block(`${label}: unknown archetype ${slide.archetype}.`);
  if (slide?.archetype && dataArchetypes.has(slide.archetype)) {
    const chart = slide.chart;
    if (!chart?.code || !chart?.source || !chart?.unit || !chart?.period) {
      block(`${label}: data page requires chart.code, chart.source, chart.unit, and chart.period.`);
    }
  }
  if (slide?.motion_code && motionNeedsFallback.has(slide.motion_code) && !slide.motion_fallback) {
    block(`${label}: ${slide.motion_code} requires motion_fallback.`);
  }
  if (slide?.motion_code && !/^M0[1-8]$/.test(slide.motion_code)) block(`${label}: unknown motion_code ${slide.motion_code}.`);
});

for (let index = 2; index < slides.length; index += 1) {
  const a = archetypes[slides[index - 2]?.archetype];
  const b = archetypes[slides[index - 1]?.archetype];
  const c = archetypes[slides[index]?.archetype];
  if (a && a === b && b === c) block(`Slides ${index - 1}-${index + 1}: three consecutive ${a} silhouettes.`);
}

const pureText = slides.filter((slide) => ['P03', 'P15', 'P17', 'P18'].includes(slide?.archetype)).length;
if (slides.length >= 10 && pureText > 2) note(`${pureText} text-forward pages detected; verify at least 40% of pages contain direct scene visuals.`);
if (plan.project?.motion_level === 'L2' || plan.project?.motion_level === 'L3') {
  const dynamicCount = slides.filter((slide) => ['M05', 'M07', 'M08'].includes(slide?.motion_code)).length;
  if (slides.length >= 12 && dynamicCount < 2) note('L2/L3 deck has fewer than two dynamic anchors.');
}

console.log(JSON.stringify({
  status: blockers ? 'blocked' : 'passed',
  slides: slides.length,
  blockers,
  warnings,
}, null, 2));
process.exit(blockers ? 1 : 0);
