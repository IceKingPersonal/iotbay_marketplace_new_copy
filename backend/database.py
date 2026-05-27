import sqlite3
from flask import current_app, g

def ensure_database_ready():
    if current_app.config.get("TESTING"):
        return

    if current_app.extensions.get("iotbay_database_ready"):
        return

    from init_db import create_tables, insert_sample_data

    database = current_app.config["DATABASE"]
    create_tables(database)
    insert_sample_data(database)
    current_app.extensions["iotbay_database_ready"] = True

#Opens a SQLite database connection and then reuses the same connection during one request.
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row

    return g.db

#Closes the database after request is done.
def close_db(error=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()

#Registers the close function with Flask.
def init_app(app):
    app.extensions["iotbay_database_ready"] = False
    app.before_request(ensure_database_ready)
    app.teardown_appcontext(close_db)
