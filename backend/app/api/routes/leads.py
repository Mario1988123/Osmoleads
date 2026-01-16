"""
Endpoints de leads.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime
import io

from app.core.database import get_db
from app.api.deps import get_current_user
from app.api.schemas import (
    LeadResponse, LeadDetailResponse, LeadUpdate,
    NoteBase, NoteResponse, LeadTabEnum
)
from app.models.lead import Lead, LeadTab
from app.models.note import Note
from app.models.keyword import Keyword
from app.models.status import LeadStatus
from app.services.scraper import ScraperService
from app.services.excel_export import ExcelExportService

router = APIRouter(prefix="/leads", tags=["Leads"])


def lead_to_response(lead: Lead) -> dict:
    """Convierte un Lead a diccionario para respuesta."""
    return {
        "id": lead.id,
        "country_id": lead.country_id,
        "keyword_id": lead.keyword_id,
        "status_id": lead.status_id,
        "name": lead.name,
        "url": lead.url,
        "domain": lead.domain,
        "snippet": lead.snippet,
        "email": lead.email,
        "phone": lead.phone,
        "cif": lead.cif,
        "tab": lead.tab.value,
        "is_reviewed": lead.is_reviewed,
        "found_at": lead.found_at,
        "reviewed_at": lead.reviewed_at,
        "contact_extracted": lead.contact_extracted,
        "keyword_text": lead.found_by_keyword.text if lead.found_by_keyword else None,
        "status_name": lead.status.name if lead.status else None,
        "status_color": lead.status.color if lead.status else None,
        "notes_count": len(lead.notes) if lead.notes else 0
    }


@router.get("/country/{country_id}", response_model=List[LeadResponse])
async def list_leads_by_country(
    country_id: int,
    tab: Optional[LeadTabEnum] = None,
    keyword_id: Optional[int] = None,
    status_id: Optional[int] = None,
    search: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Lista leads de un país con filtros opcionales.
    """
    query = db.query(Lead).filter(Lead.country_id == country_id)

    if tab:
        tab_enum = LeadTab(tab.value)
        query = query.filter(Lead.tab == tab_enum)

    if keyword_id:
        query = query.filter(Lead.keyword_id == keyword_id)

    if status_id:
        query = query.filter(Lead.status_id == status_id)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Lead.name.ilike(search_term)) |
            (Lead.domain.ilike(search_term)) |
            (Lead.email.ilike(search_term))
        )

    leads = query.order_by(Lead.found_at.desc()).offset(offset).limit(limit).all()

    return [LeadResponse(**lead_to_response(lead)) for lead in leads]


