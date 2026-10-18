"""Data cleaning and summary statistics."""
import pandas as pd


def summarize(df: pd.DataFrame) -> dict:
    df = df.copy()
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df.dropna(subset=["amount"])
    df["category"] = df["category"].fillna("uncategorized").astype(str)

    by_category = (
        df.groupby("category")["amount"]
        .agg(count="count", total="sum", average="mean")
        .sort_values("total", ascending=False)
        .reset_index()
    )
    return {
        "records": int(len(df)),
        "total": float(df["amount"].sum()),
        "average": float(df["amount"].mean()) if len(df) else 0.0,
        "top_category": by_category.iloc[0]["category"] if len(by_category) else "-",
        "by_category": by_category,
    }
