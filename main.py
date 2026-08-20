from typing import Optional
from fastapi import FastAPI, Response, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

app = FastAPI(
    title="FlyRank To-Do Task API",
    version="1.0.0",
    description="A modern, Spec-Driven RESTful To-Do CRUD API built with Python and FastAPI for the FlyRank Internship Backend Track.",
    docs_url="/docs",
    redoc_url="/redoc"
)

# --- Pydantic Models ---

class Task(BaseModel):
    id: int = Field(..., description="Unique identifier of the task", example=1)
    title: str = Field(..., description="Description of the task to perform", example="Learn HTTP & REST basics")
    done: bool = Field(..., description="Completion status of the task", example=False)

class TaskCreate(BaseModel):
    title: Optional[str] = Field(None, description="Title of the new task", example="Buy milk")

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Updated task title", example="Buy organic milk")
    done: Optional[bool] = Field(None, description="Updated completion status", example=True)

class StatsResponse(BaseModel):
    total: int = Field(..., example=5)
    done: int = Field(..., example=2)
    open: int = Field(..., example=3)

# --- In-Memory Storage & Initial Seeds ---

INITIAL_TASKS = [
    Task(id=1, title="Learn HTTP & REST basics", done=True),
    Task(id=2, title="Build CRUD API with FastAPI", done=False),
    Task(id=3, title="Test endpoints in Swagger UI", done=False),
]

tasks_db: list[Task] = [task.model_copy() for task in INITIAL_TASKS]

# --- Route Handlers ---

@app.get(
    "/",
    summary="Get API Root Information",
    description="Returns metadata about the API including its name, version, and primary endpoints.",
    tags=["Metadata"]
)
def get_root():
    """Return API metadata description."""
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

@app.get(
    "/health",
    summary="Health Check Probe",
    description="Returns server operational status for monitoring and liveness probes.",
    tags=["Metadata"]
)
def get_health():
    """Return server health status."""
    return {"status": "ok"}

@app.get(
    "/stats",
    response_model=StatsResponse,
    summary="Get Task Metrics & Statistics",
    description="Computes total, completed, and open task count metrics from memory.",
    tags=["Extras"]
)
def get_stats():
    """Compute task statistics."""
    total = len(tasks_db)
    done_count = sum(1 for t in tasks_db if t.done)
    open_count = total - done_count
    return StatsResponse(total=total, done=done_count, open=open_count)

@app.post(
    "/reset",
    summary="Reset Task Database",
    description="Restores the in-memory database to the original 3 sample tasks. Useful for testing and demos.",
    tags=["Extras"]
)
def reset_tasks():
    """Reset in-memory storage to initial 3 sample tasks."""
    global tasks_db
    tasks_db = [task.model_copy() for task in INITIAL_TASKS]
    return {"message": "Database reset to default 3 sample tasks", "tasks": tasks_db}

@app.get(
    "/tasks",
    summary="List All Tasks / Filter Tasks",
    description="Retrieves a list of tasks with optional filtering by completion status (`done`) or title search keyword (`search`).",
    tags=["Tasks"]
)
def get_tasks(
    done: Optional[bool] = Query(None, description="Filter tasks by completion status (true/false)"),
    search: Optional[str] = Query(None, description="Search term to filter task titles (case-insensitive)")
):
    """List tasks with optional done status filtering and search query."""
    result = tasks_db
    
    if done is not None:
        result = [t for t in result if t.done == done]
        
    if search and search.strip():
        query = search.strip().lower()
        result = [t for t in result if query in t.title.lower()]
        
    return result

@app.get(
    "/tasks/{id}",
    summary="Get Task by ID",
    description="Retrieves a single task object by its unique numerical ID.",
    tags=["Tasks"]
)
def get_task(id: int):
    """Retrieve a single task by ID or return 404 if not found."""
    for task in tasks_db:
        if task.id == id:
            return task
    return JSONResponse(
        status_code=404,
        content={"error": f"Task {id} not found"}
    )

@app.post(
    "/tasks",
    status_code=201,
    summary="Create New Task",
    description="Creates a new task. Requires a non-empty `title`. Automatically assigns next available ID and sets `done=False`.",
    tags=["Tasks"]
)
def create_task(payload: TaskCreate):
    """Create a new task with input validation."""
    if not payload.title or not payload.title.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Title is required and cannot be empty"}
        )
    
    next_id = max([t.id for t in tasks_db], default=0) + 1
    new_task = Task(id=next_id, title=payload.title.strip(), done=False)
    tasks_db.append(new_task)
    return new_task

@app.put(
    "/tasks/{id}",
    summary="Update Task by ID",
    description="Updates a task's `title` and/or `done` status. Returns 404 if task doesn't exist, or 400 if title is invalid.",
    tags=["Tasks"]
)
def update_task(id: int, payload: TaskUpdate):
    """Update a task's title and/or done status."""
    task_idx = None
    for idx, t in enumerate(tasks_db):
        if t.id == id:
            task_idx = idx
            break
            
    if task_idx is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {id} not found"}
        )
        
    if payload.title is not None and not payload.title.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Title cannot be an empty string"}
        )
        
    if payload.title is None and payload.done is None:
        return JSONResponse(
            status_code=400,
            content={"error": "Request body must include at least title or done"}
        )

    current_task = tasks_db[task_idx]
    updated_title = payload.title.strip() if payload.title is not None else current_task.title
    updated_done = payload.done if payload.done is not None else current_task.done

    updated_task = Task(id=id, title=updated_title, done=updated_done)
    tasks_db[task_idx] = updated_task
    return updated_task

@app.delete(
    "/tasks/{id}",
    status_code=204,
    summary="Delete Task by ID",
    description="Removes a task by ID. Returns 204 No Content on success, or 404 Not Found if missing.",
    tags=["Tasks"]
)
def delete_task(id: int):
    """Delete a task by ID."""
    task_idx = None
    for idx, t in enumerate(tasks_db):
        if t.id == id:
            task_idx = idx
            break
            
    if task_idx is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {id} not found"}
        )
        
    tasks_db.pop(task_idx)
    return Response(status_code=204)
