
import os
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

load_dotenv()

user_db_url = os.getenv("user_db_url")
print(f"Connecting to: {user_db_url}")

if not user_db_url:
    print("Error: user_db_url not found in .env")
    exit(1)

engine = create_engine(user_db_url)
inspector = inspect(engine)

def inspect_db():
    print("\n--- User Portal Database Schema ---")
    tables = inspector.get_table_names()
    print(f"Tables found: {tables}")
    
    for table_name in tables:
        print(f"\nTable: {table_name}")
        columns = inspector.get_columns(table_name)
        for column in columns:
            print(f"  - {column['name']} ({column['type']})")

if __name__ == "__main__":
    inspect_db()

