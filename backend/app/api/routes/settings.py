"""
Endpoints de configuración.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, datetime

from app.core.database import get_db
from app.api.deps import get_current_user
from app.api.schemas import SettingsUpdate, SettingsResponse, MarketplaceCreate, MarketplaceResponse
from app.models.settings import AppSettings
from app.models.marketplace import Marketplace
from app.models.search_log import SearchLog
from app.core.config import settings
from app.core.security import verify_pin

router = APIRouter(prefix="/settings", tags=["Configuración"])


@router.get("", response_model=SettingsResponse)
async def get_settings(
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Obtiene la configuración actual.
    """
    # Obtener max_searches
    max_setting = db.query(AppSettings).filter(
        AppSettings.key == "max_searches"
    ).first()

    max_searches = settings.MAX_SEARCHES_DEFAULT
    if max_setting and max_setting.value:
        try:
            max_searches = int(max_setting.value)
        except ValueError:
            pass

    # Búsquedas de hoy
    today = date.today()
    searches_today = db.query(SearchLog).filter(
        SearchLog.searched_at >= datetime.combine(today, datetime.min.time())
    ).count()

    return SettingsResponse(
        max_searches=max_searches,
        searches_today=searches_today,
        pin_configured=True
    )


@router.put("")
async def update_settings(
    data: SettingsUpdate,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Actualiza la configuración.
    """
    updates = []

    if data.max_searches is not None:
        setting = db.query(AppSettings).filter(
            AppSettings.key == "max_searches"
        ).first()

        if setting:
            setting.value = str(data.max_searches)
        else:
            setting = AppSettings(
                key="max_searches",
                value=str(data.max_searches),
                description="Límite máximo de búsquedas diarias"
            )
            db.add(setting)

        updates.append("max_searches")

    if data.access_pin:
        # Aquí solo guardamos el hash o referencia, el PIN real se guarda en .env
        # Por seguridad, no cambiamos el PIN desde la API
        pass

    db.commit()

    return {"message": f"Configuración actualizada: {', '.join(updates)}"}


# ============ Marketplaces ============
@router.get("/marketplaces", response_model=list[MarketplaceResponse])
async def list_marketplaces(
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Lista todos los marketplaces configurados.
    """
    marketplaces = db.query(Marketplace).order_by(Marketplace.domain).all()
    return marketplaces


@router.post("/marketplaces", response_model=MarketplaceResponse)
async def add_marketplace(
    data: MarketplaceCreate,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Añade un nuevo marketplace a la lista de exclusión.
    """
    # Normalizar dominio
    domain = data.domain.lower().strip()
    if domain.startswith("www."):
        domain = domain[4:]

    # Verificar si ya existe
    existing = db.query(Marketplace).filter(
        Marketplace.domain == domain
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"El marketplace '{domain}' ya existe"
        )

    marketplace = Marketplace(
        domain=domain,
        name=data.name or domain
    )
    db.add(marketplace)
    db.commit()
    db.refresh(marketplace)

    return marketplace


@router.delete("/marketplaces/{marketplace_id}")
async def delete_marketplace(
    marketplace_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Elimina un marketplace de la lista.
    """
    marketplace = db.query(Marketplace).filter(
        Marketplace.id == marketplace_id
    ).first()
    if not marketplace:
        raise HTTPException(status_code=404, detail="Marketplace no encontrado")

    if marketplace.is_system:
        raise HTTPException(status_code=400, detail="No se puede eliminar un marketplace del sistema")

    db.delete(marketplace)
    db.commit()

    return {"message": f"Marketplace '{marketplace.domain}' eliminado"}
