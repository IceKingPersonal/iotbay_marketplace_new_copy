from database import get_db
from models.order_model import OrderModel, ORDER_STATUSES


def _normalize_items(raw_items):
    if not isinstance(raw_items, list) or len(raw_items) == 0:
        return None, "items must be a non-empty array"

    lines = []
    for entry in raw_items:
        try:
            product_id = int(entry.get("product_id"))
            quantity = int(entry.get("quantity"))
        except (TypeError, ValueError, AttributeError):
            return None, "Each item needs product_id and quantity as positive integers"
        if product_id < 1 or quantity < 1:
            return None, "Each item needs product_id and quantity as positive integers"
        lines.append({"product_id": product_id, "quantity": quantity})

    return lines, None


def _resolve_lines_with_stock(lines):
    resolved = []
    for line in lines:
        product = OrderModel.get_product(line["product_id"])
        if not product:
            return None, f"Product {line['product_id']} not found"
        stock = product["stock_qty"]
        if stock < 1:
            return None, f"Product {line['product_id']} is out of stock"
        if stock < line["quantity"]:
            return None, f"Insufficient stock for product {line['product_id']}"
        resolved.append(
            {
                "product_id": line["product_id"],
                "quantity": line["quantity"],
                "unit_price": product["price"],
            }
        )
    return resolved, None


def _order_payload(order_id):
    order = OrderModel.row_to_dict(OrderModel.find_by_id(order_id))
    items = OrderModel.rows_to_list(OrderModel.find_items(order_id))
    return {"order": order, "items": items}


def restore_order_stock(order_id):
    for row in OrderModel.find_items(order_id):
        OrderModel.adjust_stock(row["product_id"], row["quantity"])


def create_order(user_id, shipping_address, currency, raw_items):
    lines, err = _normalize_items(raw_items)
    if err:
        return None, err, 400

    resolved, err = _resolve_lines_with_stock(lines)
    if err:
        return None, err, 409

    total_price = sum(line["quantity"] * line["unit_price"] for line in resolved)
    db = get_db()
    db.execute("BEGIN")
    try:
        order_id = OrderModel.create_order(user_id, shipping_address, currency, total_price)
        for line in resolved:
            OrderModel.insert_item(order_id, line["product_id"], line["quantity"], line["unit_price"])
            OrderModel.adjust_stock(line["product_id"], -line["quantity"])
        db.commit()
    except Exception as exc:
        db.rollback()
        return None, str(exc), 500

    return _order_payload(order_id), None, 201


def update_saved_order(user_id, order_id, shipping_address, currency, raw_items):
    order = OrderModel.find_by_id(order_id)
    if not order:
        return None, "Order not found", 404
    if order["user_id"] != user_id:
        return None, "Order not found", 404
    if order["status"] != "Saved":
        return None, "Only saved orders can be updated before they are paid", 409

    lines, err = _normalize_items(raw_items)
    if err:
        return None, err, 400

    resolved, err = _resolve_lines_with_stock(lines)
    if err:
        return None, err, 409

    total_price = sum(line["quantity"] * line["unit_price"] for line in resolved)
    db = get_db()
    db.execute("BEGIN")
    try:
        restore_order_stock(order_id)
        OrderModel.delete_items(order_id)
        for line in resolved:
            OrderModel.insert_item(order_id, line["product_id"], line["quantity"], line["unit_price"])
            OrderModel.adjust_stock(line["product_id"], -line["quantity"])
        OrderModel.update_order_fields(order_id, shipping_address, total_price, currency, "Saved")
        db.commit()
    except Exception as exc:
        db.rollback()
        return None, str(exc), 500

    return _order_payload(order_id), None, 200


def patch_order_status(user_id, order_id, status):
    if status not in ORDER_STATUSES:
        return None, f"status must be one of: {', '.join(ORDER_STATUSES)}", 400

    order = OrderModel.find_by_id(order_id)
    if not order:
        return None, "Order not found", 404
    if order["user_id"] != user_id:
        return None, "Order not found", 404
    if order["status"] != "Saved":
        return None, "Only saved orders can be updated before they are paid", 409

    if status not in ("Paid", "Cancelled"):
        return None, "Customers can only mark saved orders as Paid or Cancelled", 400

    db = get_db()
    db.execute("BEGIN")
    try:
        OrderModel.update_status(order_id, status)
        if status == "Cancelled":
            restore_order_stock(order_id)
        db.commit()
    except Exception as exc:
        db.rollback()
        return None, str(exc), 500

    order_dict = OrderModel.row_to_dict(OrderModel.find_by_id(order_id))
    return {"order": order_dict}, None, 200
