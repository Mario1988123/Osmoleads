"""
Modelo de Lead - Empresas encontradas en las búsquedas.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class LeadTab(enum.Enum):
    """Pestañas donde puede estar un lead"""
    NEW = "new"  # Leads nuevos
    LEADS = "leads"  # Leads revisados
    DOUBTS = "doubts"  # Dudas
    DISCARDED = "discarded"  # Descartados
    MARKETPLACE = "marketplace"  # Marketplaces


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="CASCADE"), nullable=False)
    keyword_id = Column(Integer, ForeignKey("keywords.id", ondelete="SET NULL"), nullable=True)
    status_id = Column(Integer, ForeignKey("lead_statuses.id", ondelete="SET NULL"), nullable=True)

    # Información básica
    name = Column(String(500), nullable=False)  # Título de Google
    url = Column(Text, nullable=False)  # URL completa
    domain = Column(String(255), nullable=False, index=True)  # Dominio principal
    snippet = Column(Text, nullable=True)  # Descripción de Google

    # Información de contacto (extraída por scraping)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    cif = Column(String(20), nullable=True)

    # Clasificación
    tab = Column(Enum(LeadTab), default=LeadTab.NEW, nullable=False, index=True)
    is_reviewed = Column(Boolean, default=False)

    # Metadatos
    found_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)
    contact_extracted = Column(Boolean, default=False)  # Si ya se hizo scraping
    contact_extracted_at = Column(DateTime, nullable=True)

    # Relaciones
    country = relationship("Country", back_populates="leads")
    found_by_keyword = relationship("Keyword", back_populates="leads")
    status = relationship("LeadStatus", back_populates="leads")
    notes = relationship("Note", back_populates="lead", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Lead {self.domain}>"
