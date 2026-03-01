from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import List

from models import Product, ElectronicsProduct, PerishableProduct

DB_PATH = Path(__file__).with_name("inventory.db")

SCHEMA_PATH = Path(__file__).with_name("schema.sql")

# Create a database connection 
def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# Initialize database 
def init_db() -> None:
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    with get_connection() as conn:
        conn.executescript(schema)

# Insert product into database
def insert_product(product: Product) -> None:
    if isinstance(product, ElectronicsProduct):
        product_type = "electronics"
    elif isinstance(product, PerishableProduct):
        product_type = "perishable"
    else:
        product_type = "base"

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO Products(name, price, stock_quantity, product_type)
            VALUES(?,?,?,?)
            """,
            (product.name, product.price, product.stock_quantity, product_type),
        )

        # Get auto-generated ID from cursor
        new_id = cursor.lastrowid
        product.product_id = new_id

        # Insert subtype data
        if product_type == "electronics":
            conn.execute(
                "INSERT INTO Electronics(product_id, warranty_period) VALUES(?,?)",
                (new_id, int(product.warranty_period)),
            )

        elif product_type == "perishable":
            conn.execute(
                "INSERT INTO Perishables(product_id, expiration_date) VALUES(?,?)",
                (new_id, str(product.expiration_date)),
            )
    
# Remove a product 
def delete_product(product_id: int) -> None:
    with get_connection() as conn:
        cur = conn.execute("DELETE FROM Products WHERE product_id = ?", (int(product_id),))
        if cur.rowcount == 0:
            raise KeyError("product_id not found.")

# Update stock quantity for a product
def update_stock(product_id: int, new_stock_quantity: int) -> None:
    with get_connection() as conn:
        cur = conn.execute(
            "UPDATE Products SET stock_quantity = ? WHERE product_id = ?",
            (int(new_stock_quantity), int(product_id)),
        )
        if cur.rowcount == 0:
            raise KeyError("product_id not found.")

# Update product price
def update_price(product_id: int, new_price: float) -> None:
    with get_connection() as conn:
        cur = conn.execute(
            "UPDATE Products SET price = ? WHERE product_id = ?",
            (float(new_price), int(product_id)),
        )
        if cur.rowcount == 0:
            raise KeyError("product_id not found.")

# Record a completed sale transaction
def insert_sale(product_id: int, quantity: int, total_amount: float) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO Sales(product_id, quantity, total_amount)
            VALUES(?,?,?)
            """,
            (int(product_id), int(quantity), float(total_amount)),
        )

# Load all products and rebuild appropriate product objects
def fetch_all_products() -> List[Product]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT p.product_id, p.name, p.price, p.stock_quantity, p.product_type,
                   e.warranty_period,
                   pe.expiration_date
            FROM Products p
            LEFT JOIN Electronics e ON e.product_id = p.product_id
            LEFT JOIN Perishables pe ON pe.product_id = p.product_id
            ORDER BY p.product_id ASC
            """
        ).fetchall()

    products: List[Product] = []

    # Convert database rows into domain objects
    for r in rows:
        ptype = r["product_type"]

        if ptype == "electronics":
            products.append(
                ElectronicsProduct(
                    r["product_id"], r["name"], r["price"],
                    r["stock_quantity"], r["warranty_period"] or 0
                )
            )
        elif ptype == "perishable":
            products.append(
                PerishableProduct(
                    r["product_id"], r["name"], r["price"],
                    r["stock_quantity"], r["expiration_date"] or ""
                )
            )
        else:
            products.append(
                Product(
                    r["product_id"], r["name"], r["price"],
                    r["stock_quantity"]
                )
            )

    return products

# Search products by partial name match
def search_products_by_name(query: str) -> List[Product]:
    like = f"%{query.strip()}%"

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT p.product_id, p.name, p.price, p.stock_quantity, p.product_type,
                   e.warranty_period,
                   pe.expiration_date
            FROM Products p
            LEFT JOIN Electronics e ON e.product_id = p.product_id
            LEFT JOIN Perishables pe ON pe.product_id = p.product_id
            WHERE p.name LIKE ?
            ORDER BY p.name ASC
            """,
            (like,),
        ).fetchall()

    results: List[Product] = []

    for r in rows:
        ptype = r["product_type"]

        if ptype == "electronics":
            results.append(ElectronicsProduct(r["product_id"], r["name"], r["price"], r["stock_quantity"], r["warranty_period"] or 0))
        elif ptype == "perishable":
            results.append(PerishableProduct(r["product_id"], r["name"], r["price"], r["stock_quantity"], r["expiration_date"] or ""))
        else:
            results.append(Product(r["product_id"], r["name"], r["price"], r["stock_quantity"]))

    return results

# Retrieve recent sales history 
def fetch_sales_history(limit: int = 200) -> List[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT s.sale_id, s.product_id, p.name, s.quantity, s.total_amount, s.sale_timestamp
            FROM Sales s
            JOIN Products p ON p.product_id = s.product_id
            ORDER BY s.sale_id DESC
            LIMIT ?
            """,
            (int(limit),),
        ).fetchall()