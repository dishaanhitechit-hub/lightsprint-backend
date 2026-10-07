from datetime import date
from app.extensions import db
from app.models.sprint import Sprint


def create_sprint(project_id: str, name: str, goal: str = None, start_date=None, end_date=None):
    sprint = Sprint(
        project_id=project_id,
        name=name,
        goal=goal,
        start_date=start_date,
        end_date=end_date,
    )
    db.session.add(sprint)
    db.session.commit()
    return sprint


def get_project_sprints(project_id: str):
    return Sprint.query.filter_by(project_id=project_id).order_by(Sprint.created_at.desc()).all()


def get_sprint(sprint_id: str):
    return Sprint.query.get(sprint_id)


def update_sprint(sprint_id: str, **kwargs):
    sprint = Sprint.query.get(sprint_id)
    if not sprint:
        return None, "Sprint not found"
    for k, v in kwargs.items():
        if hasattr(sprint, k) and v is not None:
            setattr(sprint, k, v)
    db.session.commit()
    return sprint, None


def delete_sprint(sprint_id: str):
    sprint = Sprint.query.get(sprint_id)
    if not sprint:
        return False
    for task in sprint.tasks:
        task.sprint_id = None
    db.session.delete(sprint)
    db.session.commit()
    return True


def start_sprint(sprint_id: str):
    sprint = Sprint.query.get(sprint_id)
    if not sprint:
        return None, "Sprint not found"
    if sprint.status != "planning":
        return None, "Only planning sprints can be started"
    sprint.status = "active"
    if not sprint.start_date:
        sprint.start_date = date.today()
    db.session.commit()
    return sprint, None


def complete_sprint(sprint_id: str):
    sprint = Sprint.query.get(sprint_id)
    if not sprint:
        return None, "Sprint not found"
    if sprint.status != "active":
        return None, "Only active sprints can be completed"
    sprint.status = "completed"
    if not sprint.end_date:
        sprint.end_date = date.today()
    db.session.commit()
    return sprint, None


def get_sprint_stats(sprint_id: str):
    sprint = Sprint.query.get(sprint_id)
    if not sprint:
        return None
    tasks = sprint.tasks
    total = len(tasks)
    done = sum(1 for t in tasks if t.status == "done")
    return {"total": total, "done": done, "remaining": total - done}
