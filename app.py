from flask import Flask
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from routes.auth import auth_bp, login_manager
from routes.home import app_bp
from routes.domains import domain_bp
from routes.table import table_bp
from helpers import database_url

# Load environment variables from .env file
load_dotenv()

migrate = Migrate()
db = SQLAlchemy()

migrate = Migrate()
db = SQLAlchemy()

app = Flask(__name__)

if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'GdsfeG7_3f6dfwxI73_rh4'

login_manager.login_view = 'auth.login'

app.register_blueprint(auth_bp)
app.register_blueprint(app_bp)
app.register_blueprint(domain_bp)
app.register_blueprint(table_bp)
db.init_app(app)
migrate = Migrate(app, db)

login_manager.init_app(app)

with app.app_context():
    db.create_all()

