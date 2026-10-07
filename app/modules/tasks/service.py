from app.extensions import db
from app.models.task import Task, Tag
from app.models.user import User


VALID_STATUSES = ("backlog", "todo", "in_progress", "review", "done")
VALID_PRIORITIES = ("critical", "high", "medium", "low")


def create_task(project_id: str, reporter_id: str, title: str, **kwargs):
    task = Task(
        project_id=project_id,
        reporter_id=reporter_id,
        title=title,
        description=kwargs.get("description"),
        status=kwargs.get("status", "backlog"),
        priority=kwargs.get("priority", "medium"),
        assignee_id=kwargs.get("assignee_id"),
        sprint_id=kwargs.get("sprint_id"),
        story_points=kwargs.get("story_points"),
    )
    due = kwargs.get("due_date")
    if due:
        from datetime import date
        task.due_date = date.fromisoformat(due)

    db.session.add(task)
    db.session.commit()
    return task


def get_project_tasks(project_id: str, sprint_id=None, status=None):
    q = Task.query.filter_by(project_id=project_id)
    if sprint_id == "backlog":
        q = q.filter(Task.sprint_id.is_(None))
    elif sprint_id:
        q = q.filter_by(sprint_id=sprint_id)
    if status:
        q = q.filter_by(status=status)
    return q.order_by(Task.created_at.desc()).all()


def get_task(task_id: str):
    return Task.query.get(task_id)


def update_task(task_id: str, **kwargs):
    task = Task.query.get(task_id)
    if not task:
        return None, "Task not found"

    allowed = ("title", "description", "status", "priority", "assignee_id", "sprint_id", "story_points", "due_date")
    for k, v in kwargs.items():
        if k in allowed:
            if k == "due_date" and v:
                from datetime import date
                task.due_date = date.fromisoformat(v)
            elif k == "status" and v not in VALID_STATUSES:
                return None, f"Invalid status. Must be one of {VALID_STATUSES}"
            elif k == "priority" and v not in VALID_PRIORITIES:
                return None, f"Invalid priority. Must be one of {VALID_PRIORITIES}"
            else:
                setattr(task, k, v)

    db.session.commit()
    return task, None


def delete_task(task_id: str):
    task = Task.query.get(task_id)
    if not task:
        return False
    db.session.delete(task)
    db.session.commit()
    return True


def move_task_status(task_id: str, status: str):
    if status not in VALID_STATUSES:
        return None, f"Invalid status"
    task = Task.query.get(task_id)
    if not task:
        return None, "Task not found"
    task.status = status
    db.session.commit()
    return task, None


def assign_to_sprint(task_id: str, sprint_id):
    task = Task.query.get(task_id)
    if not task:
        return None, "Task not found"
    task.sprint_id = sprint_id
    db.session.commit()
    return task, None


def get_user_tasks(project_id: str, user_id: str):
    return Task.query.filter_by(project_id=project_id, assignee_id=user_id).all()


def get_overdue_tasks(project_id: str):
    from datetime import date
    return Task.query.filter(
        Task.project_id == project_id,
        Task.due_date < date.today(),
        Task.status != "done",
    ).all()
