from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .service import get_user, update_user

users_bp = Blueprint("users", __name__, url_prefix="/api/users")


@users_bp.get("/<user_id>")
@jwt_required()
def get(user_id):
    user = get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": user.to_dict()}), 200


@users_bp.put("/<user_id>")
@jwt_required()
def update(user_id):
    current_user_id = get_jwt_identity()
    if current_user_id != user_id:
        return jsonify({"error": "Cannot update another user's profile"}), 403
    data = request.get_json()
    user, err = update_user(user_id, data.get("name"), data.get("password"))
    if err:
        return jsonify({"error": err}), 400
    return jsonify({"user": user.to_dict()}), 200
