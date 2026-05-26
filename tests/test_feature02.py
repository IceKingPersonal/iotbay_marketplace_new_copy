import os
import sqlite3

import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from utils.validators import validate_device_data


TEST_DATABASE = "test_feature02_iotbay.db"


@pytest.fixture
def app():
    if os.path.exists(TEST_DATABASE):
        os.remove(TEST_DATABASE)

    app = create_app()

    app.config.update({
        "TESTING": True,
        "DATABASE": TEST_DATABASE,
        "SECRET_KEY": "test-secret-key"
    })

    with app.app_context():
        connection = sqlite3.connect(TEST_DATABASE)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,

                role TEXT NOT NULL CHECK(role IN ('customer', 'staff')),

                full_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,

                phone TEXT,
                address TEXT,

                staff_id TEXT UNIQUE,
                position TEXT,

                status TEXT NOT NULL DEFAULT 'active'
                    CHECK(status IN ('active', 'inactive')),

                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            )
        """)

        cursor.execute("""
            CREATE TABLE user_access_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,

                user_id INTEGER NOT NULL,

                login_time TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                logout_time TEXT,

                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),

                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE devices (
                device_id INTEGER PRIMARY KEY AUTOINCREMENT,

                name TEXT NOT NULL,
                category TEXT NOT NULL
                    CHECK(category IN (
                        'sensor',
                        'actuator',
                        'controller',
                        'gateway',
                        'camera',
                        'wearable',
                        'smart_home',
                        'industrial',
                        'accessory',
                        'other'
                    )),
                brand TEXT NOT NULL,
                model TEXT NOT NULL,
                description TEXT,

                price REAL NOT NULL CHECK(price >= 0),
                stock_quantity INTEGER NOT NULL DEFAULT 0
                    CHECK(stock_quantity >= 0),

                condition TEXT NOT NULL DEFAULT 'new'
                    CHECK(condition IN ('new', 'used', 'refurbished')),

                status TEXT NOT NULL DEFAULT 'active'
                    CHECK(status IN ('active', 'inactive', 'archived')),

                created_by INTEGER,
                updated_by INTEGER,

                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),

                FOREIGN KEY (created_by) REFERENCES users(user_id),
                FOREIGN KEY (updated_by) REFERENCES users(user_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE device_audit_logs (
                audit_id INTEGER PRIMARY KEY AUTOINCREMENT,

                device_id INTEGER NOT NULL,
                staff_user_id INTEGER NOT NULL,

                action TEXT NOT NULL
                    CHECK(action IN ('created', 'updated', 'deleted')),
                details TEXT,

                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),

                FOREIGN KEY (device_id) REFERENCES devices(device_id),
                FOREIGN KEY (staff_user_id) REFERENCES users(user_id)
            )
        """)

        cursor.execute("""
            INSERT INTO users (
                role,
                full_name,
                email,
                password_hash,
                phone,
                address,
                staff_id,
                position,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "customer",
            "Test Customer",
            "customer@example.com",
            generate_password_hash("Password123"),
            "0412345678",
            "1 Test Street, Sydney",
            None,
            None,
            "active"
        ))

        cursor.execute("""
            INSERT INTO users (
                role,
                full_name,
                email,
                password_hash,
                phone,
                address,
                staff_id,
                position,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "staff",
            "Test Staff",
            "staff@example.com",
            generate_password_hash("Password123"),
            None,
            None,
            "S001",
            "Catalogue Manager",
            "active"
        ))

        connection.commit()
        connection.close()

    yield app

    if os.path.exists(TEST_DATABASE):
        os.remove(TEST_DATABASE)


@pytest.fixture
def client(app):
    return app.test_client()


def valid_device_data():
    return {
        "name": "Smart Temperature Sensor",
        "category": "sensor",
        "brand": "IoTCo",
        "model": "TEMP-100",
        "description": "Wireless temperature monitoring device.",
        "price": 49.99,
        "stock_quantity": 20,
        "condition": "new",
        "status": "active"
    }


def login_as_customer(client):
    return client.post("/api/auth/login", json={
        "email": "customer@example.com",
        "password": "Password123"
    })


def login_as_staff(client):
    return client.post("/api/auth/login", json={
        "email": "staff@example.com",
        "password": "Password123"
    })


def insert_device(**overrides):
    data = valid_device_data()
    data.update(overrides)

    connection = sqlite3.connect(TEST_DATABASE)
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO devices (
            name,
            category,
            brand,
            model,
            description,
            price,
            stock_quantity,
            condition,
            status,
            created_by,
            updated_by
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["name"],
        data["category"],
        data["brand"],
        data["model"],
        data["description"],
        data["price"],
        data["stock_quantity"],
        data["condition"],
        data["status"],
        data.get("created_by", 2),
        data.get("updated_by", 2)
    ))
    device_id = cursor.lastrowid
    connection.commit()
    connection.close()

    return device_id


def get_device(device_id):
    connection = sqlite3.connect(TEST_DATABASE)
    connection.row_factory = sqlite3.Row
    device = connection.execute("""
        SELECT *
        FROM devices
        WHERE device_id = ?
    """, (device_id,)).fetchone()
    connection.close()

    return device


def test_validation_accepts_valid_device_data():
    is_valid, error = validate_device_data(valid_device_data())

    assert is_valid is True
    assert error is None


def test_validation_rejects_missing_required_device_name():
    data = valid_device_data()
    data["name"] = ""

    is_valid, error = validate_device_data(data)

    assert is_valid is False
    assert "Device name" in error


def test_validation_rejects_negative_price():
    data = valid_device_data()
    data["price"] = -1

    is_valid, error = validate_device_data(data)

    assert is_valid is False
    assert "Price" in error


def test_validation_rejects_negative_stock_quantity():
    data = valid_device_data()
    data["stock_quantity"] = -1

    is_valid, error = validate_device_data(data)

    assert is_valid is False
    assert "Stock quantity" in error


def test_validation_rejects_decimal_stock_quantity():
    data = valid_device_data()
    data["stock_quantity"] = 1.5

    is_valid, error = validate_device_data(data)

    assert is_valid is False
    assert "Stock quantity" in error


def test_validation_rejects_invalid_device_type():
    data = valid_device_data()
    data["category"] = "not_a_type"

    is_valid, error = validate_device_data(data)

    assert is_valid is False
    assert "Category" in error


def test_api_requires_login_to_list_devices(client):
    response = client.get("/api/devices")

    assert response.status_code == 401


def test_api_staff_can_create_device_with_type_alias(client):
    login_as_staff(client)

    data = valid_device_data()
    data["type"] = data.pop("category")

    response = client.post("/api/devices", json=data)
    body = response.get_json()

    assert response.status_code == 201
    assert body["device"]["name"] == "Smart Temperature Sensor"
    assert body["device"]["category"] == "sensor"
    assert body["device"]["created_by"] == 2


def test_api_customer_cannot_create_device(client):
    login_as_customer(client)

    response = client.post("/api/devices", json=valid_device_data())

    assert response.status_code == 403


def test_api_customer_can_list_and_search_active_devices(client):
    insert_device(name="Smart Temperature Sensor", category="sensor")
    insert_device(
        name="Industrial Gateway",
        category="gateway",
        model="GATE-1",
        description="Network gateway for industrial deployments."
    )
    insert_device(name="Archived Camera", category="camera", status="archived")

    login_as_customer(client)

    response = client.get("/api/devices?q=temp")
    body = response.get_json()

    assert response.status_code == 200
    assert len(body["devices"]) == 1
    assert body["devices"][0]["name"] == "Smart Temperature Sensor"

    response = client.get("/api/devices?type=gateway")
    body = response.get_json()

    assert response.status_code == 200
    assert len(body["devices"]) == 1
    assert body["devices"][0]["category"] == "gateway"


def test_api_staff_can_update_device(client):
    device_id = insert_device()
    login_as_staff(client)

    data = valid_device_data()
    data["name"] = "Updated Sensor"
    data["price"] = 59.5
    data["stock_quantity"] = 15

    response = client.put(f"/api/devices/{device_id}", json=data)
    body = response.get_json()
    device = get_device(device_id)

    assert response.status_code == 200
    assert body["device"]["name"] == "Updated Sensor"
    assert device["price"] == 59.5
    assert device["updated_by"] == 2


def test_api_customer_cannot_update_or_delete_device(client):
    device_id = insert_device()
    login_as_customer(client)

    update_response = client.put(
        f"/api/devices/{device_id}",
        json=valid_device_data()
    )
    delete_response = client.delete(f"/api/devices/{device_id}")

    assert update_response.status_code == 403
    assert delete_response.status_code == 403


def test_api_staff_can_archive_single_device(client):
    device_id = insert_device()
    login_as_staff(client)

    response = client.delete(f"/api/devices/{device_id}")
    device = get_device(device_id)
    list_response = client.get("/api/devices")
    body = list_response.get_json()

    assert response.status_code == 200
    assert device["status"] == "archived"
    assert body["devices"] == []


def test_api_staff_can_archive_multiple_devices(client):
    first_device_id = insert_device(name="First Sensor", model="FIRST-1")
    second_device_id = insert_device(name="Second Sensor", model="SECOND-1")
    remaining_device_id = insert_device(name="Remaining Sensor", model="REMAIN-1")

    login_as_staff(client)

    response = client.delete("/api/devices", json={
        "device_ids": [first_device_id, second_device_id]
    })
    body = response.get_json()
    list_response = client.get("/api/devices")
    list_body = list_response.get_json()

    assert response.status_code == 200
    assert body["devices"]["device_ids"] == [first_device_id, second_device_id]
    assert get_device(first_device_id)["status"] == "archived"
    assert get_device(second_device_id)["status"] == "archived"
    assert get_device(remaining_device_id)["status"] == "active"
    assert len(list_body["devices"]) == 1
    assert list_body["devices"][0]["device_id"] == remaining_device_id
