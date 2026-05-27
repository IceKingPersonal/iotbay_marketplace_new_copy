from models.device_model import DeviceModel
from services.device_service import sanitize_device_ids


# User Story 5:
# As a staff member I need to delete outdated device records from the catalogue.


def test_unit_delete_ids_must_be_non_empty_list():
    """Unit: bulk delete input must include at least one device ID."""
    device_ids, error = sanitize_device_ids({"device_ids": []})

    assert device_ids is None
    assert error == "device_ids must be a non-empty list."


def test_unit_delete_ids_are_deduplicated():
    """Unit: repeated IDs are normalized before bulk archive work starts."""
    device_ids, error = sanitize_device_ids({"device_ids": [1, "1", 2]})

    assert error is None
    assert device_ids == [1, 2]


def test_unit_model_bulk_delete_archives_records(
    app,
    insert_device,
    get_device
):
    """Unit: the model archives selected records instead of hard deleting."""
    first_device_id = insert_device(name="Unit Delete One", model="UNIT-DEL-1")
    second_device_id = insert_device(name="Unit Delete Two", model="UNIT-DEL-2")

    with app.app_context():
        archived_ids = DeviceModel.delete_devices(
            [first_device_id, second_device_id],
            2
        )

    assert archived_ids == [first_device_id, second_device_id]
    assert get_device(first_device_id)["status"] == "archived"
    assert get_device(second_device_id)["status"] == "archived"


def test_api_staff_can_archive_single_device(
    client,
    login_as_staff,
    insert_device,
    get_device
):
    """API: staff can archive one device record."""
    device_id = insert_device(name="API Single Delete", model="API-DEL-1")

    login_as_staff(client)
    response = client.delete(f"/api/devices/{device_id}")

    assert response.status_code == 200
    assert get_device(device_id)["status"] == "archived"


def test_api_staff_can_archive_multiple_devices(
    client,
    login_as_staff,
    insert_device,
    get_device
):
    """API: staff can archive multiple records in one request."""
    first_device_id = insert_device(name="API Bulk Delete One", model="API-DEL-2")
    second_device_id = insert_device(name="API Bulk Delete Two", model="API-DEL-3")

    login_as_staff(client)
    response = client.delete("/api/devices", json={
        "device_ids": [first_device_id, second_device_id]
    })

    assert response.status_code == 200
    assert get_device(first_device_id)["status"] == "archived"
    assert get_device(second_device_id)["status"] == "archived"


def test_api_customer_cannot_archive_device(
    client,
    login_as_customer,
    insert_device
):
    """API: customers cannot delete or archive catalogue records."""
    device_id = insert_device(name="Customer Delete Attempt", model="CUST-DEL-1")

    login_as_customer(client)
    response = client.delete(f"/api/devices/{device_id}")

    assert response.status_code == 403


def test_e2e_staff_login_archive_then_catalogue_hides_device(
    client,
    login_as_staff,
    insert_device
):
    """E2E: staff archives a record and it disappears from browse results."""
    device_id = insert_device(name="E2E Archive Target", model="E2E-DEL-1")

    login_response = login_as_staff(client)
    delete_response = client.delete(f"/api/devices/{device_id}")
    browse_response = client.get("/api/devices?q=E2E Archive Target")
    browse_body = browse_response.get_json()

    assert login_response.status_code == 200
    assert delete_response.status_code == 200
    assert browse_response.status_code == 200
    assert browse_body["devices"] == []
