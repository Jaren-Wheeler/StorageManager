import tkinter as tk
from tkinter import messagebox, simpledialog

import db
from inventory import Inventory
from models import Sale, ValidationError


# Main window and UI controller.
# user interaction with the domain and database layers.
class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Inventory and Sales Management System")
        self.geometry("900x500")
        
        db.init_db()

        self.inventory = Inventory()
        self.reload_inventory()

        self.create_widgets()

    # Refresh in-memory inventory from database
    def reload_inventory(self) -> None:
        self.inventory = Inventory()
        for p in db.fetch_all_products():
            self.inventory.upsert_product(p)

    # Build main UI layout and buttons
    def create_widgets(self) -> None:
        left = tk.Frame(self, padx=10, pady=10)
        left.pack(side=tk.LEFT, fill=tk.Y)

        tk.Button(left, text="Add Product", width=22, command=self.add_product_ui).pack(pady=5)
        tk.Button(left, text="Remove Product", width=22, command=self.remove_product_ui).pack(pady=5)
        tk.Button(left, text="List Products", width=22, command=self.list_products_ui).pack(pady=5)
        tk.Button(left, text="Sell Product", width=22, command=self.sell_product_ui).pack(pady=5)
        tk.Button(left, text="Restock Product", width=22, command=self.restock_product_ui).pack(pady=5)

        tk.Button(left, text="Exit", width=22, command=self.destroy).pack(pady=15)

        self.output = tk.Text(self, wrap="word")
        self.output.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=10, pady=10)

        self.print_line("Loaded. Use the buttons on the left.")

    # Add text to output panel
    def print_line(self, text: str) -> None:
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)

    # Placeholder for full Add Product form 
    def add_product_ui(self) -> None:
        messagebox.showinfo(
            "TODO",
            "add product form",
        )

    # Remove product with user input
    def remove_product_ui(self) -> None:
        try:
            pid = simpledialog.askinteger("Remove Product", "Enter product_id")
            if pid is None:
                return
            db.delete_product(pid)
            self.reload_inventory()
            self.print_line(f"Removed product {pid}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # Display all products in inventory
    def list_products_ui(self) -> None:
        self.reload_inventory()
        self.print_line("Products:")
        for p in self.inventory.list_all_products():
            self.print_line("  " + p.get_product_details())

    # Process a product sale
    def sell_product_ui(self) -> None:
        try:
            pid = simpledialog.askinteger("Sell Product", "Enter product_id")
            if pid is None:
                return
            qty = simpledialog.askinteger("Sell Product", "Enter quantity to sell")
            if qty is None:
                return

            self.reload_inventory()
            product = self.inventory.get_product(pid)
            if product is None:
                raise KeyError("product_id not found.")

            sale = Sale.create(product, qty)

            # Persist stock change and record sale
            db.update_stock(product.product_id, product.stock_quantity)
            db.insert_sale(product.product_id, sale.quantity, sale.total_amount)

            self.reload_inventory()
            self.print_line(f"Sold {qty} of {product.name}. Total ${sale.total_amount:.2f}")

        except (ValidationError, KeyError, ValueError) as e:
            messagebox.showerror("Cannot sell", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # Increase product stock
    def restock_product_ui(self) -> None:
        try:
            pid = simpledialog.askinteger("Restock Product", "Enter product_id")
            if pid is None:
                return
            qty = simpledialog.askinteger("Restock Product", "Enter quantity to add")
            if qty is None:
                return
            if qty <= 0:
                raise ValueError("quantity must be positive.")

            self.reload_inventory()
            product = self.inventory.get_product(pid)
            if product is None:
                raise KeyError("product_id not found.")

            product.update_stock(qty)
            db.update_stock(product.product_id, product.stock_quantity)

            self.reload_inventory()
            self.print_line(f"Restocked {product.name} by {qty}. New stock {product.stock_quantity}")

        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    App().mainloop()