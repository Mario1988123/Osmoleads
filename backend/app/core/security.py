"""
Funciones de seguridad: verificación de PIN y tokens.
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from app.core.config import settings

# Algoritmo para JWT
ALGORITHM = "HS256"


def verify_pin(pin: str) -> bool:
    """
    Verifica si el PIN introducido es correcto.
    """
    return pin == settings.ACCESS_PIN


def create_access_token(expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token JWT de acceso.
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.PIN_EXPIRY_HOURS)

    to_encode = {
        "exp": expire,
        "sub": "osmoleads_access",
        "iat": datetime.utcnow()
    }

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> bool:
    """
    Verifica si un token JWT es válido.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub") == "osmoleads_access"
    except JWTError:
        return False
