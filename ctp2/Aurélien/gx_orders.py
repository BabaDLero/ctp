"""CTP 2 - Exercise 3: expectation suite for ShopFast orders (GX Core 1.x) - completed starter.
Run:  python gx_orders.py
Data Docs after the run: gx/uncommitted/data_docs/local_site/index.html
"""
import os
import pandas as pd
import great_expectations as gx

def find_kit():
    for cand in ("../shopfast-kit/data/", "../install/shopfast-kit/data/",
                 "../../install/shopfast-kit/data/", "install/shopfast-kit/data/"):
        if os.path.exists(cand + "customers.csv"):
            return cand
    raise FileNotFoundError("customers.csv not found - adjust KIT")

KIT = find_kit()
orders = pd.read_csv(KIT + "orders.csv", dtype=str)
customers = pd.read_csv(KIT + "customers.csv", dtype=str)
orders["total_amount_eur"] = pd.to_numeric(orders["total_amount_eur"], errors="coerce")
orders["order_date_dt"] = pd.to_datetime(orders["order_date"], format="%Y-%m-%d", errors="coerce")  # typed copy for range checks

context = gx.get_context(mode="file")                       # creates ./gx/ (config + Data Docs)
source = context.data_sources.add_or_update_pandas("shopfast")
asset = source.add_dataframe_asset(name="orders")
batch_def = asset.add_batch_definition_whole_dataframe("all_orders")

suite = context.suites.add_or_update(gx.ExpectationSuite(name="orders_suite"))
E = gx.expectations
# Each rule is a business decision - the "why" is in the comment next to it.
for e in [
    E.ExpectTableRowCountToBeBetween(min_value=1000, max_value=100000),   # sanity: we never lose a whole load
    E.ExpectColumnValuesToNotBeNull(column="order_id"),                   # a row without id is unusable
    E.ExpectColumnValuesToBeUnique(column="order_id"),                    # duplicate id = double invoice (critical)
    # TODO 1: customer_id must not be null -> an order must be linked to a customer to be shipped/invoiced
    E.ExpectColumnValuesToNotBeNull(column="customer_id"),
    # TODO 2: customer_id must exist in customers (foreign-key check) -> orphan orders break invoicing and CRM joins
    E.ExpectColumnValuesToBeInSet(column="customer_id", value_set=sorted(customers["customer_id"].dropna().unique())),
    # TODO 3: order_date must not be null and must look like YYYY-MM-DD -> ISO format is the contract for all downstream tools
    E.ExpectColumnValuesToNotBeNull(column="order_date"),
    E.ExpectColumnValuesToMatchRegex(column="order_date", regex=r"^\d{4}-\d{2}-\d{2}$"),
    # TODO 4: no order in the future -> a future-dated order is an input error, it corrupts monthly revenue
    E.ExpectColumnValuesToBeBetween(column="order_date_dt", min_value=pd.Timestamp("2020-01-01"), max_value=pd.Timestamp.today()),
    # TODO 5: status only in the 5 allowed values (bad ones below are casing/typos: SHIPPED, Delivered, delivered , canceled)
    E.ExpectColumnValuesToBeInSet(column="status", value_set=["pending", "shipped", "delivered", "cancelled", "returned"]),
    # TODO 6: channel and shipping_country only in their allowed values (checked with value_counts: web/mobile_app/marketplace, FR/DE/ES/BE)
    E.ExpectColumnValuesToBeInSet(column="channel", value_set=["web", "mobile_app", "marketplace"]),
    E.ExpectColumnValuesToBeInSet(column="shipping_country", value_set=["FR", "DE", "ES", "BE"]),
    # TODO 7: total_amount_eur strictly positive and below a sensible maximum (observed max 1400.79; 5000 covers real orders, catches x100 incidents)
    E.ExpectColumnValuesToBeBetween(column="total_amount_eur", min_value=0, strict_min=True, max_value=5000),
]:
    suite.add_expectation(e)
suite.save()

vd = context.validation_definitions.add_or_update(gx.ValidationDefinition(name="orders_validation", data=batch_def, suite=suite))
checkpoint = context.checkpoints.add_or_update(gx.Checkpoint(name="orders_checkpoint", validation_definitions=[vd],
                                                             actions=[gx.checkpoint.UpdateDataDocsAction(name="docs")]))
result = checkpoint.run(batch_parameters={"dataframe": orders})

print("\nSuite passed:", result.success)
for vr in result.run_results.values():
    for r in vr.results:
        cfg = r.expectation_config
        print(f"{'PASS' if r.success else 'FAIL'}  {cfg.type:<45} {cfg.kwargs.get('column', ''):<18} unexpected={r.result.get('unexpected_count', '-')}")
print("\nOpen the report: gx/uncommitted/data_docs/local_site/index.html")
