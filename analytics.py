import pandas as pd


def calculate_kpis(df):
    """Calculate the main sales KPIs."""

    total_sales = df["Sales"].sum()
    total_cost = df["Cost"].sum()
    total_profit = df["Profit"].sum()

    orders = len(df)

    profit_margin = (
        (total_profit / total_sales) * 100
        if total_sales != 0
        else 0
    )

    average_order_value = (
        total_sales / orders
        if orders != 0
        else 0
    )

    return {
        "total_sales": total_sales,
        "total_cost": total_cost,
        "total_profit": total_profit,
        "orders": orders,
        "profit_margin": profit_margin,
        "average_order_value": average_order_value
    }


def sales_by_category(df):
    """Calculate sales and profit by category."""

    return (
        df.groupby("Category")
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum")
        )
        .sort_values("Sales", ascending=False)
        .reset_index()
    )


def sales_by_region(df):
    """Calculate sales and profit by region."""

    return (
        df.groupby("Region")
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum")
        )
        .sort_values("Sales", ascending=False)
        .reset_index()
    )


def monthly_sales(df):
    """Calculate monthly sales and profit."""

    monthly = (
        df.groupby(df["Order Date"].dt.to_period("M"))
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum")
        )
        .reset_index()
    )

    monthly["Order Date"] = monthly["Order Date"].astype(str)

    return monthly