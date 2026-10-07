from app.extensions import db
from app.models.comment import Comment


def add_comment(task_id: str, user_id: str, body: str):
    comment = Comment(task_id=task_id, user_id=user_id, body=body)
    db.session.add(comment)
    db.session.commit()
    return comment


def get_task_comments(task_id: str):
    return Comment.query.filter_by(task_id=task_id).order_by(Comment.created_at.asc()).all()


def delete_comment(comment_id: str, user_id: str):
    comment = Comment.query.get(comment_id)
    if not comment:
        return False, "Comment not found"
    if comment.user_id != user_id:
        return False, "Cannot delete another user's comment"
    db.session.delete(comment)
    db.session.commit()
    return True, None
