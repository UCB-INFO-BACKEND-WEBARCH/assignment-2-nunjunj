from flask import Flask
from flask_migrate import Migrate
from app.models import db
import os
from app.routes.categories import category_routes
from app.routes.tasks import task_routes

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/postgres')
    db.init_app(app)
    Migrate(app, db)
    category_routes(app)
    task_routes(app)
    return app
