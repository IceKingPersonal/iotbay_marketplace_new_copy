from db import get_db

PK_COLUMNS = {
    "users": "user_uid",
    "carts": "carts_id",
    "cart_items": "cart_items_id",
    "orders": "orders_uid",
    "order_items": "ord_item_id",
    "logs": "logs_uid",
}


def next_primary_key(table: str) -> int:
    col = PK_COLUMNS[table]
    row = get_db().execute(f"SELECT COALESCE(MAX({col}), 0) + 1 AS n FROM {table}").fetchone()
    return row["n"]
