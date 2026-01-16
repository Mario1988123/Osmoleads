"""
Modelo de Keyword - Palabras clave para búsquedas.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, index=True)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="CASCADE"), nullable=False)
    text = Column(String(255), nullable=False)  # La palabra clave
    category = Column(String(50), nullable=True)  # producto, competencia, general
    results_per_search = Column(Integer, default=5)  # Cuántos resultados por búsqueda
    is_active = Column(Boolean, default=True)
    total_searches = Column(Integer, default=0)  # Contador de veces buscada
    total_results = Column(Integer, default=0)  # Total de resultados encontrados
    last_search_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    country = relationship("Country", back_populates="keywords")
    leads = relationship("Lead", back_populates="found_by_keyword")

    def __repr__(self):
        return f"<Keyword {self.text}>"
