---
mode: agent
description: "Investigate ONE business flow → docs/flows/<flow>/FLOW.md (the quality-deciding step)"
---

# Investigate flow: ${input:flowName}

## I/O contract

- **Input:** 1 entrypoint from `docs/FLOW_BACKLOG.md` + `docs/scan/HEATMAP.md` (ONLY the rows relevant
  to this flow) + `docs/scan/sql_inventory.json` (filtered to classes in the call chain).
- **Output:** `docs/flows/${input:flowName}/FLOW.md` (template: `docs/flows/_template/FLOW.md`)
  + updates to `QUESTIONS.md`, `docs/GLOSSARY.md`.
- **Forbidden:** reading files outside the call chain; reading other flows' FLOW.md; modifying anything in `src/`.

## Mandatory procedure, IN ORDER

1. **Locate the entrypoint** (REST endpoint / JMS listener / scheduler) of this flow. ONE flow only.
   Record `Class.java:line`.

2. **Trace the call chain** from the entrypoint. At every step record:
   - Side effects: which DB tables are written/read, which external APIs are called, which events are fired.
   - EVERY validation/exception branch: its condition + the error code returned (each branch = one candidate business rule).

2b. **SQL mining for this flow** (check `sql_inventory.json` first, read code second):
   - For each DAO/repository call in the chain: extract the SQL **VERBATIM** + `file:line`.
   - For each `?` parameter: identify which Java field sets it (read the `setXxx` code).
   - SELECTed tables → "Given — data to seed". INSERT/UPDATE/DELETE tables → "Then — assertions".
   - Dynamically-built SQL → tag `[DYNAMIC-SQL]`, list the concatenation branches, do NOT guess the final SQL.

3. **Cross-check the mobile side** (the second witness):
   - What does mobile validate BEFORE calling this endpoint? (rules duplicated on both sides = important rules)
   - Which error code maps to which message? (take the CANONICAL BUSINESS NAMES from here — string resources)
   - Server and mobile disagree → an expensive open question, often a real bug.

4. **Write the output** per template: Actors / Preconditions / Steps / Data contract / Business rules /
   External calls / Mobile cross-check / Open questions.

## Guardrails — violations mean redo

- Every business rule MUST have a citation `file:line`. No citation = not written.
- "The code does X" (fact) ≠ "the business probably wants X" (speculation). Tag speculation `[ASSUMPTION]`
  → `QUESTIONS.md`, never under Business rules.
- New term/enum/status code → add to `docs/GLOSSARY.md` with where it appears.
- Finish by reporting: number of rules found, number of [ASSUMPTION]s, number of [DYNAMIC-SQL]s — for a fast review.
