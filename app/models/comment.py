import uuid
from datetime import datetime
from app.extensions import db


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = db.Column(db.String(36), db.ForeignKey("tasks.id"), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "task_id": self.task_id,
            "user_id": self.user_id,
            "body": self.body,
            "created_at": self.created_at.isoformat(),
        }
