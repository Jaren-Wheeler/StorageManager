# Architecture Overview

This project follows a simple layered structure to separate responsibilities.

The system is divided into five main parts:

- **schema.sql** → defines database structure  
- **db.py** → handles database operations  
- **models.py** → contains business logic and validation  
- **inventory.py** → manages products in memory  
- **app.py** → user interface 

---

## Layered Structure

The application follows this flow:

**UI → Inventory → Models → Database → SQLite**

Each layer has a specific responsibility and does not mix concerns.

---

## File Responsibilities

### schema.sql

Creates database tables and defines relationships between them.

---

### models.py

Defines:

- Product classes  
- Inheritance (Electronics, Perishable)  
- Validation rules  
- Sale logic  

This layer controls how objects behave.

---

### inventory.py

- Stores product objects in memory using a dictionary  
- Provides methods to add, remove, retrieve, and list products  

---

### db.py

- Handles all SQL operations  
- Converts database rows into Python objects and vice versa  

---

### app.py

Handles:

- User input  
- Display output  
- Calling business logic  
- Calling database functions  

> No SQL or validation logic is written directly in the UI layer.

---

## Data Flow Example (Selling a Product)

1. User clicks **"Sell Product"**  
2. UI collects product ID and quantity  
3. Inventory retrieves product object  
4. `Sale.create()` validates stock and calculates total  
5. `db.update_stock()` updates database  
6. `db.insert_sale()` records transaction  

This keeps validation in **models** and persistence in **db.py**.

---

## OOP and Database Mapping

The system uses inheritance:

Product
→ ElectronicsProduct
→ PerishableProduct

This maps to the database using separate tables:

- **Products**  
- **Electronics**  
- **Perishables**  

This design keeps shared attributes in one table and subtype specific attributes in separate tables.