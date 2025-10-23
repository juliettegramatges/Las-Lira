import { useState, useEffect } from 'react'
import { productosAPI } from '../services/api'
import { Flower2, CheckCircle, XCircle } from 'lucide-react'

function ProductosPage() {
  const [productos, setProductos] = useState([])
  const [loading, setLoading] = useState(true)
  
  const cargarProductos = async () => {
    try {
      setLoading(true)
      const response = await productosAPI.listar()
      if (response.data.success) {
        setProductos(response.data.data)
      }
    } catch (err) {
      console.error('Error al cargar productos:', err)
    } finally {
      setLoading(false)
    }
  }
  
  useEffect(() => {
    cargarProductos()
  }, [])
  
  return (
    <div className="px-4 sm:px-0">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Catálogo de Productos</h1>
        <p className="mt-1 text-sm text-gray-600">
          {productos.length} producto{productos.length !== 1 ? 's' : ''} en el catálogo
        </p>
      </div>
      
      {/* Grid de productos */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {loading ? (
          <div className="col-span-full text-center py-12 text-gray-500">
            Cargando productos...
          </div>
        ) : productos.length === 0 ? (
          <div className="col-span-full text-center py-12 text-gray-500">
            No hay productos disponibles
          </div>
        ) : (
          productos.map((producto) => (
            <div
              key={producto.id}
              className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow"
            >
              {/* Imagen placeholder */}
              <div className="h-48 bg-gradient-to-br from-primary-100 to-primary-200 flex items-center justify-center">
                <Flower2 className="h-16 w-16 text-primary-600" />
              </div>
              
              {/* Contenido */}
              <div className="p-4">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      {producto.nombre}
                    </h3>
                    <p className="text-sm text-gray-500">{producto.id}</p>
                  </div>
                  {producto.disponible_shopify ? (
                    <CheckCircle className="h-5 w-5 text-green-500" title="En Shopify" />
                  ) : (
                    <XCircle className="h-5 w-5 text-gray-300" title="No en Shopify" />
                  )}
                </div>
                
                <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                  {producto.descripcion}
                </p>
                
                <div className="space-y-2 text-sm">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-500">Tipo:</span>
                    <span className="font-medium text-gray-900">{producto.tipo_arreglo}</span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-gray-500">Colores:</span>
                    <span className="font-medium text-gray-900">{producto.paleta_colores}</span>
                  </div>
                  
                  {producto.cantidad_flores_min && (
                    <div className="flex items-center justify-between">
                      <span className="text-gray-500">Flores:</span>
                      <span className="font-medium text-gray-900">
                        {producto.cantidad_flores_min}-{producto.cantidad_flores_max}
                      </span>
                    </div>
                  )}
                </div>
                
                <div className="mt-4 pt-4 border-t border-gray-100 flex items-center justify-between">
                  <span className="text-xl font-bold text-primary-600">
                    ${producto.precio_venta?.toLocaleString('es-CL')}
                  </span>
                  <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
                    Ver receta →
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default ProductosPage

