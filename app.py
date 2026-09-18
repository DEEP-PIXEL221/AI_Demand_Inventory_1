# ============================================================
# PROJECT FORESIGHT
# AI-POWERED DEMAND & INVENTORY INTELLIGENCE PLATFORM
# PURE STREAMLIT DASHBOARD
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import requests

# ============================================================
# FLASK API CONNECTION
# ============================================================

FLASK_API_URL = "http://127.0.0.1:5000/predict"


def predict_stockout_risk(stock_on_hand, reorder_point, safety_stock):

    payload = {
        "stock_on_hand": stock_on_hand,
        "reorder_point": reorder_point,
        "safety_stock": safety_stock
    }

    try:

        response = requests.post(
            FLASK_API_URL,
            json=payload,
            timeout=10
        )

        if response.status_code == 200:

            return response.json()

        else:

            return {
                "error": f"API returned status code {response.status_code}"
            }

    except requests.exceptions.RequestException as e:

        return {
            "error": f"Could not connect to Flask API: {str(e)}"
        }


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Project FORESIGHT",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# LOAD SALES DATA
# ============================================================

@st.cache_data
def load_sales():

    df = pd.read_csv(
        "data/sales_10k_clean.csv"
    )

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    return df


# ============================================================
# LOAD RISK DATA
# ============================================================

@st.cache_data
def load_risk():

    df = pd.read_csv(
        "data/final_risk_scoring.csv"
    )

    return df


# ============================================================
# LOAD DATA
# ============================================================

try:

    sales = load_sales()
    risk = load_risk()

except Exception as e:

    st.error("Data files could not be loaded.")

    st.write(
        "Please make sure these files exist:"
    )

    st.code(
        """
data/sales_10k_clean.csv
data/final_risk_scoring.csv
        """
    )

    st.error(str(e))

    st.stop()


# ============================================================
# BASIC DATA PREPARATION
# ============================================================

sales["date"] = pd.to_datetime(
    sales["date"],
    errors="coerce"
)


# ============================================================
# RECOMMENDATION FUNCTION
# ============================================================

def generate_recommendation(row):

    stockout = row.get(
        "stockout_risk",
        False
    )

    reorder = row.get(
        "reorder_risk",
        False
    )

    below_safety = row.get(
        "below_safety_risk",
        False
    )

    overstock = row.get(
        "overstock_risk",
        False
    )

    if stockout is True:

        return "Immediate Reorder"

    elif reorder is True and below_safety is True:

        return "Expedite Replenishment"

    elif reorder is True:

        return "Plan Reorder"

    elif overstock is True:

        return "Review Excess Inventory"

    else:

        return "No Immediate Action"


# ============================================================
# CREATE RECOMMENDATION COLUMN
# ============================================================

risk["recommended_action"] = risk.apply(
    generate_recommendation,
    axis=1
)


# Select the risk-category column before any page uses it.
if "final_risk_category" in risk.columns:

    category_column = "final_risk_category"

else:

    category_column = "risk_category"


# ============================================================
# WEEKLY FORECAST
# ============================================================

@st.cache_data
def prepare_weekly_forecast(data):

    weekly = (
        data
        .groupby("sku_id")
        .resample("W", on="date")
        .agg(
            units_sold=("quantity", "sum"),
            revenue=("total_value", "sum"),
            transactions=("receipt_id", "nunique")
        )
        .reset_index()
    )

    weekly["seasonal_naive_forecast"] = (
        weekly
        .groupby("sku_id")["units_sold"]
        .shift(52)
    )

    return weekly


weekly_forecast = prepare_weekly_forecast(
    sales
)


# ============================================================
# COMMON METRICS
# ============================================================

total_records = len(sales)

total_units = sales["quantity"].sum()

total_revenue = sales["total_value"].sum()

unique_skus = sales["sku_id"].nunique()

risk_records = len(risk)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("📦 Project FORESIGHT")

st.sidebar.write(
    "AI-Powered Demand & Inventory Intelligence"
)

st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Home",
        "📊 Sales Analytics",
        "📈 Forecasting",
        "📦 Inventory Dashboard",
        "🚨 Risk Dashboard",
        "🔎 Product Details",
        "📋 Executive Summary"
    ]
)

st.sidebar.divider()

st.sidebar.info(
    "Data Scope\n\n"
    "10,000 cleaned sales transactions"
)


