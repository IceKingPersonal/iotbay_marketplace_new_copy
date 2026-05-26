import re


def is_valid_email(email):
    """
    Checks whether the email follows a basic format like:
    name@example.com

    The domain does not have to be example.com.
    example.com is only used as a format example.
    """
    if not email:
        return False

    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return re.match(pattern, email) is not None


def is_valid_password(password):
    """
    Password rule:
    - At least 8 characters
    """
    if not password:
        return False

    return len(password) >= 8

#Validates phone number by ensuring it cannot contain numbers, but can contain spaces, apostrophes, hyphens and obviously text.
def is_valid_full_name(full_name):
    if not full_name:
        return False

    pattern = r"^[A-Za-z\s'-]+$"
    return re.match(pattern, full_name) is not None

#Validates phone number by stating it must start with 04 and it must be 10 digits.
def is_valid_australian_mobile(phone):
    if not phone:
        return False

    pattern = r"^04\d{8}$"
    return re.match(pattern, phone) is not None

#Validates that text can only be used in certain fields.
def is_valid_text_only(value):
    if not value:
        return False
    pattern = r"^[A-Za-z\s'-]+$"
    return re.match(pattern, value) is not None

#Validates registration info for customers and staff. Gives either a valid or error message depending on input.
def validate_registration_data(data):

    role = data.get("role")
    full_name = data.get("full_name")
    email = data.get("email")
    password = data.get("password")

    if role not in ["customer", "staff"]:
        return False, "Role must be either customer or staff."

    if not is_valid_full_name(full_name):
        return False, "Full name is required and cannot contain numbers."

    if not is_valid_email(email):
        return False, "Email must be in a valid format, such as name@example.com."

    if not is_valid_password(password):
        return False, "Password must be at least 8 characters long."

    if role == "customer":
        if not is_valid_australian_mobile(data.get("phone")):
            return False, "Phone number must be a valid Australian mobile number starting with 04 and containing 10 digits."

        if not data.get("address"):
            return False, "Address is required for customers."

    if role == "staff":
        if not is_valid_text_only(data.get("position")):
            return False, "Position is required for staff and cannot contain numbers."

    return True, None

#Validates login request data. Ensuring that fields are entered correctly/ required fields are filled in.
def validate_login_data(data):
    email = data.get("email")
    password = data.get("password")

    if not is_valid_email(email):
        return False, "Email must be in a valid format, such as name@example.com."

    if not password:
        return False, "Password is required."

    return True, None