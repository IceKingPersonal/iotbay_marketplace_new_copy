from db import get_db


def seed_products_if_empty() -> None:
    row = get_db().execute("SELECT COUNT(*) AS c FROM products").fetchone()
    if row["c"] > 0:
        return

    db = get_db()
    db.execute(
        """
        INSERT INTO products (products_uid, device_name, manufacturer, type, price, qty, unit_type)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (1, "Moisture U7 Sensor", "Ubiquiti", "Sensor", 2049, 50, "Each"),
    )
    db.execute(
        """
        INSERT INTO products (products_uid, device_name, manufacturer, type, price, qty, unit_type)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (2, "DC Motor Kit 12V", "SparkFun", "DC Motors", 4999, 30, "Each"),
    )
    db.execute(
        """
        INSERT INTO products (products_uid, device_name, manufacturer, type, price, qty, unit_type)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (3, "LoRa Gateway Pro", "RAK", "Gateway", 18900, 10, "Each"),
    )
    db.commit()
