import { useState, useEffect } from 'react'
import axios from 'axios'
import { Search, Filter, Plus, Eye, MapPin, Package, DollarSign, Calendar, User, MessageSquare, X } from 'lucide-react'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'

const API_URL = 'http://localhost:8000/api'

function PedidosPage() {
  const [pedidos, setPedidos] = useState([])
  const [loading, setLoading] = useState(true)
  const [filtroEstado, setFiltroEstado] = useState('')
  const [filtroCanal, setFiltroCanal] = useState('')
  const [pedidoDetalle, setPedidoDetalle] = useState(null)
  
  const cargarPedidos = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (filtroEstado) params.append('estado', filtroEstado)
      if (filtroCanal) params.append('canal', filtroCanal)
      
      const response = await axios.get(`${API_URL}/pedidos?${params}`)
      if (response.data.success) {
        setPedidos(response.data.data)
      }
    } catch (err) {
      console.error('Error al cargar pedidos:', err)
      alert('❌ No se pudo conectar con el servidor')
    } finally {
      setLoading(false)
    }
  }
  
  useEffect(() => {
    cargarPedidos()
  }, [filtroEstado, filtroCanal])
  
  const estadoColor = {
    'Pedido': 'bg-blue-100 text-blue-800',
    'Pedidos Semana': 'bg-indigo-100 text-indigo-800',
    'Entregas para Mañana': 'bg-orange-100 text-orange-800',
    'Entregas de Hoy': 'bg-red-100 text-red-800',
    'En Proceso': 'bg-yellow-100 text-yellow-800',
    'Listo para Despacho': 'bg-green-100 text-green-800',
    'Despachados': 'bg-purple-100 text-purple-800',
    'Archivado': 'bg-gray-100 text-gray-800',
    'Cancelado': 'bg-red-200 text-red-900',
  }
  
  const formatFecha = (fechaStr) => {
    try {
      const fecha = new Date(fechaStr)
      return format(fecha, "dd/MM/yyyy HH:mm", { locale: es })
    } catch {
      return fechaStr
    }
  }
  
  return (
    <div className="px-4 sm:px-0">
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Pedidos</h1>
          <p className="mt-1 text-sm text-gray-600">
            {pedidos.length} pedido{pedidos.length !== 1 ? 's' : ''} en total
          </p>
        </div>
        <button className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 flex items-center">
          <Plus className="h-5 w-5 mr-2" />
          Nuevo Pedido
        </button>
      </div>
      
      {/* Filtros */}
      <div className="mb-6 flex gap-4">
        <select
          value={filtroEstado}
          onChange={(e) => setFiltroEstado(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <option value="">Todos los estados</option>
          <option value="Pedido">Pedido</option>
          <option value="Pedidos Semana">Pedidos Semana</option>
          <option value="Entregas para Mañana">Entregas para Mañana</option>
          <option value="Entregas de Hoy">Entregas de Hoy</option>
          <option value="En Proceso">En Proceso</option>
          <option value="Listo para Despacho">Listo para Despacho</option>
          <option value="Despachados">Despachados</option>
          <option value="Archivado">Archivado</option>
          <option value="Cancelado">Cancelado</option>
        </select>
        
        <select
          value={filtroCanal}
          onChange={(e) => setFiltroCanal(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <option value="">Todos los canales</option>
          <option value="Shopify">Shopify</option>
          <option value="WhatsApp">WhatsApp</option>
        </select>
      </div>
      
      {/* Tabla de pedidos */}
      <div className="bg-white shadow-sm rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  ID / Cliente
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Arreglo / Para
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Comuna / Dirección
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Precio Ramo / Envío
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Motivo
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Estado
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Entrega
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {loading ? (
                <tr>
                  <td colSpan="8" className="px-6 py-8 text-center text-sm text-gray-500">
                    Cargando pedidos...
                  </td>
                </tr>
              ) : pedidos.length === 0 ? (
                <tr>
                  <td colSpan="8" className="px-6 py-8 text-center">
                    <p className="text-gray-500 mb-2">No hay pedidos</p>
                    <p className="text-xs text-gray-400">
                      Ejecuta <code className="bg-gray-100 px-2 py-1 rounded">python3 importar_datos_demo.py</code> para cargar datos
                    </p>
                  </td>
                </tr>
              ) : (
                pedidos.map((pedido) => (
                  <tr key={pedido.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="text-sm font-medium text-gray-900">{pedido.id}</div>
                      <div className="text-sm text-gray-500">{pedido.cliente_nombre}</div>
                      <div className="text-xs text-gray-400">{pedido.cliente_telefono}</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900">{pedido.arreglo_pedido || 'Sin especificar'}</div>
                      {pedido.destinatario && (
                        <div className="text-xs text-gray-500">Para: {pedido.destinatario}</div>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm font-medium text-gray-900">{pedido.comuna || 'Sin comuna'}</div>
                      <div className="text-xs text-gray-500 max-w-xs truncate" title={pedido.direccion_entrega}>
                        {pedido.direccion_entrega}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm font-semibold text-gray-900">
                        ${pedido.precio_ramo?.toLocaleString('es-CL') || '0'}
                      </div>
                      <div className="text-xs text-gray-500">
                        + ${pedido.precio_envio?.toLocaleString('es-CL') || '0'} envío
                      </div>
                      <div className="text-xs font-medium text-primary-600">
                        Total: ${pedido.precio_total?.toLocaleString('es-CL') || '0'}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-700">{pedido.motivo || '-'}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${estadoColor[pedido.estado]}`}>
                        {pedido.estado}
                      </span>
                      {pedido.canal && (
                        <div className="text-xs text-gray-500 mt-1">{pedido.canal}</div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {pedido.fecha_entrega ? formatFecha(pedido.fecha_entrega) : '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={() => setPedidoDetalle(pedido)}
                        className="text-primary-600 hover:text-primary-900 flex items-center gap-1"
                      >
                        <Eye className="h-4 w-4" />
                        Ver
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
      
      {/* Modal de Detalles del Pedido */}
      {pedidoDetalle && (
        <div 
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
          onClick={() => setPedidoDetalle(null)}
        >
          <div 
            className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Pedido {pedidoDetalle.id}</h2>
                <span className={`mt-1 px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${estadoColor[pedidoDetalle.estado]}`}>
                  {pedidoDetalle.estado}
                </span>
              </div>
              <button 
                onClick={() => setPedidoDetalle(null)}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <X className="h-6 w-6" />
              </button>
            </div>
            
            {/* Contenido */}
            <div className="p-6 space-y-6">
              {/* Cliente */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="text-sm font-semibold text-gray-500 uppercase mb-3 flex items-center">
                  <User className="h-4 w-4 mr-2" />
                  Información del Cliente
                </h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-xs text-gray-500">Nombre</p>
                    <p className="text-sm font-medium text-gray-900">{pedidoDetalle.cliente_nombre}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Teléfono</p>
                    <p className="text-sm font-medium text-gray-900">{pedidoDetalle.cliente_telefono}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Canal</p>
                    <p className="text-sm font-medium text-gray-900">{pedidoDetalle.canal}</p>
                  </div>
                  {pedidoDetalle.shopify_order_number && (
                    <div>
                      <p className="text-xs text-gray-500">Nº Shopify</p>
                      <p className="text-sm font-medium text-gray-900">{pedidoDetalle.shopify_order_number}</p>
                    </div>
                  )}
                </div>
              </div>
              
              {/* Arreglo */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="text-sm font-semibold text-gray-500 uppercase mb-3 flex items-center">
                  <Package className="h-4 w-4 mr-2" />
                  Detalles del Arreglo
                </h3>
                <div className="space-y-2">
                  <div>
                    <p className="text-xs text-gray-500">Arreglo Pedido</p>
                    <p className="text-sm font-medium text-gray-900">{pedidoDetalle.arreglo_pedido || 'Sin especificar'}</p>
                  </div>
                  {pedidoDetalle.detalles_adicionales && (
                    <div>
                      <p className="text-xs text-gray-500">Detalles Adicionales</p>
                      <p className="text-sm text-gray-700">{pedidoDetalle.detalles_adicionales}</p>
                    </div>
                  )}
                  {pedidoDetalle.motivo && (
                    <div>
                      <p className="text-xs text-gray-500">Motivo</p>
                      <p className="text-sm text-gray-700">{pedidoDetalle.motivo}</p>
                    </div>
                  )}
                </div>
              </div>
              
              {/* Destinatario y Mensaje */}
              {(pedidoDetalle.destinatario || pedidoDetalle.mensaje) && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="text-sm font-semibold text-gray-500 uppercase mb-3 flex items-center">
                    <MessageSquare className="h-4 w-4 mr-2" />
                    Mensaje y Destinatario
                  </h3>
                  <div className="space-y-2">
                    {pedidoDetalle.destinatario && (
                      <div>
                        <p className="text-xs text-gray-500">Para</p>
                        <p className="text-sm font-medium text-gray-900">{pedidoDetalle.destinatario}</p>
                      </div>
                    )}
                    {pedidoDetalle.mensaje && (
                      <div>
                        <p className="text-xs text-gray-500">Mensaje</p>
                        <p className="text-sm text-gray-700 italic">"{pedidoDetalle.mensaje}"</p>
                      </div>
                    )}
                    {pedidoDetalle.firma && (
                      <div>
                        <p className="text-xs text-gray-500">Firma</p>
                        <p className="text-sm text-gray-700">{pedidoDetalle.firma}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}
              
              {/* Entrega */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="text-sm font-semibold text-gray-500 uppercase mb-3 flex items-center">
                  <MapPin className="h-4 w-4 mr-2" />
                  Información de Entrega
                </h3>
                <div className="space-y-2">
                  <div>
                    <p className="text-xs text-gray-500">Dirección Completa</p>
                    <p className="text-sm font-medium text-gray-900">{pedidoDetalle.direccion_entrega}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Comuna</p>
                    <p className="text-sm font-medium text-gray-900">{pedidoDetalle.comuna || 'Sin especificar'}</p>
                  </div>
                  <div className="grid grid-cols-2 gap-4 pt-2">
                    <div>
                      <p className="text-xs text-gray-500">Fecha de Pedido</p>
                      <p className="text-sm text-gray-700">{formatFecha(pedidoDetalle.fecha_pedido)}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Fecha de Entrega</p>
                      <p className="text-sm font-medium text-gray-900">{formatFecha(pedidoDetalle.fecha_entrega)}</p>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Precios */}
              <div className="bg-primary-50 p-4 rounded-lg border-2 border-primary-200">
                <h3 className="text-sm font-semibold text-gray-700 uppercase mb-3 flex items-center">
                  <DollarSign className="h-4 w-4 mr-2" />
                  Desglose de Precios
                </h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-700">Precio del Ramo:</span>
                    <span className="text-sm font-medium text-gray-900">
                      ${pedidoDetalle.precio_ramo?.toLocaleString('es-CL') || '0'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-700">Precio del Envío:</span>
                    <span className="text-sm font-medium text-gray-900">
                      ${pedidoDetalle.precio_envio?.toLocaleString('es-CL') || '0'}
                    </span>
                  </div>
                  <div className="flex justify-between pt-2 border-t border-primary-300">
                    <span className="text-base font-semibold text-gray-900">Total:</span>
                    <span className="text-lg font-bold text-primary-600">
                      ${pedidoDetalle.precio_total?.toLocaleString('es-CL') || '0'}
                    </span>
                  </div>
                </div>
              </div>
              
              {/* Etiquetas adicionales */}
              {(pedidoDetalle.dia_entrega || pedidoDetalle.estado_pago || pedidoDetalle.tipo_pedido) && (
                <div className="flex flex-wrap gap-2">
                  {pedidoDetalle.dia_entrega && (
                    <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">
                      {pedidoDetalle.dia_entrega}
                    </span>
                  )}
                  {pedidoDetalle.estado_pago && (
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                      pedidoDetalle.estado_pago === 'Pagado' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {pedidoDetalle.estado_pago}
                    </span>
                  )}
                  {pedidoDetalle.tipo_pedido && (
                    <span className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-medium">
                      {pedidoDetalle.tipo_pedido}
                    </span>
                  )}
                </div>
              )}
              
              {pedidoDetalle.cobranza && (
                <div className="text-xs text-gray-500">
                  Cobranza: {pedidoDetalle.cobranza}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default PedidosPage
