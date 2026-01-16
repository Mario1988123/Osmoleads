/**
 * Dashboard principal - Vista de países.
 */
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Plus,
  Search,
  Edit2,
  Trash2,
  Play,
  Users,
  FileText,
  Loader,
} from 'lucide-react'
import toast from 'react-hot-toast'
import Layout from '../components/Layout'
import Modal from '../components/Modal'
import { countriesAPI, searchAPI } from '../services/api'
import { useCountriesStore, useSearchStore } from '../services/store'

function Dashboard() {
  const navigate = useNavigate()
  const { countries, setCountries, isLoading, setLoading } = useCountriesStore()
  const { isSearching, setSearching } = useSearchStore()
  const [showModal, setShowModal] = useState(false)
  const [editingCountry, setEditingCountry] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    code: '',
    language: 'es',
  })

  // Cargar países al montar
  useEffect(() => {
    loadCountries()
  }, [])

  const loadCountries = async () => {
    setLoading(true)
    try {
      const response = await countriesAPI.list()
      setCountries(response.data)
    } catch (error) {
      toast.error('Error al cargar países')
    } finally {
      setLoading(false)
    }
  }

  const handleOpenModal = (country = null) => {
    if (country) {
      setEditingCountry(country)
      setFormData({
        name: country.name,
        code: country.code,
        language: country.language,
      })
    } else {
      setEditingCountry(null)
      setFormData({ name: '', code: '', language: 'es' })
    }
    setShowModal(true)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!formData.name.trim() || !formData.code.trim()) {
      toast.error('Completa todos los campos')
      return
    }

    try {
      if (editingCountry) {
        await countriesAPI.update(editingCountry.id, formData)
        toast.success('País actualizado')
      } else {
        await countriesAPI.create(formData)
        toast.success('País creado')
      }
      setShowModal(false)
      loadCountries()
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error al guardar')
    }
  }

  const handleDelete = async (country) => {
    if (!confirm(`¿Eliminar "${country.name}" y todos sus leads?`)) return

    try {
      await countriesAPI.delete(country.id)
      toast.success('País eliminado')
      loadCountries()
    } catch (error) {
      toast.error('Error al eliminar')
    }
  }

  const handleSearchAll = async () => {
    if (countries.length === 0) {
      toast.error('No hay países configurados')
      return
    }

    setSearching(true)
    try {
      const response = await searchAPI.searchAll()
      toast.success(`${response.data.new_leads} nuevos leads encontrados`)
      loadCountries()
    } catch (error) {
      toast.error('Error en la búsqueda')
    } finally {
      setSearching(false)
    }
  }

  return (
    <Layout title="Países">
      {/* Acciones */}
      <div className="flex flex-wrap gap-3 mb-6">
        <button onClick={() => handleOpenModal()} className="btn-primary">
          <Plus size={20} />
          Añadir País
        </button>
        <button
          onClick={handleSearchAll}
          disabled={isSearching || countries.length === 0}
          className="btn-secondary"
        >
          {isSearching ? (
            <Loader size={20} className="animate-spin" />
          ) : (
            <Search size={20} />
          )}
          Buscar en todos
        </button>
      </div>

      {/* Grid de países */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <div key={i} className="card p-6">
              <div className="skeleton h-8 w-32 mb-4" />
              <div className="skeleton h-4 w-24 mb-2" />
              <div className="skeleton h-4 w-20" />
            </div>
          ))}
        </div>
      ) : countries.length === 0 ? (
        <div className="empty-state">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
            <Globe size={32} className="text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-700 mb-2">
            No hay países configurados
          </h3>
          <p className="text-gray-500 mb-4">
            Añade un país para empezar a buscar leads
          </p>
          <button onClick={() => handleOpenModal()} className="btn-primary">
            <Plus size={20} />
            Añadir País
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {countries.map((country) => (
            <CountryCard
              key={country.id}
              country={country}
              onEdit={() => handleOpenModal(country)}
              onDelete={() => handleDelete(country)}
              onClick={() => navigate(`/country/${country.id}`)}
            />
          ))}
        </div>
      )}

      {/* Modal de crear/editar */}
      <Modal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        title={editingCountry ? 'Editar País' : 'Nuevo País'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="label">Nombre del país</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) =>
                setFormData({ ...formData, name: e.target.value })
              }
              placeholder="España"
              className="input"
              autoFocus
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Código</label>
              <input
                type="text"
                value={formData.code}
                onChange={(e) =>
                  setFormData({ ...formData, code: e.target.value.toUpperCase() })
                }
                placeholder="ES"
                maxLength={5}
                className="input"
              />
            </div>
            <div>
              <label className="label">Idioma</label>
              <select
                value={formData.language}
                onChange={(e) =>
                  setFormData({ ...formData, language: e.target.value })
                }
                className="input"
              >
                <option value="es">Español</option>
                <option value="fr">Francés</option>
                <option value="en">Inglés</option>
                <option value="pt">Portugués</option>
                <option value="it">Italiano</option>
                <option value="de">Alemán</option>
              </select>
            </div>
          </div>
          <div className="flex gap-3 pt-4">
            <button type="submit" className="btn-primary flex-1">
              {editingCountry ? 'Guardar' : 'Crear'}
            </button>
            <button
              type="button"
              onClick={() => setShowModal(false)}
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

// Componente de tarjeta de país
function CountryCard({ country, onEdit, onDelete, onClick }) {
  return (
    <div
      className="card hover:shadow-lg transition-shadow cursor-pointer"
      onClick={onClick}
    >
      <div className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            {country.flag_image ? (
              <img
                src={country.flag_image}
                alt={country.name}
                className="w-10 h-10 rounded-lg object-cover"
              />
            ) : (
              <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                <span className="text-primary-600 font-bold">
                  {country.code}
                </span>
              </div>
            )}
            <div>
              <h3 className="font-semibold text-gray-800">{country.name}</h3>
              <p className="text-sm text-gray-500">{country.code}</p>
            </div>
          </div>
          <div
            className="flex gap-1"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              onClick={onEdit}
              className="btn-icon text-gray-400 hover:text-primary-600"
            >
              <Edit2 size={18} />
            </button>
            <button
              onClick={onDelete}
              className="btn-icon text-gray-400 hover:text-red-500"
            >
              <Trash2 size={18} />
            </button>
          </div>
        </div>

        <div className="flex items-center gap-4 text-sm text-gray-600">
          <span className="flex items-center gap-1">
            <FileText size={16} />
            {country.keywords_count || 0} keywords
          </span>
          <span className="flex items-center gap-1">
            <Users size={16} />
            {country.leads_count || 0} leads
          </span>
        </div>
      </div>
    </div>
  )
}

// Importar el componente Globe que faltaba
import { Globe } from 'lucide-react'

export default Dashboard
