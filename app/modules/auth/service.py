from app.extensions import db, bcrypt
from app.models.user import User


def register_user(name: str, email: str, password: str):
    if User.query.filter_by(email=email).first():
        return None, "Email already registered"

    hashed = bcrypt.generate_password_hash(password).decode("utf-8")
    user = User(name=name, email=email, password_hash=hashed)
    db.session.add(user)
    db.session.commit()
    return user, None


def login_user(email: str, password: str):
    user = User.query.filter_by(email=email).first()
    if not user:
        return None, "Invalid email or password"
    if not bcrypt.check_password_hash(user.password_hash, password):
        return None, "Invalid email or password"
    return user, None


def get_user_by_id(user_id: str):
    return User.query.get(user_id)
