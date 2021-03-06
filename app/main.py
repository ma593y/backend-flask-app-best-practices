import os
from flask_cors import CORS
from dotenv import load_dotenv
from flask import Flask, Blueprint, request, jsonify, make_response


# Load env variables
load_dotenv()


# Create flask app
app = Flask(__name__)
CORS(app)


# Fix Cors Issues
@app.before_request
def before_request_func():
    if request.method == "OPTIONS": # CORS preflight
        response = make_response()
        return response


# Configurations
if app.config["ENV"] == "production":
    app.config.from_object("core.config.ProductionConfig")
elif app.config["ENV"] == "testing":
    app.config.from_object("core.config.TestingConfig")
else:
    app.config.from_object("core.config.DevelopmentConfig")

print(f"\n-> ENV is set to: {app.config['ENV']}\n")


# Import Database Configurations & Models
from core.database_config import engine, Session, Base
from models.users_model import UsersModel
from models.vehicles_model import VehiclesModel
from models.categories_model import CategoriesModel


# Create/Drop Database Tables
# Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)


# SQLAlchemy session handling
@app.teardown_appcontext
def shutdown_session(*args, **kwargs):
    print(" -"*50, f"\n before: {engine.pool.status()}")
    Session.remove()
    print(f" after:  {engine.pool.status()}\n", " -"*50)


# 404 Error Handler
@app.errorhandler(404)
def endpoint_not_found(error):
    return jsonify({"message": "This endpoint doesn't exists."}), 404


# Import blueprints
from blueprints.accounts_blueprint import accounts_blueprint
from blueprints.categories_blueprint import categories_blueprint
from blueprints.vehicles_blueprint import vehicles_blueprint


# Register blueprints to app v1
app_v1 = Blueprint('app_v1', __name__, url_prefix='/v1')

app_v1.register_blueprint(accounts_blueprint)
app_v1.register_blueprint(categories_blueprint)
app_v1.register_blueprint(vehicles_blueprint)


# Temp Routes
@app_v1.route("/")
def hello():
    return jsonify({"message":"hello world!"}), 200


# Endpoint for Database Status
@app_v1.route("/db_status")
def db():
    db_session = Session()
    try:
        db_session.execute("select NOW();").all()[0][0]
        return jsonify({"message": "Database is working fine."}), 200
    except:
        return jsonify({"message": "Something is wrong with database."}), 503


# Register app version blueprints to main flask app
app.register_blueprint(app_v1)


# Run flask app
if __name__=="__main__":
    app.run(host=os.getenv("HOST"), port=os.getenv("PORT"))


