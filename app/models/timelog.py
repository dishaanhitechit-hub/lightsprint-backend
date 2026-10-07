import uuid
from datetime import datetime
from app.extensions import db


class TimeLog(db.Model):
    __tablename__ = "time_logs"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = db.Column(db.String(36), db.ForeignKey("tasks.id"), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    hours = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    logged_at = db.Column(db.DateTime, default=datetime.utcnow)

    logger = db.relationship("User", foreign_keys=[user_id])

    def to_dict(self):
        return {
            "id": self.id,
            "task_id": self.task_id,
            "user_id": self.user_id,
            "hours": self.hours,
            "description": self.description,
            "logged_at": self.logged_at.isoformat(),
        }
