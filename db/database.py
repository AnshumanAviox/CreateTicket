from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException
from models import Settings

settings = Settings()

# Create database engine with error handling
try:
    connection_string = (
        f"mssql+pyodbc://{settings.DATABASE_URL}"
        if "://" in settings.DATABASE_URL
        else settings.DATABASE_URL
    )
    
    engine = create_engine(
        connection_string,
        pool_pre_ping=True,
        pool_recycle=3600,
        connect_args={
            "timeout": 30
        }
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    print(f"Database connection error: {str(e)}")
    raise

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )
    finally:
        db.close() 