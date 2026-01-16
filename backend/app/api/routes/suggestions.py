"""
Endpoints de sugerencias de keywords.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.api.deps import get_current_user
from app.api.schemas import KeywordSuggestionResponse, KeywordCreate
from app.models.keyword_suggestion import KeywordSuggestion
from app.models.keyword import Keyword
from app.models.lead import Lead, LeadTab
from app.services.scraper import KeywordAnalyzer

router = APIRouter(prefix="/suggestions", tags=["Sugerencias"])


@router.get("/country/{country_id}", response_model=List[KeywordSuggestionResponse])
async def get_suggestions(
    country_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Obtiene sugerencias de keywords para un país.
    """
    suggestions = db.query(KeywordSuggestion).filter(
        KeywordSuggestion.country_id == country_id,
        KeywordSuggestion.is_ignored == False,
        KeywordSuggestion.is_added == False
    ).order_by(KeywordSuggestion.frequency.desc()).limit(50).all()

    return suggestions


@router.post("/analyze/{country_id}")
async def analyze_country_leads(
    country_id: int,
    limit: int = 20,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Analiza los leads guardados de un país para generar sugerencias de keywords.
    """
    # Obtener leads guardados (en pestaña Leads, no en NEW ni descartados)
    leads = db.query(Lead).filter(
        Lead.country_id == country_id,
        Lead.tab == LeadTab.LEADS
    ).order_by(Lead.found_at.desc()).limit(limit).all()

    if not leads:
        return {"message": "No hay leads para analizar", "suggestions_added": 0}

    analyzer = KeywordAnalyzer()
    all_keywords = {}

    for lead in leads:
        try:
            result = await analyzer.analyze_website(lead.url)

            if result["success"]:
                # Procesar meta keywords
                for kw in result.get("meta_keywords", []):
                    kw_lower = kw.lower().strip()
                    if len(kw_lower) > 3:
                        if kw_lower not in all_keywords:
                            all_keywords[kw_lower] = {
                                "frequency": 0,
                                "websites": set(),
                                "source": "meta"
                            }
                        all_keywords[kw_lower]["frequency"] += 1
                        all_keywords[kw_lower]["websites"].add(lead.domain)

                # Procesar keywords sugeridas del contenido
                for item in result.get("suggested_keywords", []):
                    kw = item["keyword"]
                    if len(kw) > 3:
                        if kw not in all_keywords:
                            all_keywords[kw] = {
                                "frequency": 0,
                                "websites": set(),
                                "source": "content"
                            }
                        all_keywords[kw]["frequency"] += item["frequency"]
                        all_keywords[kw]["websites"].add(lead.domain)

        except Exception:
            continue

    # Guardar sugerencias en base de datos
    suggestions_added = 0
    existing_keywords = {
        k.text.lower() for k in
        db.query(Keyword).filter(Keyword.country_id == country_id).all()
    }

    for kw, data in all_keywords.items():
        # Solo sugerir si aparece en múltiples webs o con alta frecuencia
        if data["frequency"] >= 3 or len(data["websites"]) >= 2:
            # No sugerir si ya existe como keyword
            if kw in existing_keywords:
                continue

            # Verificar si ya existe como sugerencia
            existing = db.query(KeywordSuggestion).filter(
                KeywordSuggestion.country_id == country_id,
                KeywordSuggestion.text == kw
            ).first()

            if existing:
                existing.frequency = max(existing.frequency, data["frequency"])
                existing.websites_count = max(existing.websites_count, len(data["websites"]))
            else:
                suggestion = KeywordSuggestion(
                    country_id=country_id,
                    text=kw,
                    source=data["source"],
                    frequency=data["frequency"],
                    websites_count=len(data["websites"])
                )
                db.add(suggestion)
                suggestions_added += 1

    db.commit()

    return {
        "message": f"Análisis completado. {len(leads)} leads analizados.",
        "keywords_found": len(all_keywords),
        "suggestions_added": suggestions_added
    }


@router.post("/{suggestion_id}/add")
async def add_suggestion_as_keyword(
    suggestion_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Añade una sugerencia como keyword de búsqueda.
    """
    suggestion = db.query(KeywordSuggestion).filter(
        KeywordSuggestion.id == suggestion_id
    ).first()

    if not suggestion:
        raise HTTPException(status_code=404, detail="Sugerencia no encontrada")

    # Verificar que no existe ya
    existing = db.query(Keyword).filter(
        Keyword.country_id == suggestion.country_id,
        Keyword.text == suggestion.text
    ).first()

    if existing:
        suggestion.is_added = True
        db.commit()
        return {"message": "La keyword ya existe", "keyword_id": existing.id}

    # Crear keyword
    keyword = Keyword(
        country_id=suggestion.country_id,
        text=suggestion.text,
        category="sugerida",
        results_per_search=5
    )
    db.add(keyword)

    suggestion.is_added = True

    db.commit()
    db.refresh(keyword)

    return {
        "message": f"Keyword '{suggestion.text}' añadida correctamente",
        "keyword_id": keyword.id
    }


@router.post("/{suggestion_id}/ignore")
async def ignore_suggestion(
    suggestion_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Ignora una sugerencia (no volverá a aparecer).
    """
    suggestion = db.query(KeywordSuggestion).filter(
        KeywordSuggestion.id == suggestion_id
    ).first()

    if not suggestion:
        raise HTTPException(status_code=404, detail="Sugerencia no encontrada")

    suggestion.is_ignored = True
    db.commit()

    return {"message": f"Sugerencia '{suggestion.text}' ignorada"}


@router.get("/ranking/{country_id}")
async def get_keyword_ranking(
    country_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Obtiene un ranking de las keywords más encontradas en las webs analizadas.
    Incluye tanto las sugerencias como las keywords actuales con sus estadísticas.
    """
    # Keywords actuales con estadísticas
    keywords = db.query(Keyword).filter(
        Keyword.country_id == country_id
    ).order_by(Keyword.total_results.desc()).all()

    current_keywords = [
        {
            "text": kw.text,
            "type": "active",
            "total_results": kw.total_results,
            "total_searches": kw.total_searches,
            "category": kw.category,
            "is_active": kw.is_active
        }
        for kw in keywords
    ]

    # Sugerencias ordenadas por frecuencia
    suggestions = db.query(KeywordSuggestion).filter(
        KeywordSuggestion.country_id == country_id,
        KeywordSuggestion.is_ignored == False
    ).order_by(KeywordSuggestion.frequency.desc()).limit(30).all()

    suggested_keywords = [
        {
            "text": s.text,
            "type": "suggested",
            "frequency": s.frequency,
            "websites_count": s.websites_count,
            "source": s.source,
            "is_added": s.is_added
        }
        for s in suggestions
    ]

    return {
        "current_keywords": current_keywords,
        "suggested_keywords": suggested_keywords
    }
