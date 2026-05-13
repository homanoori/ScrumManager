# Changelog

All notable changes to ScrumManager are documented here.

## [Unreleased] — Phase 2 in progress
- React frontend migration
- JWT authentication for API
- Dark mode
- Mobile responsive layout

## [v3.0.0] — 2026-05-11
### Added
- Real user authentication with hashed passwords (Flask-Login + Werkzeug)
- Role-based access control (developer / client)
- PostgreSQL database with SQLAlchemy ORM and Alembic migrations
- Docker and docker-compose support
- GitHub Actions CI/CD pipeline
- Automated test suite with pytest (66% coverage)
- Deployed to Render.com with Neon PostgreSQL
- AuditLog model tracking all PBI, sprint, and task changes
- Project model for multi-team support
- Seed script for demo data
- Professional README with badges, screenshots, and setup instructions

## [v2.0.0] — 2026-04-02
### Added
- Sprint lock and approval system
- Burndown chart generation with matplotlib
- Effort logging per task
- Role-based UI (client sees limited view)
- Sprint proposal based on capacity

## [v1.0.0] — Initial Release
### Added
- Product backlog management
- Sprint backlog tracking
- Task management
- Basic user roles via session