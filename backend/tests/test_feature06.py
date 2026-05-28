import os
import sqlite3
import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from models.shipment_model import ShipmentModel


TEST_DATABASE = "test_iotbay.db"


@pytest.fixture
def app():
    if os.path.exists(TEST_DATABASE):
        os.remove(TEST_DATABASE)

    test_app = create_app()

    test_app.config.update({
        "TESTING": True,
        "DATABASE": TEST_DATABASE,
        "SECRET_KEY": "test-secret-key"
    })

    with test_app.app_context():
        db_conn = sqlite3.connect(TEST_DATABASE)
        db_conn.row_factory = sqlite3.Row
        cur = db_conn.cursor()

        cur.execute("""
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
                status TEXT NOT NULL DEFAULT 'active',
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            )
        """)



        cur.execute("""
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



        cur.execute("""
            CREATE TABLE user_access_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                login_time TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                logout_time TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)




        cur.execute("""
            CREATE TABLE shipments (
                shipment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL UNIQUE,
                staff_user_id INTEGER NOT NULL,
                recipient_name TEXT NOT NULL,
                delivery_address TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending'
                    CHECK(status IN ('pending', 'shipped', 'delivered')),
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                FOREIGN KEY (order_id) REFERENCES orders(order_id),
                FOREIGN KEY (staff_user_id) REFERENCES users(user_id)
            )
        """)



        cur.execute("""
            INSERT INTO users (role, full_name, email, password_hash, phone, address, staff_id, position, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("customer", "Test Customer", "customer@test.com",
              generate_password_hash("Password123"),
              "0412345678", "1 Test St, Sydney", None, None, "active"))



        cur.execute("""
            INSERT INTO users (role, full_name, email, password_hash, phone, address, staff_id, position, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("staff", "Test Staff", "staff@test.com",
              generate_password_hash("Password123"),
              None, None, "S001", "Sales Assistant", "active"))



        # status is 'Paid' with capital P - matches the orders table CHECK constraint
        cur.execute("""
            INSERT INTO orders (user_id, shipping_address, total_price, status)
            VALUES (1, '1 Test St, Sydney', 199, 'Paid')
        """)



        cur.execute("""
            INSERT INTO orders (user_id, shipping_address, total_price, status)
            VALUES (1, '1 Test St, Sydney', 49, 'Saved')
        """)

        db_conn.commit()
        db_conn.close()

    yield test_app

    if os.path.exists(TEST_DATABASE):
        os.remove(TEST_DATABASE)




@pytest.fixture
def client(app):
    return app.test_client()




def login_as_staff(client):
    return client.post("/api/auth/login", json={
        "email": "staff@test.com",
        "password": "Password123"
    })




def login_as_customer(client):
    return client.post("/api/auth/login", json={
        "email": "customer@test.com",
        "password": "Password123"
    })




def get_all_shipments_from_db():
    db_conn = sqlite3.connect(TEST_DATABASE)
    db_conn.row_factory = sqlite3.Row
    rows = db_conn.execute("SELECT * FROM shipments ORDER BY shipment_id ASC").fetchall()
    db_conn.close()
    return rows




# Unit Tests
#Test 1: create() inserts a new shipment and returns the new ID
def test_unit_1(app):
    with app.app_context():
        new_id = ShipmentModel.create(1, 2, "Test Customer", "1 Test St, Sydney")
        all_shipments = get_all_shipments_from_db()

        assert new_id == 1
        assert len(all_shipments) == 1




#Test 2: new shipment has status 'pending' by default
def test_unit_2(app):
    with app.app_context():
        ShipmentModel.create(1, 2, "Test Customer", "1 Test St, Sydney")
        all_shipments = get_all_shipments_from_db()

        assert all_shipments[0]["status"] == "pending"




#Test 3: order_is_paid() returns True for a Paid order
def test_unit_3(app):
    with app.app_context():
        result = ShipmentModel.order_is_paid(1)
        assert result == True




#Test 4: order_is_paid() returns False for a Saved order
def test_unit_4(app):
    with app.app_context():
        result = ShipmentModel.order_is_paid(2)
        assert result == False




#Test 5: shipment_exists_for_order() detects an existing shipment
def test_unit_5(app):
    with app.app_context():
        ShipmentModel.create(1, 2, "Test Customer", "1 Test St, Sydney")
        already_exists = ShipmentModel.shipment_exists_for_order(1)
        assert already_exists == True




#Test 6: update() correctly changes the shipment status
def test_unit_6(app):
    with app.app_context():
        created_id = ShipmentModel.create(1, 2, "Test Customer", "1 Test St, Sydney")
        ShipmentModel.update(created_id, "shipped", "Test Customer", "1 Test St, Sydney")

        updated_shipment = ShipmentModel.find_by_id(created_id)
        assert updated_shipment["status"] == "shipped"





# API Tests
#Test 1: staff can create a shipment for a paid order
def test_api_1(client):
    login_as_staff(client)

    response = client.post("/api/shipments/", json={
        "order_id": 1,
        "delivery_address": "1 Test St, Sydney"
    })

    assert response.status_code == 201
    assert len(get_all_shipments_from_db()) == 1




#Test 2: creating a shipment for an unpaid order is rejected
def test_api_2(client):
    login_as_staff(client)

    response = client.post("/api/shipments/", json={
        "order_id": 2,
        "delivery_address": "1 Test St, Sydney"
    })

    assert response.status_code == 400
    assert len(get_all_shipments_from_db()) == 0





#Test 3: second shipment for the same order is rejected
def test_api_3(client):
    login_as_staff(client)

    client.post("/api/shipments/", json={
        "order_id": 1,
        "delivery_address": "1 Test St, Sydney"
    })

    second_response = client.post("/api/shipments/", json={
        "order_id": 1,
        "delivery_address": "1 Test St, Sydney"
    })

    assert second_response.status_code == 400
    assert len(get_all_shipments_from_db()) == 1




#Test 4: customer cannot create a shipment
def test_api_4(client):
    login_as_customer(client)

    response = client.post("/api/shipments/", json={
        "order_id": 1,
        "delivery_address": "1 Test St, Sydney"
    })

    assert response.status_code == 403




#Test 5: staff can update a shipment status
def test_api_5(client):
    login_as_staff(client)

    client.post("/api/shipments/", json={
        "order_id": 1,
        "delivery_address": "1 Test St, Sydney"
    })

    update_response = client.put("/api/shipments/1", json={
        "status": "shipped",
        "recipient_name": "Test Customer",
        "delivery_address": "1 Test St, Sydney"
    })

    assert update_response.status_code == 200
    assert update_response.get_json()["shipment"]["status"] == "shipped"



#Test 6: customer can view their own shipment
def test_api_6(client):
    login_as_staff(client)

    client.post("/api/shipments/", json={
        "order_id": 1,
        "delivery_address": "1 Test St, Sydney"
    })

    client.get("/api/auth/logout")
    login_as_customer(client)

    view_response = client.get("/api/shipments/1")
    assert view_response.status_code == 200
