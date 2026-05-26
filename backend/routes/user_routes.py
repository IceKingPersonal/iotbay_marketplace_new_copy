from flask import Blueprint, request, jsonify, session
from models.user_model import UserModel
from utils.auth_helpers import login_required, get_current_user
from utils.validators import is_valid_email


user_routes = Blueprint("user_routes", __name__)

#List of the user routes used and where they are used along with error/success messages.
@user_routes.route("/me", methods=["GET"])
@login_required
def view_profile():
    user = get_current_user()

    return jsonify({
        "user": UserModel.to_dict(user)
    }), 200


@user_routes.route("/me", methods=["PUT"])
@login_required
def update_profile():
    user = get_current_user()
    data = request.get_json()

    if data is None:
        return jsonify({"error": "Request body must be JSON."}), 400

    full_name = data.get("full_name")
    email = data.get("email")

    if not full_name:
        return jsonify({"error": "Full name is required."}), 400

    if not is_valid_email(email):
        return jsonify({"error": "Email must be in a valid format, such as name@example.com."}), 400

    existing_user = UserModel.find_by_email(email)

    if existing_user and existing_user["user_id"] != user["user_id"]:
        return jsonify({"error": "Email is already registered."}), 409

    if user["role"] == "customer":
        if not data.get("phone"):
            return jsonify({"error": "Phone number is required for customers."}), 400

        if not data.get("address"):
            return jsonify({"error": "Address is required for customers."}), 400

    if user["role"] == "staff":
        if not data.get("position"):
            return jsonify({"error": "Position is required for staff."}), 400

    UserModel.update_user(user["user_id"], data)

    updated_user = UserModel.find_by_id(user["user_id"])

    return jsonify({
        "message": "Profile updated successfully.",
        "user": UserModel.to_dict(updated_user)
    }), 200


@user_routes.route("/me/cancel", methods=["PUT"])
@login_required
def cancel_profile():
    user = get_current_user()

    UserModel.cancel_user(user["user_id"])

    session.clear()

    return jsonify({
        "message": "Account cancelled successfully."
    }), 200