# ------------------------------
# Shawarma Admin Dashboard Imports
# ------------------------------
# This section loads all necessary modules for:
# - Logging and debugging
# - Data manipulation
# - Database interaction
# - Time series forecasting
# - Interactive plotting

# --- Logging for diagnostics ---
import logging
from datetime import datetime  # To timestamp logs, track time-based events

# --- Streamlit for UI ---
import streamlit as st  # Interactive web interface

# --- Data handling ---
import pandas as pd  # Used for manipulating tabular data

# --- PostgreSQL connection ---
import psycopg2  # Enables connection to PostgreSQL database

# --- Data visualization ---
import plotly.express as px  # For quick, interactive charts
import plotly.graph_objects as go  # For detailed, customizable plots

# --- Forecasting model ---
from prophet import Prophet  # Facebook Prophet for sales forecasting

# Custom modules
from admin_neondb_helper import (
    fetch_menu,
    add_menu_item,
    update_menu_item,
    delete_menu_item,
    fetch_categories,
    fetch_order_data,
)

# Streamlit page configuration (must be first Streamlit command)
st.set_page_config(page_title="Admin Dashboard", layout="wide")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    "dbname": "dbshawarmabot",
    "user": "postgres",
    "password": "12345",
    "host": "localhost",
    "port": "5432",
}

