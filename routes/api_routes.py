from flask import Blueprint
from flask_restx import Api, Resource, fields
from flask_login import login_required
from models import db, PBI, Sprint, Task

api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp, doc="/docs", title="ScrumManager API", version="1.0",
          description="REST API for ScrumManager")

# --- Namespaces (like folders for each resource) ---
pbi_ns = api.namespace("pbis", description="Product Backlog Items")
sprint_ns = api.namespace("sprints", description="Sprints")
task_ns = api.namespace("tasks", description="Tasks")

# --- Models (defines what the JSON looks like in Swagger) ---
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

# --- PBI Endpoints ---
@pbi_ns.route("/")
class PBIList(Resource):
    @pbi_ns.marshal_list_with(pbi_model)
    def get(self):
        """Get all PBIs"""
        return PBI.query.all()

@pbi_ns.route("/<int:pbi_id>")
class PBIItem(Resource):
    @pbi_ns.marshal_with(pbi_model)
    def get(self, pbi_id):
        """Get a single PBI by ID"""
        return PBI.query.get_or_404(pbi_id)

# --- Sprint Endpoints ---
@sprint_ns.route("/")
class SprintList(Resource):
    @sprint_ns.marshal_list_with(sprint_model)
    def get(self):
        """Get all sprints"""
        return Sprint.query.all()

@sprint_ns.route("/<int:sprint_id>")
class SprintItem(Resource):
    @sprint_ns.marshal_with(sprint_model)
    def get(self, sprint_id):
        """Get a single sprint by ID"""
        return Sprint.query.get_or_404(sprint_id)

# --- Task Endpoints ---
@task_ns.route("/")
class TaskList(Resource):
    @task_ns.marshal_list_with(task_model)
    def get(self):
        """Get all tasks"""
        return Task.query.all()

@task_ns.route("/<int:task_id>")
class TaskItem(Resource):
    @task_ns.marshal_with(task_model)
    def get(self, task_id):
        """Get a single task by ID"""
        return Task.query.get_or_404(task_id)