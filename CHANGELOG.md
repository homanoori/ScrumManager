# Changelog

All notable changes to ScrumManager are documented here.

## [Unreleased] — Phase 2 in progress
- Reports page with burndown chart and velocity table (in progress)
- Comments system on PBIs
- Email notifications on sprint events
- AI-powered effort estimation and sprint planning
- Full design overhaul (dark theme, sidebar, dashboard)

## [v3.1.0] — 2026-05-19
### Added
- React frontend (Vite + TypeScript + Tailwind CSS)
- JWT authentication for all API endpoints
- Flask-RESTX with Swagger UI at /api/docs
- Dashboard page with live stat cards
- Backlog page with sortable table
- Sprint page with drag-and-drop and capacity bar
- Tasks page with inline status update and effort logging
- Dark theme with sidebar navigation across all pages
- Dashboard stats endpoint (/api/stats/)

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