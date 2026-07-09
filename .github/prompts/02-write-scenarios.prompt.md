---
mode: agent
description: "FLOW.md → SCENARIOS.md: Gherkin-lite scenarios in user language, readable by everyone"
---

# Write business scenarios for flow: ${input:flowName}

## I/O contract

- **Input:** `docs/flows/${input:flowName}/FLOW.md` — do NOT read source code (context cut;
  if FLOW.md lacks the information needed for a scenario, that is FLOW.md's defect → log it in QUESTIONS.md).
- **Output:** `docs/flows/${input:flowName}/SCENARIOS.md` (template: `docs/flows/_template/SCENARIOS.md`).
- **Forbidden:** reading `src/`; inventing rules not present in FLOW.md.

## Requirements

1. Every rule in FLOW.md → at least ONE Given/When/Then scenario in ORDINARY USER language:

   ```markdown
   ## Scenario: Transfer exceeding the daily limit
   - Given: a customer with level-2 eKYC who has already transferred 450M today, daily limit 500M
   - When: they transfer another 100M via Napas
   - Then: rejected with the message "You have exceeded your daily transfer limit"
     (ERR_DAILY_LIMIT), no transaction is created, Napas is not called
   - Source: FLOW.md#rule-3 (TransferValidator.java:87)
   ```

2. Situation names + wording come from the mobile error messages in FLOW.md's Mobile cross-check section
   (the product-approved business wording) — do not invent your own phrasing.
3. "Then" must state all 3 observables: the message/outcome, whether a transaction was created,
   whether the external was called — matching FLOW.md's Then section.
4. End of file: the **Coverage per rule** table. Rules without a scenario must be listed —
   coverage is counted per rule, not per line.
5. Rules tagged `[ASSUMPTION]` → mark the scenario `⚠ awaiting BA confirmation`; never present it as fact.
