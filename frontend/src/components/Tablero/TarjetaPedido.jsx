import { Calendar, MapPin, Phone, ShoppingBag, MessageSquare, Image as ImageIcon } from 'lucide-react'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'

const canalColor = {
  'Shopify': 'bg-green-100 text-green-800',
  'WhatsApp': 'bg-emerald-100 text-emerald-800',
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
        <div className="mb-3 -mx-4 -mt-4">
          <img 
            src={pedido.producto_imagen.startsWith('http') ? pedido.producto_imagen : `/api/upload/imagen/${pedido.producto_imagen}`}
            alt={pedido.producto_nombre || 'Arreglo'}
            className="w-full h-32 object-cover rounded-t-lg"
          />
        </div>
      )}
      
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div>
          <span className="text-xs font-medium text-gray-500">{pedido.id}</span>
          <h4 className="text-sm font-semibold text-gray-900 mt-1">
            {pedido.cliente_nombre}
          </h4>
        </div>
        <span className={`px-2 py-1 rounded text-xs font-medium ${canalColor[pedido.canal]}`}>
          {pedido.canal}
        </span>
      </div>
      
      {/* Producto/Descripción */}
      <div className="mb-3">
        {pedido.producto_nombre ? (
          <div className="flex items-center text-sm text-gray-700">
            <ShoppingBag className="h-4 w-4 mr-2 text-gray-400" />
            <span className="truncate">{pedido.producto_nombre}</span>
          </div>
        ) : pedido.descripcion_personalizada ? (
          <div className="flex items-start text-sm text-gray-700">
            <MessageSquare className="h-4 w-4 mr-2 mt-0.5 text-gray-400 flex-shrink-0" />
            <span className="line-clamp-2">{pedido.descripcion_personalizada}</span>
          </div>
        ) : null}
      </div>
      
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

