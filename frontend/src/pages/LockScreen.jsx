/**
 * Pantalla de bloqueo con PIN.
 */
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Lock, Eye, EyeOff } from 'lucide-react'
import toast from 'react-hot-toast'
import { authAPI } from '../services/api'
import { useAuthStore } from '../services/store'

function LockScreen() {
  const [pin, setPin] = useState('')
  const [showPin, setShowPin] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const navigate = useNavigate()
  const { login } = useAuthStore()

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!pin.trim()) {
      toast.error('Introduce el PIN')
      return
    }

    setIsLoading(true)

    try {
      const response = await authAPI.verifyPin(pin)
      login(response.data.access_token)
      toast.success('Acceso concedido')
      navigate('/dashboard')
    } catch (error) {
      toast.error('PIN incorrecto')
      setPin('')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="lock-screen">
      <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md mx-4 animate-fadeIn">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-20 h-20 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Lock className="w-10 h-10 text-primary-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-800">Osmoleads</h1>
          <p className="text-gray-500 mt-1">Introduce el PIN para acceder</p>
        </div>

        {/* Formulario */}
        <form onSubmit={handleSubmit}>
          <div className="relative mb-6">
            <input
              type={showPin ? 'text' : 'password'}
              value={pin}
              onChange={(e) => setPin(e.target.value)}
              placeholder="PIN de acceso"
              className="input text-center text-lg tracking-widest pr-12"
              autoFocus
              disabled={isLoading}
            />
            <button
              type="button"
              onClick={() => setShowPin(!showPin)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              {showPin ? <EyeOff size={20} /> : <Eye size={20} />}
            </button>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="btn-primary w-full justify-center text-lg py-3"
          >
            {isLoading ? (
              <span className="flex items-center gap-2">
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                    fill="none"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                  />
                </svg>
                Verificando...
              </span>
            ) : (
              'Entrar'
            )}
          </button>
        </form>

        {/* Footer */}
        <p className="text-center text-gray-400 text-sm mt-6">
          Sistema de gestión de leads
        </p>
      </div>
    </div>
  )
}

export default LockScreen
