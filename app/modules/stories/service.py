from app.extensions import db
from app.models.story import UserStory


def create_story(project_id: str, created_by: str, title: str, **kwargs):
    story = UserStory(
        project_id=project_id,
        created_by=created_by,
        title=title,
        description=kwargs.get("description"),
        priority=kwargs.get("priority", "medium"),
        estimated_hours=kwargs.get("estimated_hours"),
        sprint_id=kwargs.get("sprint_id"),
    )
    db.session.add(story)
    db.session.commit()
    return story


def get_project_stories(project_id: str):
    return UserStory.query.filter_by(project_id=project_id).order_by(UserStory.created_at.desc()).all()


def get_story(story_id: str):
    return UserStory.query.get(story_id)


def update_story(story_id: str, **kwargs):
    story = UserStory.query.get(story_id)
    if not story:
        return None, "Story not found"
    allowed = ("title", "description", "status", "priority", "estimated_hours", "sprint_id")
    for k, v in kwargs.items():
        if k in allowed and v is not None:
            setattr(story, k, v)
    db.session.commit()
    return story, None


def delete_story(story_id: str):
    story = UserStory.query.get(story_id)
    if not story:
        return False
    for task in story.tasks:
        task.user_story_id = None
    db.session.delete(story)
    db.session.commit()
    return True
