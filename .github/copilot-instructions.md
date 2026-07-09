# Global guardrails — apply to EVERY request in this repo

## Evidence & citation
- Every business rule / behavior claim MUST carry a citation `file:line`. No citation = do not write it down.
- Separate fact from speculation: "the code does X" (fact, with citation) ≠ "the business probably wants X" (speculation).
  Tag speculation `[ASSUMPTION]` and put it in `docs/flows/<flow>/QUESTIONS.md` — NEVER under Business rules.
- Quote SQL VERBATIM. Never normalize/rewrite/reformat a query — one column renamed during paraphrase corrupts the data contract.
- Dynamically-built SQL (string concat, StringBuilder): tag `[DYNAMIC-SQL]`, list the branches, do NOT guess the final SQL.

## Session scope
- One session = ONE flow. Never "understand the whole system".
- Do not read files outside the call chain being traced. Do not summarize unrelated modules.
- Do not read another flow's FLOW.md unless the prompt asks for it.

## Glossary
- On encountering a new business term/enum/status code/error code → add it to `docs/GLOSSARY.md` with where it appears (file:line).

## Test discipline
- A red test is VALUABLE OUTPUT (wrong analysis or a real bug) — report it. NEVER touch `src/main` to make a test green.
  NEVER weaken an assertion to make a test pass.
- No random data on the assertion path (faker, UUID, `Instant.now()`). Time uses a fixed `Clock`.
- Fixture names come from `docs/FIXTURE_BACKLOG.md` — do not invent new names when the backlog already has one.

## Where knowledge lives
- Domain knowledge lives in `docs/` (FLOW.md, GLOSSARY.md, backlogs) — do NOT add domain knowledge to this file.
  This file holds only always-true guardrails; keep it under 50 lines.
