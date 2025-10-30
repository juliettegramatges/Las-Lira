import { useState, useEffect, useMemo } from 'react'
import axios from 'axios'
import { Flower2, CheckCircle, XCircle, Upload, X, Camera, Package, ShoppingBag, DollarSign, AlertCircle, Calculator, RefreshCw, Plus, Trash2, Save, Download, Search, ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react'

const API_URL = 'http://localhost:5001/api'

// Función para limpiar HTML de las descripciones
const limpiarHTML = (html) => {
  if (!html) return ''
  // Crear un elemento temporal para extraer solo el texto
  const temp = document.createElement('div')
  temp.innerHTML = html
  return temp.textContent || temp.innerText || ''
}

// Colores comunes para productos
const COLORES_PRODUCTOS = [
  'Rojo',
  'Rosado',
  'Blanco',
  'Amarillo',
  'Naranja',
  'Morado',
  'Lila',
  'Azul',
  'Verde',
  'Fucsia',
  'Coral',
  'Crema',
  'Burdeo',
  'Multicolor',
  'Natural',
  'Blancos',
  'Rojos',
  'Rosados',
  'Verdes',
  'Azules',
  'Naranjos'
]

function ProductosPage() {
  const [productos, setProductos] = useState([])
  const [loading, setLoading] = useState(true)
  const [editandoFoto, setEditandoFoto] = useState(null)
  const [uploadingFoto, setUploadingFoto] = useState(false)
  const [productoDetalle, setProductoDetalle] = useState(null)
  const [receta, setReceta] = useState(null)
  const [loadingReceta, setLoadingReceta] = useState(false)
  
  // Estados de paginación y búsqueda
  const [busqueda, setBusqueda] = useState('')
  const [paginaActual, setPaginaActual] = useState(1)
  const [totalPaginas, setTotalPaginas] = useState(1)
  const [totalProductos, setTotalProductos] = useState(0)
  const [statsGlobales, setStatsGlobales] = useState({
    total_global: 0,
    con_foto: 0,
    sin_foto: 0,
    disponibles_shopify: 0
  })
  const limitePorPagina = 50
  
  // Estados del Simulador de Costos
  const [mostrarSimulador, setMostrarSimulador] = useState(false)
  const [configuracion, setConfiguracion] = useState(null)
  const [loadingConfig, setLoadingConfig] = useState(false)
  const [simulacion, setSimulacion] = useState({
    flores: {},      // { colorId: [{ id, florId, cantidad, costo... }] }
    contenedor: null
  })
  const [contenedores, setContenedores] = useState([])
  const [todasLasFlores, setTodasLasFlores] = useState([]) // Todas las flores del inventario
  const [guardandoReceta, setGuardandoReceta] = useState(false)
  const [coloresEditables, setColoresEditables] = useState([]) // Lista editable de colores
  const [precioVentaEditado, setPrecioVentaEditado] = useState(null) // Precio de venta modificado
  
  const cargarProductos = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`${API_URL}/productos/`)
      
      if (response.data.success) {
        const productosData = response.data.productos || []
        
        // Aplicar filtro de búsqueda si existe
        let productosFiltrados = productosData
        if (busqueda) {
          productosFiltrados = productosData.filter(producto => 
            producto.nombre?.toLowerCase().includes(busqueda.toLowerCase()) ||
            producto.categoria?.toLowerCase().includes(busqueda.toLowerCase()) ||
            producto.tipo?.toLowerCase().includes(busqueda.toLowerCase())
          )
        }
        
        // Aplicar paginación
        const inicio = (paginaActual - 1) * limitePorPagina
        const fin = inicio + limitePorPagina
        const productosPaginados = productosFiltrados.slice(inicio, fin)
        
        setProductos(productosPaginados)
        setTotalProductos(productosFiltrados.length)
        setTotalPaginas(Math.ceil(productosFiltrados.length / limitePorPagina))
        
        // Calcular estadísticas básicas
        const stats = {
          total_global: productosData.length,
          con_foto: productosData.filter(p => p.imagen_principal || (p.imagenes && p.imagenes.length > 0)).length,
          sin_foto: productosData.filter(p => !p.imagen_principal && (!p.imagenes || p.imagenes.length === 0)).length,
          disponibles_shopify: productosData.filter(p => p.sku && p.sku.trim() !== '').length
        }
        setStatsGlobales(stats)
      }
    } catch (err) {
      console.error('Error al cargar productos:', err)
      alert('❌ No se pudo conectar con el servidor. ¿Está corriendo el backend?')
      setProductos([])
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
      formData.append('file', file)  // ✅ Cambiado de 'imagen' a 'file'
      
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
  
  const cargarReceta = async (productoId) => {
    try {
      setLoadingReceta(true)
      const response = await axios.get(`${API_URL}/productos/${productoId}/receta`)
      if (response.data.success) {
        setReceta(response.data.data)
      }
    } catch (error) {
      console.error('Error al cargar receta:', error)
      setReceta(null)
    } finally {
      setLoadingReceta(false)
    }
  }
  
  const handleVerDetalles = (producto) => {
    setProductoDetalle(producto)
    setReceta(null)
    cargarReceta(producto.id)
  }
  
  // ============================================
  // FUNCIONES DEL SIMULADOR DE COSTOS
  // ============================================
  
  const abrirSimulador = async () => {
    setMostrarSimulador(true)
    setPrecioVentaEditado(null) // Resetear precio editado
    await Promise.all([
      cargarConfiguracionProducto(),
      cargarContenedores(),
      cargarTodasLasFlores()
    ])
  }
  
  const cargarTodasLasFlores = async () => {
    try {
      const response = await axios.get(`${API_URL}/inventario/flores`)
      if (response.data.success) {
        setTodasLasFlores(response.data.data)
      }
    } catch (error) {
      console.error('Error al cargar flores:', error)
    }
  }
  
  const cargarConfiguracionProducto = async () => {
    if (!productoDetalle) return
    
    try {
      setLoadingConfig(true)
      const response = await axios.get(`${API_URL}/productos/${productoDetalle.id}/configuracion-completa`)
      
      if (response.data.success) {
        const config = response.data.data
        setConfiguracion(config)
        
        // Si hay colores configurados, usarlos
        if (config.colores && config.colores.length > 0) {
          // Inicializar colores editables
          setColoresEditables(config.colores.map(c => ({
            id: c.id,
            nombre_color: c.nombre_color,
            cantidad_flores_sugerida: c.cantidad_flores_sugerida,
            flores_disponibles: c.flores_disponibles,
            esNuevo: false
          })))
          
          // Inicializar simulación con valores predeterminados
          const floresIniciales = {}
          config.colores.forEach(color => {
            const florPredeterminada = color.flores_disponibles.find(f => f.es_predeterminada)
            if (florPredeterminada) {
              floresIniciales[color.id] = [{
                id: Date.now(),
                florId: florPredeterminada.flor_id,
                cantidad: color.cantidad_flores_sugerida,
                costo: florPredeterminada.flor_costo
              }]
            }
          })
          
          setSimulacion({
            flores: floresIniciales,
            contenedor: config.contenedor_receta ? {
              contenedorId: config.contenedor_receta.id,
              costo: config.contenedor_receta.costo
            } : null
          })
        } else {
          // Si no hay colores configurados, cargar colores sugeridos desde colores_asociados
          try {
            const coloresResponse = await axios.get(`${API_URL}/productos/${productoDetalle.id}/colores-sugeridos`)
            
            if (coloresResponse.data.success && coloresResponse.data.data.length > 0) {
              const coloresSugeridos = coloresResponse.data.data
              
              // Crear colores editables con IDs temporales
              const coloresTemp = coloresSugeridos.map((nombreColor, index) => ({
                id: `temp-${index}`,
                nombre_color: nombreColor,
                cantidad_flores_sugerida: 10, // Cantidad por defecto
                flores_disponibles: [],
                esNuevo: true
              }))
              
              setColoresEditables(coloresTemp)
              
              // Inicializar simulación vacía
              const floresIniciales = {}
              coloresTemp.forEach(color => {
                floresIniciales[color.id] = []
              })
              
              setSimulacion({
                flores: floresIniciales,
                contenedor: config.contenedor_receta ? {
                  contenedorId: config.contenedor_receta.id,
                  costo: config.contenedor_receta.costo
                } : null
              })
            } else {
              // Si no hay colores sugeridos, inicializar con un color vacío
              setColoresEditables([{
                id: 'temp-0',
                nombre_color: 'Nuevo Color',
                cantidad_flores_sugerida: 10,
                flores_disponibles: [],
                esNuevo: true
              }])
              
              setSimulacion({
                flores: { 'temp-0': [] },
                contenedor: null
              })
            }
          } catch (err) {
            console.error('Error al cargar colores sugeridos:', err)
            // Fallback: inicializar con un color vacío
            setColoresEditables([{
              id: 'temp-0',
              nombre_color: 'Nuevo Color',
              cantidad_flores_sugerida: 10,
              flores_disponibles: [],
              esNuevo: true
            }])
            
            setSimulacion({
              flores: { 'temp-0': [] },
              contenedor: null
            })
          }
        }
      }
    } catch (error) {
      console.error('Error al cargar configuración:', error)
      alert('Error al cargar la configuración del producto')
    } finally {
      setLoadingConfig(false)
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
  
  const handleAgregarFlor = (colorId) => {
    setSimulacion(prev => ({
      ...prev,
      flores: {
        ...prev.flores,
        [colorId]: [
          ...(prev.flores[colorId] || []),
          { id: Date.now(), florId: '', cantidad: 1, costo: 0 }
        ]
      }
    }))
  }
  
  const handleEliminarFlor = (colorId, florIndex) => {
    setSimulacion(prev => ({
      ...prev,
      flores: {
        ...prev.flores,
        [colorId]: prev.flores[colorId].filter((_, idx) => idx !== florIndex)
      }
    }))
  }
  
  const handleFlorChange = (colorId, florIndex, florId) => {
    const color = coloresEditables.find(c => c.id === colorId)
    
    // Buscar la flor en las flores filtradas por color
    const floresFiltradas = obtenerFloresPorColor(color?.nombre_color || '')
    const florSeleccionada = floresFiltradas.find(f => f.flor_id === florId)
    
    setSimulacion(prev => ({
      ...prev,
      flores: {
        ...prev.flores,
        [colorId]: prev.flores[colorId].map((flor, idx) => 
          idx === florIndex 
            ? { ...flor, florId, costo: florSeleccionada?.flor_costo || 0 }
            : flor
        )
      }
    }))
  }
  
  const handleCantidadChange = (colorId, florIndex, cantidad) => {
    setSimulacion(prev => ({
      ...prev,
      flores: {
        ...prev.flores,
        [colorId]: prev.flores[colorId].map((flor, idx) => 
          idx === florIndex ? { ...flor, cantidad: parseInt(cantidad) || 0 } : flor
        )
      }
    }))
  }
  
  const handleContenedorChange = (contenedorId) => {
    const contenedor = contenedores.find(c => c.id === contenedorId)
    setSimulacion(prev => ({
      ...prev,
      contenedor: contenedor ? {
        contenedorId: contenedor.id,
        costo: contenedor.costo
      } : null
    }))
  }
  
  // Funciones para manejar colores
  const handleAgregarColor = () => {
    const nuevoColorId = `nuevo-${Date.now()}`
    const nuevoColor = {
      id: nuevoColorId,
      nombre_color: 'Nuevo Color',
      cantidad_flores_sugerida: 12,
      flores_disponibles: configuracion?.colores[0]?.flores_disponibles || [], // Usar las mismas flores del primer color
      esNuevo: true
    }
    
    setColoresEditables(prev => [...prev, nuevoColor])
    setSimulacion(prev => ({
      ...prev,
      flores: {
        ...prev.flores,
        [nuevoColorId]: []
      }
    }))
  }
  
  const handleEliminarColor = (colorId) => {
    if (coloresEditables.length <= 1) {
      alert('❌ Debe haber al menos un color en el producto')
      return
    }
    
    setColoresEditables(prev => prev.filter(c => c.id !== colorId))
    setSimulacion(prev => {
      const { [colorId]: removed, ...restFlores } = prev.flores
      return {
        ...prev,
        flores: restFlores
      }
    })
  }
  
  const handleEditarNombreColor = (colorId, nuevoNombre) => {
    setColoresEditables(prev => prev.map(c => 
      c.id === colorId ? { ...c, nombre_color: nuevoNombre } : c
    ))
  }
  
  // Función para obtener flores filtradas por color
  const obtenerFloresPorColor = (nombreColor) => {
    if (!nombreColor || !todasLasFlores || todasLasFlores.length === 0) {
      return []
    }
    
    // Filtrar flores que coincidan con el color
    return todasLasFlores
      .filter(flor => {
        const colorFlor = (flor.color || '').toLowerCase().trim()
        const colorBuscado = nombreColor.toLowerCase().trim()
        
        // Coincidencia exacta o parcial
        return colorFlor === colorBuscado || 
               colorFlor.includes(colorBuscado) ||
               colorBuscado.includes(colorFlor)
      })
      .map(flor => ({
        flor_id: flor.id,
        flor_nombre: flor.nombre,
        flor_costo: flor.costo_unitario || 0,
        flor_disponible: flor.cantidad_disponible || 0,
        color: flor.color
      }))
  }
  
  const resetearReceta = () => {
    if (!configuracion) return
    
    // Resetear colores editables a la configuración original
    setColoresEditables(configuracion.colores.map(c => ({
      id: c.id,
      nombre_color: c.nombre_color,
      cantidad_flores_sugerida: c.cantidad_flores_sugerida,
      flores_disponibles: c.flores_disponibles,
      esNuevo: false
    })))
    
    // Resetear precio editado
    setPrecioVentaEditado(null)
    
    // Resetear flores a las predeterminadas
    const floresIniciales = {}
    configuracion.colores.forEach(color => {
      const florPredeterminada = color.flores_disponibles.find(f => f.es_predeterminada)
      if (florPredeterminada) {
        floresIniciales[color.id] = [{
          id: Date.now(),
          florId: florPredeterminada.flor_id,
          cantidad: color.cantidad_flores_sugerida,
          costo: florPredeterminada.flor_costo
        }]
      }
    })
    
    setSimulacion({
      flores: floresIniciales,
      contenedor: configuracion.contenedor_receta ? {
        contenedorId: configuracion.contenedor_receta.id,
        costo: configuracion.contenedor_receta.costo
      } : null
    })
  }
  
  // Cálculos en tiempo real
  const costoFlores = useMemo(() => {
    let total = 0
    Object.values(simulacion.flores).forEach(floresColor => {
      floresColor.forEach(flor => {
        total += (flor.cantidad || 0) * (flor.costo || 0)
      })
    })
    return total
  }, [simulacion.flores])
  
  const costoContenedor = useMemo(() => {
    return simulacion.contenedor?.costo || 0
  }, [simulacion.contenedor])
  
  const costoTotal = costoFlores + costoContenedor
  const precioVenta = precioVentaEditado !== null ? precioVentaEditado : (productoDetalle?.precio_venta || 0)
  const margenActual = precioVenta - costoTotal
  const porcentajeMargen = precioVenta > 0 ? ((margenActual / precioVenta) * 100).toFixed(1) : 0
  
  const handleGuardarReceta = async () => {
    if (!productoDetalle || !coloresEditables) return
    
    try {
      setGuardandoReceta(true)
      
      // Preparar datos para enviar
      const coloresParaGuardar = coloresEditables.map(color => {
        const floresColor = simulacion.flores[color.id] || []
        
        // Obtener las flores seleccionadas con su info
        const floresConInfo = floresColor
          .filter(f => f.florId) // Solo las que tienen flor seleccionada
          .map(f => ({
            flor_id: f.florId,
            es_predeterminada: false // Por defecto ninguna es predeterminada
          }))
        
        // Marcar la primera como predeterminada si hay flores
        if (floresConInfo.length > 0) {
          floresConInfo[0].es_predeterminada = true
        }
        
        return {
          id: color.id,
          nombre_color: color.nombre_color,
          cantidad_flores_sugerida: color.cantidad_flores_sugerida,
          flores: floresConInfo
        }
      })
      
      const payload = {
        colores: coloresParaGuardar,
        precio_venta: precioVenta
      }
      
      const response = await axios.post(
        `${API_URL}/productos/${productoDetalle.id}/guardar-receta-completa`,
        payload
      )
      
      if (response.data.success) {
        alert(`✅ ${response.data.message}\n\n` +
              `🎨 Colores actualizados: ${response.data.data.colores_actualizados}\n` +
              `💰 Precio de venta: $${response.data.data.precio_venta.toLocaleString('es-CL')}`)
        
        // Recargar la configuración
        await cargarConfiguracionProducto()
        
        // Recargar productos para actualizar la lista
        await cargarProductos()
      } else {
        alert(`❌ Error: ${response.data.error}`)
      }
    } catch (error) {
      console.error('Error al guardar receta:', error)
      alert(`❌ Error al guardar receta:\n${error.response?.data?.error || error.message}`)
    } finally {
      setGuardandoReceta(false)
    }
  }
  
  useEffect(() => {
    cargarProductos()
  }, [paginaActual, busqueda])
  
  // Función para manejar cambio de búsqueda
  const handleBusquedaChange = (valor) => {
    setBusqueda(valor)
    setPaginaActual(1) // Resetear a página 1 al buscar
  }
  
  return (
    <div className="px-4 sm:px-0">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Catálogo de Productos</h1>
            <p className="mt-1 text-sm text-gray-600">
              {totalProductos} producto{totalProductos !== 1 ? 's' : ''} en total • Página {paginaActual} de {totalPaginas}
            </p>
          </div>
          <button 
            onClick={() => {
              window.open(`${API_URL}/exportar/productos`, '_blank')
            }}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center"
          >
            <Download className="h-5 w-5 mr-2" />
            Descargar Excel
          </button>
        </div>
        
        {/* Estadísticas Globales */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
          <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 font-medium">Total Productos</p>
                <p className="text-2xl font-bold text-gray-900">{statsGlobales.total_global}</p>
              </div>
              <Package className="h-8 w-8 text-blue-500" />
            </div>
          </div>
          
          <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 font-medium">Con Foto</p>
                <p className="text-2xl font-bold text-green-600">{statsGlobales.con_foto}</p>
              </div>
              <Camera className="h-8 w-8 text-green-500" />
            </div>
          </div>
          
          <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 font-medium">Sin Foto</p>
                <p className="text-2xl font-bold text-orange-600">{statsGlobales.sin_foto}</p>
              </div>
              <AlertCircle className="h-8 w-8 text-orange-500" />
            </div>
          </div>
          
          <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 font-medium">En Shopify</p>
                <p className="text-2xl font-bold text-purple-600">{statsGlobales.disponibles_shopify}</p>
              </div>
              <ShoppingBag className="h-8 w-8 text-purple-500" />
            </div>
          </div>
        </div>
        
        {/* Barra de Búsqueda */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Buscar productos por nombre, descripción o categoría..."
            value={busqueda}
            onChange={(e) => handleBusquedaChange(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
      </div>
      
      {/* Grid de productos */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {loading ? (
          <div className="col-span-full text-center py-12 text-gray-500">
            Cargando productos...
          </div>
        ) : (productos || []).length === 0 ? (
          <div className="col-span-full text-center py-12">
            <p className="text-gray-500 mb-4">No hay productos disponibles</p>
            <p className="text-sm text-gray-400">
              Ejecuta <code className="bg-gray-100 px-2 py-1 rounded">python3 importar_datos_demo.py</code> para cargar datos de ejemplo
            </p>
          </div>
        ) : (
          (productos || []).map((producto) => (
            <div
              key={producto.id}
              className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow"
            >
              {/* Imagen */}
              <div className="relative h-48 bg-gradient-to-br from-primary-100 to-primary-200 flex items-center justify-center group">
                {(producto.imagen_principal || (producto.imagenes && producto.imagenes.length > 0)) ? (
                  <img 
                    src={producto.imagen_principal || producto.imagenes[0]?.url}
                    alt={producto.nombre}
                    className="w-full h-full object-contain p-2"
                    onError={(e) => {
                      e.target.style.display = 'none'
                      e.target.nextSibling.style.display = 'flex'
                    }}
                  />
                ) : null}
                <div className={(producto.imagen_principal || (producto.imagenes && producto.imagenes.length > 0)) ? 'hidden' : 'flex items-center justify-center w-full h-full'}>
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
                  {limpiarHTML(producto.descripcion) || 'Sin descripción'}
                </p>
                
                <div className="space-y-2 text-sm">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-500">Tipo:</span>
                    <span className="font-medium text-gray-900">{producto.tipo || producto.tipo_arreglo || 'N/A'}</span>
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
                    ${(producto.precio || producto.precio_venta || 0).toLocaleString('es-CL')}
                  </span>
                  <button 
                    onClick={() => handleVerDetalles(producto)}
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
      
      {/* Paginación */}
      {!loading && totalPaginas > 1 && (
        <div className="mt-6 flex items-center justify-between border-t border-gray-200 bg-white px-4 py-3 sm:px-6 rounded-lg">
          <div className="flex flex-1 justify-between sm:hidden">
            <button
              onClick={() => setPaginaActual(Math.max(1, paginaActual - 1))}
              disabled={paginaActual === 1}
              className="relative inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Anterior
            </button>
            <button
              onClick={() => setPaginaActual(Math.min(totalPaginas, paginaActual + 1))}
              disabled={paginaActual === totalPaginas}
              className="relative ml-3 inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Siguiente
            </button>
          </div>
          <div className="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
            <div>
              <p className="text-sm text-gray-700">
                Mostrando{' '}
                <span className="font-medium">{(paginaActual - 1) * limitePorPagina + 1}</span>
                {' '}-{' '}
                <span className="font-medium">
                  {Math.min(paginaActual * limitePorPagina, totalProductos)}
                </span>
                {' '}de{' '}
                <span className="font-medium">{totalProductos}</span>
                {' '}productos
              </p>
            </div>
            <div>
              <nav className="isolate inline-flex -space-x-px rounded-md shadow-sm" aria-label="Pagination">
                <button
                  onClick={() => setPaginaActual(1)}
                  disabled={paginaActual === 1}
                  className="relative inline-flex items-center rounded-l-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronsLeft className="h-5 w-5" />
                </button>
                <button
                  onClick={() => setPaginaActual(Math.max(1, paginaActual - 1))}
                  disabled={paginaActual === 1}
                  className="relative inline-flex items-center px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronLeft className="h-5 w-5" />
                </button>
                
                <span className="relative inline-flex items-center px-4 py-2 text-sm font-semibold text-gray-900 ring-1 ring-inset ring-gray-300 focus:outline-offset-0">
                  {paginaActual} / {totalPaginas}
                </span>
                
                <button
                  onClick={() => setPaginaActual(Math.min(totalPaginas, paginaActual + 1))}
                  disabled={paginaActual === totalPaginas}
                  className="relative inline-flex items-center px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronRight className="h-5 w-5" />
                </button>
                <button
                  onClick={() => setPaginaActual(totalPaginas)}
                  disabled={paginaActual === totalPaginas}
                  className="relative inline-flex items-center rounded-r-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronsRight className="h-5 w-5" />
                </button>
              </nav>
            </div>
          </div>
        </div>
      )}
      
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
              <div className="relative h-64 bg-gradient-to-br from-primary-100 to-primary-200 rounded-lg overflow-hidden flex items-center justify-center">
                {(productoDetalle.imagen_principal || (productoDetalle.imagenes && productoDetalle.imagenes.length > 0)) ? (
                  <img 
                    src={productoDetalle.imagen_principal || productoDetalle.imagenes[0]?.url}
                    alt={productoDetalle.nombre}
                    className="w-full h-full object-contain"
                    onError={(e) => {
                      e.target.style.display = 'none'
                      e.target.nextSibling.style.display = 'flex'
                    }}
                  />
                ) : null}
                <div className={(productoDetalle.imagen_principal || (productoDetalle.imagenes && productoDetalle.imagenes.length > 0)) ? 'hidden' : 'flex items-center justify-center w-full h-full'}>
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
              
              {/* Recetario / Insumos Necesarios */}
              <div className="border-t border-gray-200 pt-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
                  <Package className="h-5 w-5 mr-2 text-primary-600" />
                  Recetario - Insumos Necesarios
                </h3>
                
                {loadingReceta ? (
                  <div className="text-center py-8 text-gray-500">
                    Cargando receta...
                  </div>
                ) : receta && receta.receta && receta.receta.length > 0 ? (
                  <div className="space-y-4">
                    {/* Lista de insumos */}
                    <div className="space-y-3">
                      {receta.receta.map((insumo) => (
                        <div 
                          key={insumo.id} 
                          className={`flex items-center gap-4 p-3 rounded-lg border ${
                            insumo.disponible ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
                          }`}
                        >
                          {/* Foto del insumo */}
                          <div className="w-16 h-16 bg-white rounded-lg overflow-hidden flex-shrink-0 shadow-sm">
                            {insumo.foto_url ? (
                              <img 
                                src={`${API_URL}/upload/imagen/${insumo.foto_url}`}
                                alt={insumo.nombre}
                                className="w-full h-full object-cover"
                                onError={(e) => {
                                  e.target.style.display = 'none'
                                  e.target.nextSibling.style.display = 'flex'
                                }}
                              />
                            ) : null}
                            <div className={insumo.foto_url ? 'hidden' : 'flex items-center justify-center w-full h-full bg-gray-100'}>
                              {insumo.tipo === 'Flor' ? (
                                <Flower2 className="h-6 w-6 text-gray-400" />
                              ) : (
                                <ShoppingBag className="h-6 w-6 text-gray-400" />
                              )}
                            </div>
                          </div>
                          
                          {/* Información del insumo */}
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span className={`text-xs px-2 py-0.5 rounded font-medium ${
                                insumo.tipo === 'Flor' ? 'bg-pink-100 text-pink-700' : 'bg-blue-100 text-blue-700'
                              }`}>
                                {insumo.tipo}
                              </span>
                              <h4 className="font-semibold text-gray-900">{insumo.nombre}</h4>
                            </div>
                            
                            <div className="flex items-center gap-4 text-sm text-gray-600">
                              <span>
                                <strong>{insumo.cantidad}</strong> {insumo.unidad}
                              </span>
                              <span>
                                ${insumo.costo_unitario?.toLocaleString('es-CL')} c/u
                              </span>
                              <span className="font-semibold text-gray-900">
                                Total: ${insumo.costo_total?.toLocaleString('es-CL')}
                              </span>
                            </div>
                            
                            {/* Stock disponible */}
                            <div className="mt-1 text-xs">
                              {insumo.disponible ? (
                                <span className="text-green-700 flex items-center gap-1">
                                  <CheckCircle className="h-3 w-3" />
                                  Stock: {insumo.stock_disponible} {insumo.unidad_stock || insumo.unidad}
                                </span>
                              ) : (
                                <span className="text-red-700 flex items-center gap-1">
                                  <AlertCircle className="h-3 w-3" />
                                  Stock insuficiente: {insumo.stock_disponible || 0} {insumo.unidad_stock || insumo.unidad}
                                </span>
                              )}
                            </div>
                            
                            {insumo.notas && (
                              <p className="text-xs text-gray-500 mt-1 italic">{insumo.notas}</p>
                            )}
                          </div>
                          
                          {insumo.es_opcional && (
                            <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                              Opcional
                            </span>
                          )}
                        </div>
                      ))}
                    </div>
                    
                    {/* Resumen de costos */}
                    <div className="bg-gradient-to-r from-primary-50 to-primary-100 p-4 rounded-lg border-2 border-primary-200">
                      <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                        <DollarSign className="h-4 w-4 mr-1" />
                        Resumen Económico
                      </h4>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-700">Costo Total Insumos:</span>
                          <span className="font-semibold text-gray-900">
                            ${receta.costo_total_insumos?.toLocaleString('es-CL')}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-700">Precio de Venta:</span>
                          <span className="font-semibold text-gray-900">
                            ${receta.precio_venta?.toLocaleString('es-CL')}
                          </span>
                        </div>
                        <div className="flex justify-between pt-2 border-t border-primary-300">
                          <span className="text-gray-700">Ganancia:</span>
                          <span className={`font-bold ${receta.ganancia > 0 ? 'text-green-600' : 'text-red-600'}`}>
                            ${receta.ganancia?.toLocaleString('es-CL')}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-700">Margen:</span>
                          <span className={`font-bold ${receta.margen_porcentaje > 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {receta.margen_porcentaje?.toFixed(1)}%
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500 bg-gray-50 rounded-lg">
                    <Package className="h-12 w-12 text-gray-300 mx-auto mb-2" />
                    <p>No hay receta configurada para este producto</p>
                    <p className="text-xs text-gray-400 mt-1">
                      Configura los insumos necesarios en el recetario
                    </p>
                  </div>
                )}
              </div>
              
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
              
              {/* Botón Simulador de Costos */}
              <div className="mt-6 pt-4 border-t border-gray-200">
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    abrirSimulador()
                  }}
                  className="w-full bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 text-white py-3 px-4 rounded-lg font-semibold flex items-center justify-center gap-2 transition-all shadow-lg hover:shadow-xl"
                >
                  <Calculator className="h-5 w-5" />
                  Simular Costos y Modificar Recetario
                </button>
                <p className="text-xs text-gray-500 text-center mt-2">
                  Experimenta con diferentes combinaciones de flores, colores y contenedores
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* MODAL SIMULADOR DE COSTOS */}
      {mostrarSimulador && productoDetalle && (
        <div 
          className="fixed inset-0 bg-black/60 flex items-center justify-center z-[60] p-4"
          onClick={() => setMostrarSimulador(false)}
        >
          <div 
            className="bg-white rounded-lg shadow-2xl w-full max-w-7xl max-h-[95vh] overflow-hidden flex flex-col"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header del Simulador */}
            <div className="bg-gradient-to-r from-primary-600 to-primary-700 text-white px-6 py-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Calculator className="h-6 w-6" />
                <div>
                  <h2 className="text-xl font-bold">Simulador de Costos</h2>
                  <p className="text-sm text-primary-100">{productoDetalle.nombre}</p>
                </div>
              </div>
              <button 
                onClick={() => setMostrarSimulador(false)}
                className="text-white/80 hover:text-white transition-colors"
              >
                <X className="h-6 w-6" />
              </button>
            </div>
            
            {/* Contenido del Simulador */}
            {loadingConfig ? (
              <div className="flex-1 flex items-center justify-center p-12">
                <div className="text-center">
                  <div className="animate-spin h-12 w-12 border-4 border-primary-200 border-t-primary-600 rounded-full mx-auto mb-4"></div>
                  <p className="text-gray-600">Cargando configuración...</p>
                </div>
              </div>
            ) : configuracion ? (
              <div className="flex-1 overflow-y-auto">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 p-6">
                  {/* COLUMNA IZQUIERDA: FORMULARIO */}
                  <div className="lg:col-span-2 space-y-6">
                    {/* Colores y Flores */}
                    <div className="bg-white border border-gray-200 rounded-lg p-5 shadow-sm">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                          <Flower2 className="h-5 w-5 text-primary-600" />
                          Flores por Color
                        </h3>
                        <button
                          onClick={resetearReceta}
                          className="text-sm text-gray-600 hover:text-primary-600 flex items-center gap-1"
                        >
                          <RefreshCw className="h-4 w-4" />
                          Resetear
                        </button>
                      </div>
                      
                      <div className="space-y-6">
                        {coloresEditables.map((color) => {
                          const floresColor = simulacion.flores[color.id] || []
                          const totalTallos = floresColor.reduce((sum, f) => sum + (f.cantidad || 0), 0)
                          const costoColor = floresColor.reduce((sum, f) => sum + (f.cantidad * f.costo || 0), 0)
                          
                          return (
                            <div key={color.id} className="bg-gray-50 rounded-lg p-4 border-2 border-gray-200 relative">
                              {/* Botón eliminar color */}
                              {coloresEditables.length > 1 && (
                                <button
                                  onClick={() => handleEliminarColor(color.id)}
                                  className="absolute top-2 right-2 text-red-600 hover:text-red-700 hover:bg-red-50 p-1.5 rounded-lg transition-all duration-200 z-10"
                                  title="Eliminar color"
                                >
                                  <Trash2 className="h-4 w-4" />
                                </button>
                              )}
                              
                              <div className="flex items-center justify-between mb-3 pr-8">
                                <div className="flex items-center gap-2 flex-1">
                                  <div 
                                    className="w-6 h-6 rounded-full border-2 border-gray-300 flex-shrink-0"
                                    style={{ backgroundColor: color.nombre_color.toLowerCase() }}
                                  ></div>
                                  {/* Select editable para nombre del color */}
                                  <select
                                    value={color.nombre_color}
                                    onChange={(e) => handleEditarNombreColor(color.id, e.target.value)}
                                    className="font-semibold text-gray-900 bg-white border border-gray-300 hover:border-primary-400 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-200 px-2 py-1 rounded"
                                  >
                                    <option value="">Seleccionar color...</option>
                                    {COLORES_PRODUCTOS.map(colorOpcion => (
                                      <option key={colorOpcion} value={colorOpcion}>{colorOpcion}</option>
                                    ))}
                                  </select>
                                  <span className="text-xs text-gray-500">
                                    ({totalTallos} tallos - ${costoColor.toLocaleString('es-CL')})
                                  </span>
                                </div>
                                <button
                                  onClick={() => handleAgregarFlor(color.id)}
                                  className="text-sm bg-primary-50 hover:bg-primary-100 text-primary-700 px-3 py-1 rounded-lg flex items-center gap-1 transition-colors flex-shrink-0"
                                >
                                  <Plus className="h-4 w-4" />
                                  Agregar Flor
                                </button>
                              </div>
                              
                              <div className="space-y-2">
                                {floresColor.map((flor, florIndex) => {
                                  const floresFiltradas = obtenerFloresPorColor(color.nombre_color)
                                  const florInfo = floresFiltradas.find(f => f.flor_id === flor.florId)
                                  const costoLinea = (flor.cantidad || 0) * (flor.costo || 0)
                                  
                                  return (
                                    <div key={flor.id} className="bg-white p-3 rounded border border-gray-200 flex items-center gap-2">
                                      {/* Selector de flor */}
                                      <select
                                        value={flor.florId}
                                        onChange={(e) => handleFlorChange(color.id, florIndex, e.target.value)}
                                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                                      >
                                        <option value="">Seleccionar flor...</option>
                                        {floresFiltradas.length > 0 ? (
                                          floresFiltradas.map(f => (
                                            <option key={f.flor_id} value={f.flor_id}>
                                              {f.flor_nombre} - ${f.flor_costo.toLocaleString('es-CL')} 
                                              (Stock: {f.flor_disponible || 0})
                                            </option>
                                          ))
                                        ) : (
                                          <option value="" disabled>No hay flores de este color en inventario</option>
                                        )}
                                      </select>
                                      
                                      {/* Cantidad */}
                                      <input
                                        type="number"
                                        min="0"
                                        value={flor.cantidad || ''}
                                        onChange={(e) => handleCantidadChange(color.id, florIndex, e.target.value)}
                                        className="w-20 px-3 py-2 border border-gray-300 rounded-lg text-sm text-center focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                                        placeholder="Cant."
                                      />
                                      
                                      {/* Costo */}
                                      <div className="w-28 text-right font-semibold text-sm text-gray-700">
                                        ${costoLinea.toLocaleString('es-CL')}
                                      </div>
                                      
                                      {/* Botón eliminar */}
                                      {floresColor.length > 1 && (
                                        <button
                                          onClick={() => handleEliminarFlor(color.id, florIndex)}
                                          className="p-1.5 rounded-lg hover:bg-red-50 text-red-600 hover:text-red-700 transition-all duration-200"
                                          title="Eliminar flor"
                                        >
                                          <Trash2 className="h-4 w-4" />
                                        </button>
                                      )}
                                    </div>
                                  )
                                })}
                              </div>
                            </div>
                          )
                        })}
                        
                        {/* Botón Agregar Nuevo Color */}
                        <button
                          onClick={handleAgregarColor}
                          className="w-full bg-white border-2 border-dashed border-gray-300 hover:border-primary-400 hover:bg-primary-50 text-gray-600 hover:text-primary-700 py-4 rounded-lg flex items-center justify-center gap-2 transition-all"
                        >
                          <Plus className="h-5 w-5" />
                          <span className="font-medium">Agregar Nuevo Color</span>
                        </button>
                      </div>
                    </div>
                    
                    {/* Contenedor */}
                    <div className="bg-white border border-gray-200 rounded-lg p-5 shadow-sm">
                      <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2 mb-4">
                        <Package className="h-5 w-5 text-primary-600" />
                        Contenedor
                      </h3>
                      
                      <select
                        value={simulacion.contenedor?.contenedorId || ''}
                        onChange={(e) => handleContenedorChange(e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      >
                        <option value="">Sin contenedor</option>
                        {contenedores.map(c => (
                          <option key={c.id} value={c.id}>
                            {c.tipo} - {c.nombre} - ${c.costo.toLocaleString('es-CL')} 
                            (Stock: {c.cantidad_disponible || 0})
                          </option>
                        ))}
                      </select>
                    </div>
                    
                    {/* Botón Guardar */}
                    <button
                      onClick={handleGuardarReceta}
                      disabled={guardandoReceta}
                      className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white py-3 px-4 rounded-lg font-semibold flex items-center justify-center gap-2 transition-all shadow-lg hover:shadow-xl"
                    >
                      <Save className="h-5 w-5" />
                      {guardandoReceta ? 'Guardando...' : 'Guardar como Receta Base'}
                    </button>
                  </div>
                  
                  {/* COLUMNA DERECHA: FOTO Y RESUMEN */}
                  <div className="space-y-6">
                    {/* Foto del Producto */}
                    <div className="bg-white border border-gray-200 rounded-lg p-5 shadow-sm">
                      <h3 className="text-sm font-semibold text-gray-500 uppercase mb-3">Vista Previa</h3>
                      <div className="aspect-square bg-gray-100 rounded-lg overflow-hidden mb-3">
                        {productoDetalle.imagen_url ? (
                          <img 
                            src={`${API_URL}/upload/imagen/${productoDetalle.imagen_url}`}
                            alt={productoDetalle.nombre}
                            className="w-full h-full object-cover"
                            onError={(e) => {
                              e.target.style.display = 'none'
                              if (e.target.nextSibling) {
                                e.target.nextSibling.style.display = 'flex'
                              }
                            }}
                          />
                        ) : null}
                        {!productoDetalle.imagen_url && (
                          <div className="flex items-center justify-center w-full h-full">
                            <Flower2 className="h-16 w-16 text-primary-600" />
                          </div>
                        )}
                      </div>
                      <p className="text-sm text-gray-700 font-semibold">{productoDetalle.nombre}</p>
                      <p className="text-xs text-gray-500 mt-1">{productoDetalle.tipo_arreglo}</p>
                    </div>
                    
                    {/* Resumen de Costos */}
                    <div className="bg-gradient-to-br from-primary-50 to-primary-100 border-2 border-primary-200 rounded-lg p-5 shadow-sm">
                      <h3 className="text-sm font-semibold text-gray-700 uppercase mb-4 flex items-center gap-2">
                        <DollarSign className="h-4 w-4" />
                        Resumen de Costos
                      </h3>
                      
                      <div className="space-y-3">
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">Flores:</span>
                          <span className="font-semibold text-gray-900">
                            ${costoFlores.toLocaleString('es-CL')}
                          </span>
                        </div>
                        
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">Contenedor:</span>
                          <span className="font-semibold text-gray-900">
                            ${costoContenedor.toLocaleString('es-CL')}
                          </span>
                        </div>
                        
                        <div className="border-t-2 border-primary-300 pt-3 flex justify-between">
                          <span className="font-semibold text-gray-700">Costo Total:</span>
                          <span className="text-lg font-bold text-primary-700">
                            ${costoTotal.toLocaleString('es-CL')}
                          </span>
                        </div>
                        
                        <div className="border-t border-primary-200 pt-3">
                          <div className="flex justify-between items-center mb-2">
                            <span className="font-semibold text-gray-700">Precio Venta:</span>
                            {precioVentaEditado !== null && (
                              <button
                                onClick={() => setPrecioVentaEditado(null)}
                                className="text-xs text-gray-500 hover:text-primary-600 underline"
                              >
                                Restaurar original
                              </button>
                            )}
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="text-gray-600">$</span>
                            <input
                              type="number"
                              value={precioVenta}
                              onChange={(e) => setPrecioVentaEditado(parseInt(e.target.value) || 0)}
                              className="flex-1 px-3 py-2 border-2 border-gray-300 focus:border-green-500 rounded-lg text-lg font-bold text-green-700 text-right focus:outline-none"
                              placeholder="Precio de venta"
                            />
                          </div>
                          <p className="text-xs text-gray-500 mt-1">
                            {precioVentaEditado !== null ? '(Editado)' : `Original: $${productoDetalle?.precio_venta?.toLocaleString('es-CL') || 0}`}
                          </p>
                        </div>
                        
                        <div className={`border-t border-primary-200 pt-3 ${margenActual >= 0 ? 'bg-green-50' : 'bg-red-50'} -mx-5 px-5 py-3 rounded-b-lg`}>
                          <div className="flex justify-between items-center">
                            <span className="font-semibold text-gray-700">Margen:</span>
                            <div className="text-right">
                              <span className={`text-xl font-bold ${margenActual >= 0 ? 'text-green-700' : 'text-red-700'}`}>
                                ${margenActual.toLocaleString('es-CL')}
                              </span>
                              <div className="text-xs text-gray-600">
                                {porcentajeMargen}% del precio de venta
                              </div>
                            </div>
                          </div>
                        </div>
                        
                        {/* Comparación con receta original */}
                        {configuracion.costo_total_estimado && (
                          <div className="mt-4 pt-3 border-t border-primary-300">
                            <p className="text-xs text-gray-600 mb-2">Comparación con receta original:</p>
                            <div className="flex justify-between text-sm">
                              <span className="text-gray-600">Costo original:</span>
                              <span className="font-medium text-gray-700">
                                ${configuracion.costo_total_estimado.toLocaleString('es-CL')}
                              </span>
                            </div>
                            <div className="flex justify-between text-sm mt-1">
                              <span className="text-gray-600">Diferencia:</span>
                              <span className={`font-semibold ${
                                costoTotal < configuracion.costo_total_estimado 
                                  ? 'text-green-600' 
                                  : 'text-red-600'
                              }`}>
                                {costoTotal < configuracion.costo_total_estimado ? '↓' : '↑'} 
                                ${Math.abs(costoTotal - configuracion.costo_total_estimado).toLocaleString('es-CL')}
                              </span>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex-1 flex items-center justify-center p-12">
                <div className="text-center text-gray-500">
                  <AlertCircle className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                  <p>No se pudo cargar la configuración del producto</p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default ProductosPage
