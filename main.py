from fastapi import FastAPI

app = FastAPI(
    title="Task API",
    version="1.0",
    description="A simple To-Do CRUD API built with FastAPI"
)

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
