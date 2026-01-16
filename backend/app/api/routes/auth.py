"""
Endpoints de autenticación.
"""
from fastapi import APIRouter, HTTPException, status
from datetime import timedelta

from app.core.security import verify_pin, create_access_token
from app.core.config import settings
from app.api.schemas import PinVerify, TokenResponse

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/verify-pin", response_model=TokenResponse)
async def verify_access_pin(data: PinVerify):
    """
    Verifica el PIN de acceso y devuelve un token JWT.
    """
    if not verify_pin(data.pin):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="PIN incorrecto"
        )

    # Crear token
    expires = timedelta(hours=settings.PIN_EXPIRY_HOURS)
    token = create_access_token(expires_delta=expires)

    return TokenResponse(
        access_token=token,
        expires_in=settings.PIN_EXPIRY_HOURS * 3600
    )


@router.post("/logout")
async def logout():
    """
    Endpoint de logout (el token se invalida en el cliente).
    """
    return {"message": "Sesión cerrada correctamente"}
