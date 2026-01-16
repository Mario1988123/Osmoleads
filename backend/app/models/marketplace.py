"""
Modelo de Marketplace - Dominios que se clasifican automáticamente como marketplace.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from app.core.database import Base


class Marketplace(Base):
    __tablename__ = "marketplaces"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String(255), nullable=False, unique=True)  # amazon.es, leroymerlin.es...
    name = Column(String(255), nullable=True)  # Nombre legible
    is_system = Column(Boolean, default=False)  # Si es del sistema (predefinido)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Marketplace {self.domain}>"
