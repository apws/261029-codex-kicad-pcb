---
name: jlc-production-review
description: Review JLCPCB factory production CAM and component placement against a frozen submission, or check BOM/CPL consistency before upload. Use for production-file comparisons, Gerber changes and placement confirmation preparation.
---

# JLCPCB production and placement review

Read [procedure](../../guides/skills/jlc-production-review/procedure.adoc), and [CAM tools](../../guides/skills/jlc-production-review/cam-diff.adoc) when executing comparisons.

Use the exact submitted manufacturing set. Preserve factory originals privately with hashes. Obtain files within actual user authorization. Calculate each notice's absolute deadline/timezone immediately; PCB and PCBA notices differ. Preselected website controls are not approval.

Check upload identity, align coordinates, compare layers, classify every difference, then separately check part identity, count, position, angle and polarity. Scripts: `scripts/render_compare.py`, `scripts/pixel_compare.py`, `scripts/check_inner_removals.py`; BOM/CPL: `scripts/check_bom_cpl.py`. Image dependencies are pinned in `scripts/requirements-cam.txt` for Python 3.12. Use fresh outputs outside sources.

Check current exit code AND JSON status. PASS is only the script's declared scope. WARNING requires explanation; INCOMPLETE/ERROR is not accepted. Raster geometry is not proof of electrical connectivity. Ask the factory for netlist-comparison evidence when needed. Do not infer placement shift from a viewer coordinate before establishing what it represents.

Prepare findings and clarification drafts. Sending, changing website confirmation choices, accepting factory changes/fees and approving production require explicit user authorization. Existing scoped authorization governs; a local review request alone is not manufacturing approval. Never change the frozen submission. Report pending questions and remaining time, not a blanket statement that manufacture is safe.

Use [supplier workflow](../../guides/skills/jlc-support/workflow.adoc) and [templates](../../guides/skills/jlc-support/templates.adoc) for correspondence. Without browser/mail tools, label status as user-supplied and continue file analysis.
