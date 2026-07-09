---
mode: agent
description: "SCENARIOS.md → IT tests (REST-assured + Testcontainers + WireMock), the analysis-verification step"
---

# Generate IT tests for flow: ${input:flowName}

## I/O contract

- **Input:** `docs/flows/${input:flowName}/SCENARIOS.md` + `FLOW.md` (Data contract section)
  + built fixtures (`**/fixtures/**`).
- **Output:** IT tests in `src/test/**/it/<flow>/` + the "IT test" column filled in SCENARIOS.md's
  Coverage table + flow status in `docs/FLOW_BACKLOG.md`.
- **Forbidden:** touching `src/main`; weakening assertions; `@Disabled` to hide red tests.

## Requirements

1. Each scenario → one `@Test`; `@DisplayName` = the scenario name; `@Nested` grouped by situation.
2. Given/When/Then structure (see `it-tests.instructions.md`):
   - **Given:** `PersistedScenarios` seeding exactly the tables in FLOW.md's Given section + WireMock stubs for externals.
   - **When:** REST-assured through the API layer.
   - **Then:** assert all 3 layers — HTTP response; DB side effects per FLOW.md's Then section
     (new record / changed column / NO record); external called or not called.
3. Scenarios marked `⚠ awaiting BA` → still write the test, tag it `@Tag("assumption")` — run separately, never blocking CI.
4. Run the tests after writing them. Handle results:
   - **GREEN** → analysis verified; the scenario becomes official documentation; update Coverage + FLOW_BACKLOG.
   - **RED** → report the expected/actual diff against the corresponding FLOW.md#rule:
     either the AI misanalyzed (propose a FLOW.md fix — back to prompt 01) or it's a real bug (jackpot —
     report separately; do NOT touch src/main, do NOT bend the assertion to green).
5. Finish with a summary table — scenario / test / result / action.
