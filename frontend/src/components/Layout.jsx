/**
 * Layout principal de la aplicación.
 */
import { useState, useEffect } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import {
  Globe,
  Settings,
  Image,
  LogOut,
  Menu,
  X,
  Search,
  ChevronRight,
} from 'lucide-react'
import { useAuthStore, useSearchStore } from '../services/store'
import { searchAPI } from '../services/api'
import toast from 'react-hot-toast'

function Layout({ children, title, breadcrumbs = [] }) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const location = useLocation()
  const navigate = useNavigate()
  const { logout } = useAuthStore()
  const { searchStats, setSearchStats } = useSearchStore()

  // Cargar estadísticas de búsqueda
  useEffect(() => {
    loadSearchStats()
  }, [])

  const loadSearchStats = async () => {
    try {
      const response = await searchAPI.getStats()
      setSearchStats(response.data)
    } catch (error) {
      console.error('Error loading search stats:', error)
    }
  }

  const handleLogout = () => {
    logout()
    toast.success('Sesión cerrada')
    navigate('/')
  }

  const navItems = [
    { path: '/dashboard', label: 'Países', icon: Globe },
    { path: '/image-search', label: 'Buscar imagen', icon: Image },
    { path: '/settings', label: 'Configuración', icon: Settings },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo y navegación */}
            <div className="flex items-center gap-8">
              <Link to="/dashboard" className="flex items-center gap-2">
                <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">O</span>
                </div>
                <span className="font-bold text-xl text-gray-800 hidden sm:block">
                  Osmoleads
                </span>
              </Link>

              {/* Navegación desktop */}
              <nav className="hidden md:flex items-center gap-1">
                {navItems.map((item) => {
                  const Icon = item.icon
                  const isActive = location.pathname === item.path
                  return (
                    <Link
                      key={item.path}
                      to={item.path}
                      className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                        isActive
                          ? 'bg-primary-50 text-primary-600'
                          : 'text-gray-600 hover:bg-gray-100'
                      }`}
                    >
                      <Icon size={18} />
                      {item.label}
                    </Link>
                  )
                })}
              </nav>
            </div>

            {/* Derecha: stats y acciones */}
            <div className="flex items-center gap-4">
              {/* Contador de búsquedas */}
              <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-gray-100 rounded-lg text-sm">
                <Search size={16} className="text-gray-500" />
                <span className="text-gray-600">
                  {searchStats.searches_today}/{searchStats.max_searches === 0 ? '∞' : searchStats.max_searches}
                </span>
              </div>

              {/* Botón logout */}
              <button
                onClick={handleLogout}
                className="btn-icon text-gray-500 hover:text-red-500"
                title="Cerrar sesión"
              >
                <LogOut size={20} />
              </button>

              {/* Menú móvil */}
              <button
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                className="md:hidden btn-icon"
              >
                {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
              </button>
            </div>
          </div>
        </div>

        {/* Menú móvil */}
        {isMobileMenuOpen && (
          <div className="md:hidden border-t border-gray-200 bg-white">
            <nav className="px-4 py-2">
              {navItems.map((item) => {
                const Icon = item.icon
                const isActive = location.pathname === item.path
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    onClick={() => setIsMobileMenuOpen(false)}
                    className={`flex items-center gap-3 px-3 py-3 rounded-lg text-sm font-medium ${
                      isActive
                        ? 'bg-primary-50 text-primary-600'
                        : 'text-gray-600'
                    }`}
                  >
                    <Icon size={20} />
                    {item.label}
                  </Link>
                )
              })}
            </nav>
          </div>
        )}
      </header>

      {/* Breadcrumbs */}
      {breadcrumbs.length > 0 && (
        <div className="bg-white border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
            <nav className="flex items-center gap-2 text-sm">
              <Link to="/dashboard" className="text-gray-500 hover:text-gray-700">
                Inicio
              </Link>
              {breadcrumbs.map((crumb, index) => (
                <span key={index} className="flex items-center gap-2">
                  <ChevronRight size={16} className="text-gray-400" />
                  {crumb.path ? (
                    <Link
                      to={crumb.path}
                      className="text-gray-500 hover:text-gray-700"
                    >
                      {crumb.label}
                    </Link>
                  ) : (
                    <span className="text-gray-800 font-medium">{crumb.label}</span>
                  )}
                </span>
              ))}
            </nav>
          </div>
        </div>
      )}

      {/* Título de página */}
      {title && (
        <div className="bg-white border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <h1 className="text-2xl font-bold text-gray-800">{title}</h1>
          </div>
        </div>
      )}

      {/* Contenido principal */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {children}
      </main>
    </div>
  )
}

export default Layout
