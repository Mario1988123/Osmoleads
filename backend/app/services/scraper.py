"""
Servicio de scraping para extraer información de contacto de webs.
Extrae: email, teléfono, CIF/NIF
"""
import re
import httpx
from typing import Dict, Optional, List
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import asyncio

from app.core.config import settings


class ScraperService:
    """Servicio para extraer información de contacto de webs."""

    # Páginas donde buscar contacto
    CONTACT_PATHS = [
        "/contacto",
        "/contact",
        "/contactenos",
        "/aviso-legal",
        "/legal",
        "/aviso_legal",
        "/politica-privacidad",
        "/privacy",
        "/empresa",
        "/about",
        "/about-us",
        "/quienes-somos",
        "/nosotros",
        "/informacion",
        "/info"
    ]

    # Patrones regex
    EMAIL_PATTERN = re.compile(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    )

    # Teléfonos españoles y europeos
    PHONE_PATTERNS = [
        # España: +34 o 34 seguido de 9 dígitos empezando por 6, 7, 8, 9
        re.compile(r'(?:\+34\s?|0034\s?)?[6789]\d{2}[\s.-]?\d{2}[\s.-]?\d{2}[\s.-]?\d{2}\b'),
        # Francia: +33
        re.compile(r'(?:\+33\s?|0033\s?)?[0-9]\d{2}[\s.-]?\d{2}[\s.-]?\d{2}[\s.-]?\d{2}\b'),
        # Portugal: +351
        re.compile(r'(?:\+351\s?|00351\s?)?[0-9]\d{2}[\s.-]?\d{3}[\s.-]?\d{3}\b'),
        # Genérico europeo
        re.compile(r'\+\d{2,3}[\s.-]?\d{2,4}[\s.-]?\d{2,4}[\s.-]?\d{2,4}[\s.-]?\d{2,4}')
    ]

    # CIF/NIF español
    CIF_PATTERN = re.compile(r'\b[A-Z]\d{8}\b|\b\d{8}[A-Z]\b')

    # Emails a excluir
    EXCLUDED_EMAILS = [
        "example@", "test@", "info@example", "noreply@",
        "no-reply@", "admin@admin", "@sentry.io", "@google",
        "@facebook", "@twitter", "@instagram", ".png", ".jpg",
        ".gif", ".webp", "@2x.", "@3x."
    ]

    def __init__(self):
        self.timeout = settings.SCRAPING_TIMEOUT
        self.delay = settings.SCRAPING_DELAY
        self.headers = {
            "User-Agent": settings.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive"
        }

    async def extract_contact_info(self, url: str, max_pages: int = 3) -> Dict:
        """
        Extrae información de contacto de una web.

        Args:
            url: URL base de la web
            max_pages: Número máximo de páginas a visitar

        Returns:
            Dict con email, phone, cif encontrados
        """
        result = {
            "email": None,
            "phone": None,
            "cif": None,
            "emails_found": [],
            "phones_found": [],
            "pages_visited": [],
            "success": True,
            "error": None
        }

        # Normalizar URL base
        base_url = self._normalize_url(url)
        if not base_url:
            result["success"] = False
            result["error"] = "URL inválida"
            return result

        # Lista de páginas a visitar
        pages_to_visit = [base_url]
        for path in self.CONTACT_PATHS[:max_pages - 1]:
            pages_to_visit.append(urljoin(base_url, path))

        # Visitar páginas
        for page_url in pages_to_visit[:max_pages]:
            try:
                page_result = await self._scrape_page(page_url)
                result["pages_visited"].append(page_url)

                if page_result:
                    # Acumular resultados
                    result["emails_found"].extend(page_result.get("emails", []))
                    result["phones_found"].extend(page_result.get("phones", []))

                    if page_result.get("cif") and not result["cif"]:
                        result["cif"] = page_result["cif"]

                # Si ya tenemos email y teléfono, podemos parar
                if result["emails_found"] and result["phones_found"] and result["cif"]:
                    break

                # Delay entre peticiones
                await asyncio.sleep(self.delay)

            except Exception as e:
                continue

        # Seleccionar mejores resultados
        result["email"] = self._select_best_email(result["emails_found"])
        result["phone"] = self._select_best_phone(result["phones_found"])

        # Limpiar duplicados
        result["emails_found"] = list(set(result["emails_found"]))
        result["phones_found"] = list(set(result["phones_found"]))

        return result

    async def _scrape_page(self, url: str) -> Optional[Dict]:
        """Extrae información de una página específica."""
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
                verify=False  # Algunas webs tienen SSL mal configurado
            ) as client:
                response = await client.get(url, headers=self.headers)

                if response.status_code != 200:
                    return None

                content_type = response.headers.get("content-type", "")
                if "text/html" not in content_type:
                    return None

                html = response.text
                soup = BeautifulSoup(html, "lxml")

                # Extraer texto visible
                text = soup.get_text(separator=" ", strip=True)

                # También buscar en atributos href y data
                for a in soup.find_all("a", href=True):
                    href = a.get("href", "")
                    if href.startswith("mailto:"):
                        text += " " + href[7:]
                    elif href.startswith("tel:"):
                        text += " " + href[4:]

                return {
                    "emails": self._find_emails(text),
                    "phones": self._find_phones(text),
                    "cif": self._find_cif(text)
                }

        except Exception:
            return None

    def _find_emails(self, text: str) -> List[str]:
        """Encuentra emails en el texto."""
        emails = self.EMAIL_PATTERN.findall(text)
        # Filtrar emails no deseados
        valid_emails = []
        for email in emails:
            email_lower = email.lower()
            if not any(exc in email_lower for exc in self.EXCLUDED_EMAILS):
                valid_emails.append(email.lower())
        return valid_emails

    def _find_phones(self, text: str) -> List[str]:
        """Encuentra teléfonos en el texto."""
        phones = []
        for pattern in self.PHONE_PATTERNS:
            matches = pattern.findall(text)
            for match in matches:
                # Limpiar formato
                clean_phone = re.sub(r'[\s.-]', '', match)
                if len(clean_phone) >= 9:  # Mínimo 9 dígitos
                    phones.append(clean_phone)
        return phones

    def _find_cif(self, text: str) -> Optional[str]:
        """Encuentra CIF/NIF en el texto."""
        matches = self.CIF_PATTERN.findall(text)
        if matches:
            return matches[0].upper()
        return None

    def _select_best_email(self, emails: List[str]) -> Optional[str]:
        """Selecciona el mejor email de la lista."""
        if not emails:
            return None

        # Prioridad: info@, contacto@, comercial@, ventas@
        priorities = ["info@", "contacto@", "contact@", "comercial@", "ventas@", "sales@"]

        for priority in priorities:
            for email in emails:
                if email.startswith(priority):
                    return email

        # Si no hay prioritarios, devolver el primero
        return emails[0]

    def _select_best_phone(self, phones: List[str]) -> Optional[str]:
        """Selecciona el mejor teléfono de la lista."""
        if not phones:
            return None

        # Priorizar móviles (empiezan por 6 o 7 en España)
        for phone in phones:
            digits = re.sub(r'\D', '', phone)
            if len(digits) >= 9:
                # Si tiene prefijo internacional, verificar después del prefijo
                if digits.startswith("34") and len(digits) >= 11:
                    if digits[2] in "67":
                        return self._format_phone(phone)
                elif digits[0] in "67":
                    return self._format_phone(phone)

        # Si no hay móvil, devolver el primero
        return self._format_phone(phones[0]) if phones else None

    def _format_phone(self, phone: str) -> str:
        """Formatea un teléfono para visualización."""
        digits = re.sub(r'\D', '', phone)

        # Si es español sin prefijo, añadir +34
        if len(digits) == 9 and digits[0] in "6789":
            return f"+34 {digits[:3]} {digits[3:5]} {digits[5:7]} {digits[7:]}"

        # Si ya tiene prefijo
        if len(digits) >= 11:
            if digits.startswith("34"):
                return f"+{digits[:2]} {digits[2:5]} {digits[5:7]} {digits[7:9]} {digits[9:]}"

        return phone

    def _normalize_url(self, url: str) -> Optional[str]:
        """Normaliza una URL añadiendo protocolo si falta."""
        if not url:
            return None

        url = url.strip()

        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                return None
            return f"{parsed.scheme}://{parsed.netloc}/"
        except Exception:
            return None