@router.get("/country/{country_id}/stats")
async def get_country_lead_stats(
    country_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Obtiene estadísticas de leads por pestaña para un país.
    """
    stats = {}
    for tab in LeadTab:
        count = db.query(Lead).filter(
            Lead.country_id == country_id,
            Lead.tab == tab
        ).count()
        stats[tab.value] = count

    return stats


@router.get("/{lead_id}", response_model=LeadDetailResponse)
async def get_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Obtiene un lead con sus notas.
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    response = lead_to_response(lead)
    response["notes"] = [
        NoteResponse(
            id=note.id,
            lead_id=note.lead_id,
            content=note.content,
            created_at=note.created_at,
            updated_at=note.updated_at
        )
        for note in sorted(lead.notes, key=lambda x: x.created_at, reverse=True)
    ]

    return LeadDetailResponse(**response)


@router.put("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: int,
    data: LeadUpdate,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Actualiza un lead (cambiar pestaña, estado, datos de contacto).
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    update_data = data.model_dump(exclude_unset=True)

    # Convertir tab string a enum
    if "tab" in update_data:
        update_data["tab"] = LeadTab(update_data["tab"])

    for field, value in update_data.items():
        setattr(lead, field, value)

    # Marcar como revisado si se mueve de NEW
    if lead.tab != LeadTab.NEW and not lead.is_reviewed:
        lead.is_reviewed = True
        lead.reviewed_at = datetime.utcnow()

    db.commit()
    db.refresh(lead)

    return LeadResponse(**lead_to_response(lead))


@router.post("/{lead_id}/move/{tab}")
async def move_lead_to_tab(
    lead_id: int,
    tab: LeadTabEnum,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Mueve un lead a otra pestaña.
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    lead.tab = LeadTab(tab.value)

    if lead.tab != LeadTab.NEW and not lead.is_reviewed:
        lead.is_reviewed = True
        lead.reviewed_at = datetime.utcnow()

    db.commit()

    return {"message": f"Lead movido a {tab.value}"}


@router.post("/{lead_id}/extract-contact")
async def extract_contact_info(
    lead_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Extrae información de contacto de la web del lead.
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    scraper = ScraperService()
    result = await scraper.extract_contact_info(lead.url)

    if result["success"]:
        if result["email"] and not lead.email:
            lead.email = result["email"]
        if result["phone"] and not lead.phone:
            lead.phone = result["phone"]
        if result["cif"] and not lead.cif:
            lead.cif = result["cif"]

        lead.contact_extracted = True
        lead.contact_extracted_at = datetime.utcnow()
        db.commit()

    return {
        "success": result["success"],
        "email": result["email"],
        "phone": result["phone"],
        "cif": result["cif"],
        "emails_found": result.get("emails_found", []),
        "phones_found": result.get("phones_found", []),
        "pages_visited": result.get("pages_visited", [])
    }


@router.delete("/{lead_id}")
async def delete_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Elimina un lead permanentemente.
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    db.delete(lead)
    db.commit()

    return {"message": "Lead eliminado correctamente"}


# ============ Notas ============
@router.get("/{lead_id}/notes", response_model=List[NoteResponse])
async def get_lead_notes(
    lead_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Obtiene las notas de un lead.
    """
    notes = db.query(Note).filter(
        Note.lead_id == lead_id
    ).order_by(Note.created_at.desc()).all()

    return notes


@router.post("/{lead_id}/notes", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    lead_id: int,
    data: NoteBase,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Crea una nota para un lead.
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    note = Note(
        lead_id=lead_id,
        content=data.content
    )
    db.add(note)
    db.commit()
    db.refresh(note)

    return note


@router.delete("/{lead_id}/notes/{note_id}")
async def delete_note(
    lead_id: int,
    note_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Elimina una nota.
    """
    note = db.query(Note).filter(
        Note.id == note_id,
        Note.lead_id == lead_id
    ).first()
    if not note:
        raise HTTPException(status_code=404, detail="Nota no encontrada")

    db.delete(note)
    db.commit()

    return {"message": "Nota eliminada correctamente"}


# ============ Exportación ============
@router.get("/country/{country_id}/export")
async def export_leads(
    country_id: int,
    tab: Optional[LeadTabEnum] = None,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Exporta leads a Excel.
    """
    query = db.query(Lead).filter(Lead.country_id == country_id)

    if tab:
        query = query.filter(Lead.tab == LeadTab(tab.value))

    leads = query.order_by(Lead.found_at.desc()).all()

    if not leads:
        raise HTTPException(status_code=404, detail="No hay leads para exportar")

    exporter = ExcelExportService()
    excel_bytes = exporter.export_leads(leads)

    filename = f"leads_{tab.value if tab else 'todos'}_{datetime.now().strftime('%Y%m%d')}.xlsx"

    return StreamingResponse(
        io.BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/country/{country_id}/export-all")
async def export_all_tabs(
    country_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Exporta todos los leads de todas las pestañas a un Excel con múltiples hojas.
    """
    leads_by_tab = {}
    for tab in LeadTab:
        leads = db.query(Lead).filter(
            Lead.country_id == country_id,
            Lead.tab == tab
        ).order_by(Lead.found_at.desc()).all()
        if leads:
            leads_by_tab[tab] = leads

    if not leads_by_tab:
        raise HTTPException(status_code=404, detail="No hay leads para exportar")

    exporter = ExcelExportService()
    excel_bytes = exporter.export_all_tabs(leads_by_tab)

    filename = f"leads_completo_{datetime.now().strftime('%Y%m%d')}.xlsx"

    return StreamingResponse(
        io.BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
