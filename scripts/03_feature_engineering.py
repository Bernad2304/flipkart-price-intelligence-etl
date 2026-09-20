"""
Feature engineering on cleaned Flipkart data:
- Phone type classification
- Discount metrics
- Brand tiering
- Value score
- Price efficiency metrics
- Deal flags, rating tiers, market segments
"""

import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEANED_DIR = os.path.join(BASE_DIR, "data_cleaned")
PROCESSED_DIR = os.path.join(BASE_DIR, "data_processed")


def run_feature_engineering():
    df = pd.read_csv(os.path.join(CLEANED_DIR, "cleaned_products.csv"))

    df["phone_type"] = df["ram_gb"].apply(lambda x: "Smartphone" if pd.notna(x) else "Feature Phone")

    df["discount_amount"] = df["mrp"] - df["price"]
    df["discount_percent"] = ((df["discount_amount"] / df["mrp"]) * 100).round(1)
    df["discount_percent"] = df["discount_percent"].clip(lower=0)

    premium_brands = ["Samsung", "Apple", "OnePlus", "Google"]
    df["brand_tier"] = df["brand"].apply(lambda b: "Premium" if b in premium_brands else "Budget/Mid")

    df["value_score"] = (df["rating"] / (df["price"] / 1000)).round(2)

    df["price_per_gb_storage"] = (df["price"] / df["storage_gb"]).round(0)

    df["is_hot_deal"] = df["discount_percent"] >= 20

    def rating_tier(r):
        if pd.isna(r):
            return "Unrated"
        elif r >= 4.3:
            return "Excellent"
        elif r >= 4.0:
            return "Good"
        elif r >= 3.5:
            return "Average"
        else:
            return "Below Average"

    df["rating_tier"] = df["rating"].apply(rating_tier)

    def market_segment(row):
        if row["phone_type"] == "Feature Phone":
            return "Feature Phone"
        elif row["price"] < 12000:
            return "Entry-level Smartphone"
        elif row["price"] < 25000:
            return "Mid-range Smartphone"
        elif row["price"] < 50000:
            return "Premium Smartphone"
        else:
            return "Flagship"

    df["market_segment"] = df.apply(market_segment, axis=1)

    df["price_rank_in_brand"] = df.groupby("brand")["price"].rank(method="dense")

    preview_cols = ["title", "price", "mrp", "discount_percent", "phone_type",
                     "brand_tier", "value_score", "market_segment", "is_hot_deal", "rating_tier"]
    print(df[preview_cols].head(10))

    os.makedirs(PROCESSED_DIR, exist_ok=True)
    output_path = os.path.join(PROCESSED_DIR, "final_products.csv")
    df.to_csv(output_path, index=False)
    print(f"\nSaved {len(df)} rows to {output_path}")


if __name__ == "__main__":
    run_feature_engineering()