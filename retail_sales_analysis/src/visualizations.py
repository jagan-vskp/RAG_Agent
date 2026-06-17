"""
visualizations.py
-----------------
Reusable chart functions for the Retail Sales Analysis project.
Import these in any notebook:
    from src.visualizations import (
        plot_sales_by_category,
        plot_monthly_trend,
        plot_profit_by_region,
        plot_discount_vs_profit,
        plot_top_n,
        plot_heatmap,
    )
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

# ── Global style ──────────────────────────────────────────────────────────────
sns.set_theme(style="whitegrid", palette="muted")
PALETTE = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3",
           "#937860", "#DA8BC3", "#8C8C8C"]


def _save_or_show(fig, filepath: str = None):
    if filepath:
        fig.savefig(filepath, bbox_inches="tight", dpi=150)
        print(f"Saved → {filepath}")
    plt.tight_layout()
    plt.show()


# ── 1. Sales & Profit by Category / Sub-Category ─────────────────────────────

def plot_sales_by_category(
    df: pd.DataFrame,
    group_col: str = "Category",
    value_col: str = "Sales",
    title: str = None,
    filepath: str = None,
) -> None:
    """
    Horizontal bar chart of total Sales (or Profit) by a categorical column.

    Parameters
    ----------
    df : pd.DataFrame
    group_col : str   Column to group by (default 'Category')
    value_col : str   Metric to aggregate (default 'Sales')
    title : str       Chart title (auto-generated if None)
    filepath : str    Optional path to save the figure (e.g. 'output/fig1.png')
    """
    summary = (
        df.groupby(group_col)[value_col]
        .sum()
        .sort_values(ascending=True)
    )
    fig, ax = plt.subplots(figsize=(9, max(4, len(summary) * 0.55)))
    bars = ax.barh(summary.index, summary.values, color=PALETTE[:len(summary)])
    ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.set_xlabel(f"Total {value_col}")
    ax.set_title(title or f"Total {value_col} by {group_col}")
    for bar in bars:
        width = bar.get_width()
        ax.text(width * 1.01, bar.get_y() + bar.get_height() / 2,
                f"${width:,.0f}", va="center", fontsize=9)
    _save_or_show(fig, filepath)


# ── 2. Monthly Sales / Profit Trend ──────────────────────────────────────────

def plot_monthly_trend(
    df: pd.DataFrame,
    date_col: str = "Order YearMonth",
    value_col: str = "Sales",
    title: str = None,
    filepath: str = None,
) -> None:
    """
    Line chart of monthly aggregated metric over time.

    Parameters
    ----------
    df : pd.DataFrame   Must contain 'Order YearMonth' (from feature_engineer)
    date_col : str      Column with period string (YYYY-MM)
    value_col : str     Metric to sum per month
    """
    if date_col not in df.columns:
        raise ValueError(f"Column '{date_col}' not found. Run feature_engineer() first.")
    monthly = df.groupby(date_col)[value_col].sum().reset_index()
    monthly = monthly.sort_values(date_col)

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(monthly[date_col], monthly[value_col], marker="o", linewidth=2,
            color=PALETTE[0], markersize=4)
    ax.fill_between(range(len(monthly)), monthly[value_col], alpha=0.1, color=PALETTE[0])
    ax.set_xticks(range(len(monthly)))
    ax.set_xticklabels(monthly[date_col], rotation=45, ha="right", fontsize=8)
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.set_xlabel("Month")
    ax.set_ylabel(f"Total {value_col}")
    ax.set_title(title or f"Monthly {value_col} Trend")
    _save_or_show(fig, filepath)


# ── 3. Profit by Region ───────────────────────────────────────────────────────

def plot_profit_by_region(
    df: pd.DataFrame,
    region_col: str = "Region",
    title: str = None,
    filepath: str = None,
) -> None:
    """
    Side-by-side bar chart showing Sales and Profit by region.
    """
    summary = df.groupby(region_col)[["Sales", "Profit"]].sum().reset_index()
    summary = summary.sort_values("Sales", ascending=False)
    x = range(len(summary))
    width = 0.35

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar([i - width / 2 for i in x], summary["Sales"], width, label="Sales",
           color=PALETTE[0])
    ax.bar([i + width / 2 for i in x], summary["Profit"], width, label="Profit",
           color=PALETTE[2])
    ax.set_xticks(x)
    ax.set_xticklabels(summary[region_col])
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda v, _: f"${v:,.0f}"))
    ax.set_title(title or "Sales & Profit by Region")
    ax.legend()
    _save_or_show(fig, filepath)


# ── 4. Discount vs. Profit Scatter ───────────────────────────────────────────

def plot_discount_vs_profit(
    df: pd.DataFrame,
    hue_col: str = "Category",
    title: str = None,
    filepath: str = None,
) -> None:
    """
    Scatter plot of Discount vs. Profit, coloured by category.
    Reveals how heavy discounting erodes margin.
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    categories = df[hue_col].unique()
    for i, cat in enumerate(categories):
        subset = df[df[hue_col] == cat]
        ax.scatter(subset["Discount"], subset["Profit"],
                   alpha=0.3, s=15, label=cat, color=PALETTE[i % len(PALETTE)])
    ax.axhline(0, color="red", linewidth=1, linestyle="--", label="Break-even")
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(xmax=1))
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda v, _: f"${v:,.0f}"))
    ax.set_xlabel("Discount")
    ax.set_ylabel("Profit")
    ax.set_title(title or "Discount vs. Profit by Category")
    ax.legend(title=hue_col)
    _save_or_show(fig, filepath)


