---
name: fixture-conventions
description: Mandatory conventions when creating/editing test fixtures - 2-layer Builder + Object Mother + Scenarios, 2-pass naming, Clock/Money helpers, external JSON fixtures. Use when writing builders, mother methods, scenario fixtures, PersistedScenarios, or JSON fixtures for external APIs.
---

# Fixture conventions (Builder + Object Mother + Scenarios)

Goal: a newcomer reading a test sees the "point of difference" immediately instead of 50 lines of
setup. The `fixtures/` directory doubles as the living glossary of the domain.

## Layer 1 — Builder (one per entity)

```java
public final class CustomerBuilder {
    // Default = the most "standard" customer PER PROD DATA: active, full KYC, resident
    private String id = "CUST-000001";
    private KycLevel kycLevel = KycLevel.LEVEL_2;
    private CustomerStatus status = CustomerStatus.ACTIVE;
    private LocalDate dob = LocalDate.of(1990, 1, 15); // fixed, never random

    public static CustomerBuilder aCustomer() { return new CustomerBuilder(); }
    public CustomerBuilder kycLevel(KycLevel v) { this.kycLevel = v; return this; }

    public Customer build() {
        // Build through the REAL production constructor/factory — NO reflection/setter bypass.
        // A fixture that creates an object production cannot create = a false-green test.
        return Customer.create(id, kycLevel, status, dob);
    }
}
```

Two rules decide the quality: (1) the default is ABSOLUTELY valid — a "slightly wrong" default puts
the noise back into every test; (2) build through production's official path.

## Layer 2 — Object Mother (the business language)

```java
public final class Customers {
    public static CustomerBuilder standardCustomer()   { return aCustomer(); }
    public static CustomerBuilder customerWithoutEkyc(){ return aCustomer().kycLevel(KycLevel.NONE); }
    public static CustomerBuilder frozenCustomer()     { return aCustomer().status(CustomerStatus.FROZEN); }
}
// Combine freely, no new method needed:
// Customers.customerWithoutEkyc().residency(NON_RESIDENT).build()
```

- ALWAYS return the **builder**, never a built object.
- The method name is a CONTRACT — override only what the name says, ≤3–4 overrides. A method taking
  parameters is doing the builder's job → delete it. A mother over ~15 methods → split by domain.
- New variants ONLY when present in `docs/FIXTURE_BACKLOG.md` with evidence.
- 2-pass naming: unconfirmed → honest technical name (`customerKycNoneStatusActive`) +
  `// TODO rename once BA confirms`; confirmed → IDE rename. NEVER block test-writing to
  "understand the business first".

## Layer 2.5 — Scenarios (the object graph for one flow)

```java
public final class Scenarios {
    public record TransferContext(Customer customer, Account source, Account dest, DailyLimit limit) {}

    /** Standard transfer setup: everything valid; each test overrides only its point of difference */
    public static TransferContext validTransfer() {
        Customer c = Customers.standardCustomer().build();
        return new TransferContext(c,
            Accounts.paymentAccount(c).balance(vnd(100_000_000)).build(),
            Accounts.internalDestinationAccount().build(),
            DailyLimits.remaining(vnd(500_000_000)));
    }
}
```

The entity list in a scenario = exactly the "Given" section of FLOW.md (SELECTed tables), nothing more.

## Time & Money — the two fintech traps

```java
public final class FixedTime {
    public static final Instant NOW = Instant.parse("2026-01-15T03:00:00Z");
    public static final Clock CLOCK = Clock.fixed(NOW, ZoneId.of("Asia/Ho_Chi_Minh"));
}
```

- Production injects `java.time.Clock` (Java EE: `@Produces Clock`) — never a direct `Instant.now()`;
  otherwise every daily-limit / cut-off / 24-7-session test goes flaky with the CI clock.
- One money helper: `vnd(600_000_000)`. Never random amounts — unseeded randomness is the enemy of
  characterization tests.

## External fixtures (JSON)

- `src/test/resources/external/napas/inquiry_account_not_found_04.json` — named by scenario.
- Deserialize through the EXACT production model: change the model, forget the fixture → red test
  immediately (self-defending contract documentation). Keep a `@ParameterizedTest` sweeping the
  directory so every file is guaranteed to parse.

## Sharing across modules (Maven)

Fixtures live in the domain module's `src/test/java`, published as a `test-jar`; other modules
consume `<type>test-jar</type> <scope>test</scope>`. Package: `com.company.domain.fixtures`.

## Anti-patterns — reject in review

- `public static final Customer VALID_CUSTOMER` — shared mutable; every method must be a factory call.
- A shared thousand-line SQL seed dump — use `PersistedScenarios` persisting the builder graph.
- The "almost right" fixture — the name says one thing, extra state set silently. A wrong name teaches
  newcomers the wrong business.
- Random/UUID on the assertion path — if persistence needs unique IDs, separate identity from what
  gets asserted.
