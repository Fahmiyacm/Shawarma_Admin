# Shawarma DKENZ Admin Dashboard Detailed Documentation

## Project Overview

The Shawarma DKENZ Admin Dashboard (admin_app.py) is a Streamlit-based web application designed 
for restaurant administrators to manage menu items, analyze sales data, and forecast future sales for 
the Shawarma DKENZ business. It integrates with a Neon PostgreSQL database for data storage, 
uses Prophet for time-series sales forecasting, and employs Plotly for interactive visualizations. 

### Scope of Documentation

This document covers the admin dashboard in the ShawarmaAdminApp folder, which contains admin_app.py, admin_neondb_helper.py, requirements.txt, screenshots/, .env, and a Dockerfile.
It details functionality, structure, dependencies, database schema, deployment, usage, and troubleshooting.

### Folder Structure

The admin dashboard resides in the ShawarmaAdminApp folder:

ShawarmaAdminApp/

├── app.py                # Main Streamlit admin dashboard

├── admin_neondb_helper.py      # Database helper module for Neon PostgreSQL

├── requirements.txt            # Python dependencies

├── screenshots/                # Screenshots for documentation

├── .env                        # Environment variables (DATABASE_URL)

├── Dockerfile                  # Docker configuration for deployment

├── .gitignore                  # Git ignore file

└── .dockerignore               # Docker ignore file
          


**admin_app.py:** Main Streamlit application for menu management, sales dashboard, and forecasting.

**admin_neondb_helper.py:** Helper module for Neon PostgreSQL database operations.

**requirements.txt:** Lists Python dependencies.

**screenshots/:** Contains screenshots of the dashboard UI.

**.env:** Stores DATABASE_URL for Neon PostgreSQL.

**Dockerfile:** Configures the Docker image for Render deployment.

Architecture

#### **Frontend:**

Streamlit interface with three pages: Menu Management, Dashboard, and Sales Forecasting.

#### **Backend:** 

**admin_neondb_helper.py:** Handles database operations (menu retrieval, updates, order data).

**Database:** Neon PostgreSQL with menu and orders tables.

**Environment:** .env file for DATABASE_URL.

### Key Features

##### Menu Management:

View all menu items (ID, name, category, price).

Add new items with name, category, and price.

Edit or delete existing items by ID.

##### Dashboard:

Displays key metrics: total sales, average order value, order count, items sold.

Category-wise analysis: sales, quantity, and average price with bar, pie, line, and stacked bar charts.

Item-wise analysis: sales, quantity, and top 10 items with a donut chart.


##### Sales Forecasting:

Forecasts sales for 7 or 30 days per category using Prophet.

Visualizes actual and forecasted sales with confidence intervals.

### Screenshots

##### **The screenshots/ folder should include:**

**Menu Management:** Screenshots of “View & Edit Items” and “Add New Item” tabs.

**Dashboard:** Screenshots of metrics, category-wise charts (bar, pie, line, stacked bar), and item-wise donut chart.

**Sales Forecasting:** Screenshots of forecast plots with confidence intervals.

#### Database Schema

The admin dashboard interacts with a Neon PostgreSQL database containing two key tables:

**menu Table**

**CREATE TABLE menu** (
    id SERIAL PRIMARY KEY,
    item_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    item_price NUMERIC(10, 2) NOT NULL
);

id: Unique identifier for menu items.

item_name: Name of the item (e.g., “Shawarma Chicken Medium”).

category: Category (e.g., “Shawarma”, “Burgers”, “Sauces”).

item_price: Price in AED (e.g., 15.00).

**orders Table**

**CREATE TABLE orders** (
    order_id VARCHAR(50),
    item_id INTEGER REFERENCES menu(id),
    item_name VARCHAR(255),
    item_price NUMERIC(10, 2),
    quantity INTEGER,
    total_price NUMERIC(10, 2),
    time_at TIMESTAMP,
    phone_number VARCHAR(20),
    type VARCHAR(50)
);


order_id: Unique order identifier.

item_id: Foreign key to menu.id.

item_name: Name of the ordered item.

item_price: Price per unit at order time.

quantity: Number of items ordered (1–20).

total_price: item_price × quantity.

time_at: Order timestamp.

phone_number: UAE phone number (e.g., “+971559745005”).

type: Order type (e.g., “Normal”, “Spicy”).

### Dependencies

See requirements.txt in ShawarmaAdminApp:

streamlit: Web framework for the dashboard UI.

psycopg2-binary: Connects to Neon PostgreSQL.

sqlalchemy: Supports database queries.

pandas: Data manipulation for analysis and forecasting.

python-dotenv: Loads DATABASE_URL from .env.

plotly: Interactive charts (bar, pie, line, donut).

prophet: Time-series sales forecasting.

#### System Dependencies

libpq-dev: Required for psycopg2.

#### admin_app.py Details

#### Overview

admin_app.py is the main Streamlit application for the admin dashboard, providing a web interface with three pages accessible via a sidebar radio button: Manage Menu, Dashboard, and Sales Forecasting.

#### Structure

###### **1. Imports**

Standard Libraries: logging for diagnostics, datetime for timestamps.

Streamlit: streamlit for UI.

Data Handling: pandas for DataFrames.

Database: psycopg2 for direct SQL queries.

Visualization: plotly.express for quick charts, plotly.graph_objects for custom plots.

Forecasting: prophet for time-series predictions.

Custom Module: admin_neondb_helper for database operations (fetch_menu, add_menu_item, etc.).

###### **2. Configuration**

Streamlit: Sets page_title="Admin Dashboard", layout="wide" for a spacious UI.

