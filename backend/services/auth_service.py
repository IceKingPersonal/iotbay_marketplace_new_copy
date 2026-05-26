from werkzeug.security import generate_password_hash, check_password_hash
from models.user_model import UserModel
from utils.validators import validate_registration_data, validate_login_data


def register_user(data):
    #Handles registration logic.
    is_valid, error = validate_registration_data(data)

    if not is_valid:
        return None, error, 400

    existing_user = UserModel.find_by_email(data.get("email"))

    if existing_user:
        return None, "Email is already registered.", 409

    password_hash = generate_password_hash(data.get("password"))

    try:
        user_id = UserModel.create_user(data, password_hash)
    except Exception as error:
        return None, str(error), 500

    new_user = UserModel.find_by_id(user_id)

    return UserModel.to_dict(new_user), None, 201


def login_user(data):
    #Handles login logic
    is_valid, error = validate_login_data(data)

    if not is_valid:
        return None, error, 400

    user = UserModel.find_by_email(data.get("email"))

    if not user:
        return None, "Invalid email or password.", 401

    if user["status"] != "active":
        return None, "This account is inactive.", 403

    password_matches = check_password_hash(
        user["password_hash"],
        data.get("password")
    )

    if not password_matches:
        return None, "Invalid email or password.", 401

    return UserModel.to_dict(user), None, 200