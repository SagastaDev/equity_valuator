# 📊 Equity Valuation System — Technical Architecture Document

## Overview

This project is a modular, self-hosted equity valuation system built with FastAPI and React. It is designed for internal use with optional multi-user support. The system processes financial data from different providers, transforms it into a standardized format, and uses it to compute equity valuations.

## 🎯 Goals

- Asynchronous, high-performance API with FastAPI
- Modular data transformation layer with provider/company/time-specific mapping rules
- Admin-managed field mappings and transformation formulas
- Support for one-time bulk imports and live data updates
- Secure user authentication and role-based access control
- Clean separation of backend, database, and frontend
- Fully dockerized and self-hosted on a Linux cloud server

---

## 📁 Project Structure

```
/project-root
│
├── backend
│   ├── main.py
│   ├── config.py
│   ├── auth/
│   │   ├── routes.py
│   │   ├── models.py
│   │   └── utils.py
│   ├── db/
│   │   ├── base.py
│   │   ├── session.py
│   │   ├── models/
│   │   │   ├── company.py
│   │   │   ├── field.py
│   │   │   ├── provider.py
│   │   │   ├── mapping.py
│   │   │   ├── user.py
│   │   │   ├── valuation.py
│   │   │   ├── changelog.py
│   │   │   └── price.py
│   ├── routes/
│   │   ├── valuation.py
│   │   ├── transform.py
│   │   └── providers.py
│   ├── services/
│   │   ├── transform_engine.py
│   │   └── formula_evaluator.py
│   └── schemas/
│       └── *.py (Pydantic models)
│
├── frontend (React)
│   └── [React App with schema editor and data mapper UI]
│
├── docker-compose.yml
├── Dockerfile
└── README.md
```

---

## ⚙️ Tech Stack

| Component     | Technology          |
| ------------- | ------------------- |
| Backend       | FastAPI (async)     |
| Auth          | JWT + FastAPI Users |
| ORM           | SQLAlchemy          |
| DB            | PostgreSQL          |
| Frontend      | React + TypeScript  |
| Styling       | TailwindCSS         |
| Deployment    | Docker + Compose    |
| Reverse Proxy | NGINX               |

---

## 🔐 Roles & Access

- **Admin**: Can create/edit providers, field mappings, and formulas.
- **Viewer**: Can view valuations only. Cannot modify data.

Role-based access is implemented with JWT and route guards. All routes are protected by dependency-injected role checks.

---

## 📄 Models (defined per file)

### Industry

- `id`: int
- `code`: string (unique)
- `name`: string
- `description`: string (nullable)

### Company

- `id`: UUID
- `ticker`: string
- `name`: string
- `country`: string
- `currency`: string
- `industry_id`: FK → Industry

### CanonicalField

- `id`: int
- `code`: int
- `name`: str (e.g., "cash\_flow")
- `display_name`: str
- `type`: str
- `category`: enum("fundamental", "market", "ratio")
- `is_computed`: bool

### Provider

- `id`: int
- `name`: str

### RawDataEntry

- `id`: UUID
- `provider_id`: FK
- `company_id`: FK → Company
- `fiscal_period`: date
- `period_type`: enum("annual", "quarterly")
- `raw_field_name`: string
- `value_type`: enum("number", "string", "list", "object")
- `value`: JSONB (can store float, string, list, or object)
- `upload_id`: FK

### MappedField

Defines how a raw field maps to a canonical field, optionally scoped to company and period:

- `id`: UUID
- `provider_id`: FK
- `canonical_id`: FK → CanonicalField
- `raw_field_name`: string
- `company_id`: FK (nullable)
- `start_date`: date (nullable)
- `end_date`: date (nullable)
- `transform_expression`: JSON (nullable, structured formula expression)

### ValuationResult

- `id`: UUID
- `company_id`: FK
- `as_of`: date
- `user_id`: FK
- `results`: JSONB (dictionary of field\_name → value)

### PriceData

- `id`: UUID
- `company_id`: FK
- `provider_id`: FK
- `date`: date
- `period_type`: enum("daily", "weekly", "monthly", "minute", "second")
- `open`: float
- `close`: float
- `adj_close`: float
- `volume`: int

### User

- `id`: int
- `email`: string
- `hashed_password`: string
- `role`: enum("admin", "viewer")
- `avatar_url`: string (nullable)

### ChangeLog

- `id`: int
- `provider_field_id`: FK → MappedField
- `user_id`: FK → User
- `timestamp`: datetime
- `change_description`: str

---

## 🧠 Formula Engine

- All formulas are structured in JSON format for safety and clarity
- Backend uses a secure evaluator (like `asteval`)
- Frontend may use `math.js` for preview
- Arbitrary Python code is strictly prohibited
- `transform_expression` is nullable

Example:

```json
{
  "target_field": "debt_ratio",
  "expression": {
    "op": "divide",
    "args": [
      { "field": "total_liabilities" },
      { "field": "total_assets" }
    ]
  }
}
```

---

## 🧰 Frontend Features

- CSV/JSON uploader
- Left/right field mapping UI
- Formula editor with validation
- Mapping and formula persistence
- View-only dashboard for final users

---

## 🚀 Deployment

- Use Docker for API, Postgres, and frontend
- Gunicorn + Uvicorn workers for FastAPI
- NGINX as reverse proxy
- Compose config to manage services

---

## 📌 Next Steps

-

