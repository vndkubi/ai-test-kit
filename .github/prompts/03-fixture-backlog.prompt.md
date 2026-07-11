---
agent: agent
description: "Derive the fixture variants a flow needs → update docs/FIXTURE_BACKLOG.md"
---

# Derive fixture backlog for flow: ${input:flowName}

## I/O contract

- **Input:** `docs/flows/${input:flowName}/FLOW.md` + `docs/scan/STATE_DIMENSIONS.md`
  + `docs/scan/HEATMAP.md` (table 2 — centrality) + DB profiling results if available.
- **Output:** update `docs/FIXTURE_BACKLOG.md` (append/update rows; never delete someone else's row).
- **Forbidden:** building fixtures at this step (that is prompt 04's job); fabricating evidence.

## Derivation rule — machine-applicable, not gut feel

A fixture variant enters the backlog **if and only if** it has ≥1 piece of evidence:

- **(a)** a validation branch in code distinguishes the state — cite `file:line` from FLOW.md;
- **(b)** the combination exists in prod/staging data with meaningful frequency — record the % from profiling;
- **(c)** an external contract can return that state — record the corresponding JSON fixture.

Plus 3 decisions:

1. **Builder default** = the most common combination in prod (evidence b, highest frequency).
2. Enum allows it but NO evidence → row `AWAITING-BA — do not build`, tagged `[ASSUMPTION]`.
3. Variant already `built` by an earlier flow → just add this flow to its "Needed by flow" column;
   never create a duplicate row (fixtures compound — flow N+1 is cheaper than flow N).
4. Each `Requires: STATE:<name>` line in FLOW.md = one variant materializing that state — evidence (a)
   is the enforcement citation. When built, fill the state's Fixture column in the GLOSSARY State catalog.

## When prod numbers are missing

If evidence column (b) is empty, generate the queries for someone with access to run on staging (read-only):

```sql
SELECT status, kyc_level, residency, COUNT(*)
FROM customer GROUP BY 1,2,3 ORDER BY 4 DESC;
```

- ONLY generate queries for the top entities by centrality (HEATMAP.md table 2) — never profile 300 tables.
- Orphan check for relationships inferred from SQL (when the DB has no FKs):

```sql
SELECT COUNT(*) FROM account a
LEFT JOIN customer c ON a.customer_id = c.id
WHERE c.id IS NULL AND a.customer_id IS NOT NULL;
-- ~0 = relationship confirmed; many = wrong inference OR intentionally dirty data → QUESTIONS.md
```
