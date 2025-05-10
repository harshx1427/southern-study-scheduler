from flask import Flask, redirect, url_for
from config import DevelopmentConfig
from app.extensions import db, login_manager

def create_app(config_object=DevelopmentConfig):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_object)

    db.init_app(app)
    login_manager.init_app(app)

    # ✅ move this inside to avoid early access to uninitialized db
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.models import User
        return User.query.get(int(user_id))

    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    from app.routes.threads import threads_bp
    app.register_blueprint(threads_bp)

    @app.route('/')
    def root():
        return redirect(url_for('auth.login'))
    
    with app.app_context():
        db.create_all()

    return app


@login_manager.user_loader
def load_user(user_id):
    from app.models.models import User
    return User.query.get(int(user_id))
