# GUÍA DE INSTALACIÓN - OSMOLEADS v1.0

## Índice
1. [Requisitos previos](#1-requisitos-previos)
2. [Contratar servidor IONOS](#2-contratar-servidor-ionos)
3. [Configurar servidor](#3-configurar-servidor)
4. [Instalar dependencias](#4-instalar-dependencias)
5. [Configurar base de datos PostgreSQL](#5-configurar-base-de-datos-postgresql)
6. [Configurar Google APIs](#6-configurar-google-apis)
7. [Desplegar Backend (Python/FastAPI)](#7-desplegar-backend)
8. [Desplegar Frontend (React PWA)](#8-desplegar-frontend)
9. [Configurar dominio y SSL](#9-configurar-dominio-y-ssl)
10. [Configurar búsquedas automáticas](#10-configurar-búsquedas-automáticas)
11. [Verificar instalación](#11-verificar-instalación)
12. [Solución de problemas](#12-solución-de-problemas)

---

## 1. Requisitos previos

### 1.1 En tu ordenador necesitas instalar:

| Programa | Para qué sirve | Descarga |
|----------|---------------|----------|
| **Visual Studio Code** | Editar código | https://code.visualstudio.com/ |
| **Git** | Control de versiones | https://git-scm.com/downloads |
| **Node.js 20 LTS** | Ejecutar React | https://nodejs.org/ |
| **Python 3.11+** | Ejecutar backend | https://www.python.org/downloads/ |
| **PuTTY** (Windows) | Conectar al servidor | https://www.putty.org/ |
| **FileZilla** | Subir archivos | https://filezilla-project.org/ |

### 1.2 Verificar instalaciones (abre terminal/cmd):

```bash
# Verificar Git
git --version
# Debe mostrar: git version 2.x.x

# Verificar Node.js
node --version
# Debe mostrar: v20.x.x

# Verificar npm
npm --version
# Debe mostrar: 10.x.x

# Verificar Python
python --version
# Debe mostrar: Python 3.11.x o superior
```

### 1.3 Cuentas necesarias:

| Cuenta | URL | Para qué |
|--------|-----|----------|
| **GitHub** | https://github.com | Guardar código |
| **Google Cloud** | https://console.cloud.google.com | APIs de búsqueda |
| **IONOS** | https://www.ionos.es | Servidor |

---

## 2. Contratar servidor IONOS

### 2.1 Ir a IONOS y contratar VPS

1. Ve a: https://www.ionos.es/servidores/vps
2. Selecciona **VPS Linux S** (6€/mes)
   - 2 GB RAM
   - 1 vCPU
   - 80 GB SSD
   - Tráfico ilimitado

3. En sistema operativo elige: **Ubuntu 22.04 LTS**

4. Completa el pago

### 2.2 Anotar datos del servidor

Una vez contratado, IONOS te enviará un email con:

```
IP del servidor: xxx.xxx.xxx.xxx (ejemplo: 85.215.123.45)
Usuario: root
Contraseña: xxxxxxxxxx
```

**GUARDA ESTOS DATOS EN UN LUGAR SEGURO**

### 2.3 Comprar dominio

1. En IONOS ve a: Dominios > Registrar dominio
2. Busca: `osmoleads.com`
3. Si está disponible, cómpralo (~12€/año)
4. Si no está disponible, prueba:
   - osmoleads.es
   - osmo-leads.com
   - app-osmoleads.com

---

## 3. Configurar servidor

### 3.1 Conectar al servidor por SSH

**En Windows (con PuTTY):**
1. Abre PuTTY
2. En "Host Name" escribe la IP de tu servidor
3. Puerto: 22
4. Click en "Open"
5. Usuario: `root`
6. Contraseña: la que te dio IONOS

**En Mac/Linux (Terminal):**
```bash
ssh root@TU_IP_DEL_SERVIDOR
# Te pedirá la contraseña
```

### 3.2 Actualizar el sistema

Una vez conectado, ejecuta estos comandos **uno por uno**:

```bash
# Actualizar lista de paquetes
apt update

# Actualizar paquetes instalados
apt upgrade -y

# Instalar paquetes básicos
apt install -y curl wget git nano unzip software-properties-common
```

### 3.3 Crear usuario para la aplicación (no usar root)

```bash
# Crear usuario osmoleads
adduser osmoleads

# Te pedirá contraseña, pon una segura y anótala
# El resto de preguntas pulsa Enter para dejar vacío

# Dar permisos de sudo
usermod -aG sudo osmoleads

# Cambiar a ese usuario
su - osmoleads
```

A partir de ahora trabajamos como usuario `osmoleads`.

### 3.4 Configurar firewall

```bash
# Activar firewall
sudo ufw allow OpenSSH
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 8000
sudo ufw enable

# Verificar
sudo ufw status
```

---

## 4. Instalar dependencias

### 4.1 Instalar Python 3.11

```bash
# Añadir repositorio
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# Instalar Python 3.11
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Verificar
python3.11 --version
# Debe mostrar: Python 3.11.x
```

### 4.2 Instalar Node.js 20

```bash
# Añadir repositorio de Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -

# Instalar Node.js
sudo apt install -y nodejs

# Verificar
node --version
# Debe mostrar: v20.x.x

npm --version
# Debe mostrar: 10.x.x
```

### 4.3 Instalar Nginx (servidor web)

```bash
# Instalar Nginx
sudo apt install -y nginx

# Iniciar Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Verificar que funciona
sudo systemctl status nginx
# Debe decir: active (running)
```

### 4.4 Instalar Tesseract (OCR para imágenes)

```bash
# Instalar Tesseract con idiomas español, inglés y francés
sudo apt install -y tesseract-ocr tesseract-ocr-spa tesseract-ocr-fra

# Verificar
tesseract --version
# Debe mostrar: tesseract 5.x.x
```

---

## 5. Configurar base de datos PostgreSQL

### 5.1 Instalar PostgreSQL

```bash
# Instalar PostgreSQL 15
sudo apt install -y postgresql postgresql-contrib

# Verificar que está corriendo
sudo systemctl status postgresql
# Debe decir: active (running)
```

### 5.2 Crear base de datos y usuario

```bash
# Entrar a PostgreSQL como superusuario
sudo -u postgres psql

# Dentro de PostgreSQL, ejecutar estos comandos:
```

```sql
-- Crear usuario para la aplicación
CREATE USER osmoleads_user WITH PASSWORD 'OsmoLeads2024_Segura!';

-- Crear base de datos
CREATE DATABASE osmoleads_db OWNER osmoleads_user;

-- Dar todos los permisos
GRANT ALL PRIVILEGES ON DATABASE osmoleads_db TO osmoleads_user;

-- Salir
\q
```

### 5.3 Verificar conexión

```bash
# Probar conexión
psql -h localhost -U osmoleads_user -d osmoleads_db

# Te pedirá la contraseña: OsmoLeads2024_Segura!
# Si entra bien, escribe \q para salir
```

### 5.4 Guardar credenciales

Anota estos datos que usaremos después:

```
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=osmoleads_db
DATABASE_USER=osmoleads_user
DATABASE_PASSWORD=OsmoLeads2024_Segura!
```

---

## 6. Configurar Google APIs

### 6.1 Crear proyecto en Google Cloud

1. Ve a: https://console.cloud.google.com/
2. Arriba a la izquierda, click en el selector de proyecto
3. Click en "NUEVO PROYECTO"
4. Nombre: `Osmoleads`
5. Click en "CREAR"
6. Espera a que se cree y selecciónalo

### 6.2 Activar Custom Search API

1. En el menú lateral: APIs y servicios > Biblioteca
2. Busca: "Custom Search API"
3. Click en el resultado
4. Click en "HABILITAR"

### 6.3 Activar Cloud Vision API (para búsqueda por imagen)

1. En el menú lateral: APIs y servicios > Biblioteca
2. Busca: "Cloud Vision API"
3. Click en el resultado
4. Click en "HABILITAR"

### 6.4 Crear API Key

1. En el menú lateral: APIs y servicios > Credenciales
2. Click en "+ CREAR CREDENCIALES"
3. Selecciona "Clave de API"
4. Se genera una clave, **CÓPIALA Y GUÁRDALA**
5. Click en "RESTRINGIR CLAVE" (recomendado)
6. En "Restricciones de API" selecciona:
   - Custom Search API
   - Cloud Vision API
7. Click en "GUARDAR"

Tu API Key será algo como: `AIzaSyC...abc123`

### 6.5 Crear motor de búsqueda personalizado

1. Ve a: https://programmablesearchengine.google.com/
2. Click en "Añadir"
3. Configuración:
   - Nombre: `Osmoleads Search`
   - En "Sitios que buscar": marca "Buscar en toda la web"
4. Click en "Crear"
5. Te dará un **ID de motor de búsqueda** (cx), **CÓPIALO**

El ID será algo como: `355217cd922dc41ac`

### 6.6 Guardar credenciales de Google

```
GOOGLE_API_KEY=AIzaSyC...tu_clave_aqui
GOOGLE_SEARCH_ENGINE_ID=tu_id_aqui
```

---

## 7. Desplegar Backend

### 7.1 Clonar repositorio

```bash
# Ir al directorio home
cd /home/osmoleads

# Clonar el repositorio (cuando esté en GitHub)
git clone https://github.com/Mario1988123/Osmoleads.git

# Entrar al directorio
cd Osmoleads
```

### 7.2 Crear entorno virtual de Python

```bash
# Crear entorno virtual
python3.11 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Verificar que está activado (debe aparecer (venv) al inicio)
```

### 7.3 Instalar dependencias de Python

```bash
# Instalar dependencias
pip install -r backend/requirements.txt
```

### 7.4 Crear archivo de configuración

```bash
# Crear archivo .env
nano backend/.env
```

Pega este contenido (cambia los valores por los tuyos):

```env
# Base de datos
DATABASE_URL=postgresql://osmoleads_user:OsmoLeads2024_Segura!@localhost:5432/osmoleads_db

# Google APIs
GOOGLE_API_KEY=tu_api_key_de_google
GOOGLE_SEARCH_ENGINE_ID=tu_search_engine_id

# Seguridad
SECRET_KEY=genera_una_clave_secreta_larga_y_aleatoria_aqui_12345
ACCESS_PIN=Osmo1980

# Configuración
MAX_SEARCHES_DEFAULT=100
DEBUG=False
```

Para guardar: `Ctrl+O`, Enter, `Ctrl+X`

### 7.5 Inicializar base de datos

```bash
# Ejecutar migraciones
cd backend
python -m app.database.init_db
```

### 7.6 Probar que el backend funciona

```bash
# Ejecutar en modo desarrollo
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Debe mostrar: Uvicorn running on http://0.0.0.0:8000
# Pulsa Ctrl+C para parar
```

### 7.7 Configurar servicio systemd (para que se ejecute siempre)

```bash
# Crear archivo de servicio
sudo nano /etc/systemd/system/osmoleads-backend.service
```

Pega este contenido:

```ini
[Unit]
Description=Osmoleads Backend API
After=network.target postgresql.service

[Service]
User=osmoleads
Group=osmoleads
WorkingDirectory=/home/osmoleads/Osmoleads/backend
Environment="PATH=/home/osmoleads/Osmoleads/venv/bin"
EnvironmentFile=/home/osmoleads/Osmoleads/backend/.env
ExecStart=/home/osmoleads/Osmoleads/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Guardar y salir (`Ctrl+O`, Enter, `Ctrl+X`)

```bash
# Activar servicio
sudo systemctl daemon-reload
sudo systemctl enable osmoleads-backend
sudo systemctl start osmoleads-backend

# Verificar que está corriendo
sudo systemctl status osmoleads-backend
# Debe decir: active (running)
```

---

## 8. Desplegar Frontend

### 8.1 Instalar dependencias del frontend

```bash
# Ir al directorio frontend
cd /home/osmoleads/Osmoleads/frontend

# Instalar dependencias
npm install
```

### 8.2 Configurar variables de entorno del frontend

```bash
# Crear archivo .env
nano .env
```

Pega:

```env
VITE_API_URL=https://osmoleads.com/api
VITE_APP_NAME=Osmoleads
```

Guardar y salir.

### 8.3 Compilar frontend para producción

```bash
# Compilar
npm run build

# Se creará una carpeta 'dist' con los archivos
```

### 8.4 Mover archivos al servidor web

```bash
# Crear directorio para la web
sudo mkdir -p /var/www/osmoleads

# Copiar archivos compilados
sudo cp -r dist/* /var/www/osmoleads/

# Dar permisos
sudo chown -R www-data:www-data /var/www/osmoleads
```

---

## 9. Configurar dominio y SSL

### 9.1 Configurar DNS en IONOS

1. Ve a tu panel de IONOS
2. Ve a: Dominios > osmoleads.com > DNS
3. Añade/modifica estos registros:

| Tipo | Nombre | Valor | TTL |
|------|--------|-------|-----|
| A | @ | TU_IP_DEL_SERVIDOR | 3600 |
| A | www | TU_IP_DEL_SERVIDOR | 3600 |

4. Espera 5-30 minutos a que se propaguen los DNS

### 9.2 Configurar Nginx

```bash
# Crear configuración de Nginx
sudo nano /etc/nginx/sites-available/osmoleads
```

Pega este contenido (cambia `osmoleads.com` si usas otro dominio):

```nginx
server {
    listen 80;
    server_name osmoleads.com www.osmoleads.com;

    # Frontend (React)
    location / {
        root /var/www/osmoleads;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # Backend API (FastAPI)
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
    }
}
```

Guardar y salir.

```bash
# Activar el sitio
sudo ln -s /etc/nginx/sites-available/osmoleads /etc/nginx/sites-enabled/

# Eliminar configuración por defecto
sudo rm /etc/nginx/sites-enabled/default

# Verificar configuración
sudo nginx -t
# Debe decir: syntax is ok / test is successful

# Reiniciar Nginx
sudo systemctl restart nginx
```

### 9.3 Instalar certificado SSL (HTTPS gratuito)

```bash
# Instalar Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtener certificado SSL
sudo certbot --nginx -d osmoleads.com -d www.osmoleads.com

# Te pedirá:
# 1. Email: pon tu email
# 2. Aceptar términos: Y
# 3. Compartir email: N (opcional)
# 4. Redirect HTTP to HTTPS: 2 (Yes)
```

El certificado se renovará automáticamente.

### 9.4 Verificar que funciona

Abre en tu navegador: `https://osmoleads.com`

Deberías ver la pantalla de login con el PIN.

---

## 10. Configurar búsquedas automáticas

### 10.1 Crear tarea programada (cron)

```bash
# Editar crontab
crontab -e

# Si te pregunta qué editor, elige 1 (nano)
```

Añade esta línea al final:

```cron
# Búsqueda automática a las 9:00 AM (hora España)
0 8 * * * cd /home/osmoleads/Osmoleads && /home/osmoleads/Osmoleads/venv/bin/python -m backend.app.services.scheduler >> /home/osmoleads/Osmoleads/logs/cron.log 2>&1
```

Guardar y salir.

### 10.2 Crear directorio de logs

```bash
mkdir -p /home/osmoleads/Osmoleads/logs
```

---

## 11. Verificar instalación

### 11.1 Lista de verificación

Ejecuta estos comandos para verificar que todo funciona:

```bash
# 1. Verificar PostgreSQL
sudo systemctl status postgresql
# Debe decir: active (running)

# 2. Verificar Backend
sudo systemctl status osmoleads-backend
# Debe decir: active (running)

# 3. Verificar Nginx
sudo systemctl status nginx
# Debe decir: active (running)

# 4. Verificar que la API responde
curl http://localhost:8000/api/health
# Debe devolver: {"status": "ok"}

# 5. Verificar certificado SSL
curl -I https://osmoleads.com
# Debe mostrar: HTTP/2 200
```

### 11.2 Probar la aplicación

1. Abre: `https://osmoleads.com`
2. Introduce el PIN: `Osmo1980`
3. Deberías ver el panel principal
4. Ve a "Países" y crea uno de prueba
5. Añade una palabra clave
6. Pulsa "Buscar"
7. Verifica que aparecen resultados

---

## 12. Solución de problemas

### Error: "Connection refused" al acceder a la web

```bash
# Verificar que Nginx está corriendo
sudo systemctl status nginx

# Si está parado, iniciarlo
sudo systemctl start nginx

# Ver logs de error
sudo tail -50 /var/log/nginx/error.log
```

### Error: "502 Bad Gateway"

```bash
# El backend no está corriendo
sudo systemctl status osmoleads-backend

# Reiniciar backend
sudo systemctl restart osmoleads-backend

# Ver logs del backend
sudo journalctl -u osmoleads-backend -n 50
```

### Error: "Database connection failed"

```bash
# Verificar PostgreSQL
sudo systemctl status postgresql

# Verificar credenciales en .env
cat /home/osmoleads/Osmoleads/backend/.env

# Probar conexión manual
psql -h localhost -U osmoleads_user -d osmoleads_db
```

### Error: "Google API quota exceeded"

Has superado las 100 búsquedas diarias gratuitas. Opciones:
1. Esperar hasta mañana (se resetea a medianoche hora del Pacífico)
2. Configurar facturación en Google Cloud para más búsquedas

### La web no carga después de cambiar código

```bash
# Recompilar frontend
cd /home/osmoleads/Osmoleads/frontend
npm run build

# Copiar archivos nuevos
sudo cp -r dist/* /var/www/osmoleads/

# Limpiar caché de Nginx
sudo systemctl restart nginx
```

### Cómo ver los logs

```bash
# Logs del backend
sudo journalctl -u osmoleads-backend -f

# Logs de Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Logs de las búsquedas automáticas
tail -f /home/osmoleads/Osmoleads/logs/cron.log
```

---

## Comandos útiles de referencia

```bash
# Reiniciar todo
sudo systemctl restart postgresql
sudo systemctl restart osmoleads-backend
sudo systemctl restart nginx

# Ver estado de todo
sudo systemctl status postgresql osmoleads-backend nginx

# Actualizar código desde GitHub
cd /home/osmoleads/Osmoleads
git pull origin main
source venv/bin/activate
pip install -r backend/requirements.txt
cd frontend && npm install && npm run build
sudo cp -r dist/* /var/www/osmoleads/
sudo systemctl restart osmoleads-backend
```

---

## Siguiente paso

Una vez completada la instalación, lee el documento **[MANUAL_DE_USO.md](./MANUAL_DE_USO.md)** para aprender a usar la aplicación.
