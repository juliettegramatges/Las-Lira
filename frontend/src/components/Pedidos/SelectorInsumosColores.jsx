import { useState, useEffect } from 'react'
import { AlertCircle, CheckCircle, Package } from 'lucide-react'
import axios from 'axios'

const API_URL = 'http://localhost:5001/api'

/**
 * Componente para seleccionar insumos (flores) por color para un producto
 * Muestra los colores del producto y permite elegir qué flores usar
 */
function SelectorInsumosColores({ productoId, onInsumosChange, onCostoChange }) {
  const [configuracion, setConfiguracion] = useState(null)
  const [loading, setLoading] = useState(false)
  const [seleccion, setSeleccion] = useState({}) // { colorId: { florId, cantidad } }
  const [contenedorSeleccionado, setContenedorSeleccionado] = useState(null)
  const [contenedores, setContenedores] = useState([])
  
  // Cargar configuración del producto cuando cambia
  useEffect(() => {
    if (productoId) {
      cargarConfiguracion()
      cargarContenedores()
    } else {
      setConfiguracion(null)
      setSeleccion({})
      setContenedorSeleccionado(null)
    }
  }, [productoId])
  
  // Calcular costo total cuando cambia la selección
  useEffect(() => {
    if (configuracion && Object.keys(seleccion).length > 0) {
      calcularCostoTotal()
      notificarCambios()
    }
  }, [seleccion, contenedorSeleccionado])
  
  const cargarConfiguracion = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`${API_URL}/productos/${productoId}/configuracion-completa`)
      
      if (response.data.success) {
        const config = response.data.data
        setConfiguracion(config)
        
        // Inicializar selección con flores predeterminadas
        const seleccionInicial = {}
        config.colores.forEach(color => {
          const florPredeterminada = color.flores_disponibles.find(f => f.es_predeterminada)
          if (florPredeterminada) {
            seleccionInicial[color.id] = {
              florId: florPredeterminada.flor_id,
              cantidad: color.cantidad_sugerida,
              flor: florPredeterminada
            }
          }
        })
        setSeleccion(seleccionInicial)
      }
    } catch (error) {
      console.error('Error al cargar configuración:', error)
    } finally {
      setLoading(false)
    }
  }
  
  const cargarContenedores = async () => {
    try {
      const response = await axios.get(`${API_URL}/inventario/contenedores`)
      if (response.data.success) {
        setContenedores(response.data.data)
      }
    } catch (error) {
      console.error('Error al cargar contenedores:', error)
    }
  }
  
  const handleFlorChange = (colorId, florId) => {
    const color = configuracion.colores.find(c => c.id === colorId)
    const flor = color.flores_disponibles.find(f => f.flor_id === florId)
    
    setSeleccion(prev => ({
      ...prev,
      [colorId]: {
        florId,
        cantidad: color.cantidad_sugerida,
        flor
      }
    }))
  }
  
  const handleCantidadChange = (colorId, nuevaCantidad) => {
    setSeleccion(prev => ({
      ...prev,
      [colorId]: {
        ...prev[colorId],
        cantidad: parseInt(nuevaCantidad) || 0
      }
    }))
  }
  
  const handleContenedorChange = (contenedorId) => {
    const contenedor = contenedores.find(c => c.id === contenedorId)
    setContenedorSeleccionado(contenedor)
  }
  
  const calcularCostoTotal = () => {
    let costoFlores = 0
    
    Object.values(seleccion).forEach(({ flor, cantidad }) => {
      if (flor && flor.flor_costo) {
        costoFlores += flor.flor_costo * cantidad
      }
    })
    
    const costoContenedor = contenedorSeleccionado ? parseFloat(contenedorSeleccionado.costo_unitario) : 0
    const costoTotal = costoFlores + costoContenedor
    
    if (onCostoChange) {
      onCostoChange({
        flores: costoFlores,
        contenedor: costoContenedor,
        total: costoTotal
      })
    }
  }
  
  const notificarCambios = () => {
    if (!onInsumosChange) return
    
    const insumos = {
      flores: Object.entries(seleccion).map(([colorId, data]) => ({
        color_id: parseInt(colorId),
        color_nombre: configuracion.colores.find(c => c.id === parseInt(colorId))?.nombre_color,
        flor_id: data.florId,
        cantidad: data.cantidad,
        costo_unitario: data.flor.flor_costo,
        costo_total: data.flor.flor_costo * data.cantidad
      })),
      contenedor: contenedorSeleccionado ? {
        contenedor_id: contenedorSeleccionado.id,
        cantidad: 1,
        costo_unitario: parseFloat(contenedorSeleccionado.costo_unitario),
        costo_total: parseFloat(contenedorSeleccionado.costo_unitario)
      } : null
    }
    
    onInsumosChange(insumos)
  }
  
  if (!productoId) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 text-center">
        <Package className="h-12 w-12 text-gray-400 mx-auto mb-2" />
        <p className="text-gray-500">Selecciona un producto para configurar los insumos</p>
      </div>
    )
  }
  
  if (loading) {
    return (
      <div className="bg-white border border-gray-200 rounded-lg p-6 text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
        <p className="mt-2 text-gray-500">Cargando configuración...</p>
      </div>
    )
  }
  
  if (!configuracion || !configuracion.tiene_configuracion) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div className="flex items-start">
          <AlertCircle className="h-5 w-5 text-yellow-600 mt-0.5 mr-2" />
          <div>
            <p className="text-sm font-medium text-yellow-800">Producto sin configuración de colores</p>
            <p className="text-xs text-yellow-700 mt-1">Este producto aún no tiene colores y flores configuradas.</p>
          </div>
        </div>
      </div>
    )
  }
  
  return (
    <div className="space-y-4">
      {/* Resumen de disponibilidad */}
      <div className={`border rounded-lg p-4 ${configuracion.hay_stock_completo ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
        <div className="flex items-center">
          {configuracion.hay_stock_completo ? (
            <CheckCircle className="h-5 w-5 text-green-600 mr-2" />
          ) : (
            <AlertCircle className="h-5 w-5 text-red-600 mr-2" />
          )}
          <div>
            <p className={`text-sm font-medium ${configuracion.hay_stock_completo ? 'text-green-800' : 'text-red-800'}`}>
              {configuracion.hay_stock_completo ? '✅ Hay stock disponible para este arreglo' : '⚠️ Stock insuficiente para algunos colores'}
            </p>
            <p className="text-xs text-gray-600 mt-0.5">
              Costo estimado: ${configuracion.costo_estimado_flores?.toLocaleString('es-CL')} | 
              Precio venta: ${configuracion.precio_venta?.toLocaleString('es-CL')} | 
              Margen: ${configuracion.margen_estimado?.toLocaleString('es-CL')}
            </p>
          </div>
        </div>
      </div>
      
      {/* Selección de flores por color */}
      <div className="space-y-4">
        <h4 className="font-semibold text-gray-900 flex items-center">
          🎨 Flores por Color
        </h4>
        
        {configuracion.colores.map((color) => (
          <div key={color.id} className="bg-white border border-gray-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <div>
                <h5 className="font-medium text-gray-900">{color.nombre_color}</h5>
                <p className="text-xs text-gray-500">Cantidad sugerida: {color.cantidad_sugerida} tallos</p>
              </div>
              {!color.tiene_stock && (
                <span className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded">Sin stock</span>
              )}
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {/* Selector de flor */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tipo de flor
                </label>
                <select
                  value={seleccion[color.id]?.florId || ''}
                  onChange={(e) => handleFlorChange(color.id, e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  {color.flores_disponibles.map((flor) => (
                    <option key={flor.flor_id} value={flor.flor_id}>
                      {flor.flor_nombre} - ${flor.flor_costo?.toLocaleString('es-CL')} 
                      {!flor.hay_stock_suficiente && ' ⚠️ Stock bajo'}
                      {flor.es_predeterminada && ' ⭐'}
                    </option>
                  ))}
                </select>
                {seleccion[color.id]?.flor && (
                  <p className="text-xs text-gray-500 mt-1">
                    📦 Disponible: <span className="font-semibold">{seleccion[color.id].flor.flor_disponible || seleccion[color.id].flor.flor_stock}</span> {seleccion[color.id].flor.flor_unidad}
                    {seleccion[color.id].flor.flor_en_uso > 0 && (
                      <span className="text-amber-600 ml-2">
                        ({seleccion[color.id].flor.flor_en_uso} en uso)
                      </span>
                    )}
                  </p>
                )}
              </div>
              
              {/* Cantidad */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Cantidad
                </label>
                <input
                  type="number"
                  min="1"
                  value={seleccion[color.id]?.cantidad || color.cantidad_sugerida}
                  onChange={(e) => handleCantidadChange(color.id, e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
                {seleccion[color.id]?.flor && (
                  <p className="text-xs text-gray-600 mt-1">
                    Costo: ${(seleccion[color.id].flor.flor_costo * seleccion[color.id].cantidad)?.toLocaleString('es-CL')}
                  </p>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {/* Selección de contenedor */}
      {configuracion.producto.tipo_arreglo !== 'Sin Contenedor' && (
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h5 className="font-medium text-gray-900 mb-3">🏺 Contenedor</h5>
          <select
            value={contenedorSeleccionado?.id || ''}
            onChange={(e) => handleContenedorChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="">Seleccionar contenedor...</option>
            {contenedores
              .filter(c => c.tipo.includes(configuracion.producto.tipo_arreglo.replace('Con ', '')))
              .map(contenedor => (
                <option key={contenedor.id} value={contenedor.id}>
                  {contenedor.tipo} {contenedor.material} - ${parseFloat(contenedor.costo_unitario).toLocaleString('es-CL')} 
                  (Stock: {contenedor.cantidad_stock})
                </option>
              ))}
          </select>
        </div>
      )}
    </div>
  )
}

export default SelectorInsumosColores

