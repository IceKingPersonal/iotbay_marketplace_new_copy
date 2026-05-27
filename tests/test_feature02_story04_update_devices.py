from models.device_model import DeviceModel
from services.device_service import sanitize_device_data


# User Story 4:
# As a staff member I want to update device details so the catalogue is accurate.


def test_unit_update_rejects_invalid_price(insert_device, get_device):
    """Unit: update validation rejects invalid numeric input."""
    device_id = insert_device()
    existing_device = get_device(device_id)

    sanitized_data, error = sanitize_device_data(
        {"price": -1},
        existing_device
    )

    assert sanitized_data is None
    assert error == "Price cannot be negative."


def test_unit_model_update_changes_record_and_writes_audit_log(
    app,
    insert_device,
    valid_device_payload,
    query_one
):
    """Unit: model update persists changed fields and records an audit entry."""
    device_id = insert_device()
    data = valid_device_payload.copy()
    data["name"] = "Unit Updated Sensor"
    data["price"] = 66.25
    data["stock_quantity"] = 7

    with app.app_context():
        DeviceModel.update_device(device_id, data, 2)

    device = query_one("""
        SELECT *
        FROM devices
        WHERE device_id = ?
    """, (device_id,))
    audit_log = query_one("""
        SELECT *
        FROM device_audit_logs
        WHERE device_id = ?
          AND action = 'updated'
    """, (device_id,))

    assert device["name"] == "Unit Updated Sensor"
    assert device["price"] == 66.25
    assert device["stock_quantity"] == 7
    assert audit_log["staff_user_id"] == 2


def test_api_staff_can_update_device(
    client,
    login_as_staff,
    insert_device,
    valid_device_payload
):
    """API: staff can update an existing device record."""
    device_id = insert_device()
    data = valid_device_payload.copy()
    data["name"] = "API Updated Sensor"
    data["stock_quantity"] = 22

    login_as_staff(client)
    response = client.put(f"/api/devices/{device_id}", json=data)
    body = response.get_json()

    assert response.status_code == 200
    assert body["device"]["name"] == "API Updated Sensor"
    assert body["device"]["stock_quantity"] == 22


def test_api_customer_cannot_update_device(
    client,
    login_as_customer,
    insert_device,
    valid_device_payload
):
    """API: customers cannot update device catalogue records."""
    device_id = insert_device()

    login_as_customer(client)
    response = client.put(f"/api/devices/{device_id}", json=valid_device_payload)

    assert response.status_code == 403


def test_api_update_missing_device_returns_not_found(
    client,
    login_as_staff,
    valid_device_payload
):
    """API: updating a non-existent device returns 404."""
    login_as_staff(client)

    response = client.put("/api/devices/9999", json=valid_device_payload)

    assert response.status_code == 404


def test_e2e_staff_login_create_update_then_view_device(
    client,
    login_as_staff,
    valid_device_payload
):
    """E2E: staff creates a record, updates it, then reads changed details."""
    create_payload = valid_device_payload.copy()
    create_payload["name"] = "E2E Update Target"
    create_payload["model"] = "E2E-UPDATE-001"

    update_payload = create_payload.copy()
    update_payload["name"] = "E2E Updated Device"
    update_payload["price"] = 77.77

    login_response = login_as_staff(client)
    create_response = client.post("/api/devices", json=create_payload)
    device_id = create_response.get_json()["device"]["device_id"]
    update_response = client.put(f"/api/devices/{device_id}", json=update_payload)
    view_response = client.get(f"/api/devices/{device_id}")
    view_body = view_response.get_json()

    assert login_response.status_code == 200
    assert create_response.status_code == 201
    assert update_response.status_code == 200
    assert view_response.status_code == 200
    assert view_body["device"]["name"] == "E2E Updated Device"
    assert view_body["device"]["price"] == 77.77
