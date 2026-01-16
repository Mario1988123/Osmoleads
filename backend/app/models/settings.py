"""
Modelo de AppSettings - Configuración de la aplicación.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from app.core.database import Base


class AppSettings(Base):
    __tablename__ = "app_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), nullable=False, unique=True)  # max_searches, pin, etc.
    value = Column(Text, nullable=True)
    description = Column(String(500), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<AppSettings {self.key}={self.value}>"
