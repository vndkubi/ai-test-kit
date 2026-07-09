---
name: db-profiling
description: Generates DB profiling queries for fixture evidence - GROUP BY state combinations, orphan checks for SQL-inferred relationships when the DB has no FKs, runtime SQL capture. Use when prod-data evidence is needed for FIXTURE_BACKLOG, when verifying implicit relationships, or when tracing a flow's SQL on staging.
---

# DB profiling — evidence from real data

Principle: NEVER run directly against prod. Generate queries for someone with access to run on a
**read-only** staging/replica with anonymized data. Only profile the top entities by centrality
(HEATMAP.md table 2) — on a large product this is the difference between an afternoon and two weeks.

## 1. State-combination profiling (evidence b for FIXTURE_BACKLOG)

```sql
SELECT status, kyc_level, residency, COUNT(*) AS cnt
FROM customer
GROUP BY status, kyc_level, residency
ORDER BY cnt DESC;
```

Reading the result:
- Top-1 combination → the **builder default**.
- Rare but existing combinations → mother-method variants (record the % in the Evidence column).
- Combinations that never occur (even though the enum allows them) → do NOT build; `AWAITING-BA` row.
- Schema constraints (NOT NULL, CHECK, unique) = business rules the DBA already "documented" — record them too.

## 2. Orphan check — verifying SQL-inferred relationships (DB without FKs)

Relationships inferred from JOIN clauses or param mapping (`stmt.setString(1, customer.getId())`):

```sql
SELECT COUNT(*) AS orphans
FROM account a
LEFT JOIN customer c ON a.customer_id = c.id
WHERE c.id IS NULL AND a.customer_id IS NOT NULL;
```

- Orphans ~0 → relationship confirmed; record it in the implicit ER.
- Many orphans → wrong inference OR intentionally dirty data (soft-delete, old migrations) — both are
  expensive open questions → QUESTIONS.md, ask the BA.

## 3. A typical record as the builder default (evidence layer 4)

```sql
-- Take one "standard" record (the most common combination) for default values, instead of inventing numbers
SELECT * FROM customer WHERE status = 'ACTIVE' AND kyc_level = 'LEVEL_2'
ORDER BY created_at DESC FETCH FIRST 5 ROWS ONLY;
-- Remind the operator: anonymize before pasting results to any AI
```

## 4. Runtime SQL capture — ground truth for dynamic SQL

Static mining misses dynamic SQL. Ground truth: wrap the DataSource with p6spy or datasource-proxy
(Java EE: configure at the app server's connection pool), or enable the DB-side query log. Then:

1. Take the mobile app and perform EXACTLY ONE flow on staging (e.g., one transfer).
2. Capture the SQL sequence it fires → save as `docs/flows/<flow>/SQL_TRACE.log`.

That trace is the most accurate documentation that can exist for the flow: right order, right tables,
real params — no speculation, no hallucination. Diff the trace against FLOW.md's Data contract;
mismatch → fix FLOW.md to match the trace.
