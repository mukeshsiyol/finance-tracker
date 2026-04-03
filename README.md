# Finance Tracker API

A Python-based finance tracking backend built with **FastAPI**, **SQLAlchemy**, and **SQLite**. Supports full CRUD on financial records, role-based access control, and analytics endpoints.

---

## Features

- 🔐 JWT Authentication (Access + Refresh tokens)
- 👥 Role-based access control (Viewer, Analyst, Admin)
- 💰 Transaction management (CRUD + filters + pagination)
- 📊 Analytics (summary, category breakdown, monthly trends)
- 📁 Export data (CSV & JSON)
- 🧪 Automated testing with pytest

## Tech Stack

| Layer        | Choice              | Reason                                          |
|--------------|---------------------|-------------------------------------------------|
| Framework    | FastAPI             | Modern, async-ready, auto-generates Swagger docs |
| ORM          | SQLAlchemy 2.x      | Pythonic, supports multiple databases            |
| Database     | SQLite              | Zero-config, perfect for local/test setups       |
| Auth         | JWT (python-jose)   | Stateless, easy to test                          |
| Validation   | Pydantic v2         | Built into FastAPI, fast and declarative         |
| Passwords    | passlib + bcrypt    | Industry-standard password hashing               |

---

## Project Structure

```
finance_tracker/
├── app/
│   ├── main.py              # FastAPI app, middleware, router registration
│   ├── database.py          # SQLAlchemy engine, session, Base
│   ├── models.py            # ORM models: User, Transaction
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── dependencies.py      # JWT helpers, role-based dependency factories
│   ├── routers/
│   │   ├── auth.py          # /auth — register, login, me
│   │   ├── transactions.py  # /transactions — CRUD + filters
│   │   ├── analytics.py     # /analytics — summary, categories, monthly, dashboard
│   │   └── users.py         # /users — admin user management
│   └── services/
│       ├── auth_service.py          # Password hashing, user registration/auth
│       ├── transaction_service.py   # Transaction CRUD + filtering logic
│       ├── analytics_service.py     # Summary, category breakdown, monthly totals
│       └── user_service.py          # User CRUD + role updates
├── seed.py                  # Populates demo users and 60 transactions
└── requirements.txt
```

---

## Setup & Running

### 1. Clone the repository

```bash
git clone https://github.com/mukeshsiyol/finance-tracker.git
cd finance-tracker
```

### 2. Create and activate a virtual environment

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
# Defaults work for local dev — no changes needed to get started
```

| Variable              | Default                            | Description                                      |
|-----------------------|------------------------------------|--------------------------------------------------|
| `SECRET_KEY`          | *(auto-generated in development)*  | Secret key used to sign JWT tokens (**set in production**) |
| `TOKEN_TTL_MINUTES`   | `60`                               | Access token expiry time (in minutes)            |
| `DATABASE_URL`        | `sqlite:///./finance_tracker.db`   | Database connection string (any SQLAlchemy URL)  |

### 5. Seed demo data

```bash
python seed.py
```

Creates three users and 60 randomised transactions:

| Username | Password   | Role    |
|----------|------------|---------|
| admin    | admin123   | admin   |
| analyst  | analyst123 | analyst |
| viewer   | viewer123  | viewer  |

### 6. Run the server

```bash
uvicorn app.main:app --reload
```

| URL | Description |
|-----|-------------|
| `http://localhost:8000` | Custom landing page |
| `http://localhost:8000/docs` | Swagger UI — interactive testing |
| `http://localhost:8000/redoc` | ReDoc documentation |

---

## API Overview

### Authentication

| Method | Endpoint         | Description            | Role Required |
|--------|------------------|------------------------|---------------|
| POST   | `/auth/register` | Register a new user    | Public        |
| POST   | `/auth/login`    | Get JWT token          | Public        |
| GET    | `/auth/me`       | View current user info | Any           |

**Login flow:**

```bash
# 1. Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Returns: { "access_token": "<jwt>", "token_type": "bearer" }

# 2. Use token in subsequent requests
curl http://localhost:8000/transactions/ \
  -H "Authorization: Bearer <jwt>"
```

---

### Transactions

| Method | Endpoint               | Description                  | Role Required |
|--------|------------------------|------------------------------|---------------|
| GET    | `/transactions/`       | List (with optional filters) | viewer+       |
| GET    | `/transactions/{id}`   | Get single transaction       | viewer+       |
| POST   | `/transactions/`       | Create transaction           | admin         |
| PATCH  | `/transactions/{id}`   | Update transaction           | admin         |
| DELETE | `/transactions/{id}`   | Delete transaction           | admin         |

**Filter parameters** (analyst and admin only):

| Param        | Example                    | Description                        |
|--------------|----------------------------|------------------------------------|
| `type`       | `?type=expense`            | Filter by income or expense        |
| `category`   | `?category=rent`           | Partial category name match        |
| `start_date` | `?start_date=2025-01-01`   | Records from this date             |
| `end_date`   | `?end_date=2025-12-31`     | Records up to this date            |
| `skip`       | `?skip=0`                  | Pagination offset (default 0)      |
| `limit`      | `?limit=50`                | Max records returned (default 50)  |

**Create transaction example:**

