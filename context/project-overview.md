# FlyRank Backend Platform — Project Overview

## Overview

FlyRank is a modular backend platform and developer internship track focused on building production-ready services. The system evolves through spec-driven milestones: establishing RESTful CRUD APIs, adding SQLite and containerized PostgreSQL database persistence, implementing secure identity management via Supabase Auth with JWT middleware, and building an idempotent, fault-tolerant web scraping pipeline for data ingestion.

## Goals

1. **Robust API Foundation**: Deliver standardized RESTful APIs with strict HTTP status code semantics, JSON request/response contracts, and interactive Swagger UI documentation.
2. **Flexible & Secure Persistence**: Transition from in-memory arrays to persistent SQLite (`tasks.db`) and containerized PostgreSQL, utilizing parameterized SQL queries and environment-based secrets.
3. **Identity & Access Control**: Protect system endpoints with Supabase Auth as the Identity Provider, enforcing JWT Bearer token verification via reusable middleware.
4. **Resilient Data Ingestion**: Build an automated, polite data scraping pipeline with request throttling, local HTML caching, Zod/Pydantic schema validation, and structured run reporting.

## Core User Flow

1. **Authentication**: Users sign up (`POST /auth/signup`) and log in (`POST /auth/login`) to receive a JWT access token.
2. **Accessing Protected Resources**: Clients send requests with `Authorization: Bearer <token>` to access private user profiles (`GET /protected/profile`) or execute session teardown (`POST /auth/logout`).
3. **Managing Resources (CRUD)**: Authenticated users manage task and SEO report resources (`GET /tasks`, `POST /tasks`, `PUT /tasks/:id`, `DELETE /tasks/:id`) with persistence across server and container restarts.
4. **Data Scraping & Ingestion**: The system politely fetches external target pages (e.g., Books to Scrape), caches raw HTML locally, extracts and normalizes fields, validates records against schemas, and writes valid outputs to `output/books.json` with a detailed `output/run-report.json`.

## Features

### 1. Core REST API & Swagger UI Documentation
- Health check (`GET /health`) and API metadata (`GET /`) endpoints.
- Full CRUD operations for resource management (`/tasks`, `/tasks/:id`).
- Input validation returning `400 Bad Request` for missing/empty fields.
- Interactive OpenAPI documentation rendered at `/docs` with Bearer auth support.

### 2. Database Persistence & Containerization
- Dual database support: SQLite (`tasks.db`) for lightweight local persistence and PostgreSQL for production-grade workloads.
- Startup auto-creation of database files and tables with first-run seeding logic.
- Single command multi-container orchestration via Docker Compose (`compose.yaml`) with persistent volume mapping (`taskdata`).
- Environment variable management using `.env` for secrets with `.env.example` committed.

### 3. Identity & Token Security
- Supabase Auth integration handling account registration and credential verification.
- Reusable JWT authentication middleware verifying Bearer tokens and injecting user context into requests.
- Endpoint classification: Public (`/public/info`) vs Protected (`/protected/profile`, `/auth/logout`).

### 4. Resilient Scraping Pipeline
- Target classification and `robots.txt` compliance verification.
- Local HTML caching (`cache/`) to avoid repeated network requests.
- Relative-to-absolute URL transformation for discovered pages.
- Data extraction, price normalization (`price_gbp`), and Zod/Pydantic schema validation.
- Non-blocking failure handling: 5xx retry logic, logging and skipping 404/broken pages without halting execution.
- Execution reporting (`output/run-report.json`) tracking timing, cache hits, valid/invalid records, and errors.

## Scope

### In Scope
- Node.js (Express) or Python (FastAPI) REST API endpoints.
- SQLite (`tasks.db`) and PostgreSQL storage layers using parameterized queries.
- Dockerfile and Docker Compose setup for local environment parity.
- Supabase Auth SDK integration and JWT middleware.
- Books to Scrape ingestion pipeline with local file caching and JSON outputs (`output/books.json`).

### Out of Scope
- Custom password hashing or rolling custom cryptography.
- Unthrottled scraping or bypassing website paywalls/logins.
- Complex frontend web applications (backend focus).
- Direct mutation of third-party DOMs or external database schemas.

## Success Criteria

1. **CRUD & Spec Adherence**: Complete CRUD cycle functions via curl and Swagger UI with correct HTTP status codes (200, 201, 204, 400, 401, 404).
2. **Verified Persistence**: Data survives full server and container restarts (`docker compose down && docker compose up`).
3. **Auth Enforcement**: Protected routes successfully reject missing/tampered tokens with `401 Unauthorized` and permit valid tokens with `200 OK`.
4. **Pipeline Resilience**: Scraping pipeline processes 60 unique book records idempotently, handles deliberate 404 failures gracefully, and generates valid `output/run-report.json`.
