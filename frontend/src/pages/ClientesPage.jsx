import { useState, useEffect } from 'react'
import { User, Search, Plus, Edit2, Trash2, X, Phone, Mail, MapPin, DollarSign, ShoppingBag, Download, Calendar, Package } from 'lucide-react'
import axios from 'axios'
import { API_URL } from '../services/api'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'

const formatFecha = (fecha) => {
  if (!fecha) return '-'
  try {
    return format(new Date(fecha), 'dd MMM yyyy', { locale: es })
  } catch {
    return '-'
  }
}

function ClientesPage() {
  const [clientes, setClientes] = useState([])
  const [loading, setLoading] = useState(true)
  const [busqueda, setBusqueda] = useState('')
  const [tipoFiltro, setTipoFiltro] = useState('')
  const [mostrarModal, setMostrarModal] = useState(false)
  const [clienteSeleccionado, setClienteSeleccionado] = useState(null)
  const [modoEdicion, setModoEdicion] = useState(false)
  
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
    nuevo: 0
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
    cargarClientes()
  }, [paginaActual, tipoFiltro])

  const cargarClientes = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (tipoFiltro) params.append('tipo', tipoFiltro)
      if (busqueda) params.append('buscar', busqueda)
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
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
        </div>
      </div>

      {/* Estadísticas rápidas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Clientes</p>
              <p className="text-2xl font-bold text-gray-900">{statsGlobales.total.toLocaleString()}</p>
            </div>
            <User className="h-8 w-8 text-blue-600" />
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Clientes VIP</p>
              <p className="text-2xl font-bold text-purple-600">
                {statsGlobales.vip.toLocaleString()}
              </p>
            </div>
            <User className="h-8 w-8 text-purple-600" />
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Clientes Fieles</p>
              <p className="text-2xl font-bold text-blue-600">
                {statsGlobales.fiel.toLocaleString()}
              </p>
            </div>
            <User className="h-8 w-8 text-blue-600" />
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Nuevos</p>
              <p className="text-2xl font-bold text-yellow-600">
                {statsGlobales.nuevo.toLocaleString()}
              </p>
            </div>
            <User className="h-8 w-8 text-yellow-600" />
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
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Cliente
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Contacto
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Tipo
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Estadísticas
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Notas
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
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
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10 bg-blue-100 rounded-full flex items-center justify-center">
                          <span className="text-blue-600 font-semibold">
                            {cliente.nombre.charAt(0).toUpperCase()}
                          </span>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">{cliente.nombre}</div>
                          <div className="text-sm text-gray-500">{cliente.id}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900 flex items-center gap-1">
                        <Phone className="h-4 w-4 text-gray-400" />
                        {cliente.telefono}
                      </div>
                      {cliente.email && (
                        <div className="text-sm text-gray-500 flex items-center gap-1 mt-1">
                          <Mail className="h-4 w-4 text-gray-400" />
                          {cliente.email}
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full border ${getTipoColor(cliente.tipo_cliente)}`}>
                        {cliente.tipo_cliente}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900 flex items-center gap-1">
                        <ShoppingBag className="h-4 w-4 text-gray-400" />
                        {cliente.total_pedidos} pedidos
                      </div>
                      <div className="text-sm text-gray-500 flex items-center gap-1 mt-1">
                        <DollarSign className="h-4 w-4 text-gray-400" />
                        ${cliente.total_gastado?.toLocaleString('es-CL') || 0}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-500 max-w-xs truncate">
                        {cliente.notas || '-'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleEditarCliente(cliente)
                        }}
                        className="text-blue-600 hover:text-blue-900 mr-3"
                        title="Editar"
                      >
                        <Edit2 className="h-4 w-4" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleEliminarCliente(cliente)
                        }}
                        className="text-red-600 hover:text-red-900"
                        title="Eliminar"
                        disabled={cliente.total_pedidos > 0}
                      >
                        <Trash2 className={`h-4 w-4 ${cliente.total_pedidos > 0 ? 'opacity-30' : ''}`} />
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

              {/* Dirección */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Dirección Principal
                </label>
                <input
                  type="text"
                  value={formData.direccion_principal}
                  onChange={(e) => setFormData({...formData, direccion_principal: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Av. Apoquindo 1234, Las Condes"
                />
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
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
          onClick={() => setMostrarDetalles(false)}
        >
          <div 
            className="bg-white rounded-lg shadow-xl max-w-5xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="sticky top-0 bg-gradient-to-r from-indigo-600 to-purple-700 text-white px-6 py-5 flex items-center justify-between z-10 shadow-lg rounded-t-lg">
              <div className="flex items-center gap-4">
                <div className="h-16 w-16 bg-white/20 rounded-full flex items-center justify-center text-3xl font-bold">
                  {clienteDetalle.nombre.charAt(0).toUpperCase()}
                </div>
                <div>
                  <h2 className="text-2xl font-bold">{clienteDetalle.nombre}</h2>
                  <p className="text-sm text-indigo-100 mt-1">ID: {clienteDetalle.id}</p>
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
                className="text-white hover:text-indigo-100 transition-colors p-2 hover:bg-white/10 rounded-lg"
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
                  <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-5 rounded-lg border-2 border-blue-200 shadow-sm">
                    <h3 className="text-sm font-bold text-blue-800 uppercase mb-4 flex items-center">
                      <Phone className="h-5 w-5 mr-2" />
                      Información de Contacto
                    </h3>
                    <div className="space-y-3">
                      {clienteDetalle.telefono && (
                        <div>
                          <p className="text-xs text-blue-700 font-semibold uppercase mb-1">Teléfono</p>
                          <p className="text-base font-medium text-blue-900 bg-white p-2 rounded border border-blue-200 flex items-center gap-2">
                            <Phone className="h-4 w-4 text-blue-600" />
                            {clienteDetalle.telefono}
                          </p>
                        </div>
                      )}
                      {clienteDetalle.email && (
                        <div>
                          <p className="text-xs text-blue-700 font-semibold uppercase mb-1">Email</p>
                          <p className="text-base font-medium text-blue-900 bg-white p-2 rounded border border-blue-200 flex items-center gap-2 break-all">
                            <Mail className="h-4 w-4 text-blue-600" />
                            {clienteDetalle.email}
                          </p>
                        </div>
                      )}
                      {clienteDetalle.direccion_principal && (
                        <div>
                          <p className="text-xs text-blue-700 font-semibold uppercase mb-1">Dirección Principal</p>
                          <p className="text-sm font-medium text-blue-900 bg-white p-3 rounded border border-blue-200 flex items-start gap-2">
                            <MapPin className="h-4 w-4 text-blue-600 mt-0.5" />
                            <span>{clienteDetalle.direccion_principal}</span>
                          </p>
                        </div>
                      )}
                      {clienteDetalle.fecha_registro && (
                        <div>
                          <p className="text-xs text-blue-700 font-semibold uppercase mb-1">Cliente desde</p>
                          <p className="text-sm text-blue-800 bg-blue-100 p-2 rounded border border-blue-200 flex items-center gap-2">
                            <Calendar className="h-4 w-4" />
                            {formatFecha(clienteDetalle.fecha_registro)}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                  
                  {/* Notas */}
                  {clienteDetalle.notas && (
                    <div className="bg-yellow-50 p-5 rounded-lg border-2 border-yellow-200 shadow-sm">
                      <h3 className="text-sm font-bold text-yellow-800 uppercase mb-3">
                        📝 Notas
                      </h3>
                      <p className="text-sm text-yellow-900 bg-white p-3 rounded border border-yellow-200">
                        {clienteDetalle.notas}
                      </p>
                    </div>
                  )}
                </div>
                
                {/* Columna Derecha: Estadísticas */}
                <div className="space-y-6">
                  
                  {/* Estadísticas */}
                  <div className="bg-gradient-to-br from-purple-50 to-pink-50 p-5 rounded-lg border-2 border-purple-200 shadow-sm">
                    <h3 className="text-sm font-bold text-purple-800 uppercase mb-4">
                      📊 Estadísticas de Compra
                    </h3>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center p-3 bg-indigo-50 rounded">
                        <span className="text-sm text-indigo-700 font-medium">Total de Pedidos:</span>
                        <span className="text-2xl font-bold text-indigo-900">{clienteDetalle.total_pedidos || 0}</span>
                      </div>
                      <div className="flex justify-between items-center p-3 bg-purple-50 rounded">
                        <span className="text-sm text-purple-700 font-medium">Total Gastado:</span>
                        <span className="text-2xl font-bold text-purple-900">
                          ${(clienteDetalle.total_gastado || 0).toLocaleString('es-CL')}
                        </span>
                      </div>
                      {clienteDetalle.total_pedidos > 0 && (
                        <div className="flex justify-between items-center p-3 bg-pink-50 rounded">
                          <span className="text-sm text-pink-700 font-medium">Ticket Promedio:</span>
                          <span className="text-xl font-bold text-pink-900">
                            ${Math.round((clienteDetalle.total_gastado || 0) / (clienteDetalle.total_pedidos || 1)).toLocaleString('es-CL')}
                          </span>
                        </div>
                      )}
                      {clienteDetalle.ultima_compra && (
                        <div className="text-xs text-purple-600 pt-2 border-t border-purple-200 flex items-center gap-2">
                          <Calendar className="h-4 w-4" />
                          <span>Última compra: {formatFecha(clienteDetalle.ultima_compra)}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Historial de Pedidos */}
              <div className="bg-gradient-to-br from-green-50 to-emerald-50 p-5 rounded-lg border-2 border-green-200 shadow-sm">
                <h3 className="text-sm font-bold text-green-800 uppercase mb-4 flex items-center justify-between">
                  <span className="flex items-center">
                    <ShoppingBag className="h-5 w-5 mr-2" />
                    Historial de Pedidos
                  </span>
                  <span className="text-xs bg-green-100 text-green-800 px-3 py-1 rounded-full">
                    {historialPedidos.length} pedidos
                  </span>
                </h3>
                
                {loadingHistorial ? (
                  <div className="text-center py-8">
                    <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-green-500 border-t-transparent"></div>
                    <p className="text-sm text-green-600 mt-2">Cargando historial...</p>
                  </div>
                ) : historialPedidos.length > 0 ? (
                  <div className="max-h-96 overflow-y-auto space-y-2 custom-scrollbar">
                    {historialPedidos.map((pedido) => (
                      <div 
                        key={pedido.id}
                        className="p-4 rounded-lg border-2 border-green-200 bg-white hover:bg-green-50 transition-all"
                      >
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <span className="text-sm font-bold text-gray-800">Pedido #{pedido.id}</span>
                            <p className="text-xs text-gray-500 mt-1 flex items-center gap-1">
                              <Calendar className="h-3 w-3" />
                              {formatFecha(pedido.fecha_pedido)}
                            </p>
                          </div>
                          <div className="text-right">
                            <span className="text-lg font-bold text-green-600">
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
                          {pedido.arreglo_pedido || 'Sin descripción'}
                        </p>
                        {pedido.fecha_entrega && (
                          <p className="text-xs text-gray-500 mt-1">
                            Entrega: {formatFecha(pedido.fecha_entrega)}
                          </p>
                        )}
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
            <div className="sticky bottom-0 bg-gray-100 px-6 py-4 flex justify-center items-center rounded-b-lg border-t border-gray-200">
              <button
                onClick={() => setMostrarDetalles(false)}
                className="px-8 py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium"
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

