from services.device_service import sanitize_device_filters


# User Story 3:
# As a user I need search to easily browse devices by name or type.


def test_unit_search_filters_accept_partial_query_and_type_alias():
    """Unit: search filters accept q plus the legacy type alias."""
    filters, error = sanitize_device_filters({
        "q": "temp",
        "type": "sensor"
    })

    assert error is None
    assert filters["search"] == "temp"
    assert filters["category"] == "sensor"


def test_unit_search_filters_reject_invalid_type():
    """Unit: invalid device type filters are rejected before database access."""
    filters, error = sanitize_device_filters({
        "type": "invalid_type"
    })

    assert filters is None
    assert error == "Category must be a valid IoT device category."


def test_api_search_matches_partial_device_name(client, login_as_customer):
    """API: partial name searches return matching active devices."""
    login_as_customer(client)

    response = client.get("/api/devices?q=temp")
    body = response.get_json()

    assert response.status_code == 200
    assert len(body["devices"]) == 1
    assert body["devices"][0]["name"] == "Smart Temperature Sensor"


def test_api_search_matches_exact_device_name(client, login_as_customer):
    """API: exact name searches return the intended device."""
    login_as_customer(client)

    response = client.get("/api/devices?q=Industrial Vibration Monitor")
    body = response.get_json()

    assert response.status_code == 200
    assert len(body["devices"]) == 1
    assert body["devices"][0]["category"] == "industrial"


def test_api_search_filters_by_exact_type_alias(client, login_as_staff):
    """API: type alias filters by exact stored category."""
    login_as_staff(client)

    response = client.get("/api/devices?type=smart_home")
    body = response.get_json()

    assert response.status_code == 200
    assert len(body["devices"]) == 1
    assert body["devices"][0]["name"] == "Smart Home Hub"


def test_e2e_user_login_search_by_partial_then_by_type(
    client,
    login_as_customer
):
    """E2E: customer logs in and searches first by text, then by type."""
    login_response = login_as_customer(client)
    partial_response = client.get("/api/devices?q=vibration")
    type_response = client.get("/api/devices?category=industrial")

    partial_body = partial_response.get_json()
    type_body = type_response.get_json()

    assert login_response.status_code == 200
    assert partial_response.status_code == 200
    assert type_response.status_code == 200
    assert partial_body["devices"][0]["device_id"] == type_body["devices"][0]["device_id"]
