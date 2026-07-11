# Operating Guide — from scan output to living documentation

This guide picks up right after `scripts/scan/run_all.sh` has produced `docs/scan/*`.
It walks one flow through the whole pipeline, then shows how to scale.
Commands are given for both Claude Code (`/command`) and Copilot (prompt files); they are equivalent.

```
Step 0        Step 1           Step 2..6 (repeat per flow)                                      Step 7 (on ✅ / monthly)
scan  ───►  FLOW_BACKLOG ───►  investigate → scenarios → fixture-backlog → build-fixtures → generate-it → onboarding-doc
(scripts)   (scanner agent)    (investigator)  (main)       (main)          (test-writer)    (test-writer)   (scanner, docs-only)
```

---

## Step 0 — Run the scan (already done if you're reading this)

```bash
./scripts/scan/run_all.sh <SRC_DIR> <PKG_PREFIX> [CLASSES_DIR...]
# example: ./scripts/scan/run_all.sh backend/src/main com.odde backend/build/classes/java/main
```

What each output is for:

| File | Feeds | Meaning |
|---|---|---|
| `ENTRYPOINTS.md` | Step 1 | every candidate flow |
| `CHURN.md` | Step 1 | most-changed files = tests that pay off fastest |
| `deps.txt` | heatmap | class dependency edges (jdeps, or 03b import fallback) |
| `SQL_INVENTORY.md` + `.json` | Steps 2, 4 | every SQL statement, verbatim, tables read/written |
| `STATE_DIMENSIONS.md` | Step 4 | every enum/state field = fixture-variant candidates |
| `HEATMAP.md` | Steps 1, 4 | **the decisive artifact**: Flow × tables + table centrality |

No compiled classes? `run_all.sh` automatically falls back to the import-based graph (03b) — an
approximation, good enough to start. Rerun with jdeps once you have a build.

## Step 1 — Fill FLOW_BACKLOG (scanner agent, ~10 minutes)

Ask the **scanner** agent (cheap model is fine):

> Read docs/scan/ENTRYPOINTS.md, HEATMAP.md and CHURN.md. Group the entrypoints by domain,
> give each flow a human name, and fill docs/FLOW_BACKLOG.md ordered by:
> money-touching (×3) > churn > incident history > touches core entities.

Your review (2 minutes): the ordering must be explainable from the scan numbers. On a product
without money flows, churn × centrality decides — e.g. on doughnut, `Note.java` (churn 142) +
table `notebook` (26 flows) makes "create note" the obvious pilot.

**Pick exactly ONE pilot flow.** Do not start three.

## Step 2 — Investigate the pilot flow (investigator agent, 1 session)

```
Claude Code:  /investigate-flow create-note
Copilot:      run prompt 01-investigate-flow with flowName=create-note
```

The agent traces the call chain, mines the SQL for this flow, cross-checks the client
(mobile app — or the web frontend on a web product), and writes `docs/flows/create-note/FLOW.md`.

**Your review (5 minutes — citations only).** Open FLOW.md and check:

- every Business rule row has a `file:line` — spot-check 2–3 of them in the code;
- speculation sits in QUESTIONS.md tagged `[ASSUMPTION]`, not under Business rules;
- Data contract lists Given tables (to seed) and Then tables (to assert);
- dynamic SQL is tagged `[DYNAMIC-SQL]` with branches listed, not a guessed final query.

Reject the whole output if citations are missing — that is the contract. Do not fix it by hand;
re-run the prompt (and improve the prompt if the same mistake repeats: prompts are code).

## Step 3 — Write scenarios (~1 session)

```
Claude Code:  /write-scenarios create-note
Copilot:      prompt 02-write-scenarios
```

Output: `SCENARIOS.md` — Given/When/Then in plain user language, one scenario per rule,
each traceable back to `FLOW.md#rule-N (file:line)`.

**Parallel action, do not skip:** send `QUESTIONS.md` to your BA/domain expert now.
Their answers are the cheapest business-knowledge recovery you will ever get, and unblock
pass-2 fixture renames later. Places where server and client disagree are gold — often real bugs.

## Step 4 — Derive the fixture backlog (~30 minutes + one DB round-trip)

```
Claude Code:  /fixture-backlog create-note
Copilot:      prompt 03-fixture-backlog
```

The evidence rule (the agent applies it, you enforce it): a variant enters
`docs/FIXTURE_BACKLOG.md` **only** with ≥1 evidence — (a) a validation branch `file:line`,
(b) the combination exists in prod data, (c) an external contract returns that state.
Enum-allows-it-but-no-evidence → `AWAITING-BA`, not built.

If evidence (b) is empty the agent emits GROUP BY / orphan-check queries (db-profiling skill).
Have someone with access run them on **read-only staging, anonymized**, paste results back,
re-run the step. Only the top entities by centrality get profiled — never all tables.

## Step 5 — Build fixtures (test-writer agent)

```
Claude Code:  /build-fixtures create-note
Copilot:      prompt 04-build-fixtures
```

Output in `src/test/**/fixtures/`: Builders (valid defaults from prod data) → Mother methods
(named exactly as the backlog Variant column) → `Scenarios.validXxx()` (object graph = the Given
table list) → `PersistedScenarios` (persists that graph into the real DB) → external JSON fixtures.

Definition of done is mechanical: builds through the real constructor without blowing up;
combination has evidence; backlog rows flipped to `built`.

## Step 6 — Generate IT tests and run them (test-writer agent)

```
Claude Code:  /generate-it create-note
Copilot:      prompt 05-generate-it
```

