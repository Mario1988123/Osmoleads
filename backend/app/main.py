"""
Aplicación principal de Osmoleads API.
FastAPI backend para el sistema de gestión de leads.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db, engine, Base
from app.api.routes import auth, countries, keywords, leads, search, statuses, settings as settings_routes, images, suggestions


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Eventos de inicio y cierre de la aplicación.
    """
    # Startup
    print(f"Iniciando {settings.APP_NAME} v{settings.APP_VERSION}")

    # Crear tablas si no existen
    Base.metadata.create_all(bind=engine)

    # Inicializar datos por defecto
    from app.core.database import SessionLocal
    from app.models.status import LeadStatus
    from app.models.marketplace import Marketplace
    from app.models.settings import AppSettings

    db = SessionLocal()
    try:
        # Crear estados por defecto si no existen
        default_statuses = [
            {"name": "Pendiente", "color": "#6B7280", "icon": "clock", "order": 0, "is_default": True, "is_system": True},
            {"name": "Competencia", "color": "#F59E0B", "icon": "building", "order": 1, "is_system": True},
            {"name": "Cliente", "color": "#10B981", "icon": "check-circle", "order": 2, "is_system": True},
            {"name": "En gestión", "color": "#3B82F6", "icon": "phone", "order": 3, "is_system": True},
            {"name": "Captado", "color": "#8B5CF6", "icon": "star", "order": 4, "is_system": True},
        ]

        for status_data in default_statuses:
            existing = db.query(LeadStatus).filter(LeadStatus.name == status_data["name"]).first()
            if not existing:
                status = LeadStatus(**status_data)
                db.add(status)

        # Crear marketplaces por defecto
        default_marketplaces = [
            "amazon.es", "amazon.com", "amazon.fr",
            "ebay.es", "ebay.com", "ebay.fr",
            "aliexpress.com", "alibaba.com",
            "leroymerlin.es", "leroymerlin.fr",
            "mediamarkt.es", "pccomponentes.com",
            "elcorteingles.es", "carrefour.es",
            "wallapop.com", "milanuncios.com",
            "manomano.es", "manomano.fr"
        ]

        for domain in default_marketplaces:
            existing = db.query(Marketplace).filter(Marketplace.domain == domain).first()
            if not existing:
                marketplace = Marketplace(domain=domain, name=domain.split(".")[0].title(), is_system=True)
                db.add(marketplace)

        # Crear configuración por defecto
        if not db.query(AppSettings).filter(AppSettings.key == "max_searches").first():
            setting = AppSettings(
                key="max_searches",
                value=str(settings.MAX_SEARCHES_DEFAULT),
                description="Límite máximo de búsquedas diarias (0 = ilimitado)"
            )
            db.add(setting)

        db.commit()

    except Exception as e:
        print(f"Error inicializando datos: {e}")
        db.rollback()
    finally:
        db.close()

    print("Aplicación iniciada correctamente")

    yield

    # Shutdown
    print("Cerrando aplicación...")


# Crear aplicación FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="API para gestión de leads y búsqueda automatizada",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Registrar routers
app.include_router(auth.router, prefix="/api")
app.include_router(countries.router, prefix="/api")
app.include_router(keywords.router, prefix="/api")
app.include_router(leads.router, prefix="/api")
app.include_router(search.router, prefix="/api")
app.include_router(statuses.router, prefix="/api")
app.include_router(settings_routes.router, prefix="/api")
app.include_router(images.router, prefix="/api")
app.include_router(suggestions.router, prefix="/api")


# Endpoint de salud
@app.get("/api/health")
async def health_check():
    """
    Endpoint para verificar que la API está funcionando.
    """
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@app.get("/api")
async def root():
    """
    Endpoint raíz de la API.
    """
    return {
        "message": f"Bienvenido a {settings.APP_NAME} API",
        "version": settings.APP_VERSION,
        "docs": "/api/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
