from flask import Blueprint, jsonify, request

from models.order_model import OrderModel
from services import order_service
from utils.auth_helpers import get_current_user, login_required

order_routes = Blueprint("order_routes", __name__)


def _parse_search_args():
    order_id = None
    order_id_raw = request.args.get("order_id")
    if order_id_raw:
        try:
            order_id = int(order_id_raw)
        except ValueError:
            return None, None, (jsonify({"error": "order_id must be an integer"}), 400)

    date_prefix = request.args.get("date", "").strip() if isinstance(request.args.get("date"), str) else ""
    return order_id, date_prefix or None, None


@order_routes.route("", methods=["GET"])
@login_required
def list_orders():
    user = get_current_user()
    order_id, date_prefix, err = _parse_search_args()
    if err:
        return err

    if user["role"] == "staff":
        rows = OrderModel.list_all_customer_orders(order_id=order_id, date_prefix=date_prefix)
    else:
        rows = OrderModel.list_for_customer(user["user_id"], order_id=order_id, date_prefix=date_prefix)

    return jsonify({"orders": OrderModel.rows_to_list(rows)}), 200


@order_routes.route("", methods=["POST"])
@login_required
def create_order():
    user = get_current_user()
    if user["role"] != "customer":
        return jsonify({"error": "Only customer users can create orders"}), 403

    data = request.get_json()
    if data is None:
        return jsonify({"error": "Request body must be JSON."}), 400

    shipping_address = data.get("shipping_address", "").strip() if isinstance(data.get("shipping_address"), str) else ""
    currency_raw = data.get("currency")
    currency = currency_raw.strip().upper() if isinstance(currency_raw, str) else "AUD"
    items = data.get("items")

    if not shipping_address:
        return jsonify({"error": "shipping_address is required"}), 400
    if len(currency) != 3:
        return jsonify({"error": "currency must be a 3-letter code"}), 400

    payload, err, code = order_service.create_order(user["user_id"], shipping_address, currency, items)
    if err:
        return jsonify({"error": err}), code
    return jsonify(payload), code


@order_routes.route("/<int:order_id>", methods=["GET"])
@login_required
def get_order(order_id):
    user = get_current_user()
    if order_id < 1:
        return jsonify({"error": "Invalid order id"}), 400

    order = OrderModel.find_by_id(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    if user["role"] == "customer" and order["user_id"] != user["user_id"]:
        return jsonify({"error": "Order not found"}), 404

    if user["role"] == "staff":
        from database import get_db

        owner_row = get_db().execute(
            "SELECT role FROM users WHERE user_id = ?",
            (order["user_id"],),
        ).fetchone()
        if not owner_row or owner_row["role"] != "customer":
            return jsonify({"error": "Order not found"}), 404

    items = OrderModel.rows_to_list(OrderModel.find_items(order_id))
    return jsonify({"order": OrderModel.row_to_dict(order), "items": items}), 200


@order_routes.route("/<int:order_id>", methods=["PATCH"])
@login_required
def patch_order(order_id):
    user = get_current_user()
    if user["role"] != "customer":
        return jsonify({"error": "Only customer users can update orders"}), 403

    data = request.get_json()
    if data is None:
        return jsonify({"error": "Request body must be JSON."}), 400

    status = data.get("status", "").strip() if isinstance(data.get("status"), str) else ""
    payload, err, code = order_service.patch_order_status(user["user_id"], order_id, status)
    if err:
        return jsonify({"error": err}), code
    return jsonify(payload), code


@order_routes.route("/<int:order_id>", methods=["PUT"])
@login_required
def put_order(order_id):
    user = get_current_user()
    if user["role"] != "customer":
        return jsonify({"error": "Only customer users can update orders"}), 403

    data = request.get_json()
    if data is None:
        return jsonify({"error": "Request body must be JSON."}), 400

    shipping_address = data.get("shipping_address", "").strip() if isinstance(data.get("shipping_address"), str) else ""
    currency_raw = data.get("currency")
    currency = currency_raw.strip().upper() if isinstance(currency_raw, str) else "AUD"
    items = data.get("items")

    if not shipping_address:
        return jsonify({"error": "shipping_address is required"}), 400
    if len(currency) != 3:
        return jsonify({"error": "currency must be a 3-letter code"}), 400

    payload, err, code = order_service.update_saved_order(
        user["user_id"], order_id, shipping_address, currency, items
    )
    if err:
        return jsonify({"error": err}), code
    return jsonify(payload), code
