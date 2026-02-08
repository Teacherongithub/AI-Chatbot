from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv
import os

# --------------------------------------------------
# Load environment variables (.env)
# --------------------------------------------------
load_dotenv()  # looks for .env in project root

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("❌ DATABASE_URL is not set. Check your .env file.")

# TEMP DEBUG (REMOVE after it works)
print("🔗 DATABASE_URL loaded:", DATABASE_URL.split("@")[0] + "@*****")

# --------------------------------------------------
# Create SQLAlchemy engine
# --------------------------------------------------
engine = create_engine(
    DATABASE_URL,
    echo=True,            # show SQL logs (good for learning/debug)
    pool_pre_ping=True,   # prevents stale connections (Neon-safe)
)

# --------------------------------------------------
# Create tables
# --------------------------------------------------
def create_db_and_tables() -> None:
    """
    Create all database tables.
    Run once during setup.
    """
    print("🔄 Creating database tables...")
    SQLModel.metadata.create_all(engine)
    print("✅ Database tables created successfully!")

# --------------------------------------------------
# Session generator (FastAPI dependency)
# --------------------------------------------------
def get_session():
    """
    Yield a database session.
    """
    with Session(engine) as session:
        yield session
