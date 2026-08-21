# FlyRank To-Do CRUD API — Containerized PostgreSQL Stack

A modern, Spec-Driven RESTful CRUD API built with Python 3.10+, FastAPI, Pydantic, PostgreSQL, Docker, and Docker Compose for the FlyRank Internship Backend Track (Week 3 Assignment A3).

---

## Features

- **Containerized PostgreSQL Database**: Application persistence is powered by a real PostgreSQL database server running inside a Docker container.
- **One-Command Orchestration**: Full stack (`api` + `db`) is launched with a single command via Docker Compose (`compose.yaml`).
- **Secrets via Environment Variables**: Zero hardcoded database credentials. Sensitive connection strings live in `.env` (git-ignored), while `.env.example` provides the committed template.
- **Persistent Docker Volume**: PostgreSQL data lives in a named Docker volume (`taskdata`), guaranteeing data persistence across full container teardowns (`docker compose down && docker compose up`).
- **Repository Architecture Pattern**: All database interactions, driver logic (`psycopg 3`), and parameterized SQL queries (`%s`) are encapsulated inside `database.py`.
- **Idempotent Auto-Initialization**: Automatically creates the `tasks` schema and seeds default tasks **only when the table is empty** (seed-once rule).
- **Interactive OpenAPI Documentation**: Built-in Swagger UI documentation hosted automatically at `http://localhost:8000/docs`.

---

## Quickstart & Local Execution

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.
- Python 3.10+ (if running locally outside Docker).

### Running the Whole Stack (Single Command)

1. Clone or navigate to the repository directory:
   ```bash
   cd FlyRank
   ```

2. Copy the environment template to create your `.env` file:
   ```bash
   cp .env.example .env
   ```

3. Launch the containerized application and database stack:
   ```bash
   docker compose up --build
   ```

4. Open your browser to test interactive Swagger UI docs:
   ```
   http://localhost:8000/docs
   ```

5. Tear down the stack while keeping stored data intact:
   ```bash
   docker compose down
   ```

---

## Endpoint Reference Table

| CRUD Operation | HTTP Method | Endpoint | Status Codes | PostgreSQL Query Shape | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Metadata** | `GET` | `/` | `200` | — | Returns API name, version, and primary endpoint list |
| **Health Probe** | `GET` | `/health` | `200` | — | Liveness check returning `{"status": "ok"}` |
| **Read (List)** | `GET` | `/tasks` | `200` | `SELECT * FROM tasks WHERE ...` | List all tasks. Supports filtering via `?done=true/false` & `?search=term` |
| **Read (Single)**| `GET` | `/tasks/{id}` | `200`, `404` | `SELECT * FROM tasks WHERE id = %s` | Retrieve a single task by ID |
| **Create** | `POST` | `/tasks` | `201`, `400` | `INSERT INTO tasks (title, done) VALUES (%s, FALSE) RETURNING *` | Create new task with title validation |
| **Update** | `PUT` | `/tasks/{id}` | `200`, `400`, `404` | `UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING *` | Update task title and/or done completion status |
| **Delete** | `DELETE` | `/tasks/{id}` | `204`, `404` | `DELETE FROM tasks WHERE id = %s` | Remove task by ID |
| **Stats** | `GET` | `/stats` | `200` | `SELECT COUNT(*) FROM tasks ...` | Returns total, completed, and open task metrics |
| **Reset** | `POST` | `/reset` | `200` | `DELETE FROM tasks; INSERT INTO ...` | Resets database to default sample tasks |

---

## Database Inspection via `psql`

To inspect the PostgreSQL database inside the running container, execute the interactive `psql` shell:

```bash
# 1. Connect to PostgreSQL inside container
docker exec -it flyrank-db-1 psql -U postgres -d tasks

# 2. Inspect table schema
\dt

# 3. Query task records
SELECT * FROM tasks;
```

---

## AI Rematch ("AI vs Me") — Stage 6 Containerized Stack Report

As required by Stage 6 of Assignment A3, an AI assistant was prompted in quarantine (`ai-version/main.py`) to containerize the task CRUD API onto PostgreSQL:

### 1. Full AI Prompt Used
> *"Write a Docker Compose file and FastAPI application using PostgreSQL (`psycopg`) to persist a To-Do CRUD API. Create a `tasks` table with `id`, `title`, and `done`. Read connection string from `.env`, seed initial tasks on startup, enforce non-empty title validation, use parameterized queries, and configure volume persistence."*

### 2. Three Concrete Differences Found

| Category | Hand-Crafted Code (`compose.yaml` + `database.py`) | AI-Generated Code (`ai-version/`) |
| :--- | :--- | :--- |
| **Volume Persistence & Service Discovery** | Configured `taskdata` named volume mount and database host `db:5432` matching Compose service network name. | Forgot volume configuration or hardcoded `localhost:5432` inside container code, breaking container-to-container networking. |
| **Seed-Once Idempotency** | Checks `SELECT COUNT(*) FROM tasks` before inserting default records. Restarts preserve user data. | Executes `INSERT` on every startup without checking existing row count, causing duplicate seed tasks on every container restart. |
| **Secrets & Security** | Connection string completely decoupled via `.env` (git-ignored) with committed `.env.example` template. | Hardcoded fallback connection string with database password in source code. |

### 3. Takeaways
Containerized multi-service orchestration requires explicit service discovery, volume mapping, health checks, and environment variable management to achieve production parity.
