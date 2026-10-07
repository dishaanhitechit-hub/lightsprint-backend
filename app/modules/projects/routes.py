from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .service import (
    create_project, get_user_projects, get_project,
    update_project, delete_project, add_member,
    remove_member, get_members, is_member, is_admin,
)

projects_bp = Blueprint("projects", __name__, url_prefix="/api/projects")


@projects_bp.get("/")
@jwt_required()
def list_projects():
    user_id = get_jwt_identity()
    projects = get_user_projects(user_id)
    return jsonify({"projects": [p.to_dict() for p in projects]}), 200


@projects_bp.post("/")
@jwt_required()
def create():
    user_id = get_jwt_identity()
    data = request.get_json()
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "Project name is required"}), 400
    project = create_project(name, data.get("description", ""), user_id)
    return jsonify({"project": project.to_dict()}), 201


@projects_bp.get("/<project_id>")
@jwt_required()
def get(project_id):
    user_id = get_jwt_identity()
    if not is_member(project_id, user_id):
        return jsonify({"error": "Access denied"}), 403
    project = get_project(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404
    return jsonify({"project": project.to_dict()}), 200


@projects_bp.put("/<project_id>")
@jwt_required()
def update(project_id):
    user_id = get_jwt_identity()
    if not is_admin(project_id, user_id):
        return jsonify({"error": "Admin access required"}), 403
    data = request.get_json()
    project, err = update_project(project_id, data.get("name"), data.get("description"))
    if err:
        return jsonify({"error": err}), 404
    return jsonify({"project": project.to_dict()}), 200


@projects_bp.delete("/<project_id>")
@jwt_required()
def delete(project_id):
    user_id = get_jwt_identity()
    if not is_admin(project_id, user_id):
        return jsonify({"error": "Admin access required"}), 403
    project = get_project(project_id)
    if not project or project.owner_id != user_id:
        return jsonify({"error": "Only owner can delete project"}), 403
    delete_project(project_id)
    return jsonify({"message": "Project deleted"}), 200


@projects_bp.get("/<project_id>/members")
@jwt_required()
def list_members(project_id):
    user_id = get_jwt_identity()
    if not is_member(project_id, user_id):
        return jsonify({"error": "Access denied"}), 403
    return jsonify({"members": get_members(project_id)}), 200


@projects_bp.post("/<project_id>/members")
@jwt_required()
def add(project_id):
    user_id = get_jwt_identity()
    if not is_admin(project_id, user_id):
        return jsonify({"error": "Admin access required"}), 403
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    if not email:
        return jsonify({"error": "email is required"}), 400
    member, err = add_member(project_id, email, data.get("role", "member"))
    if err:
        return jsonify({"error": err}), 400
    return jsonify({"member": member.to_dict()}), 201


@projects_bp.delete("/<project_id>/members/<target_user_id>")
@jwt_required()
def remove(project_id, target_user_id):
    user_id = get_jwt_identity()
    if not is_admin(project_id, user_id):
        return jsonify({"error": "Admin access required"}), 403
    if not remove_member(project_id, target_user_id):
        return jsonify({"error": "Member not found"}), 404
    return jsonify({"message": "Member removed"}), 200