Logging: Configures logging with timestamps (%(asctime)s - %(levelname)s - %(message)s).

Database: Defines DB_CONFIG for local testing (overridden by DATABASE_URL in deployment).

###### **3. Functions**

fetch_data(query: str) -> pd.DataFrame:

Executes SQL queries against the Neon database.

Returns results as a pandas DataFrame.

Handles errors with user-friendly messages and logging.

###### **4. Navigation**

Sidebar radio button (st.sidebar.radio) for selecting “Manage Menu”, “Dashboard”, or “Sales Forecasting”.

###### **5. Manage Menu Page**

**Tabs:** Two tabs via st.tabs: “View & Edit Items” and “Add New Item”.

**View/Edit Tab:**

Displays menu items in a table (id, item_name, category, item_price).
Allows deletion by ID using delete_menu_item.
Form for updating item name, category, and price using update_menu_item.

**Add Tab:**

Form for adding new items with name, category (from fetch_categories), and price.
Validates inputs and uses add_menu_item.


###### 6. Dashboard Page

**Filters:**

Date range (from_date, to_date) via st.date_input.
Category and item multiselect filters via st.multiselect.
Search term input for item names via st.text_input.


**Dynamic SQL Query:**

Builds a query for the orders table based on filters.
Joins with menu table to include category information.
Applies filters for items, categories, and search terms.


**Key Metrics:**

Displays total sales, average order value, order count, and items sold using st.metric.


**Category Analysis:**

Table: Summarizes sales, quantity, and average price by category.

Charts: Bar (sales by category), pie (category distribution), line (daily sales), stacked bar (monthly sales).


**Item Analysis:**

Table: Summarizes sales, quantity, and average price by item.

Donut Chart: Shows top 10 items by sales.



###### 7. Sales Forecasting Page

**Forecast Period:** Radio button for 7 or 30 days.

**Data Preparation:**

Fetches order data with fetch_order_data.

**Cleans data:** 

removes duplicates, outliers (1st/99th percentiles), future dates, and invalid entries.
Ensures category column exists and is cleaned.


**Prophet Forecasting:**

Groups data by date and category, sums total_price.
Uses Prophet to forecast sales with confidence intervals.


**Visualization:**

Plots actual sales, forecasted sales, and confidence intervals using Plotly go.Scatter.

### admin_neondb_helper.py Details

#### Overview

admin_neondb_helper.py is a helper module for database operations, connecting to a Neon PostgreSQL database using psycopg2 and environment variables.

#### Structure

###### 1. Imports

os, logging: Environment variables and diagnostics.

psycopg2: Database connectivity.

dotenv: Loads DATABASE_URL.

pandas: Returns order data as DataFrames.

###### 2. Configuration

Logging: Configures logging with timestamps.

Environment: Loads DATABASE_URL from .env.

###### 3. Functions

**get_connection()** -> psycopg2.extensions.connection:

Connects to Neon using DATABASE_URL.

Raises errors for missing variables or connection failures.


**get_all_menu_items()**

Fetches all menu items (id, item_name, category, item_price).


**fetch_menu()** 

Alias for get_all_menu_items.


**add_menu_item(**item_name: str, category: str, price: float) -> None:

Adds a new menu item with validation (non-empty name/category, non-negative price).


update_menu_item(item_id: int, item_name: str, category: str, price: float) -> None:

Updates a menu item by ID.


delete_menu_item(item_id: int) -> None:

Deletes a menu item by ID.


fetch_categories() 

Fetches unique categories from the menu table.


**fetch_order_data()** 

Joins orders and menu tables to fetch order details with categories.



#### Setup Instructions

**Clone Repository:**

git clone <admin_repository_url>

cd ShawarmaAdminApp


**Install Dependencies:**

pip install -r requirements.txt


**Configure Environment:**

Create .env in ShawarmaAdminApp:DATABASE_URL=<your_neon_database_url>


**Database Setup:**

Ensure menu and orders tables exist (see schema above).

Test connection:SELECT * FROM menu LIMIT 5;


**Run App Locally:**

streamlit run admin_app.py

### Usage

**Access Dashboard:**

Use the sidebar to select “Manage Menu”, “Dashboard”, or “Sales Forecasting”.


**Manage Menu:**

View/Edit Tab: Browse items, edit/delete by ID (e.g., update “Shawarma Chicken Medium” price to AED 16).

Add Tab: Add new items (e.g., “Beef Shawarma”, “Main Dish”, AED 20).


**Dashboard:**

Apply filters (e.g., date range: 2025-01-01 to 2025-12-31, category: “Shawarma”).

View metrics (e.g., total sales: AED 10,000) and charts (e.g., top item: “Shawarma Chicken Large”).


**Sales Forecasting:**

Select 7 or 30-day forecast.

View predictions (e.g., “Burgers” sales forecast for next 30 days).



### Troubleshooting

**Database Errors:**

Verify DATABASE_URL and Neon firewall settings.

Test: SELECT * FROM menu LIMIT 5;.


**Prophet Errors:**

Ensure at least 2 days of order data.

Check for valid category column in orders.


**Logs:**

Check Render logs or local logs (logging.INFO, logging.ERROR).


### Conclusion

The Shawarma DKENZ Admin Dashboard (admin_app.py) and its helper module (admin_neondb_helper.py) provide a robust interface for menu management, sales analysis, and forecasting, integrated with Neon PostgreSQL. Deployed on Render’s free tier, it supports efficient restaurant operations. For further assistance, contact support or refer to Render and Neon documentation.