import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { pedidosAPI } from '../services/api'
import ColumnaKanban from '../components/Tablero/ColumnaKanban'
import { AlertCircle, Loader2, RefreshCw } from 'lucide-react'

function TableroPage() {
  const navigate = useNavigate()
  const [tablero, setTablero] = useState({
    'Entregas de Hoy': [],
    'Entregas para Mañana': [],
    'En Proceso': [],
    'Listo para Despacho': [],
    'Despachados': [],
    'Pedidos Semana': [],
    'Eventos': []
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [mensajeActualizacion, setMensajeActualizacion] = useState(null)
  const [actualizando, setActualizando] = useState(false)
  
  // Estados según flujo del Trello de Las-Lira (orden de prioridad)
  const estados = [
    'Entregas de Hoy',      // 🔥 Urgente - hoy
    'Entregas para Mañana', // ⚡ Próximo - mañana
    'En Proceso',           // 🔧 Taller trabajando
    'Listo para Despacho',  // ✅ Listo para enviar
    'Despachados',          // 📦 Completados
    'Pedidos Semana',       // 📅 Planificación semanal
    'Eventos'               // 🎉 Pedidos para eventos especiales
  ]
  
  const cargarTablero = async (autoClasificar = true) => {
    try {
      setLoading(true)
      setMensajeActualizacion(null)
      
      // 🚀 PASO 1: Actualizar automáticamente estados según fecha (solo si autoClasificar=true)
      if (autoClasificar) {
        const actualizacionRes = await pedidosAPI.actualizarEstadosPorFecha()
        if (actualizacionRes.data.success && actualizacionRes.data.actualizados > 0) {
          setMensajeActualizacion(actualizacionRes.data.message)
          setTimeout(() => setMensajeActualizacion(null), 5000)
        }
      }
      
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
  
  const forzarActualizacion = async () => {
    try {
      setActualizando(true)
      await cargarTablero(true)
    } finally {
      setActualizando(false)
    }
  }
  
  useEffect(() => {
    cargarTablero(true) // Auto-clasificar solo al cargar inicialmente
  }, [])
  
  const moverPedido = async (pedidoId, nuevoEstado) => {
    try {
      await pedidosAPI.actualizarEstado(pedidoId, nuevoEstado)
      // NO auto-clasificar después de mover manualmente, respetar la decisión del usuario
      await cargarTablero(false)
    } catch (err) {
      console.error('Error al mover pedido:', err)
      alert('Error al actualizar el estado del pedido')
    }
  }
  
  const handleAbrirPedido = (pedido) => {
    // Navegar a la página de pedidos y pasar el pedido para abrir el modal
    navigate('/pedidos', { state: { pedidoAAbrir: pedido } })
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
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Tablero de Pedidos</h1>
            <p className="mt-1 text-sm text-gray-600">
              {totalPedidos} pedido{totalPedidos !== 1 ? 's' : ''} pendiente{totalPedidos !== 1 ? 's' : ''}
            </p>
          </div>
          <button
            onClick={forzarActualizacion}
            disabled={actualizando}
            className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            <RefreshCw className={`h-5 w-5 ${actualizando ? 'animate-spin' : ''}`} />
            {actualizando ? 'Actualizando...' : 'Actualizar Estados'}
          </button>
        </div>
        
        {/* Mensaje de Actualización */}
        {mensajeActualizacion && (
          <div className="mt-4 p-3 bg-green-100 border border-green-300 text-green-800 rounded-lg flex items-center gap-2">
            <AlertCircle className="h-5 w-5 flex-shrink-0" />
            <span className="text-sm font-medium">{mensajeActualizacion}</span>
          </div>
        )}
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
            onAbrirPedido={handleAbrirPedido}
          />
        ))}
      </div>
    </div>
  )
}

export default TableroPage

