# models.py
# Each team member adds their models here in their own branch

# Homa     — add status field to Sprint: Planned, Active, Complete
# Setayesh — add role field to User: developer or client
# Setayesh — add status field to Task: Not Started, In Progress, Done
# Hamed    — added EffortLog for burndown chart


class PBI:
    def __init__(self, id, title, priority, effort, status="Incomplete"):
        self.id = id
        self.title = title
        self.priority = priority  # H, M, L
        self.effort = effort
        self.status = status


class Sprint:
    def __init__(self, id, capacity, status="Planned", start_date=None, duration_days=14):
        self.id = id
        self.capacity = capacity
        self.status = status          # Planned, Active, Complete
        self.start_date = start_date  # YYYY-MM-DD string or None
        self.duration_days = duration_days


class Task:
    def __init__(self, id, title, effort, pbi_id, status="Not Started"):
        self.id = id
        self.title = title
        self.effort = effort
        self.pbi_id = pbi_id
        self.status = status  # Not Started, In Progress, Done


class User:
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role  # developer or client


class EffortLog:
    """One row in effort_log: how much effort was spent on a task on a given date."""
    def __init__(self, id, task_id, date, actual_effort):
        self.id = id
        self.task_id = task_id
        self.date = date              # YYYY-MM-DD string
        self.actual_effort = actual_effort
