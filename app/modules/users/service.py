from app.extensions import db, bcrypt
from app.models.user import User


def get_user(user_id: str):
    return User.query.get(user_id)


def update_user(user_id: str, name: str = None, password: str = None):
    user = User.query.get(user_id)
    if not user:
        return None, "User not found"
    if name:
        user.name = name.strip()
    if password:
        if len(password) < 6:
            return None, "Password must be at least 6 characters"
        user.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    db.session.commit()
    return user, None
