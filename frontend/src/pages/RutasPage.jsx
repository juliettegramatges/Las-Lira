import { useState, useEffect } from 'react'
import axios from 'axios'
import { MapPin, Calendar, Package, TrendingUp, Loader2 } from 'lucide-react'

function RutasPage() {
  const [rutas, setRutas] = useState([])
  const [loading, setLoading] = useState(true)
  const [vistaActual, setVistaActual] = useState('hoy') // 'hoy', 'semana', 'todas'
  
  const cargarRutas = async () => {
    try {
      setLoading(true)
      let endpoint = '/api/rutas/resumen-hoy'
      
      if (vistaActual === 'semana') {
        endpoint = '/api/rutas/por-fecha?dias=7'
      } else if (vistaActual === 'todas') {
        endpoint = '/api/rutas/optimizar'
      }
      
      const response = await axios.get(endpoint)
      
      if (response.data.success) {
        setRutas(vistaActual === 'semana' ? response.data.data : response.data.data)
      }
    } catch (err) {
      console.error('Error al cargar rutas:', err)
    } finally {
      setLoading(false)
    }
  }
  
  useEffect(() => {
    cargarRutas()
  }, [vistaActual])
  
  const getPrecioColor = (precio) => {
    if (precio <= 7000) return 'bg-green-100 text-green-800'
    if (precio <= 15000) return 'bg-blue-100 text-blue-800'
    if (precio <= 25000) return 'bg-yellow-100 text-yellow-800'
    return 'bg-red-100 text-red-800'
  }
  
  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
      </div>
    )
  }
  
  return (
    <div className="px-4 sm:px-0">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Rutas de Despacho</h1>
        <p className="mt-1 text-sm text-gray-600">
          Organiza entregas por comuna para optimizar rutas
        </p>
      </div>
      
      {/* Filtros de vista */}
      <div className="mb-6 flex gap-2">
        <button
          onClick={() => setVistaActual('hoy')}
          className={`px-4 py-2 rounded-lg font-medium ${
            vistaActual === 'hoy'
              ? 'bg-primary-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Hoy
        </button>
        <button
          onClick={() => setVistaActual('semana')}
          className={`px-4 py-2 rounded-lg font-medium ${
            vistaActual === 'semana'
              ? 'bg-primary-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Esta Semana
        </button>
        <button
          onClick={() => setVistaActual('todas')}
          className={`px-4 py-2 rounded-lg font-medium ${
            vistaActual === 'todas'
              ? 'bg-primary-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Todos los Pendientes
        </button>
      </div>
      
      {/* Vista por día (semana) */}
      {vistaActual === 'semana' ? (
        <div className="space-y-6">
          {rutas.map((dia) => (
            <div key={dia.fecha} className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
              <div className="bg-primary-50 px-6 py-4 border-b border-primary-100">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Calendar className="h-5 w-5 text-primary-600" />
                    <h2 className="text-lg font-semibold text-gray-900">
                      {new Date(dia.fecha).toLocaleDateString('es-CL', {
                        weekday: 'long',
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                      })}
                    </h2>
                  </div>
                  <span className="px-3 py-1 bg-primary-100 text-primary-800 rounded-full text-sm font-medium">
                    {dia.total_pedidos} pedido{dia.total_pedidos !== 1 ? 's' : ''}
                  </span>
                </div>
              </div>
              
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {dia.comunas.map((ruta) => (
                    <div
                      key={ruta.comuna}
                      className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <MapPin className="h-5 w-5 text-gray-400" />
                          <h3 className="font-semibold text-gray-900">{ruta.comuna}</h3>
                        </div>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${getPrecioColor(ruta.precio_envio)}`}>
                          ${ruta.precio_envio.toLocaleString('es-CL')}
                        </span>
                      </div>
                      
                      <div className="text-sm text-gray-600">
                        <p className="mb-2 font-medium">{ruta.pedidos.length} pedido{ruta.pedidos.length !== 1 ? 's' : ''}</p>
                        <div className="space-y-1.5">
                          {ruta.pedidos.slice(0, 4).map((pedido) => (
                            <div key={pedido.id} className="text-xs bg-gray-50 p-2 rounded">
                              <div className="font-medium text-gray-900">• {pedido.cliente_nombre}</div>
                              <div className="text-gray-500 mt-0.5">
                                {pedido.arreglo_pedido || 'Sin descripción'}
                              </div>
                              <div className="text-gray-500 mt-0.5 flex items-center gap-1">
                                <span className="font-medium">${(pedido.precio_ramo + pedido.precio_envio).toLocaleString('es-CL')}</span>
                                <span className="text-[10px]">(envío: ${pedido.precio_envio.toLocaleString('es-CL')})</span>
                              </div>
                            </div>
                          ))}
                          {ruta.pedidos.length > 4 && (
                            <div className="text-xs text-gray-500 font-medium pl-2">
                              + {ruta.pedidos.length - 4} pedido{ruta.pedidos.length - 4 !== 1 ? 's' : ''} más
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        /* Vista simple (hoy o todas) */
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Comuna
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Precio Envío
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Cantidad
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Total Envíos
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Clientes
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {rutas.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="px-6 py-8 text-center text-sm text-gray-500">
                      No hay pedidos pendientes para esta selección
                    </td>
                  </tr>
                ) : (
                  rutas.map((ruta) => (
                    <tr key={ruta.comuna} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <MapPin className="h-4 w-4 text-gray-400 mr-2" />
                          <span className="text-sm font-medium text-gray-900">{ruta.comuna}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${getPrecioColor(ruta.precio_envio)}`}>
                          ${ruta.precio_envio?.toLocaleString('es-CL') || 'N/A'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <Package className="h-4 w-4 text-gray-400 mr-2" />
                          <span className="text-sm text-gray-900">
                            {ruta.cantidad || ruta.total_pedidos || ruta.pedidos?.length || 0}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm font-semibold text-gray-900">
                          ${(ruta.total_envios || 0).toLocaleString('es-CL')}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-600">
                          {(ruta.pedidos || []).slice(0, 3).map((pedido, idx) => (
                            <div key={idx} className="mb-1">
                              <div className="font-medium">• {pedido.cliente_nombre}</div>
                              <div className="text-xs text-gray-500 ml-3">
                                {pedido.arreglo_pedido || 'Sin descripción'}
                              </div>
                            </div>
                          ))}
                          {(ruta.pedidos || []).length > 3 && (
                            <div className="text-xs text-gray-500 mt-1 font-medium">
                              + {(ruta.pedidos || []).length - 3} pedido{(ruta.pedidos || []).length - 3 !== 1 ? 's' : ''} más
                            </div>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
      
      {/* Resumen */}
      {rutas.length > 0 && (
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-blue-600" />
            <span className="text-sm font-medium text-blue-900">
              {vistaActual === 'semana' 
                ? `${rutas.reduce((sum, dia) => sum + dia.total_pedidos, 0)} pedidos en total esta semana`
                : `${rutas.reduce((sum, r) => sum + (r.cantidad || r.total_pedidos || r.pedidos?.length || 0), 0)} pedidos en ${rutas.length} comunas diferentes`
              }
            </span>
          </div>
        </div>
      )}
    </div>
  )
}

export default RutasPage

