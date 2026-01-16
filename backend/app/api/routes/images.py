"""
Endpoints de búsqueda por imagen y OCR.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.api.schemas import ImageSearchResponse
from app.services.image_search import ImageSearchService, OCRService

router = APIRouter(prefix="/images", tags=["Imágenes"])


@router.post("/search", response_model=ImageSearchResponse)
async def search_by_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Busca información sobre un producto usando una imagen.
    Usa Google Vision API.
    """
    # Verificar tipo de archivo
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")

    # Leer imagen
    content = await file.read()

    # Verificar tamaño (máx 5MB)
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="La imagen es demasiado grande (máx 5MB)")

    # Buscar
    service = ImageSearchService()
    result = await service.search_by_image(content)

    return ImageSearchResponse(**result)


@router.post("/ocr")
async def extract_text_from_image(
    file: UploadFile = File(...),
    language: str = "es",
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Extrae texto de una imagen usando OCR (Tesseract).
    Útil para extraer emails o teléfonos de capturas de pantalla.
    """
    # Verificar tipo de archivo
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")

    # Leer imagen
    content = await file.read()

    # Verificar tamaño
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="La imagen es demasiado grande (máx 10MB)")

    # Extraer texto
    service = OCRService()
    result = service.extract_text(content, language)

    return result


@router.post("/ocr-url")
async def extract_text_from_url(
    url: str,
    language: str = "es",
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    """
    Extrae texto de una imagen por URL.
    """
    service = OCRService()
    result = service.extract_from_url(url, language)

    return result
