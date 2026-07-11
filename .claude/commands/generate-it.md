---
description: SCENARIOS.md → IT tests (API-level, real DB, mock external only — see it-test-conventions Step 0 for which tools), the analysis-verification step
argument-hint: <flow-slug>
---

Use the **test-writer** subagent to generate IT tests for flow: **$ARGUMENTS**

## I/O contract

- Input: `docs/flows/$ARGUMENTS/SCENARIOS.md` + `FLOW.md` (Data contract) + built fixtures.
- Output: IT tests in `src/test/**/it/<flow>/` (or this repo's existing equivalent test layout, if one
  already exists — do not invent a second convention) + the Coverage table updated in SCENARIOS.md
  + flow status in `docs/FLOW_BACKLOG.md`.
- Forbidden: touching `src/main`; weakening assertions; `@Disabled` to hide red tests; adding new
  test-infrastructure dependencies (Testcontainers/REST-assured/WireMock or equivalents) without an
  explicit go-ahead — check it-test-conventions Step 0 first, a mature repo often already has its own
  API-layer + real-DB convention to match instead.

## Requirements (detailed conventions: it-test-conventions skill, START WITH ITS STEP 0)

1. Each scenario → one `@Test`; `@DisplayName` = the scenario name; `@Nested` by situation.
2. Given: seed exactly the Given tables (via `PersistedScenarios` or this repo's existing fixture-persist
   mechanism) + stub externals only (WireMock, or whatever this repo already uses to fake externals).
   When: drive the real API layer (REST-assured, or the repo's existing HTTP-level test client).
   Then: assert 3 layers — HTTP response, DB side effects per the Then section, external called/not called.
3. `⚠ awaiting BA` scenarios → still write the test, `@Tag("assumption")`, run separately, never blocking CI.
4. Run the tests:
   - **GREEN** → before trusting it, force a cache-free rerun and check the actual per-test result file
     (a build cache can replay a stale success). Then: analysis verified; update Coverage + FLOW_BACKLOG.
     Flow flips ✅ → remind the user to regenerate the onboarding rollup (`/onboarding-doc`).
   - **RED** → report the expected/actual diff against FLOW.md#rule: either the AI misanalyzed
     (propose the FLOW.md fix, back to `/investigate-flow`) or a real bug (jackpot — report separately,
     do NOT touch src/main).
5. Finish with a summary table — scenario / test / result / action.
