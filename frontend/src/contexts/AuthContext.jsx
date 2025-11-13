import { createContext, useContext, useState, useEffect } from 'react'
import { authAPI } from '../services/api'

const AuthContext = createContext(null)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth debe usarse dentro de AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Verificar si hay un usuario autenticado al cargar
    verificarAutenticacion()
  }, [])

  const verificarAutenticacion = async () => {
    try {
      const response = await authAPI.getCurrentUser()
      if (response.data.success) {
        setUser(response.data.data)
      } else {
        setUser(null)
      }
    } catch (error) {
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  const login = async (username, password) => {
    try {
      const response = await authAPI.login(username, password)
      if (response.data.success) {
        setUser(response.data.data.user)
        return { success: true, user: response.data.data.user }
      } else {
        return { success: false, error: response.data.error }
      }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Error al iniciar sesión'
      }
    }
  }

  const logout = async () => {
    try {
      await authAPI.logout()
    } catch (error) {
      console.error('Error al cerrar sesión:', error)
    } finally {
      setUser(null)
    }
  }

  const hasRole = (roles) => {
    if (!user) return false
    if (Array.isArray(roles)) {
      return roles.includes(user.rol)
    }
    return user.rol === roles
  }

  const canAccess = (route) => {
    if (!user) return false
    
    // Admin tiene acceso a todo
    if (user.rol === 'admin') return true
    
    // Definir permisos por rol
    const permisos = {
      secretaria: ['tablero', 'cobranza', 'clientes', 'productos'],
      taller: ['tablero', 'taller', 'productos']
    }
    
    return permisos[user.rol]?.includes(route) || false
  }

  const canSeePrices = () => {
    if (!user) return false
    return user.rol !== 'taller'
  }

  const value = {
    user,
    loading,
    login,
    logout,
    hasRole,
    canAccess,
    canSeePrices,
    verificarAutenticacion
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

