# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a modular equity valuation system built with FastAPI and designed for self-hosting. The system processes financial data from providers like Yahoo Finance, transforms it into a standardized format, and computes equity valuations. It features user authentication, role-based access control, and a flexible data transformation engine.

## Project Structure

```
/equity_valuator
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py              # Application configuration
│   ├── auth/                  # Authentication system
│   │   ├── routes.py          # Auth endpoints (login, register, token)
│   │   ├── models.py          # Pydantic models for auth
│   │   └── utils.py           # JWT and password utilities
│   ├── db/                    # Database layer
│   │   ├── base.py            # SQLAlchemy base configuration
│   │   ├── session.py         # Database session management
│   │   └── models/            # SQLAlchemy models
│   │       ├── company.py     # Company and Industry models
│   │       ├── field.py       # Canonical field definitions
│   │       ├── provider.py    # Data provider models
│   │       ├── mapping.py     # Field mapping and raw data
│   │       ├── user.py        # User and role models
│   │       ├── valuation.py   # Valuation results
│   │       ├── price.py       # Price data
│   │       └── changelog.py   # Audit trail
│   ├── routes/                # API endpoints
│   │   ├── valuation.py       # Valuation CRUD operations
│   │   ├── transform.py       # Data transformation and mapping
│   │   └── providers.py       # Provider management
│   ├── services/              # Business logic
│   │   ├── transform_engine.py      # Formula evaluation engine
│   │   ├── formula_evaluator.py     # Data transformation service
│   │   └── financial_data_service.py # Yahoo Finance integration
│   └── schemas/               # Pydantic response models
├── frontend/                  # React TypeScript application
│   ├── public/                # Static assets
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   │   ├── Layout.tsx     # Main application layout
│   │   │   └── ProtectedRoute.tsx # Route protection wrapper
│   │   ├── contexts/          # React context providers
│   │   │   └── AuthContext.tsx # Authentication state management
│   │   ├── pages/             # Application pages/routes
│   │   │   ├── Login.tsx      # Authentication page
│   │   │   ├── Dashboard.tsx  # Main dashboard
│   │   │   ├── Valuations.tsx # Company valuations view
│   │   │   ├── Providers.tsx  # Data provider management (admin)
│   │   │   └── Transformations.tsx # Field mapping UI (admin)
│   │   ├── services/          # API service layer
│   │   │   └── auth.ts        # Authentication API calls
│   │   └── App.tsx            # Main application component
│   ├── package.json           # NPM dependencies and scripts
│   ├── tailwind.config.js     # TailwindCSS configuration
│   └── Dockerfile             # Frontend container definition
└── legacy/                    # Legacy files (kept for reference)
    ├── FinancialDataDef.py    # Original financial analysis logic
    ├── YahooDataParser.py     # Original price data parser
    └── FinancesData.ipynb     # Original Jupyter notebook analysis
```

## Tech Stack

- **Backend**: FastAPI (async Python web framework)
- **Frontend**: React 18 with TypeScript and TailwindCSS
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens with bcrypt password hashing
- **Data Sources**: Yahoo Finance (yfinance library)
- **Development**: Uvicorn ASGI server + React dev server with hot reload
- **Deployment**: Docker Compose with NGINX reverse proxy

## Key Features

### Authentication & Authorization
- JWT-based authentication
- Role-based access control (Admin, Viewer)
- Admin users can create/edit providers, field mappings, and formulas
- Viewer users can only view valuations

### Data Transformation Engine
- Secure JSON-based formula system (no arbitrary code execution)
- Supports mathematical operations: add, subtract, multiply, divide, power
- Built-in functions: abs, round, max, min, sum, sqrt, log, trigonometric functions
- Company and time-period specific field mappings

### Financial Data Processing
- Fetches data from Yahoo Finance API
- Stores raw data with full audit trail
- Transforms raw provider data into canonical format
- Calculates derived financial metrics (ratios, enterprise value, etc.)

## Development Setup

### Local Development (SQLite)
```bash
# Install dependencies
pip install -r requirements.txt

# Start development server
python start.py

# Or manually with uvicorn
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend Development
```bash
# Install dependencies
cd frontend && npm install

# Start React development server
npm start

# Build for production
npm run build
```

### Full Stack Development (Docker)
```bash
# Start all services (PostgreSQL + FastAPI + React + NGINX)
docker-compose up --build

# Backend only (for API development)
docker-compose up db backend

# Frontend only (for UI development)
docker-compose up frontend
```

### Database Management
The system automatically creates tables on startup. Initial data (canonical fields, providers, industries) is populated via `init.sql`.

## API Endpoints

- **Authentication**: `/auth/register`, `/auth/token`, `/auth/me`
- **Valuations**: `/api/valuation/` (CRUD operations)
- **Transformations**: `/api/transform/mappings` (field mapping management)
- **Providers**: `/api/providers/` (data provider management)
- **Health Check**: `/health`
- **API Documentation**: `/docs` (Swagger UI)

## Configuration

Key environment variables:
- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: JWT signing key (change in production!)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time

## Data Flow

1. **Raw Data Ingestion**: Financial data fetched from Yahoo Finance
2. **Field Mapping**: Raw provider fields mapped to canonical fields
3. **Transformation**: Apply mathematical formulas to transform data
4. **Valuation Calculation**: Compute financial ratios and enterprise metrics
5. **Storage**: Results stored with full audit trail

## Formula Engine Example

```json
{
  "target_field": "debt_ratio",
  "expression": {
    "op": "divide",
    "args": [
      {"field": "total_liabilities"},
      {"field": "total_assets"}
    ]
  }
}
```

## Security Notes

- All routes are protected by JWT authentication
- Formula engine prevents arbitrary code execution
- Role-based access control for administrative functions
- Passwords are hashed with bcrypt
- SQL injection protection via SQLAlchemy ORM

## Legacy Files

The `legacy/` directory contains the original implementation files that are kept for reference but not used in the new system:
- `legacy/FinancialDataDef.py` - Original financial analysis logic
- `legacy/YahooDataParser.py` - Original price data parser
- `legacy/FinancesData.ipynb` - Original Jupyter notebook analysis

## Common Development Tasks

```bash
# Run linting/formatting (if configured)
black backend/
flake8 backend/

# Run tests (add pytest configuration as needed)
pytest

# View logs in Docker
docker-compose logs -f backend

# Reset database
docker-compose down -v && docker-compose up --build
```