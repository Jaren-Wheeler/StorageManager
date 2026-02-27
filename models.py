from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime


# Custom exception used for validation and business rule violations
class ValidationError(ValueError):
    pass


# Base product model containing shared attributes and core inventory logic
@dataclass
class Product:
    product_id: int
    name: str
    price: float
    stock_quantity: int

    # Runs after object creation to enforce data validity
    def __post_init__(self) -> None:
        if self.product_id <= 0:
            raise ValidationError("product_id must be a positive integer.")
        if not self.name.strip():
            raise ValidationError("name is required.")
        if self.price <= 0:
            raise ValidationError("price must be greater than zero.")
        if self.stock_quantity < 0:
            raise ValidationError("stock_quantity cannot be negative.")

    # Update product price with validation
    def update_price(self, new_price: float) -> None:
        if new_price <= 0:
            raise ValidationError("price must be greater than zero.")
        self.price = float(new_price)

    # Adjust stock level 
    def update_stock(self, quantity: int) -> None:
        new_qty = self.stock_quantity + int(quantity)
        if new_qty < 0:
            raise ValidationError("stock_quantity cannot become negative.")
        self.stock_quantity = new_qty

    # Check if enough stock exists for a requested quantity
    def is_in_stock(self, quantity: int) -> bool:
        return self.stock_quantity >= int(quantity)

    # Reduce stock when a sale occurs
    def sell(self, quantity: int) -> None:
        qty = int(quantity)
        if qty <= 0:
            raise ValidationError("quantity must be a positive integer.")
        if not self.is_in_stock(qty):
            raise ValidationError("insufficient stock.")
        self.stock_quantity -= qty

    # Summary
    def get_product_details(self) -> str:
        return f"ID {self.product_id} | {self.name} | ${self.price:.2f} | Stock {self.stock_quantity}"


# Electronics product subtype with additional warranty attribute
@dataclass
class ElectronicsProduct(Product):
    warranty_period: int = 0

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.warranty_period < 0:
            raise ValidationError("warranty_period cannot be negative.")

    # Extends base details with warranty info
    def get_product_details(self) -> str:
        base = super().get_product_details()
        return f"{base} | Warranty {self.warranty_period} months"


# Perishable product subtype with expiration tracking
@dataclass
class PerishableProduct(Product):
    expiration_date: str = ""

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.expiration_date.strip():
            raise ValidationError("expiration_date is required.")
        try:
            datetime.strptime(self.expiration_date, "%Y-%m-%d")
        except ValueError as e:
            raise ValidationError("expiration_date must be YYYY-MM-DD.") from e

    # Extends base details with expiration info
    def get_product_details(self) -> str:
        base = super().get_product_details()
        return f"{base} | Expires {self.expiration_date}"


# Represents a single sales transaction.
# Responsible for validating stock and calculating total sale value.
@dataclass
class Sale:
    product: Product
    quantity: int
    total_amount: float

    @classmethod
    def create(cls, product: Product, quantity: int) -> Sale:
        qty = int(quantity)
        if qty <= 0:
            raise ValidationError("quantity must be a positive integer.")
        if not product.is_in_stock(qty):
            raise ValidationError("insufficient stock.")
        product.sell(qty)
        total = float(product.price) * qty
        return cls(product=product, quantity=qty, total_amount=total)