# ExpenseHub — Master Project Blueprint

**Document purpose:** Single source of truth for project scope, architecture, implementation progress, and future development.

**Project type:** Production-oriented Python backend engineering learning project  
**Project status:** In progress  
**Current stage:** Stage 3.1 — Expense model and Alembic setup  
**Development environment:** Windows, PowerShell, VS Code  
**Project directory:** `D:\Development\python\expense_tracker`

---

## 1. Project vision

ExpenseHub is a personal finance and group expense management backend.

The goal is to build a working application while learning the backend engineering skills expected in mid-sized and large technology companies.

The project must teach:

- Python backend development using FastAPI.
- Relational database design using PostgreSQL.
- SQLAlchemy ORM and Alembic migrations.
- REST APIs, CRUD, validation and error handling.
- Authentication, authorization and application security.
- Automated testing with Pytest.
- Git, GitHub, branching, pull requests and code review.
- Redis, Celery and RabbitMQ.
- Docker and Docker Compose.
- Nginx, reverse proxies and load balancing.
- GitHub Actions and CI/CD.
- AWS deployment and cloud infrastructure.
- Logging, monitoring, performance testing and system design.
- Production debugging, reliability, security and scalability.

**Learning approach:** The developer writes the code. The assistant explains concepts, provides small implementation tasks, reviews code, helps debug errors, and updates this blueprint after verified milestones.

Avoid unnecessary complexity. Use a modular monolith first, introduce tools when their purpose is clear, and consider additional infrastructure only when justified.

## 2. Application features

### Phase A — Core expense management

- Create, list, retrieve, update and delete expenses.
- Store amount, title, category and creation timestamp.
- Search, filter, sort and paginate expense records.
- Validate request and response data.
- Persist records in PostgreSQL.
- Provide consistent API responses and error handling.

### Phase B — Users and security

- User registration and login.
- Secure password hashing.
- JWT-based authentication or another appropriate token-based flow.
- User profiles and account settings.
- Authorization and record ownership checks.
- Rate limiting, secure configuration and input validation.

### Phase C — Finance features

- Income and expense tracking.
- Categories and budgets.
- Recurring transactions.
- Monthly summaries and category breakdowns.
- Smart calculator for splitting amounts, percentages and totals.
- Dashboard analytics and budget utilization.

### Phase D — Groups and shared expenses

- Create groups.
- Invite and remove members.
- Enforce membership permissions.
- Record shared expenses and individual shares.
- Calculate balances and settlements.
- Preserve financial history and transaction consistency.

### Phase E — Advanced features

- Background-generated reports.
- Email or notification workflows.
- Budget reminders and recurring-expense processing.
- Redis caching for appropriate read-heavy operations.
- Optional real-time group chat using WebSockets.
- Multi-instance application deployment.

Group chat is optional and comes after the core application, group permissions and expense-sharing functionality are stable.

## 3. Technology stack

| Technology | Responsibility |
|---|---|
| Python 3.12 | Backend programming |
| FastAPI | REST API framework |
| Uvicorn | ASGI server |
| Pydantic / Pydantic Settings | Data validation and configuration |
| PostgreSQL | Persistent relational database |
| SQLAlchemy 2.x | ORM, queries, sessions and connection pooling |
| Psycopg | PostgreSQL driver |
| Alembic | Database schema migrations |
| Pytest + HTTPX | Automated tests and API integration tests |
| Ruff | Linting and formatting |
| Git + GitHub | Version control and collaboration |
| Docker + Compose | Reproducible development and containerized services |
| Redis | Caching, rate limits and other suitable temporary data |
| Celery | Background task execution |
| RabbitMQ | Task message broker |
| Nginx | Reverse proxy and optional load balancing |
| GitHub Actions | CI/CD automation |
| AWS ECS/Fargate | Potential container hosting |
| AWS ECR | Container image registry |
| AWS RDS | Managed PostgreSQL |
| AWS Secrets Manager / IAM | Secret management and access control |
| AWS CloudWatch | Logs, metrics and operational visibility |
| Locust | Load and performance testing |

