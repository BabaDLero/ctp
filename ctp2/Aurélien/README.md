# CTP 2 — Submission (Aurélien Ridard)

Data Quality: Measure, Clean, Test — 25 Nov (AM). Deliverables for the repo path `ctp/ctp2/Aurélien/`.

## What is in this folder

| # | Deliverable | File |
|---|-------------|------|
| 1 | Quality scorecard — 14 rules, 6 dimensions, severity + who fixes it | `quality_scorecard.csv` |
| 2 | Cleaned customers + replayable OpenRefine recipe | `customers_clean.csv` + `openrefine_customers_recipe.json` |
| 3 | Orders expectation suite (13 expectations: 3 given + all 7 TODOs) + Data Docs screenshot | `gx_orders.py` + `data_docs_screenshot.png` |
| 4 | Cents incident replay: history passes, `payments_batch_2.csv` fails | `gx_payments.py` |
| 5 | Missing governance guard (one sentence) | see below |

## One sentence: which governance guard was missing at ShopFast?

**The missing guard was the TEST guard (and the data contract behind it): no value-range or distribution expectation was watching the payment `amount` column, so the payment team's silent switch from euros to cents passed a suite that only checked nulls, uniqueness and allowed values.**

## Exercise results (measured)

- **Ex 1** — `profile_customers.py`: 1241 rows profiled; numbers in the scorecard (e.g. duplicate emails 168 rows, non-ISO country spellings 272 rows, bad signup_date format 303 rows, 15 spellings for 4 countries).
- **Ex 2** — `clean_customers.py` → `customers_clean.csv`: 1241 → 1233 rows (16 duplicate customer_id rows removed), all 9 recipe steps applied, self-check passes (country = FR/DE/ES/BE only, ISO dates 1233/1233, 0 duplicates, FR postal codes 5 digits). `openrefine_customers_recipe.json` is the equivalent OpenRefine operation history (sort → blank down → remove → transforms → GREL → is_duplicate_email flag) and replays the same steps on the original file.
- **Ex 3** — `gx_orders.py`: 13 expectations; 7 rules fail as expected (unique order_id ×14, orphan customer_id ×14, null order_date ×11, future dates ×5, bad status ×9, non-positive amount ×6). Data Docs: `gx/uncommitted/data_docs/local_site/index.html` (screenshot included).
- **Ex 4** — `gx_payments.py`: history = naive PASS / smart PASS; `payments_batch_2.csv` = naive PASS / **smart FAIL** (4 smart expectations: amount range ≤ 2000, mean 100–400, median 100–300, decimal format).

## How to run

```bash
python profile_customers.py
python clean_customers.py
python gx_orders.py      # Data Docs in gx/uncommitted/data_docs/local_site/index.html
python gx_payments.py
```

Scripts auto-locate the kit at `../shopfast-kit/data/` or `../install/shopfast-kit/data/`.
