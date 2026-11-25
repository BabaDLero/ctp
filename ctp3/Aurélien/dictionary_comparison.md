# Dictionary comparison — what is in my head but not yet in the code

Compared `data_dictionary_template.csv` (hand-filled, 15 columns) with `data_dictionary_from_dbt.csv` (auto-exported from the dbt YAML by `export_dictionary.py`).

## What the YAML already carries (in the code)

- model, column, description, pii tag, classification, model owner, domain, tier — all 58/58 columns documented, governance check PASSED.

## What was only in my head (not yet in the YAML/code)

1. **data_type and unit/format** — the YAML descriptions say "EUROS with 2 decimals" in prose, but there is no machine-readable `unit` or `data_type` field; the cents incident would be prevented by a real contract field, not by a sentence.
2. **allowed values / ranges** — they exist as accepted_values *tests* for status/country/method, but columns like `amount` (13.70–1400.79) have no range test yet: the range lives in the dictionary, not in CI.
3. **nullable** — nothing in the YAML flags `order_date` (11 NULLs) or `card_last4` (NULL for non-card payments) as nullable; only the descriptions mention it.
4. **example values** — the docs blocks have examples in the glossary terms, but columns have no example field in dbt YAML.
5. **source system** — it is only in `_sources.yml` (one description for the whole raw landing zone), not per column as the dictionary requires.

## Conclusion

Next step to close the gap: add range/not_null tests on `amount` and `order_date`, and keep the CSV dictionary as the business-facing view exported from YAML so the two never drift.
