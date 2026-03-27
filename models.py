# models.py
# Each team member adds their models here in their own branch

# Homa — add status field to Sprint: Planned, Active, Complete
# Setayesh — add role field to User: developer or client
# Setayesh — add status field to Task: Not Started, In Progress, Done

class PBI:
    def __init__(self, id, title, priority, effort, status="Incomplete"):
        self.id = id
        self.title = title
        self.priority = priority  # H, M, L
        self.effort = effort
        self.status = status

class Sprint:
    def __init__(self, id, capacity, status="Planned"):
        self.id = id
        self.capacity = capacity
        self.status = status  # Planned, Active, Complete

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
