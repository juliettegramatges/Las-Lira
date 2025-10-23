import { useState, useEffect } from 'react'
import { pedidosAPI } from '../services/api'
import { Search, Filter, Plus } from 'lucide-react'

function PedidosPage() {
  const [pedidos, setPedidos] = useState([])
  const [loading, setLoading] = useState(true)
  const [filtroEstado, setFiltroEstado] = useState('')
  const [filtroCanal, setFiltroCanal] = useState('')
  
  const cargarPedidos = async () => {
    try {
      setLoading(true)
      const filtros = {}
      if (filtroEstado) filtros.estado = filtroEstado
      if (filtroCanal) filtros.canal = filtroCanal
      
      const response = await pedidosAPI.listar(filtros)
      if (response.data.success) {
        setPedidos(response.data.data)
      }
    } catch (err) {
      console.error('Error al cargar pedidos:', err)
    } finally {
      setLoading(false)
    }
  }
  
  useEffect(() => {
    cargarPedidos()
  }, [filtroEstado, filtroCanal])
  
  const estadoColor = {
    'Recibido': 'bg-blue-100 text-blue-800',
    'En Preparación': 'bg-yellow-100 text-yellow-800',
    'Listo': 'bg-green-100 text-green-800',
    'Despachado': 'bg-purple-100 text-purple-800',
    'Entregado': 'bg-gray-100 text-gray-800',
    'Cancelado': 'bg-red-100 text-red-800',
  }
  
  return (
    <div className="px-4 sm:px-0">
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Pedidos</h1>
          <p className="mt-1 text-sm text-gray-600">
            Gestiona todos los pedidos
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
          <option value="Recibido">Recibido</option>
          <option value="En Preparación">En Preparación</option>
          <option value="Listo">Listo</option>
          <option value="Despachado">Despachado</option>
          <option value="Entregado">Entregado</option>
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
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                ID
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Cliente
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Canal
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Producto
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Estado
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Total
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Entrega
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {loading ? (
              <tr>
                <td colSpan="7" className="px-6 py-4 text-center text-sm text-gray-500">
                  Cargando...
                </td>
              </tr>
            ) : pedidos.length === 0 ? (
              <tr>
                <td colSpan="7" className="px-6 py-4 text-center text-sm text-gray-500">
                  No hay pedidos
                </td>
              </tr>
            ) : (
              pedidos.map((pedido) => (
                <tr key={pedido.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {pedido.id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {pedido.cliente_nombre}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {pedido.canal}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {pedido.producto_nombre || 'Personalizado'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${estadoColor[pedido.estado]}`}>
                      {pedido.estado}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${pedido.precio_total?.toLocaleString('es-CL')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {pedido.fecha_entrega}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default PedidosPage

