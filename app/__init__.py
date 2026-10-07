import os
from flask import Flask
from .config import config_map
from .extensions import db, migrate, jwt, bcrypt, cors


def create_app():
    app = Flask(__name__)

    env = os.getenv("FLASK_ENV", "development")
    app.config.from_object(config_map.get(env, config_map["development"]))

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    from .models import User, Project, ProjectMember, Sprint, Task, Tag, Comment  # noqa: F401

    from .modules.auth.routes import auth_bp
    from .modules.projects.routes import projects_bp
    from .modules.sprints.routes import sprints_bp
    from .modules.tasks.routes import tasks_bp
    from .modules.comments.routes import comments_bp
    from .modules.users.routes import users_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(sprints_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(comments_bp)
    app.register_blueprint(users_bp)

    @app.get("/api/health")
    def health():
        return {"status": "ok"}, 200

    return app
