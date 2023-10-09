from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

DB = {
    "provider": "postgres",
    "user": settings.db_username,
    "password": settings.db_password,
    "host": settings.db_hostname,
    "database": settings.db_name,
}

SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{DB['user']}:{DB['password']}@{DB['host']}/{DB['database']}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()


from sqlalchemy.exc import SQLAlchemyError


def get_db():
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        print(f"Database error: {str(e)}")
    finally:
        db.close()
