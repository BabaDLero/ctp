# CTP 3 — Submission (Aurélien Ridard)

Catalog, Lineage & Glossary — 25 Nov (evening). Deliverables for the repo path `ctp/ctp3/Aurélien/` (dbt + DuckDB catalog, ShopFast case).

## What is in this folder

| # | Deliverable | File |
|---|-------------|------|
| 1 | Governed staging + marts YAML (descriptions, owner/steward/domain/tier, PII tags + classifications, accepted_values tests) — `check_governance.py` prints **PASSED** | `_staging.yml` + `_marts.yml` + `exercise_outputs.txt` |
| 2 | 3 exposures (Sales dashboard, Finance monthly revenue report, churn-prediction ML model) + 5-line impact note for the cents change | `exposures.yml` + `impact_payments_cents.md` |
| 3 | Business glossary: 6 terms (5 required + `recently_active_customer` to settle the Sales/Finance conflict) as CSV and as dbt docs blocks, linked with `{{ doc() }}` in `_marts.yml` | `glossary_template.csv` + `glossary.md` |
| 4 | Data dictionary for the 15 columns of `stg_orders` and `stg_payments` (amount = EUROS with 2 decimals, NOT cents) + dbt export comparison | `data_dictionary_template.csv` + `data_dictionary_from_dbt.csv` + `dictionary_comparison.md` |

## Exercise results (measured)

- **Ex 1 — Document, own, classify**: every model and every column of the 7 models documented (58/58 columns), every model has owner/steward/domain/tier, PII columns tagged (`email`, `first_name`, `last_name`, `phone`, `birth_date` = confidential/restricted, `card_last4` = restricted), accepted_values tests added on `country_code`, `loyalty_tier`, `status`, `channel`, `shipping_country`, `method`, `currency`, `payment_status`. `dbt build`: 32 tests, **PASS=39 WARN=0 ERROR=0** (incl. 3 NO-OP exposures). `python check_governance.py` → `Models: 7 | documented columns: 58/58` / **GOVERNANCE CHECK: PASSED** (exit 0).
- **Ex 2 — Lineage & impact analysis**: `finance_monthly_revenue_report` (depends on `fct_orders`) and `churn_prediction_model` (depends on `dim_customers`) added → 3 exposures. `dbt ls --select source:shopfast_raw.payments+`: `stg_payments` → `fct_orders` → `dim_customers` → the 3 exposures. 5-line impact note in `impact_payments_cents.md` (what breaks, owners to warn, test to add, who approves).
- **Ex 3 — Glossary conflict settled**: company-wide **active customer = ≥ 1 non-cancelled order in the last 12 months** (Finance, investors) and **net revenue = gross − refunds, excluding VAT** (Finance). Sales keeps its 6-month view through a **new term** `recently_active_customer` (one term = one definition). Every term has: one sentence, a formula, an example, an owner, a decision date, status approved (2026-11-25). Definitions rendered on columns via `{{ doc('net_revenue') }}`, `{{ doc('gross_revenue') }}`, `{{ doc('active_customer') }}` in `_marts.yml`.
- **Ex 4 — Data dictionary**: 15 columns filled (business meaning, type, unit, allowed values, nullable, example, personal data, classification, owner, source system), verified against the data with `dbt show --select stg_payments --limit 5`. `stg_payments.amount` documented as **EUROS with 2 decimals — NOT cents**. Differences between my head and the code listed in `dictionary_comparison.md`.

## How to run

```bash
cd shopfast_dbt
dbt build
dbt docs generate && dbt docs serve --port 8080   # catalog + lineage
python check_governance.py                         # -> GOVERNANCE CHECK: PASSED
python export_dictionary.py                        # -> data_dictionary_from_dbt.csv
dbt ls --select source:shopfast_raw.payments+      # impact analysis downstream of payments
```

The YAML files shipped here are the exact files of the working `shopfast_dbt` project (`models/staging/_staging.yml`, `models/marts/_marts.yml`, `models/exposures.yml`, `models/glossary.md`).
