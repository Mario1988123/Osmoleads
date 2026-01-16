"""
Modelo de KeywordSuggestion - Sugerencias de keywords basadas en análisis.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from datetime import datetime
from app.core.database import Base


class KeywordSuggestion(Base):
    __tablename__ = "keyword_suggestions"

    id = Column(Integer, primary_key=True, index=True)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="CASCADE"), nullable=False)
    text = Column(String(255), nullable=False)  # La keyword sugerida
    source = Column(String(50), nullable=True)  # meta, title, h1, content
    frequency = Column(Integer, default=1)  # Cuántas veces se ha encontrado
    websites_count = Column(Integer, default=1)  # En cuántas webs diferentes
    is_ignored = Column(Boolean, default=False)  # Si el usuario la ha ignorado
    is_added = Column(Boolean, default=False)  # Si ya se añadió a keywords
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<KeywordSuggestion {self.text}>"
