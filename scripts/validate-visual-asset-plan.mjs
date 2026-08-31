#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const roles = new Set(['background', 'midground', 'foreground', 'cutout', 'texture', 'motion']);
const strategies = new Set(['user_asset', 'official_asset', 'licensed_external', 'imagegen', 'hyperframes_loop']);
const factualRoles = new Set(['evidence', 'atmosphere', 'illustrative', 'brand']);
const compositionControls = new Set(['safe_zone', 'sketch', 'layered_composite']);

const file = process.argv[2];
if (!file) {
  console.error('Usage: node validate-visual-asset-plan.mjs <visual-asset-plan.json>');
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
const block = (message) => { blockers += 1; console.error(`BLOCKER: ${message}`); };
const warn = (message) => { warnings += 1; console.warn(`WARNING: ${message}`); };
const requiredString = (value, label) => {
  if (typeof value !== 'string' || value.trim() === '') block(`${label} is required.`);
};
const inUnit = (value) => Number.isFinite(value) && value >= 0 && value <= 1;

requiredString(plan.schema_version, 'schema_version');
if (!/^\d+:\d+$/.test(plan.slide_ratio || '')) block('slide_ratio must be a ratio such as 16:9.');
if (!Array.isArray(plan.slides) || plan.slides.length === 0) block('slides must contain at least one page.');

for (const slide of plan.slides || []) {
  const label = `Slide ${slide?.slide_id || '?'}`;
  requiredString(slide?.slide_id, `${label}.slide_id`);
  requiredString(slide?.page_archetype, `${label}.page_archetype`);
  requiredString(slide?.claim, `${label}.claim`);
  if (!Array.isArray(slide?.layout?.text_safe_zones) || slide.layout.text_safe_zones.length === 0) {
    block(`${label} requires at least one text_safe_zone.`);
  }
  for (const zone of slide?.layout?.text_safe_zones || []) {
    for (const key of ['x', 'y', 'w', 'h']) if (!inUnit(zone[key])) block(`${label} text_safe_zone.${key} must be 0-1.`);
    if ((zone.w || 0) <= 0 || (zone.h || 0) <= 0 || (zone.x || 0) + (zone.w || 0) > 1 || (zone.y || 0) + (zone.h || 0) > 1) block(`${label} has an invalid text_safe_zone boundary.`);
  }
  if (!Array.isArray(slide?.assets) || slide.assets.length === 0) block(`${label} requires at least one asset specification.`);
  for (const asset of slide?.assets || []) {
    const assetLabel = `${label} asset ${asset?.asset_id || '?'}`;
    requiredString(asset?.asset_id, `${assetLabel}.asset_id`);
    if (!roles.has(asset?.role)) block(`${assetLabel}.role is invalid.`);
    if (!strategies.has(asset?.source_strategy)) block(`${assetLabel}.source_strategy is invalid.`);
    if (!factualRoles.has(asset?.factual_role)) block(`${assetLabel}.factual_role is invalid.`);
    for (const key of ['x', 'y', 'w', 'h']) if (!inUnit(asset?.slot?.[key])) block(`${assetLabel}.slot.${key} must be 0-1.`);
    if ((asset?.slot?.w || 0) <= 0 || (asset?.slot?.h || 0) <= 0 || (asset?.slot?.x || 0) + (asset?.slot?.w || 0) > 1 || (asset?.slot?.y || 0) + (asset?.slot?.h || 0) > 1) block(`${assetLabel} has an invalid slot boundary.`);
    requiredString(asset?.target_aspect_ratio, `${assetLabel}.target_aspect_ratio`);
    requiredString(asset?.subject_position, `${assetLabel}.subject_position`);
    if (!Array.isArray(asset?.negative_constraints) || asset.negative_constraints.length === 0) block(`${assetLabel}.negative_constraints is required.`);
    if (asset?.contains_embedded_text !== false) block(`${assetLabel}.contains_embedded_text must be false; keep PPT text editable.`);
    if (asset?.source_strategy === 'imagegen') {
      requiredString(asset?.prompt, `${assetLabel}.prompt`);
      if (!['atmosphere', 'illustrative', 'brand'].includes(asset?.factual_role)) block(`${assetLabel}: Image 2 assets cannot serve as factual evidence.`);
      if (!compositionControls.has(asset?.composition_control)) block(`${assetLabel}.composition_control must be safe_zone, sketch, or layered_composite.`);
      const brief = asset?.generation_brief;
      requiredString(brief?.title_signal, `${assetLabel}.generation_brief.title_signal`);
      if (!Array.isArray(brief?.style_keywords) || brief.style_keywords.length < 2) block(`${assetLabel}.generation_brief.style_keywords must contain at least two style keywords.`);
      requiredString(brief?.subject_description, `${assetLabel}.generation_brief.subject_description`);
      requiredString(brief?.scene_description, `${assetLabel}.generation_brief.scene_description`);
      if (asset?.composition_control === 'sketch') {
        requiredString(asset?.reference_sketch?.source, `${assetLabel}.reference_sketch.source`);
        requiredString(asset?.reference_sketch?.description, `${assetLabel}.reference_sketch.description`);
      }
      if (asset?.composition_control === 'layered_composite') {
        if (!Array.isArray(asset?.layer_order) || asset.layer_order.length < 2) block(`${assetLabel}.layer_order must contain at least two layers for layered_composite.`);
      }
    }
    if (asset?.role === 'cutout' && asset?.source_strategy === 'imagegen' && !asset?.transparent_strategy) warn(`${assetLabel} is a generated cutout without transparent_strategy; use chroma-key removal or a solid background composition.`);
    if (asset?.role === 'motion' || asset?.source_strategy === 'hyperframes_loop') {
      if (!Number.isFinite(asset?.duration_s) || asset.duration_s < 6 || asset.duration_s > 10) block(`${assetLabel}.duration_s must be 6-10 seconds.`);
      requiredString(asset?.static_fallback, `${assetLabel}.static_fallback`);
      requiredString(asset?.playback_environment, `${assetLabel}.playback_environment`);
      if (asset?.source_strategy === 'hyperframes_loop') {
        requiredString(asset?.source_still_asset_id, `${assetLabel}.source_still_asset_id`);
        requiredString(asset?.image_structure, `${assetLabel}.image_structure`);
        requiredString(asset?.focal_subject, `${assetLabel}.focal_subject`);
        requiredString(asset?.motion_path, `${assetLabel}.motion_path`);
      }
    } else if (!asset?.static_fallback) {
      warn(`${assetLabel} has no static_fallback.`);
    }
  }
}

console.log(JSON.stringify({
  status: blockers ? 'blocked' : 'passed',
  slides: Array.isArray(plan.slides) ? plan.slides.length : 0,
  blockers,
  warnings,
}, null, 2));
process.exit(blockers ? 1 : 0);
