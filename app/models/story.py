import uuid
from datetime import datetime
from app.extensions import db


class UserStory(db.Model):
    __tablename__ = "user_stories"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.String(36), db.ForeignKey("projects.id"), nullable=False)
    sprint_id = db.Column(db.String(36), db.ForeignKey("sprints.id"), nullable=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default="open")  # open | in_progress | done
    priority = db.Column(db.String(20), default="medium")
    estimated_hours = db.Column(db.Float, nullable=True)
    created_by = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tasks = db.relationship("Task", backref="story", lazy=True, foreign_keys="Task.user_story_id")
    creator = db.relationship("User", foreign_keys=[created_by])

    def total_logged_hours(self):
        return sum(t.total_logged() for t in self.tasks)

    def to_dict(self):
        total_logged = self.total_logged_hours()
        remaining = (self.estimated_hours - total_logged) if self.estimated_hours else None
        return {
            "id": self.id,
            "project_id": self.project_id,
            "sprint_id": self.sprint_id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "estimated_hours": self.estimated_hours,
            "logged_hours": total_logged,
            "remaining_hours": max(remaining, 0) if remaining is not None else None,
            "task_count": len(self.tasks),
            "done_count": sum(1 for t in self.tasks if t.status == "done"),
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
        }
