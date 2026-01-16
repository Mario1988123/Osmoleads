"""
Servicio de búsqueda por imagen usando Google Vision API.
También incluye OCR con Tesseract para extraer texto de imágenes.
"""
import base64
import httpx
from typing import Dict, List, Optional
from pathlib import Path
import pytesseract
from PIL import Image
import io

from app.core.config import settings


class ImageSearchService:
    """Servicio para búsqueda de productos por imagen."""

    VISION_API_URL = "https://vision.googleapis.com/v1/images:annotate"

    def __init__(self):
        self.api_key = settings.GOOGLE_API_KEY

    async def search_by_image(self, image_data: bytes) -> Dict:
        """
        Busca información sobre una imagen de producto.

        Args:
            image_data: Bytes de la imagen

        Returns:
            Dict con resultados de la búsqueda
        """
        result = {
            "success": True,
            "error": None,
            "labels": [],  # Etiquetas detectadas
            "web_entities": [],  # Entidades web relacionadas
            "similar_images": [],  # Imágenes similares
            "pages_with_image": [],  # Páginas donde aparece
            "products": [],  # Productos detectados
            "text_detected": ""  # Texto en la imagen (OCR)
        }

        try:
            # Codificar imagen en base64
            image_base64 = base64.b64encode(image_data).decode("utf-8")

            # Preparar request para Vision API
            request_body = {
                "requests": [{
                    "image": {"content": image_base64},
                    "features": [
                        {"type": "LABEL_DETECTION", "maxResults": 10},
                        {"type": "WEB_DETECTION", "maxResults": 10},
                        {"type": "PRODUCT_SEARCH", "maxResults": 10},
                        {"type": "TEXT_DETECTION", "maxResults": 1}
                    ]
                }]
            }

            # Llamar a Vision API
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.VISION_API_URL}?key={self.api_key}",
                    json=request_body
                )
                response.raise_for_status()
                data = response.json()

            # Procesar respuesta
            if "responses" in data and data["responses"]:
                resp = data["responses"][0]

                # Etiquetas (qué es el objeto)
                if "labelAnnotations" in resp:
                    result["labels"] = [
                        {
                            "description": label.get("description", ""),
                            "score": round(label.get("score", 0) * 100, 1)
                        }
                        for label in resp["labelAnnotations"]
                    ]

                # Detección web
                if "webDetection" in resp:
                    web = resp["webDetection"]

                    # Entidades web (qué es según la web)
                    if "webEntities" in web:
                        result["web_entities"] = [
                            {
                                "description": entity.get("description", ""),
                                "score": round(entity.get("score", 0) * 100, 1)
                            }
                            for entity in web["webEntities"]
                            if entity.get("description")
                        ]

                    # Imágenes similares
                    if "visuallySimilarImages" in web:
                        result["similar_images"] = [
                            img.get("url", "")
                            for img in web["visuallySimilarImages"][:5]
                        ]

                    # Páginas donde aparece la imagen
                    if "pagesWithMatchingImages" in web:
                        result["pages_with_image"] = [
                            {
                                "url": page.get("url", ""),
                                "title": page.get("pageTitle", "")
                            }
                            for page in web["pagesWithMatchingImages"][:10]
                        ]

                # Texto detectado (OCR de Google Vision)
                if "textAnnotations" in resp and resp["textAnnotations"]:
                    result["text_detected"] = resp["textAnnotations"][0].get("description", "")

                # Productos detectados
                if "productSearchResults" in resp:
                    results_data = resp["productSearchResults"].get("results", [])
                    result["products"] = [
                        {
                            "name": p.get("product", {}).get("displayName", ""),
                            "score": round(p.get("score", 0) * 100, 1)
                        }
                        for p in results_data
                    ]

        except httpx.HTTPStatusError as e:
            result["success"] = False
            result["error"] = f"Error API: {e.response.status_code}"
        except Exception as e:
            result["success"] = False
            result["error"] = str(e)

        return result


class OCRService:
    """Servicio de OCR usando Tesseract (gratuito)."""

    def __init__(self):
        # Configuración de Tesseract
        self.config = "--oem 3 --psm 6"  # Modo LSTM + bloque de texto

    def extract_text(self, image_data: bytes, language: str = "spa") -> Dict:
        """
        Extrae texto de una imagen usando Tesseract.

        Args:
            image_data: Bytes de la imagen
            language: Código de idioma (spa, fra, eng)

        Returns:
            Dict con texto extraído e información de contacto
        """
        result = {
            "success": True,
            "error": None,
            "raw_text": "",
            "emails": [],
            "phones": [],
            "confidence": 0
        }

        try:
            # Cargar imagen
            image = Image.open(io.BytesIO(image_data))

            # Convertir a RGB si es necesario
            if image.mode != "RGB":
                image = image.convert("RGB")

            # Mapeo de idiomas para Tesseract
            lang_map = {
                "es": "spa",
                "spa": "spa",
                "fr": "fra",
                "fra": "fra",
                "en": "eng",
                "eng": "eng",
                "pt": "por",
                "por": "por"
            }
            tess_lang = lang_map.get(language, "spa")

            # Extraer texto
            text = pytesseract.image_to_string(
                image,
                lang=tess_lang,
                config=self.config
            )

            result["raw_text"] = text.strip()

            # Extraer emails del texto
            import re
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            result["emails"] = re.findall(email_pattern, text)

            # Extraer teléfonos del texto
            phone_pattern = r'(?:\+34\s?|0034\s?)?[6789]\d{2}[\s.-]?\d{2}[\s.-]?\d{2}[\s.-]?\d{2}'
            result["phones"] = re.findall(phone_pattern, text)

            # Obtener confianza del OCR
            data = pytesseract.image_to_data(image, lang=tess_lang, output_type=pytesseract.Output.DICT)
            confidences = [int(c) for c in data["conf"] if c != "-1" and int(c) > 0]
            if confidences:
                result["confidence"] = round(sum(confidences) / len(confidences), 1)

        except pytesseract.TesseractNotFoundError:
            result["success"] = False
            result["error"] = "Tesseract no está instalado en el servidor"
        except Exception as e:
            result["success"] = False
            result["error"] = str(e)

        return result

    def extract_from_url(self, image_url: str, language: str = "spa") -> Dict:
        """Descarga una imagen de URL y extrae el texto."""
        import httpx

        try:
            response = httpx.get(image_url, timeout=10)
            response.raise_for_status()
            return self.extract_text(response.content, language)
        except Exception as e:
            return {
                "success": False,
                "error": f"No se pudo descargar la imagen: {str(e)}",
                "raw_text": "",
                "emails": [],
                "phones": [],
                "confidence": 0
            }
