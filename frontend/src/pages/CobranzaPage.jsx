import { useState, useEffect } from 'react'
import axios from 'axios'
import { DollarSign, FileText, AlertCircle, CheckCircle } from 'lucide-react'
import { API_URL } from '../services/api'

const CobranzaPage = () => {
  const [loading, setLoading] = useState(true)
  const [resumen, setResumen] = useState(null)
  const [editandoPedido, setEditandoPedido] = useState(null)
  
  // Catálogos de opciones estandarizadas (3 ETAPAS)
  
  // ETAPA 1: ¿Está pagado?
  const ESTADOS_PAGO = ['No Pagado', 'Pagado']
  
  // ETAPA 2: ¿Cómo pagó? (solo si está pagado)
  const METODOS_PAGO = [
    'Tr. BICE',
    'Tr. Santander',
    'Tr. Itaú',
    'Pago con tarjeta',
    'Efectivo',
    'Otro',
  ]
  
  // ETAPA 3: Documento
  const DOCUMENTOS = [
    'Hacer boleta',
    'Hacer factura',
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
        // Actualizar el pedido en el estado local
        if (editandoPedido) {
          setEditandoPedido(response.data.data)
        }
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

  const calcularDiasFaltantes = (fechaMaximaPago) => {
    if (!fechaMaximaPago) return null
    
    const hoy = new Date()
    const fechaLimite = new Date(fechaMaximaPago)
    const diferencia = Math.ceil((fechaLimite - hoy) / (1000 * 60 * 60 * 24))
    
    return diferencia
  }

  const formatearFecha = (fecha) => {
    if (!fecha) return null
    const date = new Date(fecha)
    return date.toLocaleDateString('es-CL', { day: '2-digit', month: '2-digit', year: 'numeric' })
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
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">📅 Plazo Pago</th>
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
                  <td className="px-6 py-4">
                    {pedido.fecha_maxima_pago ? (
                      <>
                        <div className="text-sm font-medium text-gray-900">
                          {formatearFecha(pedido.fecha_maxima_pago)}
                        </div>
                        {(() => {
                          const dias = calcularDiasFaltantes(pedido.fecha_maxima_pago)
                          if (dias < 0) {
                            return (
                              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
                                ⚠️ Vencido hace {Math.abs(dias)} días
                              </span>
                            )
                          } else if (dias === 0) {
                            return (
                              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-orange-100 text-orange-800">
                                ⏰ Vence hoy
                              </span>
                            )
                          } else if (dias <= 3) {
                            return (
                              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800">
                                ⚠️ {dias} días restantes
                              </span>
                            )
                          } else {
                            return (
                              <span className="text-xs text-gray-500">
                                ✅ {dias} días restantes
                              </span>
                            )
                          }
                        })()}
                      </>
                    ) : (
                      <span className="text-sm text-gray-400">Pago inmediato</span>
                    )}
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
                  <td colSpan="7" className="px-6 py-8 text-center text-gray-500">
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

      {/* Modal de Edición - 3 ETAPAS */}
      {editandoPedido && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-2">
              Actualizar Cobranza - {editandoPedido.id}
            </h3>
            <p className="text-sm text-gray-500 mb-6">{editandoPedido.cliente_nombre}</p>
            
            <div className="space-y-6">
              {/* ETAPA 1: ¿Está Pagado? */}
              <div className="border-2 border-gray-200 rounded-lg p-4">
                <label className="block text-sm font-bold text-gray-900 mb-3">
                  💰 ETAPA 1: ¿Está Pagado?
                </label>
                <div className="flex gap-3">
                  {ESTADOS_PAGO.map(estado => (
                    <button
                      key={estado}
                      onClick={() => actualizarCobranza(editandoPedido.id, { estado_pago: estado })}
                      className={`flex-1 py-2 px-4 rounded-lg font-medium transition-colors ${
                        editandoPedido.estado_pago === estado
                          ? estado === 'Pagado'
                            ? 'bg-green-600 text-white'
                            : 'bg-red-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {estado === 'Pagado' ? '✅' : '❌'} {estado}
                    </button>
                  ))}
                </div>
              </div>

              {/* ETAPA 2: Método de Pago (solo si está pagado) */}
              <div className={`border-2 rounded-lg p-4 transition-opacity ${
                editandoPedido.estado_pago === 'Pagado' 
                  ? 'border-green-200 bg-green-50' 
                  : 'border-gray-200 bg-gray-50 opacity-50 pointer-events-none'
              }`}>
                <label className="block text-sm font-bold text-gray-900 mb-3">
                  💳 ETAPA 2: ¿Cómo Pagó?
                  {editandoPedido.estado_pago !== 'Pagado' && (
                    <span className="ml-2 text-xs font-normal text-gray-500">(Primero marcar como pagado)</span>
                  )}
                </label>
                <select
                  value={editandoPedido.metodo_pago || ''}
                  onChange={(e) => actualizarCobranza(editandoPedido.id, { metodo_pago: e.target.value })}
                  disabled={editandoPedido.estado_pago !== 'Pagado'}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  <option value="">Seleccionar método...</option>
                  {METODOS_PAGO.map(metodo => (
                    <option key={metodo} value={metodo}>{metodo}</option>
                  ))}
                </select>
              </div>

              {/* ETAPA 3: Documento Tributario */}
              <div className="border-2 border-blue-200 rounded-lg p-4 bg-blue-50">
                <label className="block text-sm font-bold text-gray-900 mb-3">
                  🧾 ETAPA 3: Documento Tributario
                </label>
                
                {/* Tipo de Documento */}
                <select
                  value={editandoPedido.documento_tributario || 'Hacer boleta'}
                  onChange={(e) => actualizarCobranza(editandoPedido.id, { documento_tributario: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 mb-3"
                >
                  {DOCUMENTOS.map(doc => (
                    <option key={doc} value={doc}>{doc}</option>
                  ))}
                </select>

                {/* Número de Documento */}
                {(editandoPedido.documento_tributario === 'Boleta emitida' || 
                  editandoPedido.documento_tributario === 'Factura emitida' ||
                  editandoPedido.documento_tributario === 'Hacer boleta' ||
                  editandoPedido.documento_tributario === 'Hacer factura') && (
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">
                      Número de Documento
                    </label>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={editandoPedido.numero_documento || ''}
                        onChange={(e) => {
                          setEditandoPedido({...editandoPedido, numero_documento: e.target.value})
                        }}
                        placeholder="Ej: 10301"
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                      <button
                        onClick={() => actualizarCobranza(editandoPedido.id, { numero_documento: editandoPedido.numero_documento })}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
                      >
                        💾 Guardar
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>

            <div className="mt-6 flex justify-end gap-2">
              <button
                onClick={() => setEditandoPedido(null)}
                className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 font-medium"
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

