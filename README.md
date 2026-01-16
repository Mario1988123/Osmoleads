# Osmoleads v1.0

Sistema de gestión de leads con búsqueda automatizada en Google.

## Descripción

Osmoleads es una aplicación web (PWA) para buscar y gestionar leads empresariales. Permite:

- Buscar empresas en Google por palabras clave
- Organizar leads por países y estados
- Extraer datos de contacto automáticamente (email, teléfono, CIF)
- Buscar productos por imagen
- Exportar leads a Excel
- Gestionar notas y seguimiento de cada lead

## Tecnologías

| Componente | Tecnología |
|------------|------------|
| Backend | Python 3.11 + FastAPI |
| Frontend | React 18 + Vite |
| Base de datos | PostgreSQL |
| Estilos | Tailwind CSS |
| PWA | Vite PWA Plugin |

## Requisitos

- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- Cuenta de Google Cloud (para APIs)

## Estructura del proyecto

```
Osmoleads/
├── backend/                 # API FastAPI
│   ├── app/
│   │   ├── api/            # Endpoints REST
│   │   ├── core/           # Configuración
│   │   ├── models/         # Modelos SQLAlchemy
│   │   └── services/       # Lógica de negocio
│   ├── requirements.txt
│   └── .env.example
├── frontend/               # App React
│   ├── src/
│   │   ├── components/     # Componentes React
│   │   ├── pages/          # Páginas
│   │   ├── services/       # API y store
│   │   └── styles/         # CSS
│   ├── package.json
│   └── vite.config.js
├── docs/
│   ├── INSTALACION.md      # Guía de instalación
│   └── MANUAL_DE_USO.md    # Manual de usuario
└── README.md
```

## Instalación rápida

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Editar .env con tus credenciales
uvicorn app.main:app --reload
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

### 3. Base de datos

```sql
CREATE USER osmoleads_user WITH PASSWORD 'tu_password';
CREATE DATABASE osmoleads_db OWNER osmoleads_user;
```

## Documentación

- [Guía de instalación completa](docs/INSTALACION.md)
- [Manual de uso](docs/MANUAL_DE_USO.md)

## Configuración de Google APIs

1. Crear proyecto en [Google Cloud Console](https://console.cloud.google.com/)
2. Habilitar:
   - Custom Search API
   - Cloud Vision API (opcional, para búsqueda por imagen)
3. Crear credenciales (API Key)
4. Crear motor de búsqueda en [Programmable Search Engine](https://programmablesearchengine.google.com/)

## Variables de entorno

### Backend (.env)

```env
DATABASE_URL=postgresql://user:pass@localhost:5432/osmoleads_db
GOOGLE_API_KEY=tu_api_key
GOOGLE_SEARCH_ENGINE_ID=tu_search_engine_id
SECRET_KEY=clave_secreta_larga
ACCESS_PIN=Osmo1980
MAX_SEARCHES_DEFAULT=100
```

### Frontend (.env)

```env
VITE_API_URL=/api
VITE_APP_NAME=Osmoleads
```

## Características principales

### Gestión de países
- Crear países con código de idioma para búsquedas localizadas
- Subir banderas personalizadas
- Buscar en todos los países a la vez

### Keywords
- Crear palabras clave por país
- Categorías: producto, competencia, general
- Activar/desactivar keywords
- Estadísticas de rendimiento

### Leads
- 5 pestañas: Nuevos, Leads, Dudas, Descartados, Marketplaces
- Estados personalizables con colores
- Extracción automática de contacto (email, teléfono, CIF)
- Sistema de notas con historial
- Filtros por keyword y estado
- Vista en tarjetas o listado
- Exportación a Excel

### Análisis
- Sugerencias automáticas de keywords
- Análisis de webs guardadas
- Ranking de keywords por rendimiento

### Búsqueda por imagen
- Subir foto de producto
- Encontrar webs donde aparece
- OCR para extraer texto de imágenes

## Límites de Google

| Concepto | Valor |
|----------|-------|
| Búsquedas gratuitas | 100/día |
| Coste adicional | $5/1000 búsquedas |
| Vision API | $1.50/1000 imágenes |

## Licencia

Proyecto privado - Todos los derechos reservados.

## Contacto

Para soporte técnico o consultas, contactar al desarrollador.
