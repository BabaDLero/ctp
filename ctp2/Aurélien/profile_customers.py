"""CTP 2 - Exercise 1: profile customers.csv with pandas (completed starter).
Run from the 02_CTP2 folder:  python profile_customers.py
Goal: measure at least 8 rules (2 per dimension) and copy the numbers into quality_scorecard.csv
"""
import os
import pandas as pd

def find_kit():
    for cand in ("../shopfast-kit/data/", "../install/shopfast-kit/data/",
                 "../../install/shopfast-kit/data/", "install/shopfast-kit/data/"):
        if os.path.exists(cand + "customers.csv"):
            return cand
    raise FileNotFoundError("customers.csv not found - adjust KIT")

KIT = find_kit()
df = pd.read_csv(KIT + "customers.csv", dtype=str)   # dtype=str: keep the raw text (e.g. 01300)
n = len(df)
print("Rows:", n)
print(df.head())

score = lambda failing: round(100 * (1 - failing / n), 1)   # score of a rule = 100 * (1 - failing rows / total rows)

# --- Completeness: how many empty values per column? ---
print("\nEmpty values per column:\n", df.isna().sum())

# --- Uniqueness: is customer_id unique? ---
dup_id_rows = df["customer_id"].duplicated(keep=False).sum()
dup_id_extra = df["customer_id"].duplicated().sum()
print("\nDuplicated customer_id rows:", dup_id_rows, "| extra rows to remove:", dup_id_extra)

# TODO 1 (Uniqueness): normalise email (strip + lower case) and count people registered twice
em = df["email"].str.strip().str.lower()
dup_email_rows = em.duplicated(keep=False).sum()
dup_email_extra = em.duplicated().sum()
print(f"\nR1 emails duplicated: {dup_email_rows} rows in dup groups, {dup_email_extra} extra rows -> score {score(dup_email_extra)}%")

# TODO 2 (Validity): count emails that do not match the regex  ^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$
bad_email = (~em.fillna("").str.match(r"^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$")).sum()
print(f"R2 emails not matching regex: {bad_email} -> score {score(bad_email)}%")

# TODO 3 (Consistency): list the distinct values of country with value_counts() - how many spellings for 4 countries?
print("\nCountry spellings:\n", df["country"].value_counts())
spellings = df["country"].fillna("").str.strip().str.lower().nunique()
print(f"R3 {spellings} different spellings for only 4 countries")
bad_country = (~df["country"].fillna("").str.strip().str.upper().isin(["FR", "DE", "ES", "BE"])).sum()
print(f"R3 country not ISO-2 {['FR','DE','ES','BE']}: {bad_country} -> score {score(bad_country)}%")

# TODO 4 (Consistency): count signup_date values that are NOT in the format YYYY-MM-DD
bad_signup = (~df["signup_date"].fillna("").str.match(r"^\d{4}-\d{2}-\d{2}$")).sum()
print(f"R4 signup_date not YYYY-MM-DD: {bad_signup} -> score {score(bad_signup)}%")

# TODO 5 (Validity): loyalty_tier values outside bronze / silver / gold / platinum
bad_tier = (~df["loyalty_tier"].fillna("").str.strip().str.lower().isin(["bronze", "silver", "gold", "platinum"])).sum()
print(f"R5 loyalty_tier outside bronze/silver/gold/platinum: {bad_tier} -> score {score(bad_tier)}%")

# TODO 6 (Accuracy): birth dates in the future or before 1906 (convert the ISO ones with pd.to_datetime)
bd = pd.to_datetime(df["birth_date"], format="mixed", errors="coerce")
today = pd.Timestamp.today()
bad_birth = ((bd > today) | (bd < pd.Timestamp("1906-01-01"))).sum()
print(f"R6 birth_date in the future or before 1906: {bad_birth} -> score {score(bad_birth)}%")
print("   future:", (bd > today).sum(), "| before 1906:", (bd < pd.Timestamp('1906-01-01')).sum(), "| minors (<18y):", (bd > today - pd.DateOffset(years=18)).sum())

# TODO 7 (Validity): French postal codes that do not have 5 digits
fr = df[df["country"].fillna("").str.strip().str.upper().isin(["FR", "FRANCE", "FRA"])]
bad_postal = (~fr["postal_code"].fillna("").str.match(r"^\d{5}$")).sum()
print(f"R7 French postal_code not 5 digits: {bad_postal} (of {len(fr)} FR rows) -> score {score(bad_postal)}% (on FR rows)")

# Bonus: completeness / timeliness-style rules for the scorecard
bad_phone = df["phone"].isna().sum()
print(f"R8 phone empty: {bad_phone} -> score {score(bad_phone)}%")
print(f"R9 email empty: {df['email'].isna().sum()} -> score {score(df['email'].isna().sum())}%")
print(f"R10 exact duplicate rows: {df.duplicated().sum()} -> score {score(df.duplicated().sum())}%")
