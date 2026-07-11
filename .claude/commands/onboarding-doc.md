---
description: Regenerate ONBOARDING.md — derived top-down entry point for new devs (docs-only rollup)
argument-hint: (no arguments)
---

Use the **scanner** subagent to regenerate the onboarding rollup.

## I/O contract

- Input — files under the docs root + `docs/scan/` ONLY (this is a rollup, NOT an investigation):
  `FLOW_BACKLOG.md`, every `flows/*/FLOW.md` (header + Preconditions only), `GLOSSARY.md`
  (incl. State catalog), `FIXTURE_BACKLOG.md` (built counts), `scan/HEATMAP.md`.
  **Docs root** = the directory containing `FLOW_BACKLOG.md` — locate it by glob (`docs/` by default;
  namespaced deployments exist, e.g. `docs/testfixtures/`; scan output may still sit at `docs/scan/`).
- Output: `<docs-root>/ONBOARDING.md`, overwritten in full — it is a derived artifact, like a build output.
- Forbidden: reading ANY file outside the docs root and `docs/scan/` (especially `src/`); adding any
  claim that does not trace to an input file; editing any other file.

## Structure to generate (hard cap ~150 lines — depth belongs to links, not to this file)

1. Header: generation date · `X/Y flows ✅ verified` · last scan date ·
   "DERIVED FILE — do not edit by hand; regenerate with `/onboarding-doc`".
2. **What the system does** — 3–6 sentences composed ONLY from FLOW_BACKLOG flow names/domains.
3. **Flow map** — table grouped by domain: flow, entrypoint, status emoji (copied VERBATIM from
   FLOW_BACKLOG — never upgrade one), link to `flows/<flow>/SCENARIOS.md` where the folder exists.
   FLOW_BACKLOG is the ONLY status source; if a FLOW.md header disagrees, keep FLOW_BACKLOG's value
   and flag the mismatch in the Honesty footer.
4. **Dependency ladder** — collect every `Requires: STATE:<name>` line across FLOW.md files, join with
   the State catalog in GLOSSARY.md, render a mermaid graph (flow → requires → state; state → produced
   by → flow). Flows with no declared preconditions go under one line: "preconditions not yet declared
   (N flows)" — do NOT invent edges.
5. **Core data** — top ~10 tables by centrality from HEATMAP table 2, one line each (table → # flows).
6. **Minimal vocabulary** — ~15 GLOSSARY terms most relevant to the top flows, as links into GLOSSARY.md.
7. **First-week path** (fixed text): day 1 — this file + skim GLOSSARY; day 2–3 — pick ONE ✅ flow, read
   its SCENARIOS.md, run its IT tests green locally, step through with a debugger; week 2 — take one ⬜
   backlog flow through `/investigate-flow` → `/generate-it` with a reviewer.
8. Honesty footer: how many flows have only the scan map (never investigated); scan discrepancies if
   FLOW_BACKLOG lists any.

## Guardrails

- Every number, status, name must be copy-joinable from an input file. This doc adds STRUCTURE, never facts.
- Never invent runnable details: build commands, test class names, paths not present in an input file.
  When a step needs one (e.g. how to run tests), write "see the project README" instead of guessing.
- No business speculation: an ambiguous flow name is shown as-is, never explained with "probably".
- ≤150 lines. Anything that wants more space becomes a link to the source doc.
- End by reporting: flows counted, states in the ladder, flows without declared preconditions.
