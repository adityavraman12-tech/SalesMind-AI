"""SalesMind AI: deterministic business metrics with optional NVIDIA Nemotron explanations.

All numeric results are computed locally from the uploaded dataframe. The model is used
for explanations and strategy suggestions, not as the source of calculated totals.
"""
from __future__ import annotations

import os
import re
from typing import Any

import pandas as pd
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# Support either NVIDIA NIM directly or Nebius Token Factory.
# If both keys are present, NVIDIA_API_KEY takes precedence.
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
NEBIUS_API_KEY = os.getenv("NEBIUS_API_KEY")

if NVIDIA_API_KEY and OpenAI:
    client = OpenAI(
        base_url=os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1"),
        api_key=NVIDIA_API_KEY,
    )
    MODEL = os.getenv("NVIDIA_MODEL", "nvidia/nemotron-3-nano-30b-a3b")
elif NEBIUS_API_KEY and OpenAI:
    client = OpenAI(
        base_url=os.getenv("NEBIUS_BASE_URL", "https://api.tokenfactory.nebius.com/v1/"),
        api_key=NEBIUS_API_KEY,
    )
    MODEL = os.getenv("NEBIUS_MODEL", os.getenv("NVIDIA_MODEL", "nvidia/nemotron-3-nano-30b-a3b"))
else:
    client = None
    MODEL = os.getenv("NEBIUS_MODEL", os.getenv("NVIDIA_MODEL", "nvidia/nemotron-3-nano-30b-a3b"))


def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    frame = df.copy()
    frame.columns = [str(c).strip().replace(" ", "_") for c in frame.columns]
    for col in ("Sales", "Profit", "Cost"):
        if col in frame.columns:
            frame[col] = pd.to_numeric(frame[col], errors="coerce")
    if "Order_Date" in frame.columns:
        frame["Order_Date"] = pd.to_datetime(frame["Order_Date"], errors="coerce")
    return frame


def money(value: float) -> str:
    return f"{value:,.2f}"


def _summary(df: pd.DataFrame) -> dict[str, Any]:
    frame = normalize_dataframe(df)
    summary: dict[str, Any] = {
        "rows": int(len(frame)),
        "columns": [str(c) for c in frame.columns],
        "missing_cells": int(frame.isna().sum().sum()),
        "duplicate_rows": int(frame.duplicated().sum()),
        "numeric_summary": {},
        "categorical_summary": {},
    }
    for col in frame.select_dtypes(include="number").columns[:12]:
        series = frame[col].dropna()
        if len(series):
            summary["numeric_summary"][col] = {
                "sum": round(float(series.sum()), 2),
                "mean": round(float(series.mean()), 2),
                "min": round(float(series.min()), 2),
                "max": round(float(series.max()), 2),
            }
    for col in frame.select_dtypes(exclude="number").columns[:10]:
        counts = frame[col].fillna("Unknown").astype(str).value_counts().head(5)
        if len(counts):
            summary["categorical_summary"][col] = {str(k): int(v) for k, v in counts.items()}
    if "Sales" in frame.columns:
        summary["total_revenue"] = round(float(frame["Sales"].fillna(0).sum()), 2)
    if "Profit" in frame.columns and frame["Profit"].notna().any():
        profit = frame["Profit"].fillna(0)
        summary["total_profit"] = round(float(profit.sum()), 2)
        revenue = float(frame["Sales"].fillna(0).sum()) if "Sales" in frame.columns else 0.0
        summary["profit_margin_percent"] = round(float(profit.sum()) / revenue * 100, 2) if revenue else None
        summary["loss_rows"] = int((profit < 0).sum())
    if "Cost" in frame.columns:
        summary["total_cost"] = round(float(frame["Cost"].fillna(0).sum()), 2)
    if "Order_Date" in frame.columns and frame["Order_Date"].notna().any():
        summary["date_range"] = [str(frame["Order_Date"].min().date()), str(frame["Order_Date"].max().date())]
    return summary


