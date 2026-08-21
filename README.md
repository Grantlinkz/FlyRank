# FlyRank To-Do CRUD API — Supabase Auth & JWT Security Stack

A modern, Spec-Driven RESTful CRUD API built with Python 3.10+, FastAPI, Pydantic, PostgreSQL, Docker Compose, and Supabase Auth for the FlyRank Internship Backend Track (Week 4 Assignment A4).

---

## Features

- **Supabase Auth Identity Provider**: Account creation, credential verification, and JSON Web Token (JWT) issuance fully delegated to Supabase Auth.
- **Zero Local Cryptography**: Server code never touches plain or hashed passwords, following security best practices.
- **JWT Bearer Verification Middleware**: Reusable FastAPI security dependency (`get_current_user`) verifying Bearer tokens on protected endpoints.
- **Precise Status Code & JSON Error Shapes**:
  - `201 Created` on signup.
  - `200 OK` on login & profile lookup.
  - `204 No Content` on logout.
  - `400 Bad Request` with `{ "error": "Email and password are required" }` on missing inputs.
  - `401 Unauthorized` with `{ "error": "Access token required" }` or `{ "error": "Invalid or expired token" }` on auth failures.
- **Interactive Swagger UI Authorize Padlock**: Configured OpenAPI `HTTPBearer` security scheme allowing direct authentication testing from `http://localhost:8000/docs`.
- **Public & Protected Gates**: Public lobby endpoint (`GET /public/info`) alongside user-protected endpoints (`GET /protected/profile`, `POST /auth/logout`).

---

## Environment Setup & Secrets

Authentication secrets are managed via environment variables.

1. Copy `.env.example` to `.env` (git-ignored):
   ```bash
   cp .env.example .env
   ```

2. Configure your Supabase project credentials in `.env`:
   ```env
   DATABASE_URL=postgresql://postgres:dev@localhost:5432/tasks
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_KEY=your-supabase-anon-key
   ```

---

## Endpoint Reference Table

| Category | HTTP Method | Endpoint | Auth Required | Status Codes | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Public Gate** | `GET` | `/public/info` | None | `200` | Public open endpoint returning welcome message |
| **User Auth** | `POST` | `/auth/signup` | None | `201`, `400` | Registers user account via Supabase Auth |
| **User Auth** | `POST` | `/auth/login` | None | `200`, `400`, `401` | Authenticates credentials and returns JWT `access_token` |
| **User Auth** | `POST` | `/auth/logout` | Bearer Token | `204`, `401` | Ends user session in Supabase Auth |
| **Protected Profile**| `GET` | `/protected/profile` | Bearer Token | `200`, `401` | Returns verified user profile metadata |
| **Metadata** | `GET` | `/` | None | `200` | API metadata and endpoint index |
| **Health Probe** | `GET` | `/health` | None | `200` | Liveness check |
| **Task CRUD** | `GET`, `POST`, `PUT`, `DELETE` | `/tasks`, `/tasks/{id}` | None | `200`, `201`, `204`, `400`, `404` | PostgreSQL-backed task management |

---

## Using Swagger UI Bearer Authorization (`/docs`)

FastAPI renders an interactive Swagger UI documentation interface with built-in Bearer authentication support:

1. Open `http://localhost:8000/docs` in your browser.
2. Execute `POST /auth/login` with your credentials and copy the returned `access_token`.
3. Click the **Authorize** padlock button at the top right of Swagger UI.
4. Paste the `access_token` into the Value field and click **Authorize**.
5. All protected endpoints (`GET /protected/profile`, `POST /auth/logout`) can now be tested directly from the browser!

---

## Hand-Executed `curl` Commands

### 1. Register User Account (`POST /auth/signup`)
```bash
curl -i -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'
```

### 2. Login to Obtain Access Token (`POST /auth/login`)
```bash
curl -i -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'
```

### 3. Call Protected Profile Endpoint (`GET /protected/profile`)
```bash
curl -i http://localhost:8000/protected/profile \
  -H "Authorization: Bearer <PASTE_ACCESS_TOKEN_HERE>"
```

### 4. Tampered Token Rejection Test (`401 Unauthorized`)
```bash
curl -i http://localhost:8000/protected/profile \
  -H "Authorization: Bearer invalid.tampered.token"
# Returns 401 Unauthorized: { "error": "Invalid or expired token" }
```

---

## AI Rematch ("AI vs Me") — Stage 7 Security Audit Report

As required by Stage 7 of Assignment A4, an AI assistant was prompted in quarantine (`ai-version/main.py`) to implement Supabase authentication for comparison:

### 1. Full AI Prompt Used
> *"Write a FastAPI application integrated with Supabase Auth to handle `/auth/signup`, `/auth/login`, `/auth/logout`, and `/protected/profile`. Enforce JWT token verification via a reusable Bearer security dependency, configure OpenAPI HTTPBearer for Swagger UI, and return strict JSON error messages for missing tokens and invalid credentials."*

### 2. Three Concrete Security Differences Found

| Category | Hand-Crafted Code (`auth.py` + `main.py`) | AI-Generated Code (`ai-version/`) |
| :--- | :--- | :--- |
| **Token Extraction Safety** | Uses FastAPI `HTTPBearer(auto_error=False)` and cleanly extracts token string, returning `{ "error": "Access token required" }` for missing/malformed headers. | Used raw `Header(None)` and executed `authorization.split(" ")[1]`, causing uncaught `IndexError` / server 500 when malformed headers were sent. |
| **Error Contract Adherence** | Intercepts all Supabase and auth errors to return exact standard JSON (`400 Bad Request`, `401 Unauthorized`). | Allowed raw Supabase exceptions to bubble up as internal server errors or default FastAPI `422` / `500` detail shapes. |
| **Reusable Dependency Architecture** | Encapsulates token verification in `auth.get_current_user` dependency module, easily reusable across any protected route. | Embedded inline header checks inside individual route functions, creating repetitive code and risk of unverified endpoints. |

### 3. Key Takeaway
Security logic must handle invalid, malformed, and tampered inputs gracefully at the boundary without exposing tracebacks or crashing the server thread.
