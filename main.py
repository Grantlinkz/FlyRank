from contextlib import asynccontextmanager
from typing import Optional, List
from fastapi import FastAPI, Response, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

import database

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager to initialize database and tables on startup."""
    database.init_db()
    yield

app = FastAPI(
    title="FlyRank To-Do Task API",
    version="1.0.0",
    description="A modern, Spec-Driven RESTful To-Do CRUD API built with Python, FastAPI, and SQLite for the FlyRank Internship Backend Track.",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
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
    description="Computes total, completed, and open task count metrics from SQLite database.",
    tags=["Extras"]
)
def get_stats():
    """Compute task statistics from database."""
    stats = database.get_task_stats()
    return StatsResponse(**stats)

@app.post(
    "/reset",
    summary="Reset Task Database",
    description="Restores the SQLite database to the original 3 sample tasks. Useful for testing and demos.",
    tags=["Extras"]
)
def reset_tasks():
    """Reset database table to default 3 sample tasks."""
    tasks = database.reset_db()
    return {"message": "Database reset to default 3 sample tasks", "tasks": tasks}

@app.get(
    "/tasks",
    response_model=List[Task],
    summary="List All Tasks / Filter Tasks",
    description="Retrieves a list of tasks from SQLite with optional filtering by completion status (`done`) or title search keyword (`search`).",
    tags=["Tasks"]
)
def get_tasks(
    done: Optional[bool] = Query(None, description="Filter tasks by completion status (true/false)"),
    search: Optional[str] = Query(None, description="Search term to filter task titles (case-insensitive)")
):
    """List tasks from database with optional done status filtering and search query."""
    return database.get_all_tasks(done=done, search=search)

@app.get(
    "/tasks/{id}",
    response_model=Task,
    summary="Get Task by ID",
    description="Retrieves a single task object from SQLite by its unique numerical ID.",
    tags=["Tasks"]
)
def get_task(id: int):
    """Retrieve a single task by ID from database or return 404 if not found."""
    task = database.get_task_by_id(id)
    if task:
        return task
    return JSONResponse(
        status_code=404,
        content={"error": f"Task {id} not found"}
    )

@app.post(
    "/tasks",
    status_code=201,
    response_model=Task,
    summary="Create New Task",
    description="Creates a new task in SQLite. Requires a non-empty `title`. Automatically assigns next available ID and sets `done=False`.",
    tags=["Tasks"]
)
def create_task(payload: TaskCreate):
    """Create a new task in database with input validation."""
    if not payload.title or not payload.title.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Title is required and cannot be empty"}
        )
    
    new_task = database.create_task(payload.title)
    return new_task

@app.put(
    "/tasks/{id}",
    response_model=Task,
    summary="Update Task by ID",
    description="Updates a task's `title` and/or `done` status in SQLite. Returns 404 if task doesn't exist, or 400 if title is invalid.",
    tags=["Tasks"]
)
def update_task(id: int, payload: TaskUpdate):
    """Update a task's title and/or done status in database."""
    existing_task = database.get_task_by_id(id)
    if not existing_task:
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

    updated_task = database.update_task(id, title=payload.title, done=payload.done)
    return updated_task

@app.delete(
    "/tasks/{id}",
    status_code=204,
    summary="Delete Task by ID",
    description="Removes a task from SQLite by ID. Returns 204 No Content on success, or 404 Not Found if missing.",
    tags=["Tasks"]
)
def delete_task(id: int):
    """Delete a task by ID from database."""
    deleted = database.delete_task(id)
    if not deleted:
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {id} not found"}
        )
        
    return Response(status_code=204)
