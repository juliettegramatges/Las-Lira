import { useState, useEffect, useMemo } from 'react'
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
  const [mostrarFormulario, setMostrarFormulario] = useState(false)
  const [productos, setProductos] = useState([])
  const [comunas, setComunas] = useState([])
  const [loadingFormulario, setLoadingFormulario] = useState(false)
  
  // Estado del formulario
  const [formData, setFormData] = useState({
    canal: 'WhatsApp',
    shopify_order_number: '',
    cliente_nombre: '',
    cliente_telefono: '',
    cliente_email: '',
    arreglo_pedido: '',
    producto_id: '',
    detalles_adicionales: '',
    precio_ramo: '',
    precio_envio: '',
    destinatario: '',
    mensaje: '',
    firma: '',
    direccion_entrega: '',
    comuna: '',
    motivo: '',
    fecha_entrega: ''
  })
  
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
  
  const cargarDatosFormulario = async () => {
    try {
      // Cargar productos
      const prodResponse = await axios.get(`${API_URL}/productos`)
      if (prodResponse.data.success) {
        setProductos(prodResponse.data.data)
      }
      
      // Cargar comunas
      const comunasResponse = await axios.get(`${API_URL}/rutas/comunas`)
      if (comunasResponse.data.success) {
        setComunas(comunasResponse.data.data)
      }
    } catch (err) {
      console.error('Error al cargar datos del formulario:', err)
    }
  }
  
  const handleComunaChange = (comuna) => {
    const comunaData = comunas.find(c => c.nombre === comuna)
    setFormData(prev => ({
      ...prev,
      comuna,
      precio_envio: comunaData?.precio || ''
    }))
  }
  
  const handleSubmitPedido = async (e) => {
    e.preventDefault()
    
    // Validaciones
    if (!formData.cliente_nombre || !formData.cliente_telefono) {
      alert('❌ Nombre y teléfono del cliente son obligatorios')
      return
    }
    
    if (!formData.fecha_entrega) {
      alert('❌ La fecha de entrega es obligatoria')
      return
    }
    
    if (!formData.direccion_entrega) {
      alert('❌ La dirección de entrega es obligatoria')
      return
    }
    
    const precioRamo = parseFloat(formData.precio_ramo) || 0
    const precioEnvio = parseFloat(formData.precio_envio) || 0
    
    if (precioRamo <= 0) {
      alert('❌ El precio del ramo debe ser mayor a 0')
      return
    }
    
    try {
      setLoadingFormulario(true)
      
      const pedidoData = {
        canal: formData.canal,
        shopify_order_number: formData.shopify_order_number || null,
        cliente_nombre: formData.cliente_nombre,
        cliente_telefono: formData.cliente_telefono,
        cliente_email: formData.cliente_email || null,
        arreglo_pedido: formData.arreglo_pedido || null,
        producto_id: formData.producto_id || null,
        detalles_adicionales: formData.detalles_adicionales || null,
        precio_ramo: precioRamo,
        precio_envio: precioEnvio,
        precio_total: precioRamo + precioEnvio,
        destinatario: formData.destinatario || null,
        mensaje: formData.mensaje || null,
        firma: formData.firma || null,
        direccion_entrega: formData.direccion_entrega,
        comuna: formData.comuna || null,
        motivo: formData.motivo || null,
        fecha_entrega: new Date(formData.fecha_entrega).toISOString()
      }
      
      const response = await axios.post(`${API_URL}/pedidos`, pedidoData)
      
      if (response.data.success) {
        alert('✅ Pedido creado exitosamente: ' + response.data.data.id)
        setMostrarFormulario(false)
        setFormData({
          canal: 'WhatsApp',
          shopify_order_number: '',
          cliente_nombre: '',
          cliente_telefono: '',
          cliente_email: '',
          arreglo_pedido: '',
          producto_id: '',
          detalles_adicionales: '',
          precio_ramo: '',
          precio_envio: '',
          destinatario: '',
          mensaje: '',
          firma: '',
          direccion_entrega: '',
          comuna: '',
          motivo: '',
          fecha_entrega: ''
        })
        cargarPedidos()
      }
    } catch (err) {
      console.error('Error al crear pedido:', err)
      alert('❌ Error al crear pedido: ' + (err.response?.data?.error || err.message))
    } finally {
      setLoadingFormulario(false)
    }
  }
  
  useEffect(() => {
    cargarPedidos()
    cargarDatosFormulario()
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
  
  // Calcular total en tiempo real
  const totalPedido = useMemo(() => {
    const precioRamo = parseFloat(formData.precio_ramo) || 0
    const precioEnvio = parseFloat(formData.precio_envio) || 0
    return precioRamo + precioEnvio
  }, [formData.precio_ramo, formData.precio_envio])
  
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
        <button 
          onClick={() => setMostrarFormulario(true)}
          className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 flex items-center"
        >
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
      
      {/* Modal de Formulario de Nuevo Pedido */}
      {mostrarFormulario && (
        <div 
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
          onClick={() => setMostrarFormulario(false)}
        >
          <div 
            className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] flex flex-col"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header - Fijo */}
            <div className="flex-shrink-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between rounded-t-lg">
              <h2 className="text-2xl font-bold text-gray-900">Nuevo Pedido</h2>
              <button 
                onClick={() => setMostrarFormulario(false)}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <X className="h-6 w-6" />
              </button>
            </div>
            
            {/* Formulario - Con scroll */}
            <form id="form-nuevo-pedido" onSubmit={handleSubmitPedido} className="flex-1 overflow-y-auto p-6">
              <div className="space-y-6">
                {/* Canal */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Canal <span className="text-red-500">*</span>
                  </label>
                  <div className="flex gap-4">
                    <label className="flex items-center">
                      <input
                        type="radio"
                        name="canal"
                        value="WhatsApp"
                        checked={formData.canal === 'WhatsApp'}
                        onChange={(e) => setFormData({...formData, canal: e.target.value})}
                        className="mr-2"
                      />
                      WhatsApp
                    </label>
                    <label className="flex items-center">
                      <input
                        type="radio"
                        name="canal"
                        value="Shopify"
                        checked={formData.canal === 'Shopify'}
                        onChange={(e) => setFormData({...formData, canal: e.target.value})}
                        className="mr-2"
                      />
                      Shopify
                    </label>
                  </div>
                </div>
                
                {/* Nº Shopify (solo si es Shopify) */}
                {formData.canal === 'Shopify' && (
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Nº Pedido Shopify
                    </label>
                    <input
                      type="text"
                      value={formData.shopify_order_number}
                      onChange={(e) => setFormData({...formData, shopify_order_number: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                      placeholder="#1234"
                    />
                  </div>
                )}
                
                {/* Información del Cliente */}
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="text-sm font-semibold text-gray-700 uppercase mb-3">
                    Información del Cliente
                  </h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Nombre <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="text"
                        required
                        value={formData.cliente_nombre}
                        onChange={(e) => setFormData({...formData, cliente_nombre: e.target.value})}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                        placeholder="María García"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Teléfono <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="tel"
                        required
                        value={formData.cliente_telefono}
                        onChange={(e) => setFormData({...formData, cliente_telefono: e.target.value})}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                        placeholder="+56 9 1234 5678"
                      />
                    </div>
                    <div className="col-span-2">
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Email
                      </label>
                      <input
                        type="email"
                        value={formData.cliente_email}
                        onChange={(e) => setFormData({...formData, cliente_email: e.target.value})}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                        placeholder="cliente@ejemplo.com"
                      />
                    </div>
                  </div>
                </div>
                
                {/* Arreglo / Producto */}
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="text-sm font-semibold text-gray-700 uppercase mb-3">
                    Arreglo Solicitado
                  </h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Nombre del Arreglo
                      </label>
                      <input
                        type="text"
                        value={formData.arreglo_pedido}
                        onChange={(e) => setFormData({...formData, arreglo_pedido: e.target.value})}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                        placeholder="Pasión Roja, Ramo de Rosas, etc."
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Producto de Catálogo (opcional)
                      </label>
                      <select
                        value={formData.producto_id}
                        onChange={(e) => setFormData({...formData, producto_id: e.target.value})}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                      >
                        <option value="">-- Sin producto asociado --</option>
                        {productos.map(prod => (
                          <option key={prod.id} value={prod.id}>
                            {prod.nombre} - ${prod.precio_venta?.toLocaleString('es-CL')}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Detalles Adicionales
                      </label>
                      <textarea
                        value={formData.detalles_adicionales}
                        onChange={(e) => setFormData({...formData, detalles_adicionales: e.target.value})}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                        rows="3"
                        placeholder="Colores específicos, flores especiales, etc."
                      />
                    </div>
                  </div>
                </div>
                
                {/* Precios */}
                <div className="bg-primary-50 p-4 rounded-lg border-2 border-primary-200">
                  <h3 className="text-sm font-semibold text-gray-700 uppercase mb-3">
                    Precios
                  </h3>
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Precio Ramo <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="number"
                        required
                        min="0"
                        step="1000"
                        value={formData.precio_ramo}
                        onChange={(e) => setFormData({...formData, precio_ramo: e.target.value})}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                        placeholder="35000"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Precio Envío
                      </label>
                      <input
                        type="number"
                        min="0"
                        step="1000"
                        value={formData.precio_envio}
                        onChange={(e) => setFormData({...formData, precio_envio: e.target.value})}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                        placeholder="7000"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Total
                      </label>
                      <div className="w-full px-4 py-2 bg-white border border-gray-300 rounded-lg font-bold text-primary-600 text-lg">
                        ${totalPedido.toLocaleString('es-CL')}
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* Mensaje y Destinatario */}
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="text-sm font-semibold text-gray-700 uppercase mb-3">
                    Mensaje y Destinatario
                  </h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Para (Destinatario)
                      </label>
                      <input
                        type="text"
                        value={formData.destinatario}
                        onChange={(e) => setFormData({...formData, destinatario: e.target.value})}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                        placeholder="Ana López"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Mensaje
                      </label>
                      <textarea
                        value={formData.mensaje}
                        onChange={(e) => setFormData({...formData, mensaje: e.target.value})}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                        rows="3"
                        placeholder="Feliz cumpleaños! Que tengas un día maravilloso..."
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Firma
                      </label>
                      <input
                        type="text"
                        value={formData.firma}
                        onChange={(e) => setFormData({...formData, firma: e.target.value})}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                        placeholder="Con cariño, Juan"
                      />
                    </div>
                  </div>
                </div>
                
                {/* Entrega */}
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="text-sm font-semibold text-gray-700 uppercase mb-3">
                    Información de Entrega
                  </h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Dirección Completa <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="text"
                        required
                        value={formData.direccion_entrega}
                        onChange={(e) => setFormData({...formData, direccion_entrega: e.target.value})}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                        placeholder="Av. Apoquindo 1234, Depto 501"
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Comuna
                        </label>
                        <select
                          value={formData.comuna}
                          onChange={(e) => handleComunaChange(e.target.value)}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                        >
                          <option value="">-- Seleccionar comuna --</option>
                          {comunas.map(com => (
                            <option key={com.nombre} value={com.nombre}>
                              {com.nombre} - ${com.precio.toLocaleString('es-CL')}
                            </option>
                          ))}
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Fecha de Entrega <span className="text-red-500">*</span>
                        </label>
                        <input
                          type="datetime-local"
                          required
                          value={formData.fecha_entrega}
                          onChange={(e) => setFormData({...formData, fecha_entrega: e.target.value})}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                        />
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* Motivo */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Motivo
                  </label>
                  <select
                    value={formData.motivo}
                    onChange={(e) => setFormData({...formData, motivo: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="">-- Seleccionar motivo --</option>
                    <option value="Cumpleaños">Cumpleaños</option>
                    <option value="Aniversario">Aniversario</option>
                    <option value="San Valentín">San Valentín</option>
                    <option value="Día de la Madre">Día de la Madre</option>
                    <option value="Día del Padre">Día del Padre</option>
                    <option value="Mejórate">Mejórate</option>
                    <option value="Condolencias">Condolencias</option>
                    <option value="Agradecimiento">Agradecimiento</option>
                    <option value="Felicitaciones">Felicitaciones</option>
                    <option value="Graduación">Graduación</option>
                    <option value="Nacimiento">Nacimiento</option>
                    <option value="Boda">Boda</option>
                    <option value="Propuesta">Propuesta</option>
                    <option value="Amor y Romance">Amor y Romance</option>
                    <option value="Solo porque sí">Solo porque sí</option>
                    <option value="Disculpas">Disculpas</option>
                    <option value="Nuevo hogar">Nuevo hogar</option>
                    <option value="Nuevo trabajo">Nuevo trabajo</option>
                    <option value="Navidad">Navidad</option>
                    <option value="Año Nuevo">Año Nuevo</option>
                    <option value="Otro">Otro</option>
                  </select>
                </div>
              </div>
            </form>
            
            {/* Botones - Fijos en la parte inferior */}
            <div className="flex-shrink-0 bg-white border-t border-gray-200 px-6 py-4 flex justify-end gap-3 rounded-b-lg">
              <button
                type="button"
                onClick={() => setMostrarFormulario(false)}
                className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                disabled={loadingFormulario}
              >
                Cancelar
              </button>
              <button
                type="submit"
                form="form-nuevo-pedido"
                className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
                disabled={loadingFormulario}
              >
                {loadingFormulario ? 'Creando...' : 'Crear Pedido'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default PedidosPage
