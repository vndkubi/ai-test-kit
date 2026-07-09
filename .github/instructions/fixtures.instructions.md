---
applyTo: "**/fixtures/**"
description: "Mandatory conventions for test fixtures: Builder + Object Mother + Scenarios"
---

# Fixture conventions (2 layers + scenarios)

## Architecture

- **Layer 1 — Builder** (`CustomerBuilder.aCustomer()`): one builder per entity.
  - Default = an ABSOLUTELY valid object, the most "standard" one per prod data (most common combination).
  - `build()` goes through the REAL production constructor/factory. NO reflection/setter bypassing
    validation — a fixture that creates an object production cannot create is a false-green test.
  - Fixed values, never random (`LocalDate.of(1990,1,15)`, no `faker`).
- **Layer 2 — Object Mother** (`Customers.customerWithoutEkyc()`): where the business language lives.
  - ALWAYS returns the **builder**, never a built object — tests can keep tweaking without new methods.
  - Each method overrides only what ITS NAME SAYS, ≤ 3–4 overrides. The method name is a contract;
    a wrong name teaches newcomers the wrong business.
  - A method that starts taking parameters (`customer(kycLevel, status)`) is doing the builder's job → delete it.
  - A mother exceeding ~15 methods → split by domain: `Customers`, `Accounts`, `Transfers`, `NapasResponses`.
- **Layer 2.5 — Scenarios** (`Scenarios.validTransfer()`): the full object graph for one flow
  (customer + account + limits...), returned as a context record. Everything valid; the test overrides
  only its "point of difference".

## Where new variants come from

- A new variant may ONLY be created when it exists in `docs/FIXTURE_BACKLOG.md` with evidence
  (validation branch file:line / prod data / external contract). Enum allows it but no evidence → do not build.
- 2-pass naming: unsure of the business name → use an honest technical name (`customerKycNoneStatusActive`),
  rename once the BA confirms. Never block writing tests waiting to "understand the business first".

## Time & Money

- `FixedTime.CLOCK` (Clock.fixed) for all time logic — never `Instant.now()`/`LocalDate.now()`.
- One money helper used everywhere: `vnd(600_000_000)` — not `new BigDecimal("600000000")` scattered around.

## External fixtures (JSON)

- Files named by scenario: `external/napas/inquiry_account_not_found_04.json`.
- Deserialize through the EXACT model production uses — someone changes the model and forgets the fixture
  → the test goes red immediately (self-defending contract documentation). Keep a `@ParameterizedTest`
  sweeping the whole directory to guarantee every file parses.

## Anti-patterns (reject in review)

- `public static final Customer VALID_CUSTOMER` — shared mutable instance; every method must be a factory call.
- A shared SQL seed dump (`fixtures.sql`, thousands of lines) — use `PersistedScenarios` persisting the builder graph.
- The "almost right" fixture: the name says one thing, extra state set because "an old test needed it".
- Random/UUID on the assertion path; if persistence needs unique IDs, separate identity from what gets asserted.
