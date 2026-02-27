from __future__ import annotations
from typing import Dict, List, Optional
from models import Product


# Manages products in memory while the application is running
# Uses a dictionary for lookup by product_id
class Inventory:
    def __init__(self) -> None:
        self._products: Dict[int, Product] = {}

    # Add a new product to inventory 
    def add_product(self, product: Product) -> None:
        if product.product_id in self._products:
            raise ValueError("product_id already exists in inventory.")
        self._products[product.product_id] = product

    # Remove a product from inventory
    def remove_product(self, product_id: int) -> None:
        if product_id not in self._products:
            raise KeyError("product_id not found.")
        del self._products[int(product_id)]

    # Retrieve a product by ID 
    def get_product(self, product_id: int) -> Optional[Product]:
        return self._products.get(int(product_id))

    # Return all products currently loaded in memory
    def list_all_products(self) -> List[Product]:
        return list(self._products.values())

    # Add or replace a product 
    def upsert_product(self, product: Product) -> None:
        self._products[product.product_id] = product