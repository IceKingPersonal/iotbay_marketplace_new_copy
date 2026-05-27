from db import get_db, row_to_dict, rows_to_dicts


def restore_order_stock(order_id: int) -> None:
    db = get_db()
    items = rows_to_dicts(
        db.execute(
            "SELECT product_id, quantity FROM order_items WHERE order_id = ?",
            (order_id,),
        ).fetchall()
    )
    for item in items:
        db.execute(
            "UPDATE products SET qty = qty + ? WHERE products_uid = ?",
            (item["quantity"], item["product_id"]),
        )


def create_order(
    user_id: int,
    shipping_address: str,
    currency: str,
    lines: list[dict],
) -> dict:
    """Create an order with line items and decrement product stock. Status is Saved."""
    db = get_db()
    for line in lines:
        if line["stock_qty"] < 1:
            raise ValueError(f"Product {line['product_id']} is out of stock")
        if line["stock_qty"] < line["quantity"]:
            raise ValueError(f"Insufficient stock for product {line['product_id']}")

    from ids import next_primary_key

    total_price = sum(line["quantity"] * line["unit_price"] for line in lines)
    orders_uid = next_primary_key("orders")

    db.execute("BEGIN")
    try:
        db.execute(
            """
            INSERT INTO orders (orders_uid, user_id, shipping_address, total_price, currency, status)
            VALUES (?, ?, ?, ?, ?, 'Saved')
            """,
            (orders_uid, user_id, shipping_address, total_price, currency),
        )
        for line in lines:
            ord_item_id = next_primary_key("order_items")
            db.execute(
                """
                INSERT INTO order_items (ord_item_id, order_id, product_id, quantity, unit_price)
                VALUES (?, ?, ?, ?, ?)
                """,
                (ord_item_id, orders_uid, line["product_id"], line["quantity"], line["unit_price"]),
            )
            db.execute(
                "UPDATE products SET qty = qty - ? WHERE products_uid = ?",
                (line["quantity"], line["product_id"]),
            )
        db.commit()
    except Exception:
        db.rollback()
        raise

    order = row_to_dict(db.execute("SELECT * FROM orders WHERE orders_uid = ?", (orders_uid,)).fetchone())
    if order is None:
        raise RuntimeError("Order was not created")
    return order
