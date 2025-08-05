#!/usr/bin/env python3
"""
Startup script for the Equity Valuation System.
Run this to start the development server.
"""

import uvicorn
import os

def main():
    """Start the FastAPI development server"""
    # Set environment variables for development
    os.environ.setdefault("DATABASE_URL", "sqlite:///./equity_valuation.db")
    os.environ.setdefault("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # Start the server
    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()