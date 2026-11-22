# ExpenseHub

A FastAPI expense-tracking API with JWT authentication, PostgreSQL storage and Alembic migrations.

## Quick start (Docker)

```bash
cp .env.example .env        # then edit the values, especially JWT_SECRET_KEY
docker compose up --build
```

The API runs at http://127.0.0.1:8000 (interactive docs at `/docs`). Migrations run automatically on start.

## Local development

```bash
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
docker compose up -d db
alembic upgrade head
uvicorn app.main:app --reload
```

## Configuration

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | Application database |
| `TEST_DATABASE_URL` | Test database; its name must be `expense_tracker_test` |
| `JWT_SECRET_KEY` | Token signing key (required) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime, default 30 |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | Used by Docker Compose |

Create the `expense_tracker_test` database by hand before running the tests.

## Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/auth/register` | Create an account |
| POST | `/auth/login` | Get a bearer token |
| GET | `/auth/me` | Current user |
| POST | `/expense/` | Create an expense |
| GET | `/expense/` | List with filters (`category`, `min_amount`, `max_amount`, `start_date`, `end_date`), sorting and pagination |
| GET | `/expense/{id}` | Get one expense |
| PUT / PATCH | `/expense/{id}` | Replace / partially update |
| DELETE | `/expense/{id}` | Delete |
| GET | `/expense/summary/monthly?year=` | Totals per month |
| GET | `/expense/summary/categories` | Totals per category |
| GET | `/expense/export` | CSV export (same filters as the list) |
| GET | `/health/db` | Database health (503 when unavailable) |

All `/expense` routes require `Authorization: Bearer <token>` and only see the caller's own data.

## Tests and lint

```bash
pytest --cov=app
ruff check .
```
