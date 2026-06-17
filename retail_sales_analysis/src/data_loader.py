"""
data_loader.py
--------------
Reusable functions for loading and cleaning the Superstore dataset.
Import these in any notebook:
    from src.data_loader import load_superstore, clean_data, feature_engineer
"""

import os
import pandas as pd
import numpy as np


# ── Column name constants ────────────────────────────────────────────────────
NUMERIC_COLS = ["Sales", "Quantity", "Discount", "Profit"]
DATE_COLS = ["Order Date", "Ship Date"]
CAT_COLS = ["Segment", "Region", "Category", "Sub-Category", "Ship Mode", "State", "City"]

DEFAULT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sample_superstore.csv")


# ── Loading ──────────────────────────────────────────────────────────────────

def load_superstore(filepath: str = DEFAULT_PATH, encoding: str = "latin-1") -> pd.DataFrame:
    """
    Load the Superstore CSV into a DataFrame.

    Parameters
    ----------
    filepath : str
        Path to the CSV file. Defaults to data/sample_superstore.csv.
    encoding : str
        File encoding. The Tableau/Kaggle version often uses latin-1.

    Returns
    -------
    pd.DataFrame
        Raw DataFrame.

    Raises
    ------
    FileNotFoundError
        If the CSV is not found at the given path.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"Dataset not found at '{filepath}'.\n"
            "See data/README.md for download instructions."
        )
    df = pd.read_csv(filepath, encoding=encoding)
    print(f"✅ Loaded {len(df):,} rows × {len(df.columns)} columns")
    return df


# ── Cleaning ─────────────────────────────────────────────────────────────────

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply standard cleaning steps to the raw Superstore DataFrame.

    Steps
    -----
    1. Strip whitespace from column names and string columns.
    2. Parse Order Date and Ship Date as datetime.
    3. Cast numeric columns to float/int.
    4. Drop exact duplicate rows.
    5. Report any remaining nulls.

    Parameters
    ----------
    df : pd.DataFrame
        Raw DataFrame from load_superstore().

    Returns
    -------
    pd.DataFrame
        Cleaned DataFrame (copy).
    """
    df = df.copy()

    # 1. Clean column names
    df.columns = df.columns.str.strip()

    # 2. Strip string columns
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()

    # 3. Parse dates
    for col in DATE_COLS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], infer_datetime_format=True, errors="coerce")

    # 4. Numeric coercion
    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 5. Remove duplicates
    before = len(df)
    df = df.drop_duplicates()
    removed = before - len(df)
    if removed:
        print(f"⚠️  Removed {removed} duplicate rows.")

    # 6. Null report
    nulls = df.isnull().sum()
    nulls = nulls[nulls > 0]
    if not nulls.empty:
        print("⚠️  Columns with nulls:\n", nulls.to_string())
    else:
        print("✅ No null values detected.")

    print(f"✅ Clean DataFrame: {len(df):,} rows × {len(df.columns)} columns")
    return df


# ── Feature Engineering ──────────────────────────────────────────────────────

def feature_engineer(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add derived columns useful for analysis.

    New columns
    -----------
    - Profit Margin (%)  : Profit / Sales * 100
    - Order Year         : Year extracted from Order Date
    - Order Month        : Month number (1–12)
    - Order Quarter      : Quarter string (e.g. 'Q1')
    - Order YearMonth    : Period string (e.g. '2017-03')
    - Ship Lag (days)    : Ship Date - Order Date in days

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned DataFrame from clean_data().

    Returns
    -------
    pd.DataFrame
        DataFrame with additional columns (copy).
    """
    df = df.copy()

    if "Sales" in df.columns and "Profit" in df.columns:
        df["Profit Margin (%)"] = np.where(
            df["Sales"] != 0,
            (df["Profit"] / df["Sales"]) * 100,
            0.0
        ).round(2)

    if "Order Date" in df.columns:
        df["Order Year"] = df["Order Date"].dt.year
        df["Order Month"] = df["Order Date"].dt.month
        df["Order Quarter"] = df["Order Date"].dt.to_period("Q").astype(str)
        df["Order YearMonth"] = df["Order Date"].dt.to_period("M").astype(str)

    if "Order Date" in df.columns and "Ship Date" in df.columns:
        df["Ship Lag (days)"] = (df["Ship Date"] - df["Order Date"]).dt.days

    print("✅ Feature engineering complete. New columns:", [
        c for c in ["Profit Margin (%)", "Order Year", "Order Month",
                    "Order Quarter", "Order YearMonth", "Ship Lag (days)"]
        if c in df.columns
    ])
    return df


# ── Quick summary ─────────────────────────────────────────────────────────────

def quick_summary(df: pd.DataFrame) -> None:
    """Print a concise business summary of the cleaned dataset."""
    print("=" * 55)
    print("SUPERSTORE DATASET — QUICK SUMMARY")
    print("=" * 55)
    print(f"  Orders      : {df['Order ID'].nunique():,}")
    print(f"  Customers   : {df['Customer ID'].nunique():,}")
    print(f"  Products    : {df['Product ID'].nunique():,}")
    print(f"  Date range  : {df['Order Date'].min().date()} → {df['Order Date'].max().date()}")
    print(f"  Total Sales : ${df['Sales'].sum():,.2f}")
    print(f"  Total Profit: ${df['Profit'].sum():,.2f}")
    print(f"  Avg Discount: {df['Discount'].mean():.1%}")
    print("=" * 55)
