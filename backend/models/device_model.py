from database import get_db


def _price_to_cents(price):
    return int(round(float(price) * 100))


def _price_to_dollars(cents):
    return round(int(cents) / 100, 2)


class DeviceModel:
    @staticmethod
    def create_device(data, staff_user_id):
        db = get_db()

        cursor = db.execute(
            """
            INSERT INTO products (
                device_name,
                type,
                manufacturer,
                model,
                description,
                price,
                stock_qty,
                condition,
                status,
                created_by,
                updated_by
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data.get("name"),
                data.get("category"),
                data.get("brand"),
                data.get("model"),
                data.get("description"),
                _price_to_cents(data.get("price")),
                data.get("stock_quantity"),
                data.get("condition"),
                data.get("status"),
                staff_user_id,
                staff_user_id,
            ),
        )

        product_id = cursor.lastrowid
        DeviceModel.create_audit_log(
            product_id,
            staff_user_id,
            "created",
            "Device created.",
        )

        db.commit()
        return product_id

    @staticmethod
    def find_by_id(device_id):
        db = get_db()

        return db.execute(
            """
            SELECT *
            FROM products
            WHERE product_id = ?
            """,
            (device_id,),
        ).fetchone()

    @staticmethod
    def find_by_ids(device_ids):
        db = get_db()
        placeholders = ", ".join(["?"] * len(device_ids))

        return db.execute(
            f"""
            SELECT *
            FROM products
            WHERE product_id IN ({placeholders})
            """,
            device_ids,
        ).fetchall()

    @staticmethod
    def list_devices(filters):
        db = get_db()

        query = """
            SELECT *
            FROM products
            WHERE status = 'active'
        """
        values = []

        if filters.get("search"):
            query += """
                AND (
                    device_name LIKE ?
                    OR type LIKE ?
                    OR manufacturer LIKE ?
                    OR model LIKE ?
                    OR description LIKE ?
                )
            """
            search_value = f"%{filters.get('search')}%"
            values.extend([search_value] * 5)

        if filters.get("category"):
            query += " AND type = ?"
            values.append(filters.get("category"))

        if filters.get("brand"):
            query += " AND manufacturer LIKE ?"
            values.append(f"%{filters.get('brand')}%")

        if filters.get("condition"):
            query += " AND condition = ?"
            values.append(filters.get("condition"))

        if filters.get("min_price") is not None:
            query += " AND price >= ?"
            values.append(_price_to_cents(filters.get("min_price")))

        if filters.get("max_price") is not None:
            query += " AND price <= ?"
            values.append(_price_to_cents(filters.get("max_price")))

        if filters.get("in_stock"):
            query += " AND stock_qty > 0"

        query += """
            ORDER BY device_name ASC,
                     product_id ASC
        """

        return db.execute(query, values).fetchall()

    @staticmethod
    def update_device(device_id, data, staff_user_id):
        db = get_db()

        db.execute(
            """
            UPDATE products
            SET device_name = ?,
                type = ?,
                manufacturer = ?,
                model = ?,
                description = ?,
                price = ?,
                stock_qty = ?,
                condition = ?,
                status = ?,
                updated_by = ?,
                updated_at = datetime('now', 'localtime')
            WHERE product_id = ?
            """,
            (
                data.get("name"),
                data.get("category"),
                data.get("brand"),
                data.get("model"),
                data.get("description"),
                _price_to_cents(data.get("price")),
                data.get("stock_quantity"),
                data.get("condition"),
                data.get("status"),
                staff_user_id,
                device_id,
            ),
        )

        DeviceModel.create_audit_log(
            device_id,
            staff_user_id,
            "updated",
            "Device updated.",
        )

        db.commit()
        return True

    @staticmethod
    def delete_device(device_id, staff_user_id):
        db = get_db()

        db.execute(
            """
            UPDATE products
            SET status = 'archived',
                updated_by = ?,
                updated_at = datetime('now', 'localtime')
            WHERE product_id = ?
            """,
            (staff_user_id, device_id),
        )

        DeviceModel.create_audit_log(
            device_id,
            staff_user_id,
            "deleted",
            "Device archived.",
        )

        db.commit()
        return True

    @staticmethod
    def delete_devices(device_ids, staff_user_id):
        db = get_db()

        for device_id in device_ids:
            db.execute(
                """
                UPDATE products
                SET status = 'archived',
                    updated_by = ?,
                    updated_at = datetime('now', 'localtime')
                WHERE product_id = ?
                """,
                (staff_user_id, device_id),
            )

            DeviceModel.create_audit_log(
                device_id,
                staff_user_id,
                "deleted",
                "Device archived.",
            )

        db.commit()
        return device_ids

    @staticmethod
    def create_audit_log(product_id, staff_user_id, action, details):
        db = get_db()

        db.execute(
            """
            INSERT INTO product_audit_logs (
                product_id,
                staff_user_id,
                action,
                details
            )
            VALUES (?, ?, ?, ?)
            """,
            (product_id, staff_user_id, action, details),
        )

    @staticmethod
    def find_audit_logs_by_device_id(device_id):
        db = get_db()

        return db.execute(
            """
            SELECT *
            FROM product_audit_logs
            WHERE product_id = ?
            ORDER BY created_at DESC,
                     audit_id DESC
            """,
            (device_id,),
        ).fetchall()

    @staticmethod
    def to_dict(product):
        if product is None:
            return None

        row_keys = product.keys()

        return {
            "device_id": product["product_id"],
            "name": product["device_name"],
            "category": product["type"],
            "brand": product["manufacturer"],
            "model": product["model"] if "model" in row_keys else None,
            "description": product["description"] if "description" in row_keys else None,
            "price": _price_to_dollars(product["price"]),
            "stock_quantity": product["stock_qty"],
            "condition": product["condition"] if "condition" in row_keys else "new",
            "status": product["status"] if "status" in row_keys else "active",
            "created_by": product["created_by"] if "created_by" in row_keys else None,
            "updated_by": product["updated_by"] if "updated_by" in row_keys else None,
            "created_at": product["created_at"] if "created_at" in row_keys else None,
            "updated_at": product["updated_at"] if "updated_at" in row_keys else None,
        }

    @staticmethod
    def to_list(devices):
        return [DeviceModel.to_dict(device) for device in devices]

    @staticmethod
    def audit_to_dict(log):
        return {
            "audit_id": log["audit_id"],
            "device_id": log["product_id"],
            "staff_user_id": log["staff_user_id"],
            "action": log["action"],
            "details": log["details"],
            "created_at": log["created_at"],
        }

    @staticmethod
    def audit_to_list(logs):
        return [DeviceModel.audit_to_dict(log) for log in logs]
