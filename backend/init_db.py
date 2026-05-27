#Creates the actual database tables.
import sqlite3
from werkzeug.security import generate_password_hash


DATABASE = "iotbay.db"


DEVICE_CATEGORIES = [
    "sensor",
    "actuator",
    "controller",
    "gateway",
    "camera",
    "wearable",
    "smart_home",
    "industrial",
    "accessory",
    "other"
]


SAMPLE_DEVICES = [
    {
        "name": "Smart Temperature Sensor",
        "category": "sensor",
        "brand": "IoTBay",
        "model": "SEN-TEMP-100",
        "description": "Wireless sensor for room temperature monitoring.",
        "price": 49.99,
        "stock_quantity": 25,
        "condition": "new",
        "status": "active"
    },
    {
        "name": "Valve Control Actuator",
        "category": "actuator",
        "brand": "ActuaTech",
        "model": "ACT-VALVE-200",
        "description": "Remote valve actuator for water systems.",
        "price": 89.50,
        "stock_quantity": 12,
        "condition": "used",
        "status": "active"
    },
    {
        "name": "Edge Logic Controller",
        "category": "controller",
        "brand": "ControlWorks",
        "model": "CTRL-EDGE-300",
        "description": "Programmable controller for local IoT automation.",
        "price": 149.00,
        "stock_quantity": 8,
        "condition": "refurbished",
        "status": "active"
    },
    {
        "name": "Long Range IoT Gateway",
        "category": "gateway",
        "brand": "Gateway Labs",
        "model": "GATE-LORA-400",
        "description": "Gateway for long range industrial network coverage.",
        "price": 219.99,
        "stock_quantity": 5,
        "condition": "new",
        "status": "inactive"
    },
    {
        "name": "Outdoor Security Camera",
        "category": "camera",
        "brand": "SecureView",
        "model": "CAM-OUT-500",
        "description": "Weather resistant connected camera.",
        "price": 129.95,
        "stock_quantity": 0,
        "condition": "used",
        "status": "archived"
    },
    {
        "name": "Health Band Wearable",
        "category": "wearable",
        "brand": "WearSense",
        "model": "WEAR-HB-600",
        "description": "Wearable device for health telemetry.",
        "price": 79.00,
        "stock_quantity": 18,
        "condition": "refurbished",
        "status": "active"
    },
    {
        "name": "Smart Home Hub",
        "category": "smart_home",
        "brand": "HomeMesh",
        "model": "HOME-HUB-700",
        "description": "Hub for smart home device orchestration.",
        "price": 99.00,
        "stock_quantity": 30,
        "condition": "new",
        "status": "active"
    },
    {
        "name": "Industrial Vibration Monitor",
        "category": "industrial",
        "brand": "PlantSense",
        "model": "IND-VIB-800",
        "description": "Industrial monitor for machine vibration data.",
        "price": 189.00,
        "stock_quantity": 9,
        "condition": "used",
        "status": "active"
    },
    {
        "name": "Mounting Accessory Kit",
        "category": "accessory",
        "brand": "InstallPro",
        "model": "ACC-MOUNT-900",
        "description": "Mounting hardware for IoT devices.",
        "price": 19.99,
        "stock_quantity": 40,
        "condition": "refurbished",
        "status": "inactive"
    },
    {
        "name": "Prototype IoT Device",
        "category": "other",
        "brand": "IoTBay",
        "model": "OTHER-PROTO-1000",
        "description": "Archived prototype record for testing catalogue status.",
        "price": 59.00,
        "stock_quantity": 0,
        "condition": "new",
        "status": "archived"
    }
]


def validate_sample_device_category_coverage():
    sample_categories = {device["category"] for device in SAMPLE_DEVICES}
    missing_categories = [
        category
        for category in DEVICE_CATEGORIES
        if category not in sample_categories
    ]

    if missing_categories:
        missing_list = ", ".join(missing_categories)
        raise ValueError(
            f"SAMPLE_DEVICES is missing category seed data for: {missing_list}"
        )


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
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_name TEXT NOT NULL,
            manufacturer TEXT,
            type TEXT,
            price INTEGER NOT NULL,
            stock_qty INTEGER NOT NULL DEFAULT 0,
            unit_type TEXT NOT NULL DEFAULT 'Each'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            shipping_address TEXT NOT NULL,
            total_price INTEGER NOT NULL,
            currency TEXT NOT NULL DEFAULT 'AUD',
            status TEXT NOT NULL DEFAULT 'Saved'
                CHECK(status IN ('Saved', 'Paid', 'Cancelled')),
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
        CREATE TABLE IF NOT EXISTS order_items (
            order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price INTEGER NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(order_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
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
    validate_sample_device_category_coverage()

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

    staff_user = cursor.execute("""
        SELECT user_id
        FROM users
        WHERE email = ?
    """, ("staff@test.com",)).fetchone()

    staff_user_id = staff_user[0] if staff_user else None

    for device in SAMPLE_DEVICES:
        existing_device = cursor.execute("""
            SELECT device_id
            FROM devices
            WHERE name = ?
              AND model = ?
        """, (
            device["name"],
            device["model"]
        )).fetchone()

        if existing_device:
            continue

        cursor.execute("""
            INSERT INTO devices (
                name,
                category,
                brand,
                model,
                description,
                price,
                stock_quantity,
                condition,
                status,
                created_by,
                updated_by
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            device["name"],
            device["category"],
            device["brand"],
            device["model"],
            device["description"],
            device["price"],
            device["stock_quantity"],
            device["condition"],
            device["status"],
            staff_user_id,
            staff_user_id
        ))
        
    sample_products = [
        ("Moisture U7 Sensor", "Ubiquiti", "Sensor", 2049, 50),
        ("DC Motor Kit 12V", "SparkFun", "DC Motors", 4999, 30),
        ("LoRa Gateway Pro", "RAK", "Gateway", 18900, 10),
    ]
    
    for product in sample_products:
        try:
            cursor.execute(
                """
                INSERT INTO products (device_name, manufacturer, type, price, stock_qty)
                VALUES (?, ?, ?, ?, ?)
                """,
                product,
            )
        except sqlite3.IntegrityError:
            pass
        
    connection.commit()
    connection.close()


if __name__ == "__main__":
    create_tables()
    insert_sample_data()
    print("Database created successfully.")
