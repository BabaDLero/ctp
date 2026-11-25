"""CTP 2 - Exercise 2: clean customers.csv with a replayable recipe.
Run from the 02_CTP2 folder:  python clean_customers.py
Produces: customers_clean.csv (in this script's folder)
The same 9 steps are documented as an OpenRefine operation history in openrefine_customers_recipe.json.
"""
import os
import re
import pandas as pd

def find_kit():
    for cand in ("../shopfast-kit/data/", "../install/shopfast-kit/data/",
                 "../../install/shopfast-kit/data/", "install/shopfast-kit/data/"):
        if os.path.exists(cand + "customers.csv"):
            return cand
    raise FileNotFoundError("customers.csv not found - adjust KIT")

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = find_kit()
df = pd.read_csv(KIT + "customers.csv", dtype=str)
print("Before:", len(df), "rows")

# 1. Remove the exact duplicate rows: sort by customer_id, reorder permanently,
#    blank down customer_id, facet blanks, remove the blank rows (-> keeps 1 row per customer_id)
df = df.sort_values("customer_id", kind="stable").drop_duplicates(keep="first").reset_index(drop=True)
df["customer_id"] = df["customer_id"].where(~df["customer_id"].duplicated(), None)   # blank down
df = df[df["customer_id"].notna()].reset_index(drop=True)                            # remove blanks
print("After dedup:", len(df), "rows")

# 2. Names: trim + collapse spaces + To titlecase
name_expr = lambda s: s.fillna("").str.strip().str.replace(r"\s+", " ", regex=True).str.title()
df["first_name"] = name_expr(df["first_name"])
df["last_name"] = name_expr(df["last_name"])

# 3. Email: value.trim().toLowercase()
df["email"] = df["email"].fillna("").str.strip().str.lower()

# 4. Country: 18 spellings -> FR, DE, ES, BE (trim + lower + cluster)
df["country"] = (df["country"].fillna("").str.strip().str.lower()
                 .replace({"france": "FR", "fra": "FR", "germany": "DE", "deu": "DE", "allemagne": "DE",
                           "spain": "ES", "espagne": "ES", "belgium": "BE", "bel": "BE", "belgique": "BE"})
                 .str.upper())

# 5. Dates signup_date and birth_date -> YYYY-MM-DD
def to_iso(v):
    if pd.isna(v) or re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
        return v
    m = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", v)          # 25/03/2024 -> 2024-03-25
    if m:
        return f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
    m = re.fullmatch(r"(\d{2})-(\d{2})-(\d{4})", v)          # 03-25-2024 -> 2024-03-25
    if m:
        return f"{m.group(3)}-{m.group(1)}-{m.group(2)}"
    if re.fullmatch(r"\d{4}/\d{2}/\d{2}", v):
        return v.replace("/", "-")                           # 2024/03/25 -> 2024-03-25
    return v
df["signup_date"] = df["signup_date"].map(to_iso)
df["birth_date"] = df["birth_date"].map(to_iso)

# 6. Loyalty tier: lower case, fix "platinium"
df["loyalty_tier"] = (df["loyalty_tier"].fillna("").str.strip().str.lower()
                      .replace({"platinium": "platinum"}))

# 7. French postal codes with 4 digits -> add the missing leading 0
def postal(v, country):
    if pd.isna(v):
        return v
    v = v.strip()
    if country == "FR" and len(v) == 4:
        return "0" + v
    return v
df["postal_code"] = [postal(v, c) for v, c in zip(df["postal_code"], df["country"])]

# 8. Phones -> +33612345678 format
def phone(v):
    if pd.isna(v):
        return v
    v = re.sub(r"[^0-9+]", "", v.strip())
    if v.startswith("0033"):
        return "+33" + v[4:]
    if v.startswith("0") and len(v) == 10:
        return "+33" + v[1:]
    return v
df["phone"] = df["phone"].map(phone)

# 9. Email duplicates: flag, do not delete (is_duplicate_email = true/false)
em = df["email"].str.strip().str.lower()
df["is_duplicate_email"] = em.duplicated(keep=False).map({True: "true", False: "false"})

out = os.path.join(HERE, "customers_clean.csv")
df.to_csv(out, index=False)
print("Wrote", out, "-", len(df), "rows, columns:", list(df.columns))

# Quick self-check on the cleaned file
print("\nSelf-check on customers_clean.csv:")
print("  country values:", sorted(df["country"].unique()))
print("  tier values:", sorted(df["loyalty_tier"].unique()))
print("  signup ISO ok:", int(df["signup_date"].str.match(r"^\d{4}-\d{2}-\d{2}$").sum()), "/", len(df))
print("  dup customer_id:", int(df["customer_id"].duplicated().sum()),
      "| exact dup rows:", int(df.drop(columns=["is_duplicate_email"]).duplicated().sum()))
print("  FR postal 5 digits ok:", int(df[df["country"] == "FR"]["postal_code"].str.match(r"^\d{5}$").sum()))
print("  phones like +33.../+3.../+4...:", int(df["phone"].fillna("").str.match(r"^\+\d{9,13}$").sum()))
