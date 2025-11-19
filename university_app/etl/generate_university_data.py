"""
ETL Script for Generating and Loading Data into a Database.

This script generates data for employees, customers, products, orders, and sales, 
saves the data to CSV files, and loads the CSV data into a database.

Modules:
    - etl.Database.models: Database models for the project.
    - etl.Database.database: Database engine and base class.
    - etl.Database.data_generator: Functions to generate data for various entities.
    - pandas: For data manipulation and storage in CSV.
    - loguru: For logging.
    - random: For random number generation.
    - glob, os: For file path and system operations.
"""

import pandas as pd
from loguru import logger
import random
from Database.models import *
from Database.database import engine, Base
from Database.data_generator import (
    generate_customer,
    generate_product,
    generate_orders,
    generate_employee,
    generate_sales,
)
import glob
from os import path
from sqlalchemy import text

# -----------------------------------------------------
# Constants
# -----------------------------------------------------
NUMBER_OF_TRANSACTIONS = 5000
NUMBER_OF_EMPLOYEES = 100
NUMBER_OF_CUSTOMERS = 2000
NUMBER_OF_ORDERS = 200

# -----------------------------------------------------
# Generate and Save Data to CSV
# -----------------------------------------------------

# Generate Employee Data
employees = pd.DataFrame([generate_employee(employee_id) for employee_id in range(NUMBER_OF_EMPLOYEES)])
logger.info("Employee Data")
logger.info(employees.head(1))
employees.to_csv("data/employees.csv", index=False)
logger.info(f"Employee data saved to CSV: {employees.shape}")

# Generate Customer Data
customers = pd.DataFrame([generate_customer(customer_id) for customer_id in range(NUMBER_OF_CUSTOMERS)])
logger.info("Customer Data")
logger.info(customers.head(1))
customers.to_csv("data/customers.csv", index=False)
logger.info(f"Customer data saved to CSV: {customers.shape}")

# Generate Product Data
products = pd.DataFrame([generate_product(product_id) for product_id in range(1, 101)])
logger.info("Product Data")
logger.info(products.head(1))
products.to_csv("data/products.csv", index=False)
logger.info(f"Product data saved to CSV: {products.shape}")

# Generate Order Data
orders = pd.DataFrame([generate_orders(order_id) for order_id in range(NUMBER_OF_ORDERS)])
logger.info("Order Data")
logger.info(orders.head(1))
orders.to_csv("data/orders.csv", index=False)
logger.info(f"Order data saved to CSV: {orders.shape}")

# Generate Sales Data
sales = []
for transaction_id in range(1, NUMBER_OF_TRANSACTIONS + 1):
    order_id = random.randint(1, len(orders))
    product_id = random.randint(1, len(products))
    customer_id = random.randint(1, len(customers))
    employee_id = random.randint(1, len(employees))
    sale = generate_sales(transaction_id, order_id, product_id, customer_id, employee_id)
    sales.append(sale)

sales = pd.DataFrame(sales)
sales.to_csv("data/sales.csv", index=False)
logger.info(f"Sales data saved to CSV: {sales.shape}")

# -----------------------------------------------------
# Utility Function to Load Data into Database
# -----------------------------------------------------

def load_csv_to_table(table_name: str, csv_path: str) -> None:
    """
    Load data from a CSV file into a database table.

    **Parameters:**
    
    - `table_name (str):` The name of the database table.
    - `csv_path (str):` The path to the CSV file containing data.

    **Returns:**
        - `None`
    """
    df = pd.read_csv(csv_path)
    df.to_sql(table_name, con=engine, if_exists="append", index=False)
    logger.info(f"Loading data into table: {table_name}")

# -----------------------------------------------------
# Load CSV Data into Database Tables
# -----------------------------------------------------

# Get all CSV file paths
folder_path = "data/*.csv"
files = glob.glob(folder_path)
base_names = [path.splitext(path.basename(file))[0] for file in files]

# Load data from CSV files into respective tables
for table in base_names:
    try:
        logger.info(f"Loading data into table: {table}")
        load_csv_to_table(table, path.join("data/", f"{table}.csv"))
    except Exception as e:
        logger.error(f"Failed to ingest table {table}. Error: {e}")
        print(f"Failed to ingest table {table}. Moving to the next!")

print("Tables are populated.")

# Manually reset sequences for auto-increment primary keys
sequence_reset_queries = [
    "SELECT setval('employees_employee_id_seq', (SELECT MAX(employee_id) FROM employees))",
    "SELECT setval('customers_customer_id_seq', (SELECT MAX(customer_id) FROM customers))",
    "SELECT setval('products_product_id_seq', (SELECT MAX(product_id) FROM products))",
    "SELECT setval('orders_order_id_seq', (SELECT MAX(order_id) FROM orders))",
    "SELECT setval('sales_transaction_id_seq', (SELECT MAX(transaction_id) FROM sales))"
]

with engine.connect() as conn:
    for query in sequence_reset_queries:
        try:
            conn.execute(text(query))
            logger.info(f"Sequence reset: {query}")
        except Exception as e:
            logger.warning(f"Failed to reset sequence: {query}, Error: {e}")
