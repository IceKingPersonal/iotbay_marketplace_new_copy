import os
import sqlite3

import pytest
from werkzeug.security import generate_password_hash

from app import create_app


TEST_DATABASE = "test_iotbay_orders.db"


@pytest.fixture
def app():
    if os.path.exists(TEST_DATABASE):
        os.remove(TEST_DATABASE)

    app = create_app()
    app.config.update(
        {
            "TESTING": True,
            "DATABASE": TEST_DATABASE,
            "SECRET_KEY": "test-secret-key",
        }
    )

    with app.app_context():
        connection = sqlite3.connect(TEST_DATABASE)
        cursor = connection.cursor()

        cursor.execute(
            """
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
            """
        )

        cursor.execute(
            """
            CREATE TABLE user_access_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                login_time TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                logout_time TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE products (
                product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_name TEXT NOT NULL,
                manufacturer TEXT,
                type TEXT,
                price INTEGER NOT NULL,
                stock_qty INTEGER NOT NULL DEFAULT 0,
                unit_type TEXT NOT NULL DEFAULT 'Each'
            )
            """
        )

        cursor.execute(
            """
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
            """
        )

        cursor.execute(
            """
            CREATE TABLE order_items (
                order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price INTEGER NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(order_id),
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            )
            """
        )

        users = [
            (
                "customer",
                "Primary Customer",
                "customer1@example.com",
                generate_password_hash("Password123"),
                "0412345678",
                "1 Test Street, Sydney",
                None,
                None,
                "active",
            ),
            (
                "customer",
                "Other Customer",
                "customer2@example.com",
                generate_password_hash("Password123"),
                "0498765432",
                "2 Test Street, Sydney",
                None,
                None,
                "active",
            ),
            (
                "staff",
                "Team Staff",
                "staff@example.com",
                generate_password_hash("Password123"),
                None,
                None,
                "S001",
                "Sales Assistant",
                "active",
            ),
        ]
        cursor.executemany(
            """
            INSERT INTO users (
                role, full_name, email, password_hash, phone, address, staff_id, position, status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            users,
        )

        products = [
            ("Moisture U7 Sensor", "Ubiquiti", "Sensor", 2049, 20),
            ("DC Motor Kit 12V", "SparkFun", "DC Motors", 4999, 8),
            ("LoRa Gateway Pro", "RAK", "Gateway", 18900, 0),
        ]
        cursor.executemany(
            """
            INSERT INTO products (device_name, manufacturer, type, price, stock_qty)
            VALUES (?, ?, ?, ?, ?)
            """,
            products,
        )

        connection.commit()
        connection.close()

    yield app

    if os.path.exists(TEST_DATABASE):
        os.remove(TEST_DATABASE)


@pytest.fixture
def client(app):
    return app.test_client()


def _db_fetchone(query, params=()):
    connection = sqlite3.connect(TEST_DATABASE)
    connection.row_factory = sqlite3.Row
    row = connection.execute(query, params).fetchone()
    connection.close()
    return row


def _db_fetchall(query, params=()):
    connection = sqlite3.connect(TEST_DATABASE)
    connection.row_factory = sqlite3.Row
    rows = connection.execute(query, params).fetchall()
    connection.close()
    return rows


def _login(client, email, password="Password123"):
    return client.post("/api/auth/login", json={"email": email, "password": password})


def _create_order(client, items, shipping_address="1 Test Street, Sydney", currency="AUD"):
    return client.post(
        "/api/orders",
        json={
            "shipping_address": shipping_address,
            "currency": currency,
            "items": items,
        },
    )


def test_us03_1_customer_can_create_order_with_minimum_one_item(client):
    _login(client, "customer1@example.com")
    response = _create_order(client, [{"product_id": 1, "quantity": 2}])

    assert response.status_code == 201
    payload = response.get_json()
    assert payload["order"]["user_id"] == 1
    assert payload["order"]["status"] == "Saved"
    assert len(payload["items"]) >= 1

    empty_response = _create_order(client, [])
    assert empty_response.status_code == 400


def test_us03_2_total_price_is_sum_and_updates_when_items_change(client):
    _login(client, "customer1@example.com")
    create_response = _create_order(
        client,
        [
            {"product_id": 1, "quantity": 2},  # 2 * 2049
            {"product_id": 2, "quantity": 1},  # 1 * 4999
        ],
    )
    assert create_response.status_code == 201
    order_id = create_response.get_json()["order"]["order_id"]
    assert create_response.get_json()["order"]["total_price"] == 9097

    update_response = client.put(
        f"/api/orders/{order_id}",
        json={
            "shipping_address": "Updated Street",
            "currency": "AUD",
            "items": [{"product_id": 2, "quantity": 2}],
        },
    )
    assert update_response.status_code == 200
    assert update_response.get_json()["order"]["total_price"] == 9998


def test_us03_3_stock_reduces_and_is_persisted_when_order_created(client):
    _login(client, "customer1@example.com")
    before = _db_fetchone("SELECT stock_qty FROM products WHERE product_id = 1")["stock_qty"]

    response = _create_order(client, [{"product_id": 1, "quantity": 3}])
    assert response.status_code == 201

    after = _db_fetchone("SELECT stock_qty FROM products WHERE product_id = 1")["stock_qty"]
    assert after == before - 3


def test_us03_4_stock_restores_only_when_order_cancelled(client):
    _login(client, "customer1@example.com")
    before = _db_fetchone("SELECT stock_qty FROM products WHERE product_id = 2")["stock_qty"]
    create_response = _create_order(client, [{"product_id": 2, "quantity": 2}])
    order_id = create_response.get_json()["order"]["order_id"]
    after_create = _db_fetchone("SELECT stock_qty FROM products WHERE product_id = 2")["stock_qty"]
    assert after_create == before - 2

    cancel_response = client.patch(f"/api/orders/{order_id}", json={"status": "Cancelled"})
    assert cancel_response.status_code == 200
    assert cancel_response.get_json()["order"]["status"] == "Cancelled"

    after_cancel = _db_fetchone("SELECT stock_qty FROM products WHERE product_id = 2")["stock_qty"]
    assert after_cancel == before

    second_cancel = client.patch(f"/api/orders/{order_id}", json={"status": "Cancelled"})
    assert second_cancel.status_code == 409
    still_after_second = _db_fetchone("SELECT stock_qty FROM products WHERE product_id = 2")["stock_qty"]
    assert still_after_second == before


def test_us03_5_out_of_stock_items_cannot_be_ordered(client):
    _login(client, "customer1@example.com")
    response = _create_order(client, [{"product_id": 3, "quantity": 1}])

    assert response.status_code == 409
    assert "out of stock" in response.get_json()["error"].lower()

    order_count = _db_fetchone("SELECT COUNT(*) AS count FROM orders")["count"]
    assert order_count == 0


def test_us03_6_customer_can_view_only_own_orders_with_status_and_items(client):
    _login(client, "customer1@example.com")
    first = _create_order(client, [{"product_id": 1, "quantity": 1}]).get_json()["order"]["order_id"]
    second = _create_order(client, [{"product_id": 2, "quantity": 1}]).get_json()["order"]["order_id"]
    client.patch(f"/api/orders/{second}", json={"status": "Cancelled"})

    _login(client, "customer2@example.com")
    _create_order(client, [{"product_id": 1, "quantity": 1}])

    _login(client, "customer1@example.com")
    list_response = client.get("/api/orders")
    assert list_response.status_code == 200
    orders = list_response.get_json()["orders"]
    assert len(orders) == 2
    assert all(order["user_id"] == 1 for order in orders)

    statuses = {order["status"] for order in orders}
    assert "Saved" in statuses
    assert "Cancelled" in statuses

    detail_response = client.get(f"/api/orders/{first}")
    assert detail_response.status_code == 200
    detail = detail_response.get_json()
    assert "order_id" in detail["order"]
    assert "created_at" in detail["order"]
    assert "total_price" in detail["order"]
    assert len(detail["items"]) >= 1
    assert "quantity" in detail["items"][0]


def test_us03_7_customer_can_search_orders_by_id_and_date(client):
    _login(client, "customer1@example.com")
    created = _create_order(client, [{"product_id": 1, "quantity": 1}]).get_json()["order"]
    order_id = created["order_id"]
    order_date = created["created_at"].split(" ")[0]

    by_id = client.get(f"/api/orders?order_id={order_id}")
    assert by_id.status_code == 200
    assert len(by_id.get_json()["orders"]) == 1
    assert by_id.get_json()["orders"][0]["order_id"] == order_id

    by_date = client.get(f"/api/orders?date={order_date}")
    assert by_date.status_code == 200
    assert len(by_date.get_json()["orders"]) >= 1

    no_results = client.get("/api/orders?order_id=99999")
    assert no_results.status_code == 200
    assert no_results.get_json()["orders"] == []


def test_us03_8_staff_can_view_all_customer_orders_but_customers_cannot_view_others(client):
    _login(client, "customer1@example.com")
    _create_order(client, [{"product_id": 1, "quantity": 1}])

    _login(client, "customer2@example.com")
    other_order = _create_order(client, [{"product_id": 2, "quantity": 1}]).get_json()["order"]["order_id"]

    _login(client, "staff@example.com")
    staff_list = client.get("/api/orders")
    assert staff_list.status_code == 200
    assert len(staff_list.get_json()["orders"]) == 2
    assert all("customer_email" in row for row in staff_list.get_json()["orders"])

    staff_filtered = client.get(f"/api/orders?order_id={other_order}")
    assert staff_filtered.status_code == 200
    assert len(staff_filtered.get_json()["orders"]) == 1
    assert staff_filtered.get_json()["orders"][0]["order_id"] == other_order

    _login(client, "customer1@example.com")
    forbidden_detail = client.get(f"/api/orders/{other_order}")
    assert forbidden_detail.status_code == 404


def test_us03_9_customer_can_update_saved_order_items_and_total(client):
    _login(client, "customer1@example.com")
    create_response = _create_order(client, [{"product_id": 1, "quantity": 1}]).get_json()
    order_id = create_response["order"]["order_id"]

    update_response = client.put(
        f"/api/orders/{order_id}",
        json={
            "shipping_address": "Updated Address 99",
            "currency": "AUD",
            "items": [
                {"product_id": 1, "quantity": 2},
                {"product_id": 2, "quantity": 1},
            ],
        },
    )
    assert update_response.status_code == 200
    payload = update_response.get_json()
    assert payload["order"]["status"] == "Saved"
    assert payload["order"]["total_price"] == (2 * 2049) + (1 * 4999)

    rows = _db_fetchall(
        "SELECT product_id, quantity FROM order_items WHERE order_id = ? ORDER BY product_id",
        (order_id,),
    )
    assert len(rows) == 2
    assert rows[0]["product_id"] == 1 and rows[0]["quantity"] == 2
    assert rows[1]["product_id"] == 2 and rows[1]["quantity"] == 1


def test_us03_10_customer_can_cancel_saved_order(client):
    _login(client, "customer1@example.com")
    create_response = _create_order(client, [{"product_id": 1, "quantity": 1}]).get_json()
    order_id = create_response["order"]["order_id"]

    cancel_response = client.patch(f"/api/orders/{order_id}", json={"status": "Cancelled"})
    assert cancel_response.status_code == 200
    assert cancel_response.get_json()["order"]["status"] == "Cancelled"

    row = _db_fetchone("SELECT status FROM orders WHERE order_id = ?", (order_id,))
    assert row["status"] == "Cancelled"
