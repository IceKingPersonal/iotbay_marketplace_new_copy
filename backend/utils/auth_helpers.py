from functools import wraps
from flask import session, jsonify
from models.user_model import UserModel


def get_current_user():
    #Gets logged in user
    user_id = session.get("user_id")

    if not user_id:
        return None

    user = UserModel.find_by_id(user_id)

    if not user:
        return None

    if user["status"] != "active":
        return None

    return user


def login_required(route_function):
    #Ensures only logged in users can access different routes.
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        user = get_current_user()

        if not user:
            return jsonify({"error": "You must be logged in."}), 401

        return route_function(*args, **kwargs)

    return wrapper