def _result(answer: str, evidence: list[str] | None = None, metric=None, chart_type=None, chart_data=None, title="Business insight"):
    return {"answer": answer, "evidence": evidence or [], "metric": metric, "chart_type": chart_type, "chart_data": chart_data, "title": title}


def _deterministic_analysis(df: pd.DataFrame, question: str) -> dict[str, Any]:
    frame = normalize_dataframe(df)
    q = question.lower().strip()
    sales_exists = "Sales" in frame.columns
    profit_exists = "Profit" in frame.columns and frame["Profit"].notna().any()

    if not q:
        return _result("Ask a question about your uploaded business data.")
    if any(k in q for k in ("data quality", "missing values", "duplicates", "data issues")):
        return _result(
            f"The dataset contains {len(frame):,} rows and {frame.shape[1]:,} columns, with {int(frame.isna().sum().sum()):,} missing cells and {int(frame.duplicated().sum()):,} duplicate rows.",
            [f"Rows: {len(frame):,}", f"Columns: {frame.shape[1]:,}", f"Missing cells: {int(frame.isna().sum().sum()):,}", f"Duplicate rows: {int(frame.duplicated().sum()):,}"], title="Data quality"
        )
    if any(k in q for k in ("total sales", "total revenue", "revenue", "sales total", "how much sales")) and sales_exists:
        total = float(frame["Sales"].fillna(0).sum())
        return _result(f"Total mapped revenue is {money(total)}.", [f"Rows analysed: {len(frame):,}", f"Revenue column total: {money(total)}"], total, title="Total revenue")
    if any(k in q for k in ("total profit", "profit total", "how much profit", "profitability")) and profit_exists:
        total = float(frame["Profit"].fillna(0).sum())
        return _result(f"Total mapped profit is {money(total)}.", [f"Rows analysed: {len(frame):,}", f"Profit total: {money(total)}"], total, title="Total profit")
    if "margin" in q and profit_exists and sales_exists:
        sales = float(frame["Sales"].fillna(0).sum())
        profit = float(frame["Profit"].fillna(0).sum())
        margin = profit / sales * 100 if sales else 0.0
        return _result(f"The overall profit margin is {margin:.2f}%.", [f"Revenue: {money(sales)}", f"Profit: {money(profit)}", "Profit margin = profit ÷ revenue × 100"], margin, title="Profit margin")
    if any(k in q for k in ("loss", "unprofitable", "losing money", "negative profit")) and profit_exists:
        losses = frame[frame["Profit"] < 0]
        loss_total = float(losses["Profit"].sum())
        return _result(f"{len(losses):,} rows have negative profit, with combined losses of {money(abs(loss_total))}.", [f"Rows with negative profit: {len(losses):,}", f"Combined loss: {money(abs(loss_total))}"], len(losses), title="Loss analysis")

    if any(k in q for k in ("monthly sales", "sales trend", "sales over time", "revenue trend")) and sales_exists and "Order_Date" in frame.columns:
        dated = frame.dropna(subset=["Order_Date"]).copy()
        if not dated.empty:
            monthly = dated.groupby(dated["Order_Date"].dt.to_period("M"))["Sales"].sum().reset_index()
            monthly["Order_Date"] = monthly["Order_Date"].astype(str)
            if len(monthly) >= 2:
                first, last = float(monthly["Sales"].iloc[0]), float(monthly["Sales"].iloc[-1])
                change = ((last - first) / abs(first) * 100) if first else None
                sentence = f"Revenue changed by {change:.2f}% from the first to the latest available month." if change is not None else "The first month has zero revenue, so percentage change cannot be calculated reliably."
            else:
                sentence = "Only one month of usable date data is available, so a trend cannot yet be established."
            return _result(sentence, [f"Months analysed: {len(monthly)}"], None, "line", monthly, "Monthly revenue trend")

    group_column = None
    for col in frame.columns:
        if col in {"Sales", "Profit", "Cost", "Order_Date"}:
            continue
        clean = str(col).replace("_", " ").lower()
        if clean in q or clean.rstrip("s") in q:
            group_column = col
            break
    wants_profit = "profit" in q or "margin" in q
    metric_column = "Profit" if wants_profit and profit_exists else "Sales" if sales_exists else None
    if group_column and metric_column and any(k in q for k in ("highest", "top", "best", "most", "lowest", "bottom", "worst", "least")):
        grouped = frame.groupby(group_column, dropna=False)[metric_column].sum(min_count=1).dropna()
        if len(grouped):
            ascending = any(k in q for k in ("lowest", "bottom", "worst", "least"))
            grouped = grouped.sort_values(ascending=ascending)
            count_match = re.search(r"top\s+(\d+)", q)
            count = min(int(count_match.group(1)), 10) if count_match else 5 if "top" in q or "bottom" in q else 1
            selected = grouped.head(count)
            first_name, first_value = selected.index[0], float(selected.iloc[0])
            direction = "lowest" if ascending else "highest"
            chart = selected.rename(metric_column).reset_index()
            return _result(f"{first_name} has the {direction} total {metric_column.lower()} at {money(first_value)}.", [f"Compared {len(grouped):,} groups", f"Metric: {metric_column}", f"Top result: {first_name} ({money(first_value)})"], first_value, "bar", chart, f"{metric_column} by {group_column}")

    if any(k in q for k in ("business insight", "insights", "recommend", "improve", "strategy", "what should", "how can", "why", "what is happening", "analyse", "analyze", "business health", "executive summary")):
        summary = _summary(frame)
        evidence = [f"Rows: {len(frame):,}", f"Columns: {', '.join(map(str, frame.columns[:10]))}"]
        if "total_revenue" in summary:
            evidence.append(f"Revenue: {money(summary['total_revenue'])}")
        if "total_profit" in summary:
            evidence.append(f"Profit: {money(summary['total_profit'])}; margin: {summary.get('profit_margin_percent')}%")
        return _result("I can review this dataset for trends, risks, opportunities, and next steps. The AI advisor can provide a richer business interpretation when NVIDIA Nemotron is configured.", evidence, title="Business advisor")

    return _result(
        "I can analyse the mapped revenue, profit, costs, dates, and groupings in this dataset. Try asking for total revenue, total profit, profit margin, losses, data quality, or the best/worst group by one of the column names.",
        [f"Rows: {len(frame):,}", f"Available columns: {', '.join(map(str, frame.columns[:16]))}"], title="Available analysis"
    )


