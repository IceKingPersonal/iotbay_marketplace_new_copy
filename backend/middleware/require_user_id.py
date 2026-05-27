from flask import g, jsonify, request


def require_user_id():
    raw = request.headers.get("X-User-Id")
    try:
        uid = int(raw) if raw else None
        if uid is None or uid < 1:
            raise ValueError()
    except (TypeError, ValueError):
        return jsonify({"error": "Missing or invalid X-User-Id header"}), 401
    g.user_id = uid
    return None
