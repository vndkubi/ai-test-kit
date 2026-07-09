---
description: Investigate ONE business flow → docs/flows/<flow>/FLOW.md (uses the investigator agent)
argument-hint: <flow-slug from FLOW_BACKLOG.md>
---

Use the **investigator** subagent to investigate flow: **$ARGUMENTS**

## I/O contract

- Input: the flow's entrypoint in `docs/FLOW_BACKLOG.md` + the relevant rows of
  `docs/scan/HEATMAP.md` + `docs/scan/sql_inventory.json` (filtered to classes in the call chain).
- Output: `docs/flows/$ARGUMENTS/FLOW.md` (template `docs/flows/_template/FLOW.md`)
  + updates to `QUESTIONS.md`, `docs/GLOSSARY.md`.
- Forbidden: reading files outside the call chain; reading other flows' FLOW.md; modifying `src/`.

## Procedure, in order

1. Locate the entrypoint (REST/JMS/scheduler), record `Class.java:line`. ONE flow only.
2. Trace the call chain: at every step record side effects (DB tables read/written, external calls,
   events) + EVERY validation/exception branch (condition + error code).
2b. SQL mining: SQL VERBATIM + `file:line`; map each `?` to its Java field (read the `setXxx` code);
   SELECTed tables → "Given — to seed"; INSERT/UPDATE/DELETE → "Then — assertions";
   dynamic SQL → `[DYNAMIC-SQL]` + branch list, do NOT guess the final query.
3. Mobile cross-check: what does mobile validate before calling? which error code → which message
   (canonical business names from string resources)? Server–mobile mismatch = an expensive open question.
4. Write FLOW.md with every template section filled.

## Guardrails — violations mean redo

- A rule without a citation `file:line` does not get written. Speculation gets `[ASSUMPTION]` → QUESTIONS.md.
- New terms → GLOSSARY.md. Finish by reporting: rules / [ASSUMPTION]s / [DYNAMIC-SQL]s counts.
