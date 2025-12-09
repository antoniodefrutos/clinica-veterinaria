from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# URL para SQLite en desarrollo (archivo en la carpeta backend)
DATABASE_URL = "sqlite:///./clinica.db"

# Para SQLite necesitamos connect_args
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base declarativa para modelos
Base = declarative_base()

# Dependency para FastAPI (uso en routers)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