def fetch_data(query: str) -> pd.DataFrame:
    """Fetch data from the database using the provided SQL query.

    Args:
        query (str): SQL query to execute.

    Returns:
        pd.DataFrame: DataFrame containing query results, or empty DataFrame on error.
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        df = pd.read_sql_query(query, conn)
        conn.close()
        logger.info("Successfully fetched data from database")
        return df
    except Exception as e:
        st.error(f"Database Error: {e}")
        logger.error(f"Database error: {e}")
        return pd.DataFrame()

# Navigation bar
st.sidebar.title("🔧 Admin Panel")
menu_option = st.sidebar.radio(
    "Navigation",
    ["Manage Menu", "Dashboard", "Sales Forecasting"],
)

# Dashboard Page
if menu_option == "Dashboard":
    st.title("📊 Shawarma DKENZ Sales Dashboard")

    # Filters
    with st.sidebar:
        st.header("📅 Filters")
        from_date = st.date_input("Start Date", datetime(2025, 1, 1))
        to_date = st.date_input("End Date", datetime(2025, 12, 31))

    # Fetch menu data
    menu_df = fetch_data("SELECT item_name, category FROM menu")
    item_options = list(menu_df["item_name"].unique()) if not menu_df.empty else []
    category_options = list(menu_df["category"].unique()) if not menu_df.empty else []

    with st.sidebar:
        with st.expander("🎯 Advanced Filters"):
            category_filter = st.multiselect(
                "Category",
                options=category_options,
                default=category_options,
            )
            item_filter = st.multiselect(
                "Item",
                options=item_options,
                default=item_options,
            )
        search_term = st.text_input("🔍 Search by Item Name")

    # Build dynamic SQL query
    query = f"""
    SELECT order_id, item_name, item_price, quantity, total_price, time_at
    FROM orders
    WHERE time_at::date BETWEEN '{from_date}' AND '{to_date}'
    """
    if item_filter and len(item_filter) < len(item_options):
        items_str = ",".join([f"'{item}'" for item in item_filter])
        query += f" AND item_name IN ({items_str})"

    df = fetch_data(query)
    if df.empty:
        st.warning("No orders found for selected filters.")
        logger.warning("No orders found for selected filters")
        st.stop()

    df = df.merge(menu_df, on="item_name", how="left")
    if category_filter and len(category_filter) < len(category_options):
        df = df[df["category"].isin(category_filter)]
    if search_term:
        df = df[df["item_name"].str.contains(search_term, case=False, na=False)]
    if df.empty:
        st.warning("No data after applying all filters.")
        logger.warning("No data after applying all filters")
        st.stop()

    # Key Metrics
    st.subheader("📈 Key Metrics")
    total_sales = df["total_price"].sum()
    total_orders = df["order_id"].nunique()
    avg_order_value = df["total_price"].mean()
    total_items = df["quantity"].sum()

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    metric_col1.metric("💰 Total Sales", f"AED {total_sales:,.2f}")
    metric_col2.metric("📈 Avg Order", f"AED {avg_order_value:.2f}")
    metric_col3.metric("📦 Orders", total_orders)
    metric_col4.metric("🍟 Items Sold", total_items)

    # Category-wise Analysis
    st.header("📦 Category-wise Analysis")
    try:
        category_summary = df.groupby("category").agg(
            total_sales=("total_price", "sum"),
            total_quantity=("quantity", "sum"),
            avg_price=("item_price", "mean"),
        ).reset_index().sort_values(by="total_sales", ascending=False)

        st.dataframe(
            category_summary.style.format({
                "total_sales": "AED {:.2f}",
                "avg_price": "AED {:.2f}",
            })
        )

        fig_bar = px.bar(
            category_summary,
            x="category",
            y="total_sales",
            color="total_sales",
            title="Sales by Category",
            color_continuous_scale="viridis",
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        fig_pie = px.pie(
            category_summary,
            values="total_sales",
            names="category",
            title="Category Distribution",
        )
        st.plotly_chart(fig_pie, use_container_width=True)

        df["time_at"] = pd.to_datetime(df["time_at"])
        daily_sales = df.groupby([df["time_at"].dt.date, "category"])["total_price"].sum().reset_index()
        fig_line = px.line(
            daily_sales,
            x="time_at",
            y="total_price",
            color="category",
            markers=True,
            title="Daily Sales by Category",
        )
        st.plotly_chart(fig_line, use_container_width=True)

        df["month"] = df["time_at"].dt.to_period("M").astype(str)
        monthly_sales = df.groupby(["month", "category"])["total_price"].sum().reset_index()
        fig_stack = px.bar(
            monthly_sales,
            x="month",
            y="total_price",
            color="category",
            barmode="stack",
            title="Monthly Category-wise Sales",
        )
        st.plotly_chart(fig_stack, use_container_width=True)
    except Exception as e:
        st.error("Failed to generate category-wise analysis.")
        logger.error(f"Error in category-wise analysis: {e}")

    # Item-wise Analysis
    st.header("🧾 Item-wise Analysis")
    try:
        item_summary = df.groupby(["item_name", "category"]).agg(
            total_sales=("total_price", "sum"),
            total_quantity=("quantity", "sum"),
            avg_price=("item_price", "mean"),
        ).reset_index().sort_values(by="total_sales", ascending=False)

        st.dataframe(
            item_summary.style.format({
                "total_sales": "AED {:.2f}",
                "avg_price": "AED {:.2f}",
            })
        )

        top_items = item_summary.head(10)
        fig_donut = go.Figure(
            data=[
                go.Pie(
                    labels=top_items["item_name"],
                    values=top_items["total_sales"],
                    hole=0.4,
                )
            ]
        )
        fig_donut.update_layout(title="Top 10 Items by Sales")
        st.plotly_chart(fig_donut, use_container_width=True)
    except Exception as e:
        st.error("Failed to generate item-wise analysis.")
        logger.error(f"Error in item-wise analysis: {e}")

# Manage Menu Page
elif menu_option == "Manage Menu":
    st.title("🧾 Menu Management")
    tab_view_edit, tab_add = st.tabs(["🔄 View & Edit Items", "➕ Add New Item"])

    # Tab 1: View and Edit/Delete Items
    with tab_view_edit:
        try:
            menu_data = fetch_menu()
            df = pd.DataFrame(
                menu_data,
                columns=["ID", "Item Name", "Category", "Price"],
            )
            st.dataframe(df, use_container_width=True)

            st.subheader("✏️ Edit/Delete Item")
            selected_id = st.number_input(
                "Enter ID to Edit/Delete",
                min_value=1,
                step=1,
            )

            if st.button("Delete Item"):
                try:
                    delete_menu_item(selected_id)
                    st.success("Item deleted successfully.")
                    logger.info(f"Deleted menu item with ID: {selected_id}")
                except Exception as e:
                    st.error("Failed to delete item.")
                    logger.error(f"Error deleting item ID {selected_id}: {e}")

            with st.form("edit_form"):
                new_name = st.text_input("New Item Name")
                new_category = st.text_input("New Category")
                new_price = st.number_input("New Price", min_value=0.0, format="%.2f")
                submitted = st.form_submit_button("Update Item")
                if submitted:
                    try:
                        update_menu_item(selected_id, new_name, new_category, new_price)
                        st.success("Item updated successfully.")
                        logger.info(f"Updated menu item ID: {selected_id}")
                    except Exception as e:
                        st.error("Failed to update item.")
                        logger.error(f"Error updating item ID {selected_id}: {e}")
        except Exception as e:
            st.error("Failed to load menu data.")
            logger.error(f"Error loading menu data: {e}")

    # Tab 2: Add New Item
    with tab_add:
        st.subheader("Add New Menu Item")
        with st.form("add_form"):
            item_name = st.text_input("Item Name")
            categories = fetch_categories()
            category = st.selectbox("Select Category", categories)
            price = st.number_input("Price", min_value=0.0, format="%.2f")
            submitted = st.form_submit_button("Add Item")

            if submitted:
                if not item_name.strip():
                    st.error("Item name is required.")
                elif price <= 0:
                    st.error("Price must be greater than 0.")
                else:
                    try:
                        add_menu_item(item_name, category, price)
                        st.success("New item added successfully.")
                        logger.info(f"Added new menu item: {item_name}")
                    except Exception as e:
                        st.error("Failed to add new item.")
                        logger.error(f"Error adding new item {item_name}: {e}")

# Sales Forecasting Page
elif menu_option == "Sales Forecasting":
    st.subheader("📈 Sales Forecasting")
    forecast_days = st.radio("Select Forecast Period", [7, 30], index=0)

    df_orders = fetch_order_data()
    if df_orders.empty:
        st.warning("No order data found.")
        logger.warning("No order data available for forecasting")
    else:
        try:
            # Data cleaning
            df_orders = df_orders.dropna(subset=["time_at", "total_price"])
            df_orders["time_at"] = pd.to_datetime(df_orders["time_at"])
            df_orders["total_price"] = pd.to_numeric(df_orders["total_price"], errors="coerce")
            df_orders["item_price"] = pd.to_numeric(df_orders["item_price"], errors="coerce")
            df_orders["quantity"] = pd.to_numeric(df_orders["quantity"], errors="coerce")
            df_orders = df_orders.dropna(subset=["total_price", "item_price", "quantity"])
            df_orders = df_orders.drop_duplicates()

            # Remove outliers
            q_low = df_orders["total_price"].quantile(0.01)
            q_high = df_orders["total_price"].quantile(0.99)
            df_orders = df_orders[
                (df_orders["total_price"] >= q_low) & (df_orders["total_price"] <= q_high)
            ]

            # Remove future dates
            today = pd.to_datetime("today")
            df_orders = df_orders[df_orders["time_at"] <= today]

            # Clean category column
            if "category" not in df_orders.columns:
                st.error(
                    "❌ Category column not found in data. Please ensure category info is included from item table."
                )
                logger.error("Category column missing in order data")
                st.stop()

            df_orders["category"] = df_orders["category"].str.strip().str.title()
            categories = df_orders["category"].unique()

            for category in categories:
                st.markdown(f"### 🔹 Category: {category}")
                df_category = df_orders[df_orders["category"] == category]

                # Group by date and sum total_price
                df_grouped = (
                    df_category.groupby(df_category["time_at"].dt.date)["total_price"]
                    .sum()
                    .reset_index()
                )
                df_grouped.columns = ["ds", "y"]  # Prophet expects 'ds' and 'y'

                if len(df_grouped) < 2:
                    st.info(f"Not enough data to forecast for category: {category}")
                    logger.info(f"Insufficient data for category: {category}")
                    continue

                # Prophet Forecast
                model = Prophet()
                model.fit(df_grouped)
                future = model.make_future_dataframe(periods=forecast_days)
                forecast = model.predict(future)

                # Create custom plot
                actual_dates = df_grouped["ds"]
                actual_sales = df_grouped["y"]
                forecast_dates = forecast["ds"]
                forecast_sales = forecast["yhat"]
                forecast_lower = forecast["yhat_lower"]
                forecast_upper = forecast["yhat_upper"]

                fig = go.Figure()
                fig.add_trace(
                    go.Scatter(
                        x=actual_dates,
                        y=actual_sales,
                        mode="lines+markers",
                        name="Actual Sales",
                        line=dict(color="blue"),
                    )
                )
                fig.add_trace(
                    go.Scatter(
                        x=forecast_dates,
                        y=forecast_sales,
                        mode="lines",
                        name="Forecasted Sales",
                        line=dict(color="orange", dash="dash"),
                    )
                )
                fig.add_trace(
                    go.Scatter(
                        x=list(forecast_dates) + list(forecast_dates[::-1]),
                        y=list(forecast_upper) + list(forecast_lower[::-1]),
                        fill="toself",
                        fillcolor="rgba(255,165,0,0.2)",
                        line=dict(color="rgba(255,255,255,0)"),
                        hoverinfo="skip",
                        showlegend=True,
                        name="Confidence Interval",
                    )
                )
                fig.update_layout(
                    title=f"Sales Forecast with Confidence Interval - {category}",
                    xaxis_title="Date",
                    yaxis_title="Sales (AED)",
                    hovermode="x unified",
                )
                st.plotly_chart(fig, use_container_width=True)
                logger.info(f"Generated sales forecast for category: {category}")
        except Exception as e:
            st.error("Failed to generate sales forecast.")
            logger.error(f"Error in sales forecasting: {e}")