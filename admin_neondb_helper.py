import os
import logging
from typing import List, Tuple, Any
import psycopg2
from psycopg2 import Error as PsycopgError
from dotenv import load_dotenv
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

"""Database helper module for Shawarma DKENZ admin operations."""

# Load environment variables
load_dotenv()

def get_connection() -> psycopg2.extensions.connection:
    """Establish a connection to the Neon PostgreSQL database using DATABASE_URL.

    Returns:
        psycopg2.extensions.connection: Database connection object.

    Raises:
        PsycopgError: If connection to the database fails.
    """
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL not found in environment variables")
        connection = psycopg2.connect(database_url)
        logger.info("Successfully connected to the Neon database")
        return connection
    except (PsycopgError, ValueError) as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

def get_all_menu_items() -> List[Tuple[Any, ...]]:
    """Fetch all menu items from the database.

    Returns:
        List[Tuple[Any, ...]]: List of tuples containing menu item details (id, item_name, category, item_price).

    Raises:
        PsycopgError: If the query execution fails.
    """
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, item_name, category, item_price FROM menu ORDER BY id;")
                rows = cursor.fetchall()
                logger.info("Successfully fetched all menu items")
                return rows
    except PsycopgError as e:
        logger.error(f"Error fetching menu items: {e}")
        raise

def fetch_menu() -> List[Tuple[Any, ...]]:
    """Fetch menu data from the database.

    Returns:
        List[Tuple[Any, ...]]: List of tuples containing menu item details (id, item_name, category, item_price).

    Raises:
        PsycopgError: If the query execution fails.
    """
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, item_name, category, item_price FROM menu ORDER BY id")
                data = cursor.fetchall()
                logger.info("Successfully fetched menu data")
                return data
    except PsycopgError as e:
        logger.error(f"Error fetching menu data: {e}")
        raise


def add_menu_item(item_name: str, category: str, price: float) -> None:
    """Add a new menu item to the database.

    Args:
        item_name (str): Name of the menu item.
        category (str): Category of the menu item.
        price (float): Price of the menu item.

    Raises:
        ValueError: If input validation fails.
        PsycopgError: If the insert operation fails.
    """
    # Input validation
    if not item_name or not item_name.strip():
        raise ValueError("Item name cannot be empty")
    if not category or not category.strip():
        raise ValueError("Category cannot be empty")
    if price < 0:
        raise ValueError("Price cannot be negative")

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                logger.debug(f"Inserting item: name={item_name}, category={category}, price={price}")
                cursor.execute(
                    "INSERT INTO menu (item_name, category, item_price) VALUES (%s, %s, %s) RETURNING id",
                    (item_name.strip(), category.strip(), price)
                )
                item_id = cursor.fetchone()[0]
                connection.commit()
                logger.info(f"Successfully added menu item: {item_name} (ID: {item_id})")
    except PsycopgError as e:
        logger.error(f"Error adding menu item {item_name}: {e}")
        raise

def update_menu_item(item_id: int, item_name: str, category: str, price: float) -> None:
    """Update an existing menu item in the database.

    Args:
        item_id (int): ID of the menu item to update.
        item_name (str): New name for the menu item.
        category (str): New category for the menu item.
        price (float): New price for the menu item.

    Raises:
        PsycopgError: If the update operation fails.
    """
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE menu SET item_name = %s, category = %s, item_price = %s WHERE id = %s",
                    (item_name, category, price, item_id)
                )
                connection.commit()
                logger.info(f"Successfully updated menu item ID: {item_id}")
    except PsycopgError as e:
        logger.error(f"Error updating menu item ID {item_id}: {e}")
        raise

def delete_menu_item(item_id: int) -> None:
    """Delete a menu item from the database.

    Args:
        item_id (int): ID of the menu item to delete.

    Raises:
        PsycopgError: If the delete operation fails.
    """
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM menu WHERE id = %s", (item_id,))
                connection.commit()
                logger.info(f"Successfully deleted menu item ID: {item_id}")
    except PsycopgError as e:
        logger.error(f"Error deleting menu item ID {item_id}: {e}")
        raise

def fetch_categories() -> List[str]:
    """Fetch distinct categories from the menu table.

    Returns:
        List[str]: List of unique category names.

    Raises:
        PsycopgError: If the query execution fails.
    """
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT DISTINCT category FROM menu ORDER BY category;")
                categories = [row[0] for row in cursor.fetchall()]
                logger.info("Successfully fetched categories")
                return categories
    except PsycopgError as e:
        logger.error(f"Error fetching categories: {e}")
        raise

def fetch_order_data() -> pd.DataFrame:
    """Fetch order data with menu category information from the database.

    Returns:
        pd.DataFrame: DataFrame containing order details with menu categories.

    Raises:
        PsycopgError: If the query execution fails.
    """
    try:
        with get_connection() as connection:
            query = """
                SELECT o.order_id, o.item_id, o.item_name, o.item_price, o.quantity,
                       o.total_price, o.time_at, o.phone_number, o.type,
                       m.category, m.id
                FROM orders o
                JOIN menu m ON o.item_id = m.id
            """
            df = pd.read_sql_query(query, connection)
            logger.info("Successfully fetched order data")
            return df
    except PsycopgError as e:
        logger.error(f"Error fetching order data: {e}")
        raise