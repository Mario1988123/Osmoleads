/**
 * Servicio de API para comunicación con el backend.
 */
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || '/api'

// Crear instancia de axios
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor para añadir token de autenticación
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('osmoleads_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Interceptor para manejar errores de autenticación
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('osmoleads_token')
      window.location.href = '/'
    }
    return Promise.reject(error)
  }
)

// ============ Auth ============
export const authAPI = {
  verifyPin: (pin) => api.post('/auth/verify-pin', { pin }),
  logout: () => api.post('/auth/logout'),
}

// ============ Countries ============
export const countriesAPI = {
  list: () => api.get('/countries'),
  get: (id) => api.get(`/countries/${id}`),
  create: (data) => api.post('/countries', data),
  update: (id, data) => api.put(`/countries/${id}`, data),
  delete: (id) => api.delete(`/countries/${id}`),
  uploadFlag: (id, file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post(`/countries/${id}/flag`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}

// ============ Keywords ============
export const keywordsAPI = {
  listByCountry: (countryId, activeOnly = false) =>
    api.get(`/keywords/country/${countryId}`, { params: { active_only: activeOnly } }),
  get: (id) => api.get(`/keywords/${id}`),
  create: (data) => api.post('/keywords', data),
  update: (id, data) => api.put(`/keywords/${id}`, data),
  delete: (id) => api.delete(`/keywords/${id}`),
  toggle: (id) => api.post(`/keywords/${id}/toggle`),
}

// ============ Leads ============
export const leadsAPI = {
  listByCountry: (countryId, params = {}) =>
    api.get(`/leads/country/${countryId}`, { params }),
  getStats: (countryId) => api.get(`/leads/country/${countryId}/stats`),
  get: (id) => api.get(`/leads/${id}`),
  update: (id, data) => api.put(`/leads/${id}`, data),
  move: (id, tab) => api.post(`/leads/${id}/move/${tab}`),
  extractContact: (id) => api.post(`/leads/${id}/extract-contact`),
  delete: (id) => api.delete(`/leads/${id}`),
  // Notas
  getNotes: (leadId) => api.get(`/leads/${leadId}/notes`),
  createNote: (leadId, content) => api.post(`/leads/${leadId}/notes`, { content }),
  deleteNote: (leadId, noteId) => api.delete(`/leads/${leadId}/notes/${noteId}`),
  // Exportar
  export: (countryId, tab = null) => {
    const params = tab ? { tab } : {}
    return api.get(`/leads/country/${countryId}/export`, {
      params,
      responseType: 'blob',
    })
  },
  exportAll: (countryId) =>
    api.get(`/leads/country/${countryId}/export-all`, { responseType: 'blob' }),
}

// ============ Search ============
export const searchAPI = {
  getStats: () => api.get('/search/stats'),
  searchCountry: (countryId, keywordIds = null) =>
    api.post(`/search/country/${countryId}`, null, {
      params: keywordIds ? { keyword_ids: keywordIds } : {},
    }),
  searchAll: () => api.post('/search/all'),
  getHistory: (countryId = null, limit = 50) =>
    api.get('/search/history', { params: { country_id: countryId, limit } }),
}

// ============ Statuses ============
export const statusesAPI = {
  list: () => api.get('/statuses'),
  get: (id) => api.get(`/statuses/${id}`),
  create: (data) => api.post('/statuses', data),
  update: (id, data) => api.put(`/statuses/${id}`, data),
  delete: (id) => api.delete(`/statuses/${id}`),
}

// ============ Settings ============
export const settingsAPI = {
  get: () => api.get('/settings'),
  update: (data) => api.put('/settings', data),
  // Marketplaces
  listMarketplaces: () => api.get('/settings/marketplaces'),
  addMarketplace: (data) => api.post('/settings/marketplaces', data),
  deleteMarketplace: (id) => api.delete(`/settings/marketplaces/${id}`),
}

// ============ Images ============
export const imagesAPI = {
  searchByImage: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/images/search', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  extractText: (file, language = 'es') => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/images/ocr', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      params: { language },
    })
  },
}

// ============ Suggestions ============
export const suggestionsAPI = {
  getByCountry: (countryId) => api.get(`/suggestions/country/${countryId}`),
  analyze: (countryId, limit = 20) =>
    api.post(`/suggestions/analyze/${countryId}`, null, { params: { limit } }),
  add: (id) => api.post(`/suggestions/${id}/add`),
  ignore: (id) => api.post(`/suggestions/${id}/ignore`),
  getRanking: (countryId) => api.get(`/suggestions/ranking/${countryId}`),
}

export default api