# ============================================================
# HOME PAGE
# ============================================================

if page == "🏠 Home":

    st.title("📦 Project FORESIGHT")

    st.subheader(
        "AI-Powered Demand & Inventory Intelligence Platform"
    )

    st.write(
        "A data-driven platform for sales analysis, "
        "demand forecasting, inventory monitoring, "
        "and inventory risk identification."
    )

    st.divider()

    st.header("📊 Project Snapshot")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Sales Records",
            f"{total_records:,}"
        )

    with col2:
        st.metric(
            "Units Sold",
            f"{total_units:,.0f}"
        )

    with col3:
        st.metric(
            "Revenue",
            f"₹{total_revenue:,.0f}"
        )

    with col4:
        st.metric(
            "Unique SKUs",
            f"{unique_skus:,}"
        )

    with col5:
        st.metric(
            "Risk Records",
            f"{risk_records:,}"
        )

    st.divider()

    st.header("🧠 Intelligence Modules")

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("📊 Sales Analytics")

        st.write(
            "Analyze transactions, revenue, units sold, "
            "products, promotions, and sales trends."
        )

    with col2:

        st.subheader("📈 Demand Forecasting")

        st.write(
            "Analyze historical demand and generate "
            "future demand estimates."
        )

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("📦 Inventory Intelligence")

        st.write(
            "Monitor stock levels, reorder points, "
            "safety stock, and inventory coverage."
        )

    with col2:

        st.subheader("🚨 Risk Intelligence")

        st.write(
            "Identify stockout risk, reorder requirements, "
            "and inventory actions."
        )

    st.divider()

    st.header("🎯 Business Objectives")

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("1️⃣ Understand Demand")

        st.write(
            "Analyze historical sales patterns "
            "and demand trends."
        )

        st.subheader("2️⃣ Forecast Future Demand")

        st.write(
            "Generate demand estimates to support "
            "inventory planning."
        )

    with col2:

        st.subheader("3️⃣ Detect Inventory Risk")

        st.write(
            "Identify products that may face "
            "stockouts or replenishment requirements."
        )

        st.subheader("4️⃣ Support Business Decisions")

        st.write(
            "Convert sales, forecast, and inventory "
            "data into actionable insights."
        )

    st.divider()

    st.header("🚨 Quick Risk Insights")

    if "final_risk_category" in risk.columns:

        category_column = "final_risk_category"

    else:

        category_column = "risk_category"

    critical_stockout = (
        risk[category_column]
        .eq("Critical Stockout")
        .sum()
    )

    reorder_required = (
        risk[category_column]
        .eq("Reorder Required")
        .sum()
    )

    high_risk = (
        risk[category_column]
        .eq("High Risk")
        .sum()
    )

    healthy = (
        risk[category_column]
        .eq("Healthy")
        .sum()
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Critical Stockout",
            f"{critical_stockout:,}"
        )

    with col2:
        st.metric(
            "Reorder Required",
            f"{reorder_required:,}"
        )

    with col3:
        st.metric(
            "High Risk",
            f"{high_risk:,}"
        )

    with col4:
        st.metric(
            "Healthy",
            f"{healthy:,}"
        )

    st.divider()

    st.header("📈 Sales Trend")

    daily_sales = (
        sales
        .groupby("date")["quantity"]
        .sum()
        .sort_index()
    )

    st.line_chart(
        daily_sales
    )

    st.divider()

    st.header("📊 Risk Distribution")

    risk_distribution = pd.Series(
        {
            "Critical Stockout": critical_stockout,
            "Reorder Required": reorder_required,
            "High Risk": high_risk,
            "Healthy": healthy
        }
    )

    st.bar_chart(
        risk_distribution
    )

    st.divider()

    st.success(
        "Project FORESIGHT converts sales and inventory "
        "data into demand insights, forecasts, and "
        "inventory risk intelligence."
    )


# ============================================================
# SALES ANALYTICS
# ============================================================

