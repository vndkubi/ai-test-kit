# GLOSSARY — Living business dictionary

> MANDATORY for every agent: on encountering a new business term / enum / status code / error code, add it here with the place it appears.
> Status: `[ASSUMPTION]` = inferred from code, not yet confirmed. `✅` = confirmed by BA/domain expert.
> After 2–3 months, a newcomer who reads this file plus the `fixtures/` directory knows every business noun in the system.

| Term / Code | Meaning (user language) | Source (file:line) | Status |
|---|---|---|---|
| _ERR_DAILY_LIMIT_ | _Daily transfer limit exceeded (mobile message: "You have exceeded your daily transfer limit")_ | _TransferValidator.java:87; strings.xml:214_ | _✅ (example)_ |
| | | | |

## State catalog — named states used in `Requires: STATE:<name>` preconditions

> The naming authority for states, same discipline as FIXTURE_BACKLOG for fixtures: investigator REUSES
> an existing state name before inventing one; a new state gets a row here in the same session.
> A state is what a prerequisite flow LEAVES BEHIND (session, auth level, enrollment) — flows depend on
> states, not on each other. `/fixture-backlog` fills the Fixture column when the state gets a fixture.
> `/onboarding-doc` joins this table with the `Requires:` lines to draw the dependency ladder.

| State | Meaning (user language) | Produced by flow | Representation (DB/cache/token) | Enforced at | Fixture (mother method) |
|---|---|---|---|---|---|
| _logged-in_ | _user has a valid session_ | _login_ | _sessions.status = ACTIVE_ | _SessionFilter.java:87_ | _loggedInCustomer() (example)_ |
| | | | | | |
