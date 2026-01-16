#!/usr/bin/env python3
"""
Osmofilter Lead Finder V2.0 - Script mejorado con filtros avanzados
"""

import json
import os
import time
import re
from datetime import datetime
from urllib.parse import urlparse
import requests

# Configuración de API
API_KEY = os.environ.get('GOOGLE_API_KEY', '')
SEARCH_ENGINE_ID = os.environ.get('SEARCH_ENGINE_ID', '')

# Archivos de datos
DATA_DIR = 'data'
COMPANIES_FILE = f'{DATA_DIR}/companies.json'
KEYWORDS_FILE = f'{DATA_DIR}/keywords.json'
DISCARDED_FILE = f'{DATA_DIR}/discarded.json'

class LeadFinderV2:
    def __init__(self):
        self.api_key = API_KEY
        self.search_engine_id = SEARCH_ENGINE_ID
        self.companies = self.load_json(COMPANIES_FILE)
        self.keywords = self.load_json(KEYWORDS_FILE)
        self.discarded = self.load_json(DISCARDED_FILE)
        
        # Dominios principales ya procesados
        self.existing_domains = set(self.extract_main_domain(c['url']) for c in self.companies)
        self.discarded_domains = set(self.extract_main_domain(d['url']) for d in self.discarded)
        
        # Marketplaces y sitios a excluir
        self.excluded_sites = [
            'amazon', 'aliexpress', 'ebay', 'mercadolibre', 'alibaba',
            'leroymerlin', 'bricodepot', 'bauhaus', 'manomano',
            'youtube', 'vimeo', 'dailymotion', 'facebook', 'instagram',
            'twitter', 'linkedin', 'pinterest', 'tiktok',
            'wikipedia', 'wikihow', 'scribd', 'slideshare',
            'idealo', 'milanuncios', 'wallapop', 'segundamano',
            'google', 'bing', 'yahoo'
        ]
        
    def load_json(self, filepath):
        """Carga un archivo JSON"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def save_json(self, filepath, data):
        """Guarda datos en un archivo JSON"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def extract_main_domain(self, url):
        """Extrae solo el dominio principal (sin www, sin subdominios, sin rutas)"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.replace('www.', '')
            
            # Eliminar subdominios (quedarse solo con dominio.extension)
            parts = domain.split('.')
            if len(parts) > 2:
                # Para .es, .com.es, etc.
                if parts[-2] in ['com', 'co', 'org', 'net', 'edu', 'gov']:
                    domain = '.'.join(parts[-3:])
                else:
                    domain = '.'.join(parts[-2:])
            
            return domain.lower()
        except:
            return url.lower()
    
    def is_excluded_site(self, url):
        """Verifica si el sitio debe ser excluido"""
        url_lower = url.lower()
        domain = self.extract_main_domain(url)
        
        # Verificar sitios excluidos
        for excluded in self.excluded_sites:
            if excluded in url_lower or excluded in domain:
                return True
        
        # Verificar si es PDF o archivo descargable
        if url_lower.endswith(('.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.rar')):
            return True
        
        return False
    
    def is_duplicate_domain(self, url):
        """Verifica si el dominio principal ya existe"""
        domain = self.extract_main_domain(url)
        return domain in self.existing_domains or domain in self.discarded_domains
    
    def search_google(self, keyword, num_results=5):
        """Realiza una búsqueda en Google Custom Search API"""
        url = 'https://www.googleapis.com/customsearch/v1'
        
        params = {
            'key': self.api_key,
            'cx': self.search_engine_id,
            'q': keyword,
            'num': num_results,
            'gl': 'es',
            'lr': 'lang_es',
            'dateRestrict': 'y1'  # Último año - prioriza sitios activos
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            if 'items' in data:
                for item in data['items']:
                    results.append({
                        'title': item.get('title', ''),
                        'url': item.get('link', ''),
                        'snippet': item.get('snippet', ''),
                        'displayUrl': item.get('displayLink', '')
                    })
            
            return results
        except requests.exceptions.RequestException as e:
            print(f'❌ Error en búsqueda "{keyword}": {e}')
            return []
    
    def extract_contact_info(self, url):
        """Extrae información de contacto de la página web"""
        contact_info = {
            'email': None,
            'phone': None,
            'cif': None,
            'social_name': None
        }
        
        try:
            # Intentar acceder a página de contacto o legal
            contact_urls = [
                url + '/contacto',
                url + '/contact',
                url + '/aviso-legal',
                url + '/legal',
                url + '/empresa',
                url + '/about',
                url
            ]
            
            for contact_url in contact_urls[:2]:  # Solo 2 intentos para no saturar
                try:
                    response = requests.get(contact_url, timeout=5, headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    })
                    
                    if response.status_code == 200:
                        text = response.text
                        
                        # Buscar email
                        if not contact_info['email']:
                            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                            emails = re.findall(email_pattern, text)
                            if emails:
                                # Filtrar emails genéricos
                                valid_emails = [e for e in emails if not any(x in e.lower() for x in ['example', 'sentry', 'google', 'facebook'])]
                                if valid_emails:
                                    contact_info['email'] = valid_emails[0]
                        
                        # Buscar teléfono
                        if not contact_info['phone']:
                            phone_pattern = r'(\+34\s?)?[6789]\d{2}\s?\d{2}\s?\d{2}\s?\d{2}'
                            phones = re.findall(phone_pattern, text)
                            if phones:
                                contact_info['phone'] = phones[0].strip()
                        
                        # Buscar CIF/NIF
                        if not contact_info['cif']:
                            cif_pattern = r'\b[A-Z]\d{8}\b|\b\d{8}[A-Z]\b'
                            cifs = re.findall(cif_pattern, text)
                            if cifs:
                                contact_info['cif'] = cifs[0]
                        
                        # Si ya tenemos algo, no seguir buscando
                        if contact_info['email'] or contact_info['phone']:
                            break
                            
                except:
                    continue
                    
                time.sleep(0.5)  # Pequeña pausa entre peticiones
                
        except Exception as e:
            print(f'   ⚠️  No se pudo extraer info de contacto: {e}')
        
        return contact_info
    
    def extract_keywords_from_text(self, text):
        """Extrae palabras clave relevantes del texto"""
        # Palabras clave del sector
        sector_keywords = [
            'osmosis', 'inversa', 'descalcificador', 'purificador', 'tratamiento',
            'filtro', 'agua', 'potable', 'industrial', 'domestico', 'residencial',
            'desaladora', 'ablandador', 'filtración', 'potabilizadora',
            'dispensador', 'fuente', 'hidrico', 'desinfección', 'cloración',
            'ultrafiltracion', 'nanofiltración', 'membrane', 'resina', 'carbon'
        ]
        
        text_lower = text.lower()
        found_keywords = []
        
        for keyword in sector_keywords:
            if keyword in text_lower and keyword not in found_keywords:
                found_keywords.append(keyword)
        
        return found_keywords[:10]  # Máximo 10 keywords
    
    def analyze_result(self, result):
        """Analiza un resultado para determinar si es relevante"""
        url = result['url'].lower()
        title = result['title'].lower()
        snippet = result['snippet'].lower()
        
        # Verificar si está excluido
        if self.is_excluded_site(url):
            return False
        
        # Palabras clave que indican relevancia
        relevant_keywords = [
            'tratamiento', 'agua', 'osmosis', 'purificador', 'descalcificador',
            'filtro', 'potabilizadora', 'industrial', 'hidrico', 'potable',
            'desaladora', 'depuradora', 'dispensador', 'fuente', 'ablandador'
        ]
        
        # Verificar relevancia
        text = f'{title} {snippet}'
        relevant_count = sum(1 for word in relevant_keywords if word in text)
        
        # Es relevante si tiene al menos 2 palabras clave
        return relevant_count >= 2
    
    def run_search(self):
        """Ejecuta búsquedas para todas las palabras clave"""
        print('🔍 Iniciando búsqueda de empresas V2.0...\n')
        
        new_companies_count = 0
        discarded_count = 0
        new_keywords_found = set()
        
        for keyword_obj in self.keywords:
            keyword = keyword_obj['text']
            print(f'🔎 Buscando: "{keyword}"')
            
            results = self.search_google(keyword, num_results=5)
            
            if not results:
                print(f'   ⚠️  No se encontraron resultados\n')
                continue
            
            print(f'   ✅ {len(results)} resultados encontrados')
            
            for result in results:
                url = result['url']
                main_domain = self.extract_main_domain(url)
                
                # Verificar exclusiones y duplicados
                if self.is_excluded_site(url):
                    print(f'   ⛔ Excluido (marketplace/video): {main_domain}')
                    continue
                
                if self.is_duplicate_domain(url):
                    print(f'   🔄 Dominio duplicado, omitiendo: {main_domain}')
                    continue
                
                # Analizar relevancia
                if not self.analyze_result(result):
                    print(f'   ❌ No relevante: {result["title"][:50]}...')
                    # Guardar en descartados
                    self.discarded.append({
                        'id': str(int(time.time() * 1000)),
                        'url': url,
                        'domain': main_domain,
                        'reason': 'No relevante',
                        'foundBy': keyword,
                        'date': datetime.now().isoformat()
                    })
                    self.discarded_domains.add(main_domain)
                    discarded_count += 1
                    continue
                
                # Empresa relevante - extraer info
                print(f'   🔍 Analizando: {result["title"][:50]}...')
                
                # Extraer información de contacto
                contact_info = self.extract_contact_info(url)
                
                # Extraer keywords del snippet
                detected_keywords = self.extract_keywords_from_text(result['snippet'] + ' ' + result['title'])
                new_keywords_found.update(detected_keywords)
                
                # Crear empresa
                company = {
                    'id': str(int(time.time() * 1000)),
                    'name': result['title'],
                    'url': url,
                    'domain': main_domain,
                    'status': 'pending',
                    'products': detected_keywords,
                    'email': contact_info['email'],
                    'phone': contact_info['phone'],
                    'cif': contact_info['cif'],
                    'socialName': contact_info['social_name'],
                    'foundDate': datetime.now().isoformat(),
                    'foundBy': keyword,
                    'snippet': result['snippet'],
                    'notes': ''
                }
                
                self.companies.append(company)
                self.existing_domains.add(main_domain)
                new_companies_count += 1
                
                if contact_info['email']:
                    print(f'   ✅ Empresa añadida: {result["title"][:50]}... [📧 {contact_info["email"]}]')
                else:
                    print(f'   ✅ Empresa añadida: {result["title"][:50]}...')
                
                # Pausa para no saturar
                time.sleep(1)
            
            # Actualizar contador de resultados del keyword
            keyword_obj['results'] = len(results)
            keyword_obj['lastSearch'] = datetime.now().isoformat()
            
            print()
            time.sleep(2)  # Pausa entre keywords
        
        # Sugerir nuevas keywords encontradas
        if new_keywords_found:
            print('\n💡 Nuevas palabras clave detectadas:')
            for kw in sorted(new_keywords_found)[:10]:
                print(f'   • {kw}')
        
        # Guardar datos actualizados
        self.save_json(COMPANIES_FILE, self.companies)
        self.save_json(KEYWORDS_FILE, self.keywords)
        self.save_json(DISCARDED_FILE, self.discarded)
        
        print('\n' + '='*60)
        print(f'✅ Búsqueda completada!')
        print(f'📊 Nuevas empresas relevantes: {new_companies_count}')
        print(f'❌ Descartadas (no relevantes): {discarded_count}')
        print(f'📋 Total empresas en BD: {len(self.companies)}')
        print(f'🗑️  Total descartadas: {len(self.discarded)}')
        print('='*60)

if __name__ == '__main__':
    if not API_KEY or not SEARCH_ENGINE_ID:
        print('❌ Error: Faltan credenciales de API')
        print('Configura GOOGLE_API_KEY y SEARCH_ENGINE_ID en GitHub Secrets')
        exit(1)
    
    finder = LeadFinderV2()
    finder.run_search()
