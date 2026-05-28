from functools import wraps
from flask import jsonify, request, session
from . import payments_bp
from . import dal
from .models import Payment
from database import get_db
from utils.auth_helpers import login_required, get_current_user


def customer_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user or user["role"] != "customer":
            return jsonify({"error": "This endpoint is for customers only."}), 403
        return f(*args, **kwargs)
    return decorated


@payments_bp.route("/create", methods=["GET"])
@login_required
@customer_required
def get_payment_form():
    db = get_db()
    customer_id = session["user_id"]
    orders = [dict(row) for row in dal.get_saved_orders(db, customer_id)]
    payment_methods = [dict(row) for row in dal.get_payment_methods(db, customer_id)]
    return jsonify({"orders": orders, "payment_methods": payment_methods}), 200


@payments_bp.route("/create", methods=["POST"])
@login_required
@customer_required
def create_payment():
    db = get_db()
    customer_id = session["user_id"]
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON."}), 400

    order_id = data.get("order_id")
    payment_method_id = data.get("payment_method_id")

    if not order_id or not payment_method_id:
        return jsonify({"error": "Order ID and payment method ID are required."}), 400

    order = dal.get_order(db, order_id, customer_id)
    if not order:
        return jsonify({"error": "Order not found or does not belong to you."}), 404

    payment_method = dal.get_payment_method(db, payment_method_id, customer_id)
    if not payment_method:
        return jsonify({"error": "Payment method not found or does not belong to you."}), 404

    if not Payment.validate_order_status(order["status"]):
        return jsonify({"error": "Only orders with status 'Saved' can be paid."}), 400

    if not Payment.validate_amount(order["total_price"]):
        return jsonify({"error": "Order has an invalid amount."}), 400

    try:
        dal.create_payment(db, order_id, payment_method_id, customer_id, order["total_price"])
        return jsonify({"message": "Payment successful!"}), 201
    except Exception:
        return jsonify({"error": "Payment could not be processed. Please try again."}), 500


@payments_bp.route("/history", methods=["GET"])
@login_required
def payment_history():
    db = get_db()
    user = get_current_user()
    role = user["role"]

    if role == "staff":
        payments = [dict(row) for row in dal.get_all_payments(db)]
        return jsonify({"payments": payments, "role": "staff"}), 200

    payments = [dict(row) for row in dal.get_payments_by_customer(db, session["user_id"])]
    return jsonify({"payments": payments, "role": "customer"}), 200
