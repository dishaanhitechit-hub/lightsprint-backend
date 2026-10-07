from datetime import date
from app.extensions import db
from app.models.task import Task, Tag
from app.models.user import User

VALID_STATUSES = ("pool", "backlog", "todo", "in_progress", "review", "done")
VALID_PRIORITIES = ("critical", "high", "medium", "low")


def create_task(project_id: str, reporter_id: str, title: str, **kwargs):
    task = Task(
        project_id=project_id,
        reporter_id=reporter_id,
        title=title,
        description=kwargs.get("description"),
        status=kwargs.get("status", "pool"),
        priority=kwargs.get("priority", "medium"),
        assignee_id=kwargs.get("assignee_id"),
        sprint_id=kwargs.get("sprint_id"),
        user_story_id=kwargs.get("user_story_id"),
        story_points=kwargs.get("story_points"),
        estimated_hours=kwargs.get("estimated_hours"),
    )
    due = kwargs.get("due_date")
    if due:
        task.due_date = date.fromisoformat(due)
    db.session.add(task)
    db.session.commit()
    return task


def get_project_tasks(project_id: str, sprint_id=None, status=None):
    q = Task.query.filter_by(project_id=project_id)
    if sprint_id == "backlog":
        q = q.filter(Task.sprint_id.is_(None), Task.status == "backlog")
    elif sprint_id == "pool":
        q = q.filter(Task.status == "pool")
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
    allowed = ("title", "description", "status", "priority", "assignee_id",
               "sprint_id", "story_points", "due_date", "estimated_hours", "user_story_id")
    for k, v in kwargs.items():
        if k not in allowed:
            continue
        if k == "due_date" and v:
            task.due_date = date.fromisoformat(v)
        elif k == "status" and v and v not in VALID_STATUSES:
            return None, f"Invalid status"
        elif k == "priority" and v and v not in VALID_PRIORITIES:
            return None, f"Invalid priority"
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
        return None, "Invalid status"
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
    if sprint_id and task.status in ("pool", "backlog"):
        task.status = "todo"
    elif not sprint_id:
        task.status = "backlog"
    db.session.commit()
    return task, None


def move_pool_to_backlog(task_id: str):
    task = Task.query.get(task_id)
    if not task:
        return None, "Task not found"
    task.status = "backlog"
    db.session.commit()
    return task, None


def sync_overdue_tasks(project_id: str):
    today = date.today()
    overdue = Task.query.filter(
        Task.project_id == project_id,
        Task.due_date < today,
        Task.status.notin_(["done", "backlog", "pool"]),
    ).all()
    for t in overdue:
        t.status = "backlog"
        t.sprint_id = None
    db.session.commit()
    return len(overdue)


def get_user_tasks(project_id: str, user_id: str):
    return Task.query.filter_by(project_id=project_id, assignee_id=user_id).all()


def log_time(task_id: str, user_id: str, hours: float, description: str = None):
    from app.models.timelog import TimeLog
    log = TimeLog(task_id=task_id, user_id=user_id, hours=hours, description=description)
    db.session.add(log)
    db.session.commit()
    return log


def get_task_timelogs(task_id: str):
    from app.models.timelog import TimeLog
    return TimeLog.query.filter_by(task_id=task_id).order_by(TimeLog.logged_at.desc()).all()
