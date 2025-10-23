import { useState, useEffect } from 'react'
import { pedidosAPI } from '../services/api'
import ColumnaKanban from '../components/Tablero/ColumnaKanban'
import { AlertCircle, Loader2 } from 'lucide-react'

function TableroPage() {
  const [tablero, setTablero] = useState({
    'Pedido': [],
    'Pedidos Semana': [],
    'Entregas para Mañana': [],
    'Entregas de Hoy': [],
    'En Proceso': [],
    'Listo para Despacho': [],
    'Despachados': []
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  // Estados según flujo del Trello de Las-Lira
  const estados = [
    'Pedido',
    'Pedidos Semana', 
    'Entregas para Mañana', 
    'Entregas de Hoy',
    'En Proceso', 
    'Listo para Despacho',
    'Despachados'
  ]
  
  const cargarTablero = async () => {
    try {
      setLoading(true)
      
      // 🚀 PASO 1: Actualizar automáticamente estados según fecha
      await pedidosAPI.actualizarEstadosPorFecha()
      
      // 📊 PASO 2: Cargar tablero con estados actualizados
      const response = await pedidosAPI.obtenerTablero()
      if (response.data.success) {
        setTablero(response.data.data)
      }
    } catch (err) {
      setError('Error al cargar el tablero')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }
  
  useEffect(() => {
    cargarTablero()
  }, [])
  
  const moverPedido = async (pedidoId, nuevoEstado) => {
    try {
      await pedidosAPI.actualizarEstado(pedidoId, nuevoEstado)
      await cargarTablero()
    } catch (err) {
      console.error('Error al mover pedido:', err)
      alert('Error al actualizar el estado del pedido')
    }
  }
  
  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
      </div>
    )
  }
  
  if (error) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <p className="text-gray-600">{error}</p>
          <button
            onClick={cargarTablero}
            className="mt-4 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            Reintentar
          </button>
        </div>
      </div>
    )
  }
  
  const totalPedidos = Object.values(tablero).reduce((sum, pedidos) => sum + pedidos.length, 0)
  
  return (
    <div className="px-4 sm:px-0">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Tablero de Pedidos</h1>
        <p className="mt-1 text-sm text-gray-600">
          {totalPedidos} pedido{totalPedidos !== 1 ? 's' : ''} pendiente{totalPedidos !== 1 ? 's' : ''}
        </p>
      </div>
      
      {/* Tablero Kanban */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {estados.map((estado) => (
          <ColumnaKanban
            key={estado}
            estado={estado}
            pedidos={tablero[estado] || []}
            onMoverPedido={moverPedido}
            onRecargar={cargarTablero}
          />
        ))}
      </div>
    </div>
  )
}

export default TableroPage