# ── 5. Top-N bar chart ────────────────────────────────────────────────────────

def plot_top_n(
    df: pd.DataFrame,
    group_col: str,
    value_col: str = "Sales",
    n: int = 10,
    ascending: bool = False,
    title: str = None,
    filepath: str = None,
) -> None:
    """
    Horizontal bar chart for the top (or bottom) N items in group_col.

    Parameters
    ----------
    ascending : bool   True = bottom N, False = top N
    """
    summary = (
        df.groupby(group_col)[value_col]
        .sum()
        .sort_values(ascending=ascending)
        .head(n)
    )
    fig, ax = plt.subplots(figsize=(9, max(4, n * 0.5)))
    colors = PALETTE[:n] if not ascending else ["#C44E52"] * n
    ax.barh(summary.index, summary.values, color=colors)
    ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    label = "Top" if not ascending else "Bottom"
    ax.set_title(title or f"{label} {n} {group_col} by {value_col}")
    ax.set_xlabel(f"Total {value_col}")
    _save_or_show(fig, filepath)


# ── 6. Pivot Heatmap ─────────────────────────────────────────────────────────

def plot_heatmap(
    df: pd.DataFrame,
    index_col: str = "Category",
    col_col: str = "Region",
    value_col: str = "Profit",
    aggfunc: str = "sum",
    title: str = None,
    filepath: str = None,
) -> None:
    """
    Seaborn heatmap of a pivot table (e.g. Profit by Category × Region).

    Parameters
    ----------
    aggfunc : str  'sum', 'mean', or 'count'
    """
    pivot = df.pivot_table(
        index=index_col,
        columns=col_col,
        values=value_col,
        aggfunc=aggfunc,
        fill_value=0
    )
    fig, ax = plt.subplots(figsize=(max(8, len(pivot.columns) * 1.5), max(5, len(pivot) * 0.8)))
    sns.heatmap(pivot, annot=True, fmt=",.0f", cmap="RdYlGn", linewidths=0.5,
                ax=ax, cbar_kws={"label": value_col})
    ax.set_title(title or f"{aggfunc.capitalize()} {value_col} by {index_col} × {col_col}")
    _save_or_show(fig, filepath)


# ── 7. Interactive Plotly Monthly Trend ──────────────────────────────────────

def plotly_monthly_trend(
    df: pd.DataFrame,
    date_col: str = "Order YearMonth",
    value_cols: list = None,
    title: str = "Monthly Trend",
) -> go.Figure:
    """
    Interactive Plotly line chart. Returns the figure so you can call .show()
    or embed it in a dashboard.

    Parameters
    ----------
    value_cols : list   Columns to plot (default: ['Sales', 'Profit'])
    """
    if value_cols is None:
        value_cols = ["Sales", "Profit"]
    monthly = df.groupby(date_col)[value_cols].sum().reset_index()
    monthly = monthly.sort_values(date_col)

    fig = px.line(
        monthly,
        x=date_col,
        y=value_cols,
        markers=True,
        title=title,
        labels={date_col: "Month"},
        template="plotly_white",
    )
    fig.update_layout(legend_title_text="Metric", hovermode="x unified")
    return fig


# ── 8. Interactive Treemap ────────────────────────────────────────────────────

def plotly_treemap(
    df: pd.DataFrame,
    path: list = None,
    value_col: str = "Sales",
    color_col: str = "Profit",
    title: str = "Sales Treemap",
) -> go.Figure:
    """
    Interactive Plotly treemap. Great for Category → Sub-Category drilldown.

    Parameters
    ----------
    path : list   Hierarchy columns (default: ['Category', 'Sub-Category'])
    """
    if path is None:
        path = ["Category", "Sub-Category"]
    agg = df.groupby(path)[[value_col, color_col]].sum().reset_index()
    fig = px.treemap(
        agg,
        path=path,
        values=value_col,
        color=color_col,
        color_continuous_scale="RdYlGn",
        color_continuous_midpoint=0,
        title=title,
        template="plotly_white",
    )
    return fig
