import { useState, useEffect } from 'react'
import axios from 'axios'
import { DollarSign, FileText, AlertCircle, CheckCircle, X, Package, User, MapPin, Calendar, Phone, Mail } from 'lucide-react'
import { API_URL } from '../services/api'
import { formatFecha } from '../utils/helpers'

const CobranzaPage = () => {
  const [loading, setLoading] = useState(true)
  const [resumen, setResumen] = useState(null)
  const [editandoPedido, setEditandoPedido] = useState(null)
  
  // Pagados (lista inferior)
  const [pagados, setPagados] = useState([])
  const [loadingPagados, setLoadingPagados] = useState(false)
  const [busquedaPagados, setBusquedaPagados] = useState('')
  const [paginaPagados, setPaginaPagados] = useState(1)
  const [totalPaginasPagados, setTotalPaginasPagados] = useState(1)
  const limitePagados = 50
  
  // Estados para modal de detalle
  const [pedidoDetalle, setPedidoDetalle] = useState(null)
  const [clienteDetalle, setClienteDetalle] = useState(null)
  const [historialCliente, setHistorialCliente] = useState([])
  const [loadingCliente, setLoadingCliente] = useState(false)
  
  // Estados para paginación
  const [paginaPagos, setPaginaPagos] = useState(1)
  const [paginaDocumentos, setPaginaDocumentos] = useState(1)
  const itemsPorPagina = 10
  
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

  useEffect(() => {
    cargarPagados()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [paginaPagados])

  // Debounce búsqueda pagados
  useEffect(() => {
    const t = setTimeout(() => {
      setPaginaPagados(1)
      cargarPagados()
    }, 300)
    return () => clearTimeout(t)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [busquedaPagados])

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

  const cargarPagados = async () => {
    try {
      setLoadingPagados(true)
      const params = new URLSearchParams()
      if (busquedaPagados && busquedaPagados.trim()) params.append('buscar', busquedaPagados.trim())
      params.append('page', paginaPagados)
      params.append('limit', limitePagados)
      const response = await axios.get(`${API_URL}/pedidos/pagados?${params}`)
      if (response.data.success) {
        setPagados(response.data.data || [])
        setTotalPaginasPagados(response.data.total_pages || 1)
      }
    } catch (err) {
      console.error('Error al cargar pagados:', err)
    } finally {
      setLoadingPagados(false)
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

  const cargarInfoCliente = async (clienteId) => {
    try {
      setLoadingCliente(true)
      const [detalleResponse, historialResponse] = await Promise.all([
        axios.get(`${API_URL}/clientes/${clienteId}`),
        axios.get(`${API_URL}/clientes/${clienteId}/pedidos`)
      ])
      
      if (detalleResponse.data.success) {
        setClienteDetalle(detalleResponse.data.data)
      }
      
      if (historialResponse.data.success) {
        setHistorialCliente(historialResponse.data.data.pedidos || [])
      }
    } catch (err) {
      console.error('Error al cargar info del cliente:', err)
    } finally {
      setLoadingCliente(false)
    }
  }

  const handleAbrirPedido = (pedido) => {
    setPedidoDetalle(pedido)
    setClienteDetalle(null)
    setHistorialCliente([])
    
    if (pedido.cliente_id) {
      cargarInfoCliente(pedido.cliente_id)
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

  // Calcular datos para paginación
  const pedidosSinPagar = resumen?.sin_pagar?.pedidos || []
  const pedidosSinDocumentar = resumen?.sin_documentar?.pedidos || []
  
  const totalPaginasPagos = Math.ceil(pedidosSinPagar.length / itemsPorPagina)
  const totalPaginasDocumentos = Math.ceil(pedidosSinDocumentar.length / itemsPorPagina)
  
  const pedidosPagosActuales = pedidosSinPagar.slice(
    (paginaPagos - 1) * itemsPorPagina,
    paginaPagos * itemsPorPagina
  )
  
  const pedidosDocumentosActuales = pedidosSinDocumentar.slice(
    (paginaDocumentos - 1) * itemsPorPagina,
    paginaDocumentos * itemsPorPagina
  )

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">💰 Cobranza</h1>

      {/* Resumen Mejorado */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="bg-gradient-to-br from-red-500 to-red-600 rounded-lg p-6 text-white shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-red-100 text-sm font-medium mb-1">💸 PAGOS PENDIENTES</p>
              <p className="text-4xl font-bold">{resumen?.sin_pagar?.cantidad || 0}</p>
              <p className="text-red-100 text-xs mt-1">casos sin pagar</p>
            </div>
            <DollarSign className="h-16 w-16 text-red-200 opacity-50" />
          </div>
          <div className="pt-4 border-t border-red-400">
            <p className="text-sm text-red-100">Total no pagado</p>
            <p className="text-2xl font-bold">${resumen?.sin_pagar?.total?.toLocaleString('es-CL') || 0}</p>
          </div>
        </div>

        <div className="bg-gradient-to-br from-yellow-500 to-yellow-600 rounded-lg p-6 text-white shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-yellow-100 text-sm font-medium mb-1">📋 DOCUMENTOS PENDIENTES</p>
              <p className="text-4xl font-bold">{resumen?.sin_documentar?.cantidad || 0}</p>
              <p className="text-yellow-100 text-xs mt-1">documentos por hacer</p>
            </div>
            <FileText className="h-16 w-16 text-yellow-200 opacity-50" />
          </div>
          <div className="pt-4 border-t border-yellow-400">
            <p className="text-sm text-yellow-100">Boletas y Facturas</p>
            <p className="text-lg font-semibold">por emitir</p>
          </div>
        </div>
      </div>

      {/* DOS BLOQUES LADO A LADO */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* BLOQUE 1: Pagos Pendientes */}
        <div className="bg-white rounded-lg shadow-md">
          <div className="px-4 py-3 border-b border-gray-200 bg-red-50">
            <h2 className="text-lg font-bold text-red-700">🚨 Pagos Pendientes</h2>
            <p className="text-xs text-red-600">Mostrando {pedidosPagosActuales.length} de {pedidosSinPagar.length}</p>
          </div>
          
          <div className="overflow-x-auto" style={{ maxHeight: '600px', overflowY: 'auto' }}>
            <table className="w-full">
              <thead className="bg-gray-50 sticky top-0">
                <tr>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Pedido</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Cliente</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Total</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Acción</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {pedidosPagosActuales.map((pedido) => (
                  <tr 
                    key={pedido.id} 
                    onClick={() => handleAbrirPedido(pedido)}
                    className="hover:bg-red-50 cursor-pointer transition-colors"
                  >
                    <td className="px-3 py-2">
                      <div className="text-xs font-medium text-gray-900">{pedido.numero_pedido || pedido.id}</div>
                      <div className="text-xs text-gray-500 truncate max-w-[120px]">{pedido.arreglo_pedido}</div>
                    </td>
                    <td className="px-3 py-2">
                      <div className="text-xs text-gray-900">{pedido.cliente_nombre}</div>
                      <div className="text-xs text-gray-500">{pedido.cliente_telefono}</div>
                    </td>
                    <td className="px-3 py-2">
                      <div className="text-sm font-bold text-red-600">
                        ${pedido.precio_total?.toLocaleString('es-CL')}
                      </div>
                      {pedido.fecha_maxima_pago && (() => {
                        const dias = calcularDiasFaltantes(pedido.fecha_maxima_pago)
                        if (dias < 0) {
                          return (
                            <span className="text-xs text-red-600 font-medium">
                              Vencido
                            </span>
                          )
                        } else if (dias <= 3) {
                          return (
                            <span className="text-xs text-orange-600 font-medium">
                              {dias}d restantes
                            </span>
                          )
                        }
                        return null
                      })()}
                    </td>
                    <td className="px-3 py-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          setEditandoPedido(pedido)
                        }}
                        className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded hover:bg-red-200 font-medium"
                      >
                        Actualizar
                      </button>
                    </td>
                  </tr>
                ))}
                {pedidosPagosActuales.length === 0 && (
                  <tr>
                    <td colSpan="4" className="px-3 py-6 text-center text-gray-500 text-sm">
                      ✅ No hay pagos pendientes
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
          
          {/* Paginación Pagos */}
          {totalPaginasPagos > 1 && (
            <div className="px-4 py-3 border-t border-gray-200 flex items-center justify-between">
              <button
                onClick={() => setPaginaPagos(p => Math.max(1, p - 1))}
                disabled={paginaPagos === 1}
                className="text-xs px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Anterior
              </button>
              <span className="text-xs text-gray-600">
                Página {paginaPagos} de {totalPaginasPagos}
              </span>
              <button
                onClick={() => setPaginaPagos(p => Math.min(totalPaginasPagos, p + 1))}
                disabled={paginaPagos === totalPaginasPagos}
                className="text-xs px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Siguiente
              </button>
            </div>
          )}
        </div>

        {/* BLOQUE 2: Documentos Pendientes */}
        <div className="bg-white rounded-lg shadow-md">
          <div className="px-4 py-3 border-b border-gray-200 bg-yellow-50">
            <h2 className="text-lg font-bold text-yellow-700">📋 Documentos Pendientes</h2>
            <p className="text-xs text-yellow-600">Mostrando {pedidosDocumentosActuales.length} de {pedidosSinDocumentar.length}</p>
          </div>
          
          <div className="overflow-x-auto" style={{ maxHeight: '600px', overflowY: 'auto' }}>
            <table className="w-full">
              <thead className="bg-gray-50 sticky top-0">
                <tr>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Pedido</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Cliente</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Documento</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Acción</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {pedidosDocumentosActuales.map((pedido) => (
                  <tr 
                    key={pedido.id} 
                    onClick={() => handleAbrirPedido(pedido)}
                    className="hover:bg-yellow-50 cursor-pointer transition-colors"
                  >
                    <td className="px-3 py-2">
                      <div className="text-xs font-medium text-gray-900">{pedido.numero_pedido || pedido.id}</div>
                    </td>
                    <td className="px-3 py-2">
                      <div className="text-xs text-gray-900">{pedido.cliente_nombre}</div>
                      <div className="text-xs text-gray-500">{pedido.cliente_telefono}</div>
                    </td>
                    <td className="px-3 py-2">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        pedido.documento_tributario === 'Hacer boleta' ? 'bg-yellow-100 text-yellow-800' :
                        pedido.documento_tributario === 'Hacer factura' ? 'bg-yellow-100 text-yellow-800' :
                        pedido.documento_tributario === 'Falta boleta o factura' ? 'bg-red-100 text-red-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        {pedido.documento_tributario}
                      </span>
                      {pedido.numero_documento && (
                        <div className="text-xs text-gray-500 mt-1">N° {pedido.numero_documento}</div>
                      )}
                    </td>
                    <td className="px-3 py-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          setEditandoPedido(pedido)
                        }}
                        className="text-xs bg-yellow-100 text-yellow-700 px-2 py-1 rounded hover:bg-yellow-200 font-medium"
                      >
                        Actualizar
                      </button>
                    </td>
                  </tr>
                ))}
                {pedidosDocumentosActuales.length === 0 && (
                  <tr>
                    <td colSpan="4" className="px-3 py-6 text-center text-gray-500 text-sm">
                      ✅ Todos los documentos al día
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
          
          {/* Paginación Documentos */}
          {totalPaginasDocumentos > 1 && (
            <div className="px-4 py-3 border-t border-gray-200 flex items-center justify-between">
              <button
                onClick={() => setPaginaDocumentos(p => Math.max(1, p - 1))}
                disabled={paginaDocumentos === 1}
                className="text-xs px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Anterior
              </button>
              <span className="text-xs text-gray-600">
                Página {paginaDocumentos} de {totalPaginasDocumentos}
              </span>
              <button
                onClick={() => setPaginaDocumentos(p => Math.min(totalPaginasDocumentos, p + 1))}
                disabled={paginaDocumentos === totalPaginasDocumentos}
                className="text-xs px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Siguiente
              </button>
            </div>
          )}
        </div>
      </div>

      {/* PAGADOS (lista inferior con búsqueda) */}
      <div className="mt-8 bg-white rounded-lg shadow-md">
        <div className="px-4 py-3 border-b border-gray-200 flex flex-col md:flex-row md:items-center md:justify-between gap-3">
          <div>
            <h2 className="text-lg font-bold text-green-700">✅ Pagados</h2>
            <p className="text-xs text-gray-600">Máximo {limitePagados} por página</p>
          </div>
          <input
            value={busquedaPagados}
            onChange={(e) => setBusquedaPagados(e.target.value)}
            placeholder="Buscar por pedido, cliente, documento, teléfono..."
            className="w-full md:w-96 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
          />
        </div>
        <div className="overflow-x-auto">
          {loadingPagados ? (
            <div className="p-6 text-gray-500">Cargando...</div>
          ) : (
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Pedido</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Cliente</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Documento</th>
                  <th className="px-3 py-2 text-right text-xs font-medium text-gray-500">Total</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {pagados.map(p => (
                  <tr key={p.id} className="hover:bg-gray-50">
                    <td className="px-3 py-2 text-xs">
                      <div className="font-medium text-gray-900">{p.numero_pedido || p.id}</div>
                      {p.shopify_order_number && (
                        <div className="text-gray-500">{p.shopify_order_number}</div>
                      )}
                    </td>
                    <td className="px-3 py-2 text-xs">
                      <div className="text-gray-900">{p.cliente_nombre}</div>
                      <div className="text-gray-500">{p.cliente_telefono}</div>
                    </td>
                    <td className="px-3 py-2 text-xs">
                      <div className="text-gray-900">{p.documento_tributario || '-'}</div>
                      {p.numero_documento && (
                        <div className="text-gray-500">N° {p.numero_documento}</div>
                      )}
                    </td>
                    <td className="px-3 py-2 text-right text-xs font-bold text-gray-900">
                      ${((p.precio_ramo || 0) + (p.precio_envio || 0)).toLocaleString('es-CL')}
                    </td>
                  </tr>
                ))}
                {pagados.length === 0 && !loadingPagados && (
                  <tr>
                    <td colSpan="4" className="px-3 py-6 text-center text-gray-500 text-sm">
                      No hay resultados
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          )}
        </div>
        {totalPaginasPagados > 1 && (
          <div className="px-4 py-3 border-t border-gray-200 flex items-center justify-between">
            <button
              onClick={() => setPaginaPagados(p => Math.max(1, p - 1))}
              disabled={paginaPagados === 1}
              className="text-xs px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Anterior
            </button>
            <span className="text-xs text-gray-600">Página {paginaPagados} de {totalPaginasPagados}</span>
            <button
              onClick={() => setPaginaPagados(p => Math.min(totalPaginasPagados, p + 1))}
              disabled={paginaPagados === totalPaginasPagados}
              className="text-xs px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Siguiente
            </button>
          </div>
        )}
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

              {/* NOTAS DE COBRANZA */}
              <div className="border-2 border-gray-200 rounded-lg p-4 bg-gray-50">
                <label className="block text-sm font-bold text-gray-900 mb-2">
                  📝 Notas de Cobranza
                </label>
                <textarea
                  value={editandoPedido.cobranza || ''}
                  onChange={(e) => setEditandoPedido({ ...editandoPedido, cobranza: e.target.value })}
                  placeholder="Notas, referencias de pago, comentarios..."
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-400 mb-2"
                />
                <button
                  onClick={() => actualizarCobranza(editandoPedido.id, { notas: editandoPedido.cobranza })}
                  className="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-800 font-medium"
                >
                  💾 Guardar Notas
                </button>
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

      {/* Modal de Detalle del Pedido */}
      {pedidoDetalle && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 overflow-y-auto">
          <div className="bg-white rounded-lg shadow-xl max-w-5xl w-full my-8">
            {/* Header del Modal */}
            <div className="bg-gradient-to-r from-red-600 to-red-700 px-6 py-4 rounded-t-lg flex justify-between items-center">
              <div>
                <h2 className="text-2xl font-bold text-white">
                  Pedido #{pedidoDetalle.numero_pedido || pedidoDetalle.id}
                </h2>
                <p className="text-red-100 text-sm mt-1">Detalle completo del pedido</p>
              </div>
              <button
                onClick={() => setPedidoDetalle(null)}
                className="text-white hover:text-red-100 transition-colors"
              >
                <X className="h-6 w-6" />
              </button>
            </div>

            {/* Contenido del Modal */}
            <div className="p-6 max-h-[calc(100vh-200px)] overflow-y-auto">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                
                {/* Columna Izquierda */}
                <div className="space-y-6">
                  
                  {/* Producto del Catálogo */}
                  {pedidoDetalle.producto_catalogo && (
                    <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-4 border border-purple-200">
                      <h3 className="text-sm font-semibold text-purple-900 mb-3 flex items-center gap-2">
                        <Package className="h-4 w-4" />
                        Producto del Catálogo
                      </h3>
                      <div className="flex items-center gap-3">
                        {pedidoDetalle.producto_imagen && (
                          <img 
                            src={pedidoDetalle.producto_imagen} 
                            alt={pedidoDetalle.producto_catalogo}
                            className="w-16 h-16 object-cover rounded-lg"
                          />
                        )}
                        <div>
                          <p className="font-medium text-purple-900">{pedidoDetalle.producto_catalogo}</p>
                          <p className="text-xs text-purple-700">ID: {pedidoDetalle.producto_id || '-'}</p>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Detalles del Arreglo */}
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h3 className="text-sm font-semibold text-gray-900 mb-3">Detalles del Arreglo</h3>
                    <div className="space-y-2">
                      <div>
                        <p className="text-xs text-gray-500">Arreglo solicitado</p>
                        <p className="text-sm font-medium text-gray-900">{pedidoDetalle.arreglo_pedido || '-'}</p>
                      </div>
                      {pedidoDetalle.detalles_adicionales && (
                        <div>
                          <p className="text-xs text-gray-500">Detalles adicionales</p>
                          <p className="text-sm text-gray-700">{pedidoDetalle.detalles_adicionales}</p>
                        </div>
                      )}
                      {pedidoDetalle.motivo && (
                        <div className="mt-2 inline-block px-3 py-1 bg-pink-100 text-pink-800 rounded-full text-xs font-medium">
                          {pedidoDetalle.motivo}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Mensaje y Destinatario */}
                  {(pedidoDetalle.destinatario || pedidoDetalle.mensaje || pedidoDetalle.firma) && (
                    <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                      <h3 className="text-sm font-semibold text-blue-900 mb-3">Mensaje y Destinatario</h3>
                      {pedidoDetalle.destinatario && (
                        <div className="mb-2">
                          <p className="text-xs text-blue-600">Para:</p>
                          <p className="text-sm font-medium text-blue-900">{pedidoDetalle.destinatario}</p>
                        </div>
                      )}
                      {pedidoDetalle.mensaje && (
                        <div className="mb-2 bg-white p-2 rounded">
                          <p className="text-xs text-blue-600">Mensaje:</p>
                          <p className="text-sm text-gray-700 italic">"{pedidoDetalle.mensaje}"</p>
                        </div>
                      )}
                      {pedidoDetalle.firma && (
                        <div>
                          <p className="text-xs text-blue-600">Firma:</p>
                          <p className="text-sm font-medium text-blue-900">{pedidoDetalle.firma}</p>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Información del Cliente */}
                  <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4 border border-green-200">
                    <h3 className="text-sm font-semibold text-green-900 mb-3 flex items-center gap-2">
                      <User className="h-4 w-4" />
                      Información del Cliente
                    </h3>
                    <div className="space-y-2">
                      <div>
                        <p className="text-xs text-green-600">Nombre</p>
                        <p className="text-sm font-medium text-green-900">{pedidoDetalle.cliente_nombre}</p>
                      </div>
                      {pedidoDetalle.cliente_telefono && (
                        <div className="flex items-center gap-2">
                          <Phone className="h-3 w-3 text-green-600" />
                          <p className="text-sm text-gray-700">{pedidoDetalle.cliente_telefono}</p>
                        </div>
                      )}
                      {pedidoDetalle.correo_cliente && (
                        <div className="flex items-center gap-2">
                          <Mail className="h-3 w-3 text-green-600" />
                          <p className="text-sm text-gray-700">{pedidoDetalle.correo_cliente}</p>
                        </div>
                      )}
                      {pedidoDetalle.canal && (
                        <div>
                          <span className="inline-block px-2 py-1 bg-green-200 text-green-800 rounded text-xs font-medium">
                            {pedidoDetalle.canal}
                          </span>
                        </div>
                      )}
                      {clienteDetalle && (
                        <div className="mt-2 pt-2 border-t border-green-200">
                          <p className="text-xs text-green-600">Tipo de cliente</p>
                          <span className="inline-block px-2 py-1 bg-white text-green-800 rounded text-xs font-medium">
                            {clienteDetalle.tipo_cliente}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Columna Derecha */}
                <div className="space-y-6">
                  
                  {/* Información de Entrega */}
                  <div className="bg-amber-50 rounded-lg p-4 border border-amber-200">
                    <h3 className="text-sm font-semibold text-amber-900 mb-3 flex items-center gap-2">
                      <MapPin className="h-4 w-4" />
                      Información de Entrega
                    </h3>
                    <div className="space-y-2">
                      {pedidoDetalle.direccion_entrega && (
                        <div>
                          <p className="text-xs text-amber-600">Dirección</p>
                          <p className="text-sm font-medium text-gray-900">{pedidoDetalle.direccion_entrega}</p>
                        </div>
                      )}
                      {pedidoDetalle.comuna && (
                        <div>
                          <p className="text-xs text-amber-600">Comuna</p>
                          <p className="text-sm text-gray-700">{pedidoDetalle.comuna}</p>
                        </div>
                      )}
                      {pedidoDetalle.fecha_pedido && (
                        <div className="flex items-center gap-2">
                          <Calendar className="h-3 w-3 text-amber-600" />
                          <div>
                            <p className="text-xs text-amber-600">Fecha del pedido</p>
                            <p className="text-sm text-gray-700">{formatFecha(pedidoDetalle.fecha_pedido)}</p>
                          </div>
                        </div>
                      )}
                      {pedidoDetalle.fecha_entrega && (
                        <div className="flex items-center gap-2">
                          <Calendar className="h-3 w-3 text-amber-600" />
                          <div>
                            <p className="text-xs text-amber-600">Fecha de entrega</p>
                            <p className="text-sm font-medium text-gray-900">{formatFecha(pedidoDetalle.fecha_entrega)}</p>
                          </div>
                        </div>
                      )}
                      {pedidoDetalle.dia_entrega && (
                        <div>
                          <span className="inline-block px-2 py-1 bg-amber-200 text-amber-800 rounded text-xs font-medium">
                            {pedidoDetalle.dia_entrega}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Información de Pago */}
                  <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-lg p-4 border-2 border-red-300">
                    <h3 className="text-sm font-semibold text-red-900 mb-3 flex items-center gap-2">
                      <DollarSign className="h-4 w-4" />
                      Información de Pago
                    </h3>
                    <div className="space-y-3">
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <p className="text-xs text-red-600">Precio Ramo</p>
                          <p className="text-sm font-medium text-gray-900">
                            ${pedidoDetalle.precio_ramo?.toLocaleString('es-CL') || 0}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-red-600">Precio Envío</p>
                          <p className="text-sm font-medium text-gray-900">
                            ${pedidoDetalle.precio_envio?.toLocaleString('es-CL') || 0}
                          </p>
                        </div>
                      </div>
                      <div className="pt-2 border-t-2 border-red-300">
                        <p className="text-xs text-red-600">Total</p>
                        <p className="text-2xl font-bold text-red-700">
                          ${pedidoDetalle.precio_total?.toLocaleString('es-CL') || 0}
                        </p>
                      </div>
                      <div className="pt-2 border-t border-red-200">
                        <div className="flex justify-between items-center mb-2">
                          <p className="text-xs text-red-600">Estado de pago</p>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            pedidoDetalle.estado_pago === 'Pagado' 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-red-200 text-red-800'
                          }`}>
                            {pedidoDetalle.estado_pago || 'No Pagado'}
                          </span>
                        </div>
                        {pedidoDetalle.metodo_pago && (
                          <div className="flex justify-between items-center mb-2">
                            <p className="text-xs text-red-600">Método de pago</p>
                            <p className="text-sm text-gray-700">{pedidoDetalle.metodo_pago}</p>
                          </div>
                        )}
                        {pedidoDetalle.documento_tributario && (
                          <div className="flex justify-between items-center">
                            <p className="text-xs text-red-600">Documento</p>
                            <p className="text-sm text-gray-700">{pedidoDetalle.documento_tributario}</p>
                          </div>
                        )}
                        {pedidoDetalle.numero_documento && (
                          <div className="flex justify-between items-center mt-1">
                            <p className="text-xs text-red-600">N° Documento</p>
                            <p className="text-sm font-medium text-gray-900">{pedidoDetalle.numero_documento}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Perfil del Cliente (si está cargado) */}
                  {clienteDetalle && (
                    <div className="bg-gradient-to-br from-indigo-50 to-indigo-100 rounded-lg p-4 border border-indigo-200">
                      <h3 className="text-sm font-semibold text-indigo-900 mb-3">
                        📊 Perfil Completo del Cliente
                      </h3>
                      {loadingCliente ? (
                        <div className="text-center py-4">
                          <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-600"></div>
                          <p className="text-xs text-indigo-600 mt-2">Cargando...</p>
                        </div>
                      ) : (
                        <div className="space-y-3">
                          <div className="grid grid-cols-2 gap-2 text-xs">
                            <div>
                              <p className="text-indigo-600">Total pedidos</p>
                              <p className="font-semibold text-indigo-900">{clienteDetalle.total_pedidos}</p>
                            </div>
                            <div>
                              <p className="text-indigo-600">Total gastado</p>
                              <p className="font-semibold text-indigo-900">
                                ${clienteDetalle.total_gastado?.toLocaleString('es-CL')}
                              </p>
                            </div>
                            <div>
                              <p className="text-indigo-600">Ticket promedio</p>
                              <p className="font-semibold text-indigo-900">
                                ${clienteDetalle.ticket_promedio?.toLocaleString('es-CL')}
                              </p>
                            </div>
                            <div>
                              <p className="text-indigo-600">Segmento</p>
                              <p className="font-semibold text-indigo-900">{clienteDetalle.segmento || '-'}</p>
                            </div>
                          </div>
                          
                          {historialCliente.length > 0 && (
                            <div className="pt-3 border-t border-indigo-200">
                              <p className="text-xs font-medium text-indigo-900 mb-2">
                                Historial de Pedidos ({historialCliente.length})
                              </p>
                              <div className="max-h-40 overflow-y-auto space-y-1">
                                {historialCliente.slice(0, 5).map((orden) => (
                                  <div
                                    key={orden.id}
                                    className={`p-2 rounded text-xs ${
                                      orden.id === pedidoDetalle.id
                                        ? 'bg-indigo-200 border border-indigo-400'
                                        : 'bg-white'
                                    }`}
                                  >
                                    <div className="flex justify-between items-center">
                                      <span className="font-medium">{orden.numero_pedido || orden.id}</span>
                                      <span className="text-indigo-600">
                                        ${orden.precio_total?.toLocaleString('es-CL')}
                                      </span>
                                    </div>
                                    <div className="text-indigo-600 text-xs">
                                      {formatFecha(orden.fecha_pedido)}
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Footer del Modal */}
            <div className="bg-gray-50 px-6 py-4 rounded-b-lg flex justify-between items-center border-t">
              <button
                onClick={() => {
                  setPedidoDetalle(null)
                  setEditandoPedido(pedidoDetalle)
                }}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 font-medium transition-colors"
              >
                Actualizar Cobranza
              </button>
              <button
                onClick={() => setPedidoDetalle(null)}
                className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100 font-medium transition-colors"
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

