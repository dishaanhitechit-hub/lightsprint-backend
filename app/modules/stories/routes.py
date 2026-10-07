from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .service import create_story, get_project_stories, get_story, update_story, delete_story
from app.modules.projects.service import is_member

stories_bp = Blueprint("stories", __name__, url_prefix="/api")


@stories_bp.get("/projects/<project_id>/stories")
@jwt_required()
def list_stories(project_id):
    user_id = get_jwt_identity()
    if not is_member(project_id, user_id):
        return jsonify({"error": "Access denied"}), 403
    stories = get_project_stories(project_id)
    return jsonify({"stories": [s.to_dict() for s in stories]}), 200


@stories_bp.post("/projects/<project_id>/stories")
@jwt_required()
def create(project_id):
    user_id = get_jwt_identity()
    if not is_member(project_id, user_id):
        return jsonify({"error": "Access denied"}), 403
    data = request.get_json()
    title = data.get("title", "").strip()
    if not title:
        return jsonify({"error": "Story title is required"}), 400
    story = create_story(project_id, user_id, title, **{k: v for k, v in data.items() if k != "title"})
    return jsonify({"story": story.to_dict()}), 201


@stories_bp.get("/stories/<story_id>")
@jwt_required()
def get(story_id):
    story = get_story(story_id)
    if not story:
        return jsonify({"error": "Story not found"}), 404
    user_id = get_jwt_identity()
    if not is_member(story.project_id, user_id):
        return jsonify({"error": "Access denied"}), 403
    tasks = [t.to_dict() for t in story.tasks]
    return jsonify({"story": story.to_dict(), "tasks": tasks}), 200


@stories_bp.put("/stories/<story_id>")
@jwt_required()
def update(story_id):
    story = get_story(story_id)
    if not story:
        return jsonify({"error": "Story not found"}), 404
    user_id = get_jwt_identity()
    if not is_member(story.project_id, user_id):
        return jsonify({"error": "Access denied"}), 403
    data = request.get_json()
    story, err = update_story(story_id, **data)
    if err:
        return jsonify({"error": err}), 400
    return jsonify({"story": story.to_dict()}), 200


@stories_bp.delete("/stories/<story_id>")
@jwt_required()
def delete(story_id):
    story = get_story(story_id)
    if not story:
        return jsonify({"error": "Story not found"}), 404
    user_id = get_jwt_identity()
    if not is_member(story.project_id, user_id):
        return jsonify({"error": "Access denied"}), 403
    delete_story(story_id)
    return jsonify({"message": "Story deleted"}), 200
