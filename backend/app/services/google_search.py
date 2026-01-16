"""
Servicio de búsqueda en Google Custom Search API.
Gestiona las búsquedas y el control de límites.
"""
import httpx
from typing import List, Dict, Optional, Tuple
from datetime import datetime, date
from urllib.parse import urlparse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.lead import Lead, LeadTab
from app.models.keyword import Keyword
from app.models.search_log import SearchLog
from app.models.marketplace import Marketplace
from app.models.settings import AppSettings


class GoogleSearchService:
    """Servicio para búsquedas en Google Custom Search API."""

    BASE_URL = "https://www.googleapis.com/customsearch/v1"

    def __init__(self, db: Session):
        self.db = db
        self.searches_today = self._get_searches_today()
        self.max_searches = self._get_max_searches()

    def _get_searches_today(self) -> int:
        """Obtiene el número de búsquedas realizadas hoy."""
        today = date.today()
        count = self.db.query(SearchLog).filter(
            SearchLog.searched_at >= datetime.combine(today, datetime.min.time())
        ).count()
        return count

    def _get_max_searches(self) -> int:
        """Obtiene el límite máximo de búsquedas configurado."""
        setting = self.db.query(AppSettings).filter(
            AppSettings.key == "max_searches"
        ).first()
        if setting and setting.value:
            try:
                return int(setting.value)
            except ValueError:
                pass
        return settings.MAX_SEARCHES_DEFAULT

    def can_search(self) -> Tuple[bool, str]:
        """Verifica si se puede realizar una búsqueda."""
        if self.max_searches == 0:  # 0 = ilimitado
            return True, ""

        if self.searches_today >= self.max_searches:
            return False, f"Límite de búsquedas alcanzado ({self.searches_today}/{self.max_searches})"

        return True, ""

    def get_remaining_searches(self) -> int:
        """Obtiene el número de búsquedas restantes."""
        if self.max_searches == 0:
            return -1  # Ilimitado
        return max(0, self.max_searches - self.searches_today)

    async def search(
        self,
        keyword: Keyword,
        country_code: str = "es",
        language: str = "es"
    ) -> Dict:
        """
        Realiza una búsqueda en Google Custom Search API.

        Args:
            keyword: Objeto Keyword con la palabra clave
            country_code: Código del país (es, fr, pt...)
            language: Idioma de los resultados (es, fr, pt...)

        Returns:
            Dict con resultados y metadatos
        """
        # Verificar si podemos buscar
        can_search, error_msg = self.can_search()
        if not can_search:
            return {
                "success": False,
                "error": error_msg,
                "results": [],
                "new_leads": 0
            }

        # Parámetros de búsqueda
        params = {
            "key": settings.GOOGLE_API_KEY,
            "cx": settings.GOOGLE_SEARCH_ENGINE_ID,
            "q": keyword.text,
            "num": min(keyword.results_per_search, 10),  # Google máximo 10
            "gl": country_code,  # Geolocalización
            "lr": f"lang_{language}",  # Idioma
            "dateRestrict": "y1"  # Último año
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.BASE_URL, params=params)
                response.raise_for_status()
                data = response.json()

            # Procesar resultados
            items = data.get("items", [])
            results = []
            new_leads = 0

            for item in items:
                processed = self._process_result(item, keyword)
                if processed:
                    results.append(processed)
                    if processed.get("is_new"):
                        new_leads += 1

            # Registrar búsqueda
            log = SearchLog(
                country_id=keyword.country_id,
                keyword_id=keyword.id,
                keyword_text=keyword.text,
                results_count=len(items),
                new_leads_count=new_leads,
                is_success=True
            )
            self.db.add(log)

            # Actualizar keyword
            keyword.total_searches += 1
            keyword.total_results += len(items)
            keyword.last_search_at = datetime.utcnow()

            self.db.commit()
            self.searches_today += 1

            return {
                "success": True,
                "results": results,
                "total_results": len(items),
                "new_leads": new_leads,
                "searches_today": self.searches_today,
                "remaining": self.get_remaining_searches()
            }

        except httpx.HTTPStatusError as e:
            error_msg = f"Error HTTP: {e.response.status_code}"
            self._log_error(keyword, error_msg)
            return {"success": False, "error": error_msg, "results": [], "new_leads": 0}

        except Exception as e:
            error_msg = str(e)
            self._log_error(keyword, error_msg)
            return {"success": False, "error": error_msg, "results": [], "new_leads": 0}

    def _process_result(self, item: Dict, keyword: Keyword) -> Optional[Dict]:
        """
        Procesa un resultado de Google y lo guarda si es válido.

        Returns:
            Dict con los datos del lead o None si no es válido
        """
        url = item.get("link", "")
        title = item.get("title", "")
        snippet = item.get("snippet", "")

        # Extraer dominio
        domain = self._extract_domain(url)
        if not domain:
            return None

        # Verificar si es marketplace
        if self._is_marketplace(domain):
            tab = LeadTab.MARKETPLACE
        # Verificar si está excluido
        elif self._is_excluded(domain):
            return None
        else:
            tab = LeadTab.NEW

        # Verificar si ya existe
        existing = self.db.query(Lead).filter(
            Lead.country_id == keyword.country_id,
            Lead.domain == domain
        ).first()

        if existing:
            return {
                "url": url,
                "domain": domain,
                "title": title,
                "is_new": False,
                "lead_id": existing.id
            }

        # Crear nuevo lead
        lead = Lead(
            country_id=keyword.country_id,
            keyword_id=keyword.id,
            name=title[:500] if title else domain,
            url=url,
            domain=domain,
            snippet=snippet,
            tab=tab
        )
        self.db.add(lead)
        self.db.flush()  # Para obtener el ID

        return {
            "url": url,
            "domain": domain,
            "title": title,
            "is_new": True,
            "lead_id": lead.id,
            "tab": tab.value
        }

    def _extract_domain(self, url: str) -> Optional[str]:
        """Extrae el dominio principal de una URL."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()

            # Quitar www.
            if domain.startswith("www."):
                domain = domain[4:]

            # Quitar subdominios comunes
            for prefix in ["shop.", "tienda.", "store.", "blog.", "m."]:
                if domain.startswith(prefix):
                    domain = domain[len(prefix):]

            return domain if domain else None
        except Exception:
            return None

    def _is_marketplace(self, domain: str) -> bool:
        """Verifica si un dominio es un marketplace."""
        # Verificar en base de datos
        marketplace = self.db.query(Marketplace).filter(
            Marketplace.domain.ilike(f"%{domain}%")
        ).first()
        if marketplace:
            return True

        # Verificar en lista de configuración
        domain_lower = domain.lower()
        for mp in settings.MARKETPLACES:
            if mp in domain_lower:
                return True

        return False

    def _is_excluded(self, domain: str) -> bool:
        """Verifica si un dominio debe excluirse."""
        domain_lower = domain.lower()
        for excluded in settings.EXCLUDED_DOMAINS:
            if excluded in domain_lower:
                return True
        return False

    def _log_error(self, keyword: Keyword, error_msg: str):
        """Registra un error de búsqueda."""
        log = SearchLog(
            country_id=keyword.country_id,
            keyword_id=keyword.id,
            keyword_text=keyword.text,
            results_count=0,
            new_leads_count=0,
            is_success=False,
            error_message=error_msg[:500]
        )
        self.db.add(log)
        self.db.commit()
