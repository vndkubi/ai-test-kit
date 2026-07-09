---
mode: agent
description: "Build fixtures from FIXTURE_BACKLOG.md per conventions (Builder + Mother + Scenarios)"
---

# Build fixtures for flow: ${input:flowName}

## I/O contract

- **Input:** `backlog` rows in `docs/FIXTURE_BACKLOG.md` whose "Needed by flow" includes this flow
  + `docs/flows/${input:flowName}/FLOW.md` (Data contract + Business rules)
  + existing fixture code in `**/fixtures/**` (to avoid duplication).
- **Output:** code in `src/test/**/fixtures/` + row status flipped to `built` in the backlog.
- **Forbidden:** touching `src/main`; building `AWAITING-BA` rows; creating variants not in the backlog.

## Build order

1. **Builders** for entities that lack one (default = most common prod combination, fixed values,
   built through the real constructor/factory — see `fixtures.instructions.md`).
2. **Mother methods** for each backlog variant — named exactly as the Variant column
   (2-pass naming: technical name if unconfirmed, with `// TODO rename once BA confirms [QUESTIONS.md#N]`).
3. **Scenario** for the flow (`Scenarios.validTransfer()` or equivalent): the full object graph
   per FLOW.md's Given section — exactly the SELECTed tables, nothing more, nothing less.
4. **PersistedScenarios**: the layer persisting that graph into the real DB (takes EntityManager/DataSource),
   used by IT tests — every call persists FRESH data, no shared state.
5. **External fixtures**: JSON files per FLOW.md's External calls section, named by scenario,
   loaded through the production model.

## Definition of done

- The 3-question checklist a machine can answer (works even when the author doesn't know the business):
  1. Does building through the real constructor/validator blow up? (blow up = invalid state)
  2. Does the combination exist in prod data? (evidence b in the backlog)
  3. Does a test using it pass against real behavior? (verified in prompt 05)
- Every new mother method has a `built` row in the backlog + new terms added to `docs/GLOSSARY.md`.
