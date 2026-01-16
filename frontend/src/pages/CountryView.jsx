/**
 * Vista de un país - Leads, Keywords, Análisis.
 */
import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Search,
  Plus,
  Download,
  Filter,
  Grid,
  List,
  Loader,
  RefreshCw,
  FileText,
  AlertCircle,
  Trash2,
  Phone,
  Mail,
  ExternalLink,
  MessageSquare,
  ChevronDown,
  Check,
  X,
} from 'lucide-react'
import toast from 'react-hot-toast'
import Layout from '../components/Layout'
import Modal from '../components/Modal'
import {
  countriesAPI,
  keywordsAPI,
  leadsAPI,
  searchAPI,
  statusesAPI,
  suggestionsAPI,
} from '../services/api'
import { useLeadsStore, useSearchStore } from '../services/store'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'

// Pestañas disponibles
const TABS = [
  { id: 'new', label: 'Leads Nuevos', color: 'blue' },
  { id: 'leads', label: 'Leads', color: 'green' },
  { id: 'doubts', label: 'Dudas', color: 'yellow' },
  { id: 'discarded', label: 'Descartados', color: 'red' },
  { id: 'marketplace', label: 'Marketplaces', color: 'gray' },
  { id: 'keywords', label: 'Keywords', color: 'purple' },
  { id: 'analysis', label: 'Análisis', color: 'indigo' },
]

