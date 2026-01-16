/**
 * Componente principal de la aplicación.
 */
import { useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './services/store'

// Páginas
import LockScreen from './pages/LockScreen'
import Dashboard from './pages/Dashboard'
import CountryView from './pages/CountryView'
import Settings from './pages/Settings'
import ImageSearch from './pages/ImageSearch'

// Componente de ruta protegida
function ProtectedRoute({ children }) {
  const { isAuthenticated, checkAuth } = useAuthStore()

  useEffect(() => {
    checkAuth()
  }, [])

  if (!isAuthenticated) {
    return <Navigate to="/" replace />
  }

  return children
}

function App() {
  const { isAuthenticated, checkAuth } = useAuthStore()

  useEffect(() => {
    checkAuth()
  }, [])

  return (
    <Routes>
      {/* Pantalla de bloqueo */}
      <Route
        path="/"
        element={
          isAuthenticated ? <Navigate to="/dashboard" replace /> : <LockScreen />
        }
      />

      {/* Dashboard principal (países) */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />

      {/* Vista de país (leads, keywords) */}
      <Route
        path="/country/:id"
        element={
          <ProtectedRoute>
            <CountryView />
          </ProtectedRoute>
        }
      />

      {/* Configuración */}
      <Route
        path="/settings"
        element={
          <ProtectedRoute>
            <Settings />
          </ProtectedRoute>
        }
      />

      {/* Búsqueda por imagen */}
      <Route
        path="/image-search"
        element={
          <ProtectedRoute>
            <ImageSearch />
          </ProtectedRoute>
        }
      />

      {/* Ruta por defecto */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
