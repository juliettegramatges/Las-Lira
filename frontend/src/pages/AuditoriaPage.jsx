import { useState, useEffect } from 'react'
import axios from 'axios'
import { History, User, Filter, Calendar, Search, RefreshCw, FileText, AlertCircle } from 'lucide-react'
import { API_URL } from '../services/api'
import { formatFecha } from '../utils/helpers'

function AuditoriaPage() {
  const [acciones, setAcciones] = useState([])
  const [loading, setLoading] = useState(true)
  const [usuarios, setUsuarios] = useState([])
  const [filtros, setFiltros] = useState({
    usuario_id: '',
    accion: '',
    entidad: '',
    fecha_desde: '',
    fecha_hasta: ''
  })
  const [paginaActual, setPaginaActual] = useState(1)
  const [totalPaginas, setTotalPaginas] = useState(1)
  const [totalAcciones, setTotalAcciones] = useState(0)
  const limitePorPagina = 50

  useEffect(() => {
    cargarUsuarios()
  }, [])

  useEffect(() => {
    cargarAcciones()
  }, [paginaActual, filtros])

  const cargarUsuarios = async () => {
    try {
      // Usar el endpoint de auth que sabemos que funciona correctamente
      const response = await axios.get(`${API_URL}/auth/usuarios`, {
        withCredentials: true
      })
      if (response.data.success) {
        const usuariosData = response.data.data || []
        console.log('✅ Usuarios cargados:', usuariosData.length, usuariosData)
        setUsuarios(usuariosData)
      } else {
        console.error('❌ Error en respuesta de usuarios:', response.data)
      }
    } catch (err) {
      console.error('❌ Error al cargar usuarios:', err)
      console.error('Detalles:', err.response?.data || err.message)
    }
  }

  const cargarAcciones = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (filtros.usuario_id) params.append('usuario_id', filtros.usuario_id)
      if (filtros.accion) params.append('accion', filtros.accion)
      if (filtros.entidad) params.append('entidad', filtros.entidad)
      if (filtros.fecha_desde) params.append('fecha_desde', filtros.fecha_desde)
      if (filtros.fecha_hasta) params.append('fecha_hasta', filtros.fecha_hasta)
      params.append('page', paginaActual)
      params.append('limit', limitePorPagina)

      const response = await axios.get(`${API_URL}/auditoria/acciones?${params}`, {
        withCredentials: true
      })
      if (response.data.success) {
        setAcciones(response.data.data || [])
        setTotalAcciones(response.data.total || 0)
        setTotalPaginas(response.data.total_pages || 1)
      } else {
        console.error('Error en respuesta de acciones:', response.data)
      }
    } catch (err) {
      console.error('Error al cargar acciones:', err)
      alert('Error al cargar el historial de acciones')
    } finally {
      setLoading(false)
    }
  }

  const handleFiltroChange = (campo, valor) => {
    setFiltros(prev => ({ ...prev, [campo]: valor }))
    setPaginaActual(1)
  }

  const limpiarFiltros = () => {
    setFiltros({
      usuario_id: '',
      accion: '',
      entidad: '',
      fecha_desde: '',
      fecha_hasta: ''
    })
    setPaginaActual(1)
  }

  const getAccionColor = (accion) => {
    const colores = {
      'crear': 'bg-green-100 text-green-800',
      'actualizar': 'bg-blue-100 text-blue-800',
      'eliminar': 'bg-red-100 text-red-800',
      'cambiar_estado': 'bg-purple-100 text-purple-800',
      'cancelar': 'bg-orange-100 text-orange-800'
    }
    return colores[accion] || 'bg-gray-100 text-gray-800'
  }

  const getEntidadIcon = (entidad) => {
    const iconos = {
      'pedido': '📦',
      'cliente': '👤',
      'producto': '🌸',
      'cobranza': '💰',
      'inventario': '📋'
    }
    return iconos[entidad] || '📄'
  }

  const accionesDisponibles = ['crear', 'actualizar', 'eliminar', 'cambiar_estado', 'cancelar']
  const entidadesDisponibles = ['pedido', 'cliente', 'producto', 'cobranza', 'inventario']

  return (
    <div className="p-6">
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <History className="h-8 w-8 text-pink-600" />
          <h1 className="text-3xl font-bold text-gray-900">Historial de Acciones</h1>
        </div>
        <p className="text-gray-600">Registro completo de todas las acciones realizadas por los usuarios</p>
      </div>

      {/* Filtros */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
        <div className="flex items-center gap-2 mb-4">
          <Filter className="h-5 w-5 text-gray-500" />
          <h2 className="text-lg font-semibold text-gray-900">Filtros</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Usuario</label>
            <select
              value={filtros.usuario_id}
              onChange={(e) => handleFiltroChange('usuario_id', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500"
            >
              <option value="">Todos los usuarios</option>
              {usuarios.length > 0 ? (
                usuarios.map(usuario => (
                  <option key={usuario.id} value={usuario.id}>
                    {usuario.nombre} ({usuario.username})
                  </option>
                ))
              ) : (
                <option disabled>Cargando usuarios...</option>
              )}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Acción</label>
            <select
              value={filtros.accion}
              onChange={(e) => handleFiltroChange('accion', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500"
            >
              <option value="">Todas</option>
              {accionesDisponibles.map(accion => (
                <option key={accion} value={accion}>{accion}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Entidad</label>
            <select
              value={filtros.entidad}
              onChange={(e) => handleFiltroChange('entidad', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500"
            >
              <option value="">Todas</option>
              {entidadesDisponibles.map(entidad => (
                <option key={entidad} value={entidad}>{entidad}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Fecha Desde</label>
            <input
              type="date"
              value={filtros.fecha_desde}
              onChange={(e) => handleFiltroChange('fecha_desde', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Fecha Hasta</label>
            <input
              type="date"
              value={filtros.fecha_hasta}
              onChange={(e) => handleFiltroChange('fecha_hasta', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500"
            />
          </div>
        </div>
        <div className="mt-4 flex gap-2">
          <button
            onClick={limpiarFiltros}
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
          >
            Limpiar Filtros
          </button>
          <button
            onClick={cargarAcciones}
            className="px-4 py-2 bg-pink-600 text-white rounded-lg hover:bg-pink-700 transition-colors flex items-center gap-2"
          >
            <RefreshCw className="h-4 w-4" />
            Actualizar
          </button>
        </div>
      </div>

      {/* Tabla de acciones */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <div className="p-4 border-b border-gray-200 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-gray-500" />
            <h2 className="text-lg font-semibold text-gray-900">Acciones Registradas</h2>
          </div>
          <span className="text-sm text-gray-600">Total: {totalAcciones} acciones</span>
        </div>

        {loading ? (
          <div className="p-8 text-center">
            <RefreshCw className="h-8 w-8 animate-spin text-pink-600 mx-auto mb-2" />
            <p className="text-gray-600">Cargando acciones...</p>
          </div>
        ) : acciones.length === 0 ? (
          <div className="p-8 text-center">
            <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-2" />
            <p className="text-gray-600">No se encontraron acciones</p>
          </div>
        ) : (
          <>
            <div className="px-4 py-3 border-b border-gray-200 bg-gray-50">
              <div className="text-sm text-gray-600">
                <strong>{totalAcciones}</strong> movimiento{totalAcciones !== 1 ? 's' : ''} encontrado{totalAcciones !== 1 ? 's' : ''} 
                {totalPaginas > 1 && ` (${limitePorPagina} por página)`}
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fecha/Hora</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Usuario</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Acción</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Entidad</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID Entidad</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Detalles</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {acciones.map((accion) => (
                    <tr key={accion.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                        {formatFecha(accion.fecha_accion, 'dd/MM/yyyy HH:mm', true)}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap">
                        <div className="flex items-center gap-2">
                          <User className="h-4 w-4 text-gray-400" />
                          <span className="text-sm font-medium text-gray-900">{accion.usuario_nombre}</span>
                        </div>
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getAccionColor(accion.accion)}`}>
                          {accion.accion}
                        </span>
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap">
                        <div className="flex items-center gap-2">
                          <span className="text-lg">{getEntidadIcon(accion.entidad)}</span>
                          <span className="text-sm text-gray-900 capitalize">{accion.entidad}</span>
                        </div>
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-600">
                        {accion.entidad_id || '-'}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600 max-w-xs truncate">
                        {accion.detalles ? (
                          <span title={accion.detalles}>{accion.detalles.substring(0, 50)}...</span>
                        ) : '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Paginación */}
            {totalPaginas > 1 && (
              <div className="px-4 py-3 border-t border-gray-200 flex items-center justify-between bg-gray-50">
                <div className="text-sm text-gray-600">
                  Mostrando {acciones.length} de {totalAcciones} movimientos (Página {paginaActual} de {totalPaginas})
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => setPaginaActual(prev => Math.max(1, prev - 1))}
                    disabled={paginaActual === 1}
                    className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-white transition-colors"
                  >
                    ← Anterior
                  </button>
                  <button
                    onClick={() => setPaginaActual(prev => Math.min(totalPaginas, prev + 1))}
                    disabled={paginaActual === totalPaginas}
                    className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-white transition-colors"
                  >
                    Siguiente →
                  </button>
                </div>
              </div>
            )}
            {totalPaginas === 1 && totalAcciones > 0 && (
              <div className="px-4 py-3 border-t border-gray-200 bg-gray-50">
                <div className="text-sm text-gray-600">
                  Mostrando {acciones.length} de {totalAcciones} movimientos
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}

export default AuditoriaPage

