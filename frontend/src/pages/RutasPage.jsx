import { useState, useEffect } from 'react'
import axios from 'axios'
import { MapPin, Clock, AlertCircle, Check, FileText, Truck, Calendar, Package, Phone, RefreshCw } from 'lucide-react'
import Button from '../components/common/Button'
import { API_URL } from '../services/api'

function RutasPage() {
  const [rutas, setRutas] = useState([])
  const [loading, setLoading] = useState(false)
  const [filtroFecha, setFiltroFecha] = useState('manana')
  const [fechaPersonalizada, setFechaPersonalizada] = useState('')
  const [pedidosSeleccionados, setPedidosSeleccionados] = useState([])
  const [expandidas, setExpandidas] = useState({})

  useEffect(() => {
    cargarRutas()
  }, [filtroFecha])

  const cargarRutas = async () => {
    try {
      setLoading(true)
      const fecha = filtroFecha === 'personalizada' ? fechaPersonalizada : filtroFecha
      const response = await axios.get(`${API_URL}/pedidos/rutas?fecha=${fecha}`)

      if (response.data.success) {
        setRutas(response.data.data)
        const todasExpandidas = {}
        response.data.data.forEach((ruta, idx) => {
          todasExpandidas[idx] = true
        })
        setExpandidas(todasExpandidas)
      }
    } catch (error) {
      console.error('Error al cargar rutas:', error)
      alert('Error al cargar rutas: ' + (error.response?.data?.error || error.message))
    } finally {
      setLoading(false)
    }
  }

  const toggleComuna = (index) => {
    setExpandidas(prev => ({
      ...prev,
      [index]: !prev[index]
    }))
  }

  const toggleSeleccion = (pedidoId) => {
    setPedidosSeleccionados(prev => {
      if (prev.includes(pedidoId)) {
        return prev.filter(id => id !== pedidoId)
      } else {
        return [...prev, pedidoId]
      }
    })
  }

  const toggleSeleccionTodos = (pedidos) => {
    const ids = pedidos.map(p => p.id)
    const todosSeleccionados = ids.every(id => pedidosSeleccionados.includes(id))

    if (todosSeleccionados) {
      setPedidosSeleccionados(prev => prev.filter(id => !ids.includes(id)))
    } else {
      setPedidosSeleccionados(prev => [...new Set([...prev, ...ids])])
    }
  }

  const marcarUrgente = async (pedidoId, esUrgente) => {
    try {
      await axios.patch(`${API_URL}/pedidos/${pedidoId}/urgente`, {
        es_urgente: esUrgente
      })

      cargarRutas()
      alert(`✅ Pedido marcado como ${esUrgente ? 'urgente' : 'normal'}`)
    } catch (error) {
      console.error('Error:', error)
      alert('Error al marcar urgente: ' + (error.response?.data?.error || error.message))
    }
  }

  const marcarDespachados = async () => {
    if (pedidosSeleccionados.length === 0) {
      alert('❌ Selecciona al menos un pedido')
      return
    }

    if (!confirm(`¿Marcar ${pedidosSeleccionados.length} pedido(s) como despachados?`)) {
      return
    }

    try {
      const response = await axios.post(`${API_URL}/pedidos/marcar-despachados`, {
        pedidos_ids: pedidosSeleccionados
      })

      if (response.data.success) {
        alert(`✅ ${response.data.data.actualizados} pedidos marcados como despachados`)
        setPedidosSeleccionados([])
        cargarRutas()
      }
    } catch (error) {
      console.error('Error:', error)
      alert('Error al marcar despachados: ' + (error.response?.data?.error || error.message))
    }
  }

  const abrirDocumentoRepartidor = () => {
    const fecha = filtroFecha === 'personalizada' ? fechaPersonalizada : filtroFecha
    window.open(`${API_URL}/pedidos/documento-repartidor?fecha=${fecha}&formato=html`, '_blank')
  }

  const totalPedidos = rutas.reduce((sum, ruta) => sum + ruta.total_pedidos, 0)
  const totalUrgentes = rutas.reduce((sum, ruta) => sum + ruta.urgentes, 0)

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
          <Truck className="h-8 w-8 text-blue-600" />
          Planificación de Rutas
        </h1>
        <p className="text-gray-600 mt-1">Organiza y optimiza las entregas por comuna</p>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              Fecha de Entrega
            </label>
            <div className="flex gap-2">
              <select
                value={filtroFecha}
                onChange={(e) => setFiltroFecha(e.target.value)}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="hoy">Hoy</option>
                <option value="manana">Mañana</option>
                <option value="personalizada">Otra fecha...</option>
              </select>

              {filtroFecha === 'personalizada' && (
                <input
                  type="date"
                  value={fechaPersonalizada}
                  onChange={(e) => setFechaPersonalizada(e.target.value)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              )}
            </div>
          </div>

          <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
            <p className="text-xs text-blue-600 font-medium mb-1">Total Pedidos</p>
            <p className="text-2xl font-bold text-blue-700">{totalPedidos}</p>
          </div>

          <div className="bg-red-50 rounded-lg p-4 border border-red-200">
            <p className="text-xs text-red-600 font-medium mb-1">Urgentes</p>
            <p className="text-2xl font-bold text-red-700">{totalUrgentes}</p>
          </div>
        </div>

        <div className="flex flex-wrap gap-3 mt-4 pt-4 border-t border-gray-200">
          <Button
            onClick={marcarDespachados}
            disabled={pedidosSeleccionados.length === 0}
            variant="success"
            icon={Check}
          >
            Marcar como Despachados ({pedidosSeleccionados.length})
          </Button>

          <Button
            onClick={abrirDocumentoRepartidor}
            variant="info"
            icon={FileText}
          >
            Generar Documento Repartidor
          </Button>

          <Button
            onClick={cargarRutas}
            variant="gray"
            icon={RefreshCw}
          >
            Actualizar
          </Button>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-gray-600 mt-4">Cargando rutas...</p>
        </div>
      ) : rutas.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow-md">
          <Package className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 text-lg">No hay pedidos para esta fecha</p>
        </div>
      ) : (
        <div className="space-y-4">
          {rutas.map((ruta, rutaIndex) => (
            <div key={rutaIndex} className="bg-white rounded-lg shadow-md overflow-hidden">
              <div
                className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-4 cursor-pointer hover:from-blue-700 hover:to-blue-800 transition-colors"
                onClick={() => toggleComuna(rutaIndex)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <MapPin className="h-6 w-6" />
                    <h3 className="text-xl font-bold">{ruta.comuna}</h3>
                  </div>

                  <div className="flex items-center gap-4">
                    {ruta.urgentes > 0 && (
                      <span className="bg-red-500 text-white px-3 py-1 rounded-full text-sm font-semibold flex items-center gap-1">
                        <AlertCircle className="h-4 w-4" />
                        {ruta.urgentes} urgente(s)
                      </span>
                    )}

                    <span className="bg-white/20 px-4 py-1 rounded-full font-semibold">
                      {ruta.total_pedidos} pedido(s)
                    </span>

                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        toggleSeleccionTodos(ruta.pedidos)
                      }}
                      className="px-3 py-1 bg-white/20 hover:bg-white/30 rounded-lg text-sm font-medium transition-colors"
                    >
                      {ruta.pedidos.every(p => pedidosSeleccionados.includes(p.id))
                        ? '☑ Deseleccionar todos'
                        : '☐ Seleccionar todos'}
                    </button>

                    <span className="text-2xl">{expandidas[rutaIndex] ? '▼' : '▶'}</span>
                  </div>
                </div>
              </div>

              {expandidas[rutaIndex] && (
                <div className="divide-y divide-gray-200">
                  {ruta.pedidos.map((pedido) => (
                    <div
                      key={pedido.id}
                      className={`p-4 hover:bg-gray-50 transition-colors ${
                        pedido.es_urgente ? 'bg-red-50 border-l-4 border-red-500' : ''
                      } ${
                        pedidosSeleccionados.includes(pedido.id) ? 'bg-blue-50' : ''
                      }`}
                    >
                      <div className="flex items-start gap-4">
                        <input
                          type="checkbox"
                          checked={pedidosSeleccionados.includes(pedido.id)}
                          onChange={() => toggleSeleccion(pedido.id)}
                          className="mt-1 h-5 w-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />

                        <div className="flex-shrink-0">
                          <div className="text-lg font-bold text-blue-600">#{pedido.id}</div>
                        </div>

                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            {pedido.es_urgente && (
                              <span className="bg-red-500 text-white px-2 py-1 rounded text-xs font-bold">
                                🚨 URGENTE
                              </span>
                            )}

                            {pedido.motivo && (
                              <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded text-xs font-semibold">
                                {pedido.motivo}
                              </span>
                            )}

                            <span className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs font-medium">
                              {pedido.estado}
                            </span>
                          </div>

                          <p className="font-semibold text-gray-900 mb-1">{pedido.cliente_nombre}</p>

                          <div className="grid grid-cols-2 gap-2 text-sm text-gray-600">
                            <div className="flex items-center gap-2">
                              <MapPin className="h-4 w-4 text-gray-400" />
                              {pedido.direccion}
                            </div>

                            <div className="flex items-center gap-2">
                              <Phone className="h-4 w-4 text-gray-400" />
                              {pedido.telefono}
                            </div>
                          </div>

                          {pedido.destinatario && (
                            <p className="text-sm text-gray-600 mt-1">
                              👤 Para: <span className="font-medium">{pedido.destinatario}</span>
                            </p>
                          )}

                          {pedido.arreglo && (
                            <p className="text-sm text-gray-600 mt-1">
                              🌸 {pedido.arreglo}
                            </p>
                          )}

                          {pedido.foto_respaldo && (
                            <div className="mt-2">
                              <img
                                src={`${API_URL}/upload/imagen/${pedido.foto_respaldo}`}
                                alt="Foto de respaldo"
                                className="max-w-[150px] max-h-[150px] rounded-lg border-2 border-gray-200 object-cover"
                              />
                            </div>
                          )}
                        </div>

                        <div className="flex-shrink-0 text-right">
                          <div className="flex items-center gap-2 text-blue-600 font-bold text-lg mb-2">
                            <Clock className="h-5 w-5" />
                            {pedido.hora_llegada}
                          </div>

                          <button
                            onClick={() => marcarUrgente(pedido.id, !pedido.es_urgente)}
                            className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                              pedido.es_urgente
                                ? 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                                : 'bg-red-100 text-red-700 hover:bg-red-200'
                            }`}
                          >
                            {pedido.es_urgente ? '🔽 Normal' : '🔺 Urgente'}
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default RutasPage