Default stack (fresh JVM codebase, nothing established yet): REST-assured at the API layer +
Testcontainers (real DB) + WireMock (externals ONLY — on doughnut that's the OpenAI API; on a
fintech product, NAPAS/core banking). **But check first** — the it-test-conventions skill's Step 0
says to look for an existing API-layer + real-DB test convention before assuming this stack.
On the doughnut pilot, the target repo had ZERO of REST-assured/Testcontainers/WireMock as
dependencies; it already had its own convention (`@SpringBootTest` + `MockMvc` + a real dev/CI MySQL
+ `@Transactional` rollback) satisfying the same 3 principles (API-layer, real DB, mock external only)
with different tools. The right call was to match that, not bolt on a second stack — introducing new
build dependencies into a shared, mature codebase is a team-wide decision, not a pilot-flow one; ask
first.

Then the moment the whole pipeline exists for:

- **GREEN** → before trusting it, force a cache-free rerun and read the actual per-test result file —
  a build cache can replay a stale success that looks identical to a real pass in the summary line
  (this bit a verification pass on the doughnut pilot: a naive rerun returned Gradle's `FROM-CACHE`
  and would have looked green without executing anything). Once genuinely confirmed: the analysis is
  machine-verified, SCENARIOS.md is now official, trusted documentation. Update FLOW_BACKLOG status to ✅.
- **RED** → read the expected/actual diff against `FLOW.md#rule-N`. Two cases, both wins:
  the AI misread the code → fix FLOW.md (back to Step 2), or the code really does that → a bug
  found before any refactor. **Never** let anyone make it green by touching `src/main`,
  weakening the assertion, or `@Disabled`.

Tests tagged `@Tag("assumption")` (rules awaiting the BA) run in a separate CI job that never
blocks the build. When the BA answers: rename fixtures (pass 2), untag, update GLOSSARY.md.

## Step 7 — Regenerate the onboarding rollup (scanner agent, minutes)

```
Claude Code:  /onboarding-doc
Copilot:      run prompt 06-onboarding-doc
```

`ONBOARDING.md` (next to FLOW_BACKLOG.md) is the top-down entry point a new dev reads in 10 minutes
before anything else. It is **derived**: the generator reads docs/ ONLY — never src/ — and joins
FLOW_BACKLOG (map + statuses), the `Requires: STATE:` preconditions across FLOW.md files (the
dependency ladder), the GLOSSARY State catalog, and HEATMAP centrality. Structure and links only;
a claim that traces to no docs/ file must not survive review.

Generation runs bottom-up (evidence first), reading runs top-down (big picture first) — never
generate in the reading direction ("read the whole codebase, write the docs" = uncited speculation).

Regenerate when a flow flips ✅ (step 6 reminds you) and inside the monthly scan session.
Review is mechanical: spot-check that every statement links back to a docs/ file.
Flows investigated before the `Requires: STATE:` convention simply appear without dependency edges,
counted under "preconditions not yet declared" — declare states lazily when each flow is next touched.

**The onboarding loop this enables:** day 1 — ONBOARDING.md + skim GLOSSARY; day 2–3 — one ✅ flow:
read SCENARIOS.md, run its IT tests green locally, step through with a debugger; week 2 — the new dev
takes one ⬜ flow through steps 2→6 themselves. The guardrails make this safe (investigator is
read-only on src, test-writer can't touch src/main) — onboarding by contributing, not by reading.

---

## After the pilot — the operating loop

| Cadence | Action |
|---|---|
| per flow (1–2 days) | Steps 2→6. Flow N+1 is cheaper: check FIXTURE_BACKLOG first — needed fixtures are often already `built`. Flow flips ✅ → `/onboarding-doc` (minutes) |
| weekly | 15-minute review: FLOW_BACKLOG statuses, QUESTIONS.md answered vs pending, glossary growth |
| monthly | re-run `run_all.sh` in CI, diff `docs/scan/` — new endpoints/entities/enums surface as backlog items automatically; regenerate `ONBOARDING.md` in the same session |
| always | one flow per session; parallel work is safe because FIXTURE_BACKLOG is the naming coordination point |

Success metric: **number of flows with doc + green tests** — not coverage %.

## Failure modes to watch (and the built-in defense)

| Smell | Defense |
|---|---|
| Agent "summarizes the whole system" | session scope rule — reject, restart with one flow |
| Rules without `file:line` | citation rule — reject the output, don't patch by hand |
| Confident business explanations from nowhere | must be `[ASSUMPTION]` in QUESTIONS.md — evidence or it didn't happen |
| Test made green by editing src/main or softening asserts | test-writer role forbids it — treat as review-blocking |
| Fixture names invented ad hoc | names come from FIXTURE_BACKLOG only |
| Instructions file growing with domain knowledge | domain knowledge goes to docs/; instructions stay <50 lines |
| ONBOARDING.md hand-edited, or contains a claim with no docs/ source | derived-doc rule — fix the source doc and regenerate via `/onboarding-doc`; treat as review-blocking |
| Scan regex missing your codebase's patterns | scripts are code — extend them (Spring MVC support and the SIGPIPE fix both came from a real pilot) |

## Known approximations (fine to live with)

- JPQL yields entity names (`notewikititlecache`) alongside real table names
  (`note_wiki_title_cache`) — the scanner agent merges them when naming; the investigator
  confirms actual tables in Step 2.
- The import-based dep graph (03b) misses same-package references — swap in jdeps when a build exists.
- `[DYNAMIC-SQL]` entries are the investigator's job to resolve by reading branch code, or by
  runtime capture (db-profiling skill, section 4) — never by guessing.
