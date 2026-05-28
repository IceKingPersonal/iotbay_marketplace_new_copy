import os
import sqlite3
import sys
from pathlib import Path

import pytest
from werkzeug.security import generate_password_hash

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app import create_app

#Creates a separate test database so the actual database is never affected.
TEST_DATABASE = "test_feature05.db"


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
            CREATE TABLE orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                shipping_address TEXT NOT NULL,
                total_price INTEGER NOT NULL,
                currency TEXT NOT NULL DEFAULT 'AUD',
                status TEXT NOT NULL DEFAULT 'Saved'
                    CHECK(status IN ('Saved', 'Paid', 'Cancelled')),
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE payment_methods (
                payment_method_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                payment_type TEXT NOT NULL,
                details TEXT NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES users(user_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE payments (
                payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                payment_method_id INTEGER NOT NULL,
                customer_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                payment_date TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (order_id) REFERENCES orders(order_id),
                FOREIGN KEY (payment_method_id) REFERENCES payment_methods(payment_method_id),
                FOREIGN KEY (customer_id) REFERENCES users(user_id)
            )
        """)

        cursor.execute("""
            INSERT INTO users (role, full_name, email, password_hash, status)
            VALUES (?, ?, ?, ?, ?)
        """, ("customer", "Test Customer", "customer@test.com",
              generate_password_hash("Password123"), "active"))

        cursor.execute("""
            INSERT INTO users (role, full_name, email, password_hash, staff_id, position, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ("staff", "Test Staff", "staff@test.com",
              generate_password_hash("Password123"), "S001", "Sales Assistant", "active"))

        cursor.execute("""
            INSERT INTO users (role, full_name, email, password_hash, status)
            VALUES (?, ?, ?, ?, ?)
        """, ("customer", "Other Customer", "other@test.com",
              generate_password_hash("Password123"), "active"))

        customer_id = cursor.execute(
            "SELECT user_id FROM users WHERE email = ?", ("customer@test.com",)
        ).fetchone()[0]

        other_id = cursor.execute(
            "SELECT user_id FROM users WHERE email = ?", ("other@test.com",)
        ).fetchone()[0]

        #Saved order for the test customer (available to pay).
        cursor.execute("""
            INSERT INTO orders (user_id, shipping_address, total_price, status)
            VALUES (?, ?, ?, ?)
        """, (customer_id, "1 Test Street, Sydney", 150, "Saved"))

        #Already-paid order for the test customer (cannot be paid again).
        cursor.execute("""
            INSERT INTO orders (user_id, shipping_address, total_price, status)
            VALUES (?, ?, ?, ?)
        """, (customer_id, "1 Test Street, Sydney", 80, "Paid"))

        #Saved order belonging to a different customer.
        cursor.execute("""
            INSERT INTO orders (user_id, shipping_address, total_price, status)
            VALUES (?, ?, ?, ?)
        """, (other_id, "2 Test Street, Sydney", 200, "Saved"))

        #Payment method belonging to the test customer.
        cursor.execute("""
            INSERT INTO payment_methods (customer_id, payment_type, details)
            VALUES (?, ?, ?)
        """, (customer_id, "Credit Card", "Visa ending in 4242"))

        #Payment method belonging to a different customer.
        cursor.execute("""
            INSERT INTO payment_methods (customer_id, payment_type, details)
            VALUES (?, ?, ?)
        """, (other_id, "Credit Card", "Mastercard ending in 9999"))

        connection.commit()
        connection.close()

    yield app

    if os.path.exists(TEST_DATABASE):
        os.remove(TEST_DATABASE)


@pytest.fixture
def client(app):
    return app.test_client()


def login_customer(client):
    return client.post("/api/auth/login", json={
        "email": "customer@test.com", "password": "Password123"
    })


def login_staff(client):
    return client.post("/api/auth/login", json={
        "email": "staff@test.com", "password": "Password123"
    })


# ── GET /api/payments/create ──────────────────────────────────────────────────

def test_get_payment_form_returns_orders_and_methods(client):
    #Customer receives their saved orders and payment methods.
    login_customer(client)
    response = client.get("/api/payments/create")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["orders"]) == 1
    assert len(data["payment_methods"]) == 1


def test_get_payment_form_only_saved_orders(client):
    #Already-paid orders do not appear in the payment form.
    login_customer(client)
    data = client.get("/api/payments/create").get_json()
    statuses = [o.get("order_date") for o in data["orders"]]
    assert len(data["orders"]) == 1


def test_get_payment_form_requires_login(client):
    #Unauthenticated request is rejected with 401.
    response = client.get("/api/payments/create")
    assert response.status_code == 401


def test_get_payment_form_rejects_staff(client):
    #Staff users cannot access the customer-only payment form.
    login_staff(client)
    response = client.get("/api/payments/create")
    assert response.status_code == 403


# ── POST /api/payments/create ─────────────────────────────────────────────────

def test_create_payment_success(client):
    #Customer can successfully pay a saved order.
    login_customer(client)
    form = client.get("/api/payments/create").get_json()
    order_id = form["orders"][0]["order_id"]
    method_id = form["payment_methods"][0]["payment_method_id"]

    response = client.post("/api/payments/create", json={
        "order_id": order_id, "payment_method_id": method_id
    })
    assert response.status_code == 201
    assert "Payment successful" in response.get_json()["message"]


def test_create_payment_updates_order_status(client):
    #Order status changes to Paid after a successful payment.
    login_customer(client)
    form = client.get("/api/payments/create").get_json()
    order_id = form["orders"][0]["order_id"]
    method_id = form["payment_methods"][0]["payment_method_id"]

    client.post("/api/payments/create", json={
        "order_id": order_id, "payment_method_id": method_id
    })

    connection = sqlite3.connect(TEST_DATABASE)
    row = connection.execute(
        "SELECT status FROM orders WHERE order_id = ?", (order_id,)
    ).fetchone()
    connection.close()
    assert row[0] == "Paid"


def test_create_payment_missing_order_id(client):
    #Request without order_id is rejected with 400.
    login_customer(client)
    response = client.post("/api/payments/create", json={"payment_method_id": 1})
    assert response.status_code == 400


def test_create_payment_missing_method_id(client):
    #Request without payment_method_id is rejected with 400.
    login_customer(client)
    response = client.post("/api/payments/create", json={"order_id": 1})
    assert response.status_code == 400


def test_create_payment_wrong_customer_order(client):
    #Customer cannot pay an order that belongs to another customer.
    login_customer(client)
    form = client.get("/api/payments/create").get_json()
    method_id = form["payment_methods"][0]["payment_method_id"]

    response = client.post("/api/payments/create", json={
        "order_id": 3, "payment_method_id": method_id
    })
    assert response.status_code == 404


def test_create_payment_wrong_customer_method(client):
    #Customer cannot use a payment method that belongs to another customer.
    login_customer(client)
    form = client.get("/api/payments/create").get_json()
    order_id = form["orders"][0]["order_id"]

    response = client.post("/api/payments/create", json={
        "order_id": order_id, "payment_method_id": 2
    })
    assert response.status_code == 404


def test_create_payment_already_paid_order(client):
    #Customer cannot pay an order that is already Paid.
    login_customer(client)
    form = client.get("/api/payments/create").get_json()
    method_id = form["payment_methods"][0]["payment_method_id"]

    response = client.post("/api/payments/create", json={
        "order_id": 2, "payment_method_id": method_id
    })
    assert response.status_code == 400


def test_create_payment_requires_login(client):
    #Unauthenticated request is rejected with 401.
    response = client.post("/api/payments/create", json={
        "order_id": 1, "payment_method_id": 1
    })
    assert response.status_code == 401


def test_create_payment_rejects_staff(client):
    #Staff users cannot make payments.
    login_staff(client)
    response = client.post("/api/payments/create", json={
        "order_id": 1, "payment_method_id": 1
    })
    assert response.status_code == 403


# ── GET /api/payments/history ─────────────────────────────────────────────────

def test_payment_history_customer_sees_own(client):
    #Customer receives their own payment history with role = customer.
    login_customer(client)
    response = client.get("/api/payments/history")
    assert response.status_code == 200
    data = response.get_json()
    assert data["role"] == "customer"
    assert isinstance(data["payments"], list)


def test_payment_history_staff_sees_all(client):
    #Staff receives all payments with role = staff.
    login_staff(client)
    response = client.get("/api/payments/history")
    assert response.status_code == 200
    data = response.get_json()
    assert data["role"] == "staff"


def test_payment_history_requires_login(client):
    #Unauthenticated request is rejected with 401.
    response = client.get("/api/payments/history")
    assert response.status_code == 401


def test_payment_history_shows_after_payment(client):
    #A completed payment appears in the customer's history.
    login_customer(client)
    form = client.get("/api/payments/create").get_json()
    order_id = form["orders"][0]["order_id"]
    method_id = form["payment_methods"][0]["payment_method_id"]

    client.post("/api/payments/create", json={
        "order_id": order_id, "payment_method_id": method_id
    })

    history = client.get("/api/payments/history").get_json()
    assert len(history["payments"]) == 1
    assert history["payments"][0]["order_id"] == order_id
