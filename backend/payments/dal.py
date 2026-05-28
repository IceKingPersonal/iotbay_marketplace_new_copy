from database import get_db


def get_saved_orders(db, customer_id):
    return db.execute(
        """
        SELECT order_id, total_price, created_at AS order_date
        FROM orders
        WHERE user_id = ? AND status = 'Saved'
        ORDER BY created_at DESC
        """,
        (customer_id,),
    ).fetchall()


def get_payment_methods(db, customer_id):
    return db.execute(
        """
        SELECT payment_method_id, payment_type, details
        FROM payment_methods
        WHERE customer_id = ?
        """,
        (customer_id,),
    ).fetchall()


def get_order(db, order_id, customer_id):
    return db.execute(
        """
        SELECT order_id, user_id AS customer_id, total_price, status
        FROM orders
        WHERE order_id = ? AND user_id = ?
        """,
        (order_id, customer_id),
    ).fetchone()


def get_payment_method(db, payment_method_id, customer_id):
    return db.execute(
        """
        SELECT payment_method_id
        FROM payment_methods
        WHERE payment_method_id = ? AND customer_id = ?
        """,
        (payment_method_id, customer_id),
    ).fetchone()


def get_payments_by_customer(db, customer_id):
    return db.execute(
        """
        SELECT p.payment_id, p.order_id, p.amount, p.payment_date,
               pm.payment_type, pm.details
        FROM payments p
        JOIN payment_methods pm ON p.payment_method_id = pm.payment_method_id
        WHERE p.customer_id = ?
        ORDER BY p.payment_date DESC
        """,
        (customer_id,),
    ).fetchall()


def get_all_payments(db):
    return db.execute(
        """
        SELECT p.payment_id, p.order_id, p.customer_id, p.amount, p.payment_date,
               pm.payment_type, u.full_name, u.staff_id
        FROM payments p
        JOIN payment_methods pm ON p.payment_method_id = pm.payment_method_id
        JOIN users u ON p.customer_id = u.user_id
        ORDER BY p.payment_date DESC
        """,
    ).fetchall()


def create_payment(db, order_id, payment_method_id, customer_id, amount):
    db.execute(
        """
        INSERT INTO payments (order_id, payment_method_id, customer_id, amount, payment_date)
        VALUES (?, ?, ?, ?, datetime('now'))
        """,
        (order_id, payment_method_id, customer_id, amount),
    )
    db.execute(
        "UPDATE orders SET status = 'Paid' WHERE order_id = ?",
        (order_id,),
    )
    db.commit()
