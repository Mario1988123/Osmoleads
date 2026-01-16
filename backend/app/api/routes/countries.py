"""
Endpoints de países.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import base64

from app.core.database import get_db
from app.api.deps import get_current_user
from app.api.schemas import (
    CountryCreate, CountryUpdate, CountryResponse
)
from app.models.country import Country
from app.models.keyword import Keyword
from app.models.lead import Lead

router = APIRouter(prefix="/countries", tags=["Países"])


@router.get("", response_model=List[CountryResponse])
async def list_countries(
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Lista todos los países.
    """
    countries = db.query(Country).order_by(Country.name).all()

    result = []
    for country in countries:
        keywords_count = db.query(Keyword).filter(
            Keyword.country_id == country.id
        ).count()
        leads_count = db.query(Lead).filter(
            Lead.country_id == country.id
        ).count()

        country_dict = {
            "id": country.id,
            "name": country.name,
            "code": country.code,
            "language": country.language,
            "flag_image": country.flag_image,
            "is_active": country.is_active,
            "created_at": country.created_at,
            "keywords_count": keywords_count,
            "leads_count": leads_count
        }
        result.append(CountryResponse(**country_dict))

    return result


@router.get("/{country_id}", response_model=CountryResponse)
async def get_country(
    country_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Obtiene un país por ID.
    """
    country = db.query(Country).filter(Country.id == country_id).first()
    if not country:
        raise HTTPException(status_code=404, detail="País no encontrado")

    keywords_count = db.query(Keyword).filter(
        Keyword.country_id == country.id
    ).count()
    leads_count = db.query(Lead).filter(
        Lead.country_id == country.id
    ).count()

    return CountryResponse(
        id=country.id,
        name=country.name,
        code=country.code,
        language=country.language,
        flag_image=country.flag_image,
        is_active=country.is_active,
        created_at=country.created_at,
        keywords_count=keywords_count,
        leads_count=leads_count
    )


@router.post("", response_model=CountryResponse, status_code=status.HTTP_201_CREATED)
async def create_country(
    data: CountryCreate,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Crea un nuevo país.
    """
    # Verificar que no existe
    existing = db.query(Country).filter(Country.name == data.name).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe un país con el nombre '{data.name}'"
        )

    country = Country(
        name=data.name,
        code=data.code.upper(),
        language=data.language.lower(),
        flag_image=data.flag_image
    )
    db.add(country)
    db.commit()
    db.refresh(country)

    return CountryResponse(
        id=country.id,
        name=country.name,
        code=country.code,
        language=country.language,
        flag_image=country.flag_image,
        is_active=country.is_active,
        created_at=country.created_at,
        keywords_count=0,
        leads_count=0
    )


@router.put("/{country_id}", response_model=CountryResponse)
async def update_country(
    country_id: int,
    data: CountryUpdate,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Actualiza un país.
    """
    country = db.query(Country).filter(Country.id == country_id).first()
    if not country:
        raise HTTPException(status_code=404, detail="País no encontrado")

    # Actualizar campos
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "code" and value:
            value = value.upper()
        elif field == "language" and value:
            value = value.lower()
        setattr(country, field, value)

    db.commit()
    db.refresh(country)

    keywords_count = db.query(Keyword).filter(
        Keyword.country_id == country.id
    ).count()
    leads_count = db.query(Lead).filter(
        Lead.country_id == country.id
    ).count()

    return CountryResponse(
        id=country.id,
        name=country.name,
        code=country.code,
        language=country.language,
        flag_image=country.flag_image,
        is_active=country.is_active,
        created_at=country.created_at,
        keywords_count=keywords_count,
        leads_count=leads_count
    )


@router.delete("/{country_id}")
async def delete_country(
    country_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Elimina un país (y todos sus keywords y leads).
    """
    country = db.query(Country).filter(Country.id == country_id).first()
    if not country:
        raise HTTPException(status_code=404, detail="País no encontrado")

    db.delete(country)
    db.commit()

    return {"message": f"País '{country.name}' eliminado correctamente"}


@router.post("/{country_id}/flag")
async def upload_flag(
    country_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Sube una imagen de bandera para un país.
    """
    country = db.query(Country).filter(Country.id == country_id).first()
    if not country:
        raise HTTPException(status_code=404, detail="País no encontrado")

    # Verificar tipo de archivo
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")

    # Leer y codificar en base64
    content = await file.read()
    if len(content) > 500000:  # 500KB máximo
        raise HTTPException(status_code=400, detail="La imagen es demasiado grande (máx 500KB)")

    base64_image = base64.b64encode(content).decode("utf-8")
    data_url = f"data:{file.content_type};base64,{base64_image}"

    country.flag_image = data_url
    db.commit()

    return {"message": "Bandera actualizada correctamente"}
