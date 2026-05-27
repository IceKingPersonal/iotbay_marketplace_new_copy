from flask import Blueprint, g, jsonify, request

from db import get_db, row_to_dict, rows_to_dicts
from ids import next_primary_key
from lib.orders import create_order
from middleware.require_user_id import require_user_id

bp = Blueprint("cart", __name__)


@bp.before_request
def _auth():
    res = require_user_id()
    if res is not None:
        return res

    user_id = g.user_id
    # Only customer users can place orders.
    is_customer = get_db().execute("SELECT 1 FROM customer WHERE user_uid = ?", (user_id,)).fetchone() is not None
    if not is_customer:
        return jsonify({"error": "Only customer users can access cart / place orders"}), 403
    return None


def get_open_cart_id(user_id: int) -> int | None:
    row = get_db().execute(
        """
        SELECT carts_id FROM carts
        WHERE user_id = ? AND status = 'open'
        ORDER BY carts_id DESC
        LIMIT 1
        """,
        (user_id,),
    ).fetchone()
    return row["carts_id"] if row else None


def ensure_open_cart(user_id: int) -> int:
    existing = get_open_cart_id(user_id)
    if existing:
        return existing
    carts_id = next_primary_key("carts")
    get_db().execute(
        """
        INSERT INTO carts (carts_id, user_id, session_id, status)
        VALUES (?, ?, NULL, 'open')
        """,
        (carts_id, user_id),
    )
    get_db().commit()
    return carts_id


@bp.get("", strict_slashes=False)
def get_cart():
    user_id = g.user_id
    cart_id = get_open_cart_id(user_id)
    if not cart_id:
        return jsonify({"cart": None, "items": []})
    db = get_db()
    cart = row_to_dict(db.execute("SELECT * FROM carts WHERE carts_id = ?", (cart_id,)).fetchone())
    items = rows_to_dicts(
        db.execute(
            """
            SELECT
              ci.cart_items_id AS cart_item_id,
              ci.cart_id,
              ci.product_id,
              ci.quantity,
              ci.unit_price,
              ci.currency,
              p.device_name,
              p.manufacturer,
              p.type,
              p.qty AS stock_qty
            FROM cart_items ci
            JOIN products p ON p.products_uid = ci.product_id
            WHERE ci.cart_id = ?
            ORDER BY ci.cart_items_id
            """,
            (cart_id,),
        ).fetchall()
    )
    return jsonify({"cart": cart, "items": items})


@bp.post("/items")
def add_item():
    user_id = g.user_id
    body = request.get_json(silent=True) or {}
    try:
        product_id = int(body.get("product_id"))
        quantity = int(body.get("quantity"))
    except (TypeError, ValueError):
        return jsonify({"error": "product_id and positive integer quantity are required"}), 400
    if product_id < 1 or quantity < 1:
        return jsonify({"error": "product_id and positive integer quantity are required"}), 400

    db = get_db()
    product = row_to_dict(
        db.execute("SELECT products_uid, price, qty FROM products WHERE products_uid = ?", (product_id,)).fetchone()
    )
    if not product:
        return jsonify({"error": "Product not found"}), 404
    if product["qty"] < 1:
        return jsonify({"error": "Out of stock", "stock": 0}), 409
    if product["qty"] < quantity:
        return jsonify({"error": "Insufficient stock", "stock": product["qty"]}), 409

    cart_id = ensure_open_cart(user_id)
    existing = row_to_dict(
        db.execute(
            "SELECT cart_items_id, quantity FROM cart_items WHERE cart_id = ? AND product_id = ?",
            (cart_id, product_id),
        ).fetchone()
    )

    if existing:
        new_qty = existing["quantity"] + quantity
        if product["qty"] < new_qty:
            return jsonify({"error": "Insufficient stock", "stock": product["qty"]}), 409
        db.execute(
            "UPDATE cart_items SET quantity = ?, updated_at = datetime('now') WHERE cart_items_id = ?",
            (new_qty, existing["cart_items_id"]),
        )
        db.commit()
        line = row_to_dict(
            db.execute("SELECT * FROM cart_items WHERE cart_items_id = ?", (existing["cart_items_id"],)).fetchone()
        )
        return jsonify({"item": line, "merged": True})

    cart_items_id = next_primary_key("cart_items")
    db.execute(
        """
        INSERT INTO cart_items (cart_items_id, cart_id, product_id, quantity, unit_price, currency)
        VALUES (?, ?, ?, ?, ?, 'AUD')
        """,
        (cart_items_id, cart_id, product_id, quantity, product["price"]),
    )
    db.execute("UPDATE carts SET updated_at = datetime('now') WHERE carts_id = ?", (cart_id,))
    db.commit()
    item = row_to_dict(db.execute("SELECT * FROM cart_items WHERE cart_items_id = ?", (cart_items_id,)).fetchone())
    return jsonify({"item": item, "merged": False}), 201


