import { useState, useEffect } from 'react'
import { User, Search, Plus, Edit2, Trash2, X, Phone, Mail, MapPin, DollarSign, ShoppingBag, Download, Calendar, Package, Tag } from 'lucide-react'
import axios from 'axios'
import { API_URL } from '../services/api'
import EtiquetaCliente from '../components/EtiquetaCliente'
import { formatFecha } from '../utils/helpers'
import { eventBus, EVENT_TYPES } from '../utils/eventBus'

function ClientesPage() {
  const [clientes, setClientes] = useState([])
  const [loading, setLoading] = useState(true)
  const [busqueda, setBusqueda] = useState('')
  const [tipoFiltro, setTipoFiltro] = useState('')
  const [mostrarModal, setMostrarModal] = useState(false)
  const [clienteSeleccionado, setClienteSeleccionado] = useState(null)
  const [modoEdicion, setModoEdicion] = useState(false)
  
  // Estados para etiquetas
  const [etiquetasDisponibles, setEtiquetasDisponibles] = useState({})
  const [etiquetasFiltro, setEtiquetasFiltro] = useState([])
  const [categoriaEtiquetaVisible, setCategoriaEtiquetaVisible] = useState(null)
  
  // Estados para paginación
  const [paginaActual, setPaginaActual] = useState(1)
  const [totalPaginas, setTotalPaginas] = useState(1)
  const [totalClientes, setTotalClientes] = useState(0)
  const [limitePorPagina] = useState(100)
  
  // Estados para estadísticas globales
  const [statsGlobales, setStatsGlobales] = useState({
    total: 0,
    vip: 0,
    fiel: 0,
    nuevo: 0,
    ocasional: 0,
    promedio_vip: 0,
    promedio_fiel: 0,
    promedio_nuevo: 0,
    promedio_ocasional: 0,
    promedio_pedidos_vip: 0,
    promedio_pedidos_fiel: 0,
    promedio_pedidos_nuevo: 0,
    promedio_pedidos_ocasional: 0
  })
  
  // Estados para modal de detalles
  const [mostrarDetalles, setMostrarDetalles] = useState(false)
  const [clienteDetalle, setClienteDetalle] = useState(null)
  const [historialPedidos, setHistorialPedidos] = useState([])
  const [loadingHistorial, setLoadingHistorial] = useState(false)
  
  const [formData, setFormData] = useState({
    nombre: '',
    telefono: '',
    email: '',
    tipo_cliente: 'Nuevo',
    direccion_principal: '',
    notas: ''
  })

  useEffect(() => {
    cargarEtiquetasDisponibles()
  }, [])
  
  useEffect(() => {
    cargarClientes()
    
    // Escuchar eventos de actualización
    const unsubscribe = eventBus.on(EVENT_TYPES.CLIENTES, () => {
      cargarClientes()
    })
    
    return () => {
      unsubscribe()
    }
  }, [paginaActual, tipoFiltro, etiquetasFiltro])

  // Volver a cargar cuando cambia la búsqueda (con debounce) y resetear a página 1
  useEffect(() => {
    const timeout = setTimeout(() => {
      setPaginaActual(1)
      cargarClientes()
    }, 300)
    return () => clearTimeout(timeout)
  }, [busqueda])

  const cargarEtiquetasDisponibles = async () => {
    try {
      const response = await axios.get(`${API_URL}/clientes/etiquetas`)
      if (response.data.success) {
        setEtiquetasDisponibles(response.data.data || [])
      }
    } catch (error) {
      console.error('Error al cargar etiquetas:', error)
    }
  }
  
  const cargarClientes = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (tipoFiltro) params.append('tipo', tipoFiltro)
      if (busqueda) params.append('buscar', busqueda)
      
      // Filtrar por etiquetas si están seleccionadas
      if (etiquetasFiltro.length > 0) {
        params.append('etiquetas', etiquetasFiltro.join(','))
      }
      
      params.append('page', paginaActual)
      params.append('limit', limitePorPagina)
      
      const response = await axios.get(`${API_URL}/clientes?${params}`)
      if (response.data.success) {
        setClientes(response.data.data)
        setTotalClientes(response.data.total)
        setTotalPaginas(response.data.total_pages)
        // Guardar estadísticas globales
        if (response.data.stats) {
          setStatsGlobales(response.data.stats)
        }
      }
    } catch (error) {
      console.error('Error al cargar clientes:', error)
      alert('Error al cargar clientes')
    } finally {
      setLoading(false)
    }
  }
  
  const cargarDetallesCliente = async (clienteId) => {
    try {
      setLoadingHistorial(true)
      const response = await axios.get(`${API_URL}/clientes/${clienteId}/pedidos`)
      
      if (response.data.success) {
        setHistorialPedidos(response.data.data.pedidos || [])
      }
    } catch (error) {
      console.error('Error al cargar historial:', error)
    } finally {
      setLoadingHistorial(false)
    }
  }
  
  const handleAbrirDetalles = (cliente) => {
    setClienteDetalle(cliente)
    setHistorialPedidos([])
    setMostrarDetalles(true)
    cargarDetallesCliente(cliente.id)
  }

  const handleNuevoCliente = () => {
    setModoEdicion(false)
    setClienteSeleccionado(null)
    setFormData({
      nombre: '',
      telefono: '',
      email: '',
      tipo_cliente: 'Nuevo',
      direccion_principal: '',
      notas: ''
    })
    setMostrarModal(true)
  }

  const handleEditarCliente = (cliente) => {
    setModoEdicion(true)
    setClienteSeleccionado(cliente)
    setFormData({
      nombre: cliente.nombre,
      telefono: cliente.telefono,
      email: cliente.email || '',
      tipo_cliente: cliente.tipo_cliente,
      direccion_principal: cliente.direccion_principal || '',
      notas: cliente.notas || ''
    })
    setMostrarModal(true)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    try {
      if (modoEdicion) {
        // Actualizar cliente existente
        const response = await axios.put(
          `${API_URL}/clientes/${clienteSeleccionado.id}`,
          formData
        )
        if (response.data.success) {
          alert('✅ Cliente actualizado exitosamente')
          setMostrarModal(false)
          cargarClientes()
        }
      } else {
        // Crear nuevo cliente
        const response = await axios.post(`${API_URL}/clientes`, formData)
        if (response.data.success) {
          alert('✅ Cliente creado exitosamente')
          setMostrarModal(false)
          cargarClientes()
        }
      }
    } catch (error) {
      console.error('Error al guardar cliente:', error)
      alert(error.response?.data?.error || 'Error al guardar cliente')
    }
  }

  const handleEliminarCliente = async (cliente) => {
    if (!confirm(`¿Estás seguro de eliminar al cliente ${cliente.nombre}?`)) {
      return
    }
    
    try {
      const response = await axios.delete(`${API_URL}/clientes/${cliente.id}`)
      if (response.data.success) {
        alert('✅ Cliente eliminado exitosamente')
        cargarClientes()
        // Notificar a otras páginas del cambio
        eventBus.emit(EVENT_TYPES.CLIENTES, { action: 'deleted', id: cliente.id })
        eventBus.emit(EVENT_TYPES.PEDIDOS, { action: 'client_deleted' })
      }
    } catch (error) {
      console.error('Error al eliminar cliente:', error)
      alert(error.response?.data?.error || 'Error al eliminar cliente')
    }
  }

  // Filtrar clientes
  const clientesFiltrados = clientes.filter(cliente => {
    const matchBusqueda = 
      cliente.nombre.toLowerCase().includes(busqueda.toLowerCase()) ||
      cliente.telefono.includes(busqueda) ||
      (cliente.email && cliente.email.toLowerCase().includes(busqueda.toLowerCase()))
    
    const matchTipo = !tipoFiltro || cliente.tipo_cliente === tipoFiltro
    
    return matchBusqueda && matchTipo
  })

  const getTipoColor = (tipo) => {
    const colores = {
      'VIP': 'bg-purple-100 text-purple-700 border-purple-300',
      'Fiel': 'bg-blue-100 text-blue-700 border-blue-300',
      'Cumplidor': 'bg-green-100 text-green-700 border-green-300',
      'No Cumplidor': 'bg-red-100 text-red-700 border-red-300',
      'Nuevo': 'bg-yellow-100 text-yellow-700 border-yellow-300',
      'Ocasional': 'bg-gray-100 text-gray-700 border-gray-300'
    }
    return colores[tipo] || 'bg-gray-100 text-gray-700 border-gray-300'
  }

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="sm:flex sm:items-center sm:justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <User className="h-8 w-8 text-blue-600" />
            Clientes
          </h1>
          <p className="mt-2 text-sm text-gray-700">
            Gestiona tu base de clientes y su historial de compras
          </p>
        </div>
        <div className="mt-4 sm:mt-0 flex gap-3">
          <button
            onClick={() => {
              window.open(`${API_URL}/exportar/clientes`, '_blank')
            }}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700"
          >
            <Download className="h-5 w-5 mr-2" />
            Descargar Excel
          </button>
          <button
            onClick={handleNuevoCliente}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
          >
            <Plus className="h-5 w-5 mr-2" />
            Nuevo Cliente
          </button>
        </div>
      </div>

      {/* Filtros y búsqueda */}
      <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Barra de búsqueda */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar por nombre, teléfono o email..."
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Filtro por tipo */}
          <div>
            <select
              value={tipoFiltro}
              onChange={(e) => setTipoFiltro(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Todos los tipos</option>
              <option value="VIP">VIP</option>
              <option value="Fiel">Fiel</option>
              <option value="Cumplidor">Cumplidor</option>
              <option value="No Cumplidor">No Cumplidor</option>
              <option value="Nuevo">Nuevo</option>
              <option value="Ocasional">Ocasional</option>
            </select>
          </div>

          {/* Filtro por etiquetas */}
          <div className="relative">
            <Tag className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400 pointer-events-none z-10" />
            <button
              type="button"
              onClick={() => setCategoriaEtiquetaVisible(categoriaEtiquetaVisible ? null : 'all')}
              className="w-full pl-10 pr-10 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm text-left bg-white hover:bg-gray-50 transition-colors"
            >
              {etiquetasFiltro.length > 0 
                ? `${etiquetasFiltro.length} etiqueta(s) seleccionada(s)` 
                : 'Filtrar por etiquetas...'}
            </button>
            
            {/* Dropdown de etiquetas */}
            {categoriaEtiquetaVisible && (
              <>
                {/* Overlay para cerrar al hacer clic fuera */}
                <div 
                  className="fixed inset-0 z-10" 
                  onClick={() => setCategoriaEtiquetaVisible(null)}
                />
                
                {/* Menú dropdown */}
                <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-300 rounded-lg shadow-lg z-20 max-h-96 overflow-y-auto">
                  {Object.entries(etiquetasDisponibles).map(([categoria, etiquetas]) => (
                    <div key={categoria} className="border-b border-gray-100 last:border-b-0">
                      <div className="px-3 py-2 bg-gray-50 text-xs font-semibold text-gray-600 uppercase sticky top-0">
                        {categoria}
                      </div>
                      <div className="py-1">
                        {etiquetas.map((etiqueta) => (
                          <label
                            key={etiqueta.id}
                            className="flex items-center gap-2 px-3 py-2 hover:bg-gray-50 cursor-pointer transition-colors"
                          >
                            <input
                              type="checkbox"
                              checked={etiquetasFiltro.includes(etiqueta.id)}
                              onChange={(e) => {
                                if (e.target.checked) {
                                  setEtiquetasFiltro([...etiquetasFiltro, etiqueta.id])
                                } else {
                                  setEtiquetasFiltro(etiquetasFiltro.filter(id => id !== etiqueta.id))
                                }
                                setPaginaActual(1)
                              }}
                              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                            />
                            <span className="text-sm flex items-center gap-1.5">
                              <span>{etiqueta.icono}</span>
                              <span>{etiqueta.nombre}</span>
                            </span>
                          </label>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </>
            )}
            
            {etiquetasFiltro.length > 0 && (
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  setEtiquetasFiltro([])
                  setPaginaActual(1)
                }}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 z-10"
                title="Limpiar filtros"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>
        </div>
        
        {/* Etiquetas seleccionadas */}
        {etiquetasFiltro.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {etiquetasFiltro.map(etiquetaId => {
              const etiqueta = Object.values(etiquetasDisponibles)
                .flat()
                .find(e => e.id === etiquetaId)
              if (!etiqueta) return null
              return (
                <span
                  key={etiqueta.id}
                  className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium"
                  style={{
                    backgroundColor: `${etiqueta.color}15`,
                    color: etiqueta.color,
                    border: `1px solid ${etiqueta.color}40`
                  }}
                >
                  {etiqueta.icono} {etiqueta.nombre}
                  <button
                    onClick={() => {
                      setEtiquetasFiltro(etiquetasFiltro.filter(id => id !== etiqueta.id))
                      setPaginaActual(1)
                    }}
                    className="hover:opacity-70"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </span>
              )
            })}
          </div>
        )}
      </div>

      {/* Estadísticas rápidas - Scrolleable horizontalmente */}
      <div className="mb-6">
        <div className="overflow-x-auto custom-scrollbar pb-2">
          <div className="flex gap-4 min-w-max">
        {/* Total Clientes */}
        <button
          onClick={() => setTipoFiltro('')}
          className={`relative group bg-white p-4 rounded-lg shadow-sm border-2 transition-all hover:shadow-lg hover:scale-105 text-left min-w-[220px] ${
            tipoFiltro === '' ? 'border-blue-500 ring-2 ring-blue-200' : 'border-gray-200'
          }`}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Clientes</p>
              <p className="text-2xl font-bold text-gray-900">{statsGlobales.total.toLocaleString()}</p>
            </div>
            <User className="h-8 w-8 text-blue-600" />
          </div>
          <div className="absolute -top-2 -right-2 bg-blue-100 text-blue-700 text-xs px-2 py-1 rounded-full opacity-0 group-hover:opacity-100 transition-opacity">
            Ver todos
          </div>
        </button>
        
        {/* Clientes VIP */}
        <button
          onClick={() => setTipoFiltro('VIP')}
          className={`relative group bg-white p-4 rounded-lg shadow-sm border-2 transition-all hover:shadow-lg hover:scale-105 text-left min-w-[220px] ${
            tipoFiltro === 'VIP' ? 'border-purple-500 ring-2 ring-purple-200' : 'border-gray-200'
          }`}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 flex items-center gap-1">
                Clientes VIP
                <span className="text-xs">⭐</span>
              </p>
              <p className="text-2xl font-bold text-purple-600">
                {statsGlobales.vip.toLocaleString()}
              </p>
            </div>
            <User className="h-8 w-8 text-purple-600" />
          </div>
          {/* Tooltip explicativo */}
          <div className="absolute left-1/2 -translate-x-1/2 bottom-[calc(100%+0.5rem)] w-72 bg-purple-600 text-white text-xs p-3 rounded-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-[9999] shadow-xl pointer-events-none">
            <p className="font-bold mb-2">🌟 Clientes VIP</p>
            <p className="mb-1">• Plazo de pago: <span className="font-bold">45 días</span></p>
            <p className="mb-1">• Alto valor de compra</p>
            <p className="mb-2">• Máxima prioridad y beneficios</p>
            <div className="border-t border-purple-400 pt-2 mt-2 space-y-1">
              <div className="flex justify-between items-center">
                <p className="font-bold">💰 Gasto promedio:</p>
                <p className="text-base font-bold">${statsGlobales.promedio_vip.toLocaleString('es-CL', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}</p>
              </div>
              <div className="flex justify-between items-center">
                <p className="font-bold">📦 Pedidos promedio:</p>
                <p className="text-base font-bold">{statsGlobales.promedio_pedidos_vip.toFixed(1)} pedidos</p>
              </div>
            </div>
            <div className="absolute left-1/2 -translate-x-1/2 top-full w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-purple-600"></div>
          </div>
        </button>
        
        {/* Clientes Fieles */}
        <button
          onClick={() => setTipoFiltro('Fiel')}
          className={`relative group bg-white p-4 rounded-lg shadow-sm border-2 transition-all hover:shadow-lg hover:scale-105 text-left min-w-[220px] ${
            tipoFiltro === 'Fiel' ? 'border-blue-500 ring-2 ring-blue-200' : 'border-gray-200'
          }`}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 flex items-center gap-1">
                Clientes Fieles
                <span className="text-xs">💎</span>
              </p>
              <p className="text-2xl font-bold text-blue-600">
                {statsGlobales.fiel.toLocaleString()}
              </p>
            </div>
            <User className="h-8 w-8 text-blue-600" />
          </div>
          {/* Tooltip explicativo */}
          <div className="absolute left-1/2 -translate-x-1/2 bottom-[calc(100%+0.5rem)] w-72 bg-blue-600 text-white text-xs p-3 rounded-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-[9999] shadow-xl pointer-events-none">
            <p className="font-bold mb-2">💎 Clientes Fieles</p>
            <p className="mb-1">• Plazo de pago: <span className="font-bold">15 días</span></p>
            <p className="mb-1">• Compras recurrentes</p>
            <p className="mb-2">• Buen historial de pagos</p>
            <div className="border-t border-blue-400 pt-2 mt-2 space-y-1">
              <div className="flex justify-between items-center">
                <p className="font-bold">💰 Gasto promedio:</p>
                <p className="text-base font-bold">${statsGlobales.promedio_fiel.toLocaleString('es-CL', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}</p>
              </div>
              <div className="flex justify-between items-center">
                <p className="font-bold">📦 Pedidos promedio:</p>
                <p className="text-base font-bold">{statsGlobales.promedio_pedidos_fiel.toFixed(1)} pedidos</p>
              </div>
            </div>
            <div className="absolute left-1/2 -translate-x-1/2 top-full w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-blue-600"></div>
          </div>
        </button>
        
        {/* Clientes Nuevos */}
        <button
          onClick={() => setTipoFiltro('Nuevo')}
          className={`relative group bg-white p-4 rounded-lg shadow-sm border-2 transition-all hover:shadow-lg hover:scale-105 text-left min-w-[220px] ${
            tipoFiltro === 'Nuevo' ? 'border-yellow-500 ring-2 ring-yellow-200' : 'border-gray-200'
          }`}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Nuevos</p>
              <p className="text-2xl font-bold text-yellow-600">
                {statsGlobales.nuevo.toLocaleString()}
              </p>
            </div>
            <User className="h-8 w-8 text-yellow-600" />
          </div>
          {/* Tooltip explicativo */}
          <div className="absolute left-1/2 -translate-x-1/2 bottom-[calc(100%+0.5rem)] w-72 bg-yellow-600 text-white text-xs p-3 rounded-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-[9999] shadow-xl pointer-events-none">
            <p className="font-bold mb-2">🌱 Clientes Nuevos</p>
            <p className="mb-1">• Plazo de pago: <span className="font-bold">Pago inmediato</span></p>
            <p className="mb-1">• Primera compra</p>
            <p className="mb-2">• Sin historial previo</p>
            <div className="border-t border-yellow-400 pt-2 mt-2 space-y-1">
              <div className="flex justify-between items-center">
                <p className="font-bold">💰 Gasto promedio:</p>
                <p className="text-base font-bold">${statsGlobales.promedio_nuevo.toLocaleString('es-CL', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}</p>
              </div>
              <div className="flex justify-between items-center">
                <p className="font-bold">📦 Pedidos promedio:</p>
                <p className="text-base font-bold">{statsGlobales.promedio_pedidos_nuevo.toFixed(1)} pedidos</p>
              </div>
            </div>
            <div className="absolute left-1/2 -translate-x-1/2 top-full w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-yellow-600"></div>
          </div>
        </button>
        
        {/* Clientes Ocasionales */}
        <button
          onClick={() => setTipoFiltro('Ocasional')}
          className={`relative group bg-white p-4 rounded-lg shadow-sm border-2 transition-all hover:shadow-lg hover:scale-105 text-left min-w-[220px] ${
            tipoFiltro === 'Ocasional' ? 'border-gray-500 ring-2 ring-gray-200' : 'border-gray-200'
          }`}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 flex items-center gap-1">
                Ocasionales
                <span className="text-xs">🔄</span>
              </p>
              <p className="text-2xl font-bold text-gray-600">
                {statsGlobales.ocasional.toLocaleString()}
              </p>
            </div>
            <User className="h-8 w-8 text-gray-600" />
          </div>
          {/* Tooltip explicativo */}
          <div className="absolute left-1/2 -translate-x-1/2 bottom-[calc(100%+0.5rem)] w-72 bg-gray-600 text-white text-xs p-3 rounded-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-[9999] shadow-xl pointer-events-none">
            <p className="font-bold mb-2">🔄 Clientes Ocasionales</p>
            <p className="mb-1">• Plazo de pago: <span className="font-bold">7 días</span></p>
            <p className="mb-1">• Compras esporádicas</p>
            <p className="mb-2">• Sin patrón regular</p>
            <div className="border-t border-gray-400 pt-2 mt-2 space-y-1">
              <div className="flex justify-between items-center">
                <p className="font-bold">💰 Gasto promedio:</p>
                <p className="text-base font-bold">${statsGlobales.promedio_ocasional.toLocaleString('es-CL', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}</p>
              </div>
              <div className="flex justify-between items-center">
                <p className="font-bold">📦 Pedidos promedio:</p>
                <p className="text-base font-bold">{statsGlobales.promedio_pedidos_ocasional.toFixed(1)} pedidos</p>
              </div>
            </div>
            <div className="absolute left-1/2 -translate-x-1/2 top-full w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-600"></div>
          </div>
        </button>
          </div>
        </div>
      </div>

      {/* Tabla de clientes */}
      <div className="bg-white shadow-sm rounded-lg border border-gray-200 overflow-hidden">
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-2 text-gray-600">Cargando clientes...</p>
          </div>
        ) : clientesFiltrados.length === 0 ? (
          <div className="text-center py-12">
            <User className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No hay clientes</h3>
            <p className="mt-1 text-sm text-gray-500">
              {busqueda || tipoFiltro ? 'No se encontraron clientes con esos filtros' : 'Comienza agregando un nuevo cliente'}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Cliente
                  </th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Contacto
                  </th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Tipo
                  </th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Etiquetas
                  </th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Estadísticas
                  </th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Notas
                  </th>
                  <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {clientesFiltrados.map((cliente) => (
                  <tr 
                    key={cliente.id} 
                    onClick={() => handleAbrirDetalles(cliente)}
                    className="hover:bg-primary-50 cursor-pointer transition-colors"
                  >
                    <td className="px-3 py-2 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center">
                          <span className="text-blue-600 font-semibold text-sm">
                            {cliente.nombre.charAt(0).toUpperCase()}
                          </span>
                        </div>
                        <div className="ml-3">
                          <div className="text-sm font-medium text-gray-900">{cliente.nombre}</div>
                          <div className="text-xs text-gray-500">{cliente.id}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-3 py-2">
                      <div className="text-sm text-gray-900 flex items-center gap-1">
                        <Phone className="h-3.5 w-3.5 text-gray-400" />
                        {cliente.telefono}
                      </div>
                      {cliente.email && (
                        <div className="text-xs text-gray-500 flex items-center gap-1 mt-0.5">
                          <Mail className="h-3.5 w-3.5 text-gray-400" />
                          {cliente.email}
                        </div>
                      )}
                    </td>
                    <td className="px-3 py-2 whitespace-nowrap">
                      <span className={`px-2 py-0.5 inline-flex text-xs leading-5 font-semibold rounded-full border ${getTipoColor(cliente.tipo_cliente)}`}>
                        {cliente.tipo_cliente}
                      </span>
                    </td>
                    <td className="px-3 py-2">
                      <div className="flex flex-wrap gap-1 max-w-xs">
                        {cliente.etiquetas && cliente.etiquetas.length > 0 ? (
                          cliente.etiquetas.slice(0, 2).map((etiqueta) => (
                            <EtiquetaCliente key={etiqueta.id} etiqueta={etiqueta} size="sm" mostrarDescripcion={false} />
                          ))
                        ) : (
                          <span className="text-xs text-gray-400 italic">Sin etiquetas</span>
                        )}
                        {cliente.etiquetas && cliente.etiquetas.length > 2 && (
                          <span className="px-1.5 py-0.5 text-xs text-gray-600 bg-gray-100 rounded-full font-medium">
                            +{cliente.etiquetas.length - 2}
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-3 py-2">
                      <div className="text-sm text-gray-900 flex items-center gap-1">
                        <ShoppingBag className="h-3.5 w-3.5 text-gray-400" />
                        {cliente.total_pedidos} pedidos
                      </div>
                      <div className="text-xs text-gray-500 flex items-center gap-1 mt-0.5">
                        <DollarSign className="h-3.5 w-3.5 text-gray-400" />
                        ${cliente.total_gastado?.toLocaleString('es-CL') || 0}
                      </div>
                    </td>
                    <td className="px-3 py-2">
                      <div className="text-xs text-gray-500 max-w-xs truncate">
                        {cliente.notas || '-'}
                      </div>
                    </td>
                    <td className="px-3 py-2 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleEditarCliente(cliente)
                        }}
                        className="text-blue-600 hover:text-blue-900 mr-2"
                        title="Editar"
                      >
                        <Edit2 className="h-3.5 w-3.5" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleEliminarCliente(cliente)
                        }}
                        className={`p-1 rounded-lg transition-all duration-200 ${
                          cliente.total_pedidos > 0 
                            ? 'text-gray-400 cursor-not-allowed' 
                            : 'hover:bg-red-50 text-red-600 hover:text-red-700'
                        }`}
                        title={cliente.total_pedidos > 0 ? 'No se puede eliminar (tiene pedidos)' : 'Eliminar cliente'}
                        disabled={cliente.total_pedidos > 0}
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        
        {/* Controles de Paginación */}
        {!loading && clientes.length > 0 && (
          <div className="bg-white px-6 py-4 border-t border-gray-200 flex items-center justify-between">
            <div className="text-sm text-gray-700">
              Mostrando {((paginaActual - 1) * limitePorPagina) + 1} a {Math.min(paginaActual * limitePorPagina, totalClientes)} de {totalClientes.toLocaleString()} clientes
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setPaginaActual(1)}
                disabled={paginaActual === 1}
                className="px-3 py-1 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
              >
                Primera
              </button>
              <button
                onClick={() => setPaginaActual(prev => Math.max(1, prev - 1))}
                disabled={paginaActual === 1}
                className="px-3 py-1 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
              >
                Anterior
              </button>
              <span className="px-4 py-1 bg-primary-50 text-primary-700 rounded-lg text-sm font-medium">
                Página {paginaActual} de {totalPaginas}
              </span>
              <button
                onClick={() => setPaginaActual(prev => Math.min(totalPaginas, prev + 1))}
                disabled={paginaActual === totalPaginas}
                className="px-3 py-1 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
              >
                Siguiente
              </button>
              <button
                onClick={() => setPaginaActual(totalPaginas)}
                disabled={paginaActual === totalPaginas}
                className="px-3 py-1 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
              >
                Última
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Modal de Formulario */}
      {mostrarModal && (
        <div 
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
          onClick={() => setMostrarModal(false)}
        >
          <div 
            className="bg-white rounded-lg shadow-xl max-w-2xl w-full"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between rounded-t-lg">
              <h2 className="text-xl font-bold text-gray-900">
                {modoEdicion ? 'Editar Cliente' : 'Nuevo Cliente'}
              </h2>
              <button 
                onClick={() => setMostrarModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-6 w-6" />
              </button>
            </div>

            {/* Formulario */}
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              {/* Nombre */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nombre <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  value={formData.nombre}
                  onChange={(e) => setFormData({...formData, nombre: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="María González"
                />
              </div>

              {/* Teléfono y Email */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Teléfono <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="tel"
                    required
                    value={formData.telefono}
                    onChange={(e) => setFormData({...formData, telefono: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="+56912345678"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email
                  </label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="cliente@email.com"
                  />
                </div>
              </div>

              {/* Tipo de Cliente */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tipo de Cliente
                </label>
                <select
                  value={formData.tipo_cliente}
                  onChange={(e) => setFormData({...formData, tipo_cliente: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="Nuevo">Nuevo</option>
                  <option value="Fiel">Fiel</option>
                  <option value="Cumplidor">Cumplidor</option>
                  <option value="No Cumplidor">No Cumplidor</option>
                  <option value="VIP">VIP</option>
                  <option value="Ocasional">Ocasional</option>
                </select>
              </div>

              {/* Notas */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Notas
                </label>
                <textarea
                  value={formData.notas}
                  onChange={(e) => setFormData({...formData, notas: e.target.value})}
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Preferencias, observaciones, etc."
                />
              </div>

              {/* Botones */}
              <div className="flex justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setMostrarModal(false)}
                  className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  {modoEdicion ? 'Guardar Cambios' : 'Crear Cliente'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      
      {/* Modal de Detalles del Cliente */}
      {mostrarDetalles && clienteDetalle && (
        <div
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-[9999] p-4"
          onClick={() => setMostrarDetalles(false)}
        >
          <div
            className="bg-white rounded-2xl shadow-2xl max-w-5xl w-full max-h-[90vh] overflow-y-auto relative z-[10000]"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="sticky top-0 bg-gradient-to-r from-indigo-500 to-purple-500 text-white px-8 py-6 flex items-center justify-between z-10 shadow-lg rounded-t-2xl">
              <div className="flex items-center gap-4">
                <div className="h-16 w-16 bg-white/30 rounded-full flex items-center justify-center text-3xl font-bold shadow-lg">
                  {clienteDetalle.nombre.charAt(0).toUpperCase()}
                </div>
                <div>
                  <h2 className="text-3xl font-bold">{clienteDetalle.nombre}</h2>
                  <p className="text-sm text-indigo-100 mt-1 font-medium">ID: {clienteDetalle.id}</p>
                </div>
                {clienteDetalle.tipo_cliente && (
                  <span className={`px-4 py-2 rounded-full text-sm font-bold shadow-md ${
                    clienteDetalle.tipo_cliente === 'VIP' ? 'bg-yellow-400 text-yellow-900' :
                    clienteDetalle.tipo_cliente === 'Fiel' ? 'bg-green-400 text-green-900' :
                    clienteDetalle.tipo_cliente === 'Cumplidor' ? 'bg-blue-400 text-blue-900' :
                    'bg-gray-300 text-gray-800'
                  }`}>
                    ⭐ {clienteDetalle.tipo_cliente}
                  </span>
                )}
              </div>
              <button 
                onClick={() => setMostrarDetalles(false)}
                className="text-white hover:bg-white/20 transition-all duration-200 p-2 rounded-lg"
              >
                <X className="h-6 w-6" />
              </button>
            </div>

            {/* Contenido */}
            <div className="p-6 space-y-6">
              {/* Grid de 2 columnas */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                
                {/* Columna Izquierda: Información de Contacto */}
                <div className="space-y-6">
                  
                  {/* Información de Contacto */}
                  <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-all duration-200">
                    <h3 className="text-sm font-bold text-gray-900 uppercase mb-4 flex items-center">
                      <Phone className="h-5 w-5 mr-2 text-indigo-500" />
                      Información de Contacto
                    </h3>
                    <div className="space-y-3">
                      {clienteDetalle.telefono && (
                        <div>
                          <p className="text-xs text-gray-500 font-semibold uppercase mb-1">Teléfono</p>
                          <p className="text-base font-medium text-gray-900 bg-gray-50 p-2 rounded border border-gray-200 flex items-center gap-2">
                            <Phone className="h-4 w-4 text-indigo-500" />
                            {clienteDetalle.telefono}
                          </p>
                        </div>
                      )}
                      {clienteDetalle.email && (
                        <div>
                          <p className="text-xs text-gray-500 font-semibold uppercase mb-1">Email</p>
                          <p className="text-base font-medium text-gray-900 bg-gray-50 p-2 rounded border border-gray-200 flex items-center gap-2 break-all">
                            <Mail className="h-4 w-4 text-indigo-500" />
                            {clienteDetalle.email}
                          </p>
                        </div>
                      )}
                      {clienteDetalle.fecha_registro && (
                        <div>
                          <p className="text-xs text-gray-500 font-semibold uppercase mb-1">Cliente desde</p>
                          <p className="text-sm text-gray-900 bg-gray-50 p-2 rounded border border-gray-200 flex items-center gap-2">
                            <Calendar className="h-4 w-4 text-indigo-500" />
                            {formatFecha(clienteDetalle.fecha_registro)}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                  
                  {/* Etiquetas del Cliente */}
                  <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-all duration-200">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-sm font-bold text-gray-900 uppercase flex items-center">
                        <Tag className="h-5 w-5 mr-2 text-indigo-500" />
                        Etiquetas
                      </h3>
                      <button
                        onClick={() => setCategoriaEtiquetaVisible('agregar')}
                        className="px-3 py-1.5 bg-indigo-500 text-white rounded-lg text-xs font-medium hover:bg-indigo-600 transition-colors flex items-center gap-1"
                      >
                        <Plus className="h-3.5 w-3.5" />
                        Agregar
                      </button>
                    </div>

                    {/* Selector de Etiquetas */}
                    {categoriaEtiquetaVisible === 'agregar' && (
                      <div className="mb-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
                        <div className="flex items-center justify-between mb-3">
                          <h4 className="text-xs font-semibold text-gray-700">Selecciona una etiqueta:</h4>
                          <button
                            onClick={() => setCategoriaEtiquetaVisible(null)}
                            className="text-gray-400 hover:text-gray-600"
                          >
                            <X className="h-4 w-4" />
                          </button>
                        </div>
                        <div className="space-y-3 max-h-60 overflow-y-auto">
                          {Object.entries(etiquetasDisponibles).map(([categoria, etiquetas]) => (
                            <div key={categoria}>
                              <p className="text-xs font-semibold text-gray-600 uppercase mb-2">{categoria}</p>
                              <div className="flex flex-wrap gap-2">
                                {etiquetas.map((etiqueta) => {
                                  const yaLaTiene = clienteDetalle.etiquetas?.some(e => e.id === etiqueta.id)
                                  return (
                                    <button
                                      key={etiqueta.id}
                                      disabled={yaLaTiene}
                                      onClick={async () => {
                                        try {
                                          await axios.post(`${API_URL}/clientes/${clienteDetalle.id}/etiquetas`, {
                                            etiqueta_id: etiqueta.id
                                          })
                                          alert('✅ Etiqueta agregada')
                                          setCategoriaEtiquetaVisible(null)
                                          // Recargar detalles del cliente
                                          const response = await axios.get(`${API_URL}/clientes/${clienteDetalle.id}`)
                                          if (response.data.success) {
                                            setClienteDetalle(response.data.data)
                                          }
                                        } catch (error) {
                                          console.error('Error:', error)
                                          alert('❌ Error: ' + (error.response?.data?.error || error.message))
                                        }
                                      }}
                                      className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
                                        yaLaTiene
                                          ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                                          : 'bg-white border border-gray-300 text-gray-700 hover:border-indigo-500 hover:bg-indigo-50 cursor-pointer'
                                      }`}
                                      title={yaLaTiene ? 'Ya tiene esta etiqueta' : 'Clic para agregar'}
                                    >
                                      {etiqueta.nombre} {yaLaTiene && '✓'}
                                    </button>
                                  )
                                })}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {clienteDetalle.etiquetas && clienteDetalle.etiquetas.length > 0 ? (
                      <div className="space-y-3">
                        {Object.entries(
                          clienteDetalle.etiquetas.reduce((acc, etiqueta) => {
                            if (!acc[etiqueta.categoria]) {
                              acc[etiqueta.categoria] = []
                            }
                            acc[etiqueta.categoria].push(etiqueta)
                            return acc
                          }, {})
                        ).map(([categoria, etiquetas]) => (
                          <div key={categoria}>
                            <p className="text-xs font-semibold text-gray-500 uppercase mb-2">
                              {categoria}
                            </p>
                            <div className="flex flex-wrap gap-2">
                              {etiquetas.map((etiqueta) => (
                                <div key={etiqueta.id} className="group relative">
                                  <EtiquetaCliente etiqueta={etiqueta} />
                                  <button
                                    onClick={async () => {
                                      if (!confirm(`¿Eliminar la etiqueta "${etiqueta.nombre}"?`)) return

                                      try {
                                        await axios.delete(`${API_URL}/clientes/${clienteDetalle.id}/etiquetas/${etiqueta.id}`)
                                        alert('✅ Etiqueta eliminada')
                                        // Recargar detalles del cliente
                                        const response = await axios.get(`${API_URL}/clientes/${clienteDetalle.id}`)
                                        if (response.data.success) {
                                          setClienteDetalle(response.data.data)
                                        }
                                      } catch (error) {
                                        console.error('Error:', error)
                                        alert('❌ Error: ' + (error.response?.data?.error || error.message))
                                      }
                                    }}
                                    className="absolute -top-1.5 -right-1.5 bg-red-500 text-white rounded-full w-4 h-4 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity text-[10px] font-bold hover:bg-red-600"
                                    title="Eliminar etiqueta"
                                  >
                                    ×
                                  </button>
                                </div>
                              ))}
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm text-gray-500 italic">No hay etiquetas asignadas</p>
                    )}
                  </div>
                  
                  {/* Notas */}
                  {clienteDetalle.notas && (
                    <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
                      <h3 className="text-sm font-bold text-gray-900 uppercase mb-3 flex items-center">
                        📝 Notas
                      </h3>
                      <p className="text-sm text-gray-700 bg-gray-50 p-3 rounded border border-gray-200">
                        {clienteDetalle.notas}
                      </p>
                    </div>
                  )}
                </div>
                
                {/* Columna Derecha: Estadísticas */}
                <div className="space-y-6">
                  
                  {/* Estadísticas */}
                  <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
                    <h3 className="text-sm font-bold text-gray-900 uppercase mb-4 flex items-center">
                      <span className="text-indigo-500 mr-2">📊</span> Estadísticas de Compra
                    </h3>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center p-3 bg-gray-50 rounded border border-gray-200">
                        <span className="text-sm text-gray-700 font-medium">Total de Pedidos:</span>
                        <span className="text-2xl font-bold text-gray-900">{clienteDetalle.total_pedidos || 0}</span>
                      </div>
                      <div className="flex justify-between items-center p-3 bg-gray-50 rounded border border-gray-200">
                        <span className="text-sm text-gray-700 font-medium">Total Gastado:</span>
                        <span className="text-2xl font-bold text-gray-900">
                          ${(clienteDetalle.total_gastado || 0).toLocaleString('es-CL')}
                        </span>
                      </div>
                      {clienteDetalle.total_pedidos > 0 && (
                        <div className="flex justify-between items-center p-3 bg-indigo-50 rounded border border-indigo-200">
                          <span className="text-sm text-indigo-700 font-medium">Ticket Promedio:</span>
                          <span className="text-xl font-bold text-indigo-900">
                            ${Math.round((clienteDetalle.total_gastado || 0) / (clienteDetalle.total_pedidos || 1)).toLocaleString('es-CL')}
                          </span>
                        </div>
                      )}
                      {clienteDetalle.ultima_compra && (
                        <div className="text-xs text-gray-600 pt-2 border-t border-gray-200 flex items-center gap-2">
                          <Calendar className="h-4 w-4 text-indigo-500" />
                          <span>Última compra: {formatFecha(clienteDetalle.ultima_compra)}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Historial de Pedidos */}
              <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
                <h3 className="text-sm font-bold text-gray-900 uppercase mb-4 flex items-center justify-between">
                  <span className="flex items-center">
                    <ShoppingBag className="h-5 w-5 mr-2 text-indigo-500" />
                    Historial de Pedidos
                  </span>
                  <span className="text-xs bg-gray-100 text-gray-800 px-3 py-1 rounded-full">
                    {historialPedidos.length} pedidos
                  </span>
                </h3>
                
                {loadingHistorial ? (
                  <div className="text-center py-8">
                    <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-indigo-500 border-t-transparent"></div>
                    <p className="text-sm text-gray-600 mt-2">Cargando historial...</p>
                  </div>
                ) : historialPedidos.length > 0 ? (
                  <div className="max-h-96 overflow-y-auto space-y-2 custom-scrollbar">
                    {historialPedidos.map((pedido) => (
                      <div 
                        key={pedido.id}
                        className="relative p-4 rounded-lg border border-gray-200 bg-gray-50 hover:bg-gray-100 hover:border-indigo-300 hover:shadow-md transition-all group"
                      >
                        <div className="flex gap-4">
                          {/* Foto en miniatura */}
                          <div className="flex-shrink-0">
                            <div className="w-20 h-20 rounded-lg overflow-hidden bg-gradient-to-br from-indigo-100 to-purple-100 flex items-center justify-center border border-indigo-200">
                              {pedido.foto_enviado_url || pedido.producto_imagen ? (
                                <img 
                                  src={pedido.foto_enviado_url || pedido.producto_imagen} 
                                  alt={pedido.producto_nombre || 'Producto'}
                                  className="w-full h-full object-cover"
                                />
                              ) : (
                                <span className="text-3xl">🌸</span>
                              )}
                            </div>
                          </div>
                          
                          {/* Contenido del pedido */}
                          <div className="flex-1 min-w-0">
                            <div className="flex justify-between items-start mb-2">
                              <div>
                                <span className="text-sm font-bold text-gray-800">Pedido #{pedido.id}</span>
                                <p className="text-xs text-gray-500 mt-1 flex items-center gap-1">
                                  <Calendar className="h-3 w-3" />
                                  {formatFecha(pedido.fecha_pedido)}
                                </p>
                              </div>
                              <div className="text-right">
                                <span className="text-lg font-bold text-gray-900">
                                  ${(pedido.precio_total || 0).toLocaleString('es-CL')}
                                </span>
                                <span className={`block mt-1 px-2 py-0.5 rounded-full text-xs font-medium ${
                                  pedido.estado_pago === 'Pagado' 
                                    ? 'bg-green-100 text-green-800' 
                                    : 'bg-red-100 text-red-800'
                                }`}>
                                  {pedido.estado_pago === 'Pagado' ? '✓ Pagado' : '⏳ Pendiente'}
                                </span>
                              </div>
                            </div>
                            <p className="text-sm text-gray-700 flex items-center gap-2">
                              <Package className="h-4 w-4 text-gray-400" />
                              {pedido.arreglo_pedido || pedido.producto_nombre || 'Sin descripción'}
                            </p>
                            {pedido.fecha_entrega && (
                              <p className="text-xs text-gray-500 mt-1">
                                Entrega: {formatFecha(pedido.fecha_entrega)}
                              </p>
                            )}
                          </div>
                        </div>
                        
                        {/* Tooltip que aparece en hover - fixed para salir completamente del contenedor */}
                        <div className="fixed right-8 top-1/2 -translate-y-1/2 w-80 bg-white border-2 border-indigo-500 rounded-xl shadow-2xl p-4 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-[9999]">
                          <div className="space-y-2">
                            <div className="border-b border-indigo-200 pb-2">
                              <p className="text-xs font-semibold text-indigo-600 uppercase">Detalles del Pedido</p>
                            </div>
                            {pedido.producto_nombre && (
                              <div>
                                <p className="text-xs text-gray-500 font-medium">Producto:</p>
                                <p className="text-sm font-bold text-gray-900">{pedido.producto_nombre}</p>
                              </div>
                            )}
                            {pedido.direccion_entrega && (
                              <div>
                                <p className="text-xs text-gray-500 font-medium">Dirección:</p>
                                <p className="text-xs text-gray-700">{pedido.direccion_entrega}</p>
                              </div>
                            )}
                            {pedido.metodo_pago && (
                              <div>
                                <p className="text-xs text-gray-500 font-medium">Método de Pago:</p>
                                <span className="inline-block px-2 py-1 bg-indigo-100 text-indigo-800 rounded text-xs font-medium">
                                  {pedido.metodo_pago}
                                </span>
                              </div>
                            )}
                            {pedido.motivo && (
                              <div>
                                <p className="text-xs text-gray-500 font-medium">Motivo:</p>
                                <span className="inline-block px-2 py-1 bg-pink-100 text-pink-800 rounded text-xs font-medium">
                                  💐 {pedido.motivo}
                                </span>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-500 text-center py-4">
                    No hay historial de pedidos
                  </p>
                )}
              </div>
            </div>

            {/* Footer */}
            <div className="sticky bottom-0 bg-gray-50 px-6 py-4 flex justify-center items-center rounded-b-2xl border-t border-gray-200">
              <button
                onClick={() => setMostrarDetalles(false)}
                className="px-8 py-2.5 border-2 border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100 transition-all font-medium"
              >
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ClientesPage

