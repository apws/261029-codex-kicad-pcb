---
name: jlc-support
description: Prepare verifiable JLCPCB support and engineering correspondence, quote/status questions, production-file clarification and approval deadlines. Use when drafting supplier messages or organizing order follow-up.
---

# JLCPCB supplier communication

Read [workflow](../../guides/skills/jlc-support/workflow.adoc). Use [templates](../../guides/skills/jlc-support/templates.adoc) for drafts, [deadlines](../../guides/skills/jlc-support/deadlines.adoc) for historical context, and [pitfalls](../../guides/skills/jlc-support/pitfalls.adoc) when a similar issue arises. The [case study](../../guides/skills/jlc-support/case-study.adoc) is optional background.

Check detailed order status, the registered mailbox including spam, and the latest conversation. Record actual time/timezone and identifiers privately. Verify tool account and actual evidence before saying an email was sent or an action completed. If connectors are unavailable, use provided material and label the evidence accordingly.

Write a self-contained message: subject/action/reference, verified background, impact, numbered questions, responsible owner/next-update fallback, boundary sentence and thanks. Technical questions need coordinate frame and annotated evidence. Keep refund/compliance questions in separate threads; follow up only on remaining questions.

Sending requires explicit authorization; scoped preauthorization for inquiries applies only within its scope/expiry and must be recorded. Do not infer approval of production, design changes, fees, compensation, orders or payment. The user handles personal/payment information. Drafting and authorized local analysis can proceed without repeated permission prompts.

Use `scripts/deadline.py --received "TIMESTAMP" --tz +08:00 --hours 72` with the actual notice's duration/timezone. Record exact absolute deadline; exit 0 means not due, 1 overdue, 2 invalid input. Historical 48/72-hour notices are not current guarantees.

Provide verified-source note, authorization scope, channel, deadline and full English draft. Keep original correspondence privately. Stop on final rejection, completed requested deliverable, lost access or a user pause; reassurance alone is not completion. Do not automatically send periodic reminders. Factory geometry review belongs to the production-review procedure.
