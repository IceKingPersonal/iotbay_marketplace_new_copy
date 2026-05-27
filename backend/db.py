import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "iotbay.db"

conn: sqlite3.Connection | None = None

SCHEMA = """
  CREATE TABLE IF NOT EXISTS users (
    user_uid INTEGER PRIMARY KEY,
    first_name VARCHAR(15) NOT NULL,
    last_name VARCHAR(20) NOT NULL,
    status BOOLEAN NOT NULL DEFAULT 1,
    last_logon DATETIME,
    last_logout DATETIME,
    password NVARCHAR(255) NOT NULL,
    email NVARCHAR(50) NOT NULL UNIQUE,
    phone NVARCHAR(12)
  );

  CREATE TABLE IF NOT EXISTS staff (
    user_uid INTEGER PRIMARY KEY,
    position VARCHAR(30) NOT NULL,
    staff_id INTEGER NOT NULL UNIQUE,
    FOREIGN KEY (user_uid) REFERENCES users(user_uid)
  );

  CREATE TABLE IF NOT EXISTS customer (
    user_uid INTEGER PRIMARY KEY,
    address NVARCHAR(60),
    FOREIGN KEY (user_uid) REFERENCES users(user_uid)
  );

  CREATE TABLE IF NOT EXISTS products (
    products_uid INTEGER PRIMARY KEY,
    device_name NVARCHAR(50) NOT NULL,
    manufacturer VARCHAR(40) NOT NULL,
    type VARCHAR(15) NOT NULL,
    price INTEGER NOT NULL,
    qty INTEGER NOT NULL DEFAULT 0,
    unit_type VARCHAR(10) NOT NULL
  );

  CREATE TABLE IF NOT EXISTS orders (
    orders_uid INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    shipping_address VARCHAR NOT NULL,
    date_created DATETIME NOT NULL DEFAULT (datetime('now')),
    total_price INTEGER NOT NULL,
    currency VARCHAR(3) NOT NULL,
    status VARCHAR(20) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_uid)
  );

  CREATE TABLE IF NOT EXISTS order_items (
    ord_item_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price INTEGER NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(orders_uid),
    FOREIGN KEY (product_id) REFERENCES products(products_uid)
  );

  CREATE TABLE IF NOT EXISTS payment_methods (
    pay_method_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    card_type VARCHAR(10) NOT NULL,
    token_id NVARCHAR(20) NOT NULL,
    display_name VARCHAR(20) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_uid)
  );

  CREATE TABLE IF NOT EXISTS payments (
    payments_id INTEGER PRIMARY KEY,
    pay_method_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    order_id INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL,
    total_amount INTEGER NOT NULL,
    currency VARCHAR(3) NOT NULL,
    external_id NVARCHAR(15),
    error_code NVARCHAR(25),
    created_at DATETIME NOT NULL DEFAULT (datetime('now')),
    updated_at DATETIME NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (pay_method_id) REFERENCES payment_methods(pay_method_id),
    FOREIGN KEY (user_id) REFERENCES users(user_uid),
    FOREIGN KEY (order_id) REFERENCES orders(orders_uid)
  );

  CREATE TABLE IF NOT EXISTS carts (
    carts_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    session_id INTEGER,
    status VARCHAR(20) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT (datetime('now')),
    updated_at DATETIME NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(user_uid)
  );

  CREATE TABLE IF NOT EXISTS cart_items (
    cart_items_id INTEGER PRIMARY KEY,
    cart_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price INTEGER NOT NULL,
    currency VARCHAR(3) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT (datetime('now')),
    updated_at DATETIME NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (cart_id) REFERENCES carts(carts_id),
    FOREIGN KEY (product_id) REFERENCES products(products_uid)
  );

  CREATE TABLE IF NOT EXISTS shipments (
    shipments_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    carrier VARCHAR(25) NOT NULL,
    tracking_number NVARCHAR(25),
    status VARCHAR(25) NOT NULL,
    shipped_at DATETIME,
    delivered_at DATETIME,
    created_at DATETIME NOT NULL DEFAULT (datetime('now')),
    updated_at DATETIME NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (order_id) REFERENCES orders(orders_uid)
  );

  CREATE TABLE IF NOT EXISTS logs (
    logs_uid INTEGER PRIMARY KEY,
    user_id INTEGER,
    description VARCHAR(70) NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT (datetime('now')),
    order_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(user_uid),
    FOREIGN KEY (order_id) REFERENCES orders(orders_uid)
  );
"""


def init_db() -> None:
    global conn
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)


def get_db() -> sqlite3.Connection:
    if conn is None:
        init_db()
    return conn


def row_to_dict(row: sqlite3.Row | None) -> dict | None:
    return dict(row) if row else None


def rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict]:
    return [dict(r) for r in rows]
