---
description: Build fixtures from FIXTURE_BACKLOG.md per conventions (uses the test-writer agent)
argument-hint: <flow-slug>
---

Use the **test-writer** subagent to build fixtures for flow: **$ARGUMENTS**

## I/O contract

- Input: `backlog` rows in `docs/FIXTURE_BACKLOG.md` whose "Needed by flow" includes this flow
  + `docs/flows/$ARGUMENTS/FLOW.md` (Data contract + Business rules) + existing fixture code.
- Output: code in `src/test/**/fixtures/` + row status flipped to `built`.
- Forbidden: touching `src/main`; building `AWAITING-BA` rows; variants outside the backlog.

## Build order (detailed conventions: fixture-conventions skill)

1. **Builders** for entities that lack one — default = most common prod combination, fixed values,
   built through the REAL constructor/factory (no reflection bypass).
2. **Mother methods** named exactly as the Variant column — 2-pass naming; unconfirmed names get
   `// TODO rename once BA confirms [QUESTIONS.md#N]`.
3. **Scenarios** — the object graph per FLOW.md's Given section, nothing more, nothing less.
4. **PersistedScenarios** — persists the graph into the real DB for IT tests; fresh data every call.
5. **External fixtures** — JSON per the External calls section, deserialized through the production model.

## Definition of done

1. Building through the real constructor/validator does not blow up. 2. The combination has evidence
in the backlog. 3. Every new mother method has a `built` row + new terms are in GLOSSARY.md.
