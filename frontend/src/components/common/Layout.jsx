import { Outlet, Link, useLocation } from 'react-router-dom'
import { useState } from 'react'
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
  BarChart3
} from 'lucide-react'

function Layout() {
  const location = useLocation()
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  
  const navigation = [
    { name: 'Tablero', path: '/tablero', icon: LayoutDashboard, color: 'text-blue-600' },
    { name: 'Pedidos', path: '/pedidos', icon: ShoppingBag, color: 'text-green-600' },
    { name: 'Taller', path: '/taller', icon: Wrench, color: 'text-orange-600' },
    { name: 'Eventos', path: '/eventos', icon: Calendar, color: 'text-purple-600' },
    { name: 'Clientes', path: '/clientes', icon: Users, color: 'text-indigo-600' },
    { name: 'Cobranza', path: '/cobranza', icon: DollarSign, color: 'text-emerald-600' },
    { name: 'Rutas', path: '/rutas', icon: MapPin, color: 'text-red-600' },
    { name: 'Inventario', path: '/inventario', icon: Package, color: 'text-amber-600' },
    { name: 'Productos', path: '/productos', icon: Flower2, color: 'text-pink-600' },
    { name: 'Reportes', path: '/reportes', icon: BarChart3, color: 'text-violet-600' },
  ]
  
  const isActive = (path) => location.pathname === path
  
  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar Desktop */}
      <aside className={`
        hidden md:flex md:flex-col
        bg-white border-r border-gray-200
        transition-all duration-300 ease-in-out
        ${sidebarOpen ? 'w-64' : 'w-20'}
      `}>
        {/* Logo */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-gray-200">
          {sidebarOpen && (
            <div className="flex items-center">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-pink-500 to-rose-500 flex items-center justify-center">
                <Flower2 className="h-6 w-6 text-white" />
              </div>
              <span className="ml-3 text-lg font-bold text-gray-900">Las Lira</span>
            </div>
          )}
          {!sidebarOpen && (
            <button
              onClick={() => setSidebarOpen(true)}
              className="w-10 h-10 rounded-xl bg-gradient-to-br from-pink-500 to-rose-500 flex items-center justify-center mx-auto hover:from-pink-600 hover:to-rose-600 transition-all duration-200"
              title="Expandir menú"
            >
              <Flower2 className="h-6 w-6 text-white" />
            </button>
          )}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className={`
              p-1.5 rounded-lg hover:bg-gray-100 transition-colors
              ${!sidebarOpen && 'hidden'}
            `}
          >
            <ChevronLeft className={`h-5 w-5 text-gray-600 transition-transform ${!sidebarOpen && 'rotate-180'}`} />
          </button>
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
        
        {/* Collapse Button (when closed) */}
        {!sidebarOpen && (
          <div className="p-3 border-t border-gray-200">
            <button
              onClick={() => setSidebarOpen(true)}
              className="w-full p-2 rounded-lg hover:bg-gray-100 transition-colors flex justify-center"
              title="Expandir menú"
            >
              <Menu className="h-5 w-5 text-gray-600" />
            </button>
          </div>
        )}
      </aside>
      
      {/* Mobile Menu Button */}
      <div className="md:hidden fixed top-0 left-0 right-0 h-16 bg-white border-b border-gray-200 flex items-center justify-between px-4 z-40">
        <div className="flex items-center">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-pink-500 to-rose-500 flex items-center justify-center">
            <Flower2 className="h-6 w-6 text-white" />
          </div>
          <span className="ml-3 text-lg font-bold text-gray-900">Las Lira</span>
        </div>
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="p-2 rounded-lg hover:bg-gray-100"
        >
          {mobileMenuOpen ? (
            <X className="h-6 w-6 text-gray-600" />
          ) : (
            <Menu className="h-6 w-6 text-gray-600" />
          )}
        </button>
      </div>
      
      {/* Mobile Sidebar */}
      {mobileMenuOpen && (
        <div className="md:hidden fixed inset-0 z-30 bg-black bg-opacity-50" onClick={() => setMobileMenuOpen(false)}>
          <aside 
            className="fixed top-16 left-0 bottom-0 w-64 bg-white shadow-xl overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <nav className="px-3 py-4 space-y-1">
              {navigation.map((item) => {
                const Icon = item.icon
                const active = isActive(item.path)
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`
                      flex items-center h-11 px-3 rounded-lg transition-all duration-200
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
          </aside>
        </div>
      )}
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col min-h-screen">
        <main className="flex-1 p-4 md:p-6 lg:p-8 mt-16 md:mt-0">
          <div className="max-w-7xl mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}

export default Layout

