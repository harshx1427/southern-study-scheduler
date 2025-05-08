from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import DevelopmentConfig

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    from app.models.models import User
    return User.query.get(int(user_id))

def create_app(config_object=DevelopmentConfig):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object(config_object)

    #mail.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    from app.routes.threads import threads_bp
    app.register_blueprint(threads_bp)

    @app.route('/')
    def root():
        return redirect(url_for('auth.login'))
    
    with app.app_context():
        db.create_all()

    return app
