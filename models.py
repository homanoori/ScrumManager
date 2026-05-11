from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="developer")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
        }
        
class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    pbis = db.relationship("PBI", backref="project", lazy=True)
    sprints = db.relationship("Sprint", backref="project", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
        }
        
class PBI(db.Model):
    __tablename__ = "pbis"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    priority = db.Column(db.String(1), nullable=False)  # H, M, L
    effort = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="Incomplete")
    sprint_id = db.Column(db.Integer, db.ForeignKey("sprints.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=True)

    tasks = db.relationship("Task", backref="pbi", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "priority": self.priority,
            "effort": self.effort,
            "status": self.status,
            "sprint_id": self.sprint_id,
        }

class Sprint(db.Model):
    __tablename__ = "sprints"

    id = db.Column(db.Integer, primary_key=True)
    capacity = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="Planned")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=True)

    pbis = db.relationship("PBI", backref="sprint", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "capacity": self.capacity,
            "status": self.status,
        }


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    estimated_effort = db.Column(db.Float, nullable=False)
    actual_effort = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default="Not Started")
    pbi_id = db.Column(db.Integer, db.ForeignKey("pbis.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    effort_logs = db.relationship("EffortLog", backref="task", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "estimated_effort": self.estimated_effort,
            "actual_effort": self.actual_effort,
            "status": self.status,
            "pbi_id": self.pbi_id,
        }


class EffortLog(db.Model):
    __tablename__ = "effort_logs"

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    hours_spent = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
class AuditLog(db.Model):
    __tablename__ = "auditlog"
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    action = db.Column(db.String(50), nullable=False)
    entity_type = db.Column(db.String(20), nullable=False)
    entity_id = db.Column(db.Integer, nullable=True)
    old_value = db.Column(db.Text, nullable=True)
    new_value = db.Column(db.Text, nullable=True)