import { useState, useEffect } from 'react'
import axios from 'axios'
import { Flower2, CheckCircle, XCircle, Upload, X, Camera } from 'lucide-react'

const API_URL = 'http://localhost:8000/api'

function ProductosPage() {
  const [productos, setProductos] = useState([])
  const [loading, setLoading] = useState(true)
  const [editandoFoto, setEditandoFoto] = useState(null)
  const [uploadingFoto, setUploadingFoto] = useState(false)
  const [productoDetalle, setProductoDetalle] = useState(null)
  
  const cargarProductos = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`${API_URL}/productos`)
      if (response.data.success) {
        setProductos(response.data.data)
      }
    } catch (err) {
      console.error('Error al cargar productos:', err)
      alert('❌ No se pudo conectar con el servidor. ¿Está corriendo el backend?')
    } finally {
      setLoading(false)
    }
  }
  
  const handleSubirFoto = async (productoId, file) => {
    if (!file) return
    
    // Validar tipo de archivo
    if (!file.type.startsWith('image/')) {
      alert('Por favor selecciona una imagen válida')
      return
    }
    
    // Validar tamaño (máx 5MB)
    if (file.size > 5 * 1024 * 1024) {
      alert('La imagen no puede superar los 5MB')
      return
    }
    
    try {
      setUploadingFoto(true)
      const formData = new FormData()
      formData.append('imagen', file)
      
      const response = await axios.post(
        `${API_URL}/upload/producto/${productoId}/foto`,
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' }
        }
      )
      
      if (response.data.success) {
        alert('✅ Foto actualizada exitosamente')
        setEditandoFoto(null)
        cargarProductos() // Recargar productos
      }
    } catch (err) {
      console.error('Error al subir foto:', err)
      alert('❌ Error al subir la foto: ' + (err.response?.data?.error || err.message))
    } finally {
      setUploadingFoto(false)
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
          <div className="col-span-full text-center py-12">
            <p className="text-gray-500 mb-4">No hay productos disponibles</p>
            <p className="text-sm text-gray-400">
              Ejecuta <code className="bg-gray-100 px-2 py-1 rounded">python3 importar_datos_demo.py</code> para cargar datos de ejemplo
            </p>
          </div>
        ) : (
          productos.map((producto) => (
            <div
              key={producto.id}
              className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow"
            >
              {/* Imagen */}
              <div className="relative h-48 bg-gradient-to-br from-primary-100 to-primary-200 flex items-center justify-center group">
                {producto.imagen_url ? (
                  <img 
                    src={`${API_URL}/upload/imagen/${producto.imagen_url}`}
                    alt={producto.nombre}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.target.style.display = 'none'
                      e.target.nextSibling.style.display = 'flex'
                    }}
                  />
                ) : null}
                <div className={producto.imagen_url ? 'hidden' : 'flex items-center justify-center w-full h-full'}>
                  <Flower2 className="h-16 w-16 text-primary-600" />
                </div>
                
                {/* Botón para cambiar foto */}
                <button
                  onClick={() => setEditandoFoto(producto.id)}
                  className="absolute top-2 right-2 bg-white/90 hover:bg-white p-2 rounded-full shadow-lg opacity-0 group-hover:opacity-100 transition-opacity"
                  title="Cambiar foto"
                >
                  <Camera className="h-4 w-4 text-gray-700" />
                </button>
              </div>
              
              {/* Modal de edición de foto */}
              {editandoFoto === producto.id && (
                <div className="absolute inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setEditandoFoto(null)}>
                  <div className="bg-white p-6 rounded-lg shadow-xl max-w-md w-full mx-4" onClick={(e) => e.stopPropagation()}>
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold">Cambiar Foto - {producto.nombre}</h3>
                      <button onClick={() => setEditandoFoto(null)} className="text-gray-400 hover:text-gray-600">
                        <X className="h-5 w-5" />
                      </button>
                    </div>
                    
                    <div className="space-y-4">
                      <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                        <input
                          type="file"
                          accept="image/*"
                          onChange={(e) => handleSubirFoto(producto.id, e.target.files[0])}
                          className="hidden"
                          id={`file-${producto.id}`}
                          disabled={uploadingFoto}
                        />
                        <label htmlFor={`file-${producto.id}`} className="cursor-pointer">
                          <Upload className="h-12 w-12 text-gray-400 mx-auto mb-2" />
                          <p className="text-sm text-gray-600">
                            {uploadingFoto ? 'Subiendo...' : 'Haz clic para seleccionar una imagen'}
                          </p>
                          <p className="text-xs text-gray-400 mt-1">PNG, JPG, JPEG (máx. 5MB)</p>
                        </label>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              
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
                  
                  {producto.colores_asociados && (
                    <div className="flex items-center justify-between">
                      <span className="text-gray-500">Colores:</span>
                      <span className="font-medium text-gray-900 text-xs">{producto.colores_asociados}</span>
                    </div>
                  )}
                  
                  {producto.tamano && (
                    <div className="flex items-center justify-between">
                      <span className="text-gray-500">Tamaño:</span>
                      <span className="font-medium text-gray-900">{producto.tamano}</span>
                    </div>
                  )}
                  
                  {producto.vista_360_180 && (
                    <div className="flex items-center justify-between">
                      <span className="text-gray-500">Vista:</span>
                      <span className="font-medium text-gray-900">{producto.vista_360_180}°</span>
                    </div>
                  )}
                </div>
                
                <div className="mt-4 pt-4 border-t border-gray-100 flex items-center justify-between">
                  <span className="text-xl font-bold text-primary-600">
                    ${producto.precio_venta?.toLocaleString('es-CL') || '0'}
                  </span>
                  <button 
                    onClick={() => setProductoDetalle(producto)}
                    className="text-sm text-primary-600 hover:text-primary-700 font-medium hover:underline"
                  >
                    Ver detalles →
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
      
      {/* Modal de detalles del producto */}
      {productoDetalle && (
        <div 
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
          onClick={() => setProductoDetalle(null)}
        >
          <div 
            className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header del modal */}
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-900">{productoDetalle.nombre}</h2>
              <button 
                onClick={() => setProductoDetalle(null)}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <X className="h-6 w-6" />
              </button>
            </div>
            
            {/* Contenido del modal */}
            <div className="p-6 space-y-6">
              {/* Imagen */}
              <div className="relative h-64 bg-gradient-to-br from-primary-100 to-primary-200 rounded-lg overflow-hidden">
                {productoDetalle.imagen_url ? (
                  <img 
                    src={`${API_URL}/upload/imagen/${productoDetalle.imagen_url}`}
                    alt={productoDetalle.nombre}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.target.style.display = 'none'
                      e.target.nextSibling.style.display = 'flex'
                    }}
                  />
                ) : null}
                <div className={productoDetalle.imagen_url ? 'hidden' : 'flex items-center justify-center w-full h-full'}>
                  <Flower2 className="h-24 w-24 text-primary-600" />
                </div>
              </div>
              
              {/* Información básica */}
              <div>
                <h3 className="text-sm font-semibold text-gray-500 uppercase mb-2">Descripción</h3>
                <p className="text-gray-700">{productoDetalle.descripcion || 'Sin descripción'}</p>
              </div>
              
              {/* Detalles en grid */}
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-500 mb-1">Tipo de Arreglo</p>
                  <p className="font-semibold text-gray-900">{productoDetalle.tipo_arreglo}</p>
                </div>
                
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-500 mb-1">Precio</p>
                  <p className="font-semibold text-primary-600 text-xl">
                    ${productoDetalle.precio_venta?.toLocaleString('es-CL') || '0'}
                  </p>
                </div>
                
                {productoDetalle.tamano && (
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-500 mb-1">Tamaño</p>
                    <p className="font-semibold text-gray-900">{productoDetalle.tamano}</p>
                  </div>
                )}
                
                {productoDetalle.vista_360_180 && (
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-500 mb-1">Vista</p>
                    <p className="font-semibold text-gray-900">{productoDetalle.vista_360_180}°</p>
                  </div>
                )}
              </div>
              
              {/* Colores */}
              {productoDetalle.colores_asociados && (
                <div>
                  <h3 className="text-sm font-semibold text-gray-500 uppercase mb-2">Colores Asociados</h3>
                  <div className="flex flex-wrap gap-2">
                    {productoDetalle.colores_asociados.split(',').map((color, idx) => (
                      <span 
                        key={idx}
                        className="px-3 py-1 bg-primary-100 text-primary-800 rounded-full text-sm font-medium"
                      >
                        {color.trim()}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Flores */}
              {productoDetalle.flores_asociadas && (
                <div>
                  <h3 className="text-sm font-semibold text-gray-500 uppercase mb-2">Flores Asociadas</h3>
                  <div className="flex flex-wrap gap-2">
                    {productoDetalle.flores_asociadas.split(',').map((flor, idx) => (
                      <span 
                        key={idx}
                        className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium"
                      >
                        {flor.trim()}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Contenedor */}
              {productoDetalle.tipos_macetero && (
                <div>
                  <h3 className="text-sm font-semibold text-gray-500 uppercase mb-2">Contenedor</h3>
                  <p className="text-gray-700">{productoDetalle.tipos_macetero}</p>
                </div>
              )}
              
              {/* Cuidados */}
              {productoDetalle.cuidados && (
                <div>
                  <h3 className="text-sm font-semibold text-gray-500 uppercase mb-2">Instrucciones de Cuidado</h3>
                  <p className="text-gray-700 text-sm leading-relaxed">{productoDetalle.cuidados}</p>
                </div>
              )}
              
              {/* Estado */}
              <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                <div className="flex items-center gap-2">
                  {productoDetalle.disponible_shopify ? (
                    <>
                      <CheckCircle className="h-5 w-5 text-green-500" />
                      <span className="text-sm text-gray-700">Disponible en Shopify</span>
                    </>
                  ) : (
                    <>
                      <XCircle className="h-5 w-5 text-gray-400" />
                      <span className="text-sm text-gray-500">No disponible en Shopify</span>
                    </>
                  )}
                </div>
                <span className="text-xs text-gray-400">ID: {productoDetalle.id}</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ProductosPage
