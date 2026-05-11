![CI](https://github.com/homanoori/ScrumManager/actions/workflows/test.yml/badge.svg)
# ScrumManager

A Scrum backlog management system built with Flask and PostgreSQL.

This project helps Scrum teams manage:
- Product Backlogs
- Sprint Backlogs
- Tasks
- Sprint approvals
- Reports and burndown charts

The application now includes real user authentication with role-based access control using Flask-Login.

---

## Features

- User registration and login
- Password hashing and authentication
- Role-based permissions
- Protected routes using Flask-Login
- Product backlog management
- Sprint backlog tracking
- Task management
- Burndown reporting

---

## Tech Stack

### Backend
- Python
- Flask
- Flask-Login
- Flask-Migrate
- SQLAlchemy
- PostgreSQL

### Frontend
- HTML
- CSS
- Jinja Templates

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/ScrumManagerTeam/ScrumManager.git
cd ScrumManager
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file:

```env
DATABASE_URL=your_database_url
SECRET_KEY=your_secret_key
```

### 4. Run database migrations

```bash
flask db upgrade
```

### 5. Start the application

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

---

## Authentication

The system uses:
- Flask-Login for session management
- Password hashing via Werkzeug security
- Role-based authorization
- Protected routes with `@login_required`

Available roles:
- developer
- client
- scrum_master

---

## Team

- Atena Hosseinifar
- Hamed Tavanpour
- Homa Ahmadinoori
- Setayesh Mahmoudi
- Sasan Shahin

---

## Current Progress

### Completed
- Real authentication system
- Protected routes
- Role-based access control
- Product backlog functionality
- Sprint management
- Reports module

### In Progress
- SQLAlchemy migration cleanup
- Docker setup
- Automated testing
- CI/CD pipeline
- React frontend migration

----

## Licenses

Academic project for Software Engineering.
