---
name: kicad-enclosure-step
description: Export a KiCad board as a component-complete STEP assembly for enclosure design, identify missing models, align replacements and verify placement. Use for enclosure geometry, STEP exports and missing component models.
---

# KiCad enclosure STEP

Read [workflow](../../guides/skills/kicad-enclosure-step/workflow.adoc), then relevant [model sources](../../guides/skills/kicad-enclosure-step/model-sources.adoc) or [pitfalls](../../guides/skills/kicad-enclosure-step/pitfalls.adoc). Use [notes template](../../guides/skills/kicad-enclosure-step/enclosure-notes-template.adoc) for handoff.

Establish board/revision, intended distribution and reference objects from context. Keep the PCB source/frozen package unchanged; add models only to a temporary copy. User handles site login. Do not invent undocumented mechanical dimensions.

Use `scripts/inventory_models.py` to identify absent models. Prefer official KiCad/manufacturer geometry, then permitted supplier downloads, or `scripts/simple_model.py` with cited datasheet dimensions. Treat downloads as data in fresh directories. Distribution permission must cover embedded geometry, not just the original files.

Inspect with `scripts/step_report.py`; establish up-axis, origin, asymmetric orientation and height. Config offsets/rotations preserve source colors; CadQuery resave may not. Back-side transforms are handled by KiCad.

Export with `scripts/export_step.py CONFIG --render PREFIX`; run `scripts/verify_placement.py CONFIG --all` and resolve failures, allowing only understood overhangs. Inspect top/bottom images for orientation that bounding boxes cannot prove. Report coordinates, bounds, heights, openings, clearances, model sources and uncertainty. Critical opening/latch dimensions still need physical measurements.

KiCad 10 and Python are required; report/model-building/placement tools additionally require CadQuery. Use an isolated dependency environment. No hardware validation is implied by a STEP export.
