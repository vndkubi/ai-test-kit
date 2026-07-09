# Global guardrails — apply to EVERY session in this repo

## Evidence & citation
- Every business rule / behavior claim MUST have a citation `file:line`. No citation = do not write it down.
- Separate fact from speculation: "the code does X" (fact, with citation) ≠ "the business probably wants X" (speculation).
  Tag speculation `[ASSUMPTION]` and put it in `docs/flows/<flow>/QUESTIONS.md` — NEVER under Business rules.
- Quote SQL VERBATIM. Never normalize/rewrite a query — one column renamed during paraphrase corrupts the data contract.
- Dynamically-built SQL (string concat, StringBuilder): tag `[DYNAMIC-SQL]`, list the branches, do NOT guess the final SQL.

## Session scope
- One session = ONE flow. Never "understand the whole system".
- Do not read files outside the call chain being traced. Do not summarize unrelated modules.

## Glossary
- On encountering a new business term/enum/status code/error code → add it to `docs/GLOSSARY.md` with where it appears.

## Test discipline
- A red test is VALUABLE OUTPUT (wrong analysis or a real bug) — report it. NEVER touch `src/main` to go green.
  NEVER weaken an assertion to make a test pass.
- No random data on the assertion path. Time uses a fixed `Clock`; money uses the `vnd()` helper.
- Fixture names come from `docs/FIXTURE_BACKLOG.md` — never invent new names when the backlog has one.

## Pipeline & role separation
- Pipeline: scan (scripts) → `/investigate-flow` → `/write-scenarios` → `/fixture-backlog`
  → `/build-fixtures` → `/generate-it`.
- Subagents: `scanner` (writes only docs/scan/ + FLOW_BACKLOG), `investigator` (read-only src, writes docs/flows/),
  `test-writer` (writes only src/test; src/main is off-limits).
- Domain knowledge lives in `docs/` — do NOT add domain knowledge to this file. Keep it under 50 lines.
