# System Architecture

The Campus Lost and Found application is a full-stack web app designed for a university campus. It uses a modular Flask backend, a Vite + React frontend, and a PostgreSQL database hosted on Supabase.

---

## High-Level Overview

- **Frontend**: Vite + React SPA deployed on Vercel.
- **Backend**: Flask application (Gunicorn) deployed on Render.
- **Database**: PostgreSQL on Supabase, accessed via SQLAlchemy and `psycopg2-binary`.
- **Auth**: JWT (access + refresh) with HTTP-only cookies, rotation, and a blocklist.
- **Email**: SMTP integration with console fallback for development.

---

## Backend: Modular Flask

The backend lives in `backend/app/` and uses the **Application Factory Pattern**:

- Entry point: `create_app` in `app/__init__.py`.
- Configuration: `app/config/config.py` using environment variables.
- Database: SQLAlchemy and raw SQL helpers over Supabase PostgreSQL.
- Deployed on Render with Gunicorn.

### Layers

| Layer      | Location            | Responsibility                                                |
| ---------- | ------------------- | ------------------------------------------------------------- |
| Routes     | `app/routes/`       | Thin API controllers; handle HTTP requests and responses      |
| Services   | `app/services/`     | Business logic (auth, claims, scoring, matching, scheduling)  |
| Models     | `app/models/`       | Data access; raw SQL helpers for users, items, claims, tokens |
| Utils      | `app/utils/`        | Shared helpers (email, user helpers, responses, safety)       |
| Config     | `app/config/`       | Environment-based configuration objects                       |
| Extensions | `app/extensions.py` | Flask extensions: JWT, Limiter, SQLAlchemy                    |

### Request Flow

1. **HTTP request** hits a route (e.g. `POST /api/auth/login` → `auth_routes.login`).
2. **Route** validates the JSON structure (`require_json_fields`) and delegates to a service.
3. **Service** applies business rules and calls model functions to read/write the database.
4. **Models** execute parameterized SQL via `db.session.execute(text(...))`.
5. Service returns a result payload and status code to the route.
6. Route wraps the result in a JSON response (`success_response` / `error_response`).
7. Global error handlers provide consistent JSON for uncaught exceptions.

---

## Backend Security

### Authentication and Tokens

- JWTs issued by Flask-JWT-Extended:
  - **Access token**: short-lived.
  - **Refresh token**: longer-lived, used for rotation.
- Stored in HTTP-only cookies (`JWT_TOKEN_LOCATION = ["headers", "cookies"]`).
- Custom claims:
  - `role`: `user` or `admin`.
  - `auth_time`: absolute login time, used to enforce session timeout.

### Token Rotation and Blocklist

- **Refresh Token Rotation (RTR)**:
  - Each `POST /auth/refresh` call consumes the refresh token cookie.
  - New access and refresh tokens are issued.
  - The old refresh token's `jti` is inserted into `token_blocklist`.
- **Blocklist enforcement**:
  - `@jwt.token_in_blocklist_loader` checks `token_blocklist` on every request.
  - Absolute session timeout enforced via `auth_time` and `SESSION_ABSOLUTE_TIMEOUT_HOURS`.

### Passwords and Validation

- **Password hashing**: `bcrypt` in `auth_service` and `user_helpers`.
- **Strength validation**:
  - Regex checks for uppercase, lowercase, digit, and special character.
  - `zxcvbn` scoring with a minimum score enforced.
- **Email validation**:
  - `email-validator` checks syntax and MX records.
  - Disposable domains blocked via a custom list.

### Rate Limiting

Implemented via Flask-Limiter in `app/extensions.py`:

| Endpoint                | Limit              |
| ----------------------- | ------------------ |
| Global default          | 100 per 15 minutes |
| `POST /auth/register`   | 3 per 15 minutes   |
| `POST /auth/login`      | 10 per 15 minutes  |
| `POST /auth/forgot-password` | 3 per hour    |
| `POST /auth/reset-password`  | 5 per hour    |
| `POST /auth/refresh`    | 5 per minute       |

### CORS and Security Headers

- **CORS**: Configured via `flask-cors` in `create_app`. `CORS_ORIGINS` is read from the environment as a comma-separated list.
- **Security headers** (set on every response):
  - `X-Frame-Options: DENY`
  - `X-Content-Type-Options: nosniff`
  - `Strict-Transport-Security: max-age=31536000; includeSubDomains`

