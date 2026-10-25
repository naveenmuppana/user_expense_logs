# ExpenseHub — Personal Expense Tracker API

**A production-oriented backend project built with Python, FastAPI, PostgreSQL, and SQLAlchemy.**

ExpenseHub is a personal expense-tracking REST API designed to demonstrate practical backend engineering skills, including API development, relational database design, schema migrations, validation, automated testing, CI, logging, exception handling, and production readiness.

The application follows a **modular monolith architecture**, organizing related functionality into clear modules within one application.

## Current Project Status

**Current phase: Stage 5 — Production Readiness**

| Component | Status |
|---|---|
| Python 3.12 and FastAPI setup | Completed |
| Docker and PostgreSQL 17 | Configured |
| SQLAlchemy database integration | Completed |
| Expense model and Pydantic schemas | Completed |
| Alembic migration setup | Completed |
| Create, list, replace, partially update, and delete expenses | Implemented |
| Pagination and expense filtering | Implemented |
| Sorting and query validation | Implemented |
| Automated tests with Pytest | 21 tests passing |
| Test coverage | 99% in the latest local run |
| Dedicated test database | Configured |
| GitHub Actions CI | Implemented |
| Coverage reporting in CI | Implemented |
| Application logging | Implemented |
| Database health endpoint | Implemented |
| Centralized unexpected-exception handling | Implemented and tested |
| Authentication and authorization | Planned |
| Production deployment | Planned |

*Test results and coverage represent the latest local run. CI results should be verified from the latest GitHub Actions execution.*

## Technology Stack

- **Language:** Python 3.12
- **API framework:** FastAPI
- **Database:** PostgreSQL 17
- **ORM:** SQLAlchemy
- **Migrations:** Alembic
- **Validation:** Pydantic
- **Database driver:** Psycopg
- **Containerization:** Docker and Docker Compose
- **Testing:** Pytest, FastAPI TestClient, HTTPX
- **Coverage:** pytest-cov
- **CI:** GitHub Actions
- **API documentation:** OpenAPI, Swagger UI, ReDoc
- **Version control:** Git and GitHub

## Architecture

ExpenseHub uses a modular monolith structure.

```text
expense_tracker/
├── app/
│   ├── core/
│   │   ├── config.py
│   │   └── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── expense.py
│   ├── routers/
│   │   └── expense.py
│   ├── schemas/
│   │   └── expense.py
│   ├── services/
│   ├── main.py
│   └── __init__.py
├── alembic/
│   └── versions/
├── tests/
│   ├── conftest.py
│   ├── test_database.py
│   ├── test_db_connection.py
│   ├── test_expenses.py
│   └── test_health.py
├── .github/
│   └── workflows/
│       └── tests.yml
├── .env                  # Local only; not committed
├── .gitignore
├── alembic.ini
├── compose.yaml
├── project_blueprint.md
├── requirements.txt
└── README.md             # Public-facing documentation
```

The structure above describes the intended project layout; optional directories such as `services/` may remain empty until needed.

### Main responsibilities

- `app/main.py` — Creates the FastAPI application, registers routes, configures logging, exposes health checks, and handles unexpected exceptions.
- `app/core/config.py` — Loads application configuration from environment variables.
- `app/core/database.py` — Configures SQLAlchemy and database session management.
- `app/models/` — Contains database models.
- `app/schemas/` — Defines request validation and response schemas.
- `app/routers/` — Implements HTTP endpoints and request handling.
- `alembic/` — Tracks database schema changes.
- `tests/` — Contains automated tests and test fixtures.
- `.github/workflows/tests.yml` — Runs the test and coverage workflow in GitHub Actions.

## API Endpoints

Base URL: `http://127.0.0.1:8000`

