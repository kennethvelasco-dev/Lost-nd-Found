# Campus Lost & Found System

> **Production-Ready Backend Core (v1.0.0)**
> A robust, secure, and testable backend for managing lost and found items with claim scoring and admin verification.

---

## 🚀 Features

### Core Functionality

- **User Authentication**: JWT-based Register, Login, Refresh, Logout.
- **Item Management**: Post Lost & Found items with detailed attributes.
- **Claims System**: specific validation logic (`receipt_proof`, `declared_value`) and status tracking.
- **Scoring Engine**: Intelligent matching of claims against found items using weighted rules.
- **Admin Dashboard**: Verification workflow for pending claims.
- **Audit Logging**: Comprehensive activity trail for security and compliance.

### Technical Highlights

- **Architecture**: Modular Flask application with service layer pattern.
- **Database**: SQLite with normalized schema and migrations.
- **Security**: Password hashing (Argon2/PBKDF2 via Werkzeug), Role-Based Access Control (RBAC).
- **Quality Assurance**: Single-command integration test suite covering full lifecycles.

---

## 🛠️ Setup & Installation

### Prerequisites

- Python 3.8+
- Virtualenv

### Installation

1. **Clone & Setup Environment**

   ```bash
   git clone <repo>
   cd lost-and-found
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

3. **Initialize Database**
   The database is auto-initialized on first run. To seed a default admin:

   ```bash
   # Run the integration test (resets DB and creates admin)
   # Windows (PowerShell):
   $env:PYTHONPATH="." 
   python tests/integration_test.py
   
   # Mac/Linux:
   PYTHONPATH="." python tests/integration_test.py
   ```

   **Default Admin Credentials:**
   - Username: `admin`
   - Password: `adminpassword`

---

## 🧪 Testing

The system features standalone integration test scripts covering complete lifecycles (DB operations, Auth flows, Claim logic, and Admin verification).

```bash
# Run tests from the project root directory

# Windows (PowerShell):
$env:PYTHONPATH="."
python tests/integration_test.py
python backend/test.py

# Mac/Linux:
PYTHONPATH="." python tests/integration_test.py
PYTHONPATH="." python backend/test.py
```

_Expected Output:_ 
- `✅ INTEGRATION TEST PASSED` 
- `✅ FULL QA INTEGRATION TEST COMPLETED SUCCESSFULLY`

---

## 📖 API Documentation

### Authentication

- `POST /api/auth/register` - Create new user account.
- `POST /api/auth/login` - Authenticate and receive JWT.
- `POST /api/auth/refresh` - Refresh access token.
- `POST /api/auth/logout` - Revoke current token.

### Items

- `POST /api/items/lost` - Report a lost item.
- `GET /api/items/found` - View published found items.
- `POST /api/items/found` - Report a found item.

### Claims

- `POST /api/claims/claim` - Submit a claim for a found item.
  - **Required Fields**: `found_item_id`, `description`, `declared_value`, `receipt_proof`.
  - **Optional**: `claimed_brand`, `claimed_color`, etc. (used for scoring).
- `POST /api/admin/claims/<id>/verify` - Approve, Reject, or Complete a claim.
  - **Decisions**: `approved`, `rejected`, `completed`.
  - **Note**: Marking as `completed` updates the found item status to `returned`.

---

## 🧠 Scoring Logic

The system automatically scores claims (0-100) based on field matches against the found item:

| Field           | Weight | Match Type |
| --------------- | ------ | ---------- |
| Private Details | 40%    | Contains   |
| Category        | 30%    | Exact      |
| Item Type       | 25%    | Contains   |
| Brand           | 20%    | Contains   |
| Color           | 15%    | Contains   |
| Location        | 10%    | Contains   |

_Note: Scores are normalized and capped._

---

## 🔒 Security Notes

- **Admin Registration**: Public registration forces `role='user'`. Admins must be seeded or created via database access.
- **Token Revocation**: Logout adds JTI to a revocation list (in-memory for this version).

---

## 📂 Project Structure

```
backend/
├── app.py                  # App entry point
├── services/               # Business logic
│   ├── auth_service.py
│   ├── scoring_service.py  # Core scoring algorithm
│   └── ...
├── routes/                 # API controllers
├── models/                 # DB access & schemas
└── config/                 # Configuration
tests/
└── integration_test.py     # End-to-end user flow test
backend/
└── test.py                 # Full QA integration test (Auth, Claims, DB)
```
