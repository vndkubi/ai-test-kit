# FIXTURE BACKLOG — Single source for fixture naming & priority

> **Derivation rule (machine-applicable):** a fixture variant enters the backlog **if and only if** it has ≥1 piece of evidence:
> - **(a)** a validation branch in code distinguishes that state (citation file:line), or
> - **(b)** the combination exists in prod/staging data with meaningful frequency (GROUP BY query), or
> - **(c)** an external contract can return that state (JSON fixture).
>
> Builder default = the most common combination in prod.
> Enum allows it but NO evidence exists → **do NOT build**; park it awaiting the BA (`AWAITING-BA` row).
>
> This file is the coordination point when several people work in parallel — names come from here, never invented ad hoc.
> 2-pass naming: Pass 1 = honest technical name matching the code → Pass 2 = rename to the business name once the BA confirms.

| Entity | Variant (mother method) | Evidence | Needed by flow | Status |
|---|---|---|---|---|
| _Customer_ | _default (ACTIVE, KYC_2)_ | _(b) 78% of prod rows_ | _*_ | _built (example)_ |
| _Customer_ | _frozenCustomer_ | _(a) TransferValidator.java:54; (b) 0.3% prod_ | _transfer, withdrawal_ | _backlog_ |
| _Account_ | _partiallyFrozenAccount_ | _[ASSUMPTION] enum exists, prod count = 0_ | _?_ | _AWAITING-BA — do not build_ |
| | | | | |

**Status:** backlog → built → (pass-2 rename if needed) | AWAITING-BA — do not build