We will not deploy every component immediately. The initial application needs FastAPI, PostgreSQL and SQLAlchemy; later infrastructure is introduced progressively.

## 4. Current environment and confirmed progress

### Completed and verified

- Python virtual environment created and activated.
- FastAPI and Uvicorn installed.
- Initial root endpoint implemented and tested.
- Project folders created.
- `requirements.txt` generated with `pip freeze`.
- Docker Desktop running.
- PostgreSQL container named `expensehub-db` started.
- Docker PostgreSQL database `expense_tracker` exists.
- PostgreSQL user `root` successfully connected through `psql`.
- Docker PostgreSQL exposed on Windows host port `5433`.
- Local PostgreSQL uses port `5432`.
- `app/core/config.py` created.
- `app/core/database.py` created.
- FastAPI database health endpoint tested successfully with HTTP 200.

### Database connection

The intended application URL uses Docker's published port:

`postgresql+psycopg://root:<local-password>@localhost:5433/expense_tracker`

The actual password must remain in `.env`, not in source code. The Docker Compose credentials and application connection settings must match.

The health endpoint executed `SELECT 1` successfully after the database URL was configured. The application is therefore verified to connect to PostgreSQL at that checkpoint.

### Current folder structure

```text
expense_tracker/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── database.py
│   ├── models/
│   │   └── __init__.py
│   ├── routers/
│   │   └── __init__.py
│   ├── schemas/
│   │   └── __init__.py
│   └── services/
│       └── __init__.py
├── venv/
├── .env
├── .gitignore
├── compose.yaml
└── requirements.txt
```

The files listed above reflect the known project structure. The next tasks below have not yet been confirmed complete.

## 5. Complete development roadmap

### Stage 1 — Environment and infrastructure

**Status: Completed**

- Create and activate virtual environment.
- Install FastAPI and Uvicorn.
- Build the initial endpoint.
- Organize application folders.
- Configure Docker Compose.
- Run PostgreSQL with persistent storage.
- Configure `.env` and `.gitignore`.

**Verification:** API starts and the PostgreSQL container is available.

### Stage 2 — Database connection

**Status: Verified**

- Configure Pydantic Settings.
- Create the SQLAlchemy engine.
- Create the session factory.
- Create the declarative model base.
- Implement `get_db()`.
- Add a database health endpoint.
- Execute a test query against PostgreSQL.

**Verification:** `/health/db` returns HTTP 200 and reports a successful database connection.

### Stage 3 — Expense model, migrations and CRUD

**Status: In progress**

#### Stage 3.1 — Expense model and Alembic setup

- Install Alembic.
- Create `app/models/expense.py`.
- Define the Expense model.
- Register the model in `app/models/__init__.py`.
- Initialize Alembic.
- Configure Alembic to use the application database URL and `Base.metadata`.

The proposed initial Expense model includes:

| Field | Purpose |
|---|---|
| `id` | Primary key |
| `title` | Expense description |
| `amount` | Monetary value using `NUMERIC(12, 2)` |
| `category` | Expense category |
| `created_at` | Database-generated timestamp |

Use Python `Decimal` for monetary values. Additional fields such as `user_id`, currency and transaction date can be introduced when the corresponding business requirements are implemented.

**Current checkpoint:** The model and Alembic setup were instructed, but their implementation has not yet been confirmed.

#### Stage 3.2 — Database migrations

- Configure `alembic/env.py`.
- Import model metadata correctly.
- Generate an initial migration.
- Inspect the generated migration.
- Apply it to the Docker PostgreSQL database.
- Verify the `expenses` table and migration history.

**Completion criterion:** The database schema can be recreated and changed through version-controlled migrations.

#### Stage 3.3 — Expense CRUD

- Create expense request and response schemas.
- Implement `POST /expenses`.
- Implement `GET /expenses`.
- Implement `GET /expenses/{expense_id}`.
- Implement `PUT` or `PATCH /expenses/{expense_id}`.
- Implement `DELETE /expenses/{expense_id}`.
- Handle missing records, invalid data and appropriate HTTP status codes.
- Verify endpoints using `/docs`.

