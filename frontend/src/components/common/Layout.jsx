import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom'
import { useState, useMemo } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { 
  LayoutDashboard, 
  Package, 
  ShoppingBag, 
  Flower2, 
  MapPin, 
  Users, 
  DollarSign, 
  Wrench, 
  Calendar,
  ChevronLeft,
  Menu,
  X,
  BarChart3,
  LogOut,
  User as UserIcon,
  History
} from 'lucide-react'

function Layout() {
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout, canAccess } = useAuth()
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  
  const allNavigation = [
    { name: 'Tablero', path: '/tablero', icon: LayoutDashboard, color: 'text-blue-600', roles: ['admin', 'secretaria', 'taller'] },
    { name: 'Pedidos', path: '/pedidos', icon: ShoppingBag, color: 'text-green-600', roles: ['admin'] },
    { name: 'Taller', path: '/taller', icon: Wrench, color: 'text-orange-600', roles: ['admin', 'taller'] },
    { name: 'Eventos', path: '/eventos', icon: Calendar, color: 'text-purple-600', roles: ['admin'] },
    { name: 'Clientes', path: '/clientes', icon: Users, color: 'text-indigo-600', roles: ['admin', 'secretaria'] },
    { name: 'Cobranza', path: '/cobranza', icon: DollarSign, color: 'text-emerald-600', roles: ['admin', 'secretaria'] },
    { name: 'Rutas', path: '/rutas', icon: MapPin, color: 'text-red-600', roles: ['admin'] },
    { name: 'Inventario', path: '/inventario', icon: Package, color: 'text-amber-600', roles: ['admin'] },
    { name: 'Productos', path: '/productos', icon: Flower2, color: 'text-pink-600', roles: ['admin', 'secretaria', 'taller'] },
    { name: 'Reportes', path: '/reportes', icon: BarChart3, color: 'text-violet-600', roles: ['admin'] },
    { name: 'Movimientos', path: '/auditoria', icon: History, color: 'text-cyan-600', roles: ['admin'] },
  ]
  
  // Filtrar navegación según el rol del usuario
  const navigation = useMemo(() => {
    if (!user) return []
    return allNavigation.filter(item => item.roles.includes(user.rol))
  }, [user])
  
  const isActive = (path) => location.pathname === path

  const handleLogout = async () => {
    await logout()
    navigate('/login', { replace: true })
  }

  const getRolLabel = (rol) => {
    const labels = {
      admin: 'Administrador',
      secretaria: 'Secretaria',
      taller: 'Taller'
    }
    return labels[rol] || rol
  }
  
  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Backdrop para móvil/tablet */}
      {mobileMenuOpen && (
        <div 
          className="md:hidden fixed inset-0 bg-black bg-opacity-50 z-40"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}
      
      {/* Sidebar Desktop */}
      <aside className={`hidden md:flex md:flex-col fixed left-0 top-0 bottom-0 bg-white border-r border-gray-200 z-30 transition-all duration-300 ${sidebarOpen ? 'w-64' : 'w-20'}`}>
        {/* Logo Header */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-gray-200">
          {sidebarOpen ? (
            <>
              <div className="flex items-center">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-pink-500 to-rose-500 flex items-center justify-center">
                  <Flower2 className="h-6 w-6 text-white" />
                </div>
                <span className="ml-3 text-lg font-bold text-gray-900">Las Lira</span>
              </div>
              <button
                onClick={() => setSidebarOpen(false)}
                className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors"
                title="Ocultar menú"
              >
                <ChevronLeft className="h-5 w-5 text-gray-600" />
              </button>
            </>
          ) : (
            <button
              onClick={() => setSidebarOpen(true)}
              className="w-full flex justify-center"
              title="Mostrar menú"
            >
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-pink-500 to-rose-500 flex items-center justify-center">
                <Flower2 className="h-6 w-6 text-white" />
              </div>
            </button>
          )}
        </div>
        
        {/* Navigation */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {navigation.map((item) => {
            const Icon = item.icon
            const active = isActive(item.path)
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`
                  flex items-center h-11 rounded-lg transition-all duration-200
                  ${sidebarOpen ? 'px-3' : 'px-0 justify-center'}
                  ${active 
                    ? 'bg-gradient-to-r from-pink-50 to-rose-50 text-pink-700 shadow-sm' 
                    : 'text-gray-700 hover:bg-gray-50'
                  }
                `}
                title={!sidebarOpen ? item.name : ''}
              >
                <Icon className={`
                  h-5 w-5 flex-shrink-0
                  ${active ? item.color : 'text-gray-400'}
                `} />
                {sidebarOpen && (
                  <span className="ml-3 text-sm font-medium">{item.name}</span>
                )}
              </Link>
            )
          })}
        </nav>
        
        {/* User Info & Logout */}
        <div className="border-t border-gray-200 p-4 bg-gray-50">
          {sidebarOpen && user && (
            <div className="mb-3 px-2 py-2 bg-white rounded-lg">
              <div className="flex items-center gap-2 mb-1">
                <UserIcon className="h-4 w-4 text-gray-500" />
                <span className="text-xs font-medium text-gray-900 truncate">{user.nombre}</span>
              </div>
              <span className="text-xs text-gray-500">{getRolLabel(user.rol)}</span>
            </div>
          )}
          <button
            onClick={handleLogout}
            className={`w-full flex items-center gap-2 px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors ${!sidebarOpen ? 'justify-center' : ''}`}
            title={!sidebarOpen ? 'Cerrar Sesión' : ''}
          >
            <LogOut className="h-4 w-4" />
            {sidebarOpen && <span>Cerrar Sesión</span>}
          </button>
        </div>
      </aside>
      
      {/* Mobile/Tablet Header */}
      <div className="md:hidden fixed top-0 left-0 right-0 h-16 bg-white border-b border-gray-200 flex items-center justify-between px-4 z-50 shadow-sm">
        <div className="flex items-center">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-pink-500 to-rose-500 flex items-center justify-center">
            <Flower2 className="h-6 w-6 text-white" />
          </div>
          <span className="ml-3 text-lg font-bold text-gray-900">Las Lira</span>
        </div>
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
          aria-label="Toggle menu"
        >
          {mobileMenuOpen ? (
            <X className="h-6 w-6 text-gray-600" />
          ) : (
            <Menu className="h-6 w-6 text-gray-600" />
          )}
        </button>
      </div>
      
      {/* Mobile/Tablet Sidebar - Overlay */}
      <aside 
        className={`
          md:hidden fixed top-0 left-0 bottom-0 w-72 max-w-[85vw]
          bg-white shadow-2xl overflow-y-auto z-50
          transition-transform duration-300 ease-in-out
          ${mobileMenuOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        {/* Mobile Header */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-gray-200 bg-gradient-to-r from-pink-50 to-rose-50">
          <div className="flex items-center">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-pink-500 to-rose-500 flex items-center justify-center">
              <Flower2 className="h-6 w-6 text-white" />
            </div>
            <span className="ml-3 text-lg font-bold text-gray-900">Las Lira</span>
          </div>
          <button
            onClick={() => setMobileMenuOpen(false)}
            className="p-2 rounded-lg hover:bg-white/50 transition-colors"
            aria-label="Cerrar menú"
          >
            <X className="h-6 w-6 text-gray-600" />
          </button>
        </div>
        
        {/* Mobile Navigation */}
        <nav className="px-3 py-4 space-y-1 pb-24">
          {navigation.map((item) => {
            const Icon = item.icon
            const active = isActive(item.path)
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setMobileMenuOpen(false)}
                className={`
                  flex items-center h-12 px-3 rounded-lg transition-all duration-200
                  ${active 
                    ? 'bg-gradient-to-r from-pink-50 to-rose-50 text-pink-700 shadow-sm' 
                    : 'text-gray-700 hover:bg-gray-50'
                  }
                `}
              >
                <Icon className={`h-5 w-5 flex-shrink-0 ${active ? item.color : 'text-gray-400'}`} />
                <span className="ml-3 text-sm font-medium">{item.name}</span>
              </Link>
            )
          })}
        </nav>
        
        {/* Mobile User Info & Logout - Fixed at bottom */}
        {user && (
          <div className="fixed bottom-0 left-0 right-0 w-72 max-w-[85vw] border-t border-gray-200 bg-white p-4 shadow-lg">
            <div className="mb-3 px-3 py-2 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-2 mb-1">
                <UserIcon className="h-4 w-4 text-gray-500" />
                <span className="text-xs font-medium text-gray-900 truncate">{user.nombre}</span>
              </div>
              <span className="text-xs text-gray-500">{getRolLabel(user.rol)}</span>
            </div>
            <button
              onClick={() => {
                handleLogout()
                setMobileMenuOpen(false)
              }}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 text-sm font-medium text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            >
              <LogOut className="h-5 w-5" />
              <span>Cerrar Sesión</span>
            </button>
          </div>
        )}
      </aside>
      
      {/* Main Content */}
      <div className={`flex-1 min-h-screen transition-all duration-300 ${sidebarOpen ? 'md:ml-64' : 'md:ml-20'}`}>
        <main className="p-4 md:p-6 lg:p-8 pt-20 md:pt-6">
          <div className="max-w-7xl mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}

export default Layout

