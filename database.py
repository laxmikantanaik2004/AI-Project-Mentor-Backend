import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, declarative_base


# Load environment variables from .env
load_dotenv()


# Create SQLAlchemy Base
Base = declarative_base()


def get_boolean_environment(variable_name, default_value):
    value = os.getenv(variable_name, default_value)

    return value.strip().lower() in {
        "true",
        "yes",
        "1",
    }


# ============================================================
# Database Environment Variables
# ============================================================

db_server = os.getenv("DB_SERVER")

db_name = os.getenv("DB_NAME")

db_driver = os.getenv(
    "DB_DRIVER",
    "ODBC Driver 18 for SQL Server",
)

db_username = os.getenv("DB_USERNAME")

db_password = os.getenv("DB_PASSWORD")


# ============================================================
# Connection Settings
# ============================================================

trusted_connection = get_boolean_environment(
    "DB_TRUSTED_CONNECTION",
    "yes",
)

encrypt_connection = get_boolean_environment(
    "DB_ENCRYPT",
    "yes",
)

trust_server_certificate = get_boolean_environment(
    "DB_TRUST_SERVER_CERTIFICATE",
    "yes",
)


# ============================================================
# Validate Required Variables
# ============================================================

if not db_server:
    raise RuntimeError(
        "DB_SERVER environment variable is missing."
    )

if not db_name:
    raise RuntimeError(
        "DB_NAME environment variable is missing."
    )


# ============================================================
# Build ODBC Connection String
# ============================================================

connection_parts = [
    f"DRIVER={{{db_driver}}}",
    f"SERVER={db_server}",
    f"DATABASE={db_name}",
]


# Windows Trusted Connection
if trusted_connection:
    connection_parts.append(
        "Trusted_Connection=yes"
    )

# SQL Server Username/Password
else:
    if not db_username:
        raise RuntimeError(
            "DB_USERNAME is required when "
            "DB_TRUSTED_CONNECTION=no."
        )

    if not db_password:
        raise RuntimeError(
            "DB_PASSWORD is required when "
            "DB_TRUSTED_CONNECTION=no."
        )

    connection_parts.extend(
        [
            f"UID={db_username}",
            f"PWD={db_password}",
        ]
    )


# ============================================================
# Additional Connection Settings
# ============================================================

connection_parts.extend(
    [
        (
            "Encrypt=yes"
            if encrypt_connection
            else "Encrypt=no"
        ),
        (
            "TrustServerCertificate=yes"
            if trust_server_certificate
            else "TrustServerCertificate=no"
        ),
        "Connection Timeout=30",
    ]
)


connection_string = ";".join(connection_parts) + ";"


# ============================================================
# Create SQLAlchemy Database URL
# ============================================================

database_url = URL.create(
    "mssql+pyodbc",
    query={
        "odbc_connect": connection_string,
    },
)


# ============================================================
# Create Database Engine
# ============================================================

engine = create_engine(
    database_url,
    pool_pre_ping=True,
    pool_recycle=1800,
)


# ============================================================
# Create Database Session
# ============================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ============================================================
# FastAPI Database Dependency
# ============================================================

def get_db():
    database_session = SessionLocal()

    try:
        yield database_session
    finally:
        database_session.close()


# ============================================================
# Test Database Connection
# ============================================================

def test_database_connection():

    with engine.connect() as connection:

        result = connection.execute(
            text(
                """
                SELECT
                    DB_NAME() AS database_name,
                    @@SERVERNAME AS server_name,
                    SUSER_SNAME() AS connected_user
                """
            )
        )

        row = result.fetchone()

        print("SQL Server connection successful.")
        print("Database:", row.database_name)
        print("Server:", row.server_name)
        print("Connected user:", row.connected_user)


# ============================================================
# Run Connection Test Directly
# ============================================================

if __name__ == "__main__":
    test_database_connection()