import uuid
from datetime import datetime
from app.extensions import db

task_tags = db.Table(
    "task_tags",
    db.Column("task_id", db.String(36), db.ForeignKey("tasks.id"), primary_key=True),
    db.Column("tag_id", db.String(36), db.ForeignKey("tags.id"), primary_key=True),
)


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.String(36), db.ForeignKey("projects.id"), nullable=False)
    sprint_id = db.Column(db.String(36), db.ForeignKey("sprints.id"), nullable=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default="backlog")  # backlog | todo | in_progress | review | done
    priority = db.Column(db.String(20), default="medium")  # critical | high | medium | low
    assignee_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=True)
    reporter_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    story_points = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    comments = db.relationship("Comment", backref="task", lazy=True, cascade="all, delete-orphan")
    tags = db.relationship("Tag", secondary=task_tags, backref="tasks", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "sprint_id": self.sprint_id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "assignee_id": self.assignee_id,
            "reporter_id": self.reporter_id,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "story_points": self.story_points,
            "tags": [t.to_dict() for t in self.tags],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class Tag(db.Model):
    __tablename__ = "tags"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.String(36), db.ForeignKey("projects.id"), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(7), default="#6366f1")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "color": self.color}
