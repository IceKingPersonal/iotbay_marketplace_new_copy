from database import get_db

ORDER_STATUSES = ("Saved", "Paid", "Cancelled")


class OrderModel:
    @staticmethod
    def row_to_dict(row):
        return dict(row) if row else None

    @staticmethod
    def rows_to_list(rows):
        return [dict(r) for r in rows]

    @staticmethod
    def find_by_id(order_id):
        db = get_db()
        return db.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,)).fetchone()

    @staticmethod
    def find_items(order_id):
        db = get_db()
        return db.execute(
            """
            SELECT oi.*, p.device_name, p.manufacturer, p.type
            FROM order_items oi
            LEFT JOIN products p ON p.product_id = oi.product_id
            WHERE oi.order_id = ?
            ORDER BY oi.order_item_id
            """,
            (order_id,),
        ).fetchall()

    @staticmethod
    def list_for_customer(user_id, order_id=None, date_prefix=None):
        db = get_db()
        sql = "SELECT * FROM orders WHERE user_id = ?"
        params = [user_id]
        if order_id is not None:
            sql += " AND order_id = ?"
            params.append(order_id)
        if date_prefix:
            sql += " AND created_at LIKE ?"
            params.append(f"{date_prefix}%")
        sql += " ORDER BY order_id DESC"
        return db.execute(sql, params).fetchall()

    @staticmethod
    def list_all_customer_orders(order_id=None, date_prefix=None):
        db = get_db()
        sql = """
            SELECT o.*, u.full_name AS customer_name, u.email AS customer_email
            FROM orders o
            JOIN users u ON u.user_id = o.user_id
            WHERE u.role = 'customer'
        """
        params = []
        if order_id is not None:
            sql += " AND o.order_id = ?"
            params.append(order_id)
        if date_prefix:
            sql += " AND o.created_at LIKE ?"
            params.append(f"{date_prefix}%")
        sql += " ORDER BY o.order_id DESC"
        return db.execute(sql, params).fetchall()

    @staticmethod
    def create_order(user_id, shipping_address, currency, total_price):
        db = get_db()
        cursor = db.execute(
            """
            INSERT INTO orders (user_id, shipping_address, total_price, currency, status)
            VALUES (?, ?, ?, ?, 'Saved')
            """,
            (user_id, shipping_address, total_price, currency),
        )
        return cursor.lastrowid

    @staticmethod
    def insert_item(order_id, product_id, quantity, unit_price):
        db = get_db()
        db.execute(
            """
            INSERT INTO order_items (order_id, product_id, quantity, unit_price)
            VALUES (?, ?, ?, ?)
            """,
            (order_id, product_id, quantity, unit_price),
        )

    @staticmethod
    def update_order_fields(order_id, shipping_address, total_price, currency, status):
        db = get_db()
        db.execute(
            """
            UPDATE orders
            SET shipping_address = ?, total_price = ?, currency = ?, status = ?
            WHERE order_id = ?
            """,
            (shipping_address, total_price, currency, status, order_id),
        )

    @staticmethod
    def update_status(order_id, status):
        db = get_db()
        db.execute("UPDATE orders SET status = ? WHERE order_id = ?", (status, order_id))

    @staticmethod
    def delete_items(order_id):
        db = get_db()
        db.execute("DELETE FROM order_items WHERE order_id = ?", (order_id,))

    @staticmethod
    def get_product(product_id):
        db = get_db()
        return db.execute(
            "SELECT product_id, price, stock_qty FROM products WHERE product_id = ?",
            (product_id,),
        ).fetchone()

    @staticmethod
    def adjust_stock(product_id, delta):
        db = get_db()
        db.execute(
            "UPDATE products SET stock_qty = stock_qty + ? WHERE product_id = ?",
            (delta, product_id),
        )
