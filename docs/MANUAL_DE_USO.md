# MANUAL DE USO - OSMOLEADS v1.0

## Índice
1. [Acceso a la aplicación](#1-acceso-a-la-aplicación)
2. [Pantalla principal - Países](#2-pantalla-principal---países)
3. [Gestión de palabras clave](#3-gestión-de-palabras-clave)
4. [Realizar búsquedas](#4-realizar-búsquedas)
5. [Pestañas y organización de leads](#5-pestañas-y-organización-de-leads)
6. [Gestión de leads](#6-gestión-de-leads)
7. [Estados de leads](#7-estados-de-leads)
8. [Sistema de notas](#8-sistema-de-notas)
9. [Búsqueda por imagen](#9-búsqueda-por-imagen)
10. [Panel de keywords sugeridas](#10-panel-de-keywords-sugeridas)
11. [Exportar a Excel](#11-exportar-a-excel)
12. [Configuración](#12-configuración)
13. [Marketplaces](#13-marketplaces)
14. [Vistas: Tarjetas vs Listado](#14-vistas-tarjetas-vs-listado)
15. [Instalar como app (PWA)](#15-instalar-como-app-pwa)

---

## 1. Acceso a la aplicación

### 1.1 Abrir la aplicación

1. Abre tu navegador (Chrome, Firefox, Safari, Edge)
2. Ve a: `https://osmoleads.com` (o tu dominio)
3. Aparecerá una pantalla de bloqueo

### 1.2 Introducir PIN

1. En la pantalla de bloqueo verás un campo para el PIN
2. Escribe: `Osmo1980`
3. Pulsa "Entrar" o presiona Enter
4. Si el PIN es correcto, accederás al panel principal

### 1.3 Cerrar sesión

- La sesión se mantiene activa durante 24 horas
- Para cerrar sesión manualmente, pulsa el icono de candado en la esquina superior derecha
- Al cerrar el navegador completamente, la sesión se cierra

---

## 2. Pantalla principal - Países

### 2.1 Vista general

Al entrar verás la pantalla de **Países**. Aquí es donde organizas tus búsquedas por mercado.

### 2.2 Crear un nuevo país

1. Pulsa el botón **"+ Añadir País"**
2. Rellena los campos:
   - **Nombre del país**: España, Francia, Portugal...
   - **Código de país**: ES, FR, PT... (para la búsqueda de Google)
   - **Idioma**: es, fr, pt... (para filtrar resultados)
   - **Imagen/Bandera**: Sube una imagen (PNG, 64x64 px recomendado)
3. Pulsa **"Guardar"**

### 2.3 Editar un país

1. En la tarjeta del país, pulsa el icono de **lápiz** (editar)
2. Modifica los campos que necesites
3. Pulsa **"Guardar"**

### 2.4 Eliminar un país

1. En la tarjeta del país, pulsa el icono de **papelera** (eliminar)
2. Confirma la eliminación
3. **Cuidado**: Esto NO elimina los leads encontrados, solo el país

### 2.5 Buscar en todos los países

- En la pantalla de países hay un botón **"Buscar en todos"**
- Esto ejecuta las búsquedas de TODOS los países configurados
- Útil para búsquedas masivas programadas

---

## 3. Gestión de palabras clave

### 3.1 Acceder a las keywords de un país

1. Pulsa sobre la tarjeta de un país (ej: España)
2. Se abrirá el panel del país
3. Verás la pestaña **"Keywords"**

### 3.2 Añadir una palabra clave

1. Pulsa **"+ Nueva Keyword"**
2. Escribe la palabra o frase:
   - Ejemplos: `osmosis inversa`, `fuentes de agua`, `dispensador agua oficina`
3. Selecciona una categoría (opcional):
   - **Producto**: lo que vendes (fuentes de agua, filtros...)
   - **Competencia**: nombres de competidores
   - **General**: términos genéricos del sector
4. Define el número de resultados por búsqueda (1-10)
5. Pulsa **"Guardar"**

### 3.3 Editar una keyword

1. En la lista de keywords, pulsa el icono de **lápiz**
2. Modifica lo que necesites
3. Pulsa **"Guardar"**

### 3.4 Eliminar una keyword

1. Pulsa el icono de **papelera** junto a la keyword
2. Confirma la eliminación
3. Las búsquedas anteriores de esa keyword NO se eliminan

### 3.5 Activar/Desactivar keywords

- Cada keyword tiene un **switch** para activarla o desactivarla
- Las keywords desactivadas NO se buscan pero se mantienen guardadas
- Útil para pausar temporalmente una búsqueda

---

## 4. Realizar búsquedas

### 4.1 Configurar límite de búsquedas

Antes de buscar, configura el límite:

1. En la parte superior verás: **"Máx. búsquedas: [100]"**
2. Pulsa para editar
3. Pon el número que quieras:
   - `100`: Límite gratuito de Google
   - `0`: Sin límite (pagarás el exceso)
   - Cualquier número: el límite que quieras

### 4.2 Buscar manualmente

1. Dentro de un país, pulsa el botón **"Buscar ahora"**
2. Aparecerá una barra de progreso
3. Verás en tiempo real:
   - Keyword que se está buscando
   - Resultados encontrados
   - Búsquedas consumidas
4. Al terminar, los resultados aparecen en **"Leads Nuevos"**

### 4.3 Búsqueda automática

- Las búsquedas se ejecutan automáticamente a las **9:00 AM** (hora España)
- Esto ocurre todos los días
- Los resultados aparecen en "Leads Nuevos"

### 4.4 Contador de búsquedas

- En la esquina superior derecha verás: **"Búsquedas hoy: X/100"**
- Este contador se resetea cada día a medianoche
- Si llegas al límite, no podrás buscar más (o se cobrará)

---

## 5. Pestañas y organización de leads

### 5.1 Estructura de pestañas

Dentro de cada país hay 5 pestañas:

| Pestaña | Contenido | Color |
|---------|-----------|-------|
| **Leads Nuevos** | Empresas recién encontradas o no revisadas | Azul |
| **Leads** | Empresas revisadas con estado asignado | Verde |
| **Dudas** | Empresas que no sabes cómo clasificar | Amarillo |
| **Descartados** | Empresas que no te interesan | Rojo |
| **Marketplaces** | Amazon, Leroy Merlin, etc. (automático) | Gris |

### 5.2 Flujo de trabajo típico

```
Leads Nuevos → Revisar → Mover a:
                         ├── Leads (con estado)
                         ├── Dudas
                         ├── Descartados
                         └── Marketplaces
```

### 5.3 Filtrar por keyword

En cualquier pestaña puedes filtrar:

1. Pulsa el desplegable **"Filtrar por keyword"**
2. Selecciona una keyword específica
3. Solo verás leads encontrados con esa keyword
4. Para ver todos, selecciona **"Todas las keywords"**

---

## 6. Gestión de leads

### 6.1 Información de cada lead

Cada lead muestra:

- **Nombre/Título**: Extraído de Google
- **URL**: Enlace a la web
- **Dominio**: Dominio principal (sin subdominios)
- **Email**: Extraído automáticamente (si existe)
- **Teléfono**: Extraído automáticamente (si existe)
- **CIF/NIF**: Extraído automáticamente (si existe)
- **Encontrado por**: Keyword que lo encontró
- **Fecha**: Cuándo se encontró
- **Snippet**: Descripción de Google

### 6.2 Mover un lead a otra pestaña

1. En el lead, pulsa el desplegable **"Mover a..."**
2. Selecciona la pestaña destino:
   - Leads
   - Dudas
   - Descartados
   - Marketplaces
3. El lead se moverá automáticamente

### 6.3 Abrir la web del lead

- Pulsa sobre el **nombre/título** del lead
- Se abrirá la web en una nueva pestaña
- También puedes pulsar el icono de **enlace externo**

### 6.4 Copiar datos rápidamente

- Pulsa sobre el **email** para copiarlo
- Pulsa sobre el **teléfono** para copiarlo
- Aparecerá un mensaje "Copiado al portapapeles"

### 6.5 Obtener datos manualmente

Si un lead no tiene email/teléfono:

1. Pulsa el botón **"Obtener datos"**
2. El sistema hará scraping de la web
3. Buscará en: contacto, aviso legal, empresa, about...
4. Si encuentra datos, los añadirá al lead

---

## 7. Estados de leads

### 7.1 Estados disponibles

Los leads en la pestaña "Leads" pueden tener estos estados:

| Estado | Icono | Color | Descripción |
|--------|-------|-------|-------------|
| **Pendiente** | ⏳ | Gris | Sin revisar aún |
| **Competencia** | 🏢 | Naranja | Es un competidor |
| **Cliente** | ✅ | Verde | Ya es cliente |
| **En gestión** | 📞 | Azul | En proceso de contacto |
| **Captado** | 🎯 | Morado | Potencial alto |

### 7.2 Cambiar estado de un lead

1. En el lead, pulsa el desplegable de **estado**
2. Selecciona el nuevo estado
3. El lead cambiará de color automáticamente

### 7.3 Filtrar por estado

1. En la pestaña "Leads", pulsa **"Filtrar por estado"**
2. Selecciona el estado que quieres ver
3. Solo verás leads con ese estado

### 7.4 Crear estados personalizados

1. Ve a **Configuración** (icono de engranaje)
2. Sección **"Estados de leads"**
3. Pulsa **"+ Nuevo estado"**
4. Define:
   - Nombre del estado
   - Color
   - Icono (opcional)
5. Pulsa **"Guardar"**

---

## 8. Sistema de notas

### 8.1 Añadir una nota a un lead

1. En el lead, pulsa el icono de **nota** (📝)
2. Se abrirá un panel lateral
3. Pulsa **"+ Nueva nota"**
4. Escribe tu nota
5. La fecha se añade automáticamente
6. Pulsa **"Guardar"**

### 8.2 Estructura de notas

Cada nota tiene:
- **Fecha y hora**: Automática
- **Contenido**: Lo que escribiste
- **Historial**: Las notas se acumulan, nunca se borran

### 8.3 Ejemplo de uso de notas

```
📅 15/01/2026 - 10:30
Llamada realizada. Hablar con María, responsable de compras.
Interesados en fuentes de agua para oficina.
Llamar la semana que viene.

📅 22/01/2026 - 11:15
Segunda llamada. Piden presupuesto para 3 fuentes.
Enviar por email.

📅 23/01/2026 - 09:00
Presupuesto enviado. Seguimiento en 3 días.
```

### 8.4 Indicador de notas

- Los leads con notas muestran un **indicador** (punto o número)
- Puedes filtrar para ver solo leads con notas

---

## 9. Búsqueda por imagen

### 9.1 Para qué sirve

- Subir una foto de un producto
- Encontrar empresas que vendan ese producto
- Útil para identificar proveedores o competidores

### 9.2 Cómo buscar por imagen

1. En el menú principal, pulsa **"Buscar por imagen"**
2. Pulsa **"Subir imagen"** o arrastra una foto
3. Formatos permitidos: JPG, PNG, WEBP
4. Tamaño máximo: 5 MB
5. Pulsa **"Buscar"**
6. Los resultados aparecerán en una lista

### 9.3 Resultados de búsqueda por imagen

- **Webs donde aparece**: Lista de sitios donde está esa imagen
- **Productos similares**: Productos parecidos encontrados
- **Texto detectado**: Si la imagen tiene texto, lo extrae

### 9.4 Limitaciones

- Coste: ~$1.50 por cada 1000 búsquedas de imagen
- No funciona bien con logos muy simples
- Mejor con fotos de productos reales

---

## 10. Panel de keywords sugeridas

### 10.1 Acceder al panel

1. Dentro de un país, ve a la pestaña **"Análisis"**
2. Verás el panel de keywords sugeridas

### 10.2 Información que muestra

| Columna | Descripción |
|---------|-------------|
| **Keyword** | Palabra encontrada en las webs |
| **Frecuencia** | Cuántas veces aparece |
| **Webs** | En cuántas webs diferentes |
| **Fuente** | De dónde se extrajo (meta, título, contenido) |
| **Acción** | Añadir o ignorar |

### 10.3 Cómo funciona

- El sistema analiza las webs de los leads guardados
- Extrae: meta keywords, meta description, títulos H1-H2
- Cuenta las palabras más frecuentes
- Te sugiere nuevas keywords para añadir

### 10.4 Añadir keyword sugerida

1. En la lista de sugerencias, pulsa **"+ Añadir"**
2. La keyword se añadirá a tu lista de búsqueda
3. Se empezará a buscar en la próxima ejecución

### 10.5 Ignorar sugerencia

- Pulsa **"Ignorar"** si no te interesa esa keyword
- No volverá a aparecer como sugerencia

### 10.6 Sugerencias de eliminación

- Si una keyword tuya no está dando resultados, el sistema te avisará
- Verás un mensaje: "Esta keyword no ha dado resultados en X días"
- Puedes desactivarla o eliminarla

---

## 11. Exportar a Excel

### 11.1 Exportar leads de una pestaña

1. Ve a la pestaña que quieras exportar (Leads, Dudas, etc.)
2. Pulsa el botón **"Exportar"** (icono de Excel)
3. Se descargará un archivo `.xlsx`

### 11.2 Columnas del Excel

El archivo exportado incluye:

| Columna | Contenido |
|---------|-----------|
| A | Nombre |
| B | URL |
| C | Dominio |
| D | Email |
| E | Teléfono |
| F | CIF/NIF |
| G | Estado |
| H | Keyword |
| I | Fecha encontrado |
| J | Notas |
| K | Snippet |

### 11.3 Exportar con filtros

- Si tienes filtros aplicados, solo se exportará lo filtrado
- Ejemplo: Si filtras por "osmosis inversa", solo se exportan esos leads

### 11.4 Exportar todos los leads de un país

1. En la vista del país, pulsa **"Exportar todo"**
2. Se descargará un Excel con TODAS las pestañas
3. Cada pestaña será una hoja del Excel

---

## 12. Configuración

### 12.1 Acceder a configuración

- Pulsa el icono de **engranaje** en la esquina superior derecha

### 12.2 Opciones disponibles

#### Límite de búsquedas
- Cambia el límite diario predefinido
- `0` = Sin límite

#### Estados personalizados
- Añadir nuevos estados
- Editar estados existentes
- Cambiar colores e iconos

#### Marketplaces
- Ver lista de marketplaces detectados automáticamente
- Añadir nuevos marketplaces a la lista negra
- Ejemplo: Si quieres que "PcComponentes" vaya a marketplaces, añádelo aquí

#### Exclusiones
- Dominios que siempre se descartan
- Ejemplo: añadir "wikipedia.org" para nunca verlo

#### Tema visual
- Modo claro / oscuro (si está implementado)

#### Cambiar PIN
- Cambiar el PIN de acceso
- Por seguridad, necesitas el PIN actual

---

## 13. Marketplaces

### 13.1 Detección automática

El sistema detecta automáticamente estos marketplaces:

```
Amazon, eBay, AliExpress, Alibaba, Mercado Libre,
Leroy Merlin, Bauhaus, Bricomart, Media Markt,
PcComponentes, El Corte Inglés, Carrefour,
Wallapop, Milanuncios, Fnac, Worten
```

### 13.2 Mover de Marketplace a otra pestaña

Si el sistema se equivocó:

1. Ve a la pestaña **"Marketplaces"**
2. Encuentra el lead
3. Pulsa **"Mover a..."**
4. Selecciona "Leads Nuevos" o "Leads"

### 13.3 Añadir marketplace a la lista

1. Ve a **Configuración > Marketplaces**
2. Pulsa **"+ Añadir"**
3. Escribe el dominio (ej: `tienda.com`)
4. Pulsa **"Guardar"**
5. A partir de ahora, ese dominio irá a Marketplaces

---

## 14. Vistas: Tarjetas vs Listado

### 14.1 Cambiar vista

En cualquier pestaña de leads:

1. Busca los iconos de **vista** (arriba a la derecha)
2. Pulsa el icono de **tarjetas** (cuadrícula)
3. O pulsa el icono de **listado** (líneas)

### 14.2 Vista de tarjetas

- Cada lead es una tarjeta visual
- Muestra toda la información de un vistazo
- Mejor para revisar pocos leads
- Más visual y espaciosa

### 14.3 Vista de listado

- Los leads se muestran en una tabla
- Una fila por lead
- Mejor para revisar muchos leads rápidamente
- Más compacto
- Permite ordenar por columnas

### 14.4 Ordenar en vista listado

Pulsa en el encabezado de la columna para ordenar:
- **Nombre**: Alfabético
- **Fecha**: Más reciente / más antiguo
- **Estado**: Por estado
- **Keyword**: Por palabra clave

---

## 15. Instalar como app (PWA)

### 15.1 En Chrome (ordenador)

1. Abre `https://osmoleads.com`
2. Pulsa el icono de **tres puntos** (menú)
3. Selecciona **"Instalar Osmoleads..."**
4. Confirma la instalación
5. Se creará un acceso directo en tu escritorio

### 15.2 En Chrome (Android)

1. Abre `https://osmoleads.com` en Chrome
2. Pulsa el icono de **tres puntos**
3. Selecciona **"Añadir a pantalla de inicio"**
4. Confirma
5. Aparecerá como una app en tu móvil

### 15.3 En Safari (iPhone/iPad)

1. Abre `https://osmoleads.com` en Safari
2. Pulsa el icono de **compartir** (cuadrado con flecha)
3. Selecciona **"Añadir a pantalla de inicio"**
4. Confirma
5. Aparecerá como una app

### 15.4 Ventajas de la PWA

- Funciona sin barra de navegador
- Acceso más rápido
- Notificaciones (si se implementan)
- Funciona parcialmente offline

---

## Atajos de teclado

| Atajo | Acción |
|-------|--------|
| `Ctrl + K` | Búsqueda rápida |
| `Ctrl + N` | Nueva nota |
| `Ctrl + E` | Exportar |
| `Esc` | Cerrar modal |
| `Enter` | Confirmar acción |

---

## Preguntas frecuentes

### ¿Puedo recuperar un lead descartado?

Sí. Ve a la pestaña "Descartados", encuentra el lead y muévelo a "Leads Nuevos".

### ¿Cuántos leads puedo guardar?

Ilimitados. La base de datos no tiene límite de almacenamiento.

### ¿Se borran los leads antiguos?

No. Los leads nunca se borran automáticamente. Solo tú puedes eliminarlos.

### ¿Puedo buscar en varios países a la vez?

Sí. Usa el botón "Buscar en todos" en la pantalla principal de países.

### ¿Qué pasa si Google no encuentra datos de contacto?

El sistema buscará en varias páginas de la web (contacto, aviso legal, etc.). Si no encuentra nada, los campos quedarán vacíos y podrás buscar manualmente.

### ¿Funciona en el móvil?

Sí. La aplicación es responsive y funciona en móviles y tablets. Además puedes instalarla como PWA.

---

## Soporte

Si tienes problemas o dudas:

1. Revisa esta documentación
2. Contacta con el desarrollador
3. Revisa los logs del servidor (si tienes acceso)

---

**Versión del documento**: 1.0
**Última actualización**: Enero 2026
