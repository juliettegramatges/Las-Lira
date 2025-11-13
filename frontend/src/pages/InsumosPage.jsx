import { useState, useEffect } from 'react'
import { Flower, Package, AlertCircle, Search, Plus, Save, X, Trash2, Building2, Phone, Mail, ShoppingCart } from 'lucide-react'
import axios from 'axios'
import { API_URL, inventarioAPI } from '../services/api'

// Colores comunes para flores
const COLORES_FLORES = [
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
  'Natural'
]

function InsumosPage() {
  const [flores, setFlores] = useState([])
  const [contenedores, setContenedores] = useState([])
  const [proveedores, setProveedores] = useState([])
  const [loading, setLoading] = useState(true)
  const [busqueda, setBusqueda] = useState('')
  const [vistaActiva, setVistaActiva] = useState('flores')
  const [soloEnUso, setSoloEnUso] = useState(false)  // 🆕 Filtro para ver solo insumos en uso
  const [soloEnEvento, setSoloEnEvento] = useState(false)  // 🆕 Filtro para ver solo insumos en evento
  const [soloStockBajo, setSoloStockBajo] = useState(false)  // 🆕 Filtro para ver solo insumos con stock bajo
  const [guardando, setGuardando] = useState({})
  const [modalFlorAbierto, setModalFlorAbierto] = useState(false)
  const [modalContenedorAbierto, setModalContenedorAbierto] = useState(false)
  const [modalProveedorAbierto, setModalProveedorAbierto] = useState(false)
  const [proveedorEditando, setProveedorEditando] = useState(null)
  const [modalAsociarInsumos, setModalAsociarInsumos] = useState(null)  // ID del proveedor
  const [proveedorDetalle, setProveedorDetalle] = useState(null)  // Proveedor para ver detalles
  const [modalReponerAbierto, setModalReponerAbierto] = useState(false)
  const [lineasReposicion, setLineasReposicion] = useState([])  // Array de {tipo, insumo_id, cantidad, proveedor_id}
  const [nuevaFlor, setNuevaFlor] = useState({
    tipo: '',
    color: '',
    costo_unitario: 0,
    ubicacion: 'Taller',
    cantidad_stock: 0,
    stock_bajo: 10
  })
  const [nuevoContenedor, setNuevoContenedor] = useState({
    tipo: '',
    material: '',
    tamano: '',
    color: '',
    costo: 0,
    ubicacion: 'Bodega 1',
    cantidad_stock: 0,
    stock_bajo: 5
  })
  const [nuevoProveedor, setNuevoProveedor] = useState({
    nombre: '',
    contacto: '',
    telefono: '',
    empresa: '',
    email: '',
    especialidad: '',
    dias_entrega: '',
    notas: ''
  })

  useEffect(() => {
    cargarInsumos()
  }, [])

  const cargarInsumos = async () => {
    try {
      setLoading(true)
      const [floresResponse, contenedoresResponse, proveedoresResponse] = await Promise.all([
        axios.get(`${API_URL}/inventario/flores`),
        axios.get(`${API_URL}/inventario/contenedores`),
        axios.get(`${API_URL}/inventario/proveedores`)
      ])
      
      if (floresResponse.data.success) {
        setFlores(floresResponse.data.data)
      }
      
      if (contenedoresResponse.data.success) {
        setContenedores(contenedoresResponse.data.data)
      }
      
      if (proveedoresResponse.data.success) {
        setProveedores(proveedoresResponse.data.data)
      }
    } catch (error) {
      console.error('Error al cargar insumos:', error)
      alert('Error al cargar insumos')
    } finally {
      setLoading(false)
    }
  }

  const actualizarFlor = async (id, campo, valor) => {
    try {
      setGuardando(prev => ({ ...prev, [`flor-${id}`]: true }))
      
      // Actualizar estado local inmediatamente para feedback visual
      setFlores(prev => prev.map(f => 
        f.id === id ? { ...f, [campo]: valor } : f
      ))
      
      // Determinar el tipo de valor según el campo
      let valorFinal
      if (campo === 'ubicacion' || campo === 'color') {
        valorFinal = valor
      } else if (campo === 'costo_unitario') {
        valorFinal = parseFloat(valor) || 0
      } else if (campo === 'stock_bajo') {
        valorFinal = parseInt(valor) || 10
      } else {
        valorFinal = parseInt(valor) || 0
      }
      
      console.log(`📤 Enviando actualización de ${campo} para flor ${id}:`, valorFinal)
      const response = await inventarioAPI.actualizarFlor(id, {
        [campo]: valorFinal
      })
      
      console.log('📥 Respuesta del servidor:', response.data)
      if (response.data.success) {
        // Actualizar con la respuesta del servidor
        setFlores(prev => prev.map(f => 
          f.id === id ? response.data.data : f
        ))
        console.log('✅ Flor actualizada correctamente, nuevo stock_bajo:', response.data.data?.stock_bajo)
      } else {
        console.error('❌ Error en respuesta:', response.data)
      }
    } catch (error) {
      console.error('Error al actualizar flor:', error)
      alert('Error al actualizar flor. Por favor, recarga la página.')
      // Recargar para restaurar el estado correcto
      cargarInsumos()
    } finally {
      setGuardando(prev => ({ ...prev, [`flor-${id}`]: false }))
    }
  }

  const actualizarContenedor = async (id, campo, valor) => {
    try {
      setGuardando(prev => ({ ...prev, [`contenedor-${id}`]: true }))

      // Actualizar estado local inmediatamente para feedback visual
      setContenedores(prev => prev.map(c =>
        c.id === id ? { ...c, [campo]: valor } : c
      ))

      // Determinar el tipo de valor según el campo
      let valorFinal
      if (campo === 'ubicacion') {
        valorFinal = valor
      } else if (campo === 'costo') {
        valorFinal = parseFloat(valor) || 0
      } else if (campo === 'stock_bajo') {
        valorFinal = parseInt(valor) || 5
      } else {
        valorFinal = parseInt(valor) || 0
      }

      console.log(`📤 Enviando actualización de ${campo} para contenedor ${id}:`, valorFinal)
      const response = await inventarioAPI.actualizarContenedor(id, {
        [campo]: valorFinal
      })

      console.log('📥 Respuesta del servidor:', response.data)
      if (response.data.success) {
        // Actualizar con la respuesta del servidor
        setContenedores(prev => prev.map(c =>
          c.id === id ? response.data.data : c
        ))
        console.log('✅ Contenedor actualizado correctamente, nuevo stock_bajo:', response.data.data?.stock_bajo)
      } else {
        console.error('❌ Error en respuesta:', response.data)
      }
    } catch (error) {
      console.error('Error al actualizar contenedor:', error)
      alert('Error al actualizar contenedor. Por favor, recarga la página.')
      // Recargar para restaurar el estado correcto
      cargarInsumos()
    } finally {
      setGuardando(prev => ({ ...prev, [`contenedor-${id}`]: false }))
    }
  }

  const crearFlor = async () => {
    try {
      if (!nuevaFlor.tipo.trim()) {
        alert('El tipo de flor es obligatorio')
        return
      }

      const response = await inventarioAPI.crearFlor(nuevaFlor)

      if (response.data.success) {
        setFlores(prev => [...prev, response.data.data])
        setModalFlorAbierto(false)
        setNuevaFlor({
          tipo: '',
          color: '',
          costo_unitario: 0,
          ubicacion: 'Taller',
          cantidad_stock: 0,
          stock_bajo: 10
        })
        alert(response.data.message || 'Flor creada exitosamente')
      }
    } catch (error) {
      console.error('Error al crear flor:', error)
      alert(error.response?.data?.error || 'Error al crear flor')
    }
  }

  const crearContenedor = async () => {
    try {
      if (!nuevoContenedor.tipo.trim()) {
        alert('El tipo de contenedor es obligatorio')
        return
      }

      const response = await inventarioAPI.crearContenedor(nuevoContenedor)

      if (response.data.success) {
        setContenedores(prev => [...prev, response.data.data])
        setModalContenedorAbierto(false)
        setNuevoContenedor({
          tipo: '',
          material: '',
          tamano: '',
          color: '',
          costo: 0,
          ubicacion: 'Bodega 1',
          cantidad_stock: 0,
          stock_bajo: 5
        })
        alert(response.data.message || 'Contenedor creado exitosamente')
      }
    } catch (error) {
      console.error('Error al crear contenedor:', error)
      alert(error.response?.data?.error || 'Error al crear contenedor')
    }
  }

  const eliminarFlor = async (florId, nombre) => {
    const confirmar = window.confirm(
      `¿Estás seguro de que deseas eliminar la flor "${nombre}"?\n\nEsta acción no se puede deshacer.`
    )

    if (!confirmar) return

    try {
      const response = await inventarioAPI.eliminarFlor(florId)

      if (response.data.success) {
        setFlores(prev => prev.filter(f => f.id !== florId))
        alert(response.data.message || 'Flor eliminada exitosamente')
      }
    } catch (error) {
      console.error('Error al eliminar flor:', error)
      alert(error.response?.data?.error || 'Error al eliminar flor')
    }
  }

  const eliminarContenedor = async (contenedorId, nombre) => {
    const confirmar = window.confirm(
      `¿Estás seguro de que deseas eliminar el contenedor "${nombre}"?\n\nEsta acción no se puede deshacer.`
    )

    if (!confirmar) return

    try {
      const response = await inventarioAPI.eliminarContenedor(contenedorId)

      if (response.data.success) {
        setContenedores(prev => prev.filter(c => c.id !== contenedorId))
        alert(response.data.message || 'Contenedor eliminado exitosamente')
      }
    } catch (error) {
      console.error('Error al eliminar contenedor:', error)
      alert(error.response?.data?.error || 'Error al eliminar contenedor')
    }
  }

  // ===== FUNCIONES PARA PROVEEDORES =====
  
  const crearProveedor = async () => {
    try {
      if (!nuevoProveedor.nombre.trim()) {
        alert('El nombre del proveedor es obligatorio')
        return
      }

      const response = await inventarioAPI.crearProveedor(nuevoProveedor)

      if (response.data.success) {
        setProveedores(prev => [...prev, response.data.data])
        setModalProveedorAbierto(false)
        setNuevoProveedor({
          nombre: '',
          contacto: '',
          telefono: '',
          empresa: '',
          email: '',
          especialidad: '',
          dias_entrega: '',
          notas: ''
        })
        alert(response.data.message || 'Proveedor creado exitosamente')
      }
    } catch (error) {
      console.error('Error al crear proveedor:', error)
      alert(error.response?.data?.error || 'Error al crear proveedor')
    }
  }

  const editarProveedor = async (proveedorId) => {
    try {
      const proveedor = proveedores.find(p => p.id === proveedorId)
      if (!proveedor) return

      setProveedorEditando(proveedor)
      setNuevoProveedor({
        nombre: proveedor.nombre || '',
        contacto: proveedor.contacto || '',
        telefono: proveedor.telefono || '',
        empresa: proveedor.empresa || '',
        email: proveedor.email || '',
        especialidad: proveedor.especialidad || '',
        dias_entrega: proveedor.dias_entrega || '',
        notas: proveedor.notas || ''
      })
      setModalProveedorAbierto(true)
    } catch (error) {
      console.error('Error al cargar proveedor:', error)
    }
  }

  const actualizarProveedor = async () => {
    try {
      if (!nuevoProveedor.nombre.trim()) {
        alert('El nombre del proveedor es obligatorio')
        return
      }

      const response = await inventarioAPI.actualizarProveedor(proveedorEditando.id, nuevoProveedor)

      if (response.data.success) {
        setProveedores(prev => prev.map(p => 
          p.id === proveedorEditando.id ? response.data.data : p
        ))
        setModalProveedorAbierto(false)
        setProveedorEditando(null)
        setNuevoProveedor({
          nombre: '',
          contacto: '',
          telefono: '',
          empresa: '',
          email: '',
          especialidad: '',
          dias_entrega: '',
          notas: ''
        })
        alert(response.data.message || 'Proveedor actualizado exitosamente')
        cargarInsumos()  // Recargar para actualizar asociaciones
      }
    } catch (error) {
      console.error('Error al actualizar proveedor:', error)
      alert(error.response?.data?.error || 'Error al actualizar proveedor')
    }
  }

  const eliminarProveedor = async (proveedorId, nombre) => {
    const confirmar = window.confirm(
      `¿Estás seguro de que deseas eliminar el proveedor "${nombre}"?\n\nEsta acción no se puede deshacer.`
    )

    if (!confirmar) return

    try {
      const response = await inventarioAPI.eliminarProveedor(proveedorId)

      if (response.data.success) {
        setProveedores(prev => prev.filter(p => p.id !== proveedorId))
        alert(response.data.message || 'Proveedor eliminado exitosamente')
      }
    } catch (error) {
      console.error('Error al eliminar proveedor:', error)
      alert(error.response?.data?.error || 'Error al eliminar proveedor')
    }
  }

  const abrirModalAsociarInsumos = async (proveedorId) => {
    try {
      const response = await axios.get(`${API_URL}/inventario/proveedores/${proveedorId}`)
      if (response.data.success) {
        setModalAsociarInsumos(response.data.data)
      }
    } catch (error) {
      console.error('Error al cargar proveedor:', error)
      alert('Error al cargar información del proveedor')
    }
  }

  const verDetalleProveedor = async (proveedorId) => {
    try {
      const response = await axios.get(`${API_URL}/inventario/proveedores/${proveedorId}`)
      if (response.data.success) {
        setProveedorDetalle(response.data.data)
      }
    } catch (error) {
      console.error('Error al cargar detalle del proveedor:', error)
      alert('Error al cargar información del proveedor')
    }
  }

  const asociarInsumo = async (proveedorId, tipo, insumoId) => {
    try {
      const endpoint = tipo === 'flor' 
        ? `${API_URL}/inventario/proveedores/${proveedorId}/insumos/flores`
        : `${API_URL}/inventario/proveedores/${proveedorId}/insumos/contenedores`
      
      const data = tipo === 'flor' 
        ? { flor_id: insumoId }
        : { contenedor_id: insumoId }

      const response = await axios.post(endpoint, data)

      if (response.data.success) {
        setModalAsociarInsumos(response.data.data)
        cargarInsumos()  // Recargar para actualizar las asociaciones en insumos
        alert(response.data.message || 'Insumo asociado exitosamente')
      }
    } catch (error) {
      console.error('Error al asociar insumo:', error)
      alert(error.response?.data?.error || 'Error al asociar insumo')
    }
  }

  const desasociarInsumo = async (proveedorId, tipo, insumoId) => {
    try {
      const endpoint = tipo === 'flor'
        ? `${API_URL}/inventario/proveedores/${proveedorId}/insumos/flores/${insumoId}`
        : `${API_URL}/inventario/proveedores/${proveedorId}/insumos/contenedores/${insumoId}`

      const response = await axios.delete(endpoint)

      if (response.data.success) {
        setModalAsociarInsumos(response.data.data)
        cargarInsumos()  // Recargar para actualizar las asociaciones en insumos
        alert(response.data.message || 'Insumo desasociado exitosamente')
      }
    } catch (error) {
      console.error('Error al desasociar insumo:', error)
      alert(error.response?.data?.error || 'Error al desasociar insumo')
    }
  }

  // ===== FUNCIONES PARA REPOSICIÓN =====
  
  const agregarLineaReposicion = () => {
    setLineasReposicion([...lineasReposicion, {
      tipo: 'flor',
      insumo_id: '',
      cantidad: '',
      proveedor_id: ''
    }])
  }

  const eliminarLineaReposicion = (index) => {
    setLineasReposicion(lineasReposicion.filter((_, i) => i !== index))
  }

  const actualizarLineaReposicion = (index, campo, valor) => {
    const nuevasLineas = [...lineasReposicion]
    nuevasLineas[index] = { ...nuevasLineas[index], [campo]: valor }
    setLineasReposicion(nuevasLineas)
  }

  const procesarReposicion = async () => {
    try {
      // Validar que todas las líneas tengan datos
      const lineasInvalidas = lineasReposicion.filter(linea => 
        !linea.insumo_id || !linea.cantidad || parseInt(linea.cantidad) <= 0 || !linea.proveedor_id
      )

      if (lineasInvalidas.length > 0) {
        alert('Por favor completa todos los campos de cada línea (insumo, cantidad > 0, y proveedor)')
        return
      }

      // Enviar cada reposición
      const reposiciones = []
      for (const linea of lineasReposicion) {
        const endpoint = linea.tipo === 'flor'
          ? `${API_URL}/inventario/flores/${linea.insumo_id}/reponer`
          : `${API_URL}/inventario/contenedores/${linea.insumo_id}/reponer`
        
        const response = await axios.post(endpoint, {
          cantidad: parseInt(linea.cantidad),
          proveedor_id: linea.proveedor_id
        })

        if (response.data.success) {
          reposiciones.push(response.data.data)
        } else {
          throw new Error(response.data.error || 'Error al reponer insumo')
        }
      }

      alert(`✅ Reposición completada: ${reposiciones.length} insumo(s) actualizado(s)`)
      setModalReponerAbierto(false)
      setLineasReposicion([])
      cargarInsumos()  // Recargar para ver los cambios
    } catch (error) {
      console.error('Error al procesar reposición:', error)
      alert(error.response?.data?.error || 'Error al procesar la reposición')
    }
  }

  const floresFiltradas = flores.filter(f => {
    // Filtro por búsqueda
    const coincideBusqueda = f.nombre.toLowerCase().includes(busqueda.toLowerCase()) ||
                            f.color?.toLowerCase().includes(busqueda.toLowerCase())

    // Filtro por "en uso"
    const cumpleFiltroEnUso = !soloEnUso || (f.cantidad_en_uso && f.cantidad_en_uso > 0)

    // Filtro por "en evento"
    const cumpleFiltroEnEvento = !soloEnEvento || (f.cantidad_en_evento && f.cantidad_en_evento > 0)

    // Filtro por "stock bajo"
    const tieneStockBajo = f.cantidad_disponible <= (f.stock_bajo || 10)
    const cumpleFiltroStockBajo = !soloStockBajo || tieneStockBajo

    return coincideBusqueda && cumpleFiltroEnUso && cumpleFiltroEnEvento && cumpleFiltroStockBajo
  })

  const contenedoresFiltrados = contenedores.filter(c => {
    // Filtro por búsqueda
    const coincideBusqueda = c.nombre.toLowerCase().includes(busqueda.toLowerCase()) ||
                            c.tipo?.toLowerCase().includes(busqueda.toLowerCase())

    // Filtro por "en uso"
    const cumpleFiltroEnUso = !soloEnUso || (c.cantidad_en_uso && c.cantidad_en_uso > 0)

    // Filtro por "en evento"
    const cumpleFiltroEnEvento = !soloEnEvento || (c.cantidad_en_evento && c.cantidad_en_evento > 0)

    // Filtro por "stock bajo"
    const tieneStockBajo = c.cantidad_disponible <= (c.stock_bajo || 5)
    const cumpleFiltroStockBajo = !soloStockBajo || tieneStockBajo

    return coincideBusqueda && cumpleFiltroEnUso && cumpleFiltroEnEvento && cumpleFiltroStockBajo
  })

  const getStockColor = (disponible, total) => {
    if (total === 0) return 'text-gray-400'
    const porcentaje = (disponible / total) * 100
    if (porcentaje <= 10) return 'text-red-600 font-bold'
    if (porcentaje <= 30) return 'text-orange-600 font-semibold'
    return 'text-green-600 font-medium'
  }

  if (loading) {
    return (
      <div className="p-6">
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-600">Cargando insumos...</p>
        </div>
      </div>
    )
  }

  // Verificar si no hay datos
  if (!loading && flores.length === 0 && contenedores.length === 0) {
    return (
      <div className="p-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <Package className="h-8 w-8" />
            Inventario
          </h1>
          <p className="text-gray-600 mt-1">Gestión completa de flores, contenedores y materiales</p>
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <Package className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-2xl font-semibold text-gray-900 mb-2">No hay insumos en el inventario</h2>
          <p className="text-gray-600 mb-6">Importa los datos desde el CSV para comenzar</p>
          <div className="bg-blue-50 border-l-4 border-blue-500 p-4 mb-4 text-left max-w-2xl mx-auto">
            <p className="text-sm font-medium text-blue-900 mb-2">📋 Para importar los insumos:</p>
            <ol className="text-sm text-blue-800 space-y-1 list-decimal list-inside">
              <li>Abre una terminal</li>
              <li>Ejecuta: <code className="bg-blue-100 px-2 py-1 rounded">cd /Users/juliettegramatges/Las-Lira/backend</code></li>
              <li>Ejecuta: <code className="bg-blue-100 px-2 py-1 rounded">python3 importar_insumos_csv.py</code></li>
              <li>Recarga esta página</li>
            </ol>
          </div>
          <p className="text-xs text-gray-500">Este script lee el archivo 'insumos_las_lira.csv' y crea flores y contenedores</p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
          <Package className="h-8 w-8" />
          Inventario
        </h1>
        <p className="text-gray-600 mt-1">Gestión completa de flores, contenedores y materiales</p>
      </div>

      {/* Estadísticas Rápidas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Flores</p>
              <p className="text-2xl font-bold text-purple-600">{flores.length}</p>
            </div>
            <Flower className="h-8 w-8 text-purple-600" />
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Contenedores</p>
              <p className="text-2xl font-bold text-blue-600">{contenedores.length}</p>
            </div>
            <Package className="h-8 w-8 text-blue-600" />
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Stock Bajo</p>
              <p className="text-2xl font-bold text-orange-600">
                {flores.filter(f => f.cantidad_disponible <= (f.stock_bajo || 10)).length + 
                 contenedores.filter(c => c.cantidad_disponible <= (c.stock_bajo || 5)).length}
              </p>
            </div>
            <AlertCircle className="h-8 w-8 text-orange-600" />
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">En Uso/Evento</p>
              <p className="text-2xl font-bold text-indigo-600">
                {flores.reduce((acc, f) => acc + (f.cantidad_en_uso || 0) + (f.cantidad_en_evento || 0), 0) +
                 contenedores.reduce((acc, c) => acc + (c.cantidad_en_uso || 0) + (c.cantidad_en_evento || 0), 0)}
              </p>
            </div>
            <Package className="h-8 w-8 text-indigo-600" />
          </div>
        </div>
      </div>

      {/* Barra de búsqueda y pestañas */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
        <div className="p-3 border-b border-gray-200">
          <div className="flex flex-col gap-3">
            {/* Primera fila: Búsqueda y Filtros */}
            <div className="flex flex-wrap items-center gap-2">
              <div className="relative flex-1 min-w-[200px] max-w-sm">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Buscar..."
                  value={busqueda}
                  onChange={(e) => setBusqueda(e.target.value)}
                  className="w-full pl-10 pr-4 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>

              {/* Botones de filtro compactos */}
              <button
                onClick={() => setSoloEnUso(!soloEnUso)}
                className={`px-3 py-1.5 text-sm rounded-md font-medium transition-all flex items-center gap-1.5 ${
                  soloEnUso
                    ? 'bg-indigo-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <Package className="h-3.5 w-3.5" />
                En Uso
                {soloEnUso && <span className="text-xs">({flores.filter(f => f.cantidad_en_uso && f.cantidad_en_uso > 0).length + contenedores.filter(c => c.cantidad_en_uso && c.cantidad_en_uso > 0).length})</span>}
              </button>
              <button
                onClick={() => setSoloEnEvento(!soloEnEvento)}
                className={`px-3 py-1.5 text-sm rounded-md font-medium transition-all flex items-center gap-1.5 ${
                  soloEnEvento
                    ? 'bg-pink-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <Flower className="h-3.5 w-3.5" />
                En Evento
                {soloEnEvento && <span className="text-xs">({flores.filter(f => f.cantidad_en_evento && f.cantidad_en_evento > 0).length + contenedores.filter(c => c.cantidad_en_evento && c.cantidad_en_evento > 0).length})</span>}
              </button>
              <button
                onClick={() => setSoloStockBajo(!soloStockBajo)}
                className={`px-3 py-1.5 text-sm rounded-md font-medium transition-all flex items-center gap-1.5 ${
                  soloStockBajo
                    ? 'bg-orange-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <AlertCircle className="h-3.5 w-3.5" />
                Bajo
                {soloStockBajo && <span className="text-xs">({flores.filter(f => f.cantidad_disponible <= (f.stock_bajo || 10)).length + contenedores.filter(c => c.cantidad_disponible <= (c.stock_bajo || 5)).length})</span>}
              </button>
            </div>

            {/* Segunda fila: Tabs y Botones de Acción */}
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div className="flex gap-1">
                <button
                  onClick={() => setVistaActiva('flores')}
                  className={`px-3 py-1.5 text-sm rounded-md font-medium transition-colors ${
                    vistaActiva === 'flores'
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  <Flower className="inline h-3.5 w-3.5 mr-1" />
                  Flores <span className="text-xs opacity-75">({flores.length})</span>
                </button>
                <button
                  onClick={() => setVistaActiva('contenedores')}
                  className={`px-3 py-1.5 text-sm rounded-md font-medium transition-colors ${
                    vistaActiva === 'contenedores'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  <Package className="inline h-3.5 w-3.5 mr-1" />
                  Contenedores <span className="text-xs opacity-75">({contenedores.length})</span>
                </button>
                <button
                  onClick={() => setVistaActiva('proveedores')}
                  className={`px-3 py-1.5 text-sm rounded-md font-medium transition-colors ${
                    vistaActiva === 'proveedores'
                      ? 'bg-green-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  <Building2 className="inline h-3.5 w-3.5 mr-1" />
                  Proveedores <span className="text-xs opacity-75">({proveedores.length})</span>
                </button>
              </div>

              <div className="flex gap-2">
                {vistaActiva === 'flores' && (
                  <button
                    onClick={() => setModalFlorAbierto(true)}
                    className="px-3 py-1.5 text-sm rounded-md font-medium bg-purple-600 text-white hover:bg-purple-700 transition-colors flex items-center gap-1.5"
                  >
                    <Plus className="h-3.5 w-3.5" />
                    Nueva
                  </button>
                )}

                {vistaActiva === 'contenedores' && (
                  <button
                    onClick={() => setModalContenedorAbierto(true)}
                    className="px-3 py-1.5 text-sm rounded-md font-medium bg-blue-600 text-white hover:bg-blue-700 transition-colors flex items-center gap-1.5"
                  >
                    <Plus className="h-3.5 w-3.5" />
                    Nuevo
                  </button>
                )}

                {vistaActiva === 'proveedores' && (
                  <button
                    onClick={() => {
                      setProveedorEditando(null)
                      setNuevoProveedor({
                        nombre: '',
                        contacto: '',
                        telefono: '',
                        empresa: '',
                        email: '',
                        especialidad: '',
                        dias_entrega: '',
                        notas: ''
                      })
                      setModalProveedorAbierto(true)
                    }}
                    className="px-3 py-1.5 text-sm rounded-md font-medium bg-green-600 text-white hover:bg-green-700 transition-colors flex items-center gap-1.5"
                  >
                    <Plus className="h-3.5 w-3.5" />
                    Nuevo
                  </button>
                )}

                {(vistaActiva === 'flores' || vistaActiva === 'contenedores') && (
                  <button
                    onClick={() => {
                      setLineasReposicion([{
                        tipo: vistaActiva === 'flores' ? 'flor' : 'contenedor',
                        insumo_id: '',
                        cantidad: '',
                        proveedor_id: ''
                      }])
                      setModalReponerAbierto(true)
                    }}
                    className="px-3 py-1.5 text-sm rounded-md font-medium bg-orange-600 text-white hover:bg-orange-700 transition-colors flex items-center gap-1.5"
                  >
                    <ShoppingCart className="h-3.5 w-3.5" />
                    Reponer
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Tabla de Flores */}
        {vistaActiva === 'flores' && (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-purple-50">
                <tr>
                  <th className="px-3 py-2 text-left text-xs font-semibold text-purple-900 uppercase">Nombre</th>
                  <th className="px-3 py-2 text-left text-xs font-semibold text-purple-900 uppercase">Color</th>
                  <th className="px-3 py-2 text-left text-xs font-semibold text-purple-900 uppercase">Costo/u</th>
                  <th className="px-3 py-2 text-left text-xs font-semibold text-purple-900 uppercase">Sector</th>
                  <th className="px-3 py-2 text-left text-xs font-semibold text-purple-900 uppercase">Proveedores</th>
                  <th className="px-3 py-2 text-center text-xs font-semibold text-purple-900 uppercase">Stock</th>
                  <th className="px-3 py-2 text-center text-xs font-semibold text-purple-900 uppercase">En Uso</th>
                  <th className="px-3 py-2 text-center text-xs font-semibold text-purple-900 uppercase">Evento</th>
                  <th className="px-3 py-2 text-center text-xs font-semibold text-purple-900 uppercase">Disp.</th>
                  <th className="px-3 py-2 text-center text-xs font-semibold text-purple-900 uppercase">Bajo</th>
                  <th className="px-3 py-2 text-center text-xs font-semibold text-purple-900 uppercase w-16">Acciones</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {floresFiltradas.map((flor) => {
                  const estaEnUso = flor.cantidad_en_uso && flor.cantidad_en_uso > 0
                  return (
                    <tr
                      key={flor.id}
                      className={`hover:bg-purple-50 transition-colors ${estaEnUso ? 'bg-indigo-50/50 border-l-2 border-l-indigo-500' : ''}`}
                    >
                      <td className="px-3 py-2">
                        <div className="flex items-center gap-1.5">
                          <Flower className="h-3.5 w-3.5 text-purple-600 flex-shrink-0" />
                          <span className="text-sm font-medium text-gray-900 truncate">{flor.nombre}</span>
                          {estaEnUso && (
                            <span className="px-1.5 py-0.5 bg-indigo-500 text-white text-[10px] font-bold rounded flex-shrink-0">USO</span>
                          )}
                        </div>
                      </td>
                    <td className="px-3 py-2">
                      <select
                        value={flor.color || ''}
                        onChange={(e) => actualizarFlor(flor.id, 'color', e.target.value)}
                        className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-purple-500 bg-white"
                      >
                        <option value="">-</option>
                        {COLORES_FLORES.map(color => (
                          <option key={color} value={color}>{color}</option>
                        ))}
                      </select>
                    </td>
                    <td className="px-3 py-2">
                      <div className="flex items-center gap-1">
                        <span className="text-xs text-gray-500">$</span>
                        <input
                          type="text"
                          value={flor.costo_unitario || 0}
                          onChange={(e) => actualizarFlor(flor.id, 'costo_unitario', e.target.value)}
                          className="w-20 px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-purple-500"
                        />
                      </div>
                    </td>
                    <td className="px-3 py-2">
                      <input
                        type="text"
                        value={flor.ubicacion || ''}
                        onChange={(e) => actualizarFlor(flor.id, 'ubicacion', e.target.value)}
                        placeholder="Sector"
                        className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-purple-500"
                      />
                    </td>
                    <td className="px-3 py-2">
                      <div className="flex items-center gap-1 max-w-[140px] overflow-x-auto">
                        {(flor.proveedores || []).length > 0 ? (
                          <>
                            {(flor.proveedores || []).slice(0, 1).map(prov => (
                              <button
                                key={prov.id}
                                onClick={() => verDetalleProveedor(prov.id)}
                                className="px-1.5 py-0.5 bg-green-100 text-green-700 text-xs rounded hover:bg-green-200 transition-colors whitespace-nowrap"
                                title={`Ver detalles de ${prov.nombre}`}
                              >
                                {prov.nombre.length > 10 ? `${prov.nombre.substring(0, 9)}...` : prov.nombre}
                              </button>
                            ))}
                            {(flor.proveedores || []).length > 1 && (
                              <button
                                onClick={() => verDetalleProveedor(flor.proveedores[0].id)}
                                className="px-1.5 py-0.5 bg-green-200 text-green-800 text-xs rounded hover:bg-green-300 transition-colors whitespace-nowrap font-semibold"
                                title={`Ver ${(flor.proveedores || []).length} proveedores`}
                              >
                                +{(flor.proveedores || []).length - 1}
                              </button>
                            )}
                          </>
                        ) : (
                          <span className="text-xs text-gray-400">-</span>
                        )}
                      </div>
                    </td>
                    <td className="px-3 py-2 text-center">
                      <input
                        type="text"
                        value={flor.cantidad_stock || 0}
                        onChange={(e) => actualizarFlor(flor.id, 'cantidad_stock', e.target.value)}
                        className="w-16 px-2 py-1 text-sm text-center border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-purple-500"
                      />
                    </td>
                    <td className="px-3 py-2 text-center">
                      <input
                        type="text"
                        value={flor.cantidad_en_uso || 0}
                        onChange={(e) => actualizarFlor(flor.id, 'cantidad_en_uso', e.target.value)}
                        className="w-16 px-2 py-1 text-sm text-center border border-blue-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 bg-blue-50"
                      />
                    </td>
                    <td className="px-3 py-2 text-center">
                      <input
                        type="text"
                        value={flor.cantidad_en_evento || 0}
                        onChange={(e) => actualizarFlor(flor.id, 'cantidad_en_evento', e.target.value)}
                        className="w-16 px-2 py-1 text-sm text-center border border-purple-300 rounded focus:outline-none focus:ring-1 focus:ring-purple-500 bg-purple-50"
                      />
                    </td>
                    <td className="px-3 py-2 text-center">
                      <span className={`text-sm font-semibold ${getStockColor(flor.cantidad_disponible, flor.cantidad_stock)} ${flor.cantidad_disponible <= (flor.stock_bajo || 10) ? 'text-red-600 font-bold' : ''}`}>
                        {flor.cantidad_disponible || 0}
                      </span>
                      {guardando[`flor-${flor.id}`] && (
                        <span className="ml-1 text-xs">💾</span>
                      )}
                    </td>
                    <td className="px-3 py-2 text-center">
                      <input
                        type="text"
                        value={flor.stock_bajo !== undefined && flor.stock_bajo !== null ? flor.stock_bajo : ''}
                        onChange={(e) => {
                          const valor = e.target.value
                          setFlores(prev => prev.map(f =>
                            f.id === flor.id ? { ...f, stock_bajo: valor === '' ? '' : parseInt(valor) || 0 } : f
                          ))
                        }}
                        onBlur={(e) => {
                          const valor = e.target.value
                          const valorFinal = valor === '' ? 10 : parseInt(valor) || 10
                          console.log('💾 Guardando stock_bajo para flor', flor.id, 'valor:', valorFinal)
                          actualizarFlor(flor.id, 'stock_bajo', valorFinal)
                        }}
                        className="w-14 px-2 py-1 text-sm text-center border border-orange-300 rounded focus:outline-none focus:ring-1 focus:ring-orange-500 bg-orange-50"
                        title="Umbral bajo"
                        placeholder="10"
                      />
                    </td>
                    <td className="px-3 py-2 text-center">
                      <button
                        onClick={() => eliminarFlor(flor.id, flor.nombre)}
                        className="p-1.5 bg-red-50 text-red-700 rounded hover:bg-red-100 transition-colors"
                        title="Eliminar"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </td>
                  </tr>
                  )
                })}
                {floresFiltradas.length === 0 && (
                  <tr>
                    <td colSpan="11" className="px-2 py-6 text-center text-xs text-gray-500">
                      No se encontraron flores
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}

        {/* Tabla de Contenedores */}
        {vistaActiva === 'contenedores' && (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-blue-50">
                <tr>
                  <th className="px-3 py-2 text-left text-xs font-semibold text-blue-900 uppercase">Nombre</th>
                  <th className="px-3 py-2 text-left text-xs font-semibold text-blue-900 uppercase">Tipo</th>
                  <th className="px-3 py-2 text-left text-xs font-semibold text-blue-900 uppercase">Costo</th>
                  <th className="px-3 py-2 text-left text-xs font-semibold text-blue-900 uppercase">Sector</th>
                  <th className="px-3 py-2 text-left text-xs font-semibold text-blue-900 uppercase">Proveedores</th>
                  <th className="px-3 py-2 text-center text-xs font-semibold text-blue-900 uppercase">Stock</th>
                  <th className="px-3 py-2 text-center text-xs font-semibold text-blue-900 uppercase">En Uso</th>
                  <th className="px-3 py-2 text-center text-xs font-semibold text-blue-900 uppercase">Evento</th>
                  <th className="px-3 py-2 text-center text-xs font-semibold text-blue-900 uppercase">Disp.</th>
                  <th className="px-3 py-2 text-center text-xs font-semibold text-blue-900 uppercase">Bajo</th>
                  <th className="px-3 py-2 text-center text-xs font-semibold text-blue-900 uppercase w-16">Acciones</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {contenedoresFiltrados.map((contenedor) => {
                  const estaEnUso = contenedor.cantidad_en_uso && contenedor.cantidad_en_uso > 0
                  return (
                    <tr
                      key={contenedor.id}
                      className={`hover:bg-blue-50 transition-colors ${estaEnUso ? 'bg-indigo-50/50 border-l-4 border-l-indigo-500' : ''}`}
                    >
                      <td className="px-3 py-2">
                        <div className="flex items-center gap-1.5">
                          <Package className="h-3.5 w-3.5 text-blue-600 flex-shrink-0" />
                          <span className="text-sm font-medium text-gray-900 truncate">{contenedor.nombre}</span>
                          {estaEnUso && (
                            <span className="px-1.5 py-0.5 bg-indigo-500 text-white text-[10px] font-bold rounded flex-shrink-0">USO</span>
                          )}
                        </div>
                      </td>
                    <td className="px-3 py-2">
                      <span className="text-sm text-gray-700">{contenedor.tipo || '-'}</span>
                    </td>
                    <td className="px-3 py-2">
                      <div className="flex items-center gap-1">
                        <span className="text-xs text-gray-500">$</span>
                        <input
                          type="text"
                          value={contenedor.costo || 0}
                          onChange={(e) => actualizarContenedor(contenedor.id, 'costo', e.target.value)}
                          className="w-20 px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                        />
                      </div>
                    </td>
                    <td className="px-3 py-2">
                      <input
                        type="text"
                        value={contenedor.ubicacion || ''}
                        onChange={(e) => actualizarContenedor(contenedor.id, 'ubicacion', e.target.value)}
                        placeholder="Sector"
                        className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                      />
                    </td>
                    <td className="px-3 py-2">
                      <div className="flex items-center gap-1 max-w-[140px] overflow-x-auto">
                        {(contenedor.proveedores || []).length > 0 ? (
                          <>
                            {(contenedor.proveedores || []).slice(0, 1).map(prov => (
                              <button
                                key={prov.id}
                                onClick={() => verDetalleProveedor(prov.id)}
                                className="px-1.5 py-0.5 bg-green-100 text-green-700 text-xs rounded hover:bg-green-200 transition-colors whitespace-nowrap"
                                title={`Ver detalles de ${prov.nombre}`}
                              >
                                {prov.nombre.length > 10 ? `${prov.nombre.substring(0, 9)}...` : prov.nombre}
                              </button>
                            ))}
                            {(contenedor.proveedores || []).length > 1 && (
                              <button
                                onClick={() => verDetalleProveedor(contenedor.proveedores[0].id)}
                                className="px-1.5 py-0.5 bg-green-200 text-green-800 text-xs rounded hover:bg-green-300 transition-colors whitespace-nowrap font-semibold"
                                title={`Ver ${(contenedor.proveedores || []).length} proveedores`}
                              >
                                +{(contenedor.proveedores || []).length - 1}
                              </button>
                            )}
                          </>
                        ) : (
                          <span className="text-xs text-gray-400">-</span>
                        )}
                      </div>
                    </td>
                    <td className="px-3 py-2 text-center">
                      <input
                        type="text"
                        value={contenedor.cantidad_stock || 0}
                        onChange={(e) => actualizarContenedor(contenedor.id, 'cantidad_stock', e.target.value)}
                        className="w-16 px-2 py-1 text-sm text-center border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                      />
                    </td>
                    <td className="px-3 py-2 text-center">
                      <input
                        type="text"
                        value={contenedor.cantidad_en_uso || 0}
                        onChange={(e) => actualizarContenedor(contenedor.id, 'cantidad_en_uso', e.target.value)}
                        className="w-16 px-2 py-1 text-sm text-center border border-blue-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 bg-blue-50"
                      />
                    </td>
                    <td className="px-3 py-2 text-center">
                      <input
                        type="text"
                        value={contenedor.cantidad_en_evento || 0}
                        onChange={(e) => actualizarContenedor(contenedor.id, 'cantidad_en_evento', e.target.value)}
                        className="w-16 px-2 py-1 text-sm text-center border border-purple-300 rounded focus:outline-none focus:ring-1 focus:ring-purple-500 bg-purple-50"
                      />
                    </td>
                    <td className="px-3 py-2 text-center">
                      <span className={`text-sm font-semibold ${getStockColor(contenedor.cantidad_disponible, contenedor.cantidad_stock)} ${contenedor.cantidad_disponible <= (contenedor.stock_bajo || 5) ? 'text-red-600 font-bold' : ''}`}>
                        {contenedor.cantidad_disponible || 0}
                      </span>
                      {guardando[`contenedor-${contenedor.id}`] && (
                        <span className="ml-1 text-xs">💾</span>
                      )}
                    </td>
                    <td className="px-3 py-2 text-center">
                      <input
                        type="text"
                        value={contenedor.stock_bajo !== undefined && contenedor.stock_bajo !== null ? contenedor.stock_bajo : ''}
                        onChange={(e) => {
                          const valor = e.target.value
                          setContenedores(prev => prev.map(c =>
                            c.id === contenedor.id ? { ...c, stock_bajo: valor === '' ? '' : parseInt(valor) || 0 } : c
                          ))
                        }}
                        onBlur={(e) => {
                          const valor = e.target.value
                          const valorFinal = valor === '' ? 5 : parseInt(valor) || 5
                          console.log('💾 Guardando stock_bajo para contenedor', contenedor.id, 'valor:', valorFinal)
                          actualizarContenedor(contenedor.id, 'stock_bajo', valorFinal)
                        }}
                        className="w-14 px-2 py-1 text-sm text-center border border-orange-300 rounded focus:outline-none focus:ring-1 focus:ring-orange-500 bg-orange-50"
                        title="Umbral bajo"
                        placeholder="5"
                      />
                    </td>
                    <td className="px-3 py-2 text-center">
                      <button
                        onClick={() => eliminarContenedor(contenedor.id, contenedor.nombre)}
                        className="px-2 py-1 bg-red-50 text-red-700 rounded hover:bg-red-100 transition-colors"
                        title="Eliminar contenedor"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </td>
                  </tr>
                  )
                })}
                {contenedoresFiltrados.length === 0 && (
                  <tr>
                    <td colSpan="11" className="px-3 py-8 text-center text-gray-500">
                      No se encontraron contenedores
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}

        {/* Tabla de Proveedores */}
        {vistaActiva === 'proveedores' && (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-green-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-green-900 uppercase tracking-wider">Nombre</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-green-900 uppercase tracking-wider">Empresa</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-green-900 uppercase tracking-wider">Contacto</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-green-900 uppercase tracking-wider">Teléfono</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-green-900 uppercase tracking-wider">Email</th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-green-900 uppercase tracking-wider">Flores</th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-green-900 uppercase tracking-wider">Contenedores</th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-green-900 uppercase tracking-wider">Acciones</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {proveedores.filter(p => 
                  p.nombre.toLowerCase().includes(busqueda.toLowerCase()) ||
                  (p.empresa && p.empresa.toLowerCase().includes(busqueda.toLowerCase()))
                ).map((proveedor) => (
                  <tr
                    key={proveedor.id}
                    className="hover:bg-green-50 transition-colors"
                  >
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <Building2 className="h-4 w-4 text-green-600" />
                        <span className="text-sm font-medium text-gray-900">{proveedor.nombre}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-sm text-gray-700">{proveedor.empresa || '-'}</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-sm text-gray-700">{proveedor.contacto || '-'}</span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-1">
                        <Phone className="h-3 w-3 text-gray-400" />
                        <span className="text-sm text-gray-700">{proveedor.telefono || '-'}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      {proveedor.email ? (
                        <div className="flex items-center gap-1">
                          <Mail className="h-3 w-3 text-gray-400" />
                          <span className="text-sm text-gray-700">{proveedor.email}</span>
                        </div>
                      ) : (
                        <span className="text-sm text-gray-400">-</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span className="px-2 py-1 bg-purple-100 text-purple-700 text-xs font-medium rounded">
                        {proveedor.total_flores || 0}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs font-medium rounded">
                        {proveedor.total_contenedores || 0}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2 justify-center">
                        <button
                          onClick={() => abrirModalAsociarInsumos(proveedor.id)}
                          className="px-2 py-1 bg-blue-50 text-blue-700 rounded hover:bg-blue-100 transition-colors text-xs"
                          title="Asociar insumos"
                        >
                          <Package className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => editarProveedor(proveedor.id)}
                          className="px-2 py-1 bg-yellow-50 text-yellow-700 rounded hover:bg-yellow-100 transition-colors text-xs"
                          title="Editar proveedor"
                        >
                          <Save className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => eliminarProveedor(proveedor.id, proveedor.nombre)}
                          className="px-2 py-1 bg-red-50 text-red-700 rounded hover:bg-red-100 transition-colors"
                          title="Eliminar proveedor"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
                {proveedores.filter(p => 
                  p.nombre.toLowerCase().includes(busqueda.toLowerCase()) ||
                  (p.empresa && p.empresa.toLowerCase().includes(busqueda.toLowerCase()))
                ).length === 0 && (
                  <tr>
                    <td colSpan="8" className="px-4 py-8 text-center text-gray-500">
                      No se encontraron proveedores
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Leyenda */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <h3 className="text-sm font-semibold text-gray-900 mb-3">📋 Leyenda:</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div>
            <span className="font-medium">Stock Total:</span> Cantidad total de insumos
          </div>
          <div>
            <span className="font-medium bg-blue-100 px-2 py-1 rounded">En Uso:</span> En pedidos activos del taller
          </div>
          <div>
            <span className="font-medium bg-purple-100 px-2 py-1 rounded">En Evento:</span> Reservados para eventos
          </div>
          <div>
            <span className="font-medium text-green-600">Disponible:</span> Stock Total - En Uso - En Evento
          </div>
          <div>
            <span className="text-red-600 font-bold">⚠️ Alerta:</span> Stock disponible ≤10% del total
          </div>
          <div>
            <span className="text-orange-600 font-semibold">⚠️ Advertencia:</span> Stock disponible ≤30% del total
          </div>
        </div>
        <div className="mt-3 text-xs text-gray-600 bg-blue-50 p-2 rounded">
          💡 <strong>Edición directa:</strong> Puedes modificar los valores de stock y sector directamente en la tabla. Los cambios se guardan automáticamente.
        </div>
      </div>

      {/* Modal Nueva Flor */}
      {modalFlorAbierto && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                <Flower className="h-6 w-6 text-purple-600" />
                Nueva Flor
              </h2>
              <button
                onClick={() => setModalFlorAbierto(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-6 w-6" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tipo de Flor <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={nuevaFlor.tipo}
                  onChange={(e) => setNuevaFlor({ ...nuevaFlor, tipo: e.target.value })}
                  placeholder="Ej: Rosa, Clavel, Lilium..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Color
                </label>
                <select
                  value={nuevaFlor.color}
                  onChange={(e) => setNuevaFlor({ ...nuevaFlor, color: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value="">Seleccionar color</option>
                  {COLORES_FLORES.map(color => (
                    <option key={color} value={color}>{color}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Costo Unitario (CLP)
                </label>
                <input
                  type="text"
                  value={nuevaFlor.costo_unitario}
                  onChange={(e) => setNuevaFlor({ ...nuevaFlor, costo_unitario: parseFloat(e.target.value) || 0 })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Ubicación
                </label>
                <input
                  type="text"
                  value={nuevaFlor.ubicacion}
                  onChange={(e) => setNuevaFlor({ ...nuevaFlor, ubicacion: e.target.value })}
                  placeholder="Ej: Taller, Bodega 1..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Stock Inicial
                </label>
                <input
                  type="text"
                  value={nuevaFlor.cantidad_stock}
                  onChange={(e) => setNuevaFlor({ ...nuevaFlor, cantidad_stock: parseInt(e.target.value) || 0 })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Umbral Stock Bajo
                </label>
                <input
                  type="text"
                  value={nuevaFlor.stock_bajo}
                  onChange={(e) => setNuevaFlor({ ...nuevaFlor, stock_bajo: parseInt(e.target.value) || 10 })}
                  className="w-full px-3 py-2 border border-orange-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 bg-orange-50"
                  placeholder="Cantidad mínima antes de alerta (default: 10)"
                />
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setModalFlorAbierto(false)}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={crearFlor}
                className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center justify-center gap-2"
              >
                <Save className="h-4 w-4" />
                Crear Flor
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal Nuevo Contenedor */}
      {modalContenedorAbierto && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                <Package className="h-6 w-6 text-blue-600" />
                Nuevo Contenedor
              </h2>
              <button
                onClick={() => setModalContenedorAbierto(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-6 w-6" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tipo <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={nuevoContenedor.tipo}
                  onChange={(e) => setNuevoContenedor({ ...nuevoContenedor, tipo: e.target.value })}
                  placeholder="Ej: Florero, Macetero, Canasto..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Material
                </label>
                <input
                  type="text"
                  value={nuevoContenedor.material}
                  onChange={(e) => setNuevoContenedor({ ...nuevoContenedor, material: e.target.value })}
                  placeholder="Ej: Vidrio, Cerámica, Mimbre..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tamaño
                </label>
                <input
                  type="text"
                  value={nuevoContenedor.tamano}
                  onChange={(e) => setNuevoContenedor({ ...nuevoContenedor, tamano: e.target.value })}
                  placeholder="Ej: Pequeño, Mediano, Grande..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Color
                </label>
                <input
                  type="text"
                  value={nuevoContenedor.color}
                  onChange={(e) => setNuevoContenedor({ ...nuevoContenedor, color: e.target.value })}
                  placeholder="Ej: Transparente, Blanco..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Costo (CLP)
                </label>
                <input
                  type="text"
                  value={nuevoContenedor.costo}
                  onChange={(e) => setNuevoContenedor({ ...nuevoContenedor, costo: parseFloat(e.target.value) || 0 })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Ubicación
                </label>
                <input
                  type="text"
                  value={nuevoContenedor.ubicacion}
                  onChange={(e) => setNuevoContenedor({ ...nuevoContenedor, ubicacion: e.target.value })}
                  placeholder="Ej: Bodega 1, Bodega 2..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Stock Inicial
                </label>
                <input
                  type="text"
                  value={nuevoContenedor.cantidad_stock}
                  onChange={(e) => setNuevoContenedor({ ...nuevoContenedor, cantidad_stock: parseInt(e.target.value) || 0 })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Umbral Stock Bajo
                </label>
                <input
                  type="text"
                  value={nuevoContenedor.stock_bajo}
                  onChange={(e) => setNuevoContenedor({ ...nuevoContenedor, stock_bajo: parseInt(e.target.value) || 5 })}
                  className="w-full px-3 py-2 border border-orange-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 bg-orange-50"
                  placeholder="Cantidad mínima antes de alerta (default: 5)"
                />
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setModalContenedorAbierto(false)}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={crearContenedor}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
              >
                <Save className="h-4 w-4" />
                Crear Contenedor
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal Proveedor */}
      {modalProveedorAbierto && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                <Building2 className="h-6 w-6 text-green-600" />
                {proveedorEditando ? 'Editar Proveedor' : 'Nuevo Proveedor'}
              </h2>
              <button
                onClick={() => {
                  setModalProveedorAbierto(false)
                  setProveedorEditando(null)
                  setNuevoProveedor({
                    nombre: '',
                    contacto: '',
                    telefono: '',
                    empresa: '',
                    email: '',
                    especialidad: '',
                    dias_entrega: '',
                    notas: ''
                  })
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-6 w-6" />
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nombre <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={nuevoProveedor.nombre}
                  onChange={(e) => setNuevoProveedor({ ...nuevoProveedor, nombre: e.target.value })}
                  placeholder="Nombre del proveedor"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Empresa
                </label>
                <input
                  type="text"
                  value={nuevoProveedor.empresa}
                  onChange={(e) => setNuevoProveedor({ ...nuevoProveedor, empresa: e.target.value })}
                  placeholder="Nombre de la empresa"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Contacto
                </label>
                <input
                  type="text"
                  value={nuevoProveedor.contacto}
                  onChange={(e) => setNuevoProveedor({ ...nuevoProveedor, contacto: e.target.value })}
                  placeholder="Nombre de contacto"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Teléfono
                </label>
                <input
                  type="text"
                  value={nuevoProveedor.telefono}
                  onChange={(e) => setNuevoProveedor({ ...nuevoProveedor, telefono: e.target.value })}
                  placeholder="+56 9 1234 5678"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  value={nuevoProveedor.email}
                  onChange={(e) => setNuevoProveedor({ ...nuevoProveedor, email: e.target.value })}
                  placeholder="proveedor@empresa.com"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Especialidad
                </label>
                <textarea
                  value={nuevoProveedor.especialidad}
                  onChange={(e) => setNuevoProveedor({ ...nuevoProveedor, especialidad: e.target.value })}
                  placeholder="Ej: Flores importadas, contenedores de vidrio..."
                  rows="2"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Días de Entrega
                </label>
                <input
                  type="text"
                  value={nuevoProveedor.dias_entrega}
                  onChange={(e) => setNuevoProveedor({ ...nuevoProveedor, dias_entrega: e.target.value })}
                  placeholder="Ej: Lunes a Viernes, 2-3 días hábiles"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Notas
                </label>
                <textarea
                  value={nuevoProveedor.notas}
                  onChange={(e) => setNuevoProveedor({ ...nuevoProveedor, notas: e.target.value })}
                  placeholder="Notas adicionales..."
                  rows="2"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => {
                  setModalProveedorAbierto(false)
                  setProveedorEditando(null)
                  setNuevoProveedor({
                    nombre: '',
                    contacto: '',
                    telefono: '',
                    empresa: '',
                    email: '',
                    especialidad: '',
                    dias_entrega: '',
                    notas: ''
                  })
                }}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={proveedorEditando ? actualizarProveedor : crearProveedor}
                className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center gap-2"
              >
                <Save className="h-4 w-4" />
                {proveedorEditando ? 'Actualizar' : 'Crear'} Proveedor
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal Asociar Insumos */}
      {modalAsociarInsumos && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full p-6 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                <Building2 className="h-6 w-6 text-green-600" />
                Asociar Insumos - {modalAsociarInsumos.nombre}
              </h2>
              <button
                onClick={() => setModalAsociarInsumos(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-6 w-6" />
              </button>
            </div>

            <div className="mb-4 p-4 bg-gray-50 rounded-lg">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium">Empresa:</span> {modalAsociarInsumos.empresa || '-'}
                </div>
                <div>
                  <span className="font-medium">Teléfono:</span> {modalAsociarInsumos.telefono || '-'}
                </div>
                <div className="col-span-2">
                  <span className="font-medium">Contacto:</span> {modalAsociarInsumos.contacto || '-'}
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Flores Asociadas */}
              <div>
                <h3 className="text-lg font-semibold text-purple-700 mb-3 flex items-center gap-2">
                  <Flower className="h-5 w-5" />
                  Flores Asociadas ({modalAsociarInsumos.flores?.length || 0})
                </h3>
                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {modalAsociarInsumos.flores?.map(flor => (
                    <div key={flor.id} className="flex items-center justify-between p-2 bg-purple-50 rounded">
                      <span className="text-sm">{flor.nombre}</span>
                      <button
                        onClick={() => desasociarInsumo(modalAsociarInsumos.id, 'flor', flor.id)}
                        className="px-2 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200 text-xs"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </div>
                  ))}
                  {(!modalAsociarInsumos.flores || modalAsociarInsumos.flores.length === 0) && (
                    <p className="text-sm text-gray-400 text-center py-4">No hay flores asociadas</p>
                  )}
                </div>
                <div className="mt-3">
                  <select
                    onChange={(e) => {
                      if (e.target.value) {
                        asociarInsumo(modalAsociarInsumos.id, 'flor', e.target.value)
                        e.target.value = ''
                      }
                    }}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                  >
                    <option value="">Agregar flor...</option>
                    {flores.filter(f => !modalAsociarInsumos.flores?.some(af => af.id === f.id)).map(flor => (
                      <option key={flor.id} value={flor.id}>{flor.nombre}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Contenedores Asociados */}
              <div>
                <h3 className="text-lg font-semibold text-blue-700 mb-3 flex items-center gap-2">
                  <Package className="h-5 w-5" />
                  Contenedores Asociados ({modalAsociarInsumos.contenedores?.length || 0})
                </h3>
                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {modalAsociarInsumos.contenedores?.map(contenedor => (
                    <div key={contenedor.id} className="flex items-center justify-between p-2 bg-blue-50 rounded">
                      <span className="text-sm">{contenedor.nombre}</span>
                      <button
                        onClick={() => desasociarInsumo(modalAsociarInsumos.id, 'contenedor', contenedor.id)}
                        className="px-2 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200 text-xs"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </div>
                  ))}
                  {(!modalAsociarInsumos.contenedores || modalAsociarInsumos.contenedores.length === 0) && (
                    <p className="text-sm text-gray-400 text-center py-4">No hay contenedores asociados</p>
                  )}
                </div>
                <div className="mt-3">
                  <select
                    onChange={(e) => {
                      if (e.target.value) {
                        asociarInsumo(modalAsociarInsumos.id, 'contenedor', e.target.value)
                        e.target.value = ''
                      }
                    }}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Agregar contenedor...</option>
                    {contenedores.filter(c => !modalAsociarInsumos.contenedores?.some(ac => ac.id === c.id)).map(contenedor => (
                      <option key={contenedor.id} value={contenedor.id}>{contenedor.nombre}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            <div className="flex justify-end mt-6">
              <button
                onClick={() => setModalAsociarInsumos(null)}
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
              >
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal Detalle Proveedor */}
      {proveedorDetalle && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full p-6 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                <Building2 className="h-6 w-6 text-green-600" />
                {proveedorDetalle.nombre}
              </h2>
              <button
                onClick={() => setProveedorDetalle(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-6 w-6" />
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div className="p-4 bg-gray-50 rounded-lg">
                <h3 className="text-sm font-semibold text-gray-700 mb-2">Información de Contacto</h3>
                <div className="space-y-2 text-sm">
                  {proveedorDetalle.empresa && (
                    <div className="flex items-center gap-2">
                      <Building2 className="h-4 w-4 text-gray-400" />
                      <span className="text-gray-600">Empresa:</span>
                      <span className="font-medium">{proveedorDetalle.empresa}</span>
                    </div>
                  )}
                  {proveedorDetalle.contacto && (
                    <div className="flex items-center gap-2">
                      <span className="text-gray-600">Contacto:</span>
                      <span className="font-medium">{proveedorDetalle.contacto}</span>
                    </div>
                  )}
                  {proveedorDetalle.telefono && (
                    <div className="flex items-center gap-2">
                      <Phone className="h-4 w-4 text-gray-400" />
                      <span className="text-gray-600">Teléfono:</span>
                      <a href={`tel:${proveedorDetalle.telefono}`} className="font-medium text-blue-600 hover:underline">
                        {proveedorDetalle.telefono}
                      </a>
                    </div>
                  )}
                  {proveedorDetalle.email && (
                    <div className="flex items-center gap-2">
                      <Mail className="h-4 w-4 text-gray-400" />
                      <span className="text-gray-600">Email:</span>
                      <a href={`mailto:${proveedorDetalle.email}`} className="font-medium text-blue-600 hover:underline">
                        {proveedorDetalle.email}
                      </a>
                    </div>
                  )}
                </div>
              </div>

              <div className="p-4 bg-gray-50 rounded-lg">
                <h3 className="text-sm font-semibold text-gray-700 mb-2">Información Adicional</h3>
                <div className="space-y-2 text-sm">
                  {proveedorDetalle.especialidad && (
                    <div>
                      <span className="text-gray-600 font-medium">Especialidad:</span>
                      <p className="text-gray-800 mt-1">{proveedorDetalle.especialidad}</p>
                    </div>
                  )}
                  {proveedorDetalle.dias_entrega && (
                    <div>
                      <span className="text-gray-600 font-medium">Días de Entrega:</span>
                      <p className="text-gray-800 mt-1">{proveedorDetalle.dias_entrega}</p>
                    </div>
                  )}
                  {proveedorDetalle.notas && (
                    <div>
                      <span className="text-gray-600 font-medium">Notas:</span>
                      <p className="text-gray-800 mt-1">{proveedorDetalle.notas}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Flores Asociadas */}
              <div>
                <h3 className="text-lg font-semibold text-purple-700 mb-3 flex items-center gap-2">
                  <Flower className="h-5 w-5" />
                  Flores Asociadas ({proveedorDetalle.flores?.length || 0})
                </h3>
                <div className="space-y-2 max-h-60 overflow-y-auto border border-purple-200 rounded-lg p-3 bg-purple-50">
                  {proveedorDetalle.flores && proveedorDetalle.flores.length > 0 ? (
                    proveedorDetalle.flores.map(flor => (
                      <div key={flor.id} className="flex items-center gap-2 p-2 bg-white rounded hover:bg-purple-100 transition-colors">
                        <Flower className="h-4 w-4 text-purple-600" />
                        <span className="text-sm text-gray-800">{flor.nombre}</span>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-gray-400 text-center py-4">No hay flores asociadas</p>
                  )}
                </div>
              </div>

              {/* Contenedores Asociados */}
              <div>
                <h3 className="text-lg font-semibold text-blue-700 mb-3 flex items-center gap-2">
                  <Package className="h-5 w-5" />
                  Contenedores Asociados ({proveedorDetalle.contenedores?.length || 0})
                </h3>
                <div className="space-y-2 max-h-60 overflow-y-auto border border-blue-200 rounded-lg p-3 bg-blue-50">
                  {proveedorDetalle.contenedores && proveedorDetalle.contenedores.length > 0 ? (
                    proveedorDetalle.contenedores.map(contenedor => (
                      <div key={contenedor.id} className="flex items-center gap-2 p-2 bg-white rounded hover:bg-blue-100 transition-colors">
                        <Package className="h-4 w-4 text-blue-600" />
                        <span className="text-sm text-gray-800">{contenedor.nombre}</span>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-gray-400 text-center py-4">No hay contenedores asociados</p>
                  )}
                </div>
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => {
                  setProveedorDetalle(null)
                  abrirModalAsociarInsumos(proveedorDetalle.id)
                }}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
              >
                <Package className="h-4 w-4" />
                Asociar Insumos
              </button>
              <button
                onClick={() => {
                  setProveedorDetalle(null)
                  editarProveedor(proveedorDetalle.id)
                }}
                className="flex-1 px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors flex items-center justify-center gap-2"
              >
                <Save className="h-4 w-4" />
                Editar Proveedor
              </button>
              <button
                onClick={() => setProveedorDetalle(null)}
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
              >
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal Reponer Stock */}
      {modalReponerAbierto && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full p-6 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                <ShoppingCart className="h-6 w-6 text-orange-600" />
                Reponer Stock
              </h2>
              <button
                onClick={() => {
                  setModalReponerAbierto(false)
                  setLineasReposicion([])
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-6 w-6" />
              </button>
            </div>

            <div className="mb-4">
              <p className="text-sm text-gray-600 mb-4">
                Registra los insumos recibidos. El stock se actualizará automáticamente.
              </p>

              <div className="space-y-3">
                {lineasReposicion.map((linea, index) => (
                  <div key={index} className="p-4 border border-gray-200 rounded-lg bg-gray-50">
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-sm font-semibold text-gray-700">Línea #{index + 1}</span>
                      {lineasReposicion.length > 1 && (
                        <button
                          onClick={() => eliminarLineaReposicion(index)}
                          className="text-red-600 hover:text-red-800"
                        >
                          <X className="h-4 w-4" />
                        </button>
                      )}
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                      <div>
                        <label className="block text-xs font-medium text-gray-700 mb-1">
                          Tipo
                        </label>
                        <select
                          value={linea.tipo}
                          onChange={(e) => actualizarLineaReposicion(index, 'tipo', e.target.value)}
                          className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                        >
                          <option value="flor">Flor</option>
                          <option value="contenedor">Contenedor</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-xs font-medium text-gray-700 mb-1">
                          Insumo <span className="text-red-500">*</span>
                        </label>
                        <select
                          value={linea.insumo_id}
                          onChange={(e) => actualizarLineaReposicion(index, 'insumo_id', e.target.value)}
                          className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                        >
                          <option value="">Seleccionar...</option>
                          {linea.tipo === 'flor' ? (
                            flores.map(flor => (
                              <option key={flor.id} value={flor.id}>
                                {flor.nombre} (Stock: {flor.cantidad_stock || 0})
                              </option>
                            ))
                          ) : (
                            contenedores.map(contenedor => (
                              <option key={contenedor.id} value={contenedor.id}>
                                {contenedor.nombre} (Stock: {contenedor.cantidad_stock || 0})
                              </option>
                            ))
                          )}
                        </select>
                      </div>

                      <div>
                        <label className="block text-xs font-medium text-gray-700 mb-1">
                          Cantidad <span className="text-red-500">*</span>
                        </label>
                        <input
                          type="text"
                          value={linea.cantidad}
                          onChange={(e) => actualizarLineaReposicion(index, 'cantidad', e.target.value)}
                          placeholder="0"
                          className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                        />
                      </div>

                      <div className="md:col-span-3">
                        <label className="block text-xs font-medium text-gray-700 mb-1">
                          Proveedor <span className="text-red-500">*</span>
                        </label>
                        <select
                          value={linea.proveedor_id}
                          onChange={(e) => actualizarLineaReposicion(index, 'proveedor_id', e.target.value)}
                          className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                        >
                          <option value="">Seleccionar proveedor...</option>
                          {proveedores.map(prov => (
                            <option key={prov.id} value={prov.id}>
                              {prov.nombre} {prov.empresa ? `(${prov.empresa})` : ''}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <button
                onClick={agregarLineaReposicion}
                className="mt-3 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors flex items-center gap-2 text-sm"
              >
                <Plus className="h-4 w-4" />
                Agregar otra línea
              </button>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => {
                  setModalReponerAbierto(false)
                  setLineasReposicion([])
                }}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={procesarReposicion}
                className="flex-1 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors flex items-center justify-center gap-2"
              >
                <ShoppingCart className="h-4 w-4" />
                Procesar Reposición
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default InsumosPage

