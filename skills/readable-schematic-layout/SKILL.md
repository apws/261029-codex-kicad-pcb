---
name: readable-schematic-layout
description: Make KiCad schematics and PCB layouts readable and debuggable, checking that presentation-only changes preserve connectivity. Use for drawing cleanup, symbol replacement, wiring readability and debug-oriented layout review.
---

# Readable schematics and layouts

Read [the workflow](../../guides/skills/readable-schematic-layout/workflow.adoc) for schematic edits and verification. For PCB readability also read [layout](../../guides/skills/readable-schematic-layout/layout.adoc); for Konnect editing read [observed limits](../../guides/skills/readable-schematic-layout/konnect-limits.adoc).

Establish the authoritative source, sole writer, allowed symbol/net-name/hierarchy changes and fallback method from the existing task context. Ask only for unresolved choices affecting the edit. A read-only review needs no editing decisions. Do not overwrite native changes with an old generator or stale GUI buffer.

Preserve reference, value, footprint, datasheet, manufacturer/supplier fields and DNP when changing symbol appearance. Verify pin functions against primary sources, not merely numbering. Use recognizable symbols, explicit local wires, clear power/signal flow, functional grouping and readable text.

Save a complete baseline. For presentation-only work, export both native XML netlists and run `scripts/compare_netlist.py BASE.xml NEW.xml --names` when names must remain fixed. Require IDENTICAL; intended circuit edits instead need explained differences. Run native ERC and `scripts/check_pin_pad.py NEW.xml --pcb Board.kicad_pcb` (or `--footprints DIR` before a PCB exists). The latter compares number sets, not electrical pin functions.

Export and visually inspect every schematic page. For PCB changes use native full DRC/parity, inspect geometry differences and render relevant layers. MCP success is not acceptance. Report unresolved warnings/exclusions and what remains untested. Keep temporary edits outside fixed releases.
