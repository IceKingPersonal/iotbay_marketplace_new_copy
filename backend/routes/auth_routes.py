from flask import Blueprint, request, jsonify, session
from services.auth_service import register_user, login_user
from models.user_model import UserModel
from models.access_log_model import AccessLogModel


auth_routes = Blueprint("auth_routes", __name__)

#List of the authenticate routes used and where they are used along with error/success messages.
@auth_routes.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if data is None:
        return jsonify({"error": "Request body must be JSON."}), 400

    user, error, status_code = register_user(data)

    if error:
        return jsonify({"error": error}), status_code

    return jsonify({
        "message": "Registration successful.",
        "user": user
    }), status_code


@auth_routes.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if data is None:
        return jsonify({"error": "Request body must be JSON."}), 400

    user, error, status_code = login_user(data)

    if error:
        return jsonify({"error": error}), status_code

    session["user_id"] = user["user_id"]

    log_id = AccessLogModel.create_login_log(user["user_id"])
    session["access_log_id"] = log_id

    return jsonify({
        "message": "Login successful.",
        "user": user
    }), status_code


@auth_routes.route("/logout", methods=["POST"])
def logout():
    log_id = session.get("access_log_id")

    if log_id:
        AccessLogModel.update_logout_time(log_id)

    session.clear()

    return jsonify({
        "message": "Logout successful."
    }), 200


@auth_routes.route("/me", methods=["GET"])
def get_current_user():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Not logged in."}), 401

    user = UserModel.find_by_id(user_id)

    if not user:
        session.clear()
        return jsonify({"error": "User not found."}), 404

    if user["status"] != "active":
        session.clear()
        return jsonify({"error": "Account is inactive."}), 403

    return jsonify({
        "user": UserModel.to_dict(user)
    }), 200