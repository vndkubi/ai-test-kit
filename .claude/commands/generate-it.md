---
description: SCENARIOS.md → IT tests (REST-assured + Testcontainers + WireMock), the analysis-verification step
argument-hint: <flow-slug>
---

Use the **test-writer** subagent to generate IT tests for flow: **$ARGUMENTS**

## I/O contract

- Input: `docs/flows/$ARGUMENTS/SCENARIOS.md` + `FLOW.md` (Data contract) + built fixtures.
- Output: IT tests in `src/test/**/it/<flow>/` + the Coverage table updated in SCENARIOS.md
  + flow status in `docs/FLOW_BACKLOG.md`.
- Forbidden: touching `src/main`; weakening assertions; `@Disabled` to hide red tests.

## Requirements (detailed conventions: it-test-conventions skill)

1. Each scenario → one `@Test`; `@DisplayName` = the scenario name; `@Nested` by situation.
2. Given: `PersistedScenarios` seeding exactly the Given tables + WireMock stubs (external is the ONLY mock).
   When: REST-assured through the API layer. Then: assert 3 layers — HTTP response, DB side effects
   per the Then section, external called/not called.
3. `⚠ awaiting BA` scenarios → still write the test, `@Tag("assumption")`, run separately, never blocking CI.
4. Run the tests:
   - **GREEN** → analysis verified; update Coverage + FLOW_BACKLOG.
   - **RED** → report the expected/actual diff against FLOW.md#rule: either the AI misanalyzed
     (propose the FLOW.md fix, back to `/investigate-flow`) or a real bug (jackpot — report separately,
     do NOT touch src/main).
5. Finish with a summary table — scenario / test / result / action.
