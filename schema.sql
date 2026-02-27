-- Turn on foreign key rules so related records stay consistent
PRAGMA foreign_keys = ON;


-- Base product records shared by all product types.
-- Extra fields for specific types are stored in separate tables.
CREATE TABLE IF NOT EXISTS Products (
  product_id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  price REAL NOT NULL CHECK (price > 0),
  stock_quantity INTEGER NOT NULL CHECK (stock_quantity >= 0),
  product_type TEXT NOT NULL CHECK (product_type IN ('base','electronics','perishable'))
);


-- Stores warranty info for electronic products 1:1 with Products.
CREATE TABLE IF NOT EXISTS Electronics (
  product_id INTEGER PRIMARY KEY,
  warranty_period INTEGER NOT NULL CHECK (warranty_period >= 0),
  FOREIGN KEY (product_id) REFERENCES Products(product_id) ON DELETE CASCADE
);


-- Stores expiration info for perishable products 1:1 with Products.
CREATE TABLE IF NOT EXISTS Perishables (
  product_id INTEGER PRIMARY KEY,
  expiration_date TEXT NOT NULL,
  FOREIGN KEY (product_id) REFERENCES Products(product_id) ON DELETE CASCADE
);


-- Records each sale transaction.
-- Total amount is saved so past sales remain accurate if prices change later.
CREATE TABLE IF NOT EXISTS Sales (
  sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
  product_id INTEGER NOT NULL,
  quantity INTEGER NOT NULL CHECK (quantity > 0),
  total_amount REAL NOT NULL CHECK (total_amount >= 0),
  sale_timestamp TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (product_id) REFERENCES Products(product_id) ON DELETE RESTRICT
);