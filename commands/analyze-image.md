---
description: Read-only visual audit of a rendered figure (PNG, PDF, or SVG). Delegates to the figura-image-auditor subagent so the image bytes do not pollute the main context.
argument-hint: <path-to-image-pdf-or-svg> [path-to-producing-script]
allowed-tools: ["Agent"]
---

Audit the figure at `$ARGUMENTS` by **delegating to the `figura-image-auditor` subagent**. The subagent reads the image, walks the six defect categories, and returns a compact defect table. The main thread does not load image bytes.

Supported inputs: PNG, PDF, SVG. The subagent rasterizes SVG to PNG via the bundled `svg_to_png.sh` helper before reading.

If `$ARGUMENTS` is empty, ask the user for a path. Do not improvise (no globbing, no guessing).

## How to dispatch

Call the `Agent` tool with `subagent_type="figura-image-auditor"`. Pass the image path verbatim and (if available) the producing script's path. Brief the agent like a colleague who just walked into the room: state the figure path, say which venue/column-width if known, mention any user concerns the audit should focus on.

Example dispatch prompt body:

```
Audit the figure at /abs/path/figures/expt_b2.png. Producing script: /abs/path/scripts/expt_b2.py. Target venue: NeurIPS (double-column ~6.75 in). User specifically wants you to check whether the inset axes collides with the legend, and whether the headline blue line at 21.56° has enough margin from the inset frame edge.
```

The subagent returns a markdown defect table + 1-sentence verdict + 1-sentence routing recommendation.

## What to do with the result

1. Surface the table to the user verbatim (it's already compact).
2. If the verdict says "Ship it", ship.
3. Otherwise, the routing recommendation names the next slash command (`/figura:beautify`, `/figura:fix-overlap`, `/figura:iterate`). Mention it as the next step; do **not** auto-invoke unless the user asks.

## Why this is delegated

Reading a PDF or PNG into the main context costs ~5-50K tokens of image data the user will never need. The subagent owns the raw image; you get a 200-word defect report back. Keeps the main thread focused on the actual work (editing scripts, dispatching follow-up commands).
