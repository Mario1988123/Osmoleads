/**
 * Página de configuración.
 */
import { useState, useEffect } from 'react'
import { Plus, Trash2, Save, Loader } from 'lucide-react'
import toast from 'react-hot-toast'
import Layout from '../components/Layout'
import Modal from '../components/Modal'
import { settingsAPI, statusesAPI } from '../services/api'

function Settings() {
  const [settings, setSettings] = useState({
    max_searches: 100,
    searches_today: 0,
  })
  const [statuses, setStatuses] = useState([])
  const [marketplaces, setMarketplaces] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)

  // Modales
  const [showStatusModal, setShowStatusModal] = useState(false)
  const [showMarketplaceModal, setShowMarketplaceModal] = useState(false)
  const [newStatus, setNewStatus] = useState({ name: '', color: '#3B82F6', icon: '' })
  const [newMarketplace, setNewMarketplace] = useState({ domain: '', name: '' })

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setIsLoading(true)
    try {
      const [settingsRes, statusesRes, marketplacesRes] = await Promise.all([
        settingsAPI.get(),
        statusesAPI.list(),
        settingsAPI.listMarketplaces(),
      ])
      setSettings(settingsRes.data)
      setStatuses(statusesRes.data)
      setMarketplaces(marketplacesRes.data)
    } catch (error) {
      toast.error('Error al cargar configuración')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSaveSettings = async () => {
    setIsSaving(true)
    try {
      await settingsAPI.update({ max_searches: settings.max_searches })
      toast.success('Configuración guardada')
    } catch (error) {
      toast.error('Error al guardar')
    } finally {
      setIsSaving(false)
    }
  }

  const handleCreateStatus = async (e) => {
    e.preventDefault()
    if (!newStatus.name.trim()) {
      toast.error('Escribe un nombre')
      return
    }

    try {
      await statusesAPI.create(newStatus)
      toast.success('Estado creado')
      setShowStatusModal(false)
      setNewStatus({ name: '', color: '#3B82F6', icon: '' })
      loadData()
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error al crear')
    }
  }

  const handleDeleteStatus = async (id) => {
    if (!confirm('¿Eliminar este estado?')) return

    try {
      await statusesAPI.delete(id)
      toast.success('Estado eliminado')
      loadData()
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error al eliminar')
    }
  }

  const handleCreateMarketplace = async (e) => {
    e.preventDefault()
    if (!newMarketplace.domain.trim()) {
      toast.error('Escribe un dominio')
      return
    }

    try {
      await settingsAPI.addMarketplace(newMarketplace)
      toast.success('Marketplace añadido')
      setShowMarketplaceModal(false)
      setNewMarketplace({ domain: '', name: '' })
      loadData()
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error al añadir')
    }
  }

  const handleDeleteMarketplace = async (id) => {
    if (!confirm('¿Eliminar este marketplace?')) return

    try {
      await settingsAPI.deleteMarketplace(id)
      toast.success('Marketplace eliminado')
      loadData()
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error al eliminar')
    }
  }

  if (isLoading) {
    return (
      <Layout title="Configuración">
        <div className="flex items-center justify-center h-64">
          <Loader className="animate-spin text-primary-600" size={32} />
        </div>
      </Layout>
    )
  }

  return (
    <Layout title="Configuración">
      <div className="space-y-6">
        {/* Límite de búsquedas */}
        <div className="card">
          <div className="card-header">
            <h2 className="font-semibold text-gray-800">Límite de búsquedas</h2>
          </div>
          <div className="card-body">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="label">Máximo de búsquedas diarias</label>
                <div className="flex gap-3">
                  <input
                    type="number"
                    min="0"
                    value={settings.max_searches}
                    onChange={(e) =>
                      setSettings({ ...settings, max_searches: parseInt(e.target.value) || 0 })
                    }
                    className="input"
                    placeholder="0 = ilimitado"
                  />
                  <button
                    onClick={handleSaveSettings}
                    disabled={isSaving}
                    className="btn-primary"
                  >
                    {isSaving ? <Loader size={18} className="animate-spin" /> : <Save size={18} />}
                    Guardar
                  </button>
                </div>
                <p className="text-sm text-gray-500 mt-2">
                  0 = ilimitado (pagarás el exceso del límite gratuito de Google)
                </p>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600">
                  <strong>Hoy:</strong> {settings.searches_today} búsquedas realizadas
                </p>
                <p className="text-sm text-gray-600">
                  <strong>Límite gratuito Google:</strong> 100 búsquedas/día
                </p>
                <p className="text-sm text-gray-600">
                  <strong>Coste adicional:</strong> $5 por cada 1000 búsquedas
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Estados de leads */}
        <div className="card">
          <div className="card-header flex items-center justify-between">
            <h2 className="font-semibold text-gray-800">Estados de leads</h2>
            <button onClick={() => setShowStatusModal(true)} className="btn-primary">
              <Plus size={18} />
              Nuevo estado
            </button>
          </div>
          <div className="divide-y divide-gray-100">
            {statuses.map((status) => (
              <div
                key={status.id}
                className="flex items-center justify-between p-4 hover:bg-gray-50"
              >
                <div className="flex items-center gap-3">
                  <div
                    className="w-4 h-4 rounded-full"
                    style={{ backgroundColor: status.color }}
                  />
                  <span className="font-medium text-gray-800">{status.name}</span>
                  {status.is_system && (
                    <span className="badge badge-gray">Sistema</span>
                  )}
                </div>
                {!status.is_system && (
                  <button
                    onClick={() => handleDeleteStatus(status.id)}
                    className="btn-icon text-gray-400 hover:text-red-500"
                  >
                    <Trash2 size={18} />
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Marketplaces */}
        <div className="card">
          <div className="card-header flex items-center justify-between">
            <div>
              <h2 className="font-semibold text-gray-800">Marketplaces</h2>
              <p className="text-sm text-gray-500">
                Los resultados de estos dominios se clasifican automáticamente como marketplaces
              </p>
            </div>
            <button onClick={() => setShowMarketplaceModal(true)} className="btn-primary">
              <Plus size={18} />
              Añadir
            </button>
          </div>
          <div className="p-4">
            <div className="flex flex-wrap gap-2">
              {marketplaces.map((mp) => (
                <span
                  key={mp.id}
                  className="inline-flex items-center gap-2 px-3 py-1.5 bg-gray-100 rounded-full text-sm"
                >
                  {mp.domain}
                  {!mp.is_system && (
                    <button
                      onClick={() => handleDeleteMarketplace(mp.id)}
                      className="text-gray-400 hover:text-red-500"
                    >
                      <Trash2 size={14} />
                    </button>
                  )}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Modal nuevo estado */}
      <Modal
        isOpen={showStatusModal}
        onClose={() => setShowStatusModal(false)}
        title="Nuevo Estado"
      >
        <form onSubmit={handleCreateStatus} className="space-y-4">
          <div>
            <label className="label">Nombre</label>
            <input
              type="text"
              value={newStatus.name}
              onChange={(e) => setNewStatus({ ...newStatus, name: e.target.value })}
              placeholder="Mi estado"
              className="input"
              autoFocus
            />
          </div>
          <div>
            <label className="label">Color</label>
            <div className="flex gap-3 items-center">
              <input
                type="color"
                value={newStatus.color}
                onChange={(e) => setNewStatus({ ...newStatus, color: e.target.value })}
                className="w-12 h-10 rounded cursor-pointer"
              />
              <input
                type="text"
                value={newStatus.color}
                onChange={(e) => setNewStatus({ ...newStatus, color: e.target.value })}
                className="input flex-1"
              />
            </div>
          </div>
          <div className="flex gap-3 pt-4">
            <button type="submit" className="btn-primary flex-1">
              Crear
            </button>
            <button
              type="button"
              onClick={() => setShowStatusModal(false)}
              className="btn-secondary"
            >
              Cancelar
            </button>
          </div>
        </form>
      </Modal>

      {/* Modal nuevo marketplace */}
      <Modal
        isOpen={showMarketplaceModal}
        onClose={() => setShowMarketplaceModal(false)}
        title="Añadir Marketplace"
      >
        <form onSubmit={handleCreateMarketplace} className="space-y-4">
          <div>
            <label className="label">Dominio</label>
            <input
              type="text"
              value={newMarketplace.domain}
              onChange={(e) =>
                setNewMarketplace({ ...newMarketplace, domain: e.target.value })
              }
              placeholder="ejemplo.com"
              className="input"
              autoFocus
            />
          </div>
          <div>
            <label className="label">Nombre (opcional)</label>
            <input
              type="text"
              value={newMarketplace.name}
              onChange={(e) =>
                setNewMarketplace({ ...newMarketplace, name: e.target.value })
              }
              placeholder="Nombre del marketplace"
              className="input"
            />
          </div>
          <div className="flex gap-3 pt-4">
            <button type="submit" className="btn-primary flex-1">
              Añadir
            </button>
            <button
              type="button"
              onClick={() => setShowMarketplaceModal(false)}
              className="btn-secondary"
            >
              Cancelar
            </button>
          </div>
        </form>
      </Modal>
    </Layout>
  )
}

export default Settings
