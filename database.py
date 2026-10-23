
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

from backend.config import settings


database_url = URL.create(
    drivername="postgresql+psycopg",
    username=settings.db_user,
    password=settings.db_password,
    host=settings.db_host,
    port=settings.db_port,
    database=settings.db_name,
    query={"sslmode": settings.db_sslmode},
)


engine = create_engine(
    database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=0,
    connect_args={
        "options": "-c default_transaction_read_only=on",
        "connect_timeout": 5,
    },
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


def get_db():
    with SessionLocal() as db:
        yield db
