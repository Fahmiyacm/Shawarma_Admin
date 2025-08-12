sdk: docker
app_port: 8501
# Shawarma DKENZ Admin Dashboard – Summary Documentation

## Overview

The Shawarma DKENZ Admin Dashboard is a Streamlit web app used by restaurant admins to manage menu items, view sales analytics, and forecast future sales. It connects to a Neon PostgreSQL database, uses Prophet for forecasting, and Plotly for visualizations.

## Folder Structure

app.py: Main dashboard UI (menu management, dashboard, forecasting).

admin_neondb_helper.py: Handles database operations.

requirements.txt: Lists Python dependencies.

.env: Stores DATABASE_URL.

Dockerfile: Deployment config for Render.

screenshots/: UI snapshots for documentation.

## Key Features

**1. Menu Management**
View, add, update, or delete menu items (ID, name, category, price).

**2. Dashboard**
Filters: date range, category, item name.

Metrics: total sales, order count, avg order value.

Visuals: category/item-wise charts (bar, pie, donut, line, stacked).

**3. Sales Forecasting**
Forecast 7 or 30 days of category-wise sales using Prophet.

Shows forecast plots with confidence intervals.

## ️ Database Schema

**Tables:**

menu: Stores menu item info (id, item_name, category, item_price).

orders: Stores order data (order_id, item_id, quantity, time_at, etc.).

## Dependencies

streamlit, psycopg2-binary, sqlalchemy, pandas, plotly, prophet, dotenv

## Setup Instructions
**Clone repo:**

git clone <repo_url> && cd ShawarmaAdminApp
**Install dependencies:**

pip install -r requirements.txt
**Configure .env:**

DATABASE_URL=<your_neon_db_url>
**Run app locally:**

streamlit run admin_app.py

## Usage

Use sidebar to switch between Menu, Dashboard, and Forecasting.

**Manage menu:** Add/edit/delete items.

**Analyze sales:** Filter by date/category, view charts.

**Forecast sales:** Select forecast window, view predicted trends.

##  Troubleshooting

DB Errors: Check .env and Neon firewall rules.

Prophet Issues: Ensure enough valid order data.

Logging: Logs output to console or Streamlit logs for debugging.

## Hugging Face Deployment Notes
This app is configured for Hugging Face Spaces with a Docker runtime.  
- Ensure you set `DATABASE_URL` in Space **Settings → Secrets**.  
- The Space will auto-build using the `Dockerfile` in this repo.  
- Streamlit runs on port 8501.
## Conclusion

The Shawarma DKENZ Admin Dashboard offers a simple, powerful interface for managing restaurant data and sales trends. It’s fully integrated with Neon and ready for deployment on platforms like Render.

