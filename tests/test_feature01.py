import os
import sqlite3
import sys

import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from models.access_log_model import AccessLogModel

#Creates a test database so actual databse isn't effected.
TEST_DATABASE = "test_iotbay.db"

#Setup before creating and trying different tests.

#Create seperate Flask app and test database for each test. Ensures tests are independent and prevents changes to actual db.
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
            "customer",
            "Other Customer",
            "other@example.com",
            generate_password_hash("Password123"),
            "0498765432",
            "2 Test Street, Sydney",
            None,
            None,
            "active"
        ))

        connection.commit()
        connection.close()

    yield app

    if os.path.exists(TEST_DATABASE):
        os.remove(TEST_DATABASE)

#Create a Flask test client. Allows API endpoints to be tested manually without having to run python app.py
@pytest.fixture
def client(app):
    return app.test_client()

#Helper function to read all acceess logs from the test database.
def get_logs():
    connection = sqlite3.connect(TEST_DATABASE)
    connection.row_factory = sqlite3.Row
    
    logs = connection.execute("""
        SELECT *
        FROM user_access_logs
        ORDER BY log_id ASC
    """).fetchall()

    connection.close()
    return logs

#Unit Tests
#Test 1: Checks that create_login_log() creates a new access log record when a user logs in
def test_unit_1(app):
    with app.app_context():
        log_id = AccessLogModel.create_login_log(1)
        
        logs = get_logs()
        
        assert log_id == 1
        assert len(logs) == 1
        
#Test 2: Checks that the created access log is linked to correct user ID
def test_unit_2(app):
    with app.app_context():
        AccessLogModel.create_login_log(1)
        logs = get_logs()
        assert logs[0]["user_id"] == 1
        
#Test 3: Checks that a login timestamp is automatically recorded when the access log is created.
def test_unit_3(app):
    with app.app_context():
        AccessLogModel.create_login_log(1)
        logs = get_logs()
        
        assert logs[0]["login_time"] is not None
        assert logs[0]["login_time"] != ""

#Test 4: Checks multiple logins create seperate access log records with a unique log ID.
def test_unit_4(app):
    with app.app_context():
        first_log_id = AccessLogModel.create_login_log(1)
        second_log_id = AccessLogModel.create_login_log(1)
        
        logs = get_logs()
        
        assert len(logs) == 2
        assert first_log_id != second_log_id
        assert logs[0]["log_id"] != logs[1]["log_id"]
        
#API Tests
#Test 1: Checks that a successful login request creates one access log.
def test_api_1(client):
    response = client.post("/api/auth/login", json={
        "email": "customer@example.com",
        "password": "Password123" 
    })
    
    logs = get_logs()
    assert response.status_code == 200
    assert len(logs) == 1
    
#Test 2: Checks that the access log created by login belongs to the logged-in user.
def test_api_2(client):
    response = client.post("/api/auth/login", json={
        "email": "customer@example.com",
        "password": "Password123"
    })

    logs = get_logs()

    assert response.status_code == 200
    assert logs[0]["user_id"] == 1
    
#Test 3: Checks that the accesss log created by login includes a login timestamp.
def test_api_3(client):
    response = client.post("/api/auth/login", json={
        "email": "customer@example.com",
        "password": "Password123"
    })

    logs = get_logs()

    assert response.status_code == 200
    assert logs[0]["login_time"] is not None
    assert logs[0]["login_time"] != ""
    
#Test 4: Checks that an access log is not created when login fails.
def test_api_4(client):
    response = client.post("/api/auth/login", json={
        "email": "customer@example.com",
        "password": "WrongPassword"
    })

    logs = get_logs()

    assert response.status_code != 200
    assert len(logs) == 0