import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text

# Load environment variables from backend/.env
BACKEND_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_DIR / ".env")

# Build the database URL safely, including special characters
# in the password.
database_url = URL.create(
    drivername="postgresql+psycopg2",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "5432")),
    database=os.getenv("DB_NAME", "customer_support_db"),
)

engine = create_engine(
    database_url,
    pool_pre_ping=True,
)


def test_connection():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("Database connection successful!")
        print("Test query result:", result.scalar())