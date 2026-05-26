from models.device_model import DeviceModel
from utils.validators import (
    DEVICE_CATEGORIES,
    DEVICE_CONDITIONS,
    validate_device_data
)


def clean_text(value):
    if value is None:
        return None

    return str(value).strip()


def normalize_option(value):
    cleaned_value = clean_text(value)

    if cleaned_value is None:
        return None

    return cleaned_value.lower().replace("-", "_").replace(" ", "_")


def is_staff(user):
    return user is not None and user["role"] == "staff"


def validate_staff_user(user):
    if not is_staff(user):
        return "Only staff can manage device records."

    return None


def to_float(value, field_name):
    if isinstance(value, bool):
        return None, f"{field_name} must be a number."

    try:
        number = float(value)
    except (TypeError, ValueError):
        return None, f"{field_name} must be a number."

    return number, None


def to_integer(value, field_name):
    if isinstance(value, bool):
        return None, f"{field_name} must be a whole number."

    try:
        if isinstance(value, float) and not value.is_integer():
            return None, f"{field_name} must be a whole number."

        number = int(value)
    except (TypeError, ValueError):
        return None, f"{field_name} must be a whole number."

    return number, None


def sanitize_device_data(data, existing_device=None):
    sanitized_data = {}

    name = clean_text(data.get("name"))
    category = normalize_option(data.get("category") or data.get("type"))
    brand = clean_text(data.get("brand"))
    model = clean_text(data.get("model"))
    description = clean_text(data.get("description"))
    condition = normalize_option(data.get("condition"))
    status = normalize_option(data.get("status"))

    if existing_device is not None:
        name = name if name is not None else existing_device["name"]
        category = category if category is not None else existing_device["category"]
        brand = brand if brand is not None else existing_device["brand"]
        model = model if model is not None else existing_device["model"]
        description = (
            description
            if description is not None
            else existing_device["description"]
        )
        condition = condition if condition is not None else existing_device["condition"]
        status = status if status is not None else existing_device["status"]

    if not name:
        return None, "Device name is required."

    if len(name) > 120:
        return None, "Device name must be 120 characters or fewer."

    if category not in DEVICE_CATEGORIES:
        return None, "Category must be a valid IoT device category."

    if not brand:
        return None, "Brand is required."

    if len(brand) > 80:
        return None, "Brand must be 80 characters or fewer."

    if not model:
        return None, "Model is required."

    if len(model) > 80:
        return None, "Model must be 80 characters or fewer."

    if description is not None and len(description) > 1000:
        return None, "Description must be 1000 characters or fewer."

    if "price" in data:
        price, error = to_float(data.get("price"), "Price")
        if error:
            return None, error
    elif existing_device is not None:
        price = existing_device["price"]
    else:
        return None, "Price is required."

    if price < 0:
        return None, "Price cannot be negative."

    if "stock_quantity" in data:
        stock_quantity, error = to_integer(
            data.get("stock_quantity"),
            "Stock quantity"
        )
        if error:
            return None, error
    elif existing_device is not None:
        stock_quantity = existing_device["stock_quantity"]
    else:
        stock_quantity = 0

    if stock_quantity < 0:
        return None, "Stock quantity cannot be negative."

    if condition is None:
        condition = "new"

    if condition not in DEVICE_CONDITIONS:
        return None, "Condition must be new, used, or refurbished."

    if status is None:
        status = "active"

    sanitized_data["name"] = name
    sanitized_data["category"] = category
    sanitized_data["brand"] = brand
    sanitized_data["model"] = model
    sanitized_data["description"] = description
    sanitized_data["price"] = round(price, 2)
    sanitized_data["stock_quantity"] = stock_quantity
    sanitized_data["condition"] = condition
    sanitized_data["status"] = status

    return sanitized_data, None


def sanitize_device_filters(args):
    filters = {}

    search = clean_text(args.get("q") or args.get("search"))
    category = normalize_option(args.get("category") or args.get("type"))
    brand = clean_text(args.get("brand"))
    condition = normalize_option(args.get("condition"))
    min_price = clean_text(args.get("min_price"))
    max_price = clean_text(args.get("max_price"))
    in_stock = normalize_option(args.get("in_stock"))

    if search:
        filters["search"] = search[:100]

    if category:
        if category not in DEVICE_CATEGORIES:
            return None, "Category must be a valid IoT device category."
        filters["category"] = category

    if brand:
        filters["brand"] = brand[:80]

    if condition:
        if condition not in DEVICE_CONDITIONS:
            return None, "Condition must be new, used, or refurbished."
        filters["condition"] = condition

    if min_price:
        price, error = to_float(min_price, "Minimum price")
        if error:
            return None, error
        if price < 0:
            return None, "Minimum price cannot be negative."
        filters["min_price"] = price

    if max_price:
        price, error = to_float(max_price, "Maximum price")
        if error:
            return None, error
        if price < 0:
            return None, "Maximum price cannot be negative."
        filters["max_price"] = price

    if (
        filters.get("min_price") is not None
        and filters.get("max_price") is not None
        and filters.get("min_price") > filters.get("max_price")
    ):
        return None, "Minimum price cannot be greater than maximum price."

    if in_stock in ["true", "1", "yes"]:
        filters["in_stock"] = True
    else:
        filters["in_stock"] = False

    return filters, None


def list_devices(args):
    filters, error = sanitize_device_filters(args)

    if error:
        return None, error, 400

    devices = DeviceModel.list_devices(filters)

    return DeviceModel.to_list(devices), None, 200


def get_device(device_id):
    device = DeviceModel.find_by_id(device_id)

    if device is None or device["status"] != "active":
        return None, "Device not found.", 404

    return DeviceModel.to_dict(device), None, 200


def create_device(data, user):
    staff_error = validate_staff_user(user)

    if staff_error:
        return None, staff_error, 403

    sanitized_data, error = sanitize_device_data(data)

    if error:
        return None, error, 400

    is_valid, error = validate_device_data(sanitized_data)

    if not is_valid:
        return None, error, 400

    device_id = DeviceModel.create_device(sanitized_data, user["user_id"])
    device = DeviceModel.find_by_id(device_id)

    return DeviceModel.to_dict(device), None, 201


def update_device(device_id, data, user):
    staff_error = validate_staff_user(user)

    if staff_error:
        return None, staff_error, 403

    existing_device = DeviceModel.find_by_id(device_id)

    if existing_device is None:
        return None, "Device not found.", 404

    sanitized_data, error = sanitize_device_data(data, existing_device)

    if error:
        return None, error, 400

    is_valid, error = validate_device_data(sanitized_data)

    if not is_valid:
        return None, error, 400

    DeviceModel.update_device(device_id, sanitized_data, user["user_id"])
    updated_device = DeviceModel.find_by_id(device_id)

    return DeviceModel.to_dict(updated_device), None, 200


def delete_device(device_id, user):
    staff_error = validate_staff_user(user)

    if staff_error:
        return None, staff_error, 403

    existing_device = DeviceModel.find_by_id(device_id)

    if existing_device is None:
        return None, "Device not found.", 404

    DeviceModel.delete_device(device_id, user["user_id"])

    return {"device_id": device_id}, None, 200


def get_device_audit_logs(device_id, user):
    staff_error = validate_staff_user(user)

    if staff_error:
        return None, staff_error, 403

    existing_device = DeviceModel.find_by_id(device_id)

    if existing_device is None:
        return None, "Device not found.", 404

    logs = DeviceModel.find_audit_logs_by_device_id(device_id)

    return DeviceModel.audit_to_list(logs), None, 200