### Expense APIs

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/expense/` | Create an expense |
| GET | `/expense/` | Retrieve expenses with filtering, pagination, and sorting |
| PUT | `/expense/{expense_id}` | Replace editable expense fields |
| PATCH | `/expense/{expense_id}` | Partially update an expense |
| DELETE | `/expense/{expense_id}` | Delete an expense |

### Operational endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Basic application response |
| GET | `/health/db` | Check database connectivity |

### List API capabilities

The expense listing endpoint supports:

- Pagination through `limit` and `offset`.
- Category filtering.
- Minimum and maximum amount filters.
- Start and end date filters.
- Sorting by supported fields, including ID, amount, title, and creation timestamp.
- Ascending and descending sort order.
- Validation of invalid ranges and unsupported sorting fields.

### Example: Create an expense

Request:

```json
{
  "title": "Metro Ticket",
  "amount": "61.00",
  "category": "Travel"
}
```

Expected successful status: `201 Created`.

Example response:

```json
{
  "id": 1,
  "title": "Metro Ticket",
  "amount": "61.00",
  "category": "Travel",
  "created_at": "2026-10-21T00:00:00"
}
```

The ID and timestamp above are illustrative. The actual response depends on the database-generated values.

### API documentation

Start the application and visit:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Getting Started

### Prerequisites

- Python 3.12
- Docker Desktop
- Git

### 1. Clone the repository

```powershell
git clone https://github.com/naveenmuppana/user_expense_logs.git
cd user_expense_logs
```

### 2. Create and activate a virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file in the project root.

Example configuration:

```env
DATABASE_URL=postgresql+psycopg://root:<your-password>@localhost:5433/expense_tracker
TEST_DATABASE_URL=postgresql+psycopg://root:<your-password>@localhost:5433/expense_tracker_test
```

Replace the placeholder with your locally configured database password. Adjust the host port if your Docker configuration differs.

**Security:** Never commit `.env` or actual credentials. Keep the test database separate from the development database.

### 5. Start PostgreSQL

From the project root:

```powershell
docker compose up -d
docker compose ps
```

Confirm the database container is running before starting the application or tests.

### 6. Apply database migrations

```powershell
python -m alembic upgrade head
python -m alembic current
```

Alembic manages schema changes through versioned migration files.

### 7. Start the application

```powershell
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` to explore the API.

## Database Design

The initial `Expense` model contains:

| Field | Purpose |
|---|---|
| `id` | Primary key |
| `title` | Expense description |
| `amount` | Monetary amount using a decimal-compatible type |
| `category` | Expense category |
| `created_at` | Creation timestamp |

SQLAlchemy defines the model and manages database interactions. Alembic tracks schema changes.

Financial values use decimal-compatible types to avoid common floating-point precision problems.

## Automated Testing

ExpenseHub uses Pytest to verify API behavior, database configuration, and error handling.

The test suite covers:

- Database session cleanup.
- Confirmation that tests use `expense_tracker_test`.
- Expense creation and retrieval.
- Input validation.
- Pagination and filtering.
- Sorting.
- PUT, PATCH, and DELETE operations.
- Missing-expense responses.
- Invalid amount and date ranges.
- Database health-check success and failure.
- Safe responses from the centralized exception handler.

Run the complete suite with coverage:

```powershell
python -m pytest --cov=app --cov-report=term-missing --cov-report=xml
```

The command generates `coverage.xml` locally. The file is excluded from Git through `.gitignore`.

**Latest verified local result:** 21 tests passed, 99% code coverage, and no warnings.

Coverage is a measure of executed code, not a guarantee that every possible behavior is correct. Continue adding tests for important edge cases.

## Continuous Integration

GitHub Actions runs the automated tests in a CI environment with PostgreSQL.

The workflow:

1. Checks out the repository.
2. Sets up Python.
3. Starts a PostgreSQL service for tests.
4. Installs project dependencies.
5. Configures test database environment variables.
6. Runs Pytest with coverage reporting.

Workflow location:

```text
.github/workflows/tests.yml
```

The CI workflow validates changes before they are considered ready to merge or deploy. Production deployment automation has not yet been implemented.

## Logging and Error Handling

The application includes:

- Configured application logging.
- Database connectivity checks through `/health/db`.
- A centralized handler for unexpected exceptions.
- Generic error responses that avoid exposing internal exception details to API clients.
- Server-side exception logging for troubleshooting.

Expected application errors, such as missing resources and invalid requests, should continue to use appropriate HTTP status codes rather than being treated as unexpected server failures.

## Development Roadmap

### Stage 1 — Foundation

- [x] Set up FastAPI and Python.
- [x] Configure PostgreSQL with Docker.
- [x] Configure SQLAlchemy and database sessions.
- [x] Create the Expense model.
- [x] Initialize Alembic and apply the initial migration.
- [x] Create Pydantic schemas.

### Stage 2 — Core REST APIs

- [x] Create expenses.
- [x] Retrieve expenses.
- [x] Replace expenses using PUT.
- [x] Partially update expenses using PATCH.
- [x] Delete expenses.
- [x] Implement pagination, filtering, and sorting.
- [x] Validate query parameters and common invalid ranges.

### Stage 3 — Automated Testing and CI

- [x] Configure Pytest and the test client.
- [x] Create a dedicated test database.
- [x] Add API and database tests.
- [x] Add coverage reporting.
- [x] Configure GitHub Actions to run tests.
- [ ] Add Ruff linting and formatting.
- [ ] Expand edge-case and integration testing as features grow.

### Stage 4 — Production Readiness

- [x] Add application logging.
- [x] Add a database health endpoint.
- [x] Add centralized unexpected-exception handling.
- [x] Test safe error responses.
- [ ] Separate development and production configuration.
- [ ] Review secret handling and database permissions.
- [ ] Add structured logging and operational monitoring.
- [ ] Review database connection pooling and lifecycle behavior.
- [ ] Add production deployment configuration.
- [ ] Verify all important error paths and health checks.

### Stage 5 — Authentication and Security

- [ ] User registration and login.
- [ ] Secure password hashing.
- [ ] Token-based authentication.
- [ ] Authorization and expense ownership checks.
- [ ] Rate limiting.
- [ ] Security-focused tests.

### Stage 6 — Finance Features

- [ ] Income tracking.
- [ ] Budgets and category management.
- [ ] Recurring transactions.
- [ ] Monthly summaries and analytics.
- [ ] Group expenses and expense splitting.
- [ ] Settlements and balance calculations.

### Stage 7 — Deployment and Scalability

- [ ] Production Docker configuration.
- [ ] Nginx reverse proxy.
- [ ] AWS deployment.
- [ ] Production CI/CD and deployment verification.
- [ ] Redis caching where justified.
- [ ] Background jobs with Celery and a suitable message broker where justified.
- [ ] Load testing and performance optimization.
- [ ] Monitoring, alerting, and operational documentation.

## Engineering Principles

- Keep routes, models, schemas, and business logic separated.
- Validate incoming data.
- Use decimal-compatible types for financial values.
- Manage database schema changes through migrations.
- Manage database sessions safely.
- Never expose secrets or internal exception details to API clients.
- Keep automated tests isolated from development data.
- Add authentication and ownership checks before supporting multiple users.
- Introduce infrastructure tools only when they solve a real problem.
- Document completed work separately from planned work.

## Learning Objectives

ExpenseHub is intended to build practical experience with:

- Python backend engineering and REST API design.
- FastAPI dependency injection and validation.
- SQLAlchemy and PostgreSQL.
- Database migrations and schema evolution.
- Automated testing and CI.
- Logging, error handling, and operational readiness.
- Authentication and authorization.
- Docker and production deployment.
- AWS, caching, background jobs, and scalability.

## License

A license has not yet been specified. Add an appropriate license before distributing the project for reuse.
