import { useState, useEffect } from 'react'
import { inventarioAPI } from '../services/api'
import { Package, AlertCircle, TrendingDown } from 'lucide-react'

function InventarioPage() {
  const [tab, setTab] = useState('flores')
  const [flores, setFlores] = useState([])
  const [contenedores, setContenedores] = useState([])
  const [resumen, setResumen] = useState(null)
  const [loading, setLoading] = useState(true)
  
  const cargarDatos = async () => {
    try {
      setLoading(true)
      const [floresRes, contenedoresRes, resumenRes] = await Promise.all([
        inventarioAPI.listarFlores(),
        inventarioAPI.listarContenedores(),
        inventarioAPI.obtenerResumen(),
      ])
      
      if (floresRes.data.success) setFlores(floresRes.data.data)
      if (contenedoresRes.data.success) setContenedores(contenedoresRes.data.data)
      if (resumenRes.data.success) setResumen(resumenRes.data.data)
    } catch (err) {
      console.error('Error al cargar inventario:', err)
    } finally {
      setLoading(false)
    }
  }
  
  useEffect(() => {
    cargarDatos()
  }, [])
  
  return (
    <div className="px-4 sm:px-0">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Inventario</h1>
        <p className="mt-1 text-sm text-gray-600">
          Control de flores y contenedores
        </p>
      </div>
      
      {/* Resumen */}
      {resumen && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Flores</p>
                <p className="text-2xl font-bold text-gray-900">{resumen.total_flores}</p>
              </div>
              <Package className="h-8 w-8 text-primary-600" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Contenedores</p>
                <p className="text-2xl font-bold text-gray-900">{resumen.total_contenedores}</p>
              </div>
              <Package className="h-8 w-8 text-blue-600" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Flores Stock Bajo</p>
                <p className="text-2xl font-bold text-yellow-600">{resumen.flores_bajo_stock}</p>
              </div>
              <AlertCircle className="h-8 w-8 text-yellow-600" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Valor Inventario</p>
                <p className="text-2xl font-bold text-green-600">
                  ${Math.round(resumen.valor_total_inventario).toLocaleString('es-CL')}
                </p>
              </div>
              <TrendingDown className="h-8 w-8 text-green-600" />
            </div>
          </div>
        </div>
      )}
      
      {/* Tabs */}
      <div className="mb-4 border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setTab('flores')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              tab === 'flores'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Flores ({flores.length})
          </button>
          <button
            onClick={() => setTab('contenedores')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              tab === 'contenedores'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Contenedores ({contenedores.length})
          </button>
        </nav>
      </div>
      
      {/* Contenido de tabs */}
      <div className="bg-white shadow-sm rounded-lg overflow-hidden">
        {tab === 'flores' ? (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tipo
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Color
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Stock
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Costo Unitario
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Bodega
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {flores.map((flor) => (
                <tr key={flor.id} className={flor.cantidad_stock < 20 ? 'bg-yellow-50' : ''}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {flor.id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {flor.tipo}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <span className="flex items-center">
                      <span
                        className="inline-block w-3 h-3 rounded-full mr-2"
                        style={{ backgroundColor: flor.color.toLowerCase() }}
                      />
                      {flor.color}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {flor.cantidad_stock}
                    {flor.cantidad_stock < 20 && (
                      <AlertCircle className="inline h-4 w-4 ml-2 text-yellow-600" />
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${flor.costo_unitario?.toLocaleString('es-CL')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {flor.bodega_nombre}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tipo
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Material
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tamaño
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Stock
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Costo
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {contenedores.map((contenedor) => (
                <tr key={contenedor.id} className={contenedor.stock < 5 ? 'bg-yellow-50' : ''}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {contenedor.id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {contenedor.tipo}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {contenedor.material}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {contenedor.tamano}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {contenedor.stock}
                    {contenedor.stock < 5 && (
                      <AlertCircle className="inline h-4 w-4 ml-2 text-yellow-600" />
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${contenedor.costo?.toLocaleString('es-CL')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

export default InventarioPage

