# DevTrack API

DevTrack is an independent personal project and task tracker API built with Python, FastAPI, SQLAlchemy, and SQLite. It is designed as a small, testable backend that can later support a web dashboard.

## Features in the initial version

- Health endpoint: `GET /health`
- Project CRUD endpoints under `/api/v1/projects`
- Task CRUD endpoints nested under `/api/v1/projects/{project_id}/tasks`
- Task status filtering and pagination
- Request validation with Pydantic
- SQLite persistence through SQLAlchemy
- Automated API tests using pytest and an isolated in-memory SQLite database
- Interactive API documentation at `/docs`

## Requirements

- Python 3.11 or newer
- Git

## Setup

```bash
python -m venv .venv
source .venv/bin/activate       # Windows PowerShell: .venv\\Scripts\\Activate.ps1
python -m pip install -e '.[dev]'
```

The application defaults to `sqlite:///./devtrack.db`. To use a different database URL, set `DATABASE_URL` before starting the application. `.env.example` documents the default; environment variables are not automatically loaded from that file.

## Run the API

```bash
uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000/docs> for interactive API documentation.

## Example requests

Create a project:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/projects \
  -H 'Content-Type: application/json' \
  -d '{"name":"DevTrack","description":"My personal development tracker"}'
```

Create a task (replace `1` with the returned project ID):

```bash
curl -X POST http://127.0.0.1:8000/api/v1/projects/1/tasks \
  -H 'Content-Type: application/json' \
  -d '{"title":"Add task filtering","priority":"high"}'
```

List completed tasks:

```bash
curl 'http://127.0.0.1:8000/api/v1/projects/1/tasks?status_filter=done'
```

## Run tests and lint

```bash
pytest
ruff check .
```

## API overview

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Health status |
| POST | `/api/v1/projects` | Create a project |
| GET | `/api/v1/projects` | List projects |
| GET | `/api/v1/projects/{project_id}` | Get a project |
| PATCH | `/api/v1/projects/{project_id}` | Update a project |
| DELETE | `/api/v1/projects/{project_id}` | Delete a project and its tasks |
| POST | `/api/v1/projects/{project_id}/tasks` | Create a task |
| GET | `/api/v1/projects/{project_id}/tasks` | List/filter tasks |
| GET | `/api/v1/projects/{project_id}/tasks/{task_id}` | Get a task |
| PATCH | `/api/v1/projects/{project_id}/tasks/{task_id}` | Update a task |
| DELETE | `/api/v1/projects/{project_id}/tasks/{task_id}` | Delete a task |

## Design decisions

- **SQLite first:** zero separate database server is needed for local development.
- **Nested tasks:** task URLs make the parent project explicit, and queries ensure a task belongs to the requested project.
- **Validation at the API boundary:** Pydantic schemas validate titles, names, statuses, priorities, and lengths.
- **Test isolation:** tests use a separate in-memory SQLite database and do not depend on local development data.
- **Small initial scope:** no authentication, cloud services, frontend, or AI integration is included in the first version.

## Roadmap

1. Add filtering and sorting options with explicit API tests.
2. Add database migrations with Alembic.
3. Add structured logging and consistent error handling.
4. Add project/task summary endpoints.
5. Consider a React UI only after the API behavior is stable.

## Ownership and project eligibility

This repository is intended to be developed as a personal project. Keep it separate from employer and university repositories, and do not copy proprietary code or data into it. Before submitting it to any external program, verify the program's current eligibility rules and confirm that the repository's license and ownership satisfy them.
