from app.extensions import db
from app.models.project import Project, ProjectMember
from app.models.user import User


def create_project(name: str, description: str, owner_id: str):
    project = Project(name=name, description=description, owner_id=owner_id)
    db.session.add(project)
    db.session.flush()

    member = ProjectMember(project_id=project.id, user_id=owner_id, role="admin")
    db.session.add(member)
    db.session.commit()
    return project


def get_user_projects(user_id: str):
    memberships = ProjectMember.query.filter_by(user_id=user_id).all()
    project_ids = [m.project_id for m in memberships]
    return Project.query.filter(Project.id.in_(project_ids)).all()


def get_project(project_id: str):
    return Project.query.get(project_id)


def update_project(project_id: str, name: str = None, description: str = None):
    project = Project.query.get(project_id)
    if not project:
        return None, "Project not found"
    if name:
        project.name = name
    if description is not None:
        project.description = description
    db.session.commit()
    return project, None


def delete_project(project_id: str):
    project = Project.query.get(project_id)
    if not project:
        return False
    db.session.delete(project)
    db.session.commit()
    return True


def add_member(project_id: str, email: str, role: str = "member"):
    user = User.query.filter_by(email=email).first()
    if not user:
        return None, "User not found"
    existing = ProjectMember.query.filter_by(project_id=project_id, user_id=user.id).first()
    if existing:
        return None, "User already a member"
    member = ProjectMember(project_id=project_id, user_id=user.id, role=role)
    db.session.add(member)
    db.session.commit()
    return member, None


def remove_member(project_id: str, user_id: str):
    member = ProjectMember.query.filter_by(project_id=project_id, user_id=user_id).first()
    if not member:
        return False
    db.session.delete(member)
    db.session.commit()
    return True


def get_members(project_id: str):
    members = ProjectMember.query.filter_by(project_id=project_id).all()
    result = []
    for m in members:
        user = User.query.get(m.user_id)
        if user:
            result.append({**m.to_dict(), "user": user.to_dict()})
    return result


def is_member(project_id: str, user_id: str):
    return ProjectMember.query.filter_by(project_id=project_id, user_id=user_id).first() is not None


def is_admin(project_id: str, user_id: str):
    m = ProjectMember.query.filter_by(project_id=project_id, user_id=user_id).first()
    return m and m.role == "admin"
