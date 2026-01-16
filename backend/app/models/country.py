"""
Modelo de País - Representa un mercado/país donde se realizan búsquedas.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)  # España, Francia...
    code = Column(String(10), nullable=False)  # ES, FR, PT...
    language = Column(String(10), nullable=False, default="es")  # es, fr, pt...
    flag_image = Column(Text, nullable=True)  # Ruta a la imagen de bandera
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    keywords = relationship("Keyword", back_populates="country", cascade="all, delete-orphan")
    leads = relationship("Lead", back_populates="country", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Country {self.name} ({self.code})>"
