import { Navigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'

function ProtectedRoute({ children, requiredRole = null }) {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-pink-600"></div>
          <p className="mt-4 text-gray-600">Cargando...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  if (requiredRole && user.rol !== requiredRole) {
    return <Navigate to="/tablero" replace />
  }

  return children
}

export default ProtectedRoute