```json
{
  "amount": 45000.00,
  "type": "income",
  "category": "Salary",
  "date": "2025-03-01",
  "notes": "March salary credit"
}
```

---

### Analytics

| Method | Endpoint                  | Description                              | Role Required |
|--------|---------------------------|------------------------------------------|---------------|
| GET    | `/analytics/summary`      | Total income, expenses, balance          | viewer+       |
| GET    | `/analytics/categories`   | Per-category breakdown by type           | analyst+      |
| GET    | `/analytics/monthly`      | Monthly income/expense/net totals        | analyst+      |
| GET    | `/analytics/dashboard`    | Full dashboard (all of the above)        | analyst+      |

**Summary response example:**

```json
{
  "total_income": 240000.00,
  "total_expenses": 87500.00,
  "current_balance": 152500.00,
  "total_records": 60,
  "income_records": 20,
  "expense_records": 40
}
```

---

### Users (Admin Only)

| Method | Endpoint               | Description             |
|--------|------------------------|-------------------------|
| GET    | `/users/`              | List all users          |
| GET    | `/users/{id}`          | Get user by ID          |
| PATCH  | `/users/{id}/role`     | Update a user's role    |
| DELETE | `/users/{id}`          | Delete a user           |

---

## Role-Based Access Summary

| Feature                        | Viewer | Analyst | Admin |
|--------------------------------|:------:|:-------:|:-----:|
| View transactions              | ✅     | ✅      | ✅    |
| Filter transactions            | ❌     | ✅      | ✅    |
| Create/Update/Delete records   | ❌     | ❌      | ✅    |
| View summary                   | ✅     | ✅      | ✅    |
| Category & monthly analytics   | ❌     | ✅      | ✅    |
| Dashboard                      | ❌     | ✅      | ✅    |
| Manage users                   | ❌     | ❌      | ✅    |

---

## Data Model

### User

| Field         | Type    | Notes                              |
|---------------|---------|------------------------------------|
| id            | integer | Primary key                        |
| username      | string  | Unique, 3–50 chars                 |
| email         | string  | Unique, valid email format         |
| password_hash | string  | bcrypt-hashed                      |
| role          | enum    | viewer / analyst / admin           |
| created_at    | datetime| Auto-set on creation               |

### Transaction

| Field      | Type    | Notes                                   |
|------------|---------|-----------------------------------------|
| id         | integer | Primary key                             |
| amount     | float   | Must be positive                        |
| type       | enum    | income or expense                       |
| category   | string  | Auto-titlecased on input                |
| date       | date    | YYYY-MM-DD                              |
| notes      | string  | Optional, max 500 chars                 |
| user_id    | integer | Foreign key → users.id                  |
| created_at | datetime| Auto-set on creation                    |
| updated_at | datetime| Auto-updated on modification            |

---

## Running Tests

```bash
pip install pytest httpx
pytest -v
```

All tests use an **in-memory SQLite database** — no setup required, nothing left on disk after a run.

| File                    | What it covers                                   |
|-------------------------|--------------------------------------------------|
| `test_auth.py`          | Register, login, /me, token validation           |
| `test_transactions.py`  | CRUD, filters, pagination, role enforcement      |
| `test_analytics.py`     | Summary values, category %, monthly totals       |
| `test_users.py`         | Admin user management and self-action guards     |
| `test_export.py`        | CSV/JSON download, filter params, role checks    |

---

## Export

Download filtered transaction records as a file.

| Method | Endpoint      | Format | Role Required |
|--------|---------------|--------|---------------|
| GET    | `/export/csv` | CSV    | analyst+      |
| GET    | `/export/json`| JSON   | analyst+      |

```bash
# Download all transactions as CSV
curl http://localhost:8000/export/csv \
  -H "Authorization: Bearer <token>" --output transactions.csv

# Filtered JSON — expenses only, date range
curl "http://localhost:8000/export/json?type=expense&start_date=2025-01-01" \
  -H "Authorization: Bearer <token>" --output expenses.json
```

---

## Assumptions Made

1. **Transactions are user-scoped** — each user can access only their own records, while admins can view all data.

2. **Roles are assigned at registration** — in production this would be admin-only. For this assignment, the role can optionally be passed in the register payload.

3. **SQLite is used for persistence** — easy to run locally without any DB server setup. Switching to PostgreSQL requires only changing the `SQLALCHEMY_DATABASE_URL` in `database.py`.

4. **JWT secret key** — is loaded from environment variables (with a fallback for development).

5. **Filtering is restricted to analyst+ roles** — viewers can see all data but cannot narrow results. This mirrors a dashboard where standard users see curated summary views.

---

## Validation & Error Handling

- `amount` must be a positive float — `422 Unprocessable Entity` if violated
- `category` is auto-sanitized (trimmed + titlecased)
- Duplicate username or email on register → `409 Conflict`
- Wrong credentials → `401 Unauthorized`
- Accessing a restricted route → `403 Forbidden`
- Fetching a non-existent record → `404 Not Found`
- Partial update with no fields → `400 Bad Request`
- Admin cannot change their own role or delete their own account → `400 Bad Request`

All error responses follow the standard FastAPI shape:
```json
{ "detail": "Human-readable error message." }
```
