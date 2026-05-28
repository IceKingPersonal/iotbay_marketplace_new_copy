from flask import Blueprint, jsonify, request
from models.shipment_model import ShipmentModel
from utils.auth_helpers import login_required, get_current_user


shipment_routes = Blueprint("shipment_routes", __name__)


@shipment_routes.route("/", methods=["GET"])
@login_required
def list_shipments():
    current_user = get_current_user()

    if current_user["role"] == "staff":
        shipment_list = ShipmentModel.find_by_staff(current_user["user_id"])

    elif current_user["role"] == "customer":
        shipment_list = ShipmentModel.find_by_customer(current_user["user_id"])

    else:
        shipment_list = []

    return jsonify({
        "shipments": ShipmentModel.to_list(shipment_list)
    }), 200




@shipment_routes.route("/<int:shipment_id>", methods=["GET"])
@login_required
def get_shipment(shipment_id):
    current_user = get_current_user()

    target_shipment = ShipmentModel.find_by_id(shipment_id)

    if target_shipment is None:
        return jsonify({"error": "Shipment not found."}), 404


    # staff should only see shipments they are assigned to
    if current_user["role"] == "staff" and target_shipment["staff_user_id"] != current_user["user_id"]:
        return jsonify({"error": "You are not assigned to this shipment."}), 403


    # customers should only see shipments from their own orders
    if current_user["role"] == "customer":
        my_shipments = ShipmentModel.find_by_customer(current_user["user_id"])
        my_order_ids = [s["order_id"] for s in my_shipments]

        if target_shipment["order_id"] not in my_order_ids:
            return jsonify({"error": "You do not have access to this shipment."}), 403

    return jsonify({
        "shipment": ShipmentModel.to_dict(target_shipment)
    }), 200





@shipment_routes.route("/", methods=["POST"])
@login_required
def create_shipment():
    current_user = get_current_user()

    if current_user["role"] != "staff":
        return jsonify({"error": "Only staff can create shipments."}), 403

    incoming_data = request.get_json()

    order_id = incoming_data.get("order_id")
    delivery_address = incoming_data.get("delivery_address", "").strip()

    if not order_id:
        return jsonify({"error": "Order ID is required."}), 400

    if not delivery_address:
        return jsonify({"error": "Delivery address is required."}), 400

    if not ShipmentModel.order_is_paid(order_id):
        return jsonify({"error": "Shipment can only be created for a paid order."}), 400

    if ShipmentModel.shipment_exists_for_order(order_id):
        return jsonify({"error": "A shipment already exists for this order."}), 400

    recipient_name = ShipmentModel.get_customer_name_for_order(order_id)

    new_shipment_id = ShipmentModel.create(order_id, current_user["user_id"], recipient_name, delivery_address)

    new_shipment = ShipmentModel.find_by_id(new_shipment_id)

    return jsonify({
        "message": "Shipment created successfully.",
        "shipment": ShipmentModel.to_dict(new_shipment)
    }), 201





@shipment_routes.route("/<int:shipment_id>", methods=["PUT"])
@login_required
def update_shipment(shipment_id):
    current_user = get_current_user()

    target_shipment = ShipmentModel.find_by_id(shipment_id)

    if target_shipment is None:
        return jsonify({"error": "Shipment not found."}), 404

    if target_shipment["staff_user_id"] != current_user["user_id"]:
        return jsonify({"error": "Only the assigned staff can edit this shipment."}), 403

    incoming_data = request.get_json()

    new_status = incoming_data.get("status", "").strip()
    new_recipient = incoming_data.get("recipient_name", "").strip()
    new_address = incoming_data.get("delivery_address", "").strip()

    valid_statuses = ["pending", "shipped", "delivered"]

    if new_status not in valid_statuses:
        return jsonify({"error": "Status must be pending, shipped, or delivered."}), 400

    if not new_recipient or not new_address:
        return jsonify({"error": "Recipient name and delivery address are required."}), 400

    ShipmentModel.update(shipment_id, new_status, new_recipient, new_address)

    updated_shipment = ShipmentModel.find_by_id(shipment_id)

    return jsonify({
        "message": "Shipment updated successfully.",
        "shipment": ShipmentModel.to_dict(updated_shipment)
    }), 200
