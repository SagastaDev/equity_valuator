#!/usr/bin/env python3
"""
Initialize test users for the equity valuation system.
Creates admin and viewer users for testing and development purposes.
"""

import sys
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.db.base import Base
from backend.db.models.user import User, UserRole
from backend.auth.utils import get_password_hash

def create_test_users(database_url: str):
    """Create test users in the database."""
    
    # Create engine and session
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Test users to create
        test_users = [
            {
                "email": "admin@test.com",
                "password": "admin123",
                "role": UserRole.ADMIN,
                "description": "Test admin user"
            },
            {
                "email": "viewer@test.com", 
                "password": "viewer123",
                "role": UserRole.VIEWER,
                "description": "Test viewer user"
            },
            {
                "email": "john.admin@company.com",
                "password": "secure123",
                "role": UserRole.ADMIN,
                "description": "John Smith - Admin"
            },
            {
                "email": "jane.analyst@company.com",
                "password": "analyst123",
                "role": UserRole.VIEWER,
                "description": "Jane Doe - Financial Analyst"
            },
            {
                "email": "demo@equity.com",
                "password": "demo123",
                "role": UserRole.VIEWER,
                "description": "Demo user for presentations"
            }
        ]
        
        created_count = 0
        skipped_count = 0
        
        for user_data in test_users:
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == user_data["email"]).first()
            
            if existing_user:
                print(f"User {user_data['email']} already exists, skipping...")
                skipped_count += 1
                continue
            
            # Create new user
            hashed_password = get_password_hash(user_data["password"])
            db_user = User(
                email=user_data["email"],
                hashed_password=hashed_password,
                role=user_data["role"]
            )
            
            db.add(db_user)
            print(f"Created {user_data['role'].value} user: {user_data['email']} ({user_data['description']})")
            created_count += 1
        
        # Commit all changes
        db.commit()
        
        print(f"\n✅ Database initialization complete!")
        print(f"   • Created: {created_count} users")
        print(f"   • Skipped: {skipped_count} existing users")
        
        if created_count > 0:
            print(f"\n📝 Test User Credentials:")
            print(f"   Admin users:")
            print(f"   • admin@test.com / admin123")
            print(f"   • john.admin@company.com / secure123")
            print(f"   ")
            print(f"   Viewer users:")
            print(f"   • viewer@test.com / viewer123")
            print(f"   • jane.analyst@company.com / analyst123")
            print(f"   • demo@equity.com / demo123")
            print(f"\n🔐 Change these passwords in production!")
        
    except Exception as e:
        print(f"❌ Error creating test users: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) != 2:
        print("Usage: python init_test_users.py <database_url>")
        print("Example: python init_test_users.py 'postgresql://postgres:postgres@localhost:5433/equity_valuation'")
        print("Example: python init_test_users.py 'sqlite:///./equity_valuation.db'")
        sys.exit(1)
    
    database_url = sys.argv[1]
    print(f"🗄️  Initializing test users in database: {database_url}")
    
    try:
        create_test_users(database_url)
    except Exception as e:
        print(f"❌ Failed to initialize test users: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()