from flask import Blueprint, jsonify

from db import get_db, rows_to_dicts

bp = Blueprint("products", __name__)


@bp.get("", strict_slashes=False)
def list_products():
    products = rows_to_dicts(get_db().execute("SELECT * FROM products ORDER BY products_uid").fetchall())
    return jsonify({"products": products})
