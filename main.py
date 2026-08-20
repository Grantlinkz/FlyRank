from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(
    title="Task API",
    version="1.0",
    description="A simple To-Do CRUD API built with FastAPI"
)

class Task(BaseModel):
    id: int
    title: str
    done: bool

# In-memory storage pre-filled with 3 example tasks
tasks_db: list[Task] = [
    Task(id=1, title="Learn HTTP & REST basics", done=True),
    Task(id=2, title="Build CRUD API with FastAPI", done=False),
    Task(id=3, title="Test endpoints in Swagger UI", done=False),
]

@app.get("/")
def get_root():
    """Return API metadata description."""
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

@app.get("/health")
def get_health():
    """Return server health status."""
    return {"status": "ok"}

@app.get("/tasks")
def get_tasks():
    """List all tasks in memory."""
    return tasks_db

@app.get("/tasks/{id}")
def get_task(id: int):
    """Retrieve a single task by ID or return 404 if not found."""
    for task in tasks_db:
        if task.id == id:
            return task
    return JSONResponse(
        status_code=404,
        content={"error": f"Task {id} not found"}
    )
