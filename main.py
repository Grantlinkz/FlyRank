from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Response, Query, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

import database
import auth
from auth import get_current_user, AuthException

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager to initialize database and tables on startup."""
    database.init_db()
    yield

app = FastAPI(
    title="FlyRank To-Do Task API",
    version="1.0.0",
    description="A modern, Spec-Driven RESTful CRUD API built with Python, FastAPI, PostgreSQL, and Supabase Auth for the FlyRank Internship Backend Track.",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Exception Handler for Custom Auth Errors
@app.exception_handler(AuthException)
async def auth_exception_handler(request: Request, exc: AuthException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message}
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

class SignUpRequest(BaseModel):
    email: Optional[str] = Field(None, example="user@example.com")
    password: Optional[str] = Field(None, example="password123")

class LoginRequest(BaseModel):
    email: Optional[str] = Field(None, example="user@example.com")
    password: Optional[str] = Field(None, example="password123")

# --- Metadata & Public Endpoints ---

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
        "endpoints": ["/tasks", "/auth/signup", "/auth/login", "/protected/profile"]
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
    "/public/info",
    summary="Public Gate Information",
    description="Public endpoint accessible by anyone without authentication.",
    tags=["Auth Public"]
)
def get_public_info():
    """Return open public lobby message."""
    return {"message": "Welcome stranger! This info is public."}

# --- Authentication Endpoints ---

@app.post(
    "/auth/signup",
    status_code=201,
    summary="User Registration",
    description="Creates a new user account with email and password via Supabase Auth.",
    tags=["Auth"]
)
def signup(payload: SignUpRequest):
    """Register a new user account with Supabase Auth."""
    if not payload.email or not payload.email.strip() or not payload.password or not payload.password.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Email and password are required"}
        )
        
    try:
        res = auth.supabase.auth.sign_up({
            "email": payload.email.strip(),
            "password": payload.password.strip()
        })
        if not res.user:
            return JSONResponse(
                status_code=400,
                content={"error": "Signup failed. User creation returned empty response."}
            )
        return {
            "message": "User registered successfully",
            "user": {
                "id": res.user.id,
                "email": res.user.email,
                "created_at": str(res.user.created_at)
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"error": str(e)}
        )

@app.post(
    "/auth/login",
    summary="User Login",
    description="Authenticates credentials against Supabase Auth and returns JWT access token.",
    tags=["Auth"]
)
def login(payload: LoginRequest):
    """Authenticate user credentials and return JWT access token."""
    if not payload.email or not payload.email.strip() or not payload.password or not payload.password.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Email and password are required"}
        )
        
    try:
        res = auth.supabase.auth.sign_in_with_password({
            "email": payload.email.strip(),
            "password": payload.password.strip()
        })
        if not res.session or not res.session.access_token:
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid login credentials"}
            )
            
        return {
            "access_token": res.session.access_token,
            "refresh_token": res.session.refresh_token,
            "token_type": "bearer",
            "user": {
                "id": res.user.id,
                "email": res.user.email
            }
        }
    except Exception:
        return JSONResponse(
            status_code=401,
            content={"error": "Invalid login credentials"}
        )

@app.post(
    "/auth/logout",
    status_code=204,
    summary="User Logout",
    description="Ends the user's session in Supabase Auth. Requires Bearer JWT in Authorization header.",
    tags=["Auth Protected"]
)
def logout(current_user: Any = Depends(get_current_user)):
    """End user session and invalidate token."""
    try:
        auth.supabase.auth.sign_out()
    except Exception:
        pass
    return Response(status_code=204)

@app.get(
    "/protected/profile",
    summary="Get Protected User Profile",
    description="Returns private user profile metadata. Protected by Supabase Auth JWT verification dependency.",
    tags=["Auth Protected"]
)
def get_protected_profile(current_user: Any = Depends(get_current_user)):
    """Retrieve protected user profile metadata."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": getattr(current_user, "role", "authenticated"),
        "created_at": str(current_user.created_at)
    }

# --- Task Management Endpoints (CRUD) ---

@app.get(
    "/stats",
    response_model=StatsResponse,
    summary="Get Task Metrics & Statistics",
    description="Computes total, completed, and open task count metrics from database.",
    tags=["Extras"]
)
def get_stats():
    """Compute task statistics from database."""
    stats = database.get_task_stats()
    return StatsResponse(**stats)

@app.post(
    "/reset",
    summary="Reset Task Database",
    description="Restores the database to default sample tasks.",
    tags=["Extras"]
)
def reset_tasks():
    """Reset database table to default sample tasks."""
    tasks = database.reset_db()
    return {"message": "Database reset to default 3 sample tasks", "tasks": tasks}

@app.get(
    "/tasks",
    response_model=List[Task],
    summary="List All Tasks / Filter Tasks",
    description="Retrieves a list of tasks with optional status filtering (`done`) or title search (`search`).",
    tags=["Tasks"]
)
def get_tasks(
    done: Optional[bool] = Query(None, description="Filter tasks by completion status (true/false)"),
    search: Optional[str] = Query(None, description="Search term to filter task titles")
):
    """List tasks from database with optional done status filtering and search query."""
    return database.get_all_tasks(done=done, search=search)

@app.get(
    "/tasks/{id}",
    response_model=Task,
    summary="Get Task by ID",
    description="Retrieves a single task object by its unique numerical ID.",
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
    description="Creates a new task. Requires non-empty `title`.",
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
    description="Updates a task's `title` and/or `done` status. Returns 404 if not found, 400 if invalid.",
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
    description="Removes a task by ID. Returns 204 No Content on success, 404 if not found.",
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
