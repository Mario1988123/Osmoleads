"""
Esquemas Pydantic para validación de datos de la API.
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ============ Auth ============
class PinVerify(BaseModel):
    pin: str = Field(..., min_length=1, max_length=50)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


# ============ Country ============
class CountryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=2, max_length=10)
    language: str = Field(default="es", max_length=10)
    flag_image: Optional[str] = None


class CountryCreate(CountryBase):
    pass


class CountryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    code: Optional[str] = Field(None, min_length=2, max_length=10)
    language: Optional[str] = Field(None, max_length=10)
    flag_image: Optional[str] = None
    is_active: Optional[bool] = None


class CountryResponse(CountryBase):
    id: int
    is_active: bool
    created_at: datetime
    keywords_count: int = 0
    leads_count: int = 0

    class Config:
        from_attributes = True


# ============ Keyword ============
class KeywordBase(BaseModel):
    text: str = Field(..., min_length=1, max_length=255)
    category: Optional[str] = Field(None, max_length=50)
    results_per_search: int = Field(default=5, ge=1, le=10)


class KeywordCreate(KeywordBase):
    country_id: int


class KeywordUpdate(BaseModel):
    text: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[str] = Field(None, max_length=50)
    results_per_search: Optional[int] = Field(None, ge=1, le=10)
    is_active: Optional[bool] = None


class KeywordResponse(KeywordBase):
    id: int
    country_id: int
    is_active: bool
    total_searches: int
    total_results: int
    last_search_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Lead ============
class LeadTabEnum(str, Enum):
    new = "new"
    leads = "leads"
    doubts = "doubts"
    discarded = "discarded"
    marketplace = "marketplace"


class LeadBase(BaseModel):
    name: str
    url: str
    domain: str
    snippet: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    cif: Optional[str] = None


class LeadUpdate(BaseModel):
    tab: Optional[LeadTabEnum] = None
    status_id: Optional[int] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    cif: Optional[str] = None
    is_reviewed: Optional[bool] = None


class NoteBase(BaseModel):
    content: str = Field(..., min_length=1)


class NoteResponse(NoteBase):
    id: int
    lead_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LeadResponse(LeadBase):
    id: int
    country_id: int
    keyword_id: Optional[int]
    status_id: Optional[int]
    tab: LeadTabEnum
    is_reviewed: bool
    found_at: datetime
    reviewed_at: Optional[datetime]
    contact_extracted: bool
    keyword_text: Optional[str] = None
    status_name: Optional[str] = None
    status_color: Optional[str] = None
    notes_count: int = 0

    class Config:
        from_attributes = True


class LeadDetailResponse(LeadResponse):
    notes: List[NoteResponse] = []


# ============ Status ============
class StatusBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    color: str = Field(default="#6B7280", max_length=20)
    icon: Optional[str] = Field(None, max_length=50)
    order: int = Field(default=0)


class StatusCreate(StatusBase):
    pass


class StatusUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    color: Optional[str] = Field(None, max_length=20)
    icon: Optional[str] = Field(None, max_length=50)
    order: Optional[int] = None


class StatusResponse(StatusBase):
    id: int
    is_default: bool
    is_system: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Search ============
class SearchRequest(BaseModel):
    country_id: int
    keyword_ids: Optional[List[int]] = None  # None = todas las activas


class SearchResponse(BaseModel):
    success: bool
    message: str
    total_results: int = 0
    new_leads: int = 0
    searches_used: int = 0
    remaining_searches: int = 0


class SearchStats(BaseModel):
    searches_today: int
    max_searches: int
    remaining: int
    is_unlimited: bool


# ============ Image Search ============
class ImageSearchResponse(BaseModel):
    success: bool
    error: Optional[str] = None
    labels: List[dict] = []
    web_entities: List[dict] = []
    pages_with_image: List[dict] = []
    text_detected: str = ""


# ============ Keyword Suggestion ============
class KeywordSuggestionResponse(BaseModel):
    id: int
    text: str
    source: Optional[str]
    frequency: int
    websites_count: int
    is_ignored: bool
    is_added: bool

    class Config:
        from_attributes = True


# ============ Settings ============
class SettingsUpdate(BaseModel):
    max_searches: Optional[int] = Field(None, ge=0)
    access_pin: Optional[str] = Field(None, min_length=4, max_length=50)


class SettingsResponse(BaseModel):
    max_searches: int
    searches_today: int
    pin_configured: bool


# ============ Marketplace ============
class MarketplaceCreate(BaseModel):
    domain: str = Field(..., min_length=3, max_length=255)
    name: Optional[str] = Field(None, max_length=255)


class MarketplaceResponse(BaseModel):
    id: int
    domain: str
    name: Optional[str]
    is_system: bool
    created_at: datetime

    class Config:
        from_attributes = True
