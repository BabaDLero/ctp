{% docs gross_revenue %}
**Gross revenue (EUR)** — total amount paid by the customer for an order, VAT included, shipping included, before refunds.
Owner: Head of Sales · Steward: Karim Benali · Status: approved (2026-11-10)
{% enddocs %}

{% docs net_revenue %}
**Net revenue (EUR)** — what ShopFast really keeps: gross revenue of the order minus refunds, **excluding VAT** (VAT is not our money), shipping fees included.
Formula: `net_revenue_eur = round((total_amount_eur − refunds) / 1.20, 2)` (French VAT rate of 20%).
Example: an order of €120 paid, fully refunded, gives net revenue €0; an order of €120 with no refund gives €100.
Owner: Paul Girard (Head of Finance) — decided for the board and the annual accounts · Steward: Karim Benali · Status: approved (2026-11-25).
Note: the Sales team needs VAT-included amounts for commissions — they must use gross_revenue, or ask for a **new term** ("net revenue incl. VAT"), never redefine this one.
{% enddocs %}

{% docs active_customer %}
**Active customer** — a customer account with at least one **non-cancelled** order in the **last 12 months**, counted as of the analysis date.
Formula: `max(order_date) >= current_date - 365` over orders whose status is not 'cancelled' (status pending/shipped/delivered/returned counts; cancelled does not).
Example: on 2026-11-25, a customer whose last order was 2026-01-10 (not cancelled) is active; a customer whose last order was 2025-10-01 is not.
Owner: Paul Girard (Head of Finance) — 12 months matches the investor year-over-year comparisons · Steward: Karim Benali · Status: approved (2026-11-25).
Note: Sales targets "recently active customers" with a 6-month window — that is a separate term (see recently_active_customer), not a redefinition of this one.
{% enddocs %}

{% docs recently_active_customer %}
**Recently active customer (6 months)** — a customer account with at least one **non-cancelled** order in the **last 6 months**; the segment the Sales dashboard and marketing campaigns work on.
Formula: `max(order_date) >= current_date - 183` over orders whose status is not 'cancelled'.
Example: on 2026-11-25, a customer whose last order was 2026-06-01 is recently active but a customer whose last order was 2026-02-01 is not (though still active).
Owner: Sara Martin (Head of Sales) — 6 months matches seasonal collections · Steward: Karim Benali · Status: approved (2026-11-25).
Note: created to settle the Sales/Finance conflict: one term = one definition; this term reuses the company rule for cancelled orders.
{% enddocs %}

{% docs churned_customer %}
**Churned customer** — a customer who is not active: no non-cancelled order in the last 12 months, i.e. `last_order_date < current_date - 365` (or NULL last_order_date and signed up more than 12 months ago).
Formula: `last_order_date < current_date - 365 OR last_order_date IS NULL`.
Example: on 2026-11-25, a customer whose last order was 2025-10-01 is churned; the churn-prediction model scores the customers at risk of joining this group.
Owner: Sara Martin (Head of Sales) · Steward: Karim Benali · Status: approved (2026-11-25).
{% enddocs %}

{% docs order %}
**Order** — a purchase transaction placed by a customer on the ShopFast site in one go (one row in fct_orders), whatever its current status.
Formula: identified by a unique `order_id`; statuses: pending → shipped → delivered, or returned / cancelled. Cancelled orders generate no revenue; returned orders are removed from net revenue through refunds.
Example: order 700002, placed 2026-10-08 on mobile_app for €217.38, delivered.
Owner: Sara Martin (Head of Sales) · Steward: Karim Benali · Status: approved (2026-11-25).
{% enddocs %}

{% docs customer %}
**Customer** — a person who created an account on the ShopFast site (one row in stg_customers / dim_customers, identified by customer_id). The same person may hold several accounts (duplicate emails), so customer count ≠ person count.
Formula: counted by `customer_id`; a customer exists from `signup_date` onwards.
Example: customer 10845, signed up in 2024, gold loyalty tier, one account.
Owner: Sara Martin (Head of Sales) · Steward: Karim Benali · Status: approved (2026-11-25).
{% enddocs %}