class KeywordAnalyzer:
    """Analiza webs para sugerir nuevas keywords."""

    # Palabras comunes a ignorar (stopwords)
    STOPWORDS = {
        "es": ["de", "la", "el", "en", "y", "a", "los", "las", "del", "con", "para",
               "un", "una", "por", "que", "se", "su", "al", "es", "lo", "como",
               "más", "o", "pero", "sus", "le", "ya", "este", "ha", "me", "si",
               "porque", "esta", "son", "entre", "cuando", "muy", "sin", "sobre",
               "también", "ser", "hay", "puede", "todos", "así", "nos", "ni"],
        "fr": ["de", "la", "le", "et", "en", "un", "une", "du", "des", "les", "est",
               "dans", "que", "pour", "au", "sur", "par", "pas", "plus", "avec"],
        "en": ["the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
               "of", "with", "by", "from", "as", "is", "was", "are", "were", "been"]
    }

    def __init__(self):
        self.headers = {
            "User-Agent": settings.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "es-ES,es;q=0.9"
        }

    async def analyze_website(self, url: str, language: str = "es") -> Dict:
        """
        Analiza una web y extrae keywords potenciales.

        Returns:
            Dict con keywords encontradas y su frecuencia
        """
        result = {
            "meta_keywords": [],
            "meta_description": "",
            "title": "",
            "h1_tags": [],
            "h2_tags": [],
            "suggested_keywords": [],
            "success": True,
            "error": None
        }

        try:
            async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
                response = await client.get(url, headers=self.headers)

                if response.status_code != 200:
                    result["success"] = False
                    result["error"] = f"HTTP {response.status_code}"
                    return result

                soup = BeautifulSoup(response.text, "lxml")

                # Extraer meta keywords
                meta_kw = soup.find("meta", attrs={"name": "keywords"})
                if meta_kw and meta_kw.get("content"):
                    keywords = [k.strip() for k in meta_kw["content"].split(",")]
                    result["meta_keywords"] = [k for k in keywords if k]

                # Extraer meta description
                meta_desc = soup.find("meta", attrs={"name": "description"})
                if meta_desc and meta_desc.get("content"):
                    result["meta_description"] = meta_desc["content"]

                # Extraer title
                title_tag = soup.find("title")
                if title_tag:
                    result["title"] = title_tag.get_text(strip=True)

                # Extraer H1
                for h1 in soup.find_all("h1")[:3]:
                    text = h1.get_text(strip=True)
                    if text:
                        result["h1_tags"].append(text)

                # Extraer H2
                for h2 in soup.find_all("h2")[:5]:
                    text = h2.get_text(strip=True)
                    if text:
                        result["h2_tags"].append(text)

                # Generar sugerencias de keywords
                all_text = " ".join([
                    result["meta_description"],
                    result["title"],
                    " ".join(result["h1_tags"]),
                    " ".join(result["h2_tags"])
                ])

                result["suggested_keywords"] = self._extract_keywords(all_text, language)

        except Exception as e:
            result["success"] = False
            result["error"] = str(e)

        return result

    def _extract_keywords(self, text: str, language: str = "es") -> List[Dict]:
        """Extrae keywords relevantes del texto."""
        # Limpiar texto
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = text.split()

        # Filtrar stopwords
        stopwords = self.STOPWORDS.get(language, self.STOPWORDS["es"])
        words = [w for w in words if w not in stopwords and len(w) > 3]

        # Contar frecuencia
        freq = {}
        for word in words:
            freq[word] = freq.get(word, 0) + 1

        # Ordenar por frecuencia
        sorted_keywords = sorted(freq.items(), key=lambda x: x[1], reverse=True)

        return [
            {"keyword": kw, "frequency": count}
            for kw, count in sorted_keywords[:20]
        ]
