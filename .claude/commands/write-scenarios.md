---
description: FLOW.md → SCENARIOS.md Given/When/Then scenarios in user language, readable by everyone
argument-hint: <flow-slug>
---

Write the business scenarios for flow: **$ARGUMENTS**

## I/O contract

- Input: `docs/flows/$ARGUMENTS/FLOW.md` — do NOT read source code (if FLOW.md lacks information,
  that is FLOW.md's defect: log it in QUESTIONS.md, do not go read src to compensate).
- Output: `docs/flows/$ARGUMENTS/SCENARIOS.md` (template `docs/flows/_template/SCENARIOS.md`).
- Forbidden: reading `src/`; inventing rules not present in FLOW.md.

## Requirements

1. Every rule → ≥1 Given/When/Then scenario in ORDINARY USER language, with
   `Source: FLOW.md#rule-N (file:line)`.
2. Wording comes from the mobile error messages (Mobile cross-check section) — the product-approved
   business phrasing.
3. "Then" states all 3 observables: message/outcome + transaction created or not + external called or not.
4. End of file: the Coverage-per-rule table — rules without a scenario must be listed explicitly.
5. `[ASSUMPTION]` rules → mark the scenario `⚠ awaiting BA confirmation`; never present it as fact.
