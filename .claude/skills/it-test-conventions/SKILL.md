---
name: it-test-conventions
description: Conventions for fintech integration tests - test from the API layer with REST-assured, real DB via Testcontainers, mock ONLY externals with WireMock, data init per case. Use when writing/editing IT tests, setting up Testcontainers/WireMock/MicroShed, or asserting DB side effects.
---

# IT test conventions — API-level, real DB, mock external only

## Test boundary

- Test from the API LAYER: REST-assured firing HTTP at the real endpoint.
- REAL DB via Testcontainers — never mock the DB/DAOs/repositories.
- Mock ONLY externals (NAPAS, core banking, partners) with WireMock, replaying JSON fixtures
  from `src/test/resources/external/`.
- Java EE app server: MicroShed Testing (light, made for this use case) or Arquillian (heavy).

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
