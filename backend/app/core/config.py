"""
Configuración central de la aplicación.
Carga variables de entorno desde .env
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Aplicación
    APP_NAME: str = "Osmoleads"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Seguridad
    SECRET_KEY: str = "cambiar-esta-clave-secreta-en-produccion"
    ACCESS_PIN: str = "Osmo1980"
    PIN_EXPIRY_HOURS: int = 24

    # Base de datos
    DATABASE_URL: str = "postgresql://osmoleads_user:password@localhost:5432/osmoleads_db"

    # Google APIs
    GOOGLE_API_KEY: str = ""
    GOOGLE_SEARCH_ENGINE_ID: str = ""

    # Límites
    MAX_SEARCHES_DEFAULT: int = 100
    MAX_RESULTS_PER_SEARCH: int = 10

    # Scraping
    SCRAPING_TIMEOUT: int = 10
    SCRAPING_DELAY: float = 0.5
    USER_AGENT: str = "Osmoleads Bot/1.0 (Contact: admin@osmoleads.com)"

    # Marketplaces a excluir automáticamente
    MARKETPLACES: list = [
        "amazon", "ebay", "aliexpress", "alibaba", "mercadolibre",
        "leroymerlin", "leroy-merlin", "bauhaus", "bricomart",
        "mediamarkt", "media-markt", "pccomponentes", "elcorteingles",
        "carrefour", "wallapop", "milanuncios", "fnac", "worten",
        "manomano", "bricodepot", "bricor", "aki"
    ]

    # Dominios a excluir siempre
    EXCLUDED_DOMAINS: list = [
        "youtube.com", "facebook.com", "instagram.com", "twitter.com",
        "linkedin.com", "tiktok.com", "pinterest.com", "wikipedia.org",
        "google.com", "bing.com", "yahoo.com", "scribd.com"
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
