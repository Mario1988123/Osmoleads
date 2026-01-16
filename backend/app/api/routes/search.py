"""
Endpoints de búsqueda en Google.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date, datetime

from app.core.database import get_db
from app.api.deps import get_current_user
from app.api.schemas import SearchRequest, SearchResponse, SearchStats
from app.models.country import Country
from app.models.keyword import Keyword
from app.models.search_log import SearchLog
from app.models.settings import AppSettings
from app.services.google_search import GoogleSearchService
from app.services.scheduler import SchedulerService
from app.core.config import settings

router = APIRouter(prefix="/search", tags=["Búsqueda"])


@router.get("/stats", response_model=SearchStats)
async def get_search_stats(
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Obtiene estadísticas de búsquedas del día.
    """
    today = date.today()
    searches_today = db.query(SearchLog).filter(
        SearchLog.searched_at >= datetime.combine(today, datetime.min.time())
    ).count()

    # Obtener límite configurado
    setting = db.query(AppSettings).filter(
        AppSettings.key == "max_searches"
    ).first()

    max_searches = settings.MAX_SEARCHES_DEFAULT
    if setting and setting.value:
        try:
            max_searches = int(setting.value)
        except ValueError:
            pass

    is_unlimited = max_searches == 0
    remaining = -1 if is_unlimited else max(0, max_searches - searches_today)

    return SearchStats(
        searches_today=searches_today,
        max_searches=max_searches,
        remaining=remaining,
        is_unlimited=is_unlimited
    )


@router.post("/country/{country_id}", response_model=SearchResponse)
async def search_country(
    country_id: int,
    keyword_ids: Optional[List[int]] = None,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Ejecuta búsquedas para un país específico.
    Si se proporcionan keyword_ids, solo busca esas keywords.
    Si no, busca todas las keywords activas del país.
    """
    # Verificar país
    country = db.query(Country).filter(Country.id == country_id).first()
    if not country:
        raise HTTPException(status_code=404, detail="País no encontrado")

    # Obtener keywords
    query = db.query(Keyword).filter(
        Keyword.country_id == country_id,
        Keyword.is_active == True
    )

    if keyword_ids:
        query = query.filter(Keyword.id.in_(keyword_ids))

    keywords = query.all()

    if not keywords:
        raise HTTPException(status_code=400, detail="No hay keywords activas para buscar")

    # Iniciar búsqueda
    search_service = GoogleSearchService(db)

    total_results = 0
    new_leads = 0
    searches_used = 0
    errors = []

    for keyword in keywords:
        can_search, error_msg = search_service.can_search()
        if not can_search:
            errors.append(error_msg)
            break

        result = await search_service.search(
            keyword=keyword,
            country_code=country.code,
            language=country.language
        )

        searches_used += 1

        if result["success"]:
            total_results += result.get("total_results", 0)
            new_leads += result.get("new_leads", 0)
        else:
            errors.append(f"{keyword.text}: {result.get('error')}")

    message = f"Búsqueda completada. {new_leads} nuevos leads encontrados."
    if errors:
        message += f" Errores: {len(errors)}"

    return SearchResponse(
        success=len(errors) == 0,
        message=message,
        total_results=total_results,
        new_leads=new_leads,
        searches_used=searches_used,
        remaining_searches=search_service.get_remaining_searches()
    )


@router.post("/all", response_model=SearchResponse)
async def search_all_countries(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Ejecuta búsquedas para todos los países activos.
    Se ejecuta en background para no bloquear.
    """
    # Verificar que hay países activos
    active_countries = db.query(Country).filter(Country.is_active == True).count()
    if active_countries == 0:
        raise HTTPException(status_code=400, detail="No hay países activos")

    # Ejecutar en background
    scheduler = SchedulerService(db)
    stats = await scheduler.run_all_searches()

    return SearchResponse(
        success=len(stats.get("errors", [])) == 0,
        message=f"Búsqueda completada en {stats['countries_processed']} países",
        total_results=stats.get("total_searches", 0),
        new_leads=stats.get("new_leads", 0),
        searches_used=stats.get("total_searches", 0),
        remaining_searches=0
    )


@router.get("/history")
async def get_search_history(
    country_id: Optional[int] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Obtiene el historial de búsquedas.
    """
    query = db.query(SearchLog)

    if country_id:
        query = query.filter(SearchLog.country_id == country_id)

    logs = query.order_by(SearchLog.searched_at.desc()).limit(limit).all()

    return [
        {
            "id": log.id,
            "keyword": log.keyword_text,
            "results": log.results_count,
            "new_leads": log.new_leads_count,
            "success": log.is_success,
            "error": log.error_message,
            "date": log.searched_at.isoformat()
        }
        for log in logs
    ]
