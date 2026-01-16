"""
Modelo de LeadStatus - Estados personalizables para leads.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class LeadStatus(Base):
    __tablename__ = "lead_statuses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)  # Pendiente, Cliente, En gestión...
    color = Column(String(20), default="#6B7280")  # Color hex
    icon = Column(String(50), nullable=True)  # Nombre del icono (FontAwesome)
    order = Column(Integer, default=0)  # Orden de aparición
    is_default = Column(Boolean, default=False)  # Si es el estado por defecto
    is_system = Column(Boolean, default=False)  # Si es un estado del sistema (no editable)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    leads = relationship("Lead", back_populates="status")

    def __repr__(self):
        return f"<LeadStatus {self.name}>"
