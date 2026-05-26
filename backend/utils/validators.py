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


DEVICE_CATEGORIES = [
    "sensor",
    "actuator",
    "controller",
    "gateway",
    "camera",
    "wearable",
    "smart_home",
    "industrial",
    "accessory",
    "other"
]

DEVICE_CONDITIONS = ["new", "used", "refurbished"]
DEVICE_STATUSES = ["active", "inactive", "archived"]


def is_valid_device_name(name):
    return name is not None and 1 <= len(str(name).strip()) <= 120


def is_valid_device_category(category):
    return category in DEVICE_CATEGORIES


def is_valid_device_brand(brand):
    return brand is not None and 1 <= len(str(brand).strip()) <= 80


def is_valid_device_model(model):
    return model is not None and 1 <= len(str(model).strip()) <= 80


def is_valid_device_description(description):
    return description is None or len(str(description).strip()) <= 1000


def is_valid_device_price(price):
    if isinstance(price, bool):
        return False

    try:
        price = float(price)
    except (TypeError, ValueError):
        return False

    return 0 <= price <= 100000


def is_valid_device_stock_quantity(stock_quantity):
    if isinstance(stock_quantity, bool):
        return False

    try:
        if isinstance(stock_quantity, float) and not stock_quantity.is_integer():
            return False

        stock_quantity = int(stock_quantity)
    except (TypeError, ValueError):
        return False

    return 0 <= stock_quantity <= 100000


def is_valid_device_condition(condition):
    return condition in DEVICE_CONDITIONS


def is_valid_device_status(status):
    return status in DEVICE_STATUSES


#Validates Feature 02 device catalogue data before records are saved.
def validate_device_data(data):
    category = data.get("category") or data.get("type")

    if not is_valid_device_name(data.get("name")):
        return False, "Device name is required and must be 120 characters or fewer."

    if not is_valid_device_category(category):
        return False, "Category must be a valid IoT device category."

    if not is_valid_device_brand(data.get("brand")):
        return False, "Brand is required and must be 80 characters or fewer."

    if not is_valid_device_model(data.get("model")):
        return False, "Model is required and must be 80 characters or fewer."

    if not is_valid_device_description(data.get("description")):
        return False, "Description must be 1000 characters or fewer."

    if not is_valid_device_price(data.get("price")):
        return False, "Price must be a number between 0 and 100000."

    if not is_valid_device_stock_quantity(data.get("stock_quantity")):
        return False, "Stock quantity must be a whole number between 0 and 100000."

    if not is_valid_device_condition(data.get("condition")):
        return False, "Condition must be new, used, or refurbished."

    if not is_valid_device_status(data.get("status")):
        return False, "Status must be active, inactive, or archived."

    return True, None

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
