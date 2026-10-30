# Codex + KiCad PCB laboratory

Read README.adoc, guides/01-how-it-works.adoc and the current experiment README/WORKLOG before working. This toolkit targets generic 7xsys/7xmod/7xmem designs; never infer family pinouts, voltages, timing or mechanics. JLCPCB is preferred.

- Use Codex as the only AI agent. Claude configuration/hooks are not required. Subagents are optional only when requested or otherwise authorized; ordinary work does not require them.
- One writer per project/editor. Coordinate live GUI buffers and disk edits; preserve recoverable source and complete libraries. Never regenerate a finished routed board from initialization code.
- Native KiCad files are authoritative. Native ERC/DRC, netlists, geometry readback and visual inspection provide evidence. Tool success is not electrical or hardware validation.
- Use tools/pcb-lab.py with KiCad Python for disposable experiments. Keep source, candidates, fixed releases and reports distinct. Do not overwrite examples or submitted manufacturing files.
- Respect the user's existing authorization for reversible local experiment work. Ask for missing electrical/mechanical decisions when they affect results. External messages, orders, payments and factory approvals need explicit authorization.
- Human docs are English AsciiDoc: maintained guides/ use leveloffset +1; internal dated docs/ use +2, with TOC, sectnums, highlight.js and experimental. Keep AGENTS.md and SKILL.md as Markdown machine entry points.
- Four skills live in skills/ and are exposed through .agents/skills/ relative links. Read only relevant references. The toolkit must stay together because translated references are under guides/skills/.
- Konnect is optional and archived upstream as of 2026-10-26. Pin and inspect actual tools before use. Our first routing path uses native KiCad DSN/SES and a separately selected local Freerouting release.
- Preserve LICENSE, NOTICE and provenance. Design/manufacturing example artifacts are immutable. Local experiments and private supplier data are ignored by the outer Git repository.
- After code changes, run relevant tests, script help and repository checks. After documentation changes, validate links and AsciiDoc rendering. Record precisely what was and was not exercised in docs/.
