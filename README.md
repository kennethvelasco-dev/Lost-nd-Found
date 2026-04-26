# Campus Lost and Found

A full-stack web application that streamlines the lost-and-found process for university campuses.

- **Backend**: Flask application on Render with PostgreSQL (Supabase session pooler).
- **Frontend**: Vite + React application on Vercel.
- **Auth**: JWT with access/refresh tokens, email verification, and password reset.
- **Security**: bcrypt hashing, password strength checking, rate limiting, validation.

---

## Live URLs

- **Frontend (Vercel)**: `https://lost-nd-found.vercel.app`
- **Backend (Render API)**: `https://lost-nd-found.onrender.com/api`

You normally share the Vercel URL with users. The frontend talks to the backend via HTTP.

---

## Features

- **Lost and Found Reporting**
  - Users can report both lost and found items.
  - Items include category, type, color, brand, locations, timestamps, descriptions, and photos.

- **Claims and Matching**
  - Users can submit claims for found items.
  - A scoring service compares claim answers with item details.
  - Admins can approve, reject, or complete claims and schedule pickups.

- **Admin Dashboard**
  - View pending item reports and claims.
  - Approve or reject reports and claims.
  - Mark items as returned and view dashboard statistics.

- **Return Logs (User-Facing)**
  - `/returned-items`: list of successful returns available to authenticated users.
  - `/returns/:id`: detailed audit view per released item, including:
    - Original report photo and handover proof photo.
    - Claimant name and student/recipient ID.
    - Admin username and admin office ID.
    - Handover notes and item metadata (category, type, color, brand, locations).

- **Authentication and Security**
  - Username/password login with bcrypt.
  - Automatic email verification on registration (Zero-Cost strategy).
  - Password reset via email link (mocks logged to console in dev).
  - Access and refresh tokens with rotation and a token blocklist.
  - Rate limiting on sensitive endpoints (login, register, reset, etc.).

- **Architecture**
  - Flask application factory (`create_app`) with blueprints for auth, items, claims, and admin.
  - Service layer (`app/services/`) for business logic.
  - Raw SQL via SQLAlchemy for models and migrations.
  - Single schema file (`backend/migrations/schema.sql`) initializes all tables.

---

## Project Structure

```text
root/
│
├── frontend/                     # Vite + React frontend (Vercel)
│   ├── src/
│   │   ├── components/           # UI components
│   │   ├── pages/                # React pages
│   │   └── services/             # API client (axios)
│   ├── public/
│   └── .env.example              # Frontend env template
│
├── backend/                      # Flask backend (Render)
│   ├── app/
│   │   ├── routes/               # Blueprints (auth, items, claims, admin, health)
│   │   ├── services/             # Business logic (auth_service, claim_service, scoring_service, etc.)
│   │   ├── models/               # DB access helpers (users, items, claims, audit, validators, auth)
│   │   ├── utils/                # Helpers (email_service, user_helpers, production_safety, response)
│   │   ├── config/               # Config objects and environment handling
│   │   ├── extensions.py         # Flask extensions (JWT, limiter, SQLAlchemy)
│   │   └── __init__.py           # Flask app factory, error handlers, security headers
│   ├── migrations/
│   │   └── schema.sql            # Database schema (users, items, claims, logs, token_blocklist)
│   ├── requirements.txt          # Python dependencies
│   ├── .env.example              # Backend env template
│   └── gunicorn.conf.py          # Gunicorn config for Render
│
├── docs/
│   ├── API.md
│   └── ARCHITECTURE.md
│
├── README.md
└── .gitignore
```

---

## Backend

### Technologies

- Python `3.10+`
- Flask `3.x`
- Flask-JWT-Extended
- Flask-Limiter
- Flask-SQLAlchemy / SQLAlchemy `2.x`
- `psycopg2-binary` (PostgreSQL driver)
- Supabase Postgres via session pooler (IPv4-compatible) as the primary database host (no Supabase Auth or storage; the backend owns the `users`, `items`, `claims`, and `released_items` tables).
- `bcrypt` for password hashing
- `email-validator` and `zxcvbn` for email and password strength checks
- `python-dotenv` for configuration

### Local Setup

From the project root:

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

Copy the environment template:

```bash
cp .env.example .env
# On Windows, create .env manually and copy the values
```

Configure at minimum:

```env
FLASK_ENV=development
JWT_SECRET_KEY=<random-value>
FLASK_SECRET_KEY=<random-value>
```

And either:

- Set `DATABASE_URL` to your Supabase session pooler URI, **or**
- Leave `DATABASE_URL` unset to fall back to a local SQLite file (`lostnfound.db`).

Run the backend:

