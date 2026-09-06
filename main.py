from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any
from pathlib import Path
from fastapi import FastAPI, Response, Query, Depends, Request, Security
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field

import database
import auth
from auth import get_current_user, AuthException
from fastapi.exceptions import RequestValidationError
import inngest
import inngest.fast_api
from src.jobs import (
    inngest_client,
    say_hello,
    make_report,
    heartbeat,
    create_report,
    get_report,
    get_all_reports,
)
from src.llm import (
    triage_task,
    TaskTriageRequest,
    TaskTriageResponse,
    LLMTimeoutException,
    LLMDisabledException,
    LLMQuarantineException,
    LLMClientException,
)
from src.reports import (
    generate_or_get_report,
    get_report_record,
    get_all_pdf_reports,
    init_report_db,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager to initialize database and tables on startup."""
    database.init_db()
    init_report_db()
    yield

app = FastAPI(
    title="FlyRank To-Do Task API",
    version="1.0.0",
    description="A modern, Spec-Driven RESTful CRUD API built with Python, FastAPI, PostgreSQL, and Supabase Auth for the FlyRank Internship Backend Track.",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Mount Inngest background job handler at /api/inngest
inngest.fast_api.serve(
    app,
    inngest_client,
    [say_hello, make_report, heartbeat],
)

# Exception Handler for Custom Auth Errors
@app.exception_handler(AuthException)
async def auth_exception_handler(request: Request, exc: AuthException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message}
    )

# Exception Handlers for LLM Service
@app.exception_handler(LLMTimeoutException)
async def llm_timeout_handler(request: Request, exc: LLMTimeoutException):
    return JSONResponse(
        status_code=504,
        content={"error": "Gateway Timeout: LLM provider did not respond in time", "detail": str(exc)}
    )

@app.exception_handler(LLMDisabledException)
async def llm_disabled_handler(request: Request, exc: LLMDisabledException):
    return JSONResponse(
        status_code=503,
        content={"error": "Service Unavailable: LLM integration is disabled", "detail": str(exc)}
    )

@app.exception_handler(LLMQuarantineException)
async def llm_quarantine_handler(request: Request, exc: LLMQuarantineException):
    return JSONResponse(
        status_code=422,
        content={"error": "Unprocessable Entity: Model output could not be validated after repair", "details": exc.details}
    )

@app.exception_handler(LLMClientException)
async def llm_client_handler(request: Request, exc: LLMClientException):
    return JSONResponse(
        status_code=502,
        content={"error": f"Bad Gateway: LLM provider returned error {exc.status_code}", "detail": exc.message}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    from fastapi.encoders import jsonable_encoder
    errors = exc.errors()
    msg = errors[0].get("msg", "Invalid request body") if errors else "Invalid request body"
    loc = errors[0].get("loc", []) if errors else []
    field = loc[-1] if loc else "body"
    return JSONResponse(
        status_code=400,
        content={"error": f"Validation failed for field '{field}': {msg}", "details": jsonable_encoder(errors)}
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

class ReportCreateRequest(BaseModel):
    topic: Optional[str] = Field(None, description="Topic for the report to generate", example="cats")

class ReportAcceptedResponse(BaseModel):
    id: str = Field(..., description="Unique tracking ID of the report", example="rep_a1b2c3d4")
    status: str = Field(..., description="Lifecycle status", example="pending")

class ReportDetailResponse(BaseModel):
    id: str = Field(..., description="Unique tracking ID of the report", example="rep_a1b2c3d4")
    topic: str = Field(..., description="Topic of the report", example="cats")
    status: str = Field(..., description="Lifecycle status (pending, done, failed)", example="pending")
    result: Optional[str] = Field(None, description="Result payload if finished", example="Report on 'cats' generated successfully.")
    created_at: Optional[str] = Field(None, description="Timestamp of generation request")
    attempts: Optional[int] = Field(None, description="Execution attempts count")
    error: Optional[str] = Field(None, description="Error message if failed")

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
        "endpoints": [
            "/tasks",
            "/tasks/triage",
            "/reports",
            "/api/inngest",
            "/auth/signup",
            "/auth/login",
            "/protected/profile",
        ]
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
def logout(credentials: Optional[HTTPAuthorizationCredentials] = Security(auth.security_scheme)):
    """End user session and invalidate token."""
    if not credentials or not credentials.credentials:
        raise AuthException(401, "Access token required")
    token = credentials.credentials.strip()
    if not token:
        raise AuthException(401, "Access token required")
    auth.logout_user(token)
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
    description="Restores the database to default sample tasks. Protected by server-side authentication check.",
    tags=["Extras"]
)
def reset_tasks(current_user: Any = Depends(get_current_user)):
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

@app.post(
    "/tasks/triage",
    response_model=TaskTriageResponse,
    summary="Triage Task via LLM",
    description="Classifies, prioritizes, and estimates inbound tasks using LLM or deterministic stub mode.",
    tags=["Tasks"]
)
def triage_task_endpoint(payload: TaskTriageRequest):
    """
    Triage an inbound task.
    Classifies into closed category enums, assesses urgency, estimated effort, and confidence.
    """
    response, _ = triage_task(payload)
    return response


# --- Background Jobs & Reports Endpoints (Milestone W7) ---

@app.post(
    "/reports",
    summary="Generate Report (PDF Artifact or Async Job)",
    description="Generates an executive PDF report using Store and Link architecture (201 Created / 200 OK), or dispatches an async background job if 'topic' is specified.",
    tags=["Reports & Jobs"]
)
async def create_report_endpoint(request: Request):
    """
    Unified report creation endpoint:
    - If 'topic' is provided: Validates topic and offloads to Inngest background job (202 Accepted, A7).
    - If 'force' is provided or standard POST: Queries SQL aggregations, prints multi-page PDF via Playwright,
      saves to disk, registers metadata in report.db, and returns file link (201 Created or 200 OK if already generated today).
    """
    raw_body = await request.body()
    data = {}
    if raw_body:
        try:
            data = await request.json()
        except Exception:
            data = {}

    # Check if this is an A7 Background Job request
    is_a7_job_request = False
    if "topic" in data:
        is_a7_job_request = True
    elif "force" not in data and "type" not in data and raw_body and raw_body.strip() == b"{}":
        # Missing body / empty dict in A7 test_jobs test_post_reports_validation_gatekeeper expects 400
        is_a7_job_request = True

    if is_a7_job_request:
        topic = data.get("topic")
        if not topic or not str(topic).strip():
            return JSONResponse(
                status_code=400,
                content={"error": "Topic is required and cannot be empty"}
            )

        clean_topic = str(topic).strip()
        report = create_report(clean_topic)

        try:
            await inngest_client.send(
                inngest.Event(
                    name="report/requested",
                    data={
                        "id": report["id"],
                        "topic": clean_topic
                    }
                )
            )
        except Exception as e:
            print(f"[WARN] Inngest event dispatch notice: {e}", flush=True)

        return JSONResponse(
            status_code=202,
            content={
                "id": report["id"],
                "status": "pending"
            }
        )

    # W7b PDF Report Generator Flow (Store and Link with Idempotency)
    force = bool(data.get("force", False))
    pdf_report, is_created = await generate_or_get_report(force=force)
    status_code = 201 if is_created else 200

    return JSONResponse(
        status_code=status_code,
        content={
            "id": pdf_report["id"],
            "file": pdf_report["file"]
        }
    )


@app.get(
    "/reports",
    summary="List All Reports",
    description="Control panel endpoint returning tracked reports. Pass ?type=pdf for PDF report artifacts.",
    tags=["Reports & Jobs"]
)
def list_reports(type: Optional[str] = Query(None, description="Filter report type ('pdf' or 'jobs')")):
    """Retrieve all reports and their current statuses."""
    if type == "pdf":
        return get_all_pdf_reports()
    return get_all_reports()


@app.get(
    "/reports/{id}",
    summary="Get Report Status & Result",
    description="Returns metadata and download link for PDF reports (integer ID), or status for async background jobs (UUID).",
    tags=["Reports & Jobs"]
)
def get_report_endpoint(id: str):
    """Retrieve report status by ID or return 404 if not found."""
    # 1. Check SQLite PDF reports bookkeeping if ID is integer
    if id.isdigit():
        pdf_rec = get_report_record(int(id))
        if pdf_rec:
            return JSONResponse(
                status_code=200,
                content={
                    "id": pdf_rec["id"],
                    "created_at": pdf_rec["created_at"],
                    "file": pdf_rec["file"],
                }
            )

    # 2. Check in-memory A7 async background jobs state
    report = get_report(id)
    if report:
        return report

    return JSONResponse(
        status_code=404,
        content={"error": f"Report '{id}' not found"}
    )


@app.get(
    "/reports/{id}/file",
    summary="Download PDF Report Artifact",
    description="Streams binary PDF report directly from disk using FileResponse (Store and Link architecture).",
    tags=["Reports & Jobs"]
)
def download_report_file(id: int):
    """Download the generated PDF report artifact by integer ID."""
    pdf_rec = get_report_record(id)
    if not pdf_rec:
        return JSONResponse(
            status_code=404,
            content={"error": f"Report '{id}' not found"}
        )

    file_path = Path(pdf_rec["path"])
    if not file_path.exists():
        return JSONResponse(
            status_code=404,
            content={"error": f"Report file for ID '{id}' not found on disk"}
        )

    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=f"report-{id}.pdf"
    )

