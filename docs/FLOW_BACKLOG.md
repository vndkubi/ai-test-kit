# FLOW BACKLOG — Order in which flows get investigated + tested

> Source: `docs/scan/ENTRYPOINTS.md` (scanner agent groups them and assigns human names).
> Priority = money-touching (×3) > high churn (CHURN.md) > incident history > touches core entities (HEATMAP.md table 2).
> The goal is NOT coverage % — the goal is **the number of flows with doc + tests**.
> One flow per investigation session. Flow N+1 is cheaper than flow N because fixtures compound.

| Priority | Flow (business name) | Entrypoint | Money | Churn | Incidents | Status | Notes |
|---|---|---|---|---|---|---|---|
| 1 | _Instant transfer 24/7 (example)_ | _POST /api/v1/transfers — TransferResource.java_ | ✅ | high | 2 | ⬜ backlog | pilot |
| | | | | | | | |

**Status:** ⬜ backlog → 🔍 investigating → 📝 FLOW.md reviewed → 📖 scenarios → 🧪 IT green → ✅ done (official doc)
