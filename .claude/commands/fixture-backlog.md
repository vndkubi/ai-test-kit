---
description: Derive a flow's fixture variants via the evidence rule → update FIXTURE_BACKLOG.md
argument-hint: <flow-slug>
---

Derive the fixture backlog for flow: **$ARGUMENTS**

## I/O contract

- Input: `docs/flows/$ARGUMENTS/FLOW.md` + `docs/scan/STATE_DIMENSIONS.md`
  + `docs/scan/HEATMAP.md` (table 2 centrality) + DB profiling results if available.
- Output: update `docs/FIXTURE_BACKLOG.md` (append/update; never delete someone else's row).
- Forbidden: building fixtures at this step (that is `/build-fixtures`); fabricating evidence.

## Derivation rule — machine-applicable

A variant enters the backlog **if and only if** it has ≥1 piece of evidence:
**(a)** a validation branch (citation from FLOW.md) / **(b)** exists in prod data (% from profiling)
/ **(c)** an external contract can return the state (JSON fixture).

- Builder default = the most common prod combination.
- Enum allows it but no evidence → row `AWAITING-BA — do not build` + `[ASSUMPTION]`.
- Variant already `built` by an earlier flow → just add this flow to "Needed by flow" (fixtures compound).
- Each `Requires: STATE:<name>` line in FLOW.md = one variant materializing that state — evidence (a)
  is the enforcement citation. When built, fill the state's Fixture column in the GLOSSARY State catalog.

## When prod numbers are missing

Use the **db-profiling** skill to generate GROUP BY / orphan-check queries for the top entities by
centrality (NEVER profile every table) for someone with access to run on read-only staging.
