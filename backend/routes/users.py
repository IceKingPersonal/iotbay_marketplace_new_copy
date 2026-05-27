from flask import Blueprint, jsonify, request

from db import get_db, row_to_dict
from ids import next_primary_key
from lib.name_split import split_full_name

bp = Blueprint("users", __name__)

def infer_role(db, user_uid: int) -> str:
    if db.execute("SELECT 1 FROM staff WHERE user_uid = ?", (user_uid,)).fetchone() is not None:
        return "staff"
    if db.execute("SELECT 1 FROM customer WHERE user_uid = ?", (user_uid,)).fetchone() is not None:
        return "customer"
    # Fallback if legacy data exists without an entry in staff/customer tables.
    return "customer"


@bp.post("/bootstrap")
def bootstrap():
    body = request.get_json(silent=True) or {}
    email = body.get("email", "").strip() if isinstance(body.get("email"), str) else ""
    full_name_raw = body.get("fullName")
    if isinstance(full_name_raw, str) and full_name_raw.strip():
        full_name = full_name_raw.strip()
    else:
        full_name = email.split("@")[0] if email else "User"
    password_raw = body.get("password")
    if isinstance(password_raw, str) and len(password_raw) > 0:
        password = password_raw[:255]
    else:
        password = "[bootstrap]"

    role = body.get("role")
    if role not in ("customer", "staff"):
        role = "customer"
    position = body.get("position") if isinstance(body.get("position"), str) else ""
    address = body.get("address") if isinstance(body.get("address"), str) else ""

    if not email or len(email) > 50:
        return jsonify({"error": "Invalid email"}), 400

    db = get_db()
    existing = row_to_dict(db.execute("SELECT user_uid FROM users WHERE email = ?", (email,)).fetchone())
    if existing:
        user_uid = existing["user_uid"]
        return jsonify({"user_uid": user_uid, "created": False, "role": infer_role(db, user_uid)})

    names = split_full_name(full_name)
    user_uid = next_primary_key("users")
    db.execute(
        """
        INSERT INTO users (user_uid, first_name, last_name, status, password, email)
        VALUES (?, ?, ?, 1, ?, ?)
        """,
        (user_uid, names["first_name"], names["last_name"], password, email),
    )

    # Create the role-specific row so order authorization can distinguish staff vs customer.
    if role == "staff":
        position = position.strip() or "Staff"
        db.execute(
            """
            INSERT INTO staff (user_uid, position, staff_id)
            VALUES (?, ?, ?)
            """,
            (user_uid, position[:30], user_uid),
        )
    else:
        address = address.strip() or None
        db.execute(
            """
            INSERT INTO customer (user_uid, address)
            VALUES (?, ?)
            """,
            (user_uid, address),
        )

    db.commit()
    return jsonify({"user_uid": user_uid, "created": True, "role": role}), 201
