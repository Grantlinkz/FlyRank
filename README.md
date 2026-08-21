# FlyRank To-Do CRUD API — SQLite Database Persistence

A modern, Spec-Driven RESTful CRUD API built with Python 3.10+, FastAPI, Pydantic, and SQLite for the FlyRank Internship Backend Track (Week 3 Assignment A2).

---

## Features

- **SQLite Persistent Storage**: Task data is stored on disk in a lightweight SQLite database (`tasks.db`), surviving application restarts.
- **Repository Architecture Pattern**: Database access code is fully isolated in `database.py`, keeping FastAPI route handlers clean and decoupled.
- **Idempotent Auto-Initialization**: Automatically creates `tasks.db` and the `tasks` schema on startup, seeding initial sample data **only when empty** (seed-once rule).
- **Strict Parameterized SQL Queries**: All database operations use SQL placeholders (`?`) to prevent SQL injection vulnerabilities.
- **Standardized RESTful Endpoints**: Full CRUD operations (`GET`, `POST`, `PUT`, `DELETE`) adhering to precise HTTP status code semantics (`200`, `201`, `204`, `400`, `404`).
- **Interactive OpenAPI Documentation**: Built-in Swagger UI documentation hosted automatically at `http://localhost:8000/docs`.
- **SQL-Powered Extras**: Server-side filtering (`?done=true`), title pattern search (`?search=keyword` with SQL `LIKE`), direct SQL metrics (`GET /stats`), and database state reset (`POST /reset`).

---

## Why SQLite?

SQLite was chosen for this storage layer migration because:
1. **Zero Configuration**: SQLite requires no separate background database server process, installation, or administration.
2. **Single-File Simplicity**: The entire relational database lives inside one local file (`tasks.db`).
3. **True Persistence**: Unlike in-memory data structures, disk writes ensure task data survives server shutdowns and restarts.
4. **Git Isolation**: `tasks.db` is listed in `.gitignore` so every repository clone starts fresh with automatic database creation on first run.

---

## Quickstart & Installation

### Prerequisites

- Python 3.10+ installed on your system.

### Running the Application

1. Clone or navigate to the repository directory:
   ```bash
   cd FlyRank
   ```

2. Start the Uvicorn dev server (single command):
   ```bash
   python -m uvicorn main:app --reload --port 8000
   ```
   > *On startup, `tasks.db` will be created automatically if missing and seeded with 3 default tasks.*

3. Open your browser to test interactive Swagger UI docs:
   ```
   http://localhost:8000/docs
   ```

---

## Endpoint Reference Table

| CRUD Operation | HTTP Method | Endpoint | Status Codes | SQL Query Shape | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Metadata** | `GET` | `/` | `200` | — | Returns API name, version, and primary endpoint list |
| **Health Probe** | `GET` | `/health` | `200` | — | Liveness check returning `{"status": "ok"}` |
| **Read (List)** | `GET` | `/tasks` | `200` | `SELECT * FROM tasks WHERE ...` | List all tasks. Supports SQL filtering via `?done=true/false` & `?search=term` |
| **Read (Single)**| `GET` | `/tasks/{id}` | `200`, `404` | `SELECT * FROM tasks WHERE id = ?` | Retrieve a single task by ID |
| **Create** | `POST` | `/tasks` | `201`, `400` | `INSERT INTO tasks (title, done) VALUES (?, 0)` | Create new task with title validation |
| **Update** | `PUT` | `/tasks/{id}` | `200`, `400`, `404` | `UPDATE tasks SET title = ?, done = ? WHERE id = ?` | Update task title and/or done completion status |
| **Delete** | `DELETE` | `/tasks/{id}` | `204`, `404` | `DELETE FROM tasks WHERE id = ?` | Remove task by ID |
| **Stats** | `GET` | `/stats` | `200` | `SELECT COUNT(*) FROM tasks ...` | Returns total, completed, and open task metrics |
| **Reset** | `POST` | `/reset` | `200` | `DELETE FROM tasks; INSERT INTO ...` | Resets database to default sample tasks |

---

## Hand-Executed SQL Queries (Stage 4 Exploration)

Using **DB Browser for SQLite** (or the SQLite CLI), the database file (`tasks.db`) can be opened directly to execute queries by hand. The API and DB Browser operate on the exact same single source of truth.

```sql
-- 1. List every task in the database
SELECT * FROM tasks;

-- 2. List only completed tasks
SELECT * FROM tasks WHERE done = 1;

-- 3. Count total tasks stored
SELECT COUNT(*) FROM tasks;

-- 4. Mark all tasks as completed
UPDATE tasks SET done = 1;

-- 5. Clean up completed tasks
DELETE FROM tasks WHERE done = 1;
```

---

## AI Rematch ("AI vs Me") — Stage 6 Report

As required by Stage 6 of Assignment A2, an AI assistant was prompted in quarantine (`ai-version/main.py`) to migrate the in-memory CRUD API to SQLite for comparison against the hand-crafted codebase:

### 1. Full AI Prompt Used
> *"Write a FastAPI application using SQLite (`sqlite3`) to persist a To-Do task API. Create a `tasks` table with `id`, `title`, and `done`. Seed initial tasks on startup, enforce non-empty title validation on `POST /tasks`, use parameterized SQL queries, and return standard JSON error responses."*

### 2. Three Concrete Differences Found

| Category | Hand-Crafted Code (`database.py` + `main.py`) | AI-Generated Code (`ai-version/main.py`) |
| :--- | :--- | :--- |
| **Seed-Once Idempotency** | Checks `SELECT COUNT(*) FROM tasks` before inserting default records. Restarts preserve existing user data without duplication. | Calls `INSERT` on every startup without checking existing row count, causing duplicate seed tasks on every server restart. |
| **Error Handling & Contracts** | Returns standard HTTP `400 Bad Request` with custom `{ "error": "Title is required..." }` JSON shape. | Raised generic `HTTPException(400)` or relied on default FastAPI `422 Unprocessable Entity`, breaking client error shape contracts. |
| **Architecture & Separation** | Implements clean Repository pattern separating SQL queries (`database.py`) from FastAPI route logic (`main.py`). | Embedded direct `sqlite3.connect()` calls inside route handlers, mixing storage, connection management, and HTTP routing logic. |

### 3. Prompt Specification Takeaway
AI outputs strictly mirror prompt precision. Specifying architectural patterns (Repository layer), exact HTTP status codes (`400` vs `422`), error JSON schemas, and row count checks for seed idempotency are necessary to avoid silent design compromises.
