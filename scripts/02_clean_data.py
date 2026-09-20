"""
Cleans raw scraped Flipkart data:
- Removes duplicates and unusable rows
- Extracts brand, RAM, storage (handling both GB and MB units), color
- Fixes data types
- Applies realistic range validation to spec-derived fields
- Creates price bands
"""

import pandas as pd
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data_raw")
CLEANED_DIR = os.path.join(BASE_DIR, "data_cleaned")


def extract_ram_gb(specs):
    """Extracts RAM and normalizes to GB, handling both GB and MB units."""
    gb_match = re.search(r"(\d+)\s*GB RAM", specs)
    if gb_match:
        return float(gb_match.group(1))
    mb_match = re.search(r"(\d+)\s*MB RAM", specs)
    if mb_match:
        return round(int(mb_match.group(1)) / 1024, 4)
    return None


def extract_storage_gb(specs):
    """Extracts storage and normalizes to GB, handling both GB and MB units."""
    gb_match = re.search(r"(\d+)\s*GB ROM", specs)
    if gb_match:
        return float(gb_match.group(1))
    mb_match = re.search(r"(\d+)\s*MB ROM", specs)
    if mb_match:
        return round(int(mb_match.group(1)) / 1024, 4)
    return None


def run_cleaning():
    df = pd.read_csv(os.path.join(RAW_DIR, "price_history.csv"))

    print("BEFORE CLEANING")
    print("Total rows:", len(df))
    print("Missing values:\n", df.isnull().sum())

    df["color"] = df["title"].str.extract(r"\(([\w\s]+),", expand=False)
    df["color"] = df["color"].fillna("Unknown")

    print("\nDIAGNOSTIC")
    print("Total rows:", len(df))
    print("Unique titles:", df["title"].nunique())
    print("Unique (title+price+color+date):", df.drop_duplicates(subset=["title", "price", "color", "scrape_date"]).shape[0])

    df = df.drop_duplicates(subset=["title", "price", "color", "scrape_date"], keep="last")
    df = df.dropna(subset=["price"])

    df["brand"] = df["title"].str.split().str[0]

    df["specs"] = df["specs"].fillna("")

    # Fixed: properly handles both GB and MB units, converting MB to GB
    df["ram_gb"] = df["specs"].apply(extract_ram_gb)
    df["storage_gb"] = df["specs"].apply(extract_storage_gb)

    # Sanity bounds - realistic phone spec ranges (now allows small MB-converted values like 0.046875)
    df.loc[(df["ram_gb"] < 0.01) | (df["ram_gb"] > 24), "ram_gb"] = None
    df.loc[(df["storage_gb"] < 0.01) | (df["storage_gb"] > 1024), "storage_gb"] = None

    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")

    df["mrp"] = pd.to_numeric(df["mrp"], errors="coerce")
    df["mrp"] = df["mrp"].fillna(df["price"])

    def price_band(price):
        if price < 10000:
            return "Budget (<10k)"
        elif price < 25000:
            return "Mid-range (10k-25k)"
        else:
            return "Premium (25k+)"

    df["price_band"] = df["price"].apply(price_band)

    print("\nAFTER CLEANING")
    print("Total rows:", len(df))
    print("Missing values:\n", df.isnull().sum())
    print("Max ram_gb:", df["ram_gb"].max())
    print("Max storage_gb:", df["storage_gb"].max())
    print("Min storage_gb (non-null):", df["storage_gb"].min())

    os.makedirs(CLEANED_DIR, exist_ok=True)
    output_path = os.path.join(CLEANED_DIR, "cleaned_products.csv")
    df.to_csv(output_path, index=False)
    print(f"\nSaved to {output_path}")


if __name__ == "__main__":
    run_cleaning()