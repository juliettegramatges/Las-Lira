import { useState } from 'react'
import TarjetaPedido from './TarjetaPedido'
import { Plus } from 'lucide-react'

const colorEstado = {
  'Recibido': 'bg-blue-50 border-blue-200',
  'En Preparación': 'bg-yellow-50 border-yellow-200',
  'Listo': 'bg-green-50 border-green-200',
  'Despachado': 'bg-purple-50 border-purple-200',
}

const colorBadge = {
  'Recibido': 'bg-blue-100 text-blue-800',
  'En Preparación': 'bg-yellow-100 text-yellow-800',
  'Listo': 'bg-green-100 text-green-800',
  'Despachado': 'bg-purple-100 text-purple-800',
}

function ColumnaKanban({ estado, pedidos, onMoverPedido, onRecargar }) {
  const [dragOver, setDragOver] = useState(false)
  
  const handleDragOver = (e) => {
    e.preventDefault()
    setDragOver(true)
  }
  
  const handleDragLeave = () => {
    setDragOver(false)
  }
  
  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    
    const pedidoId = e.dataTransfer.getData('pedidoId')
    if (pedidoId) {
      onMoverPedido(pedidoId, estado)
    }
  }
  
  return (
    <div
      className={`rounded-lg border-2 ${colorEstado[estado]} ${
        dragOver ? 'ring-2 ring-primary-400' : ''
      } transition-all`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {/* Header de la columna */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-gray-900">{estado}</h3>
          <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${colorBadge[estado]}`}>
            {pedidos.length}
          </span>
        </div>
      </div>
      
      {/* Lista de pedidos */}
      <div className="p-3 space-y-3 min-h-[200px] max-h-[calc(100vh-300px)] overflow-y-auto">
        {pedidos.length === 0 ? (
          <div className="text-center py-8 text-gray-400 text-sm">
            No hay pedidos
          </div>
        ) : (
          pedidos.map((pedido) => (
            <TarjetaPedido
              key={pedido.id}
              pedido={pedido}
              onRecargar={onRecargar}
            />
          ))
        )}
      </div>
    </div>
  )
}

export default ColumnaKanban

