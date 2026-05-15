from flask import Blueprint
from flask_restx import Api, Resource, fields
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from models import db, PBI, Sprint, Task, User
from werkzeug.security import check_password_hash

api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp, doc="/docs", title="ScrumManager API", version="1.0",
          description="REST API for ScrumManager",
          authorizations={
              "Bearer": {
                  "type": "apiKey",
                  "in": "header",
                  "name": "Authorization",
                  "description": "Enter: Bearer <your_token>"
              }
          },
          security="Bearer")

# --- Namespaces ---
auth_ns = api.namespace("auth", description="Authentication")
pbi_ns = api.namespace("pbis", description="Product Backlog Items")
sprint_ns = api.namespace("sprints", description="Sprints")
task_ns = api.namespace("tasks", description="Tasks")

# --- Models ---
login_model = api.model("Login", {
    "username": fields.String(required=True),
    "password": fields.String(required=True),
})

token_model = api.model("Token", {
    "access_token": fields.String,
    "role": fields.String,
})

pbi_model = api.model("PBI", {
    "id": fields.Integer,
    "title": fields.String,
    "priority": fields.String,
    "effort": fields.Float,
    "status": fields.String,
    "sprint_id": fields.Integer,
})

sprint_model = api.model("Sprint", {
    "id": fields.Integer,
    "capacity": fields.Float,
    "status": fields.String,
})

task_model = api.model("Task", {
    "id": fields.Integer,
    "title": fields.String,
    "estimated_effort": fields.Float,
    "actual_effort": fields.Float,
    "status": fields.String,
    "pbi_id": fields.Integer,
})

# --- Auth Endpoints ---
@auth_ns.route("/login")
class Login(Resource):
    @auth_ns.expect(login_model)
    @auth_ns.marshal_with(token_model)
    def post(self):
        """Login and get a JWT token"""
        data = api.payload
        user = User.query.filter_by(username=data["username"]).first()
        if user and user.check_password(data["password"]):
            token = create_access_token(identity=str(user.id))
            return {"access_token": token, "role": user.role}
        api.abort(401, "Invalid username or password")

# --- PBI Endpoints ---
@pbi_ns.route("/")
class PBIList(Resource):
    @jwt_required()
    @pbi_ns.marshal_list_with(pbi_model)
    def get(self):
        """Get all PBIs"""
        return PBI.query.all()

@pbi_ns.route("/<int:pbi_id>")
class PBIItem(Resource):
    @jwt_required()
    @pbi_ns.marshal_with(pbi_model)
    def get(self, pbi_id):
        """Get a single PBI by ID"""
        return PBI.query.get_or_404(pbi_id)

# --- Sprint Endpoints ---
@sprint_ns.route("/")
class SprintList(Resource):
    @jwt_required()
    @sprint_ns.marshal_list_with(sprint_model)
    def get(self):
        """Get all sprints"""
        return Sprint.query.all()

@sprint_ns.route("/<int:sprint_id>")
class SprintItem(Resource):
    @jwt_required()
    @sprint_ns.marshal_with(sprint_model)
    def get(self, sprint_id):
        """Get a single sprint by ID"""
        return Sprint.query.get_or_404(sprint_id)

# --- Task Endpoints ---
@task_ns.route("/")
class TaskList(Resource):
    @jwt_required()
    @task_ns.marshal_list_with(task_model)
    def get(self):
        """Get all tasks"""
        return Task.query.all()

@task_ns.route("/<int:task_id>")
class TaskItem(Resource):
    @jwt_required()
    @task_ns.marshal_with(task_model)
    def get(self, task_id):
        """Get a single task by ID"""
        return Task.query.get_or_404(task_id)