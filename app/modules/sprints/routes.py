from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .service import (
    create_sprint, get_project_sprints, get_sprint,
    update_sprint, delete_sprint, start_sprint, complete_sprint, get_sprint_stats,
)
from app.modules.projects.service import is_member, is_admin

sprints_bp = Blueprint("sprints", __name__, url_prefix="/api")


@sprints_bp.get("/projects/<project_id>/sprints")
@jwt_required()
def list_sprints(project_id):
    user_id = get_jwt_identity()
    if not is_member(project_id, user_id):
        return jsonify({"error": "Access denied"}), 403
    sprints = get_project_sprints(project_id)
    return jsonify({"sprints": [s.to_dict() for s in sprints]}), 200


@sprints_bp.post("/projects/<project_id>/sprints")
@jwt_required()
def create(project_id):
    user_id = get_jwt_identity()
    if not is_member(project_id, user_id):
        return jsonify({"error": "Access denied"}), 403
    data = request.get_json()
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "Sprint name is required"}), 400

    from datetime import date
    start = data.get("start_date")
    end = data.get("end_date")
    sprint = create_sprint(
        project_id, name, data.get("goal"),
        date.fromisoformat(start) if start else None,
        date.fromisoformat(end) if end else None,
    )
    return jsonify({"sprint": sprint.to_dict()}), 201


@sprints_bp.get("/sprints/<sprint_id>")
@jwt_required()
def get(sprint_id):
    sprint = get_sprint(sprint_id)
    if not sprint:
        return jsonify({"error": "Sprint not found"}), 404
    user_id = get_jwt_identity()
    if not is_member(sprint.project_id, user_id):
        return jsonify({"error": "Access denied"}), 403
    return jsonify({"sprint": sprint.to_dict()}), 200


@sprints_bp.put("/sprints/<sprint_id>")
@jwt_required()
def update(sprint_id):
    sprint = get_sprint(sprint_id)
    if not sprint:
        return jsonify({"error": "Sprint not found"}), 404
    user_id = get_jwt_identity()
    if not is_member(sprint.project_id, user_id):
        return jsonify({"error": "Access denied"}), 403
    data = request.get_json()
    sprint, err = update_sprint(sprint_id, **{k: v for k, v in data.items() if k in ("name", "goal", "start_date", "end_date")})
    if err:
        return jsonify({"error": err}), 404
    return jsonify({"sprint": sprint.to_dict()}), 200


@sprints_bp.delete("/sprints/<sprint_id>")
@jwt_required()
def delete(sprint_id):
    sprint = get_sprint(sprint_id)
    if not sprint:
        return jsonify({"error": "Sprint not found"}), 404
    user_id = get_jwt_identity()
    if not is_admin(sprint.project_id, user_id):
        return jsonify({"error": "Admin access required"}), 403
    delete_sprint(sprint_id)
    return jsonify({"message": "Sprint deleted"}), 200


@sprints_bp.post("/sprints/<sprint_id>/start")
@jwt_required()
def start(sprint_id):
    sprint = get_sprint(sprint_id)
    if not sprint:
        return jsonify({"error": "Sprint not found"}), 404
    user_id = get_jwt_identity()
    if not is_member(sprint.project_id, user_id):
        return jsonify({"error": "Access denied"}), 403
    sprint, err = start_sprint(sprint_id)
    if err:
        return jsonify({"error": err}), 400
    return jsonify({"sprint": sprint.to_dict()}), 200


@sprints_bp.post("/sprints/<sprint_id>/complete")
@jwt_required()
def complete(sprint_id):
    sprint = get_sprint(sprint_id)
    if not sprint:
        return jsonify({"error": "Sprint not found"}), 404
    user_id = get_jwt_identity()
    if not is_member(sprint.project_id, user_id):
        return jsonify({"error": "Access denied"}), 403
    sprint, err = complete_sprint(sprint_id)
    if err:
        return jsonify({"error": err}), 400
    return jsonify({"sprint": sprint.to_dict()}), 200


@sprints_bp.get("/sprints/<sprint_id>/stats")
@jwt_required()
def stats(sprint_id):
    sprint = get_sprint(sprint_id)
    if not sprint:
        return jsonify({"error": "Sprint not found"}), 404
    user_id = get_jwt_identity()
    if not is_member(sprint.project_id, user_id):
        return jsonify({"error": "Access denied"}), 403
    return jsonify(get_sprint_stats(sprint_id)), 200
