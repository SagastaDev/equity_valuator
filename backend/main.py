from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import valuation, transform, providers, companies
from backend.auth import routes as auth_routes
from backend.db.base import engine
from backend.db import models
from backend.db.session import get_db
from backend.db.init_data import initialize_database

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Equity Valuation System",
    description="A modular equity valuation system with data transformation capabilities",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Initialize database with default data on startup."""
    db = next(get_db())
    try:
        initialize_database(db)
    finally:
        db.close()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://0.0.0.0:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_routes.router, prefix="/auth", tags=["authentication"])
app.include_router(valuation.router, prefix="/api/valuation", tags=["valuation"])
app.include_router(transform.router, prefix="/api/transform", tags=["transform"])
app.include_router(providers.router, prefix="/api/providers", tags=["providers"])
app.include_router(companies.router, tags=["companies"])  # companies router includes its own prefix

@app.get("/")
async def root():
    return {"message": "Equity Valuation System API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}