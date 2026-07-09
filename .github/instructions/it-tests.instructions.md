---
applyTo: "**/it/**"
description: "Integration test conventions: API-level, real DB, mock external only"
---

# IT test conventions

## Stack & test boundary

- Test from the API LAYER: REST-assured firing HTTP at the real endpoint.
- REAL DB via Testcontainers — do NOT mock the DB or DAOs/repositories.
- Mock ONLY external APIs (NAPAS, core banking, partners...) with WireMock,
  replaying JSON fixtures from `src/test/resources/external/`.
- Java EE app server: consider MicroShed Testing (light) or Arquillian (heavy).

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
