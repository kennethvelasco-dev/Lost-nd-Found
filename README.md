# Campus Lost & Found System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![Standard: Senior Engineer Checklist](https://img.shields.io/badge/Standard-Senior%20Engineer%20Checklist-gold.svg)](#production-readiness)

> **Production-Ready Backend Core (v1.1.0)**
> A robust, secure, and professionally architected backend for managing campus lost and found items, featuring intelligent scoring, rate limiting, and RBAC.

---

## 🚀 Key Features

### 🛡️ Security & Authentication
- **Strong Auth**: JWT-based authentication with secure cookie/header support and token revocation.
- **RBAC**: Multi-tiered Role-Based Access Control (Admin, User) for all sensitive operations.
- **Rate Limiting**: Brute-force protection on authentication and reporting endpoints via Flask-Limiter.
- **Data Protection**: Parameterized SQL queries and strict input validation prevent injection attacks.

### 🧩 Core Functionality
- **Dual Reporting**: Dedicated pipelines for reporting Lost and Found items.
- **Intelligent Scoring**: Weighted matching engine that ranks claims based on field accuracy.
- **Claim Lifecycle**: Full management from submission and matching to admin approval and handover.
- **Audit Trails**: Global activity logging for tracking system changes and user actions.

### 🏛️ Architecture
- **Service Layer Pattern**: Decoupled business logic from routes for maximum testability.
- **App Factory Pattern**: Clean application initialization including dynamic extension loading.
- **Isolated Testing**: Robust testing suite with automated database state management.

---

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.8 or higher
- `pip` and `virtualenv`

### Installation

1. **Clone & Setup Environment**
   ```bash
   git clone <repo-url>
   cd LostnFound
   python -m venv backend/venv
   
   # Windows:
   .\backend\venv\Scripts\activate
   # Mac/Linux:
   source backend/venv/bin/activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Environment Configuration**
   Copy `.env.example` to `.env` and configure your secret keys:
   ```bash
   cp backend/.env.example backend/.env
   ```

---

## 🧪 Testing

The backend uses a structured `pytest` suite divided into logical categories:

```bash
# Run the complete test suite (from project root)
# The system automatically handles temporary test database creation.
pytest tests/
```

### Test Categories
| Category | Location | Description |
| :--- | :--- | :--- |
| **Unit** | `tests/unit/` | Core matching logic and utility functions. |
| **Integration** | `tests/integration/` | End-to-end API flows (Auth, Claims, Items). |
| **Security** | `tests/security/` | IDOR prevention, concurrency, and RBAC checks. |

---

## 📖 API Documentation

Detailed endpoint specifications, request envelopes, and response structures are available in the [**API Spec**](./API_SPEC.md).

### Quick Reference
- `POST /api/auth/register` - User/Admin onboarding.
- `POST /api/auth/login` - JWT generation.
- `POST /api/items/found` - Report found item.
- `POST /api/claims/submit` - File a claim/report.
- `POST /api/admin/claims/<id>/verify` - Admin verification (Approve/Reject).

---

## 📂 Project Structure

```text
.
├── backend/
│   ├── routes/          # API Controllers (Blueprints)
│   ├── services/        # Business Logic & Scoring Engine
│   ├── models/          # Data Access Layer & DB Schema
│   ├── helpers/         # Shared Utilities & Validations
│   ├── config/          # Environment Configurations
│   ├── extensions.py    # Global Flask Extensions (JWT, Limiter)
│   └── __init__.py      # App Factory
├── tests/
│   ├── unit/            # Isolated Logic Tests
│   ├── integration/     # API Flow Tests
│   └── security/        # Access Control & Concurrency
├── API_SPEC.md          # Detailed Endpoint Documentation
└── requirements.txt     # Dependency Management
```

---

## 🏆 Production Readiness
This project fulfills the **Senior Engineer 20-Point Backend Checklist**, including:
- [x] Standardized JSON response envelopes.
- [x] Global exception handling (Production vs. Test mode).
- [x] Timezone-aware UTC datetime management.
- [x] Automated Resource Cleanup (Try-Finally DB enclosure).
- [x] No raw SQL concatenation.
