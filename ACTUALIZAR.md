# 🚀 ACTUALIZAR DE V1.0 A V2.0

## ⚡ INSTRUCCIONES RÁPIDAS

### OPCIÓN 1: Mantener datos actuales (RECOMENDADO)

Si ya tienes empresas en V1.0 y quieres mantenerlas:

#### 1. Copia tus datos actuales

```powershell
cd C:\Users\Osmofilter\Documents\Osmofilter_leads
```

Copia estos archivos a un lugar seguro:
- `data/companies.json`
- `data/keywords.json`

#### 2. Elimina archivos (MENOS .git)

```powershell
Remove-Item * -Exclude .git -Recurse -Force
```

#### 3. Copia archivos de V2.0

Descomprime el ZIP de V2.0 y copia TODO el contenido a:
```
C:\Users\Osmofilter\Documents\Osmofilter_leads
```

#### 4. Restaura tus datos

Copia de vuelta:
- `companies.json` → `data/companies.json`
- `keywords.json` → `data/keywords.json`

#### 5. Sube a GitHub

```powershell
git add .
git commit -m "Actualización a V2.0"
git push origin main
```

---

### OPCIÓN 2: Empezar de cero (LIMPIO)

Si quieres empezar con todo nuevo:

#### 1. Elimina todo

```powershell
cd C:\Users\Osmofilter\Documents\Osmofilter_leads
Remove-Item * -Exclude .git -Recurse -Force
```

#### 2. Copia archivos V2.0

Descomprime el ZIP y copia TODO

#### 3. Sube a GitHub

```powershell
git add .
git commit -m "Actualización a V2.0 - Reset completo"
git push origin main
```

---

## ✅ VERIFICAR QUE FUNCIONÓ

1. Ve a: https://mario1988123.github.io/Osmofilter_leads/

2. Deberías ver:
   - **Diseño nuevo** con gradientes morados
   - **Pestañas nuevas** (Pendientes, Mis Clientes, etc.)
   - **Estadísticas** en el header con iconos
   - **Cards modernas** en lugar de tabla

3. Ejecuta una búsqueda de prueba:
   - Ve a: https://github.com/Mario1988123/Osmofilter_leads/actions
   - Run workflow
   - Espera 1-2 minutos
   - Refresca tu panel

---

## 🎯 PRINCIPALES CAMBIOS

### Lo que CAMBIA:
- ✅ Diseño completamente renovado
- ✅ Filtros mejorados (excluye Amazon, YouTube, etc.)
- ✅ Solo dominio principal (sin duplicados)
- ✅ Cambio de estado con 1 click
- ✅ Pestañas separadas por estado
- ✅ Email/Teléfono/CIF extraídos
- ✅ Sistema de notas
- ✅ Empresas descartadas no se repiten

### Lo que NO cambia:
- ✅ Tus credenciales (las mismas API keys)
- ✅ GitHub Pages (misma URL)
- ✅ Búsqueda automática (sigue siendo a las 9 AM)

---

## 🔧 SI HAY PROBLEMAS

### Problema: No se ve el diseño nuevo

**Solución:**
1. Presiona `Ctrl + Shift + R` en tu navegador
2. Espera 2-3 minutos (GitHub Pages tarda en actualizar)
3. Limpia caché del navegador

### Problema: Error en GitHub Actions

**Solución:**
1. Verifica que los Secrets sigan configurados:
   - https://github.com/Mario1988123/Osmofilter_leads/settings/secrets/actions
2. Debe haber `GOOGLE_API_KEY` y `SEARCH_ENGINE_ID`

### Problema: No aparecen mis empresas

**Solución:**
1. Verifica que copiaste `companies.json` correctamente
2. El archivo debe estar en `data/companies.json`
3. Formato JSON válido (abre con Notepad para verificar)

---

## 📞 COMANDOS DE AYUDA

**Ver qué archivos cambiaron:**
```powershell
git status
```

**Deshacer cambios (volver a V1.0):**
```powershell
git reset --hard HEAD~1
git push --force origin main
```

**Ver logs de commits:**
```powershell
git log --oneline
```

---

## 🎉 ¡LISTO!

Una vez actualizado:
- Panel más bonito ✅
- Más funcional ✅
- Más rápido ✅
- Menos duplicados ✅
- Info de contacto automática ✅

**¡Disfruta de la V2.0!** 🚀
