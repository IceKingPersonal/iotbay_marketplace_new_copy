#Creates the actual database tables.
import sqlite3
from werkzeug.security import generate_password_hash


DATABASE = "iotbay.db"


def create_tables():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,

            role TEXT NOT NULL CHECK(role IN ('customer', 'staff')),

            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,

            phone TEXT,
            address TEXT,

            staff_id TEXT UNIQUE,
            position TEXT,

            status TEXT NOT NULL DEFAULT 'active'
                CHECK(status IN ('active', 'inactive')),

            created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_access_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            login_time TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            logout_time TEXT,

            created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),

            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS devices (
            device_id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,
            category TEXT NOT NULL
                CHECK(category IN (
                    'sensor',
                    'actuator',
                    'controller',
                    'gateway',
                    'camera',
                    'wearable',
                    'smart_home',
                    'industrial',
                    'accessory',
                    'other'
                )),
            brand TEXT NOT NULL,
            model TEXT NOT NULL,
            description TEXT,

            price REAL NOT NULL CHECK(price >= 0),
            stock_quantity INTEGER NOT NULL DEFAULT 0
                CHECK(stock_quantity >= 0),

            condition TEXT NOT NULL DEFAULT 'new'
                CHECK(condition IN ('new', 'used', 'refurbished')),

            status TEXT NOT NULL DEFAULT 'active'
                CHECK(status IN ('active', 'inactive', 'archived')),

            created_by INTEGER,
            updated_by INTEGER,

            created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),

            FOREIGN KEY (created_by) REFERENCES users(user_id),
            FOREIGN KEY (updated_by) REFERENCES users(user_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS device_audit_logs (
            audit_id INTEGER PRIMARY KEY AUTOINCREMENT,

            device_id INTEGER NOT NULL,
            staff_user_id INTEGER NOT NULL,

            action TEXT NOT NULL
                CHECK(action IN ('created', 'updated', 'deleted')),
            details TEXT,

            created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),

            FOREIGN KEY (device_id) REFERENCES devices(device_id),
            FOREIGN KEY (staff_user_id) REFERENCES users(user_id)
        )
    """)

    connection.commit()
    connection.close()


def insert_sample_data():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    sample_users = [
        {
            "role": "customer",
            "full_name": "Test Customer",
            "email": "customer@test.com",
            "password_hash": generate_password_hash("Password123"),
            "phone": "0412345678",
            "address": "1 Test Street, Sydney",
            "staff_id": None,
            "position": None
        },
        {
            "role": "staff",
            "full_name": "Test Staff",
            "email": "staff@test.com",
            "password_hash": generate_password_hash("Password123"),
            "phone": None,
            "address": None,
            "staff_id": "S001",
            "position": "Sales Assistant"
        }
    ]

    for user in sample_users:
        try:
            cursor.execute("""
                INSERT INTO users (
                    role,
                    full_name,
                    email,
                    password_hash,
                    phone,
                    address,
                    staff_id,
                    position
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user["role"],
                user["full_name"],
                user["email"],
                user["password_hash"],
                user["phone"],
                user["address"],
                user["staff_id"],
                user["position"]
            ))
        except sqlite3.IntegrityError:
            pass

    connection.commit()
    connection.close()


if __name__ == "__main__":
    create_tables()
    insert_sample_data()
    print("Database created successfully.")
