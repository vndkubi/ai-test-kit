# AI Test Kit — Tests as Living Documentation for legacy fintech

Agents + instructions + skills + prompts + scan scripts to: excavate the business from code/DB/mobile
→ write flow docs with citations → human-language scenarios → IT tests (API-level, real DB, mock external only).
Root principle: **a correct analysis is one whose generated tests pass against the real system.**

## Layout (pre-installed at this repo root)

```
.github/                 GitHub Copilot adapter
  copilot-instructions.md   global guardrails (<50 lines — every request carries them)
  instructions/             scoped conventions via applyTo (fixtures / it-tests / flow-docs)
  prompts/                  workflow steps 01→05 (each with an explicit I/O contract)
  agents/                   scanner / investigator / test-writer (role separation via tools)
.claude/                 Claude Code adapter
  agents/                   same 3 roles (scanner runs on a cheap model)
  commands/                 /investigate-flow /write-scenarios /fixture-backlog /build-fixtures /generate-it
  skills/                   fixture-conventions / it-test-conventions / db-profiling
CLAUDE.md                Claude Code global guardrails
scripts/scan/            Phase 0 — mechanical, NO AI (cheap, deterministic, re-run monthly)
docs/                    Accumulated knowledge (docs growing over time is GOOD — growing instructions is a tax)
  GLOSSARY.md               living business dictionary
  FLOW_BACKLOG.md           flow order: money-touching(×3) > churn > incidents > core entities
  FIXTURE_BACKLOG.md        single source for fixture naming + the evidence rule
  flows/_template/          FLOW.md / SCENARIOS.md / QUESTIONS.md
```

## Operating pipeline

```
Week 0   ./scripts/scan/run_all.sh src/main com.company target/classes
         → scanner agent groups flows, fills FLOW_BACKLOG.md
Week 1   PILOT the single most important flow (usually: money transfer):
         01 investigate → review FLOW.md (5 minutes, citations only)
         02 scenarios   → send QUESTIONS.md to the BA in parallel
         03 fixture-backlog → 04 build-fixtures → 05 generate-it → run tests
           ├─ GREEN: analysis verified, scenario becomes official documentation
           └─ RED:   AI misread the code (fix FLOW.md) or a real bug (jackpot)
Week 2+  Scale horizontally, 1–2 flows/week/person. Flow N+1 is cheaper (fixtures compound).
Monthly  Re-run the scan in CI, diff the output → new flows/entities surface as backlog items.
```

The goal is NOT coverage % — it is **the number of flows with doc + tests**.

Step-by-step walkthrough with review checklists and failure modes: see **[GUIDE.md](GUIDE.md)**.

## Copilot ↔ Claude Code mapping

| Role | Copilot | Claude Code |
|---|---|---|
| Global guardrails (<50 lines, every request pays for them) | `.github/copilot-instructions.md` | `CLAUDE.md` |
| Per-file-type conventions (paid only when touching such files) | `.instructions.md` + `applyTo` | skills (auto-trigger via description) |
| Step-by-step workflows (on demand) | `.prompt.md` + `${input:flowName}` | slash commands + `$ARGUMENTS` |
| Role separation | `.agent.md` + tools | `.claude/agents/*.md` + tools + model |

Route models by agent: **scanner** = cheap model (formatting markdown needs no genius),
**investigator** = your strongest model (the quality-deciding step), **test-writer** = mid-tier.

## The 3 survival principles (if you remember only three things)

1. **One session, ONE flow.** "Understand the whole system" = the hallucination + token-burn recipe.
2. **No citation `file:line` = it doesn't get written.** Speculation gets `[ASSUMPTION]` → QUESTIONS.md → ask the BA.
3. **A red test is valuable output.** Never touch `src/main` to go green; never weaken an assertion.

## Prompts are code

Don't write 10 perfect prompts up front. Run the pilot; wherever the AI goes wrong, fix that prompt.
The scan scripts are starting heuristics — when a regex misses a pattern in your codebase, extend it:
they're your code now.