function CountryView() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [country, setCountry] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  // Estado de leads
  const {
    leads,
    setLeads,
    stats,
    setStats,
    currentTab,
    setCurrentTab,
    filters,
    setFilters,
    viewMode,
    setViewMode,
  } = useLeadsStore()

  // Estado de búsqueda
  const { isSearching, setSearching } = useSearchStore()

  // Keywords y estados
  const [keywords, setKeywords] = useState([])
  const [statuses, setStatuses] = useState([])
  const [suggestions, setSuggestions] = useState([])

  // Modales
  const [showKeywordModal, setShowKeywordModal] = useState(false)
  const [showLeadModal, setShowLeadModal] = useState(false)
  const [selectedLead, setSelectedLead] = useState(null)
  const [newKeyword, setNewKeyword] = useState({ text: '', category: 'general', results_per_search: 5 })

  // Cargar datos al montar
  useEffect(() => {
    loadCountry()
    loadStatuses()
  }, [id])

  useEffect(() => {
    if (country) {
      loadLeads()
      loadKeywords()
    }
  }, [country, currentTab, filters])

  const loadCountry = async () => {
    try {
      const response = await countriesAPI.get(id)
      setCountry(response.data)
    } catch (error) {
      toast.error('País no encontrado')
      navigate('/dashboard')
    } finally {
      setIsLoading(false)
    }
  }

  const loadLeads = async () => {
    if (!['new', 'leads', 'doubts', 'discarded', 'marketplace'].includes(currentTab)) return

    try {
      const response = await leadsAPI.listByCountry(id, {
        tab: currentTab,
        ...filters,
      })
      setLeads(response.data)

      // Cargar stats
      const statsResponse = await leadsAPI.getStats(id)
      setStats(statsResponse.data)
    } catch (error) {
      console.error('Error loading leads:', error)
    }
  }

  const loadKeywords = async () => {
    try {
      const response = await keywordsAPI.listByCountry(id)
      setKeywords(response.data)
    } catch (error) {
      console.error('Error loading keywords:', error)
    }
  }

  const loadStatuses = async () => {
    try {
      const response = await statusesAPI.list()
      setStatuses(response.data)
    } catch (error) {
      console.error('Error loading statuses:', error)
    }
  }

  const loadSuggestions = async () => {
    try {
      const response = await suggestionsAPI.getRanking(id)
      setSuggestions(response.data)
    } catch (error) {
      console.error('Error loading suggestions:', error)
    }
  }

  const handleSearch = async () => {
    setSearching(true)
    try {
      const response = await searchAPI.searchCountry(id)
      toast.success(`${response.data.new_leads} nuevos leads encontrados`)
      loadLeads()
      loadCountry()
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error en la búsqueda')
    } finally {
      setSearching(false)
    }
  }

  const handleExport = async () => {
    try {
      const response = await leadsAPI.export(id, currentTab !== 'keywords' && currentTab !== 'analysis' ? currentTab : null)
      const blob = new Blob([response.data], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `leads_${currentTab}_${format(new Date(), 'yyyyMMdd')}.xlsx`
      a.click()
      window.URL.revokeObjectURL(url)
      toast.success('Excel descargado')
    } catch (error) {
      toast.error('Error al exportar')
    }
  }

  const handleCreateKeyword = async (e) => {
    e.preventDefault()
    if (!newKeyword.text.trim()) {
      toast.error('Escribe la keyword')
      return
    }

    try {
      await keywordsAPI.create({
        country_id: parseInt(id),
        ...newKeyword,
      })
      toast.success('Keyword añadida')
      setShowKeywordModal(false)
      setNewKeyword({ text: '', category: 'general', results_per_search: 5 })
      loadKeywords()
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error al crear keyword')
    }
  }

  const handleDeleteKeyword = async (keywordId) => {
    if (!confirm('¿Eliminar esta keyword?')) return
    try {
      await keywordsAPI.delete(keywordId)
      toast.success('Keyword eliminada')
      loadKeywords()
    } catch (error) {
      toast.error('Error al eliminar')
    }
  }

  const handleToggleKeyword = async (keywordId) => {
    try {
      await keywordsAPI.toggle(keywordId)
      loadKeywords()
    } catch (error) {
      toast.error('Error al cambiar estado')
    }
  }

  const handleAnalyze = async () => {
    try {
      const response = await suggestionsAPI.analyze(id)
      toast.success(`${response.data.suggestions_added} sugerencias nuevas`)
      loadSuggestions()
    } catch (error) {
      toast.error('Error al analizar')
    }
  }

  if (isLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <Loader className="animate-spin text-primary-600" size={32} />
        </div>
      </Layout>
    )
  }

  return (
    <Layout
      breadcrumbs={[{ label: country?.name }]}
    >
      {/* Header del país */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            {country?.flag_image ? (
              <img
                src={country.flag_image}
                alt={country.name}
                className="w-14 h-14 rounded-xl object-cover"
              />
            ) : (
              <div className="w-14 h-14 bg-primary-100 rounded-xl flex items-center justify-center">
                <span className="text-primary-600 font-bold text-xl">
                  {country?.code}
                </span>
              </div>
            )}
            <div>
              <h1 className="text-2xl font-bold text-gray-800">{country?.name}</h1>
              <p className="text-gray-500">
                {keywords.filter(k => k.is_active).length} keywords activas
              </p>
            </div>
          </div>

          <div className="flex flex-wrap gap-3">
            <button
              onClick={handleSearch}
              disabled={isSearching}
              className="btn-primary"
            >
              {isSearching ? (
                <Loader size={20} className="animate-spin" />
              ) : (
                <Search size={20} />
              )}
              Buscar ahora
            </button>
            <button onClick={handleExport} className="btn-secondary">
              <Download size={20} />
              Exportar
            </button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap gap-2 mb-6 overflow-x-auto pb-2">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => {
              setCurrentTab(tab.id)
              if (tab.id === 'analysis') loadSuggestions()
            }}
            className={`tab whitespace-nowrap ${
              currentTab === tab.id ? 'tab-active' : 'tab-inactive'
            }`}
          >
            {tab.label}
            {stats[tab.id] !== undefined && (
              <span className="ml-2 px-2 py-0.5 rounded-full text-xs bg-white/20">
                {stats[tab.id]}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Contenido según pestaña */}
      {currentTab === 'keywords' ? (
        <KeywordsTab
          keywords={keywords}
          onAdd={() => setShowKeywordModal(true)}
          onDelete={handleDeleteKeyword}
          onToggle={handleToggleKeyword}
        />
      ) : currentTab === 'analysis' ? (
        <AnalysisTab
          suggestions={suggestions}
          onAnalyze={handleAnalyze}
          countryId={id}
          onRefresh={loadSuggestions}
        />
      ) : (
        <LeadsTab
          leads={leads}
          statuses={statuses}
          keywords={keywords}
          viewMode={viewMode}
          setViewMode={setViewMode}
          filters={filters}
          setFilters={setFilters}
          onRefresh={loadLeads}
          onSelectLead={(lead) => {
            setSelectedLead(lead)
            setShowLeadModal(true)
          }}
        />
      )}

      {/* Modal de nueva keyword */}
      <Modal
        isOpen={showKeywordModal}
        onClose={() => setShowKeywordModal(false)}
        title="Nueva Keyword"
      >
        <form onSubmit={handleCreateKeyword} className="space-y-4">
          <div>
            <label className="label">Palabra clave</label>
            <input
              type="text"
              value={newKeyword.text}
              onChange={(e) =>
                setNewKeyword({ ...newKeyword, text: e.target.value })
              }
              placeholder="osmosis inversa"
              className="input"
              autoFocus
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Categoría</label>
              <select
                value={newKeyword.category}
                onChange={(e) =>
                  setNewKeyword({ ...newKeyword, category: e.target.value })
                }
                className="input"
              >
                <option value="general">General</option>
                <option value="producto">Producto</option>
                <option value="competencia">Competencia</option>
              </select>
            </div>
            <div>
              <label className="label">Resultados</label>
              <input
                type="number"
                min="1"
                max="10"
                value={newKeyword.results_per_search}
                onChange={(e) =>
                  setNewKeyword({
                    ...newKeyword,
                    results_per_search: parseInt(e.target.value),
                  })
                }
                className="input"
              />
            </div>
          </div>
          <div className="flex gap-3 pt-4">
            <button type="submit" className="btn-primary flex-1">
              Añadir
            </button>
            <button
              type="button"
              onClick={() => setShowKeywordModal(false)}
              className="btn-secondary"
            >
              Cancelar
            </button>
          </div>
        </form>
      </Modal>

      {/* Modal de detalle de lead */}
      {selectedLead && (
        <LeadDetailModal
          lead={selectedLead}
          statuses={statuses}
          isOpen={showLeadModal}
          onClose={() => {
            setShowLeadModal(false)
            setSelectedLead(null)
          }}
          onUpdate={loadLeads}
        />
      )}
    </Layout>
  )
}

