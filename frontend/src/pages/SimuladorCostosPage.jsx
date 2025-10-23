import { useState, useEffect, useMemo } from 'react'
import axios from 'axios'
import { Calculator, RefreshCw, TrendingUp, Package, DollarSign } from 'lucide-react'

const API_URL = 'http://localhost:8000/api'

function SimuladorCostosPage() {
  const [productos, setProductos] = useState([])
  const [productoSeleccionado, setProductoSeleccionado] = useState(null)
  const [configuracion, setConfiguracion] = useState(null)
  const [loading, setLoading] = useState(false)
  
  // Estado de la simulación
  const [simulacion, setSimulacion] = useState({
    flores: {},      // { colorId: { florId, cantidad, costo } }
    contenedor: null // { contenedorId, costo }
  })
  
  const [contenedores, setContenedores] = useState([])

  useEffect(() => {
    cargarProductos()
    cargarContenedores()
  }, [])

  const cargarProductos = async () => {
    try {
      const response = await axios.get(`${API_URL}/productos`)
      if (response.data.success) {
        setProductos(response.data.data)
      }
    } catch (error) {
      console.error('Error al cargar productos:', error)
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

  const cargarConfiguracion = async (productoId) => {
    try {
      setLoading(true)
      const response = await axios.get(`${API_URL}/productos/${productoId}/configuracion-completa`)
      
      if (response.data.success) {
        const config = response.data.data
        setConfiguracion(config)
        
        // Inicializar simulación con receta predeterminada
        const floresIniciales = {}
        config.colores.forEach(color => {
          const florPredeterminada = color.flores_disponibles.find(f => f.es_predeterminada)
          if (florPredeterminada) {
            floresIniciales[color.id] = {
              florId: florPredeterminada.flor_id,
              florNombre: florPredeterminada.flor_nombre,
              cantidad: color.cantidad_sugerida,
              costoUnitario: florPredeterminada.flor_costo,
              costoTotal: florPredeterminada.flor_costo * color.cantidad_sugerida
            }
          }
        })
        
        setSimulacion({
          flores: floresIniciales,
          contenedor: null
        })
      }
    } catch (error) {
      console.error('Error al cargar configuración:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleProductoChange = (productoId) => {
    const producto = productos.find(p => p.id === productoId)
    setProductoSeleccionado(producto)
    if (productoId) {
      cargarConfiguracion(productoId)
    } else {
      setConfiguracion(null)
      setSimulacion({ flores: {}, contenedor: null })
    }
  }

  const handleFlorChange = (colorId, florId) => {
    const color = configuracion.colores.find(c => c.id === colorId)
    const flor = color.flores_disponibles.find(f => f.flor_id === florId)
    
    setSimulacion(prev => ({
      ...prev,
      flores: {
        ...prev.flores,
        [colorId]: {
          florId,
          florNombre: flor.flor_nombre,
          cantidad: prev.flores[colorId]?.cantidad || color.cantidad_sugerida,
          costoUnitario: flor.flor_costo,
          costoTotal: flor.flor_costo * (prev.flores[colorId]?.cantidad || color.cantidad_sugerida)
        }
      }
    }))
  }

  const handleCantidadChange = (colorId, nuevaCantidad) => {
    setSimulacion(prev => {
      const florActual = prev.flores[colorId]
      if (!florActual) return prev
      
      return {
        ...prev,
        flores: {
          ...prev.flores,
          [colorId]: {
            ...florActual,
            cantidad: parseInt(nuevaCantidad) || 0,
            costoTotal: florActual.costoUnitario * (parseInt(nuevaCantidad) || 0)
          }
        }
      }
    })
  }

  const handleContenedorChange = (contenedorId) => {
    if (!contenedorId) {
      setSimulacion(prev => ({ ...prev, contenedor: null }))
      return
    }
    
    const contenedor = contenedores.find(c => c.id === contenedorId)
    setSimulacion(prev => ({
      ...prev,
      contenedor: {
        contenedorId,
        contenedorNombre: `${contenedor.tipo} ${contenedor.material}`,
        costo: parseFloat(contenedor.costo)
      }
    }))
  }

  const resetearReceta = () => {
    if (!configuracion) return
    
    const floresIniciales = {}
    configuracion.colores.forEach(color => {
      const florPredeterminada = color.flores_disponibles.find(f => f.es_predeterminada)
      if (florPredeterminada) {
        floresIniciales[color.id] = {
          florId: florPredeterminada.flor_id,
          florNombre: florPredeterminada.flor_nombre,
          cantidad: color.cantidad_sugerida,
          costoUnitario: florPredeterminada.flor_costo,
          costoTotal: florPredeterminada.flor_costo * color.cantidad_sugerida
        }
      }
    })
    
    setSimulacion({
      flores: floresIniciales,
      contenedor: null
    })
  }

  // Cálculos
  const costoFlores = useMemo(() => {
    return Object.values(simulacion.flores).reduce((sum, f) => sum + f.costoTotal, 0)
  }, [simulacion.flores])

  const costoContenedor = simulacion.contenedor?.costo || 0
  const costoTotal = costoFlores + costoContenedor
  const precioVenta = productoSeleccionado?.precio_venta || 0
  const margen = precioVenta - costoTotal
  const porcentajeMargen = precioVenta > 0 ? ((margen / precioVenta) * 100) : 0

  // Comparación con receta original
  const costoRecetaOriginal = configuracion?.costo_estimado_flores || 0
  const diferenciaConReceta = costoTotal - costoRecetaOriginal
  const porcentajeDiferencia = costoRecetaOriginal > 0 ? ((diferenciaConReceta / costoRecetaOriginal) * 100) : 0

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Calculator className="h-7 w-7 text-primary-600" />
            Simulador de Costos
          </h1>
          <p className="text-gray-600 mt-1">
            Calcula costos de arreglos con combinaciones personalizadas
          </p>
        </div>
      </div>

      {/* Selector de Producto */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          Selecciona un Producto
        </label>
        <select
          value={productoSeleccionado?.id || ''}
          onChange={(e) => handleProductoChange(e.target.value)}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 text-lg"
        >
          <option value="">-- Selecciona un producto --</option>
          {productos.map(prod => (
            <option key={prod.id} value={prod.id}>
              {prod.nombre} - ${prod.precio_venta?.toLocaleString('es-CL')}
            </option>
          ))}
        </select>
      </div>

      {loading && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-500">Cargando configuración...</p>
        </div>
      )}

      {!loading && configuracion && (
        <>
          {/* Configuración de Insumos */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Panel de Simulación */}
            <div className="lg:col-span-2 space-y-4">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-bold text-gray-900">🎨 Configuración de Flores</h2>
                  <button
                    onClick={resetearReceta}
                    className="flex items-center gap-2 px-3 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                  >
                    <RefreshCw className="h-4 w-4" />
                    Resetear Receta
                  </button>
                </div>

                <div className="space-y-4">
                  {configuracion.colores.map((color) => (
                    <div key={color.id} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                      <h3 className="font-semibold text-gray-900 mb-3">{color.nombre_color}</h3>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                        {/* Tipo de Flor */}
                        <div className="md:col-span-2">
                          <label className="block text-xs font-medium text-gray-700 mb-1">
                            Tipo de Flor
                          </label>
                          <select
                            value={simulacion.flores[color.id]?.florId || ''}
                            onChange={(e) => handleFlorChange(color.id, e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                          >
                            {color.flores_disponibles.map((flor) => (
                              <option key={flor.flor_id} value={flor.flor_id}>
                                {flor.flor_nombre} - ${flor.flor_costo?.toLocaleString('es-CL')}
                                {flor.es_predeterminada && ' ⭐ (Receta)'}
                              </option>
                            ))}
                          </select>
                        </div>

                        {/* Cantidad */}
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">
                            Cantidad
                          </label>
                          <input
                            type="number"
                            min="0"
                            value={simulacion.flores[color.id]?.cantidad || 0}
                            onChange={(e) => handleCantidadChange(color.id, e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                          />
                        </div>
                      </div>

                      {/* Costo del color */}
                      <div className="mt-2 text-right">
                        <span className="text-sm text-gray-600">Costo: </span>
                        <span className="text-lg font-bold text-primary-600">
                          ${simulacion.flores[color.id]?.costoTotal?.toLocaleString('es-CL')}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Contenedor */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h2 className="text-lg font-bold text-gray-900 mb-4">🏺 Contenedor</h2>
                <select
                  value={simulacion.contenedor?.contenedorId || ''}
                  onChange={(e) => handleContenedorChange(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="">Sin contenedor</option>
                  {contenedores
                    .filter(c => c.tipo.toLowerCase().includes(productoSeleccionado?.tipo_arreglo?.toLowerCase()?.replace('con ', '') || ''))
                    .map(cont => (
                      <option key={cont.id} value={cont.id}>
                        {cont.tipo} {cont.material} - ${parseFloat(cont.costo).toLocaleString('es-CL')}
                      </option>
                    ))}
                </select>
              </div>
            </div>

            {/* Panel de Resultados */}
            <div className="space-y-4">
              {/* Costos Calculados */}
              <div className="bg-gradient-to-br from-primary-50 to-primary-100 rounded-lg shadow-sm border-2 border-primary-200 p-6">
                <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                  <DollarSign className="h-5 w-5" />
                  Costos Calculados
                </h2>

                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-700">Flores:</span>
                    <span className="font-semibold text-gray-900">${costoFlores.toLocaleString('es-CL')}</span>
                  </div>

                  <div className="flex justify-between items-center">
                    <span className="text-gray-700">Contenedor:</span>
                    <span className="font-semibold text-gray-900">${costoContenedor.toLocaleString('es-CL')}</span>
                  </div>

                  <div className="border-t-2 border-primary-300 pt-2 mt-2">
                    <div className="flex justify-between items-center">
                      <span className="text-gray-900 font-bold">Costo Total:</span>
                      <span className="text-2xl font-bold text-primary-600">${costoTotal.toLocaleString('es-CL')}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Análisis de Margen */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                  <TrendingUp className="h-5 w-5" />
                  Análisis de Margen
                </h2>

                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-700">Precio Venta:</span>
                    <span className="font-semibold text-gray-900">${precioVenta.toLocaleString('es-CL')}</span>
                  </div>

                  <div className="flex justify-between items-center">
                    <span className="text-gray-700">Costo:</span>
                    <span className="font-semibold text-gray-900">-${costoTotal.toLocaleString('es-CL')}</span>
                  </div>

                  <div className={`border-t-2 pt-2 mt-2 ${margen >= 0 ? 'border-green-300' : 'border-red-300'}`}>
                    <div className="flex justify-between items-center">
                      <span className="font-bold text-gray-900">Margen:</span>
                      <span className={`text-xl font-bold ${margen >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        ${margen.toLocaleString('es-CL')}
                      </span>
                    </div>
                    <div className="text-right text-sm mt-1">
                      <span className={margen >= 0 ? 'text-green-600' : 'text-red-600'}>
                        ({porcentajeMargen.toFixed(1)}%)
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Comparación con Receta Original */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                  <Package className="h-5 w-5" />
                  vs Receta Original
                </h2>

                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-700">Costo Receta:</span>
                    <span className="font-semibold text-gray-900">${costoRecetaOriginal.toLocaleString('es-CL')}</span>
                  </div>

                  <div className="flex justify-between items-center">
                    <span className="text-gray-700">Diferencia:</span>
                    <span className={`font-bold ${diferenciaConReceta > 0 ? 'text-red-600' : 'text-green-600'}`}>
                      {diferenciaConReceta > 0 ? '+' : ''}${diferenciaConReceta.toLocaleString('es-CL')}
                    </span>
                  </div>

                  <div className="text-sm text-gray-500 text-center mt-2">
                    {diferenciaConReceta > 0 ? '📈' : '📉'} {Math.abs(porcentajeDiferencia).toFixed(1)}% {diferenciaConReceta > 0 ? 'más caro' : 'más barato'}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </>
      )}

      {!loading && !configuracion && productoSeleccionado && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
          <p className="text-yellow-800">
            Este producto aún no tiene configuración de colores y flores.
          </p>
        </div>
      )}
    </div>
  )
}

export default SimuladorCostosPage

