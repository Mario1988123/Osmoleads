"""
Endpoints de palabras clave.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.api.deps import get_current_user
from app.api.schemas import (
    KeywordCreate, KeywordUpdate, KeywordResponse
)
from app.models.keyword import Keyword
from app.models.country import Country

router = APIRouter(prefix="/keywords", tags=["Keywords"])


@router.get("/country/{country_id}", response_model=List[KeywordResponse])
async def list_keywords_by_country(
    country_id: int,
    active_only: bool = False,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Lista todas las keywords de un país.
    """
    query = db.query(Keyword).filter(Keyword.country_id == country_id)

    if active_only:
        query = query.filter(Keyword.is_active == True)

    keywords = query.order_by(Keyword.text).all()
    return keywords


@router.get("/{keyword_id}", response_model=KeywordResponse)
async def get_keyword(
    keyword_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Obtiene una keyword por ID.
    """
    keyword = db.query(Keyword).filter(Keyword.id == keyword_id).first()
    if not keyword:
        raise HTTPException(status_code=404, detail="Keyword no encontrada")
    return keyword


@router.post("", response_model=KeywordResponse, status_code=status.HTTP_201_CREATED)
async def create_keyword(
    data: KeywordCreate,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Crea una nueva keyword.
    """
    # Verificar que el país existe
    country = db.query(Country).filter(Country.id == data.country_id).first()
    if not country:
        raise HTTPException(status_code=404, detail="País no encontrado")

    # Verificar que no existe ya
    existing = db.query(Keyword).filter(
        Keyword.country_id == data.country_id,
        Keyword.text == data.text
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe la keyword '{data.text}' en este país"
        )

    keyword = Keyword(
        country_id=data.country_id,
        text=data.text,
        category=data.category,
        results_per_search=data.results_per_search
    )
    db.add(keyword)
    db.commit()
    db.refresh(keyword)

    return keyword


@router.put("/{keyword_id}", response_model=KeywordResponse)
async def update_keyword(
    keyword_id: int,
    data: KeywordUpdate,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Actualiza una keyword.
    """
    keyword = db.query(Keyword).filter(Keyword.id == keyword_id).first()
    if not keyword:
        raise HTTPException(status_code=404, detail="Keyword no encontrada")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(keyword, field, value)

    db.commit()
    db.refresh(keyword)

    return keyword


@router.delete("/{keyword_id}")
async def delete_keyword(
    keyword_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Elimina una keyword.
    """
    keyword = db.query(Keyword).filter(Keyword.id == keyword_id).first()
    if not keyword:
        raise HTTPException(status_code=404, detail="Keyword no encontrada")

    db.delete(keyword)
    db.commit()

    return {"message": f"Keyword '{keyword.text}' eliminada correctamente"}


@router.post("/{keyword_id}/toggle")
async def toggle_keyword(
    keyword_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Activa/desactiva una keyword.
    """
    keyword = db.query(Keyword).filter(Keyword.id == keyword_id).first()
    if not keyword:
        raise HTTPException(status_code=404, detail="Keyword no encontrada")

    keyword.is_active = not keyword.is_active
    db.commit()

    state = "activada" if keyword.is_active else "desactivada"
    return {"message": f"Keyword '{keyword.text}' {state}", "is_active": keyword.is_active}