---

## Frontend: Vite + React

The frontend lives in `frontend/` and is a single-page application deployed on Vercel.

### Key Design Choices

- **Build system**: Vite for fast dev server and optimized production builds.
- **State management**: React hooks and context for authentication and UI state.
- **API client**: Centralized Axios instance in `src/services/api.js`. Base URL is configurable via environment variable:

  ```js
  const API_BASE_URL =
    import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api';
  ```

- **Authentication**: Relies on HTTP-only cookies set by the backend. On `401` responses, an interceptor attempts `POST /auth/refresh` and retries the request. On refresh failure, it clears local storage and redirects to login.

### Deployment

| Setting          | Value                                        |
| ---------------- | -------------------------------------------- |
| Platform         | Vercel                                       |
| Framework preset | Vite                                         |
| Root directory   | `frontend`                                   |
| Build command    | `npm run build`                              |
| Output directory | `dist`                                       |
| `VITE_API_BASE_URL` | `https://lost-nd-found.onrender.com/api`  |

---

## Database: Supabase PostgreSQL

The schema is defined in `backend/migrations/schema.sql` and applied via `init_db()` on startup.

### Core Tables

| Table             | Purpose                                                               |
| ----------------- | --------------------------------------------------------------------- |
| `users`           | User accounts, roles, email verification, lockout, and password reset |
| `lost_items`      | Lost item reports (user-submitted)                                    |
| `found_items`     | Found item reports                                                    |
| `claims`          | Claims linking users to items, with scores and decisions              |
| `activity_logs`   | High-level admin/user actions                                         |
| `audit_logs`      | Detailed audit trail of sensitive actions (e.g. approvals)            |
| `token_blocklist` | Revoked JWT tokens (by `jti`)                                         |

### Initialization

- `app/models/base.py` — `init_db()`:
  - Reads `backend/migrations/schema.sql`.
  - Splits on `;` and executes each statement via `db.session`.
  - Called inside `create_app`'s application context on startup.

### Supabase and Networking

- The direct DB host is IPv6-only and not reachable from Render.
- A Supabase **session pooler** URI is used instead:
  ```
  postgresql://<user>:<password>@<pooler-host>:5432/postgres
  ```
- This URI is provided via the `DATABASE_URL` environment variable.

---

## Email and Zero-Cost Strategy

Email sending is handled in `app/utils/email_service.py`.

- **Primary send path**: Uses `smtplib` with SMTP credentials from environment variables.
- **Zero-cost fallback**: If SMTP is not configured or sending fails, emails are logged to the console instead. Applies to:
  - Verification emails (`send_verification_email`)
  - Password reset emails (`send_password_reset_email`)

This allows development and demos without requiring a paid email service.

---

## Error Handling and Logging

Global error handlers are registered in `app/__init__.py`:

| Exception type     | Behavior                                    |
| ------------------ | ------------------------------------------- |
| `ValidationError`  | Returns `400` with a JSON error message     |
| `HTTPException`    | Returns JSON instead of default HTML        |
| Generic `Exception`| Logs stack trace, returns `SERVER_ERROR`    |

Logging uses Python's `logging` module throughout:

- `models.base` — schema initialization
- `models.items`, `models.claims` — DB errors
- `models.audit` — failures in audit logging
- `utils.email_service` — SMTP and console email logs

---

## Summary

| Concern           | Approach                                                                 |
| ----------------- | ------------------------------------------------------------------------ |
| Security          | JWT cookies, token rotation, strong passwords, rate limiting, validation |
| Maintainability   | Clear separation into routes, services, models, and utilities            |
| Deployability     | Render + Vercel + Supabase with environment-driven configuration         |
| Cost              | Free-tier services; console email logging when SMTP is not configured    |

---

## Deployment Overview

```text
User Browser
    │
    ▼
Vercel (Frontend)
frontend/        ← Vite + React, calls API via Axios
    │
    │ HTTP (JSON API)
    ▼
Render (Backend)
backend/         ← Flask + Gunicorn
    │
    │ PostgreSQL over psycopg2
    ▼
Supabase
PostgreSQL (session pooler, IPv4-compatible)
```
