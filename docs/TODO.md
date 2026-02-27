# Inventory System  TODO

##  What’s Done

- Database schema 
- Product models and validation
- Inventory class
- Database functions 
- Basic UI window
- Sell product working
- Restock product working

**So the core structure is set up!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!.**

---

## What Still Needs To Be Done

### Add Product UI 

We need a real form for adding products.

It needs:

- Product ID
- Name
- Price
- Stock Quantity
- Type (Base / Electronics / Perishable)

**Conditional fields:**

- If Electronics → ask for warranty period  
- If Perishable → ask for expiration date  

Then:

- Call `db.insert_product()`
- Refresh inventory

> This is the only missing main feature.

---

### Extra features

We have to add two things as a group of 3. 
These are probably good choices:
- Low stock warning
- View sales history
- Search products by name
- Daily sales summary
- Update product price

---