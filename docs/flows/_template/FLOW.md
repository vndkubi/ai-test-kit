# Flow: <business name>

> Entrypoint: `<METHOD> <path>` — `<Class.java:line>`
> Status: 🔍 investigating | 📝 reviewed | ✅ verified by IT tests
> Investigator session: <date> — ONE flow per session.

## Actors

<!-- Who/what participates: customer, mobile app or web frontend, and this product's own externals
     (e.g. NAPAS/core banking for a fintech product, a payment gateway, an LLM API, a CMS...). -->

## Preconditions

<!-- State that must exist before the flow runs. Each precondition cites where the code checks it.
     Machine-readable line (feeds the ONBOARDING dependency ladder):
       - Requires: STATE:<name> — enforced at <file:line>
     State names: reuse from the State catalog in GLOSSARY.md; a new state gets registered there first.
     ⚠ Auth/step-up checks usually live in cross-cutting code (security filter chain, interceptor,
     @PreAuthorize, AOP) — check there before concluding "no preconditions". -->

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

## Client cross-check (mobile app, or the web frontend if the product has no mobile app)

<!-- The server tells you WHAT the rule is; the client tells you WHAT THE RULE IS CALLED in user
     language. Both agree = high confidence. They disagree = an expensive open question (often a
     real bug). -->

| Server rule | Does the client validate before calling? | Error code → client message | Match? |
|---|---|---|---|

## Open questions

→ See `QUESTIONS.md` in this folder. Unconfirmed rules must NOT appear under Business rules.
