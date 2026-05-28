#This is used to run the backend.
from flask import Flask
from flask_cors import CORS

from config import Config
from database import init_app
from routes.auth_routes import auth_routes
from routes.user_routes import user_routes
from routes.access_log_routes import access_log_routes
from payments import payments_bp
from routes.device_routes import device_routes
from routes.order_routes import order_routes
from routes.shipment_routes import shipment_routes


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    if not app.config.get("SECRET_KEY"):
        app.config["SECRET_KEY"] = "super-secret-key-for-iotbay"

    CORS(
        app,
        supports_credentials=True,
        origins=["http://localhost:5173"],
    )

    init_app(app)

    app.register_blueprint(auth_routes, url_prefix="/api/auth")
    app.register_blueprint(user_routes, url_prefix="/api/users")
    app.register_blueprint(access_log_routes, url_prefix="/api/access-logs")
    app.register_blueprint(payments_bp)
    app.register_blueprint(device_routes, url_prefix="/api/devices")
    app.register_blueprint(order_routes, url_prefix="/api/orders")
    app.register_blueprint(shipment_routes, url_prefix="/api/shipments")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
