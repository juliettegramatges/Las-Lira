import { useState, useEffect } from 'react'
import { Wrench, Package, CheckCircle, AlertCircle, Edit, Image as ImageIcon } from 'lucide-react'
import { pedidoInsumosAPI, inventarioAPI, productosAPI, API_URL } from '../services/api'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'

function TallerPage() {
  const [pedidos, setPedidos] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [pedidoSeleccionado, setPedidoSeleccionado] = useState(null)
  const [insumos, setInsumos] = useState([])
  const [loadingInsumos, setLoadingInsumos] = useState(false)
  const [confirmando, setConfirmando] = useState(false)

  useEffect(() => {
    cargarPedidosTaller()
  }, [])

  const cargarPedidosTaller = async () => {
    try {
      setLoading(true)
      const response = await pedidoInsumosAPI.obtenerPedidosTaller()
      setPedidos(response.data)
    } catch (err) {
      console.error('Error al cargar pedidos del taller:', err)
      setError('Error al cargar los pedidos')
    } finally {
      setLoading(false)
    }
  }

  const handleVerInsumos = async (pedido) => {
    try {
      setLoadingInsumos(true)
      setPedidoSeleccionado(pedido)
      
      const response = await pedidoInsumosAPI.obtenerInsumos(pedido.id)
      setInsumos(response.data.insumos || [])
    } catch (err) {
      console.error('Error al cargar insumos:', err)
      alert('Error al cargar los insumos del pedido')
    } finally {
      setLoadingInsumos(false)
    }
  }

  const handleConfirmarInsumos = async () => {
    if (!pedidoSeleccionado) return
    
    if (!confirm(`¿Confirmar insumos y descontar stock para el pedido ${pedidoSeleccionado.id}?\n\nEsto moverá el pedido a "Listo para Despacho" y descontará el inventario.`)) {
      return
    }

    try {
      setConfirmando(true)
      const response = await pedidoInsumosAPI.confirmarYDescontar(pedidoSeleccionado.id)
      
      alert(`✅ ${response.data.message}\n\n${response.data.insumos_procesados} insumos procesados`)
      
      // Recargar lista y cerrar modal
      await cargarPedidosTaller()
      setPedidoSeleccionado(null)
      setInsumos([])
    } catch (err) {
      console.error('Error al confirmar insumos:', err)
      const errorMsg = err.response?.data?.detalles 
        ? `❌ Error:\n\n${err.response.data.detalles.join('\n')}`
        : `❌ Error: ${err.response?.data?.error || err.message}`
      alert(errorMsg)
    } finally {
      setConfirmando(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Cargando pedidos del taller...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-red-500">{error}</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Wrench className="h-7 w-7 text-primary-600" />
            Taller
          </h1>
          <p className="text-gray-600 mt-1">
            Pedidos en proceso - Confirma insumos antes de despachar
          </p>
        </div>
        <div className="bg-primary-50 px-4 py-2 rounded-lg">
          <span className="text-primary-900 font-semibold">{pedidos.length}</span>
          <span className="text-primary-700 ml-1">en proceso</span>
        </div>
      </div>

      {/* Lista de pedidos */}
      {pedidos.length === 0 ? (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
          <Package className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 text-lg">No hay pedidos en proceso</p>
          <p className="text-gray-400 text-sm mt-2">
            Los pedidos aparecerán aquí cuando estén listos para trabajar
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {pedidos.map((pedido) => (
            <div
              key={pedido.id}
              className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow"
            >
              {/* Imagen del producto */}
              {pedido.producto_imagen && (
                <div className="h-32 bg-gradient-to-br from-primary-100 to-primary-200 flex items-center justify-center">
                  <img
                    src={pedido.producto_imagen.startsWith('http') ? pedido.producto_imagen : `${API_URL}/upload/imagen/${pedido.producto_imagen}`}
                    alt={pedido.producto_nombre}
                    className="w-full h-full object-contain p-2"
                  />
                </div>
              )}

              <div className="p-4">
                {/* Header */}
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="font-semibold text-gray-900">{pedido.cliente_nombre}</h3>
                    <p className="text-xs text-gray-500 font-mono">{pedido.id}</p>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    pedido.tiene_insumos 
                      ? 'bg-green-100 text-green-700' 
                      : 'bg-yellow-100 text-yellow-700'
                  }`}>
                    {pedido.tiene_insumos ? '✓ Con insumos' : '⚠ Sin insumos'}
                  </span>
                </div>

                {/* Producto */}
                {pedido.producto_nombre && (
                  <p className="text-sm text-gray-700 mb-2">
                    📦 {pedido.producto_nombre}
                  </p>
                )}

                {/* Fecha de entrega */}
                {pedido.fecha_entrega && (
                  <p className="text-sm text-gray-600 mb-3">
                    📅 {format(new Date(pedido.fecha_entrega), "d 'de' MMMM", { locale: es })}
                  </p>
                )}

                {/* Precio */}
                <div className="text-lg font-bold text-primary-600 mb-3">
                  ${(pedido.precio_ramo || 0).toLocaleString()}
                </div>

                {/* Botón de acción */}
                <button
                  onClick={() => handleVerInsumos(pedido)}
                  className="w-full bg-primary-600 text-white py-2 px-4 rounded-lg hover:bg-primary-700 transition-colors flex items-center justify-center gap-2"
                >
                  <Edit className="h-4 w-4" />
                  {pedido.tiene_insumos ? 'Ver/Confirmar Insumos' : 'Definir Insumos'}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal de insumos */}
      {pedidoSeleccionado && (
        <div
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
          onClick={() => setPedidoSeleccionado(null)}
        >
          <div
            className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="bg-primary-600 text-white px-6 py-4">
              <h2 className="text-xl font-bold">
                Insumos - {pedidoSeleccionado.producto_nombre || pedidoSeleccionado.cliente_nombre}
              </h2>
              <p className="text-primary-100 text-sm">{pedidoSeleccionado.id}</p>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-6">
              {loadingInsumos ? (
                <div className="text-center py-12">
                  <div className="text-gray-500">Cargando insumos...</div>
                </div>
              ) : insumos.length === 0 ? (
                <div className="text-center py-12">
                  <AlertCircle className="h-16 w-16 text-yellow-400 mx-auto mb-4" />
                  <p className="text-gray-600">Este pedido aún no tiene insumos definidos</p>
                  <p className="text-gray-400 text-sm mt-2">
                    Los insumos se definen al crear el pedido
                  </p>
                </div>
              ) : (
                <div className="space-y-6">
                  {/* Tabla de insumos */}
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                            Insumo
                          </th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                            Tipo
                          </th>
                          <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                            Cantidad
                          </th>
                          <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                            Stock Disp.
                          </th>
                          <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                            Costo Unit.
                          </th>
                          <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                            Total
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {insumos.map((insumo) => {
                          const stockSuficiente = insumo.stock_disponible >= insumo.cantidad
                          return (
                            <tr key={insumo.id} className={!stockSuficiente ? 'bg-red-50' : ''}>
                              <td className="px-4 py-3">
                                <div className="flex items-center gap-2">
                                  {insumo.insumo_foto ? (
                                    <img
                                      src={`${API_URL}/upload/imagen/${insumo.insumo_foto}`}
                                      alt={insumo.insumo_nombre}
                                      className="w-10 h-10 rounded object-cover"
                                      onError={(e) => {
                                        e.target.style.display = 'none'
                                      }}
                                    />
                                  ) : (
                                    <div className="w-10 h-10 bg-gray-200 rounded flex items-center justify-center">
                                      <ImageIcon className="h-5 w-5 text-gray-400" />
                                    </div>
                                  )}
                                  <div>
                                    <div className="font-medium text-gray-900">
                                      {insumo.insumo_nombre}
                                    </div>
                                    {insumo.insumo_color && (
                                      <div className="text-xs text-gray-500">{insumo.insumo_color}</div>
                                    )}
                                  </div>
                                </div>
                              </td>
                              <td className="px-4 py-3">
                                <span className={`px-2 py-1 rounded text-xs font-medium ${
                                  insumo.insumo_tipo === 'Flor' 
                                    ? 'bg-green-100 text-green-700' 
                                    : 'bg-blue-100 text-blue-700'
                                }`}>
                                  {insumo.insumo_tipo}
                                </span>
                              </td>
                              <td className="px-4 py-3 text-right font-medium">
                                {insumo.cantidad}
                              </td>
                              <td className={`px-4 py-3 text-right ${!stockSuficiente ? 'text-red-600 font-bold' : 'text-gray-600'}`}>
                                {insumo.stock_disponible || 0}
                                {!stockSuficiente && ' ⚠️'}
                              </td>
                              <td className="px-4 py-3 text-right text-gray-600">
                                ${insumo.costo_unitario.toLocaleString()}
                              </td>
                              <td className="px-4 py-3 text-right font-medium text-gray-900">
                                ${insumo.costo_total.toLocaleString()}
                              </td>
                            </tr>
                          )
                        })}
                      </tbody>
                      <tfoot className="bg-gray-50">
                        <tr>
                          <td colSpan="5" className="px-4 py-3 text-right font-semibold text-gray-700">
                            Total Insumos:
                          </td>
                          <td className="px-4 py-3 text-right font-bold text-primary-600 text-lg">
                            ${insumos.reduce((sum, i) => sum + i.costo_total, 0).toLocaleString()}
                          </td>
                        </tr>
                      </tfoot>
                    </table>
                  </div>

                  {/* Alertas */}
                  {insumos.some(i => i.stock_disponible < i.cantidad) && (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                      <div className="flex items-start gap-3">
                        <AlertCircle className="h-5 w-5 text-red-600 mt-0.5" />
                        <div>
                          <h3 className="font-semibold text-red-900">Stock insuficiente</h3>
                          <p className="text-red-700 text-sm mt-1">
                            Algunos insumos no tienen stock suficiente. Debes reponer inventario antes de confirmar este pedido.
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="border-t border-gray-200 px-6 py-4 bg-gray-50 flex justify-end gap-3">
              <button
                onClick={() => setPedidoSeleccionado(null)}
                className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors"
              >
                Cerrar
              </button>
              {insumos.length > 0 && (
                <button
                  onClick={handleConfirmarInsumos}
                  disabled={confirmando || insumos.some(i => i.stock_disponible < i.cantidad)}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  <CheckCircle className="h-4 w-4" />
                  {confirmando ? 'Confirmando...' : 'Confirmar y Descontar Stock'}
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default TallerPage

