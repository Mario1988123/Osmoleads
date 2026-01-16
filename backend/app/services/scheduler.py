"""
Servicio de tareas programadas.
Ejecuta búsquedas automáticas según la configuración.
"""
import asyncio
import logging
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.country import Country
from app.models.keyword import Keyword
from app.services.google_search import GoogleSearchService

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("osmoleads.scheduler")


class SchedulerService:
    """Servicio para ejecutar búsquedas programadas."""

    def __init__(self, db: Session):
        self.db = db
        self.search_service = GoogleSearchService(db)

    async def run_all_searches(self) -> dict:
        """
        Ejecuta búsquedas para todos los países y keywords activos.

        Returns:
            Dict con estadísticas de la ejecución
        """
        logger.info("Iniciando búsquedas programadas...")

        stats = {
            "started_at": datetime.utcnow().isoformat(),
            "countries_processed": 0,
            "keywords_processed": 0,
            "total_searches": 0,
            "new_leads": 0,
            "errors": [],
            "finished_at": None
        }

        try:
            # Obtener países activos
            countries = self.db.query(Country).filter(
                Country.is_active == True
            ).all()

            for country in countries:
                logger.info(f"Procesando país: {country.name}")
                stats["countries_processed"] += 1

                # Obtener keywords activas del país
                keywords = self.db.query(Keyword).filter(
                    Keyword.country_id == country.id,
                    Keyword.is_active == True
                ).all()

                for keyword in keywords:
                    # Verificar si podemos seguir buscando
                    can_search, error_msg = self.search_service.can_search()
                    if not can_search:
                        logger.warning(f"Límite alcanzado: {error_msg}")
                        stats["errors"].append(error_msg)
                        break

                    logger.info(f"  Buscando: {keyword.text}")

                    result = await self.search_service.search(
                        keyword=keyword,
                        country_code=country.code,
                        language=country.language
                    )

                    stats["keywords_processed"] += 1
                    stats["total_searches"] += 1

                    if result["success"]:
                        stats["new_leads"] += result.get("new_leads", 0)
                        logger.info(f"    Resultados: {result.get('total_results', 0)}, Nuevos: {result.get('new_leads', 0)}")
                    else:
                        error = result.get("error", "Error desconocido")
                        stats["errors"].append(f"{keyword.text}: {error}")
                        logger.error(f"    Error: {error}")

                    # Pequeña pausa entre búsquedas
                    await asyncio.sleep(1)

                # Verificar límite después de cada país
                can_continue, _ = self.search_service.can_search()
                if not can_continue:
                    break

        except Exception as e:
            logger.exception("Error en búsquedas programadas")
            stats["errors"].append(str(e))

        stats["finished_at"] = datetime.utcnow().isoformat()
        logger.info(f"Búsquedas finalizadas. Nuevos leads: {stats['new_leads']}")

        return stats

    async def run_country_search(self, country_id: int) -> dict:
        """
        Ejecuta búsquedas solo para un país específico.

        Args:
            country_id: ID del país

        Returns:
            Dict con estadísticas
        """
        stats = {
            "started_at": datetime.utcnow().isoformat(),
            "keywords_processed": 0,
            "total_searches": 0,
            "new_leads": 0,
            "errors": [],
            "finished_at": None
        }

        country = self.db.query(Country).filter(Country.id == country_id).first()
        if not country:
            stats["errors"].append("País no encontrado")
            return stats

        logger.info(f"Buscando en: {country.name}")

        keywords = self.db.query(Keyword).filter(
            Keyword.country_id == country_id,
            Keyword.is_active == True
        ).all()

        for keyword in keywords:
            can_search, error_msg = self.search_service.can_search()
            if not can_search:
                stats["errors"].append(error_msg)
                break

            result = await self.search_service.search(
                keyword=keyword,
                country_code=country.code,
                language=country.language
            )

            stats["keywords_processed"] += 1
            stats["total_searches"] += 1

            if result["success"]:
                stats["new_leads"] += result.get("new_leads", 0)
            else:
                stats["errors"].append(f"{keyword.text}: {result.get('error')}")

            await asyncio.sleep(0.5)

        stats["finished_at"] = datetime.utcnow().isoformat()
        return stats


def run_scheduled_search():
    """
    Función para ejecutar desde cron/scheduler externo.
    Se llama desde: python -m backend.app.services.scheduler
    """
    db = SessionLocal()
    try:
        scheduler = SchedulerService(db)
        stats = asyncio.run(scheduler.run_all_searches())
        print(f"Búsqueda completada: {stats['new_leads']} nuevos leads")
        return stats
    finally:
        db.close()


if __name__ == "__main__":
    run_scheduled_search()
