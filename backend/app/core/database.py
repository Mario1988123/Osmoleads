"""
Configuración de la base de datos PostgreSQL con SQLAlchemy.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Crear engine de SQLAlchemy
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Crear sesión local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()


def get_db():
    """
    Dependency para obtener sesión de base de datos.
    Se usa en los endpoints de FastAPI.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Inicializa la base de datos creando todas las tablas.
    """
    from app.models import country, keyword, lead, note, status, search_log
    Base.metadata.create_all(bind=engine)
