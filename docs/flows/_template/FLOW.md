# Flow: <business name>

> Entrypoint: `<METHOD> <path>` — `<Class.java:line>`
> Status: 🔍 investigating | 📝 reviewed | ✅ verified by IT tests
> Investigator session: <date> — ONE flow per session.

## Actors

<!-- Who/what participates: customer, mobile app, NAPAS, core banking... -->

## Preconditions

<!-- State that must exist before the flow runs. Each precondition cites where the code checks it. -->

## Steps (call chain)

| # | Step | Class.method | Side effects (DB/external/event) | Citation |
|---|---|---|---|---|
| 1 | | | | `file:line` |

## Data contract

### Given — tables SELECTed (the exact list of tables to seed, nothing more, nothing less)

| Table | Columns used in this flow | SQL at | Notes |
|---|---|---|---|

### Then — tables INSERTed/UPDATEd/DELETEd (the assertion list)

| Table | Operation | Columns changed | SQL at |
|---|---|---|---|

### [DYNAMIC-SQL] in this flow (if any)

<!-- List the concatenation branches + their conditions. Do NOT guess the final SQL. -->

## Business rules

> Every rule MUST carry a citation `file:line`. No citation = it does not get written down.
> "The code does X" (fact) — speculation goes to QUESTIONS.md tagged [ASSUMPTION].

| # | Rule | Condition | Error code / outcome | Citation |
|---|---|---|---|---|
| 1 | | | | `file:line` |

## External calls

| External | When called | Request/Response fixture | Timeout/error handling | Citation |
|---|---|---|---|---|

## Mobile cross-check

<!-- The server tells you WHAT the rule is; mobile tells you WHAT THE RULE IS CALLED in user language.
     Both agree = high confidence. They disagree = an expensive open question (often a real bug). -->

| Server rule | Does mobile validate before calling? | Error code → mobile message | Match? |
|---|---|---|---|

## Open questions

→ See `QUESTIONS.md` in this folder. Unconfirmed rules must NOT appear under Business rules.
