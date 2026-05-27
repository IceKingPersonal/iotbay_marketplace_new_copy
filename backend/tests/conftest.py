import os
import sqlite3
import sys
from pathlib import Path

import pytest


BACKEND_DIR = Path(__file__).resolve().parents[1]

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import init_db
from app import create_app


TEST_DATABASE = "test_feature02_story_iotbay.db"


@pytest.fixture
def app(monkeypatch):
    if os.path.exists(TEST_DATABASE):
        os.remove(TEST_DATABASE)

    monkeypatch.setattr(init_db, "DATABASE", TEST_DATABASE)
    init_db.create_tables()
    init_db.insert_sample_data()

    app = create_app()
    app.config.update({
        "TESTING": True,
        "DATABASE": TEST_DATABASE,
        "SECRET_KEY": "test-secret-key"
    })

    yield app

    if os.path.exists(TEST_DATABASE):
        os.remove(TEST_DATABASE)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def valid_device_payload():
    return {
        "name": "Deterministic Test Sensor",
        "category": "sensor",
        "brand": "TestBrand",
        "model": "TEST-SENSOR-001",
        "description": "Device used by one deterministic test.",
        "price": 55.75,
        "stock_quantity": 11,
        "condition": "new",
        "status": "active"
    }


@pytest.fixture
def login_as_customer():
    def _login(client):
        return client.post("/api/auth/login", json={
            "email": "customer@test.com",
            "password": "Password123"
        })

    return _login


@pytest.fixture
def login_as_staff():
    def _login(client):
        return client.post("/api/auth/login", json={
            "email": "staff@test.com",
            "password": "Password123"
        })

    return _login


@pytest.fixture
def query_one(app):
    def _query(sql, params=()):
        connection = sqlite3.connect(TEST_DATABASE)
        connection.row_factory = sqlite3.Row
        row = connection.execute(sql, params).fetchone()
        connection.close()
        return row

    return _query


@pytest.fixture
def query_all(app):
    def _query(sql, params=()):
        connection = sqlite3.connect(TEST_DATABASE)
        connection.row_factory = sqlite3.Row
        rows = connection.execute(sql, params).fetchall()
        connection.close()
        return rows

    return _query


@pytest.fixture
def insert_device(app, valid_device_payload):
    def _insert(**overrides):
        data = valid_device_payload.copy()
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

    return _insert


@pytest.fixture
def get_device(query_one):
    def _get(device_id):
        return query_one("""
            SELECT *
            FROM devices
            WHERE device_id = ?
        """, (device_id,))

    return _get
