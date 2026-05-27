from flask import Blueprint, request, jsonify
from services.device_service import (
    bulk_delete_devices,
    create_device,
    delete_device,
    get_device,
    get_device_audit_logs,
    list_devices,
    update_device
)
from utils.auth_helpers import login_required, get_current_user


device_routes = Blueprint("device_routes", __name__)


@device_routes.route("", methods=["GET"])
@device_routes.route("/", methods=["GET"])
@login_required
def view_devices():
    devices, error, status_code = list_devices(request.args)

    if error:
        return jsonify({"error": error}), status_code

    return jsonify({
        "devices": devices
    }), status_code


@device_routes.route("/search", methods=["GET"])
@login_required
def search_devices():
    devices, error, status_code = list_devices(request.args)

    if error:
        return jsonify({"error": error}), status_code

    return jsonify({
        "devices": devices
    }), status_code


@device_routes.route("/<int:device_id>", methods=["GET"])
@login_required
def view_device(device_id):
    device, error, status_code = get_device(device_id)

    if error:
        return jsonify({"error": error}), status_code

    return jsonify({
        "device": device
    }), status_code


@device_routes.route("", methods=["POST"])
@device_routes.route("/", methods=["POST"])
@login_required
def add_device():
    data = request.get_json()

    if data is None:
        return jsonify({"error": "Request body must be JSON."}), 400

    user = get_current_user()
    device, error, status_code = create_device(data, user)

    if error:
        return jsonify({"error": error}), status_code

    return jsonify({
        "message": "Device created successfully.",
        "device": device
    }), status_code


@device_routes.route("", methods=["DELETE"])
@device_routes.route("/", methods=["DELETE"])
@login_required
def remove_devices():
    data = request.get_json()

    if data is None:
        return jsonify({"error": "Request body must be JSON."}), 400

    user = get_current_user()
    result, error, status_code = bulk_delete_devices(data, user)

    if error:
        return jsonify({"error": error}), status_code

    return jsonify({
        "message": "Devices archived successfully.",
        "devices": result
    }), status_code


@device_routes.route("/<int:device_id>", methods=["PUT"])
@login_required
def edit_device(device_id):
    data = request.get_json()

    if data is None:
        return jsonify({"error": "Request body must be JSON."}), 400

    user = get_current_user()
    device, error, status_code = update_device(device_id, data, user)

    if error:
        return jsonify({"error": error}), status_code

    return jsonify({
        "message": "Device updated successfully.",
        "device": device
    }), status_code


@device_routes.route("/<int:device_id>", methods=["DELETE"])
@login_required
def remove_device(device_id):
    user = get_current_user()
    device, error, status_code = delete_device(device_id, user)

    if error:
        return jsonify({"error": error}), status_code

    return jsonify({
        "message": "Device archived successfully.",
        "device": device
    }), status_code


@device_routes.route("/<int:device_id>/audit", methods=["GET"])
@login_required
def view_device_audit_logs(device_id):
    user = get_current_user()
    logs, error, status_code = get_device_audit_logs(device_id, user)

    if error:
        return jsonify({"error": error}), status_code

    return jsonify({
        "logs": logs
    }), status_code
