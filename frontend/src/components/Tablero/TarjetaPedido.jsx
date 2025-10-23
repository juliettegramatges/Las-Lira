import { Calendar, MapPin, Phone, ShoppingBag, MessageSquare, Image as ImageIcon } from 'lucide-react'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'

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
  const handleDragStart = (e) => {
    e.dataTransfer.setData('pedidoId', pedido.id)
  }
  
  const fechaEntrega = pedido.fecha_entrega ? new Date(pedido.fecha_entrega) : null
  
  return (
    <div
      draggable
      onDragStart={handleDragStart}
      className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm hover:shadow-md transition-shadow cursor-move"
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
        <div className="flex flex-wrap gap-1 mb-2">
          {pedido.dia_entrega && (
            <span className={`px-2 py-0.5 rounded text-xs font-medium ${diaColor[pedido.dia_entrega]}`}>
              {pedido.dia_entrega}
            </span>
          )}
          {pedido.estado_pago && (
            <span className={`px-2 py-0.5 rounded text-xs font-medium ${pagoColor[pedido.estado_pago]}`}>
              {pedido.estado_pago === 'No Pagado' ? '❌ NO PAGADO' : pedido.estado_pago}
            </span>
          )}
          {pedido.tipo_pedido && pedido.tipo_pedido !== 'Normal' && (
            <span className="px-2 py-0.5 rounded text-xs font-medium bg-gray-800 text-white">
              {pedido.tipo_pedido}
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
  )
}

export default TarjetaPedido

