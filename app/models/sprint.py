import uuid
from datetime import datetime
from app.extensions import db


class Sprint(db.Model):
    __tablename__ = "sprints"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.String(36), db.ForeignKey("projects.id"), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    goal = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default="planning")  # planning | active | completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tasks = db.relationship("Task", backref="sprint", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "name": self.name,
            "goal": self.goal,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }
