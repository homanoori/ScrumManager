from flask import Blueprint, request
from flask_restx import Api, Resource, fields
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from models import db, PBI, Sprint, Task, User

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

pbi_input_model = api.model("PBIInput", {
    "title": fields.String(required=True, description="PBI title"),
    "priority": fields.String(required=True, description="H, M, or L"),
    "effort": fields.Float(required=True, description="Effort in hours"),
})

pbi_model = api.model("PBI", {
    "id": fields.Integer,
    "title": fields.String,
    "priority": fields.String,
    "effort": fields.Float,
    "status": fields.String,
    "sprint_id": fields.Integer,
})

paginated_pbi_model = api.model("PaginatedPBIs", {
    "pbis": fields.List(fields.Nested(pbi_model)),
    "total": fields.Integer,
    "page": fields.Integer,
    "per_page": fields.Integer,
    "pages": fields.Integer,
})

sprint_model = api.model("Sprint", {
    "id": fields.Integer,
    "capacity": fields.Float,
    "status": fields.String,
})

paginated_sprint_model = api.model("PaginatedSprints", {
    "sprints": fields.List(fields.Nested(sprint_model)),
    "total": fields.Integer,
    "page": fields.Integer,
    "per_page": fields.Integer,
    "pages": fields.Integer,
})

task_model = api.model("Task", {
    "id": fields.Integer,
    "title": fields.String,
    "estimated_effort": fields.Float,
    "actual_effort": fields.Float,
    "status": fields.String,
    "pbi_id": fields.Integer,
})

paginated_task_model = api.model("PaginatedTasks", {
    "tasks": fields.List(fields.Nested(task_model)),
    "total": fields.Integer,
    "page": fields.Integer,
    "per_page": fields.Integer,
    "pages": fields.Integer,
})

# --- Auth Endpoints ---
@auth_ns.route("/login")
class Login(Resource):
    @auth_ns.expect(login_model)
    @auth_ns.marshal_with(token_model)
    def post(self):
        """Login and get a JWT token"""
        data = api.payload
        if not data or "username" not in data or "password" not in data:
            api.abort(400, "Username and password are required")
        user = User.query.filter_by(username=data["username"]).first()
        if user and user.check_password(data["password"]):
            token = create_access_token(identity=str(user.id))
            return {"access_token": token, "role": user.role}
        api.abort(401, "Invalid username or password")

# --- PBI Endpoints ---
@pbi_ns.route("/")
class PBIList(Resource):
    @jwt_required()
    @pbi_ns.marshal_with(paginated_pbi_model)
    def get(self):
        """Get all PBIs with pagination"""
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        per_page = min(per_page, 100)
        pagination = PBI.query.paginate(page=page, per_page=per_page, error_out=False)
        return {
            "pbis": pagination.items,
            "total": pagination.total,
            "page": pagination.page,
            "per_page": pagination.per_page,
            "pages": pagination.pages,
        }

    @jwt_required()
    @pbi_ns.expect(pbi_input_model)
    @pbi_ns.marshal_with(pbi_model, code=201)
    def post(self):
        """Create a new PBI"""
        data = api.payload
        if not data.get("title", "").strip():
            api.abort(400, "title is required")
        if data.get("priority") not in ["H", "M", "L"]:
            api.abort(400, "priority must be H, M, or L")
        if not data.get("effort") or data["effort"] <= 0:
            api.abort(400, "effort must be a positive number")
        pbi = PBI(
            title=data["title"].strip(),
            priority=data["priority"],
            effort=data["effort"],
            status="Incomplete"
        )
        db.session.add(pbi)
        db.session.commit()
        return pbi, 201

@pbi_ns.route("/<int:pbi_id>")
class PBIItem(Resource):
    @jwt_required()
    @pbi_ns.marshal_with(pbi_model)
    def get(self, pbi_id):
        """Get a single PBI by ID"""
        pbi = PBI.query.get(pbi_id)
        if not pbi:
            api.abort(404, f"PBI {pbi_id} not found")
        return pbi

# --- Sprint Endpoints ---
@sprint_ns.route("/")
class SprintList(Resource):
    @jwt_required()
    @sprint_ns.marshal_with(paginated_sprint_model)
    def get(self):
        """Get all sprints with pagination"""
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        per_page = min(per_page, 100)
        pagination = Sprint.query.paginate(page=page, per_page=per_page, error_out=False)
        return {
            "sprints": pagination.items,
            "total": pagination.total,
            "page": pagination.page,
            "per_page": pagination.per_page,
            "pages": pagination.pages,
        }

@sprint_ns.route("/<int:sprint_id>")
class SprintItem(Resource):
    @jwt_required()
    @sprint_ns.marshal_with(sprint_model)
    def get(self, sprint_id):
        """Get a single sprint by ID"""
        sprint = Sprint.query.get(sprint_id)
        if not sprint:
            api.abort(404, f"Sprint {sprint_id} not found")
        return sprint

# --- Task Endpoints ---
@task_ns.route("/")
class TaskList(Resource):
    @jwt_required()
    @task_ns.marshal_with(paginated_task_model)
    def get(self):
        """Get all tasks with pagination"""
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        per_page = min(per_page, 100)
        pagination = Task.query.paginate(page=page, per_page=per_page, error_out=False)
        return {
            "tasks": pagination.items,
            "total": pagination.total,
            "page": pagination.page,
            "per_page": pagination.per_page,
            "pages": pagination.pages,
        }

@task_ns.route("/<int:task_id>")
class TaskItem(Resource):
    @jwt_required()
    @task_ns.marshal_with(task_model)
    def get(self, task_id):
        """Get a single task by ID"""
        task = Task.query.get(task_id)
        if not task:
            api.abort(404, f"Task {task_id} not found")
        return task