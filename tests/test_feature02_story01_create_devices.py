from models.device_model import DeviceModel
from services.device_service import create_device, sanitize_device_data


# User Story 1:
# As a staff user I want to create IoT device records for the catalogue.


def test_unit_create_sanitizes_required_fields_and_type_alias(valid_device_payload):
    """Unit: type is accepted as an alias and text input is stripped."""
    data = valid_device_payload.copy()
    data["name"] = "  Trimmed Sensor  "
    data["type"] = data.pop("category")

    sanitized_data, error = sanitize_device_data(data)

    assert error is None
    assert sanitized_data["name"] == "Trimmed Sensor"
    assert sanitized_data["category"] == "sensor"
    assert sanitized_data["price"] == 55.75
    assert sanitized_data["stock_quantity"] == 11


def test_unit_create_rejects_missing_device_name(valid_device_payload):
    """Unit: a required device name must be present before saving."""
    data = valid_device_payload.copy()
    data["name"] = ""

    sanitized_data, error = sanitize_device_data(data)

    assert sanitized_data is None
    assert error == "Device name is required."


def test_unit_model_create_persists_staff_creator_and_audit_log(
    app,
    valid_device_payload,
    query_one
):
    """Unit: the model stores creator/updater IDs and writes an audit log."""
    with app.app_context():
        device_id = DeviceModel.create_device(valid_device_payload, 2)

    device = query_one("""
        SELECT *
        FROM devices
        WHERE device_id = ?
    """, (device_id,))
    audit_log = query_one("""
        SELECT *
        FROM device_audit_logs
        WHERE device_id = ?
          AND action = 'created'
    """, (device_id,))

    assert device["created_by"] == 2
    assert device["updated_by"] == 2
    assert audit_log["staff_user_id"] == 2


def test_api_staff_can_create_device(client, login_as_staff, valid_device_payload):
    """API: a logged-in staff user can create a valid device record."""
    login_as_staff(client)

    response = client.post("/api/devices", json=valid_device_payload)
    body = response.get_json()

    assert response.status_code == 201
    assert body["device"]["name"] == "Deterministic Test Sensor"
    assert body["device"]["category"] == "sensor"
    assert body["device"]["created_by"] == 2


def test_api_customer_cannot_create_device(
    client,
    login_as_customer,
    valid_device_payload
):
    """API: customers are forbidden from creating catalogue records."""
    login_as_customer(client)

    response = client.post("/api/devices", json=valid_device_payload)

    assert response.status_code == 403


def test_e2e_staff_login_create_then_browse_created_device(
    client,
    login_as_staff,
    valid_device_payload
):
    """E2E: staff logs in, creates a device, then finds it in the catalogue."""
    payload = valid_device_payload.copy()
    payload["name"] = "E2E Created Controller"
    payload["category"] = "controller"
    payload["model"] = "E2E-CREATE-001"

    login_response = login_as_staff(client)
    create_response = client.post("/api/devices", json=payload)
    browse_response = client.get("/api/devices?q=E2E Created Controller")
    browse_body = browse_response.get_json()

    assert login_response.status_code == 200
    assert create_response.status_code == 201
    assert browse_response.status_code == 200
    assert len(browse_body["devices"]) == 1
    assert browse_body["devices"][0]["name"] == "E2E Created Controller"
