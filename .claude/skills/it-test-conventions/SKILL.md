---
name: it-test-conventions
description: Conventions for integration tests - test from the API layer, real DB, mock ONLY externals, data init per case. Default stack for a fresh JVM codebase is REST-assured + Testcontainers + WireMock, but Step 0 below governs - use when writing/editing IT tests, setting up test infrastructure, or asserting DB side effects.
---

# IT test conventions — API-level, real DB, mock external only

## Step 0 — detect the target repo's OWN convention before assuming any stack

The 3 principles below (API-layer, real DB, mock only externals) are non-negotiable. The TOOLS used to
achieve them are not — a mature codebase usually already has an established way to hit its own API layer
with a real DB. Before writing anything:

1. Check the build file (`build.gradle`/`pom.xml`/`package.json`/`requirements.txt`...) for an existing
   HTTP-level test client (REST-assured, MockMvc/WebTestClient, Supertest, httpx/TestClient, etc.) and an
   existing real-DB test setup (Testcontainers, a dev/CI database already wired to a `test` profile, etc.).
2. If the repo ALREADY has a working convention (even an unfamiliar one) — READ 2-3 existing test files
   first and MATCH that shape. Introducing a second, parallel test stack is worse than adapting to an
   imperfect existing one.
3. Only when NO real-DB/API-layer convention exists at all does "introduce REST-assured + Testcontainers +
   WireMock" become the right call — and even then, adding new build dependencies to a shared codebase is a
   team-wide, hard-to-reverse decision. Propose it and get an explicit go-ahead before touching the build
   file; do not add new test-infrastructure dependencies unprompted for a single pilot flow.
4. Whatever stack you land on, the assertions below (3-layer: HTTP + DB + external) and the structure
   (situation-based `@Nested`, one test per scenario) are unchanged — only the plumbing differs.

## Test boundary (default stack — a fresh JVM codebase with no existing convention)

- Test from the API LAYER: REST-assured firing HTTP at the real endpoint.
- REAL DB via Testcontainers — never mock the DB/DAOs/repositories.
- Mock ONLY externals (NAPAS, core banking, partners, or whatever this product's own third parties are)
  with WireMock, replaying JSON fixtures from `src/test/resources/external/`.
- Java EE app server: MicroShed Testing (light, made for this use case) or Arquillian (heavy).
- Non-JVM stacks: use the equivalent — e.g. Supertest/nock (Node), pytest + testcontainers-python +
  responses (Python) — same 3 principles, different tools.

## Test structure — reads like a specification

```java
@DisplayName("Business flow: instant transfer 24/7")
class InstantTransferIT {

  @Nested @DisplayName("When the amount exceeds the daily limit")
  class ExceedsDailyLimit {

    @Test @DisplayName("rejects with ERR_DAILY_LIMIT, creates no transaction, does not call Napas")
    void dailyLimitExceeded() {
        // Given — REAL data into the DB, no mocks (scenario ref: SCENARIOS.md#daily-limit)
        var ctx = persistedScenarios.validTransfer()
                .alreadyTransferredToday(vnd(450_000_000))
                .persist();
        napasMock.stubInquirySuccess();

        // When — through the API layer
        var res = given().body(transferRequest(ctx, vnd(100_000_000)))
                .post("/api/v1/transfers");

        // Then — all 3 layers
        res.then().statusCode(422).body("errorCode", is("ERR_DAILY_LIMIT"));
        assertThat(transactionTable.countFor(ctx.customer())).isZero();
        napasMock.verifyNoTransferCalled();
    }
  }
}
```

- `@DisplayName` in business language; `@Nested` by SITUATION (never mirroring classes).
  The DisplayName tree in the test report = business documentation auto-verified every build.
- Each test maps to one scenario in SCENARIOS.md; record the ref in a comment.

## Data per case

- Every test persists ITS OWN data (truncate before each test, or rollback). Shared SQL dumps are BANNED.
- Tables to seed = exactly FLOW.md's Given section. DB without FKs: any seed order works, but a
  missing table fails as a confusing "query returns empty" — the FLOW.md data contract replaces the FK's role.

## Then — assert all 3 layers per FLOW.md's Then section

1. HTTP response (status + body).
2. DB side effects: new record / changed column / NO record
   (asserting the absence of interaction is a business assertion too).
3. External: called or not called, with the right payload.

## Discipline when a test is red

Red test = wrong analysis OR a real bug — both precious. Report the expected/actual diff pointing at
FLOW.md#rule. NEVER touch `src/main`, NEVER weaken assertions, NEVER `@Disabled` to hide.
`⚠ awaiting BA` scenarios → `@Tag("assumption")`, run separately, never blocking CI.

## Discipline when confirming a test is GREEN

A build tool's cache can replay a stale "success" without executing anything (e.g. Gradle's
`FROM-CACHE`/`UP-TO-DATE`, or an equivalent incremental-test skip in other tools) — this looks identical
to a real pass in the summary line. Before trusting or reporting a GREEN result — especially when
independently re-verifying someone else's claim — force a clean rerun (`--rerun --no-build-cache` for
Gradle, the equivalent "ignore cache" flag elsewhere) and read the actual per-test result file
(JUnit XML or equivalent), not just the "BUILD SUCCESSFUL" line.
