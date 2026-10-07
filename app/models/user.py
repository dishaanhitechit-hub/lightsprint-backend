import uuid
from datetime import datetime
from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owned_projects = db.relationship("Project", backref="owner", lazy=True, foreign_keys="Project.owner_id")
    memberships = db.relationship("ProjectMember", backref="user", lazy=True)
    assigned_tasks = db.relationship("Task", backref="assignee", lazy=True, foreign_keys="Task.assignee_id")
    reported_tasks = db.relationship("Task", backref="reporter", lazy=True, foreign_keys="Task.reporter_id")
    comments = db.relationship("Comment", backref="author", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
        }
