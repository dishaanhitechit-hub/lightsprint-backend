from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .service import (
    create_task, get_project_tasks, get_task, update_task, delete_task,
    move_task_status, assign_to_sprint, move_pool_to_backlog,
    sync_overdue_tasks, get_user_tasks, log_time, get_task_timelogs,
)
from app.modules.projects.service import is_member, is_admin, get_members

tasks_bp = Blueprint("tasks", __name__, url_prefix="/api")


@tasks_bp.get("/projects/<project_id>/tasks")
@jwt_required()
def list_tasks(project_id):
    user_id = get_jwt_identity()
    if not is_member(project_id, user_id):
        return jsonify({"error": "Access denied"}), 403
    sprint_id = request.args.get("sprint_id")
    status = request.args.get("status")
    tasks = get_project_tasks(project_id, sprint_id, status)
    return jsonify({"tasks": [t.to_dict() for t in tasks]}), 200


@tasks_bp.post("/projects/<project_id>/tasks")
@jwt_required()
def create(project_id):
    user_id = get_jwt_identity()
    if not is_member(project_id, user_id):
        return jsonify({"error": "Access denied"}), 403
    data = request.get_json()
    title = data.get("title", "").strip()
    if not title:
        return jsonify({"error": "Task title is required"}), 400
    task = create_task(project_id, user_id, title, **{k: v for k, v in data.items() if k != "title"})
    return jsonify({"task": task.to_dict()}), 201


@tasks_bp.get("/tasks/<task_id>")
@jwt_required()
def get(task_id):
    user_id = get_jwt_identity()
    task = get_task(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    if not is_member(task.project_id, user_id):
        return jsonify({"error": "Access denied"}), 403
    return jsonify({"task": task.to_dict()}), 200


@tasks_bp.put("/tasks/<task_id>")
@jwt_required()
def update(task_id):
    user_id = get_jwt_identity()
    task = get_task(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    if not is_member(task.project_id, user_id):
        return jsonify({"error": "Access denied"}), 403
    data = request.get_json()
    task, err = update_task(task_id, **data)
    if err:
        return jsonify({"error": err}), 400
    return jsonify({"task": task.to_dict()}), 200


@tasks_bp.delete("/tasks/<task_id>")
@jwt_required()
def delete(task_id):
    user_id = get_jwt_identity()
    task = get_task(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    if not is_member(task.project_id, user_id):
        return jsonify({"error": "Access denied"}), 403
    delete_task(task_id)
    return jsonify({"message": "Task deleted"}), 200


@tasks_bp.patch("/tasks/<task_id>/status")
@jwt_required()
def move_status(task_id):
    user_id = get_jwt_identity()
    task = get_task(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    if not is_member(task.project_id, user_id):
        return jsonify({"error": "Access denied"}), 403
    data = request.get_json()
    task, err = move_task_status(task_id, data.get("status", ""))
    if err:
        return jsonify({"error": err}), 400
    return jsonify({"task": task.to_dict()}), 200


@tasks_bp.patch("/tasks/<task_id>/sprint")
@jwt_required()
def move_sprint(task_id):
    user_id = get_jwt_identity()
    task = get_task(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    if not is_member(task.project_id, user_id):
        return jsonify({"error": "Access denied"}), 403
    data = request.get_json()
    task, err = assign_to_sprint(task_id, data.get("sprint_id"))
    if err:
        return jsonify({"error": err}), 400
    return jsonify({"task": task.to_dict()}), 200


@tasks_bp.patch("/tasks/<task_id>/to-backlog")
@jwt_required()
def to_backlog(task_id):
    user_id = get_jwt_identity()
    task = get_task(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    if not is_admin(task.project_id, user_id):
        return jsonify({"error": "Admin access required"}), 403
    task, err = move_pool_to_backlog(task_id)
    if err:
        return jsonify({"error": err}), 400
    return jsonify({"task": task.to_dict()}), 200


@tasks_bp.post("/projects/<project_id>/tasks/sync-overdue")
@jwt_required()
def sync_overdue(project_id):
    user_id = get_jwt_identity()
    if not is_member(project_id, user_id):
        return jsonify({"error": "Access denied"}), 403
    count = sync_overdue_tasks(project_id)
    return jsonify({"moved": count}), 200


@tasks_bp.get("/projects/<project_id>/tasks/my")
@jwt_required()
def my_tasks(project_id):
    user_id = get_jwt_identity()
    if not is_member(project_id, user_id):
        return jsonify({"error": "Access denied"}), 403
    tasks = get_user_tasks(project_id, user_id)
    return jsonify({"tasks": [t.to_dict() for t in tasks]}), 200


@tasks_bp.get("/projects/<project_id>/members")
@jwt_required()
def project_members(project_id):
    user_id = get_jwt_identity()
    if not is_member(project_id, user_id):
        return jsonify({"error": "Access denied"}), 403
    return jsonify({"members": get_members(project_id)}), 200


@tasks_bp.post("/tasks/<task_id>/log-time")
@jwt_required()
def log_task_time(task_id):
    user_id = get_jwt_identity()
    task = get_task(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    if not is_member(task.project_id, user_id):
        return jsonify({"error": "Access denied"}), 403
    data = request.get_json()
    hours = data.get("hours")
    if not hours or float(hours) <= 0:
        return jsonify({"error": "Valid hours required"}), 400
    log = log_time(task_id, user_id, float(hours), data.get("description"))
    return jsonify({"log": log.to_dict(), "task": task.to_dict()}), 201


@tasks_bp.get("/tasks/<task_id>/time-logs")
@jwt_required()
def task_time_logs(task_id):
    user_id = get_jwt_identity()
    task = get_task(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    if not is_member(task.project_id, user_id):
        return jsonify({"error": "Access denied"}), 403
    logs = get_task_timelogs(task_id)
    return jsonify({"logs": [l.to_dict() for l in logs]}), 200
