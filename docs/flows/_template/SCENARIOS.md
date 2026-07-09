# Business scenarios: <flow name>

> Documentation for EVERYONE: BAs can read it, newcomers can read it, and every scenario traces back to code.
> Written in user language (take names from mobile error messages when available).
> CONSTRAINT: each scenario maps to exactly ONE rule in FLOW.md. Coverage is counted per rule, not per line.

## Scenario: <situation name, in user language>

- **Given:** <initial state — what the customer looks like, the account state, what happened before>
- **When:** <the action the user performs>
- **Then:** <observable outcomes: message shown, transaction created or not, external called or not>
- **Source:** FLOW.md#rule-N (`file:line`)

<!-- ... repeat per rule ... -->

---

## Coverage per rule

| Rule (FLOW.md) | Scenario | IT test |
|---|---|---|
| rule-1 | ✅ Scenario "..." | `XxxIT.java` |
| rule-2 | ⬜ NO scenario yet | — |

> Rules without a scenario MUST be listed here — never silently skipped.