```bash
flask run
```

By default the API listens on `http://localhost:5000`.

### Deployment (Render)

**Service settings:**

| Setting        | Value                                          |
| -------------- | ---------------------------------------------- |
| Root directory | `backend`                                      |
| Build command  | `pip install -r requirements.txt`              |
| Start command  | `gunicorn "app:create_app()" -b 0.0.0.0:$PORT` |

**Required environment variables on Render:**

```env
FLASK_ENV=production
FLASK_SECRET_KEY=<random-value>
JWT_SECRET_KEY=<random-value>
DATABASE_URL=postgresql://postgres.<ref>:<password>@aws-1-ap-southeast-2.pooler.supabase.com:5432/postgres
FRONTEND_URL=https://lost-nd-found.vercel.app
CORS_ORIGINS=http://localhost:3000,https://lost-nd-found.vercel.app
```

**Optional SMTP email configuration:**

```env
SMTP_SERVER=
SMTP_PORT=
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_USE_TLS=
SMTP_FROM_EMAIL=
```

> **Note**: If SMTP is not configured, emails are logged to the backend console instead of being sent.

---

## Frontend

### Technologies

- Node.js `18+`
- Vite
- React
- Axios

### Local Setup

From the project root:

```bash
cd frontend
npm install
```

Copy the environment template:

```bash
cp .env.example .env
# or manually create .env
```

Set the API base URL if you want to override the default:

```env
VITE_API_BASE_URL=http://localhost:5000/api
```

The Axios client in `src/services/api.js` uses:

```js
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:5000/api";
```

Run the frontend:

```bash
npm run dev
```

Vite serves the app at `http://localhost:5173` by default.

### Deployment (Vercel)

**Project configuration:**

| Setting          | Value           |
| ---------------- | --------------- |
| Framework preset | Vite            |
| Root directory   | `frontend`      |
| Build command    | `npm run build` |
| Output directory | `dist`          |

**Environment variable on Vercel:**

```env
VITE_API_BASE_URL=https://lost-nd-found.onrender.com/api
```

The deployed frontend will then call the Render backend.

---

## Authentication Flow

### Registration

1. User registers with username, email, password, and role.
2. Backend validates input, enforces strong passwords, and hashes the password.
3. An email verification token is generated and emailed (or logged to console in development).

### Email Verification

1. In this deployment, accounts are automatically verified upon registration to ensure a zero-cost, friction-less developer experience.
2. An email verification token is still generated and logged to the backend console (mock email).
3. If manual verification were enabled:
   - The verification link points to `FRONTEND_URL/verify-email?token=...`.
   - The frontend calls `GET /api/auth/verify-email` with that token.
   - On success, the account is marked as verified.

### Login

1. User logs in with username and password.
2. Failed attempts are tracked; excessive failures cause a temporary lockout.
3. On success, short-lived access and refresh tokens are created and set in HTTP-only cookies.

### Token Refresh

1. When an access token expires, the frontend calls `POST /api/auth/refresh`.
2. The backend validates the refresh token, issues new tokens, rotates the refresh token, and blocklists the old one.

### Logout

- `POST /api/auth/logout` clears JWT cookies and revokes the current token.

---

## Database Schema

The schema is defined in `backend/migrations/schema.sql` and includes:

| Table             | Description                                                                   |
| ----------------- | ----------------------------------------------------------------------------- |
| `users`           | Users with roles, email verification, lockout, and password reset fields      |
| `lost_items`      | Lost item reports with status, descriptions, and reporter                     |
| `found_items`     | Found item reports with status, descriptions, and reporter                    |
| `claims`          | Claims linking users to items, with scoring, decisions, and pickup info       |
| `released_items`  | Snapshot record of resolved items with claimant info, pictures, and locations |
| `activity_logs`   | Logging admin and system actions                                              |
| `audit_logs`      | Audit trail for sensitive operations                                          |
| `token_blocklist` | JWT blocklist table                                                           |

On startup, `init_db()` executes `schema.sql` against the configured database.

---

## Running the Full Stack Locally

Start the backend:

```bash
cd backend
flask run
# Serves the API at http://localhost:5000
```

Start the frontend:

```bash
cd frontend
npm run dev
# Serves the UI at http://localhost:5173
```

Ensure `VITE_API_BASE_URL` points to `http://localhost:5000/api` during local development (via `.env` or the default in `api.js`).

Then:

- Visit `http://localhost:5173` to use the app locally.
- Visit `https://lost-nd-found.vercel.app` to use the deployed app.

---

## Documentation

- [API Specification](docs/API.md)
- [System Architecture](docs/ARCHITECTURE.md)
<!-- CI trigger -->