def enhance_with_nemotron(question: str, result: dict[str, Any], df: pd.DataFrame) -> dict[str, Any]:
    if client is None:
        return result
    summary = _summary(df)
    prompt = f"""You are SalesMind AI, a careful business intelligence and strategy advisor.
Use the dataset profile and calculated evidence below. Never invent numbers or claim the dataset proves causation. If a metric is unavailable, say so. Distinguish observed facts from hypotheses and recommendations. Give practical, prioritized actions and note what additional data would validate them. Use relevant public business frameworks when useful (for example, competitive positioning, customer value, unit economics, working capital, or continuous improvement), but do not claim private knowledge or impersonate any business leader. Do not state that you were trained on every business leader. Keep the answer concise and specific to this business.

USER QUESTION:
{question}

DETERMINISTIC RESULT:
{result.get('answer')}

CALCULATED EVIDENCE:
{result.get('evidence')}

DATASET PROFILE (computed locally):
{summary}

Answer the user's question directly. If they ask for business strategy, give up to 3 prioritized recommendations with reasoning and a measurable next step. Never alter the calculated totals above."""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": "You are SalesMind AI's evidence-grounded business advisor."}, {"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=650,
        )
        answer = (response.choices[0].message.content or "").strip()
        if answer:
            result["answer"] = answer
    except Exception as exc:
        # Preserve the deterministic result; never let AI failure break the dashboard.
        result["ai_error"] = str(exc)[:240]
    return result


def analyze_question(df: pd.DataFrame, question: str) -> dict[str, Any]:
    result = _deterministic_analysis(df, question)
    return enhance_with_nemotron(question, result, df)
