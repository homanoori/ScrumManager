# Contributing to ScrumManager
## Prerequisites
- Python 3.12+
- Node.js 18+
- Docker + docker-compose (optional, for containerised setup)
- PostgreSQL (or use docker-compose which includes it)
## Running the app locally
### Option A — Docker (recommended)
```
cp .env.example .env
# Fill in your database credentials in .env
docker-compose up
```
### Option B — Manual
```
cp .env.example .env
pip install -r requirements.txt
flask db upgrade
python3 seed.py
python3 app.py
```
### Running the React frontend
```
cd frontend
npm install
npm run dev
```
Frontend runs on http://localhost:5173
Flask API runs on http://localhost:5000
## Running tests
```
pytest -v
pytest --cov=. --cov-report=term-missing
```
## Branch strategy
- main — always deployable. Protected. No direct pushes.
- feature/your-feature-name — one branch per feature
- All changes to main must go through a Pull Request
- PR must have CI passing before merge
## Commit message format
Type(scope): short description
Types: feat, fix, refactor, test, docs, chore
Examples:
feat(auth): add JWT login endpoint
fix(sprint): return unfinished PBIs on sprint complete
docs(readme): add screenshots section
test(api): add PBI CRUD coverage
Rules:
- Subject line max 50 characters
- Use imperative mood: 'add' not 'added'
- No period at end of subject line
## Pull Request process
1. Create a feature branch from main
2. Make your changes with meaningful commits
3. Push your branch and open a PR against main
4. Make sure CI is green (GitHub Actions pytest must pass)
5. Request review from your teammate
6. Merge only after approval
## Environment variables
Never commit .env. See .env.example for required variables.
Never hardcode secrets, API keys, or database URLs in source code.