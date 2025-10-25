import { useState } from 'react'
import { Calendar, MapPin, Phone, ShoppingBag, MessageSquare, Image as ImageIcon, X, User, CreditCard, FileText, Package, Camera, Upload, CheckCircle2 } from 'lucide-react'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import axios from 'axios'

const API_URL = 'http://localhost:5001/api'

const canalColor = {
  'Shopify': 'bg-green-100 text-green-800',
  'WhatsApp': 'bg-emerald-100 text-emerald-800',
}

const diaColor = {
  'LUNES': 'bg-yellow-400 text-gray-900',
  'MARTES': 'bg-orange-400 text-white',
  'MIERCOLES': 'bg-red-500 text-white',
  'JUEVES': 'bg-purple-500 text-white',
  'VIERNES': 'bg-blue-500 text-white',
  'SABADO': 'bg-cyan-400 text-white',
  'DOMINGO': 'bg-green-500 text-white',
}

const pagoColor = {
  'Pagado': 'bg-green-100 text-green-800',
  'No Pagado': 'bg-red-100 text-red-800',
  'Falta Boleta o Factura': 'bg-orange-100 text-orange-800',
}

function TarjetaPedido({ pedido, onRecargar }) {
  const [mostrarModal, setMostrarModal] = useState(false)
  const [mostrarModalFoto, setMostrarModalFoto] = useState(false)
  const [subiendoFoto, setSubiendoFoto] = useState(false)
  const [archivoSeleccionado, setArchivoSeleccionado] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  
  const handleDragStart = (e) => {
    e.dataTransfer.setData('pedidoId', pedido.id)
  }
  
  const handleClick = (e) => {
    // Solo abrir modal si no estamos arrastrando
    if (e.defaultPrevented) return
    setMostrarModal(true)
  }
  
  const handleSeleccionarArchivo = (e) => {
    const archivo = e.target.files[0]
    if (archivo) {
      setArchivoSeleccionado(archivo)
      setPreviewUrl(URL.createObjectURL(archivo))
    }
  }
  
  const handleSubirFoto = async () => {
    if (!archivoSeleccionado) return
    
    try {
      setSubiendoFoto(true)
      const formData = new FormData()
      formData.append('imagen', archivoSeleccionado)
      
      await axios.post(`${API_URL}/pedidos/${pedido.id}/foto-respaldo`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      
      alert('✅ Foto de respaldo subida correctamente')
      setMostrarModalFoto(false)
      setArchivoSeleccionado(null)
      setPreviewUrl(null)
      
      // Recargar el tablero para actualizar
      if (onRecargar) onRecargar()
    } catch (error) {
      console.error('Error al subir foto:', error)
      alert('❌ Error al subir la foto')
    } finally {
      setSubiendoFoto(false)
    }
  }
  
  const handleAbrirModalFoto = (e) => {
    e.stopPropagation()
    setMostrarModalFoto(true)
  }
  
  const fechaEntrega = pedido.fecha_entrega ? new Date(pedido.fecha_entrega) : null
  const fechaPedido = pedido.fecha_pedido ? new Date(pedido.fecha_pedido) : null
  
  // Determinar si necesita foto de respaldo
  const necesitaFotoRespaldo = ['Listo para Despacho', 'Despachados'].includes(pedido.estado) && !pedido.foto_enviado_url
  
  return (
    <>
      <div
        draggable
        onDragStart={handleDragStart}
        onClick={handleClick}
        className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm hover:shadow-md transition-shadow cursor-pointer"
      >
      {/* Imagen del producto (si tiene) */}
      {pedido.producto_imagen && (
        <div className="mb-3 -mx-4 -mt-4 bg-gradient-to-br from-primary-100 to-primary-200 rounded-t-lg overflow-hidden flex items-center justify-center" style={{height: '128px'}}>
          <img 
            src={pedido.producto_imagen.startsWith('http') ? pedido.producto_imagen : `/api/upload/imagen/${pedido.producto_imagen}`}
            alt={pedido.producto_nombre || 'Arreglo'}
            className="w-full h-full object-contain p-2"
          />
        </div>
      )}
      
      {/* Header */}
      <div className="mb-3">
        {/* Nombre y teléfono */}
        <div className="flex items-start justify-between mb-2">
          <div className="flex-1">
            <h4 className="text-sm font-semibold text-gray-900">
              {pedido.cliente_nombre}
            </h4>
            <p className="text-xs text-gray-600">{pedido.cliente_telefono}</p>
          </div>
        </div>
        
        {/* IDs del pedido */}
        <div className="flex flex-wrap gap-2 mb-2 text-xs">
          <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded font-mono">
            {pedido.id}
          </span>
          {pedido.canal === 'Shopify' && pedido.shopify_order_number && (
            <span className="px-2 py-1 bg-green-50 text-green-700 rounded font-mono">
              🛍️ {pedido.shopify_order_number}
            </span>
          )}
        </div>
        
        {/* Etiquetas */}
        <div className="flex flex-wrap gap-1.5 mb-2">
          {/* Etiqueta de Canal */}
          <span className={`px-2 py-1 rounded-full text-xs font-bold ${canalColor[pedido.canal]} border-2 ${pedido.canal === 'Shopify' ? 'border-green-300' : 'border-emerald-300'}`}>
            {pedido.canal === 'Shopify' ? '🛍️ Shopify' : '📱 WhatsApp'}
          </span>
          
          {/* Día de la semana */}
          {pedido.dia_entrega && (
            <span className={`px-2 py-1 rounded-full text-xs font-bold ${diaColor[pedido.dia_entrega]} shadow-sm`}>
              📅 {pedido.dia_entrega}
            </span>
          )}
          
          {/* Estado de Pago - MÁS VISIBLE */}
          {pedido.estado_pago && (
            <span className={`px-2 py-1 rounded-full text-xs font-bold ${pagoColor[pedido.estado_pago]} border-2 ${
              pedido.estado_pago === 'Pagado' ? 'border-green-300' : 'border-red-300'
            } shadow-sm`}>
              {pedido.estado_pago === 'No Pagado' ? '❌ NO PAGADO' : 
               pedido.estado_pago === 'Pagado' ? '✅ PAGADO' : pedido.estado_pago}
            </span>
          )}
          
          {/* Método de Pago */}
          {pedido.metodo_pago && pedido.metodo_pago !== 'Pendiente' && (
            <span className="px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 border border-blue-200">
              💳 {pedido.metodo_pago}
            </span>
          )}
          
          {/* Documento Tributario */}
          {pedido.documento_tributario && pedido.documento_tributario !== 'No requiere' && (
            <span className="px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800 border border-purple-200">
              📄 {pedido.documento_tributario}
            </span>
          )}
          
          {/* Tipo de Pedido Especial */}
          {pedido.tipo_pedido && pedido.tipo_pedido !== 'Normal' && (
            <span className="px-2 py-1 rounded-full text-xs font-bold bg-gray-900 text-white shadow-sm">
              ⭐ {pedido.tipo_pedido}
            </span>
          )}
          
          {/* Etiqueta de URGENTE para entregas de hoy */}
          {pedido.estado === 'Entregas de Hoy' && (
            <span className="px-2 py-1 rounded-full text-xs font-bold bg-red-600 text-white shadow-lg animate-pulse">
              🔥 URGENTE HOY
            </span>
          )}
          
          {/* Motivo del pedido */}
          {pedido.motivo && pedido.motivo !== 'Sin motivo específico' && (
            <span className="px-2 py-1 rounded-full text-xs font-medium bg-pink-100 text-pink-800 border border-pink-200">
              💐 {pedido.motivo}
            </span>
          )}
        </div>
      </div>
      
      {/* Tipo de Arreglo */}
      <div className="mb-3">
        {pedido.arreglo_pedido && (
          <div className="flex items-center text-sm font-medium text-primary-700 bg-primary-50 rounded px-2 py-1.5">
            <ShoppingBag className="h-4 w-4 mr-2 flex-shrink-0" />
            <span className="truncate">{pedido.arreglo_pedido}</span>
          </div>
        )}
      </div>
      
      {/* Detalles Adicionales */}
      {pedido.detalles_adicionales && (
        <div className="mb-3">
          <div className="flex items-start text-xs text-gray-600 bg-yellow-50 rounded px-2 py-1.5 border border-yellow-200">
            <MessageSquare className="h-3.5 w-3.5 mr-1.5 mt-0.5 flex-shrink-0 text-yellow-600" />
            <span className="line-clamp-2">{pedido.detalles_adicionales}</span>
          </div>
        </div>
      )}
      
      {/* Detalles */}
      <div className="space-y-2 text-xs text-gray-600">
        {fechaEntrega && (
          <div className="flex items-center">
            <Calendar className="h-3.5 w-3.5 mr-2 text-gray-400" />
            {format(fechaEntrega, "d 'de' MMMM", { locale: es })}
          </div>
        )}
        
        {pedido.comuna && (
          <div className="flex items-center">
            <MapPin className="h-3.5 w-3.5 mr-2 text-gray-400" />
            {pedido.comuna}
          </div>
        )}
        
        <div className="flex items-center">
          <Phone className="h-3.5 w-3.5 mr-2 text-gray-400" />
          {pedido.cliente_telefono}
        </div>
      </div>
      
      {/* Botón para agregar foto de respaldo */}
      {necesitaFotoRespaldo && (
        <div className="mt-3">
          <button
            onClick={handleAbrirModalFoto}
            className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-amber-500 hover:bg-amber-600 text-white rounded-lg text-sm font-medium transition-colors shadow-sm animate-pulse"
          >
            <Camera className="h-4 w-4" />
            Agregar Foto de Respaldo
          </button>
        </div>
      )}
      
      {/* Indicador de foto subida */}
      {pedido.foto_enviado_url && ['Listo para Despacho', 'Despachados'].includes(pedido.estado) && (
        <div className="mt-3 flex items-center gap-2 px-3 py-2 bg-green-50 border border-green-200 rounded-lg">
          <CheckCircle2 className="h-4 w-4 text-green-600" />
          <span className="text-xs font-medium text-green-700">Foto de respaldo subida ✓</span>
        </div>
      )}
      
      {/* Precio */}
      <div className="mt-3 pt-3 border-t border-gray-100">
        <span className="text-sm font-semibold text-gray-900">
          ${pedido.precio_total?.toLocaleString('es-CL')}
        </span>
      </div>
      
      {/* Notas (si existen) */}
      {pedido.notas && (
        <div className="mt-2 text-xs text-gray-500 bg-gray-50 rounded p-2">
          {pedido.notas}
        </div>
      )}
    </div>

    {/* Modal de detalles completos */}
    {mostrarModal && (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" onClick={() => setMostrarModal(false)}>
        <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
          {/* Header del modal */}
          <div className="sticky top-0 bg-primary-600 text-white px-6 py-4 flex items-center justify-between z-10">
            <div>
              <h2 className="text-xl font-bold">Detalles del Pedido</h2>
              <p className="text-sm opacity-90">{pedido.id}</p>
            </div>
            <button
              onClick={() => setMostrarModal(false)}
              className="p-2 hover:bg-primary-700 rounded-lg transition-colors"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          {/* Contenido del modal */}
          <div className="p-6 space-y-6">
            {/* Imagen del producto */}
            {pedido.producto_imagen && (
              <div className="bg-gradient-to-br from-primary-100 to-primary-200 rounded-lg overflow-hidden flex items-center justify-center" style={{height: '200px'}}>
                <img 
                  src={pedido.producto_imagen.startsWith('http') ? pedido.producto_imagen : `/api/upload/imagen/${pedido.producto_imagen}`}
                  alt={pedido.producto_nombre || 'Arreglo'}
                  className="w-full h-full object-contain p-4"
                />
              </div>
            )}

            {/* Información del Cliente */}
            <div className="bg-blue-50 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-blue-900 mb-3 flex items-center">
                <User className="h-5 w-5 mr-2" />
                Información del Cliente
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                <div>
                  <span className="font-medium text-gray-700">Nombre:</span>
                  <p className="text-gray-900">{pedido.cliente_nombre}</p>
                </div>
                <div>
                  <span className="font-medium text-gray-700">Teléfono:</span>
                  <p className="text-gray-900">{pedido.cliente_telefono}</p>
                </div>
                {pedido.cliente_email && (
                  <div>
                    <span className="font-medium text-gray-700">Email:</span>
                    <p className="text-gray-900">{pedido.cliente_email}</p>
                  </div>
                )}
                {pedido.cliente_tipo && (
                  <div>
                    <span className="font-medium text-gray-700">Tipo:</span>
                    <p className="text-gray-900">{pedido.cliente_tipo}</p>
                  </div>
                )}
              </div>
            </div>

            {/* Información del Pedido */}
            <div className="bg-green-50 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-green-900 mb-3 flex items-center">
                <ShoppingBag className="h-5 w-5 mr-2" />
                Detalles del Pedido
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                <div>
                  <span className="font-medium text-gray-700">Canal:</span>
                  <p className={`inline-block ml-2 px-2 py-1 rounded text-xs ${canalColor[pedido.canal]}`}>
                    {pedido.canal}
                  </p>
                </div>
                {pedido.shopify_order_number && (
                  <div>
                    <span className="font-medium text-gray-700">Nro. Shopify:</span>
                    <p className="text-gray-900 font-mono">{pedido.shopify_order_number}</p>
                  </div>
                )}
                <div>
                  <span className="font-medium text-gray-700">Arreglo:</span>
                  <p className="text-gray-900 font-medium">{pedido.arreglo_pedido}</p>
                </div>
                {pedido.motivo && (
                  <div>
                    <span className="font-medium text-gray-700">Motivo:</span>
                    <p className="text-gray-900">{pedido.motivo}</p>
                  </div>
                )}
                {fechaPedido && (
                  <div>
                    <span className="font-medium text-gray-700">Fecha Pedido:</span>
                    <p className="text-gray-900">{format(fechaPedido, "d 'de' MMMM, yyyy 'a las' HH:mm", { locale: es })}</p>
                  </div>
                )}
                {fechaEntrega && (
                  <div>
                    <span className="font-medium text-gray-700">Fecha Entrega:</span>
                    <p className="text-gray-900 font-semibold">{format(fechaEntrega, "d 'de' MMMM, yyyy 'a las' HH:mm", { locale: es })}</p>
                  </div>
                )}
              </div>
              {pedido.detalles_adicionales && (
                <div className="mt-3 pt-3 border-t border-green-200">
                  <span className="font-medium text-gray-700">Detalles Adicionales:</span>
                  <p className="text-gray-900 mt-1 bg-white rounded p-2">{pedido.detalles_adicionales}</p>
                </div>
              )}
            </div>

            {/* Dirección y Destinatario */}
            <div className="bg-purple-50 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-purple-900 mb-3 flex items-center">
                <MapPin className="h-5 w-5 mr-2" />
                Entrega
              </h3>
              <div className="space-y-3 text-sm">
                <div>
                  <span className="font-medium text-gray-700">Dirección:</span>
                  <p className="text-gray-900">{pedido.direccion_entrega}</p>
                </div>
                {pedido.comuna && (
                  <div>
                    <span className="font-medium text-gray-700">Comuna:</span>
                    <p className="text-gray-900">{pedido.comuna}</p>
                  </div>
                )}
                {pedido.destinatario && (
                  <div>
                    <span className="font-medium text-gray-700">Para (Destinatario):</span>
                    <p className="text-gray-900">{pedido.destinatario}</p>
                  </div>
                )}
                {pedido.mensaje && (
                  <div>
                    <span className="font-medium text-gray-700">Mensaje:</span>
                    <p className="text-gray-900 bg-white rounded p-2 italic">"{pedido.mensaje}"</p>
                  </div>
                )}
                {pedido.firma && (
                  <div>
                    <span className="font-medium text-gray-700">Firma:</span>
                    <p className="text-gray-900">{pedido.firma}</p>
                  </div>
                )}
              </div>
            </div>

            {/* Precios */}
            <div className="bg-yellow-50 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-yellow-900 mb-3 flex items-center">
                <CreditCard className="h-5 w-5 mr-2" />
                Valores
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
                <div>
                  <span className="font-medium text-gray-700">Precio Ramo:</span>
                  <p className="text-gray-900 text-lg font-semibold">${pedido.precio_ramo?.toLocaleString('es-CL')}</p>
                </div>
                <div>
                  <span className="font-medium text-gray-700">Precio Envío:</span>
                  <p className="text-gray-900 text-lg font-semibold">${pedido.precio_envio?.toLocaleString('es-CL')}</p>
                </div>
                <div className="md:col-span-1">
                  <span className="font-medium text-gray-700">Total:</span>
                  <p className="text-primary-600 text-2xl font-bold">${pedido.precio_total?.toLocaleString('es-CL')}</p>
                </div>
              </div>
            </div>

            {/* Estado y Cobranza */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                <FileText className="h-5 w-5 mr-2" />
                Estado y Cobranza
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                <div>
                  <span className="font-medium text-gray-700">Estado:</span>
                  <p className="text-gray-900 font-semibold">{pedido.estado}</p>
                </div>
                <div>
                  <span className="font-medium text-gray-700">Estado de Pago:</span>
                  <p className={`inline-block ml-2 px-2 py-1 rounded text-xs font-medium ${pagoColor[pedido.estado_pago]}`}>
                    {pedido.estado_pago}
                  </p>
                </div>
                {pedido.metodo_pago && pedido.metodo_pago !== 'Pendiente' && (
                  <div>
                    <span className="font-medium text-gray-700">Método de Pago:</span>
                    <p className="text-gray-900">{pedido.metodo_pago}</p>
                  </div>
                )}
                {pedido.documento_tributario && (
                  <div>
                    <span className="font-medium text-gray-700">Documento:</span>
                    <p className="text-gray-900">{pedido.documento_tributario}</p>
                  </div>
                )}
                {pedido.numero_documento && (
                  <div>
                    <span className="font-medium text-gray-700">Nro. Documento:</span>
                    <p className="text-gray-900 font-mono">{pedido.numero_documento}</p>
                  </div>
                )}
                {pedido.plazo_pago_dias > 0 && (
                  <div>
                    <span className="font-medium text-gray-700">Plazo de Pago:</span>
                    <p className="text-gray-900">{pedido.plazo_pago_dias} días</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Footer del modal */}
          <div className="sticky bottom-0 bg-gray-100 px-6 py-4 flex justify-end">
            <button
              onClick={() => setMostrarModal(false)}
              className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              Cerrar
            </button>
          </div>
        </div>
      </div>
    )}
    
    {/* Modal para subir foto de respaldo */}
    {mostrarModalFoto && (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" onClick={() => setMostrarModalFoto(false)}>
        <div className="bg-white rounded-lg shadow-xl max-w-md w-full" onClick={(e) => e.stopPropagation()}>
          {/* Header */}
          <div className="bg-amber-500 text-white px-6 py-4 flex items-center justify-between rounded-t-lg">
            <div className="flex items-center gap-2">
              <Camera className="h-6 w-6" />
              <h2 className="text-xl font-bold">Foto de Respaldo</h2>
            </div>
            <button
              onClick={() => setMostrarModalFoto(false)}
              className="p-2 hover:bg-amber-600 rounded-lg transition-colors"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          {/* Contenido */}
          <div className="p-6 space-y-4">
            <p className="text-gray-600 text-sm">
              Sube una foto del arreglo antes de despacharlo para tener un respaldo visual.
            </p>
            
            {/* Input de archivo */}
            <div>
              <label className="block w-full">
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-amber-500 transition-colors cursor-pointer">
                  <Upload className="h-12 w-12 mx-auto text-gray-400 mb-2" />
                  <p className="text-sm text-gray-600">
                    {archivoSeleccionado ? archivoSeleccionado.name : 'Haz clic o arrastra una imagen aquí'}
                  </p>
                  <p className="text-xs text-gray-400 mt-1">JPG, PNG o WEBP (máx. 5MB)</p>
                </div>
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleSeleccionarArchivo}
                  className="hidden"
                />
              </label>
            </div>
            
            {/* Preview de la imagen */}
            {previewUrl && (
              <div className="mt-4">
                <img 
                  src={previewUrl} 
                  alt="Preview" 
                  className="w-full h-64 object-contain bg-gray-50 rounded-lg border border-gray-200"
                />
              </div>
            )}
            
            {/* Información del pedido */}
            <div className="bg-gray-50 rounded-lg p-3 text-sm">
              <p className="font-medium text-gray-700">Pedido: {pedido.id}</p>
              <p className="text-gray-600">{pedido.cliente_nombre}</p>
              <p className="text-gray-600">{pedido.arreglo_pedido}</p>
            </div>
          </div>

          {/* Footer */}
          <div className="bg-gray-50 px-6 py-4 flex justify-end gap-3 rounded-b-lg">
            <button
              onClick={() => {
                setMostrarModalFoto(false)
                setArchivoSeleccionado(null)
                setPreviewUrl(null)
              }}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors"
            >
              Cancelar
            </button>
            <button
              onClick={handleSubirFoto}
              disabled={!archivoSeleccionado || subiendoFoto}
              className="px-4 py-2 bg-amber-500 text-white rounded-lg hover:bg-amber-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
            >
              {subiendoFoto ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                  Subiendo...
                </>
              ) : (
                <>
                  <Upload className="h-4 w-4" />
                  Subir Foto
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    )}
    </>
  )
}

export default TarjetaPedido

