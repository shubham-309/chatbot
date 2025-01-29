from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from authlib.integrations.flask_client import OAuth
from flask_cors import CORS

# Initialize app components
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
oauth = OAuth()  # OAuth instance

def create_app():
    app = Flask(__name__)

    # Load app config
    app.config.from_object('app.config.Config')
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    oauth.init_app(app)

    # Register OAuth providers
    oauth.init_app(app)
    app.extensions['oauth'] = oauth  # Ensure OAuth is registered under extensions

    oauth.register(
        name='google',
        client_id="229253112686-iqfc9k9vudissfoq3rf8ik6708fq365t.apps.googleusercontent.com",
        client_secret="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",
        access_token_url='https://accounts.google.com/o/oauth2/token',
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        api_base_url='https://www.googleapis.com/oauth2/v1/',
        client_kwargs={'scope': 'email profile'}
    )

    # Register blueprints
    from app.auth.routes import auth_bp
    from app.chatbot.routes import chatbot_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(chatbot_bp, url_prefix='/chatbot')

    return app