**Completion criterion:** Expense records persist in PostgreSQL and all CRUD operations behave correctly.

### Stage 4 — PostgreSQL engineering

- Primary and foreign keys.
- Constraints and indexes.
- One-to-many and many-to-many relationships.
- Joins and aggregation.
- Transactions and rollback.
- Isolation levels and locking.
- Connection pooling.
- Query plans using `EXPLAIN ANALYZE`.
- Pagination and efficient filtering.
- Avoiding N+1 query problems.
- Backup and restore procedures.
- Migration safety and backward-compatible schema changes.

**Completion criterion:** Understand and demonstrate data integrity, query performance and safe schema evolution.

### Stage 5 — Authentication and security

- User model and registration.
- Password hashing.
- Login and token generation.
- Token validation and expiry.
- Authentication dependencies.
- Authorization and ownership checks.
- Group-level access control.
- Rate limiting and abuse prevention.
- CORS configuration where appropriate.
- Secret management.
- Safe error responses.
- Security tests.

**Completion criterion:** Users can access only resources they are authorized to access.

### Stage 6 — Testing and code quality

- Install Pytest and HTTPX.
- Write unit tests.
- Write API integration tests.
- Configure fixtures and dependency overrides.
- Use an isolated test database.
- Test CRUD, validation, authentication and permissions.
- Test failure cases and database transactions.
- Add Ruff linting and formatting.
- Introduce type checking where useful.
- Measure coverage without treating coverage alone as proof of correctness.

**Completion criterion:** Tests can be run locally and catch meaningful regressions.

### Stage 7 — Business features

- Categories and income.
- Budgets and budget utilization.
- Recurring transactions.
- Profiles and account settings.
- Group creation and membership.
- Shared expense splitting.
- Settlements and balance calculations.
- Monthly summaries and analytics.
- Smart calculator endpoints.
- Data export where appropriate.

**Completion criterion:** Business rules are validated, financial records remain consistent, and access is correctly restricted.

### Stage 8 — Git and GitHub workflow

- Initialize Git repository.
- Create a remote GitHub repository.
- Commit changes incrementally.
- Use feature branches.
- Create GitHub Issues with acceptance criteria.
- Open pull requests against `main`.
- Review diffs and automated checks.
- Resolve merge conflicts.
- Use branch protection and required checks when appropriate.
- Merge and tag releases.
- Practise reverting a faulty change.

**Completion criterion:** Complete a feature from issue to branch, PR, review, merge and release.

### Stage 9 — Redis, Celery and RabbitMQ

- Learn caching and cache invalidation.
- Add Redis only for justified use cases.
- Configure Celery workers and a RabbitMQ broker.
- Implement background reports and notifications.
- Add retries, timeouts and failure handling.
- Make tasks idempotent.
- Understand acknowledgement and duplicate delivery.
- Monitor queues and failed tasks.
- Learn the transactional outbox pattern if reliable event publication becomes necessary.

**Completion criterion:** Slow work can be processed asynchronously without compromising financial correctness.

### Stage 10 — Docker and Nginx

- Dockerize the FastAPI application.
- Use Docker Compose for local infrastructure.
- Separate application and database containers.
- Configure environment variables and health checks.
- Run multiple API instances.
- Configure Nginx as a reverse proxy.
- Practise local load balancing.
- Configure request timeouts and proxy headers.
- Understand graceful shutdown and connection pooling.

**Completion criterion:** Multiple API instances can serve requests against a shared database and their behavior can be tested.

### Stage 11 — GitHub Actions and CI/CD

- Trigger workflows on pushes and pull requests.
- Run linting and automated tests.
- Build Docker images.
- Tag images consistently.
- Publish images to a container registry.
- Protect deployment credentials.
- Add deployment approvals where appropriate.
- Deploy to a test environment.
- Implement release verification and rollback procedures.

**Completion criterion:** Code changes produce repeatable, tested deployment artifacts.

### Stage 12 — AWS deployment

