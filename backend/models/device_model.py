from database import get_db


class DeviceModel:

    @staticmethod
    def create_device(data, staff_user_id):
        db = get_db()

        cursor = db.execute("""
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
            data.get("name"),
            data.get("category"),
            data.get("brand"),
            data.get("model"),
            data.get("description"),
            data.get("price"),
            data.get("stock_quantity"),
            data.get("condition"),
            data.get("status"),
            staff_user_id,
            staff_user_id
        ))

        device_id = cursor.lastrowid
        DeviceModel.create_audit_log(
            device_id,
            staff_user_id,
            "created",
            "Device created."
        )

        db.commit()
        return device_id

    @staticmethod
    def find_by_id(device_id):
        db = get_db()

        device = db.execute("""
            SELECT *
            FROM devices
            WHERE device_id = ?
        """, (device_id,)).fetchone()

        return device

    @staticmethod
    def list_devices(filters):
        db = get_db()

        query = """
            SELECT *
            FROM devices
            WHERE status = 'active'
        """
        values = []

        if filters.get("search"):
            query += """
                AND (
                    name LIKE ?
                    OR category LIKE ?
                    OR brand LIKE ?
                    OR model LIKE ?
                    OR description LIKE ?
                )
            """
            search_value = f"%{filters.get('search')}%"
            values.extend([
                search_value,
                search_value,
                search_value,
                search_value,
                search_value
            ])

        if filters.get("category"):
            query += " AND category = ?"
            values.append(filters.get("category"))

        if filters.get("brand"):
            query += " AND brand LIKE ?"
            values.append(f"%{filters.get('brand')}%")

        if filters.get("condition"):
            query += " AND condition = ?"
            values.append(filters.get("condition"))

        if filters.get("min_price") is not None:
            query += " AND price >= ?"
            values.append(filters.get("min_price"))

        if filters.get("max_price") is not None:
            query += " AND price <= ?"
            values.append(filters.get("max_price"))

        if filters.get("in_stock"):
            query += " AND stock_quantity > 0"

        query += """
            ORDER BY name ASC,
                     device_id ASC
        """

        devices = db.execute(query, values).fetchall()

        return devices

    @staticmethod
    def update_device(device_id, data, staff_user_id):
        db = get_db()

        db.execute("""
            UPDATE devices
            SET name = ?,
                category = ?,
                brand = ?,
                model = ?,
                description = ?,
                price = ?,
                stock_quantity = ?,
                condition = ?,
                status = ?,
                updated_by = ?,
                updated_at = datetime('now', 'localtime')
            WHERE device_id = ?
        """, (
            data.get("name"),
            data.get("category"),
            data.get("brand"),
            data.get("model"),
            data.get("description"),
            data.get("price"),
            data.get("stock_quantity"),
            data.get("condition"),
            data.get("status"),
            staff_user_id,
            device_id
        ))

        DeviceModel.create_audit_log(
            device_id,
            staff_user_id,
            "updated",
            "Device updated."
        )

        db.commit()
        return True

    @staticmethod
    def delete_device(device_id, staff_user_id):
        db = get_db()

        db.execute("""
            UPDATE devices
            SET status = 'archived',
                updated_by = ?,
                updated_at = datetime('now', 'localtime')
            WHERE device_id = ?
        """, (
            staff_user_id,
            device_id
        ))

        DeviceModel.create_audit_log(
            device_id,
            staff_user_id,
            "deleted",
            "Device archived."
        )

        db.commit()
        return True

    @staticmethod
    def create_audit_log(device_id, staff_user_id, action, details):
        db = get_db()

        db.execute("""
            INSERT INTO device_audit_logs (
                device_id,
                staff_user_id,
                action,
                details
            )
            VALUES (?, ?, ?, ?)
        """, (
            device_id,
            staff_user_id,
            action,
            details
        ))

    @staticmethod
    def find_audit_logs_by_device_id(device_id):
        db = get_db()

        logs = db.execute("""
            SELECT *
            FROM device_audit_logs
            WHERE device_id = ?
            ORDER BY created_at DESC,
                     audit_id DESC
        """, (device_id,)).fetchall()

        return logs

    @staticmethod
    def to_dict(device):
        if device is None:
            return None

        return {
            "device_id": device["device_id"],
            "name": device["name"],
            "category": device["category"],
            "brand": device["brand"],
            "model": device["model"],
            "description": device["description"],
            "price": device["price"],
            "stock_quantity": device["stock_quantity"],
            "condition": device["condition"],
            "status": device["status"],
            "created_by": device["created_by"],
            "updated_by": device["updated_by"],
            "created_at": device["created_at"],
            "updated_at": device["updated_at"]
        }

    @staticmethod
    def to_list(devices):
        return [DeviceModel.to_dict(device) for device in devices]

    @staticmethod
    def audit_to_dict(log):
        return {
            "audit_id": log["audit_id"],
            "device_id": log["device_id"],
            "staff_user_id": log["staff_user_id"],
            "action": log["action"],
            "details": log["details"],
            "created_at": log["created_at"]
        }

    @staticmethod
    def audit_to_list(logs):
        return [DeviceModel.audit_to_dict(log) for log in logs]
