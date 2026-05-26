from flask import Blueprint, jsonify, request
from models.access_log_model import AccessLogModel
from utils.auth_helpers import login_required, get_current_user


access_log_routes = Blueprint("access_log_routes", __name__)


@access_log_routes.route("/me", methods=["GET"])
@login_required
def view_my_access_logs():
    #Allows the logged in user to view their own access logs.
    user = get_current_user()
    search_date = request.args.get("date")

    if search_date:
        logs = AccessLogModel.find_by_user_id_and_date(
            user["user_id"],
            search_date
        )
    else:
        logs = AccessLogModel.find_by_user_id(user["user_id"])

    return jsonify({
        "logs": AccessLogModel.to_list(logs)
    }), 200