elif page == "📊 Sales Analytics":

    st.title("📊 Sales Analytics")

    st.write(
        "Explore historical sales performance "
        "and identify business trends."
    )

    st.divider()

    st.header("🔎 Filters")

    col1, col2, col3 = st.columns(3)

    # Store filter
    with col1:

        if "store_id" in sales.columns:

            store_values = sorted(
                sales["store_id"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

            selected_store = st.selectbox(
                "Store",
                ["All"] + store_values
            )

        else:

            selected_store = "All"

            st.info(
                "Store information unavailable."
            )

    # Channel filter
    with col2:

        if "channel" in sales.columns:

            channel_values = sorted(
                sales["channel"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

            selected_channel = st.selectbox(
                "Channel",
                ["All"] + channel_values
            )

        else:

            selected_channel = "All"

            st.info(
                "Channel information unavailable."
            )

    # Date filter
    with col3:

        min_date = sales["date"].min().date()

        max_date = sales["date"].max().date()

        selected_dates = st.date_input(
            "Date Range",
            value=(min_date, max_date)
        )

    filtered_sales = sales.copy()

    if selected_store != "All":

        filtered_sales = filtered_sales[
            filtered_sales["store_id"]
            .astype(str)
            == selected_store
        ]

    if selected_channel != "All":

        filtered_sales = filtered_sales[
            filtered_sales["channel"]
            .astype(str)
            == selected_channel
        ]

    if (
        isinstance(selected_dates, tuple)
        and len(selected_dates) == 2
    ):

        filtered_sales = filtered_sales[
            (
                filtered_sales["date"].dt.date
                >= selected_dates[0]
            )
            &
            (
                filtered_sales["date"].dt.date
                <= selected_dates[1]
            )
        ]

    st.divider()

    st.header("📌 Sales KPIs")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Transactions",
            f"{len(filtered_sales):,}"
        )

    with col2:

        st.metric(
            "Units Sold",
            f"{filtered_sales['quantity'].sum():,.0f}"
        )

    with col3:

        st.metric(
            "Revenue",
            f"₹{filtered_sales['total_value'].sum():,.0f}"
        )

    with col4:

        st.metric(
            "Unique SKUs",
            f"{filtered_sales['sku_id'].nunique():,}"
        )

    st.divider()

    st.header("📈 Daily Sales Trend")

    daily = (
        filtered_sales
        .groupby("date")
        .agg(
            Units=("quantity", "sum"),
            Revenue=("total_value", "sum")
        )
        .sort_index()
    )

    st.line_chart(
        daily
    )

    st.divider()

    st.header("🏆 Top 10 Products")

    top_products = (
        filtered_sales
        .groupby("sku_id")
        .agg(
            Units_Sold=("quantity", "sum"),
            Revenue=("total_value", "sum")
        )
        .sort_values(
            "Revenue",
            ascending=False
        )
        .head(10)
    )

    st.dataframe(
        top_products,
        use_container_width=True
    )

    st.bar_chart(
        top_products["Revenue"]
    )

    st.divider()

    st.header("📅 Monthly Performance")

    monthly = (
        filtered_sales
        .set_index("date")
        .resample("ME")
        .agg(
            Units=("quantity", "sum"),
            Revenue=("total_value", "sum")
        )
    )

    st.line_chart(
        monthly
    )

    st.divider()

    if "promo_flag" in filtered_sales.columns:

        st.header("🎯 Promotion Analysis")

        promotion = (
            filtered_sales
            .groupby("promo_flag")
            .agg(
                Transactions=("receipt_id", "count"),
                Units=("quantity", "sum"),
                Revenue=("total_value", "sum")
            )
        )

        st.dataframe(
            promotion,
            use_container_width=True
        )

    st.divider()

    st.header("📋 Sales Data Preview")

    st.dataframe(
        filtered_sales.head(100),
        use_container_width=True
    )


# ============================================================
# FORECASTING PAGE
# ============================================================

elif page == "📈 Forecasting":

    st.title("📈 Demand Forecasting")

    st.write(
        "Analyze weekly demand and Seasonal Naive forecasts."
    )

    st.divider()

    sku_list = sorted(
        weekly_forecast["sku_id"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_sku = st.selectbox(
        "Select SKU",
        sku_list
    )

    sku_data = weekly_forecast[
        weekly_forecast["sku_id"]
        == selected_sku
    ].copy()

    sku_data = sku_data.sort_values(
        "date"
    )

    st.divider()

    latest_row = sku_data.iloc[-1]

    latest_actual = latest_row[
        "units_sold"
    ]

    latest_forecast = latest_row[
        "seasonal_naive_forecast"
    ]

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Latest Actual Demand",
            f"{latest_actual:.2f}"
        )

    with col2:

        if pd.notna(latest_forecast):

            st.metric(
                "Seasonal Naive Forecast",
                f"{latest_forecast:.2f}"
            )

        else:

            st.metric(
                "Seasonal Naive Forecast",
                "N/A"
            )

    with col3:

        st.metric(
            "Forecast Horizon",
            "6 Weeks"
        )

    st.divider()

    st.header("📊 Model Performance")

    model_performance = pd.DataFrame(
        {
            "Model": [
                "Seasonal Naive",
                "Random Forest",
                "Gradient Boosting"
            ],
            "MAE": [
                0.1915,
                0.2027,
                0.2019
            ],
            "MSE": [
                0.5568,
                0.3831,
                0.3839
            ],
            "RMSE": [
                0.7462,
                0.6190,
                0.6196
            ],
            "R²": [
                -0.2891,
                0.1130,
                0.1112
            ],
            "WAPE (%)": [
                125.3690,
                132.7293,
                132.2248
            ]
        }
    )

    st.dataframe(
        model_performance,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.header("📈 Historical Weekly Demand")

    historical = (
        sku_data
        .set_index("date")
        [["units_sold"]]
    )

    st.line_chart(
        historical
    )

    st.divider()

    st.header("🔮 Actual vs Forecast")

    actual_forecast = (
        sku_data
        .set_index("date")
        [
            [
                "units_sold",
                "seasonal_naive_forecast"
            ]
        ]
        .tail(52)
    )

    actual_forecast.columns = [
        "Actual Demand",
        "Forecast"
    ]

    st.line_chart(
        actual_forecast
    )

    st.divider()

    st.header("🔮 Forecast View")

    forecast_view = (
        sku_data[
            sku_data[
                "seasonal_naive_forecast"
            ].notna()
        ]
        .tail(6)
        [
            [
                "date",
                "seasonal_naive_forecast"
            ]
        ]
    )

    forecast_view.columns = [
        "Reference Week",
        "Forecast Demand"
    ]

    st.dataframe(
        forecast_view,
        use_container_width=True,
        hide_index=True
    )

    st.info(
        "Seasonal Naive forecasting uses demand from "
        "the corresponding week in the previous year."
    )


# ============================================================
# INVENTORY DASHBOARD
# ============================================================

elif page == "📦 Inventory Dashboard":

    st.title("📦 Inventory Dashboard")

    st.write(
        "Monitor stock levels, safety stock, reorder points, "
        "and inventory conditions."
    )

    st.divider()

    stockout_count = (
        risk["stockout_risk"]
        .eq(True)
        .sum()
    )

    safety_count = (
        risk["below_safety_risk"]
        .eq(True)
        .sum()
    )

    reorder_count = (
        risk["reorder_risk"]
        .eq(True)
        .sum()
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Inventory Records",
            f"{len(risk):,}"
        )

    with col2:

        st.metric(
            "Stockout Risk",
            f"{stockout_count:,}"
        )

    with col3:

        st.metric(
            "Below Safety Stock",
            f"{safety_count:,}"
        )

    with col4:

        st.metric(
            "Reorder Point Risk",
            f"{reorder_count:,}"
        )

    st.divider()

    st.header("📦 Stock Position")

    stock_columns = [
        "store_id",
        "sku_id",
        "stock_on_hand",
        "reorder_point",
        "safety_stock",
        "avg_weekly_demand"
    ]

    available_columns = [
        col
        for col in stock_columns
        if col in risk.columns
    ]

    st.dataframe(
        risk[available_columns].head(100),
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.header("❤️ Inventory Health")

    health = (
        risk[category_column]
        .value_counts()
    )

    st.bar_chart(
        health
    )

    st.divider()

    st.header("🎯 Inventory Recommendations")

    recommendation_summary = (
        risk["recommended_action"]
        .value_counts()
        .rename_axis("Recommended Action")
        .reset_index(
            name="Records"
        )
    )

    st.dataframe(
        recommendation_summary,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.header("📋 Inventory Planning View")

    planning_columns = [
        "store_id",
        "sku_id",
        "stock_on_hand",
        "reorder_point",
        "safety_stock",
        "avg_weekly_demand",
        "risk_demand_estimate",
        category_column,
        "recommended_action"
    ]

    available_planning = [
        col
        for col in planning_columns
        if col in risk.columns
    ]

    st.dataframe(
        risk[available_planning],
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# RISK DASHBOARD
# ============================================================

elif page == "🚨 Risk Dashboard":

    st.title("🚨 Inventory Risk Dashboard")

    st.write(
        "Identify inventory risks and prioritize "
        "recommended actions."
    )

    st.divider()

    st.header("📊 Risk Category Overview")

    risk_summary = (
        risk[category_column]
        .value_counts()
        .rename_axis("Risk Category")
        .reset_index(
            name="Records"
        )
    )

    st.dataframe(
        risk_summary,
        use_container_width=True,
        hide_index=True
    )

    st.bar_chart(
        risk_summary.set_index(
            "Risk Category"
        )
    )

    st.divider()

    st.header("🎯 Recommended Actions")

    action_summary = (
        risk["recommended_action"]
        .value_counts()
        .rename_axis("Recommended Action")
        .reset_index(
            name="Records"
        )
    )

    st.dataframe(
        action_summary,
        use_container_width=True,
        hide_index=True
    )

    st.bar_chart(
        action_summary.set_index(
            "Recommended Action"
        )
    )

    st.divider()

    st.header("🔎 Filter Risk Category")

    categories = [
        "All"
    ] + sorted(
        risk[category_column]
        .dropna()
        .unique()
        .tolist()
    )

    selected_category = st.selectbox(
        "Risk Category",
        categories
    )

    filtered_risk = risk.copy()

    if selected_category != "All":

        filtered_risk = filtered_risk[
            filtered_risk[category_column]
            == selected_category
        ]

    st.metric(
        "Selected Records",
        f"{len(filtered_risk):,}"
    )

    st.divider()

    st.header("📋 Risk Details")

    risk_columns = [
        "store_id",
        "sku_id",
        "stock_on_hand",
        "reorder_point",
        "safety_stock",
        "avg_weekly_demand",
        "risk_demand_estimate",
        category_column,
        "recommended_action"
    ]

    available_risk_columns = [
        col
        for col in risk_columns
        if col in filtered_risk.columns
    ]

    st.dataframe(
        filtered_risk[
            available_risk_columns
        ],
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.header("🔴 Critical Stockout")

    critical = risk[
        risk[category_column]
        == "Critical Stockout"
    ]

    st.metric(
        "Critical Stockout Records",
        f"{len(critical):,}"
    )

    st.dataframe(
        critical[
            available_risk_columns
        ].head(100),
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# PRODUCT DETAILS
# ============================================================

elif page == "🔎 Product Details":

    st.title("🔎 Product Details")

    st.write(
        "Analyze individual SKU sales, inventory, "
        "forecast, and risk information."
    )

    st.divider()

    sku_list = sorted(
        sales["sku_id"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_sku = st.selectbox(
        "Select Product / SKU",
        sku_list
    )

    product_sales = sales[
        sales["sku_id"]
        == selected_sku
    ].copy()

    product_risk = risk[
        risk["sku_id"]
        == selected_sku
    ].copy()

    st.divider()

    st.header("📊 Product Sales Performance")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Units Sold",
            f"{product_sales['quantity'].sum():,.0f}"
        )

    with col2:

        st.metric(
            "Revenue",
            f"₹{product_sales['total_value'].sum():,.0f}"
        )

    with col3:

        st.metric(
            "Transactions",
            f"{len(product_sales):,}"
        )

    st.divider()

    st.header("📈 Product Demand Trend")

    product_trend = (
        product_sales
        .groupby("date")["quantity"]
        .sum()
        .sort_index()
    )

    st.line_chart(
        product_trend
    )

    st.divider()

    st.header("📦 Inventory Position")

    if len(product_risk) > 0:

        inventory_columns = [
            "store_id",
            "stock_on_hand",
            "reorder_point",
            "safety_stock",
            "avg_weekly_demand",
            "risk_demand_estimate",
            category_column,
            "recommended_action"
        ]

        available_inventory = [
            col
            for col in inventory_columns
            if col in product_risk.columns
        ]

        st.dataframe(
            product_risk[
                available_inventory
            ],
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No inventory risk record found for this SKU."
        )

    st.divider()

    st.header("🔮 Product Forecast")

    product_forecast = weekly_forecast[
        weekly_forecast["sku_id"]
        == selected_sku
    ].copy()

    if len(product_forecast) > 0:

        forecast_chart = (
            product_forecast
            .set_index("date")
            [
                [
                    "units_sold",
                    "seasonal_naive_forecast"
                ]
            ]
            .tail(52)
        )

        forecast_chart.columns = [
            "Actual Demand",
            "Seasonal Naive Forecast"
        ]

        st.line_chart(
            forecast_chart
        )

    else:

        st.info(
            "Forecast information unavailable."
        )

    st.divider()

    st.header("📋 Product Sales Records")

    st.dataframe(
        product_sales,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# EXECUTIVE SUMMARY
# ============================================================

elif page == "📋 Executive Summary":

    st.title("📋 Executive Summary")

    st.write(
        "High-level overview of sales, forecasting, "
        "inventory, and risk intelligence."
    )

    st.divider()

    st.header("💼 Business KPIs")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Sales Transactions",
            f"{total_records:,}"
        )

    with col2:

        st.metric(
            "Units Sold",
            f"{total_units:,.0f}"
        )

    with col3:

        st.metric(
            "Revenue",
            f"₹{total_revenue:,.0f}"
        )

    with col4:

        st.metric(
            "Unique SKUs",
            f"{unique_skus:,}"
        )

    st.divider()

    st.header("📈 Forecast Performance")

    forecast_summary = pd.DataFrame(
        {
            "Model": [
                "Seasonal Naive",
                "Random Forest",
                "Gradient Boosting"
            ],
            "MAE": [
                0.1915,
                0.2027,
                0.2019
            ],
            "MSE": [
                0.5568,
                0.3831,
                0.3839
            ],
            "RMSE": [
                0.7462,
                0.6190,
                0.6196
            ],
            "R²": [
                -0.2891,
                0.1130,
                0.1112
            ],
            "WAPE (%)": [
                125.3690,
                132.7293,
                132.2248
            ]
        }
    )

    st.dataframe(
        forecast_summary,
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "Final test metrics are based on the same 19,073 test records."
    )

    st.divider()

    st.header("🚨 Inventory Risk Summary")

    if "final_risk_category" in risk.columns:
        executive_category_column = "final_risk_category"
    else:
        executive_category_column = "risk_category"

    critical_stockout = risk[executive_category_column].eq(
        "Critical Stockout"
    ).sum()

    reorder_required = risk[executive_category_column].eq(
        "Reorder Required"
    ).sum()

    high_risk = risk[executive_category_column].eq(
        "High Risk"
    ).sum()

    healthy = risk[executive_category_column].eq(
        "Healthy"
    ).sum()

    executive_risk = (
        risk[executive_category_column]
        .value_counts()
        .rename_axis("Risk Category")
        .reset_index(
            name="Records"
        )
    )

    st.dataframe(
        executive_risk,
        use_container_width=True,
        hide_index=True
    )

    st.bar_chart(
        executive_risk.set_index(
            "Risk Category"
        )
    )

    st.divider()

    st.header("🎯 Recommended Actions")

    executive_actions = (
        risk["recommended_action"]
        .value_counts()
        .rename_axis("Recommended Action")
        .reset_index(
            name="Records"
        )
    )

    st.dataframe(
        executive_actions,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.header("💡 Key Project Insights")

    st.info(
        f"""
        • The project analyzes {total_records:,} cleaned sales transactions.

        • The dataset contains {unique_skus:,} unique SKUs.

        • The inventory risk dataset contains {risk_records:,} records.

        • {critical_stockout:,} records are classified as Critical Stockout.

        • {reorder_required:,} records are classified as Reorder Required.

        • {high_risk:,} records are classified as High Risk.

        • {healthy:,} records are classified as Healthy.

        • Demand forecasting was evaluated using Seasonal Naive,
          Random Forest, and Gradient Boosting.
        """
    )

    st.divider()

    st.header("🏁 Project Conclusion")

    st.write(
        "Project FORESIGHT integrates sales analytics, "
        "demand forecasting, inventory monitoring, and "
        "risk scoring into a single decision-support dashboard."
    )

    st.write(
        "The platform helps users understand historical demand, "
        "review forecast information, monitor inventory conditions, "
        "and identify potential replenishment requirements."
    )

    st.success(
        "Project FORESIGHT Dashboard is ready for business analysis."
    )


# ============================================================
# SIDEBAR FOOTER
# ============================================================

st.sidebar.divider()

st.sidebar.caption(
    "Project FORESIGHT"
)

st.sidebar.caption(
    "AI-Powered Demand & Inventory Intelligence"
)

st.sidebar.caption(
    "Data scope: 10,000 cleaned sales transactions"
)