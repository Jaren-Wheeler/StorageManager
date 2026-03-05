import tkinter as tk
from tkinter import messagebox, simpledialog, Frame

import db
from inventory import Inventory
from models import Sale, ValidationError, ElectronicsProduct, PerishableProduct


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
        tk.Button(left, text="Update Price", width=22, command=self.update_price_ui).pack(pady=5)


        tk.Button(left, text="Exit", width=22, command=self.destroy).pack(pady=15)

        self.output = tk.Text(self, wrap="word")
        self.output.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=10, pady=10)

        self.print_line("Loaded. Use the buttons on the left.")

        
    # Add text to output panel
    def print_line(self, text: str) -> None:
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)

    # Logic and UI for adding products
    def add_product_ui(self) -> None:
        modal = tk.Toplevel(self)
        modal.geometry("320x380")
        modal.title("Add Product")

        # Name
        tk.Label(modal, text="Product Name").pack(pady=5)
        name_entry = tk.Entry(modal)
        name_entry.pack(pady=5)

        # Price
        tk.Label(modal, text="Price").pack(pady=5)
        price_entry = tk.Entry(modal)
        price_entry.pack(pady=5)

        # Quantity
        tk.Label(modal, text="Quantity").pack(pady=5)
        qty_entry = tk.Entry(modal)
        qty_entry.pack(pady=5)

        # Product Type
        tk.Label(modal, text="Product Type").pack(pady=5)

        options = ["electronics", "perishable"]
        selected_type = tk.StringVar(modal)
        selected_type.set(options[0])

        tk.OptionMenu(modal, selected_type, *options).pack(pady=5)

        # Subtype Field Label
        extra_label = tk.Label(modal)
        extra_label.pack(pady=5)

        extra_entry = tk.Entry(modal)
        extra_entry.pack(pady=5)

        # Dynamically update extra field label
        def update_extra_field(*args):
            if selected_type.get() == "electronics":
                extra_label.config(text="Warranty Period (months)")
            else:
                extra_label.config(text="Expiration Date (YYYY-MM-DD)")

        selected_type.trace("w", update_extra_field)
        update_extra_field()

        # Submit logic
        def submit():
            try:
                name = name_entry.get().strip()
                price = float(price_entry.get())
                qty = int(qty_entry.get())
                ptype = selected_type.get()

                if not name:
                    raise ValueError("Product name is required.")
                if price <= 0:
                    raise ValueError("Price must be positive.")
                if qty < 0:
                    raise ValueError("Quantity cannot be negative.")

                if ptype == "electronics":
                    warranty = int(extra_entry.get())
                    product = ElectronicsProduct(
                        None, name, price, qty, warranty
                    )

                else:
                    expiration = extra_entry.get().strip()
                    if not expiration:
                        raise ValueError("Expiration date required.")
                    product = PerishableProduct(
                        None, name, price, qty, expiration
                    )

                # DB call
                db.insert_product(product)

                self.reload_inventory()
                self.print_line(f"Added product '{name}' (ID {product.product_id})")

                modal.destroy()

            except Exception as e:
                messagebox.showerror("Error", str(e))

        # Buttons
        button_frame = tk.Frame(modal)
        button_frame.pack(pady=15)

        tk.Button(button_frame, text="Cancel", command=modal.destroy).pack(side="left", padx=10)
        tk.Button(button_frame, text="Submit", command=submit).pack(side="right", padx=10)

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

    # Search products by name
    def search_product_ui(self) -> None:
        try:
            name= simpledialog.askstring("Search Product", "Enter Product Name")
            if name is None:
                return

            self.reload_inventory()
            product = self.inventory.search_product(name)
            if product is None:
                self.print_line(f"Product: {name}, not found.")
            else:
                self.print_line("  " + product.get_product_details())

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # Update Product Price
    def update_price_ui(self) -> None:
        try:
            pid = simpledialog.askinteger("Update Price", "Enter A Product ID")
            if pid is None:
                return
            new_price = simpledialog.askfloat("Update Price", "Enter New Price")
            if new_price is None:
                return
            
            self.reload_inventory()
            product = self.inventory.get_product(pid)
            if product is None:
                raise KeyError("product_id not found.")

            product.update_price(new_price)
            db.update_price(product.product_id, product.price)

            self.reload_inventory()
            self.print_line(f"Updated {product.name} price to ${product.price:.2f}")

        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    App().mainloop()