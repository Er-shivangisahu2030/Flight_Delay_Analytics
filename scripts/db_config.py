"""
db_config.py
------------
Single source of truth for the MySQL connection used across the project.
"""

from urllib.parse import quote_plus
from sqlalchemy import create_engine

# ------------------------------------------------------------------
# MySQL Connection Settings
# ------------------------------------------------------------------
DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = "disha@8249"

# IMPORTANT: This must match the database shown in MySQL Workbench
DB_NAME = "airlinedw_project"

# ------------------------------------------------------------------
# Build Connection URL
# ------------------------------------------------------------------
ENCODED_PASSWORD = quote_plus(DB_PASSWORD)

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{ENCODED_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# ------------------------------------------------------------------
# Create SQLAlchemy Engine
# ------------------------------------------------------------------
def get_engine():
    """
    Return SQLAlchemy engine connected to MySQL.
    """
    return create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        echo=False,
    )


# ------------------------------------------------------------------
# Test Connection
# ------------------------------------------------------------------
if __name__ == "__main__":
    try:
        engine = get_engine()

        with engine.connect() as conn:
            print(f"✓ Successfully connected to database: {DB_NAME}")

        print("✓ Database connection working")

    except Exception as e:
        print("✗ Database connection failed")
        print(e)