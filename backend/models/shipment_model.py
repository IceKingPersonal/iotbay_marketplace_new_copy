from database import get_db


class ShipmentModel:

    @staticmethod
    def create(order_id, staff_user_id, recipient_name, delivery_address):
        db = get_db()

        cursor = db.execute("""
            INSERT INTO shipments (order_id, staff_user_id, recipient_name, delivery_address, status)
            VALUES (?, ?, ?, ?, 'pending')
        """, (order_id, staff_user_id, recipient_name, delivery_address))

        db.commit()
        return cursor.lastrowid



    @staticmethod
    def find_by_id(shipment_id):
        db = get_db()

        found_shipment = db.execute("""
            SELECT * FROM shipments
            WHERE shipment_id = ?
        """, (shipment_id,)).fetchone()

        return found_shipment




    @staticmethod
    def find_by_staff(staff_user_id):
        db = get_db()

        staff_shipments = db.execute("""
            SELECT * FROM shipments
            WHERE staff_user_id = ?
            ORDER BY created_at DESC
        """, (staff_user_id,)).fetchall()

        return staff_shipments



    @staticmethod
    def find_by_customer(customer_id):
        db = get_db()

        # orders table uses user_id column (not customer_id)
        customer_shipments = db.execute("""
            SELECT s.*
            FROM shipments s
            JOIN orders o ON s.order_id = o.order_id
            WHERE o.user_id = ?
            ORDER BY s.created_at DESC
        """, (customer_id,)).fetchall()

        return customer_shipments




    @staticmethod
    def update(shipment_id, new_status, new_recipient, new_address):
        db = get_db()

        db.execute("""
            UPDATE shipments
            SET status = ?,
                recipient_name = ?,
                delivery_address = ?,
                updated_at = datetime('now', 'localtime')
            WHERE shipment_id = ?
        """, (new_status, new_recipient, new_address, shipment_id))

        db.commit()
        return True




    @staticmethod
    def order_is_paid(order_id):
        db = get_db()

        order_row = db.execute("""
            SELECT status FROM orders
            WHERE order_id = ?
        """, (order_id,)).fetchone()

        if order_row is None:
            return False

        # orders table uses 'Paid' 
        return order_row["status"] == "Paid"




    @staticmethod
    def shipment_exists_for_order(order_id):
        db = get_db()

        existing_shipment = db.execute("""
            SELECT shipment_id FROM shipments
            WHERE order_id = ?
        """, (order_id,)).fetchone()

        return existing_shipment is not None




    @staticmethod
    def get_customer_name_for_order(order_id):
        db = get_db()

        # orders user_id, join with users to get the name
        name_row = db.execute("""
            SELECT u.full_name
            FROM orders o
            JOIN users u ON o.user_id = u.user_id
            WHERE o.order_id = ?
        """, (order_id,)).fetchone()

        if name_row is None:
            return "Unknown"

        return name_row["full_name"]





    @staticmethod
    def to_dict(shipment):
        if shipment is None:
            return None

        return {
            "shipment_id": shipment["shipment_id"],
            "order_id": shipment["order_id"],
            "staff_user_id": shipment["staff_user_id"],
            "recipient_name": shipment["recipient_name"],
            "delivery_address": shipment["delivery_address"],
            "status": shipment["status"],
            "created_at": shipment["created_at"],
            "updated_at": shipment["updated_at"]
        }


    @staticmethod
    def to_list(shipments):
        return [ShipmentModel.to_dict(s) for s in shipments]