- Understand AWS IAM and least-privilege access.
- Configure networking and security groups.
- Deploy containers using ECS/Fargate or an appropriate alternative.
- Store images in ECR.
- Use RDS for managed PostgreSQL.
- Configure secrets securely.
- Add HTTPS and appropriate load balancing.
- Configure logs, metrics, health checks and backups.
- Manage environment-specific configuration.
- Estimate and control infrastructure costs.

**Completion criterion:** A deployed API can be accessed securely, monitored, updated and recovered.

### Stage 13 — Scaling and operations

- Load test with Locust.
- Profile slow endpoints.
- Optimize SQL queries and indexes.
- Measure database connection-pool pressure.
- Add caching only where measurements justify it.
- Understand horizontal scaling and stateless services.
- Evaluate queue backlogs and worker capacity.
- Add structured logs, metrics, tracing and alerts.
- Practise incident diagnosis and recovery.
- Learn capacity planning and high-availability trade-offs.
- Document system design decisions.

**Completion criterion:** Explain the system's bottlenecks, demonstrate measurable improvements, and justify architectural choices.

### Optional Stage 14 — Real-time group chat

- WebSocket endpoints.
- Authenticated connections.
- Group membership authorization.
- Connection lifecycle and disconnect handling.
- Cross-instance message distribution.
- Message persistence and delivery guarantees.
- Redis Pub/Sub or another suitable messaging approach if multiple instances are required.

This stage is optional and comes after the core ExpenseHub product is stable.

## 6. Architecture principles

1. Start with a modular monolith rather than microservices.
2. PostgreSQL is the source of truth for financial records.
3. Use transactions and database constraints to protect data integrity.
4. Use `Decimal` and PostgreSQL `NUMERIC` for monetary values.
5. Keep API routing, schemas, models and business logic clearly separated.
6. Use Alembic for schema changes instead of relying on ad hoc production DDL.
7. Keep secrets out of source control.
8. Use Redis for measured performance or temporary-state requirements, not as a replacement for durable financial storage.
9. Use background jobs when work should not block an API response.
10. Add load balancing, cloud services and additional infrastructure when the architecture or operational requirements justify them.
11. Test behavior and failure cases, not only successful requests.
12. Update this blueprint after verified milestones and significant architectural changes.

## 7. Working method for each feature

Follow this workflow throughout the project:

1. Define the requirement and acceptance criteria.
2. Understand the data model and API contract.
3. Create a Git feature branch when the repository is ready.
4. Implement a small piece of functionality.
5. Add tests.
6. Run the application and verify the behavior.
7. Review the code and address errors.
8. Open and review a pull request.
9. Merge after checks pass.
10. Update the blueprint and mark the milestone complete.

The assistant should explain the purpose of each file and tool, provide code in manageable sections, and avoid replacing hands-on implementation with large unexplained code dumps.

## 8. Immediate next actions

Resume from Stage 3.1.

1. Confirm `alembic` is installed and `expense.py` exists.
2. Confirm the Expense model and its registration are implemented.
3. Initialize Alembic if it has not been initialized.
4. Configure Alembic to load `DATABASE_URL` and `Base.metadata`.
5. Generate and inspect the initial migration.
6. Apply the migration to the Docker PostgreSQL database on host port `5433`.
7. Verify that the `expenses` table exists.
8. Build and test the first database-backed expense endpoints.

Do not mark Stage 3 complete merely because the model file exists; the migration and endpoints must also work.

## 9. Continuation instructions for a future conversation

When continuing this project, use this document as the authoritative project plan.

First, identify the current stage and the last verified milestone. Ask for or inspect the current files and command output when necessary. Do not assume planned work has been completed.

Preserve the user's hands-on learning approach: explain the purpose of each component, give small tasks, review their implementation, and debug errors before advancing.

Update the roadmap when a milestone is verified. Keep the current stage, completed work, next task and any changes to the architecture accurate.

**Immediate continuation:** Stage 3.1 — Expense model and Alembic setup. The last confirmed working checkpoint is the FastAPI database health endpoint returning HTTP 200 against PostgreSQL.