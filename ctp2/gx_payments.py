"""CTP 2 - Exercise 4: replay the 'cents' incident.
A naive suite (not null / unique / allowed values) PASSES on payments_batch_2.csv although every amount is 100x too big.
Only value-range and distribution expectations catch it.
Run:  python gx_payments.py
Expected output: history -> naive PASS / smart PASS ; batch_2 -> naive PASS / smart FAIL
"""
import os
import pandas as pd
import great_expectations as gx

def find_kit():
    for cand in ("../shopfast-kit/data/", "../install/shopfast-kit/data/",
                 "../../install/shopfast-kit/data/", "install/shopfast-kit/data/"):
        if os.path.exists(cand + "payments.csv"):
            return cand
    raise FileNotFoundError("payments.csv not found - adjust KIT")

KIT = find_kit()
files = {"payments (history)": KIT + "payments.csv", "payments_batch_2 (new)": "payments_batch_2.csv"}

context = gx.get_context(mode="file")
source = context.data_sources.add_or_update_pandas("shopfast_payments")
asset = source.add_dataframe_asset(name="payments")
batch_def = asset.add_batch_definition_whole_dataframe("whole")
E = gx.expectations

naive = [E.ExpectColumnValuesToNotBeNull(column="payment_id"), E.ExpectColumnValuesToBeUnique(column="payment_id"),
         E.ExpectColumnValuesToNotBeNull(column="amount"), E.ExpectColumnValuesToBeInSet(column="currency", value_set=["EUR"]),
         E.ExpectColumnValuesToBeInSet(column="method", value_set=["card", "paypal", "apple_pay", "bank_transfer"])]
# Smart expectations: calibrated on the history (max 1400.79 EUR, mean 235.92, median 184.31).
# Every value of batch_2 is individually "valid" but 100x too big -> only distribution checks catch it.
smart = naive + [
    # 1. a single payment above ~1500 EUR never happened in the history (batch max: 37996 = 379.96 EUR x100)
    E.ExpectColumnValuesToBeBetween(column="amount", min_value=0, max_value=2000),
    # 2. the mean amount sits between 100 and 400 EUR in the history; batch_2 mean is 18922 -> x100 shift
    E.ExpectColumnMeanToBeBetween(column="amount", min_value=100, max_value=400),
    # 3. the median too: 184.31 in history vs 18488.5 in batch_2
    E.ExpectColumnMedianToBeBetween(column="amount", min_value=100, max_value=300),
    # 4. amounts are decimal strings ("217.38", "54.5"); cents-mode values are pure integers ("7879")
    E.ExpectColumnValuesToMatchRegex(column="amount_txt", regex=r"^\d+\.\d+$"),
]

def run(name, expectations, df):
    suite = context.suites.add_or_update(gx.ExpectationSuite(name=name))
    for e in expectations: suite.add_expectation(e.copy() if hasattr(e, "copy") else e)
    suite.save()
    return batch_def.get_batch(batch_parameters={"dataframe": df}).validate(suite)

for label, path in files.items():
    df = pd.read_csv(path, dtype=str); df["amount_txt"] = df["amount"]; df["amount"] = pd.to_numeric(df["amount"])
    for suite_name, exps in [("naive_payments", naive), ("smart_payments", smart)]:
        res = run(suite_name, exps, df)
        failed = [r.expectation_config.type for r in res.results if not r.success]
        print(f"{label:<24} {suite_name:<15} success={res.success}  failed={failed}")

print("\nExpected: history passes both suites, payments_batch_2 fails the smart suite (cents incident).")
print("Guard missing: the TEST guard - no value-range / distribution expectation was watching the amount column,")
print("so a unit change (euros -> cents) sailed through a suite that only checked nulls, uniqueness and allowed values.")
