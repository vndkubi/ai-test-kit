---
agent: test-writer
description: "SCENARIOS.md → IT tests (API-level, real DB, mock external only — see it-tests.instructions.md Step 0 for which tools), the analysis-verification step"
---

# Generate IT tests for flow: ${input:flowName}

## I/O contract

- **Input:** `docs/flows/${input:flowName}/SCENARIOS.md` + `FLOW.md` (Data contract section)
  + built fixtures (`**/fixtures/**`).
- **Output:** IT tests in `src/test/**/it/<flow>/` (or this repo's existing equivalent test layout —
  do not invent a second convention) + the "IT test" column filled in SCENARIOS.md's
  Coverage table + flow status in `docs/FLOW_BACKLOG.md`.
- **Forbidden:** touching `src/main`; weakening assertions; `@Disabled` to hide red tests; adding new
  test-infrastructure dependencies without an explicit go-ahead (see Step 0 in `it-tests.instructions.md` —
  a mature repo often already has its own API-layer + real-DB convention to match instead).

## Requirements

0. **Read `it-tests.instructions.md`'s Step 0 first**: detect whether this repo already has an
   API-layer test client + real-DB test setup before assuming REST-assured/Testcontainers/WireMock.
1. Each scenario → one `@Test`; `@DisplayName` = the scenario name; `@Nested` grouped by situation.
2. Given/When/Then structure (see `it-tests.instructions.md`):
   - **Given:** seed exactly the tables in FLOW.md's Given section (via `PersistedScenarios` or this
     repo's existing mechanism) + stub externals only (WireMock or this repo's existing fake).
   - **When:** drive the real API layer (REST-assured, or this repo's existing HTTP-level test client).
   - **Then:** assert all 3 layers — HTTP response; DB side effects per FLOW.md's Then section
     (new record / changed column / NO record); external called or not called.
3. Scenarios marked `⚠ awaiting BA` → still write the test, tag it `@Tag("assumption")` — run separately, never blocking CI.
4. Run the tests after writing them. Handle results:
   - **GREEN** → before trusting it, force a cache-free rerun and check the actual per-test result file
     (a build cache can replay a stale success). Then: analysis verified; the scenario becomes official
     documentation; update Coverage + FLOW_BACKLOG. Flow flips ✅ → remind the user to regenerate the
     onboarding rollup (prompt 06).
   - **RED** → report the expected/actual diff against the corresponding FLOW.md#rule:
     either the AI misanalyzed (propose a FLOW.md fix — back to prompt 01) or it's a real bug (jackpot —
     report separately; do NOT touch src/main, do NOT bend the assertion to green).
5. Finish with a summary table — scenario / test / result / action.
