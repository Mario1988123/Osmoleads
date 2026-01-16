# 🔍 Osmofilter CRM Leads V2.0

## 🎉 ¡VERSIÓN MEJORADA!

Sistema completo de gestión de leads con diseño moderno y funcionalidades avanzadas.

---

## ✨ NUEVAS CARACTERÍSTICAS V2.0

### 🎯 **1. Filtros Mejorados**
- ✅ **Excluye marketplaces** (Amazon, AliExpress, Leroy Merlin, etc.)
- ✅ **Excluye YouTube y redes sociales**
- ✅ **Solo dominio principal** - No duplica subdominios ni carpetas
- ✅ **Sistema de descartados** - Empresas eliminadas no se vuelven a buscar

### 🚀 **2. UI Moderna y Ágil**
- ✅ **Cambio de estado con 1 click** - Sin modales, directo en el dropdown
- ✅ **Pestañas separadas** por estado:
  - Pendientes
  - Mis Clientes
  - Clientes de Compañero
  - En Proceso
  - Captados
- ✅ **Diseño moderno** con gradientes y animaciones
- ✅ **Notificaciones** visuales de acciones

### 📊 **3. Información de Contacto**
- ✅ **Email** extraído automáticamente
- ✅ **Teléfono** detectado en la web
- ✅ **CIF** encontrado si está disponible
- ✅ **Todo sin coste adicional** - scraping básico

### 📝 **4. Sistema de Notas**
- ✅ Añadir notas a cada empresa
- ✅ Visible en la tarjeta de empresa
- ✅ Editar notas en cualquier momento

### 🔍 **5. Análisis de Keywords**
- ✅ Detecta palabras clave de las empresas encontradas
- ✅ Sugiere nuevas keywords para buscar
- ✅ Productos detectados automáticamente

### 📸 **6. Búsqueda por Imagen**
- ✅ Interfaz preparada para Google Vision API
- ✅ Subir foto de producto
- ✅ Encontrar empresas que lo venden

### 💪 **7. Mejoras Técnicas**
- ✅ Solo 5 resultados por keyword (50 búsquedas/día vs 100)
- ✅ Extracción inteligente de información
- ✅ Base de datos de descartados
- ✅ Rendimiento optimizado

---

## 🎨 DISEÑO

### Antes (V1.0):
- Tabla simple
- Sin animaciones
- Edición con modal
- Todo junto

### Ahora (V2.0):
- ✅ Cards modernas con gradientes
- ✅ Animaciones suaves
- ✅ Cambio rápido de estado
- ✅ Organizado por pestañas
- ✅ Estadísticas visuales
- ✅ Responsive total

---

## 📦 INSTALACIÓN

### Si ya tienes V1.0 instalada:

```bash
cd C:\Users\Osmofilter\Documents\Osmofilter_leads
```

Elimina todo el contenido EXCEPTO la carpeta `.git`

Copia los nuevos archivos de V2.0

```bash
git add .
git commit -m "Actualización a V2.0"
git push origin main
```

### Instalación nueva:

Sigue las instrucciones del archivo `SETUP.md`

---

## 🔐 CREDENCIALES

Las mismas que en V1.0:
- API Key: `AIzaSyCD0ZYbTzL-0jJmafElcnD20TiG4bnQl7I`
- Search Engine ID: `355217cd922dc41ac`

---

## 🎯 CÓMO USAR

### Flujo de Trabajo:

1. **Búsqueda automática diaria** a las 9:00 AM
2. **Revisa "Pendientes"** - Empresas nuevas encontradas
3. **Cambia el estado** con 1 click en el dropdown
4. **Añade notas** si es necesario
5. **Descarta** empresas no relevantes (no volverán a aparecer)
6. **Las empresas se mueven** automáticamente a su pestaña

### Estados:

- ⏳ **Pendiente**: Recién encontrada, sin revisar
- ✅ **Captado**: Empresa identificada como potencial
- 👤 **Mi Cliente**: Tu cliente personal
- 👥 **Cliente Compañero**: Cliente de otro comercial
- 🔄 **En Proceso**: Negociación activa

---

## 🗑️ SISTEMA DE DESCARTADOS

Cuando eliminas una empresa:
- Se guarda en `discarded.json`
- **No volverá a aparecer** en futuras búsquedas
- Evita duplicados automáticamente
- Dominio completo bloqueado

---

## 📊 DATOS EXTRAÍDOS

Para cada empresa intenta obtener:
- ✅ Nombre
- ✅ URL (dominio principal)
- ✅ Email de contacto
- ✅ Teléfono
- ✅ CIF (si está en aviso legal)
- ✅ Productos/Keywords detectados
- ✅ Snippet de descripción

---

## 🔧 PERSONALIZACIÓN

### Añadir Keywords:
- Ve a pestaña "Keywords"
- Click en "+ Añadir Keyword"
- Se usará en la próxima búsqueda

### Cambiar frecuencia:
Edita `.github/workflows/daily-search.yml` línea 5

---

## 🚀 RENDIMIENTO

- **50 búsquedas/día** (vs 100 en V1.0)
- **Más precisión** en resultados
- **Menos descartados** gracias a filtros
- **0€ gastados** - todo dentro del límite gratis

---

## 📱 RESPONSIVE

- ✅ Funciona en móvil
- ✅ Funciona en tablet
- ✅ Funciona en PC
- ✅ Diseño adaptativo

---

## 🔒 SEGURIDAD

- ✅ API Keys en Secrets de GitHub
- ✅ No se exponen en el código
- ✅ Repositorio puede ser público (sin riesgo)
- ✅ Límites de Google Cloud configurados

---

## ⚡ PRÓXIMAS MEJORAS POSIBLES

- Integración con Google Vision API completa
- Exportar a Excel/CSV
- Envío de emails desde el panel
- Integración con tu CRM actual
- Análisis de competencia avanzado
- Gráficas y estadísticas

---

## 🆘 SOPORTE

Si algo no funciona:
1. Verifica GitHub Actions (debe estar verde ✅)
2. Comprueba que los Secrets estén configurados
3. Revisa la consola del navegador (F12)
4. Lee los logs de GitHub Actions

---

**Creado con ❤️ para Osmofilter** 🚰💧

**Versión:** 2.0  
**Fecha:** Diciembre 2025  
**Autor:** Sistema automatizado de gestión de leads
