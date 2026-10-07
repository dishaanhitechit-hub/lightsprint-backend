from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
from .service import register_user, login_user, get_user_by_id

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/register")
def register():
    data = request.get_json()
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not name or not email or not password:
        return jsonify({"error": "name, email and password are required"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    user, err = register_user(name, email, password)
    if err:
        return jsonify({"error": err}), 409

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    return jsonify({"user": user.to_dict(), "access_token": access_token, "refresh_token": refresh_token}), 201


@auth_bp.post("/login")
def login():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    user, err = login_user(email, password)
    if err:
        return jsonify({"error": err}), 401

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    return jsonify({"user": user.to_dict(), "access_token": access_token, "refresh_token": refresh_token}), 200


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=user_id)
    return jsonify({"access_token": access_token}), 200


@auth_bp.get("/me")
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": user.to_dict()}), 200
