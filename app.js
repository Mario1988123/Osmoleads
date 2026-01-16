// Osmofilter CRM Leads V2.0 - Application Logic

class OsmofilterCRMV2 {
    constructor() {
        this.companies = [];
        this.keywords = [];
        this.discarded = [];
        
        this.init();
    }
    
    async init() {
        await this.loadData();
        this.setupEventListeners();
        this.renderAll();
    }
    
    async loadData() {
        try {
            const [companiesRes, keywordsRes, discardedRes] = await Promise.all([
                fetch('data/companies.json'),
                fetch('data/keywords.json'),
                fetch('data/discarded.json')
            ]);
            
            this.companies = await companiesRes.json();
            this.keywords = await keywordsRes.json();
            this.discarded = await discardedRes.json();
        } catch (error) {
            console.log('Inicializando datos...');
            this.companies = [];
            this.keywords = [];
            this.discarded = [];
        }
    }
    
    setupEventListeners() {
        // Tabs
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.switchTab(e.target.closest('.tab-btn').dataset.tab));
        });
        
        // Modals
        document.getElementById('addKeywordBtn').addEventListener('click', () => this.showModal('keywordModal'));
        
        // Close modals
        document.querySelectorAll('.close').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.target.closest('.modal').style.display = 'none';
            });
        });
        
        // Cancel buttons
        document.getElementById('cancelKeyword')?.addEventListener('click', () => {
            document.getElementById('keywordModal').style.display = 'none';
        });
        document.getElementById('cancelNotes')?.addEventListener('click', () => {
            document.getElementById('notesModal').style.display = 'none';
        });
        
        // Forms
        document.getElementById('keywordForm').addEventListener('submit', (e) => this.addKeyword(e));
        document.getElementById('notesForm').addEventListener('submit', (e) => this.saveNotes(e));
        
        // Image upload
        document.getElementById('imageInput')?.addEventListener('change', (e) => this.handleImageUpload(e));
        
        // Search inputs
        document.getElementById('searchPending')?.addEventListener('input', (e) => this.searchCompanies(e.target.value, 'pending'));
        document.getElementById('searchMyClients')?.addEventListener('input', (e) => this.searchCompanies(e.target.value, 'my-client'));
        document.getElementById('searchColleague')?.addEventListener('input', (e) => this.searchCompanies(e.target.value, 'colleague-client'));
        document.getElementById('searchInProgress')?.addEventListener('input', (e) => this.searchCompanies(e.target.value, 'in-progress'));
        document.getElementById('searchCaptured')?.addEventListener('input', (e) => this.searchCompanies(e.target.value, 'captured'));
    }
    
    switchTab(tabName) {
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(tabName).classList.add('active');
    }
    
    renderAll() {
        this.updateStats();
        this.renderCompaniesByStatus();
        this.renderKeywords();
    }
    
    updateStats() {
        const total = this.companies.length;
        const pending = this.companies.filter(c => c.status === 'pending').length;
        const myClients = this.companies.filter(c => c.status === 'my-client').length;
        const colleague = this.companies.filter(c => c.status === 'colleague-client').length;
        
        document.getElementById('totalCompanies').textContent = total;
        document.getElementById('pendingCompanies').textContent = pending;
        document.getElementById('myClients').textContent = myClients;
        document.getElementById('colleagueClients').textContent = colleague;
    }
    
    renderCompaniesByStatus() {
        this.renderCompaniesGrid('pending', 'pendingGrid');
        this.renderCompaniesGrid('my-client', 'myClientsGrid');
        this.renderCompaniesGrid('colleague-client', 'colleagueGrid');
        this.renderCompaniesGrid('in-progress', 'inProgressGrid');
        this.renderCompaniesGrid('captured', 'capturedGrid');
    }
    
    renderCompaniesGrid(status, gridId) {
        const grid = document.getElementById(gridId);
        const companies = this.companies.filter(c => c.status === status);
        
        if (companies.length === 0) {
            grid.innerHTML = `
                <div class="empty-state" style="grid-column: 1/-1;">
                    <div class="empty-state-icon"><i class="fas fa-inbox"></i></div>
                    <div class="empty-state-text">No hay empresas en esta categoría</div>
                </div>
            `;
            return;
        }
        
        grid.innerHTML = companies.map(company => this.createCompanyCard(company)).join('');
        
        // Añadir event listeners a los selects
        grid.querySelectorAll('.status-select').forEach(select => {
            select.addEventListener('change', (e) => this.quickStatusChange(e.target.value, e.target.dataset.id));
        });
    }
    
    createCompanyCard(company) {
        return `
            <div class="company-card" data-id="${company.id}">
                <h3 class="company-name">${company.name}</h3>
                <a href="${company.url}" target="_blank" class="company-url">
                    <i class="fas fa-external-link-alt"></i>
                    ${this.extractDomain(company.url)}
                </a>
                
                <div class="company-info">
                    ${company.email ? `
                        <div class="info-row">
                            <i class="fas fa-envelope"></i>
                            <strong>${company.email}</strong>
                        </div>
                    ` : ''}
                    ${company.phone ? `
                        <div class="info-row">
                            <i class="fas fa-phone"></i>
                            <strong>${company.phone}</strong>
                        </div>
                    ` : ''}
                    ${company.cif ? `
                        <div class="info-row">
                            <i class="fas fa-id-card"></i>
                            <strong>CIF: ${company.cif}</strong>
                        </div>
                    ` : ''}
                    <div class="info-row">
                        <i class="fas fa-calendar"></i>
                        Encontrado: ${new Date(company.foundDate).toLocaleDateString('es-ES')}
                    </div>
                    <div class="info-row">
                        <i class="fas fa-key"></i>
                        Por: "${company.foundBy}"
                    </div>
                </div>
                
                ${company.products && company.products.length > 0 ? `
                    <div class="products-tags">
                        ${company.products.map(p => `<span class="product-tag">${p}</span>`).join('')}
                    </div>
                ` : ''}
                
                ${company.notes ? `
                    <div class="info-row" style="margin: 12px 0;">
                        <i class="fas fa-sticky-note"></i>
                        <em>${company.notes}</em>
                    </div>
                ` : ''}
                
                <div class="company-actions">
                    <select class="status-select" data-id="${company.id}">
                        <option value="pending" ${company.status === 'pending' ? 'selected' : ''}>⏳ Pendiente</option>
                        <option value="captured" ${company.status === 'captured' ? 'selected' : ''}>✅ Captado</option>
                        <option value="my-client" ${company.status === 'my-client' ? 'selected' : ''}>👤 Mi Cliente</option>
                        <option value="colleague-client" ${company.status === 'colleague-client' ? 'selected' : ''}>👥 Cliente Compañero</option>
                        <option value="in-progress" ${company.status === 'in-progress' ? 'selected' : ''}>🔄 En Proceso</option>
                    </select>
                    
                    <button class="btn-icon btn-secondary" onclick="crm.addNote('${company.id}')" title="Añadir nota">
                        <i class="fas fa-sticky-note"></i>
                    </button>
                    
                    <button class="btn-icon btn-danger" onclick="crm.discardCompany('${company.id}')" title="Descartar">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    }
    
    async quickStatusChange(newStatus, companyId) {
        const company = this.companies.find(c => c.id === companyId);
        if (!company) return;
        
        company.status = newStatus;
        company.lastModified = new Date().toISOString();
        
        await this.saveToGitHub();
        this.renderAll();
        
        // Mostrar notificación
        this.showNotification(`Estado actualizado a: ${this.getStatusLabel(newStatus)}`);
    }
    
    addNote(companyId) {
        const company = this.companies.find(c => c.id === companyId);
        if (!company) return;
        
        document.getElementById('notesCompanyId').value = companyId;
        document.getElementById('notesText').value = company.notes || '';
        this.showModal('notesModal');
    }
    
    async saveNotes(e) {
        e.preventDefault();
        
        const companyId = document.getElementById('notesCompanyId').value;
        const notes = document.getElementById('notesText').value;
        
        const company = this.companies.find(c => c.id === companyId);
        if (company) {
            company.notes = notes;
            company.lastModified = new Date().toISOString();
        }
        
        await this.saveToGitHub();
        document.getElementById('notesModal').style.display = 'none';
        this.renderAll();
        
        this.showNotification('Nota guardada correctamente');
    }
    
    async discardCompany(companyId) {
        if (!confirm('¿Descartar esta empresa? No volverá a aparecer en futuras búsquedas.')) return;
        
        const company = this.companies.find(c => c.id === companyId);
        if (!company) return;
        
        // Mover a descartados
        this.discarded.push({
            id: company.id,
            url: company.url,
            domain: company.domain,
            name: company.name,
            reason: 'Descartado manualmente',
            date: new Date().toISOString()
        });
        
        // Eliminar de empresas
        this.companies = this.companies.filter(c => c.id !== companyId);
        
        await this.saveToGitHub();
        this.renderAll();
        
        this.showNotification('Empresa descartada');
    }
    
    searchCompanies(query, status) {
        const companies = this.companies.filter(c => c.status === status);
        
        if (!query) {
            this.renderCompaniesGrid(status, this.getGridId(status));
            return;
        }
        
        const filtered = companies.filter(c => 
            c.name.toLowerCase().includes(query.toLowerCase()) ||
            c.url.toLowerCase().includes(query.toLowerCase()) ||
            (c.email && c.email.toLowerCase().includes(query.toLowerCase()))
        );
        
        const grid = document.getElementById(this.getGridId(status));
        if (filtered.length === 0) {
            grid.innerHTML = `
                <div class="empty-state" style="grid-column: 1/-1;">
                    <div class="empty-state-icon"><i class="fas fa-search"></i></div>
                    <div class="empty-state-text">No se encontraron resultados</div>
                </div>
            `;
            return;
        }
        
        grid.innerHTML = filtered.map(company => this.createCompanyCard(company)).join('');
        
        grid.querySelectorAll('.status-select').forEach(select => {
            select.addEventListener('change', (e) => this.quickStatusChange(e.target.value, e.target.dataset.id));
        });
    }
    
    getGridId(status) {
        const mapping = {
            'pending': 'pendingGrid',
            'my-client': 'myClientsGrid',
            'colleague-client': 'colleagueGrid',
            'in-progress': 'inProgressGrid',
            'captured': 'capturedGrid'
        };
        return mapping[status];
    }
    
    renderKeywords() {
        const container = document.getElementById('keywordsList');
        
        if (this.keywords.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon"><i class="fas fa-key"></i></div>
                    <div class="empty-state-text">No hay palabras clave configuradas</div>
                </div>
            `;
            return;
        }
        
        container.innerHTML = this.keywords.map(keyword => `
            <div class="keyword-card">
                <h3>${keyword.text}</h3>
                <div class="keyword-meta">${keyword.results || 0} resultados encontrados</div>
                <span class="keyword-category">${keyword.category}</span>
                <button class="btn-danger btn-icon" style="margin-top: 12px;" onclick="crm.deleteKeyword('${keyword.id}')">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `).join('');
    }
    
    async addKeyword(e) {
        e.preventDefault();
        
        const keyword = {
            id: Date.now().toString(),
            text: document.getElementById('newKeyword').value,
            category: document.getElementById('keywordCategory').value,
            results: 0,
            addedDate: new Date().toISOString()
        };
        
        this.keywords.push(keyword);
        await this.saveToGitHub();
        
        document.getElementById('keywordModal').style.display = 'none';
        document.getElementById('keywordForm').reset();
        this.renderKeywords();
        
        this.showNotification('Palabra clave añadida');
    }
    
    async deleteKeyword(id) {
        if (!confirm('¿Eliminar esta palabra clave?')) return;
        
        this.keywords = this.keywords.filter(k => k.id !== id);
        await this.saveToGitHub();
        this.renderKeywords();
        
        this.showNotification('Palabra clave eliminada');
    }
    
    async handleImageUpload(e) {
        const file = e.target.files[0];
        if (!file) return;
        
        const resultsDiv = document.getElementById('imageResults');
        resultsDiv.innerHTML = '<div class="loading">Buscando productos similares...</div>';
        
        // Simular búsqueda por ahora
        setTimeout(() => {
            resultsDiv.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon"><i class="fas fa-info-circle"></i></div>
                    <div class="empty-state-text">
                        Funcionalidad de búsqueda por imagen en desarrollo.<br>
                        Requiere configuración adicional de Google Vision API.
                    </div>
                </div>
            `;
        }, 1500);
    }
    
    async saveToGitHub() {
        localStorage.setItem('osmofilter_companies', JSON.stringify(this.companies));
        localStorage.setItem('osmofilter_keywords', JSON.stringify(this.keywords));
        localStorage.setItem('osmofilter_discarded', JSON.stringify(this.discarded));
    }
    
    showModal(modalId) {
        document.getElementById(modalId).style.display = 'block';
    }
    
    showNotification(message) {
        // Crear notificación temporal
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #10b981, #059669);
            color: white;
            padding: 16px 24px;
            border-radius: 8px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            z-index: 9999;
            animation: slideIn 0.3s ease-out;
        `;
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
    
    getStatusLabel(status) {
        const labels = {
            'pending': '⏳ Pendiente',
            'captured': '✅ Captado',
            'my-client': '👤 Mi Cliente',
            'colleague-client': '👥 Cliente Compañero',
            'in-progress': '🔄 En Proceso'
        };
        return labels[status] || status;
    }
    
    extractDomain(url) {
        try {
            const domain = new URL(url).hostname.replace('www.', '');
            return domain.length > 35 ? domain.substring(0, 35) + '...' : domain;
        } catch {
            return url.substring(0, 35) + '...';
        }
    }
}

// Animaciones CSS adicionales
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(400px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(400px); opacity: 0; }
    }
`;
document.head.appendChild(style);

// Initialize app
let crm;
document.addEventListener('DOMContentLoaded', () => {
    crm = new OsmofilterCRMV2();
});
