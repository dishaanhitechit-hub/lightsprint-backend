from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .service import add_comment, get_task_comments, delete_comment
from app.modules.tasks.service import get_task
from app.modules.projects.service import is_member

comments_bp = Blueprint("comments", __name__, url_prefix="/api")


@comments_bp.get("/tasks/<task_id>/comments")
@jwt_required()
def list_comments(task_id):
    user_id = get_jwt_identity()
    task = get_task(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    if not is_member(task.project_id, user_id):
        return jsonify({"error": "Access denied"}), 403
    comments = get_task_comments(task_id)
    return jsonify({"comments": [c.to_dict() for c in comments]}), 200


@comments_bp.post("/tasks/<task_id>/comments")
@jwt_required()
def create(task_id):
    user_id = get_jwt_identity()
    task = get_task(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    if not is_member(task.project_id, user_id):
        return jsonify({"error": "Access denied"}), 403
    data = request.get_json()
    body = data.get("body", "").strip()
    if not body:
        return jsonify({"error": "Comment body is required"}), 400
    comment = add_comment(task_id, user_id, body)
    return jsonify({"comment": comment.to_dict()}), 201


@comments_bp.delete("/comments/<comment_id>")
@jwt_required()
def delete(comment_id):
    user_id = get_jwt_identity()
    ok, err = delete_comment(comment_id, user_id)
    if not ok:
        return jsonify({"error": err}), 400
    return jsonify({"message": "Comment deleted"}), 200