@bp.patch("/items/<int:cart_item_id>")
def update_item(cart_item_id: int):
    user_id = g.user_id
    body = request.get_json(silent=True) or {}
    try:
        qty = int(body.get("quantity"))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid cart item id or quantity"}), 400
    if cart_item_id < 1 or qty < 1:
        return jsonify({"error": "Invalid cart item id or quantity"}), 400

    db = get_db()
    line = row_to_dict(
        db.execute(
            """
            SELECT ci.*, c.user_id
            FROM cart_items ci
            JOIN carts c ON c.carts_id = ci.cart_id
            WHERE ci.cart_items_id = ?
            """,
            (cart_item_id,),
        ).fetchone()
    )
    if not line or line["user_id"] != user_id:
        return jsonify({"error": "Cart item not found"}), 404

    product = row_to_dict(db.execute("SELECT qty FROM products WHERE products_uid = ?", (line["product_id"],)).fetchone())
    if not product or product["qty"] < 1:
        return jsonify({"error": "Out of stock", "stock": 0}), 409
    if product["qty"] < qty:
        return jsonify({"error": "Insufficient stock", "stock": product["qty"] if product else 0}), 409

    db.execute(
        "UPDATE cart_items SET quantity = ?, updated_at = datetime('now') WHERE cart_items_id = ?",
        (qty, cart_item_id),
    )
    db.commit()
    item = row_to_dict(db.execute("SELECT * FROM cart_items WHERE cart_items_id = ?", (cart_item_id,)).fetchone())
    return jsonify({"item": item})


@bp.delete("/items/<int:cart_item_id>")
def delete_item(cart_item_id: int):
    user_id = g.user_id
    if cart_item_id < 1:
        return jsonify({"error": "Invalid cart item id"}), 400

    db = get_db()
    line = row_to_dict(
        db.execute(
            """
            SELECT ci.cart_items_id, c.user_id, ci.cart_id
            FROM cart_items ci
            JOIN carts c ON c.carts_id = ci.cart_id
            WHERE ci.cart_items_id = ?
            """,
            (cart_item_id,),
        ).fetchone()
    )
    if not line or line["user_id"] != user_id:
        return jsonify({"error": "Cart item not found"}), 404

    db.execute("DELETE FROM cart_items WHERE cart_items_id = ?", (cart_item_id,))
    db.execute("UPDATE carts SET updated_at = datetime('now') WHERE carts_id = ?", (line["cart_id"],))
    db.commit()
    return "", 204


@bp.post("/checkout")
def checkout():
    user_id = g.user_id
    body = request.get_json(silent=True) or {}
    shipping_address = body.get("shipping_address", "").strip() if isinstance(body.get("shipping_address"), str) else ""
    currency_raw = body.get("currency")
    currency = currency_raw.strip().upper() if isinstance(currency_raw, str) else "AUD"

    if not shipping_address:
        return jsonify({"error": "shipping_address is required"}), 400
    if len(currency) != 3:
        return jsonify({"error": "currency must be a 3-letter code"}), 400

    cart_id = get_open_cart_id(user_id)
    if not cart_id:
        return jsonify({"error": "No open cart"}), 400

    db = get_db()
    lines = rows_to_dicts(
        db.execute(
            """
            SELECT ci.*, p.qty AS stock_qty
            FROM cart_items ci
            JOIN products p ON p.products_uid = ci.product_id
            WHERE ci.cart_id = ?
            """,
            (cart_id,),
        ).fetchall()
    )

    if not lines:
        return jsonify({"error": "Cart is empty"}), 400

    for line in lines:
        if line["stock_qty"] < 1:
            return jsonify({"error": "Out of stock", "product_id": line["product_id"], "stock": 0}), 409
        if line["stock_qty"] < line["quantity"]:
            return jsonify({"error": "Insufficient stock for checkout", "product_id": line["product_id"]}), 409

    try:
        order = create_order(user_id, shipping_address, currency, lines)
    except ValueError as e:
        return jsonify({"error": str(e)}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    db.execute(
        "UPDATE carts SET status = 'checked_out', updated_at = datetime('now') WHERE carts_id = ?",
        (cart_id,),
    )
    db.commit()

    items = rows_to_dicts(
        db.execute(
            """
            SELECT oi.*, p.device_name, p.manufacturer, p.type
            FROM order_items oi
            LEFT JOIN products p ON p.products_uid = oi.product_id
            WHERE oi.order_id = ?
            ORDER BY oi.ord_item_id
            """,
            (order["orders_uid"],),
        ).fetchall()
    )
    return jsonify({"order": order, "items": items}), 201


@bp.patch("/<int:cart_id>")
def update_cart(cart_id: int):
    user_id = g.user_id
    db = get_db()
    row = row_to_dict(
        db.execute("SELECT carts_id FROM carts WHERE carts_id = ? AND user_id = ?", (cart_id, user_id)).fetchone()
    )
    if not row:
        return jsonify({"error": "Cart not found"}), 404

    body = request.get_json(silent=True) or {}
    status = body.get("status", "").strip() if isinstance(body.get("status"), str) else ""
    allowed = ["open", "checked_out", "abandoned"]
    if not status or status not in allowed:
        return jsonify({"error": f"status must be one of: {', '.join(allowed)}"}), 400

    db.execute(
        "UPDATE carts SET status = ?, updated_at = datetime('now') WHERE carts_id = ?",
        (status, cart_id),
    )
    db.commit()
    cart = row_to_dict(db.execute("SELECT * FROM carts WHERE carts_id = ?", (cart_id,)).fetchone())
    return jsonify({"cart": cart})
