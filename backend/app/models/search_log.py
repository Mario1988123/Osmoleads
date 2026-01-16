"""
Modelo de SearchLog - Registro de búsquedas realizadas.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from datetime import datetime
from app.core.database import Base


class SearchLog(Base):
    __tablename__ = "search_logs"

    id = Column(Integer, primary_key=True, index=True)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="SET NULL"), nullable=True)
    keyword_id = Column(Integer, ForeignKey("keywords.id", ondelete="SET NULL"), nullable=True)
    keyword_text = Column(String(255), nullable=True)  # Guardamos el texto por si se borra la keyword
    results_count = Column(Integer, default=0)
    new_leads_count = Column(Integer, default=0)  # Leads nuevos (no duplicados)
    is_success = Column(Boolean, default=True)
    error_message = Column(String(500), nullable=True)
    searched_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<SearchLog {self.keyword_text} at {self.searched_at}>"
