"""
Database utility scripts for WattWise Admin Portal.

Usage:
    python -m scripts.db_utils --init              # Initialize database
    python -m scripts.db_utils --drop              # Drop all tables (WARNING!)
    python -m scripts.db_utils --seed              # Seed with test data
    python -m scripts.db_utils --reset             # Drop and recreate
"""

import argparse
import sys
from config.database import init_db, drop_db, SessionLocal, engine
from models.admin import Admin, Base
from utils.password import hash_password, generate_secure_password
from datetime import datetime


def seed_database():
    """Seed database with test admin accounts."""
    db = SessionLocal()

    try:
        # Check if data already exists
        existing_admin = db.query(Admin).first()
        if existing_admin:
            print("✅ Database already seeded with test data")
            return

        # Test admin 1
        test_admin_1 = Admin(
            admin_id="ADM000001",
            name="John Doe",
            email="john@example.com",
            phone_number="1234567890",
            descom_name="Power Company A",
            hashed_password=hash_password("TestPass@123"),
            is_active=True
        )

        # Test admin 2
        test_admin_2 = Admin(
            admin_id="ADM000002",
            name="Jane Smith",
            email="jane@example.com",
            phone_number="0987654321",
            descom_name="Power Company B",
            hashed_password=hash_password("TestPass@456"),
            is_active=True
        )

        db.add(test_admin_1)
        db.add(test_admin_2)
        db.commit()

        print("✅ Database seeded with test admins:")
        print(f"   1. Admin ID: ADM000001, Email: john@example.com, Password: TestPass@123")
        print(f"   2. Admin ID: ADM000002, Email: jane@example.com, Password: TestPass@456")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {str(e)}")
    finally:
        db.close()


def check_database():
    """Check database connection and tables."""
    try:
        # Try to connect
        connection = engine.connect()
        connection.close()
        print("✅ Database connection: OK")

        # Check tables
        inspector = None
        try:
            from sqlalchemy import inspect
            inspector = inspect(engine)
            tables = inspector.get_table_names()

            if tables:
                print(f"✅ Tables found: {', '.join(tables)}")
            else:
                print("⚠️  No tables found. Run with --init to create tables.")
        except Exception as e:
            print(f"⚠️  Could not inspect tables: {str(e)}")

    except Exception as e:
        print(f"❌ Database connection error: {str(e)}")
        print("   Check DATABASE_URL in .env file")


def reset_database():
    """Drop and recreate all tables."""
    response = input("⚠️  WARNING: This will DELETE ALL DATA! Continue? (y/N): ")
    if response.lower() != 'y':
        print("❌ Operation cancelled")
        return

    print("🗑️  Dropping all tables...")
    drop_db()

    print("🔨 Creating new tables...")
    init_db()

    print("✅ Database reset complete!")


def main():
    parser = argparse.ArgumentParser(
        description="WattWise Admin Portal - Database Utilities"
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize database tables"
    )
    parser.add_argument(
        "--drop",
        action="store_true",
        help="Drop all tables (WARNING!)"
    )
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Seed database with test data"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Drop and recreate all tables"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check database connection and tables"
    )

    args = parser.parse_args()

    if not any(vars(args).values()):
        print("Use --help for usage information")
        check_database()
        return

    if args.init:
        print("🔨 Initializing database...")
        init_db()
        print("✅ Database initialized successfully!")

    if args.drop:
        response = input("⚠️  WARNING: This will DELETE ALL DATA! Continue? (y/N): ")
        if response.lower() == 'y':
            print("🗑️  Dropping all tables...")
            drop_db()
            print("✅ Database dropped successfully!")
        else:
            print("❌ Operation cancelled")

    if args.seed:
        print("🌱 Seeding database...")
        seed_database()

    if args.reset:
        reset_database()

    if args.check:
        print("🔍 Checking database...")
        check_database()


if __name__ == "__main__":
    main()

