---
applyTo: "docs/flows/**"
description: "Conventions for flow documentation (FLOW.md, SCENARIOS.md, QUESTIONS.md)"
---

# Flow docs conventions

- One flow = one directory `docs/flows/<flow-slug>/` holding 3 files, templates in `docs/flows/_template/`:
  - `FLOW.md` — technical analysis; EVERY rule carries a citation `file:line`.
  - `SCENARIOS.md` — user language, Gherkin-lite (Given/When/Then), readable by BAs.
  - `QUESTIONS.md` — every `[ASSUMPTION]` lands here awaiting the BA.
- FLOW.md "Data contract" section: SELECTed tables = **Given** (to seed); INSERT/UPDATE/DELETE tables = **Then**
  (to assert). SQL verbatim; dynamic SQL tagged `[DYNAMIC-SQL]` + branches listed.
- SCENARIOS.md: each scenario maps to exactly ONE rule of FLOW.md, with `Source: FLOW.md#rule-N (file:line)`.
  Rules without a scenario must appear in the Coverage table at the end of the file — never silently skipped.
- Situation names come from mobile error messages when available (that's the product-approved
  translation of the business into user language).
- Flow status changes propagate back to `docs/FLOW_BACKLOG.md`.
