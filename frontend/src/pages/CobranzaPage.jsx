import { useState, useEffect } from 'react'
import axios from 'axios'
import { DollarSign, FileText, AlertCircle, CheckCircle } from 'lucide-react'
import { API_URL } from '../services/api'

const CobranzaPage = () => {
  const [loading, setLoading] = useState(true)
  const [resumen, setResumen] = useState(null)
  const [editandoPedido, setEditandoPedido] = useState(null)
  
  // Catálogos de opciones estandarizadas
  const METODOS_PAGO = [
    'Pendiente',
    'Tr. BICE',
    'Tr. Santander',
    'Tr. Itaú',
    'Tr. Falta transferencia',
    'Pago confirmado',
    'Pago con tarjeta',
  ]
  
  const DOCUMENTOS = [
    'Hacer boleta',
    'Hacer factura',
    'Falta boleta o factura',
    'Boleta emitida',
    'Factura emitida',
    'No requiere',
  ]

  useEffect(() => {
    cargarResumen()
  }, [])

  const cargarResumen = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`${API_URL}/pedidos/resumen-cobranza`)
      if (response.data.success) {
        setResumen(response.data.data)
      }
    } catch (err) {
      console.error('Error al cargar resumen:', err)
    } finally {
      setLoading(false)
    }
  }

  const actualizarCobranza = async (pedidoId, datos) => {
    try {
      const response = await axios.patch(`${API_URL}/pedidos/${pedidoId}/cobranza`, datos)
      if (response.data.success) {
        alert('✅ Cobranza actualizada exitosamente')
        setEditandoPedido(null)
        cargarResumen()
      }
    } catch (err) {
      console.error('Error al actualizar:', err)
      alert('❌ Error al actualizar cobranza')
    }
  }

  const getIconoPago = (metodo) => {
    if (metodo === 'Pago confirmado' || metodo === 'Pago con tarjeta') {
      return <CheckCircle className="h-4 w-4 text-green-600" />
    }
    return <AlertCircle className="h-4 w-4 text-orange-600" />
  }

  if (loading) {
    return <div className="p-6">Cargando...</div>
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">💰 Cobranza</h1>

      {/* Resumen */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="bg-red-50 border-2 border-red-200 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-red-600 font-medium">Pedidos sin Pagar</p>
              <p className="text-3xl font-bold text-red-700">{resumen?.sin_pagar?.cantidad || 0}</p>
              <p className="text-sm text-red-600 mt-2">Total: ${resumen?.sin_pagar?.total?.toLocaleString('es-CL') || 0}</p>
            </div>
            <DollarSign className="h-12 w-12 text-red-400" />
          </div>
        </div>

        <div className="bg-yellow-50 border-2 border-yellow-200 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-yellow-600 font-medium">Sin Documentar</p>
              <p className="text-3xl font-bold text-yellow-700">{resumen?.sin_documentar?.cantidad || 0}</p>
              <p className="text-sm text-yellow-600 mt-2">Boletas/Facturas pendientes</p>
            </div>
            <FileText className="h-12 w-12 text-yellow-400" />
          </div>
        </div>
      </div>

      {/* Tabla de Pedidos sin Pagar */}
      <div className="bg-white rounded-lg shadow-md mb-8">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">🚨 Pendientes de Pago</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Pedido</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Cliente</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">💰 Pago</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">🧾 Documento</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {resumen?.sin_pagar?.pedidos?.map((pedido) => (
                <tr key={pedido.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{pedido.id}</div>
                    <div className="text-xs text-gray-500">{pedido.arreglo_pedido}</div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900">{pedido.cliente_nombre}</div>
                    <div className="text-xs text-gray-500">{pedido.cliente_telefono}</div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      {getIconoPago(pedido.metodo_pago)}
                      <span className="text-sm">{pedido.metodo_pago}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-sm">
                      {pedido.documento_tributario === 'Boleta emitida' && pedido.numero_documento 
                        ? `Boleta N° ${pedido.numero_documento}`
                        : pedido.documento_tributario === 'Factura emitida' && pedido.numero_documento
                        ? `Factura N° ${pedido.numero_documento}`
                        : pedido.documento_tributario}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-semibold text-gray-900">
                      ${pedido.precio_total?.toLocaleString('es-CL')}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <button
                      onClick={() => setEditandoPedido(pedido)}
                      className="text-primary-600 hover:text-primary-900 text-sm font-medium"
                    >
                      Actualizar
                    </button>
                  </td>
                </tr>
              ))}
              {(!resumen?.sin_pagar?.pedidos || resumen.sin_pagar.pedidos.length === 0) && (
                <tr>
                  <td colSpan="6" className="px-6 py-8 text-center text-gray-500">
                    ✅ No hay pedidos pendientes de pago
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Tabla de Pedidos sin Documentar */}
      <div className="bg-white rounded-lg shadow-md">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">📋 Pendientes de Documentar</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Pedido</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Cliente</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">🧾 Estado Documento</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">N° Documento</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {resumen?.sin_documentar?.pedidos?.map((pedido) => (
                <tr key={pedido.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{pedido.id}</div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900">{pedido.cliente_nombre}</div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                      pedido.documento_tributario === 'Hacer boleta' ? 'bg-yellow-100 text-yellow-800' :
                      pedido.documento_tributario === 'Hacer factura' ? 'bg-yellow-100 text-yellow-800' :
                      pedido.documento_tributario === 'Falta boleta o factura' ? 'bg-red-100 text-red-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {pedido.documento_tributario}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-sm">{pedido.numero_documento || '-'}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <button
                      onClick={() => setEditandoPedido(pedido)}
                      className="text-primary-600 hover:text-primary-900 text-sm font-medium"
                    >
                      Actualizar
                    </button>
                  </td>
                </tr>
              ))}
              {(!resumen?.sin_documentar?.pedidos || resumen.sin_documentar.pedidos.length === 0) && (
                <tr>
                  <td colSpan="5" className="px-6 py-8 text-center text-gray-500">
                    ✅ Todos los pedidos están documentados
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal de Edición */}
      {editandoPedido && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">
              Actualizar Cobranza - {editandoPedido.id}
            </h3>
            
            <div className="space-y-4">
              {/* Método de Pago */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  💰 Método de Pago
                </label>
                <select
                  defaultValue={editandoPedido.metodo_pago}
                  onChange={(e) => actualizarCobranza(editandoPedido.id, { metodo_pago: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  {METODOS_PAGO.map(metodo => (
                    <option key={metodo} value={metodo}>{metodo}</option>
                  ))}
                </select>
              </div>

              {/* Documento Tributario */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  🧾 Documento Tributario
                </label>
                <select
                  defaultValue={editandoPedido.documento_tributario}
                  onChange={(e) => actualizarCobranza(editandoPedido.id, { documento_tributario: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  {DOCUMENTOS.map(doc => (
                    <option key={doc} value={doc}>{doc}</option>
                  ))}
                </select>
              </div>

              {/* Número de Documento */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  N° Documento
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    defaultValue={editandoPedido.numero_documento || ''}
                    placeholder="Ej: 10301"
                    id="numero_doc_input"
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                  <button
                    onClick={() => {
                      const numero = document.getElementById('numero_doc_input').value
                      actualizarCobranza(editandoPedido.id, { numero_documento: numero })
                    }}
                    className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                  >
                    Guardar
                  </button>
                </div>
              </div>
            </div>

            <div className="mt-6 flex justify-end">
              <button
                onClick={() => setEditandoPedido(null)}
                className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
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

export default CobranzaPage

