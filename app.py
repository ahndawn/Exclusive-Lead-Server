#REFER TO 'docs' DIRECTORY FOR INFORMATION AND QUESTIONS ABOUT THE APP
from flask import Flask
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from routes.auth import auth_bp, login_manager, email_key
from routes.home import app_bp
from routes.domains import domain_bp
from routes.table import table_bp
from helpers import database_url

# Load environment variables from .env file. Information on .env found in docs/herokuDeployment.md
load_dotenv()

migrate = Migrate()
db = SQLAlchemy()

app = Flask(__name__)

# database wasn't able to migrate with postgres url provided from heroku, so 'postgres://' needed to be changed to 'postgresql://'
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'GdsfeG7_3f6dfwxI73_rh4'
app.config['SENDGRID_API_KEY'] = email_key

login_manager.login_view = 'auth.login'


# used BluePrint for clean route management
app.register_blueprint(auth_bp)
app.register_blueprint(app_bp)
app.register_blueprint(domain_bp)
app.register_blueprint(table_bp)
db.init_app(app)
migrate = Migrate(app, db)

login_manager.init_app(app)


with app.app_context():
    db.create_all()

