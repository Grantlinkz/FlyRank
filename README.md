# FlyRank To-Do CRUD API — Python FastAPI Lane

A modern, Spec-Driven RESTful CRUD API built with Python 3.10+, FastAPI, and Pydantic for the FlyRank Internship Backend Track (Week 2 Assignment A1).

---

## Features

- **Standardized RESTful Endpoints**: Full CRUD operations for managing tasks in memory (`GET`, `POST`, `PUT`, `DELETE`).
- **Strict Status Code Semantics**: Precise HTTP response codes (`200 OK`, `201 Created`, `204 No Content`, `400 Bad Request`, `404 Not Found`).
- **Input Validation**: Rejects empty payloads or missing required fields (`title`) with clear JSON error responses (`{ "error": "..." }`).
- **Interactive OpenAPI Documentation**: Built-in Swagger UI documentation hosted automatically at `http://localhost:8000/docs`.
- **Extras & Query Extensions**: Filtering by status (`?done=true`), title search (`?search=keyword`), live metrics (`GET /stats`), and instant state reset (`POST /reset`).

---

## Quickstart & Installation

### Prerequisites

- Python 3.10+ installed on your system.

### Running the API

1. Clone or navigate to the repository directory:
   ```bash
   cd FlyRank
   ```

2. Run the server using Uvicorn (single command):
   ```bash
   python -m uvicorn main:app --reload --port 8000
   ```

3. Open your browser to test interactive Swagger UI docs:
   ```
   http://localhost:8000/docs
   ```

---

## Endpoint Reference Table

| CRUD Operation | HTTP Method | Endpoint | Status Codes | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Metadata** | `GET` | `/` | `200` | Returns API name, version, and primary endpoint list |
| **Health Probe** | `GET` | `/health` | `200` | Liveness check returning `{"status": "ok"}` |
| **Read (List)** | `GET` | `/tasks` | `200` | List all tasks. Supports `?done=true/false` & `?search=term` |
| **Read (Single)**| `GET` | `/tasks/{id}` | `200`, `404` | Retrieve a single task by ID |
| **Create** | `POST` | `/tasks` | `201`, `400` | Create new task with title validation (`done` defaults to `false`) |
| **Update** | `PUT` | `/tasks/{id}` | `200`, `400`, `404` | Update task title and/or done completion status |
| **Delete** | `DELETE` | `/tasks/{id}` | `204`, `404` | Remove task by ID |
| **Stats** | `GET` | `/stats` | `200` | Returns total, completed, and open task count metrics |
| **Reset** | `POST` | `/reset` | `200` | Resets in-memory database to default sample tasks |

---

## Verified Sample Terminal Output (`curl -i`)

### 1. Root & Health Check (`GET /`, `GET /health`)
```http
HTTP/1.1 200 OK
content-type: application/json

{
  "name": "Task API",
  "version": "1.0",
  "endpoints": ["/tasks"]
}
```

### 2. Create Task (`POST /tasks`)
```http
HTTP/1.1 201 Created
content-type: application/json

{
  "id": 4,
  "title": "Buy milk",
  "done": false
}
```

### 3. Create Task Validation Error (`POST /tasks` with empty title)
```http
HTTP/1.1 400 Bad Request
content-type: application/json

{
  "error": "Title is required and cannot be empty"
}
```

### 4. Single Task Lookup Not Found (`GET /tasks/99`)
```http
HTTP/1.1 404 Not Found
content-type: application/json

{
  "error": "Task 99 not found"
}
```

### 5. Delete Task (`DELETE /tasks/1`)
```http
HTTP/1.1 204 No Content
```

---

## In-Memory Storage & The Mortality Experiment

This API stores task records in Python in-memory data structures (`tasks_db`). 

> [!NOTE]
> **Observation**: Creating new tasks or updating existing tasks mutates the state in memory. However, restarting the Uvicorn server processes resets the application state back to the initial sample tasks.
> **Why this matters**: In-memory storage is fast and zero-config for development, but volatile. This observation is the primary motivation for Week 3's milestone: connecting the CRUD API to persistent SQLite and containerized PostgreSQL databases.

---

## Bonus: AI Rematch ("AI vs Me")

As part of the FlyRank curriculum Stage 7 AI Rematch protocol, an AI assistant was prompted to independently generate the same FastAPI CRUD API in an isolated `ai-version/` module for comparison:

1. **What the AI did well**:
   - Fast initial endpoint scaffolding using FastAPI routing decorators.
   - Used Pydantic schemas out of the box for JSON parsing.
2. **What the AI missed or got wrong**:
   - Returned FastAPI default `422 Unprocessable Entity` for empty title validation instead of the strict required business rule `400 Bad Request` with custom `{ "error": "..." }` JSON shape.
   - Failed to handle empty/whitespace string validation (`title=""`) without explicit string trimming logic.
   - Omitted custom endpoint tag groupings and detailed OpenAPI field examples in Swagger UI.
3. **Prompt precision takeaways**:
   - Explicitly naming required error status codes (`400` vs `422`) and error response schemas in system prompts is critical for exact specification adherence.
