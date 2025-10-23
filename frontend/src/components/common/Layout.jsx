import { Outlet, Link, useLocation } from 'react-router-dom'
import { LayoutDashboard, Package, ShoppingBag, Flower2, MapPin, Users, DollarSign, Wrench } from 'lucide-react'

function Layout() {
  const location = useLocation()
  
  const navigation = [
    { name: 'Tablero', path: '/tablero', icon: LayoutDashboard },
    { name: 'Pedidos', path: '/pedidos', icon: ShoppingBag },
    { name: 'Taller', path: '/taller', icon: Wrench },
    { name: 'Clientes', path: '/clientes', icon: Users },
    { name: 'Cobranza', path: '/cobranza', icon: DollarSign },
    { name: 'Rutas', path: '/rutas', icon: MapPin },
    { name: 'Inventario', path: '/inventario', icon: Package },
    { name: 'Productos', path: '/productos', icon: Flower2 },
  ]
  
  const isActive = (path) => location.pathname === path
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navbar */}
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              {/* Logo */}
              <div className="flex-shrink-0 flex items-center">
                <Flower2 className="h-8 w-8 text-primary-600" />
                <span className="ml-2 text-xl font-bold text-gray-900">Las-Lira</span>
              </div>
              
              {/* Navigation Links */}
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                {navigation.map((item) => {
                  const Icon = item.icon
                  return (
                    <Link
                      key={item.path}
                      to={item.path}
                      className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
                        isActive(item.path)
                          ? 'border-primary-500 text-gray-900'
                          : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                      }`}
                    >
                      <Icon className="h-4 w-4 mr-2" />
                      {item.name}
                    </Link>
                  )
                })}
              </div>
            </div>
            
            {/* User Menu */}
            <div className="flex items-center">
              <span className="text-sm text-gray-700">Admin</span>
            </div>
          </div>
        </div>
      </nav>
      
      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <Outlet />
      </main>
    </div>
  )
}

export default Layout

