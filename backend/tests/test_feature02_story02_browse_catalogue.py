from init_db import SAMPLE_DEVICES
from models.device_model import DeviceModel
from utils.validators import DEVICE_CATEGORIES, DEVICE_CONDITIONS, DEVICE_STATUSES


# User Story 2:
# As a user of the system I want the ability to browse available devices.


def test_unit_seed_devices_cover_all_catalogue_enums(query_all):
    """Unit: seeded devices cover every category, condition, and status enum."""
    rows = query_all("""
        SELECT type AS category, condition, status
        FROM products
    """)

    categories = {row["category"] for row in rows}
    conditions = {row["condition"] for row in rows}
    statuses = {row["status"] for row in rows}

    assert categories == set(DEVICE_CATEGORIES)
    assert conditions == set(DEVICE_CONDITIONS)
    assert statuses == set(DEVICE_STATUSES)
    assert len(rows) == len(SAMPLE_DEVICES) + 3


def test_unit_model_list_devices_returns_only_active_records(app):
    """Unit: catalogue queries hide inactive and archived device records."""
    with app.app_context():
        devices = DeviceModel.list_devices({})

    assert len(devices) > 0
    assert all(device["status"] == "active" for device in devices)


def test_api_customer_can_browse_active_device_catalogue(
    client,
    login_as_customer
):
    """API: a logged-in customer can view active catalogue devices."""
    login_as_customer(client)

    response = client.get("/api/devices")
    body = response.get_json()

    assert response.status_code == 200
    assert len(body["devices"]) == 11
    assert all(device["status"] == "active" for device in body["devices"])
    assert {"name", "category", "price", "stock_quantity"}.issubset(
        body["devices"][0].keys()
    )


def test_api_staff_can_browse_active_device_catalogue(client, login_as_staff):
    """API: a logged-in staff user can view the same active catalogue."""
    login_as_staff(client)

    response = client.get("/api/devices")
    body = response.get_json()

    assert response.status_code == 200
    assert len(body["devices"]) == 11
    assert all(device["status"] == "active" for device in body["devices"])


def test_api_catalogue_requires_login(client):
    """API: unauthenticated catalogue browsing is rejected."""
    response = client.get("/api/devices")

    assert response.status_code == 401


def test_e2e_customer_login_then_browse_seed_catalogue(
    client,
    login_as_customer
):
    """E2E: customer logs in and sees active seed devices, not archived ones."""
    login_response = login_as_customer(client)
    browse_response = client.get("/api/devices")
    body = browse_response.get_json()
    device_names = {device["name"] for device in body["devices"]}

    assert login_response.status_code == 200
    assert browse_response.status_code == 200
    assert "Smart Temperature Sensor" in device_names
    assert "Outdoor Security Camera" not in device_names