// Componente de pestaña de Keywords
function KeywordsTab({ keywords, onAdd, onDelete, onToggle }) {
  return (
    <div className="card">
      <div className="card-header flex items-center justify-between">
        <h2 className="font-semibold text-gray-800">Keywords de búsqueda</h2>
        <button onClick={onAdd} className="btn-primary">
          <Plus size={18} />
          Nueva keyword
        </button>
      </div>
      <div className="divide-y divide-gray-100">
        {keywords.length === 0 ? (
          <div className="empty-state py-12">
            <FileText size={32} className="text-gray-400 mb-2" />
            <p>No hay keywords configuradas</p>
          </div>
        ) : (
          keywords.map((keyword) => (
            <div
              key={keyword.id}
              className="flex items-center justify-between p-4 hover:bg-gray-50"
            >
              <div className="flex items-center gap-4">
                <button
                  onClick={() => onToggle(keyword.id)}
                  className={`w-10 h-6 rounded-full transition-colors ${
                    keyword.is_active ? 'bg-primary-600' : 'bg-gray-300'
                  }`}
                >
                  <div
                    className={`w-5 h-5 bg-white rounded-full shadow transition-transform ${
                      keyword.is_active ? 'translate-x-4' : 'translate-x-0.5'
                    }`}
                  />
                </button>
                <div>
                  <p className="font-medium text-gray-800">{keyword.text}</p>
                  <p className="text-sm text-gray-500">
                    {keyword.category} · {keyword.total_results} resultados
                  </p>
                </div>
              </div>
              <button
                onClick={() => onDelete(keyword.id)}
                className="btn-icon text-gray-400 hover:text-red-500"
              >
                <Trash2 size={18} />
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

// Componente de pestaña de Leads
function LeadsTab({
  leads,
  statuses,
  keywords,
  viewMode,
  setViewMode,
  filters,
  setFilters,
  onRefresh,
  onSelectLead,
}) {
  return (
    <div>
      {/* Filtros y vista */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
        <div className="flex flex-wrap gap-2">
          <select
            value={filters.keyword_id || ''}
            onChange={(e) =>
              setFilters({ keyword_id: e.target.value || null })
            }
            className="input w-auto"
          >
            <option value="">Todas las keywords</option>
            {keywords.map((kw) => (
              <option key={kw.id} value={kw.id}>
                {kw.text}
              </option>
            ))}
          </select>
          <select
            value={filters.status_id || ''}
            onChange={(e) =>
              setFilters({ status_id: e.target.value || null })
            }
            className="input w-auto"
          >
            <option value="">Todos los estados</option>
            {statuses.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </select>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setViewMode('cards')}
            className={`btn-icon ${viewMode === 'cards' ? 'bg-primary-100 text-primary-600' : ''}`}
          >
            <Grid size={20} />
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={`btn-icon ${viewMode === 'list' ? 'bg-primary-100 text-primary-600' : ''}`}
          >
            <List size={20} />
          </button>
        </div>
      </div>

      {/* Lista de leads */}
      {leads.length === 0 ? (
        <div className="card empty-state py-12">
          <AlertCircle size={32} className="text-gray-400 mb-2" />
          <p>No hay leads en esta pestaña</p>
        </div>
      ) : viewMode === 'cards' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {leads.map((lead) => (
            <LeadCard
              key={lead.id}
              lead={lead}
              statuses={statuses}
              onClick={() => onSelectLead(lead)}
              onRefresh={onRefresh}
            />
          ))}
        </div>
      ) : (
        <div className="card overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Empresa
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Contacto
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Estado
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Keyword
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Fecha
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {leads.map((lead) => (
                <tr
                  key={lead.id}
                  className="hover:bg-gray-50 cursor-pointer"
                  onClick={() => onSelectLead(lead)}
                >
                  <td className="px-4 py-3">
                    <p className="font-medium text-gray-800 truncate max-w-xs">
                      {lead.name}
                    </p>
                    <p className="text-sm text-gray-500">{lead.domain}</p>
                  </td>
                  <td className="px-4 py-3">
                    {lead.email && (
                      <p className="text-sm text-gray-600">{lead.email}</p>
                    )}
                    {lead.phone && (
                      <p className="text-sm text-gray-600">{lead.phone}</p>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    {lead.status_name && (
                      <span
                        className="badge"
                        style={{ backgroundColor: `${lead.status_color}20`, color: lead.status_color }}
                      >
                        {lead.status_name}
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {lead.keyword_text}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500">
                    {lead.found_at &&
                      format(new Date(lead.found_at), 'dd/MM/yyyy', { locale: es })}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

// Tarjeta de lead
function LeadCard({ lead, statuses, onClick, onRefresh }) {
  const [isMoving, setIsMoving] = useState(false)

  const handleMove = async (tab) => {
    setIsMoving(true)
    try {
      await leadsAPI.move(lead.id, tab)
      toast.success('Lead movido')
      onRefresh()
    } catch (error) {
      toast.error('Error al mover')
    } finally {
      setIsMoving(false)
    }
  }

  const copyToClipboard = (text, label) => {
    navigator.clipboard.writeText(text)
    toast.success(`${label} copiado`)
  }

  return (
    <div className="lead-card" onClick={onClick}>
      <div className="p-4">
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1 min-w-0">
            <h3 className="font-medium text-gray-800 truncate">{lead.name}</h3>
            <a
              href={lead.url}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              className="text-sm text-primary-600 hover:underline flex items-center gap-1"
            >
              {lead.domain}
              <ExternalLink size={12} />
            </a>
          </div>
          {lead.notes_count > 0 && (
            <span className="flex items-center gap-1 text-gray-400">
              <MessageSquare size={16} />
              {lead.notes_count}
            </span>
          )}
        </div>

        {/* Contacto */}
        <div className="space-y-1 mb-3">
          {lead.email && (
            <button
              onClick={(e) => {
                e.stopPropagation()
                copyToClipboard(lead.email, 'Email')
              }}
              className="flex items-center gap-2 text-sm text-gray-600 hover:text-primary-600 w-full"
            >
              <Mail size={14} />
              <span className="truncate">{lead.email}</span>
            </button>
          )}
          {lead.phone && (
            <button
              onClick={(e) => {
                e.stopPropagation()
                copyToClipboard(lead.phone, 'Teléfono')
              }}
              className="flex items-center gap-2 text-sm text-gray-600 hover:text-primary-600 w-full"
            >
              <Phone size={14} />
              {lead.phone}
            </button>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between pt-3 border-t border-gray-100">
          <span className="text-xs text-gray-500">
            {lead.keyword_text}
          </span>
          <select
            onClick={(e) => e.stopPropagation()}
            onChange={(e) => handleMove(e.target.value)}
            disabled={isMoving}
            className="text-xs border border-gray-200 rounded px-2 py-1"
            defaultValue=""
          >
            <option value="" disabled>
              Mover a...
            </option>
            <option value="leads">Leads</option>
            <option value="doubts">Dudas</option>
            <option value="discarded">Descartados</option>
          </select>
        </div>
      </div>
    </div>
  )
}

// Modal de detalle de lead
function LeadDetailModal({ lead, statuses, isOpen, onClose, onUpdate }) {
  const [notes, setNotes] = useState([])
  const [newNote, setNewNote] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isExtracting, setIsExtracting] = useState(false)

  useEffect(() => {
    if (isOpen && lead) {
      loadNotes()
    }
  }, [isOpen, lead])

  const loadNotes = async () => {
    try {
      const response = await leadsAPI.getNotes(lead.id)
      setNotes(response.data)
    } catch (error) {
      console.error('Error loading notes:', error)
    }
  }

  const handleAddNote = async () => {
    if (!newNote.trim()) return

    setIsLoading(true)
    try {
      await leadsAPI.createNote(lead.id, newNote)
      setNewNote('')
      loadNotes()
      toast.success('Nota añadida')
    } catch (error) {
      toast.error('Error al añadir nota')
    } finally {
      setIsLoading(false)
    }
  }

  const handleExtractContact = async () => {
    setIsExtracting(true)
    try {
      const response = await leadsAPI.extractContact(lead.id)
      if (response.data.email || response.data.phone) {
        toast.success('Datos extraídos')
        onUpdate()
      } else {
        toast.error('No se encontraron datos de contacto')
      }
    } catch (error) {
      toast.error('Error al extraer datos')
    } finally {
      setIsExtracting(false)
    }
  }

  const handleStatusChange = async (statusId) => {
    try {
      await leadsAPI.update(lead.id, { status_id: statusId })
      toast.success('Estado actualizado')
      onUpdate()
    } catch (error) {
      toast.error('Error al actualizar')
    }
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={lead.name} size="lg">
      <div className="space-y-6">
        {/* Info básica */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="label">Dominio</label>
            <a
              href={lead.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary-600 hover:underline flex items-center gap-1"
            >
              {lead.domain}
              <ExternalLink size={14} />
            </a>
          </div>
          <div>
            <label className="label">Keyword</label>
            <p className="text-gray-800">{lead.keyword_text || '-'}</p>
          </div>
        </div>

        {/* Contacto */}
        <div className="p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-medium text-gray-800">Datos de contacto</h3>
            {!lead.contact_extracted && (
              <button
                onClick={handleExtractContact}
                disabled={isExtracting}
                className="btn-secondary text-sm"
              >
                {isExtracting ? (
                  <Loader size={16} className="animate-spin" />
                ) : (
                  <RefreshCw size={16} />
                )}
                Obtener datos
              </button>
            )}
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Email</label>
              <p className="text-gray-800">{lead.email || 'No disponible'}</p>
            </div>
            <div>
              <label className="label">Teléfono</label>
              <p className="text-gray-800">{lead.phone || 'No disponible'}</p>
            </div>
            <div>
              <label className="label">CIF/NIF</label>
              <p className="text-gray-800">{lead.cif || 'No disponible'}</p>
            </div>
          </div>
        </div>

        {/* Estado */}
        <div>
          <label className="label">Estado</label>
          <select
            value={lead.status_id || ''}
            onChange={(e) => handleStatusChange(e.target.value)}
            className="input"
          >
            <option value="">Sin estado</option>
            {statuses.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </select>
        </div>

        {/* Notas */}
        <div>
          <label className="label">Notas ({notes.length})</label>
          <div className="space-y-2 max-h-48 overflow-y-auto mb-3">
            {notes.map((note) => (
              <div key={note.id} className="p-3 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-800">{note.content}</p>
                <p className="text-xs text-gray-500 mt-1">
                  {format(new Date(note.created_at), 'dd/MM/yyyy HH:mm', { locale: es })}
                </p>
              </div>
            ))}
          </div>
          <div className="flex gap-2">
            <textarea
              value={newNote}
              onChange={(e) => setNewNote(e.target.value)}
              placeholder="Añadir nota..."
              className="input flex-1"
              rows={2}
            />
            <button
              onClick={handleAddNote}
              disabled={isLoading || !newNote.trim()}
              className="btn-primary"
            >
              {isLoading ? <Loader size={18} className="animate-spin" /> : 'Añadir'}
            </button>
          </div>
        </div>
      </div>
    </Modal>
  )
}

// Componente de pestaña de Análisis
function AnalysisTab({ suggestions, onAnalyze, countryId, onRefresh }) {
  const handleAddSuggestion = async (id) => {
    try {
      await suggestionsAPI.add(id)
      toast.success('Keyword añadida')
      onRefresh()
    } catch (error) {
      toast.error('Error al añadir')
    }
  }

  const handleIgnoreSuggestion = async (id) => {
    try {
      await suggestionsAPI.ignore(id)
      toast.success('Sugerencia ignorada')
      onRefresh()
    } catch (error) {
      toast.error('Error')
    }
  }

  return (
    <div className="space-y-6">
      <div className="card">
        <div className="card-header flex items-center justify-between">
          <h2 className="font-semibold text-gray-800">Análisis de Keywords</h2>
          <button onClick={onAnalyze} className="btn-primary">
            <RefreshCw size={18} />
            Analizar webs guardadas
          </button>
        </div>
        <div className="p-6">
          <p className="text-gray-600 mb-4">
            Analiza las webs de los leads guardados para descubrir nuevas palabras clave
            que podrían mejorar tus búsquedas.
          </p>
        </div>
      </div>

      {/* Sugerencias */}
      {suggestions.suggested_keywords && suggestions.suggested_keywords.length > 0 && (
        <div className="card">
          <div className="card-header">
            <h2 className="font-semibold text-gray-800">Keywords sugeridas</h2>
          </div>
          <div className="divide-y divide-gray-100">
            {suggestions.suggested_keywords
              .filter((s) => !s.is_added && !s.is_ignored)
              .map((suggestion, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-4 hover:bg-gray-50"
                >
                  <div>
                    <p className="font-medium text-gray-800">{suggestion.text}</p>
                    <p className="text-sm text-gray-500">
                      Frecuencia: {suggestion.frequency} · En {suggestion.websites_count} webs
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleAddSuggestion(suggestion.id)}
                      className="btn-icon text-green-600 hover:bg-green-50"
                      title="Añadir como keyword"
                    >
                      <Check size={18} />
                    </button>
                    <button
                      onClick={() => handleIgnoreSuggestion(suggestion.id)}
                      className="btn-icon text-red-600 hover:bg-red-50"
                      title="Ignorar"
                    >
                      <X size={18} />
                    </button>
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Ranking actual */}
      {suggestions.current_keywords && suggestions.current_keywords.length > 0 && (
        <div className="card">
          <div className="card-header">
            <h2 className="font-semibold text-gray-800">Rendimiento de Keywords actuales</h2>
          </div>
          <div className="divide-y divide-gray-100">
            {suggestions.current_keywords.map((kw, index) => (
              <div key={index} className="flex items-center justify-between p-4">
                <div>
                  <p className="font-medium text-gray-800">{kw.text}</p>
                  <p className="text-sm text-gray-500">
                    {kw.category} · {kw.total_searches} búsquedas
                  </p>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-primary-600">
                    {kw.total_results} resultados
                  </p>
                  <span
                    className={`badge ${kw.is_active ? 'badge-green' : 'badge-gray'}`}
                  >
                    {kw.is_active ? 'Activa' : 'Inactiva'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default CountryView
