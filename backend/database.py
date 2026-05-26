import sqlite3
from flask import current_app, g

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
    app.teardown_appcontext(close_db)