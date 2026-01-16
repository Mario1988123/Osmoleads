"""
Endpoints de estados de leads.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.api.deps import get_current_user
from app.api.schemas import StatusCreate, StatusUpdate, StatusResponse
from app.models.status import LeadStatus

router = APIRouter(prefix="/statuses", tags=["Estados"])


@router.get("", response_model=List[StatusResponse])
async def list_statuses(
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Lista todos los estados disponibles.
    """
    statuses = db.query(LeadStatus).order_by(LeadStatus.order, LeadStatus.name).all()
    return statuses


@router.get("/{status_id}", response_model=StatusResponse)
async def get_status(
    status_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Obtiene un estado por ID.
    """
    status_obj = db.query(LeadStatus).filter(LeadStatus.id == status_id).first()
    if not status_obj:
        raise HTTPException(status_code=404, detail="Estado no encontrado")
    return status_obj


@router.post("", response_model=StatusResponse, status_code=status.HTTP_201_CREATED)
async def create_status(
    data: StatusCreate,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Crea un nuevo estado.
    """
    # Verificar que no existe
    existing = db.query(LeadStatus).filter(LeadStatus.name == data.name).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe un estado con el nombre '{data.name}'"
        )

    status_obj = LeadStatus(
        name=data.name,
        color=data.color,
        icon=data.icon,
        order=data.order
    )
    db.add(status_obj)
    db.commit()
    db.refresh(status_obj)

    return status_obj


@router.put("/{status_id}", response_model=StatusResponse)
async def update_status(
    status_id: int,
    data: StatusUpdate,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Actualiza un estado.
    """
    status_obj = db.query(LeadStatus).filter(LeadStatus.id == status_id).first()
    if not status_obj:
        raise HTTPException(status_code=404, detail="Estado no encontrado")

    if status_obj.is_system:
        raise HTTPException(status_code=400, detail="No se puede modificar un estado del sistema")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(status_obj, field, value)

    db.commit()
    db.refresh(status_obj)

    return status_obj


@router.delete("/{status_id}")
async def delete_status(
    status_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Elimina un estado.
    """
    status_obj = db.query(LeadStatus).filter(LeadStatus.id == status_id).first()
    if not status_obj:
        raise HTTPException(status_code=404, detail="Estado no encontrado")

    if status_obj.is_system:
        raise HTTPException(status_code=400, detail="No se puede eliminar un estado del sistema")

    db.delete(status_obj)
    db.commit()

    return {"message": f"Estado '{status_obj.name}' eliminado correctamente"}
