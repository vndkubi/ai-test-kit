---
applyTo: "**/it/**"
description: "Integration test conventions: API-level, real DB, mock external only. Check Step 0 before assuming a stack."
---

# IT test conventions

## Step 0 — detect the target repo's OWN convention before assuming any stack

The 3 principles below (API-layer, real DB, mock only externals) are non-negotiable; the TOOLS are not.
Before writing anything: check the build file for an existing HTTP-level test client (REST-assured,
MockMvc/WebTestClient, Supertest, httpx/TestClient...) and an existing real-DB test setup (Testcontainers,
or a dev/CI database already wired to a test profile). If the repo already has a working convention —
even an unfamiliar one — read 2-3 existing tests and MATCH that shape; a second parallel test stack is
worse than adapting to an imperfect existing one. Only when nothing exists does introducing REST-assured +
Testcontainers + WireMock become the right call, and adding new build dependencies to a shared codebase
is a team-wide decision — propose it and get an explicit go-ahead first, don't add it unprompted for one
pilot flow.

## Stack & test boundary (default — a fresh JVM codebase with no existing convention)

- Test from the API LAYER: REST-assured firing HTTP at the real endpoint.
- REAL DB via Testcontainers — do NOT mock the DB or DAOs/repositories.
- Mock ONLY external APIs (NAPAS, core banking, partners, or this product's own third parties) with
  WireMock, replaying JSON fixtures from `src/test/resources/external/`.
- Java EE app server: consider MicroShed Testing (light) or Arquillian (heavy).
- Non-JVM stacks: same 3 principles, equivalent tools (Supertest/nock for Node, pytest +
  testcontainers-python for Python, etc.).

## Structure of every test — reads like a specification

```java
@Test @DisplayName("Rejects when daily limit exceeded: no transaction created, Napas not called")
void dailyLimitExceeded() {
    // Given — REAL data into the DB via PersistedScenarios, no mocks
    var ctx = persistedScenarios.validTransfer()
            .alreadyTransferredToday(vnd(450_000_000))
            .persist();
    napasMock.stubInquirySuccess();

    // When — through the API layer
    var res = given().body(transferRequest(ctx, vnd(100_000_000)))
            .post("/api/v1/transfers");

    // Then — response + DB side effects + external interactions
    res.then().statusCode(422).body("errorCode", is("ERR_DAILY_LIMIT"));
    assertThat(transactionTable.countFor(ctx.customer())).isZero();
    napasMock.verifyNoTransferCalled();
}
```

## Data per case

- Every test persists ITS OWN data (truncate before each test, or rollback). Shared SQL dumps are banned.
- The list of tables to seed = the **Given** section of FLOW.md (SELECTed tables) — nothing more, nothing less.
- DB without FKs: any seed order works, but a missing table fails as a confusing "query returns empty"
  instead of a constraint error — the data contract in FLOW.md substitutes for the FK's role.

## Assertions

- Assert all 3 layers per the **Then** section of FLOW.md: (1) HTTP response, (2) DB — which table gained
  a record / which column changed, (3) external — called or not called (`verifyNoInteractions` is a business assertion too).
- `@DisplayName` in business language; `@Nested` structure by situation, not by class.
- Every IT test maps to one scenario in SCENARIOS.md — record the ref in a comment or tag.

## Discipline when a test is red

- Red test = wrong analysis OR a real bug — both are valuable. Report the expected/actual diff.
- NEVER touch `src/main` to go green. NEVER weaken assertions. NEVER `@Disabled` to hide it.

## Discipline when confirming a test is GREEN

A build tool's cache can replay a stale "success" without executing anything (e.g. Gradle's
`FROM-CACHE`/`UP-TO-DATE`) — indistinguishable from a real pass in the summary line. Before trusting or
reporting GREEN — especially when re-verifying someone else's claim — force a clean rerun (ignore-cache
flag for your build tool) and read the actual per-test result file, not just the summary line.
