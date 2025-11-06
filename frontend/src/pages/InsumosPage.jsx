import { useState, useEffect } from 'react'
import { Flower, Package, AlertCircle, Search, Plus, Save, X } from 'lucide-react'
import axios from 'axios'
import { API_URL } from '../services/api'

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
  const [loading, setLoading] = useState(true)
  const [busqueda, setBusqueda] = useState('')
  const [vistaActiva, setVistaActiva] = useState('flores')
  const [guardando, setGuardando] = useState({})
  const [modalFlorAbierto, setModalFlorAbierto] = useState(false)
  const [modalContenedorAbierto, setModalContenedorAbierto] = useState(false)
  const [nuevaFlor, setNuevaFlor] = useState({
    tipo: '',
    color: '',
    costo_unitario: 0,
    ubicacion: 'Taller',
    cantidad_stock: 0
  })
  const [nuevoContenedor, setNuevoContenedor] = useState({
    tipo: '',
    material: '',
    tamano: '',
    color: '',
    costo: 0,
    ubicacion: 'Bodega 1',
    cantidad_stock: 0
  })

  useEffect(() => {
    cargarInsumos()
  }, [])

  const cargarInsumos = async () => {
    try {
      setLoading(true)
      const [floresResponse, contenedoresResponse] = await Promise.all([
        axios.get(`${API_URL}/inventario/flores`),
        axios.get(`${API_URL}/inventario/contenedores`)
      ])
      
      if (floresResponse.data.success) {
        setFlores(floresResponse.data.data)
      }
      
      if (contenedoresResponse.data.success) {
        setContenedores(contenedoresResponse.data.data)
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
      } else {
        valorFinal = parseInt(valor) || 0
      }
      
      const response = await axios.patch(`${API_URL}/inventario/flores/${id}`, {
        [campo]: valorFinal
      })
      
      if (response.data.success) {
        // Actualizar con la respuesta del servidor
        setFlores(prev => prev.map(f => 
          f.id === id ? response.data.data : f
        ))
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
      } else {
        valorFinal = parseInt(valor) || 0
      }

      const response = await axios.patch(`${API_URL}/inventario/contenedores/${id}`, {
        [campo]: valorFinal
      })

      if (response.data.success) {
        // Actualizar con la respuesta del servidor
        setContenedores(prev => prev.map(c =>
          c.id === id ? response.data.data : c
        ))
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

      const response = await axios.post(`${API_URL}/inventario/flores`, nuevaFlor)

      if (response.data.success) {
        setFlores(prev => [...prev, response.data.data])
        setModalFlorAbierto(false)
        setNuevaFlor({
          tipo: '',
          color: '',
          costo_unitario: 0,
          ubicacion: 'Taller',
          cantidad_stock: 0
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

      const response = await axios.post(`${API_URL}/inventario/contenedores`, nuevoContenedor)

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
          cantidad_stock: 0
        })
        alert(response.data.message || 'Contenedor creado exitosamente')
      }
    } catch (error) {
      console.error('Error al crear contenedor:', error)
      alert(error.response?.data?.error || 'Error al crear contenedor')
    }
  }

  const floresFiltradas = flores.filter(f =>
    f.nombre.toLowerCase().includes(busqueda.toLowerCase()) ||
    f.color?.toLowerCase().includes(busqueda.toLowerCase())
  )

  const contenedoresFiltrados = contenedores.filter(c =>
    c.nombre.toLowerCase().includes(busqueda.toLowerCase()) ||
    c.tipo?.toLowerCase().includes(busqueda.toLowerCase())
  )

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
                {flores.filter(f => f.cantidad_disponible < 10).length + 
                 contenedores.filter(c => c.cantidad_disponible < 5).length}
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
        <div className="p-4 border-b border-gray-200">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Buscar por nombre o color..."
                value={busqueda}
                onChange={(e) => setBusqueda(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            
            <div className="flex gap-2">
              <button
                onClick={() => setVistaActiva('flores')}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  vistaActiva === 'flores'
                    ? 'bg-purple-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <Flower className="inline h-4 w-4 mr-2" />
                Flores ({flores.length})
              </button>
              <button
                onClick={() => setVistaActiva('contenedores')}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  vistaActiva === 'contenedores'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <Package className="inline h-4 w-4 mr-2" />
                Contenedores ({contenedores.length})
              </button>

              {vistaActiva === 'flores' && (
                <button
                  onClick={() => setModalFlorAbierto(true)}
                  className="px-4 py-2 rounded-lg font-medium bg-purple-600 text-white hover:bg-purple-700 transition-colors flex items-center gap-2"
                >
                  <Plus className="h-4 w-4" />
                  Nueva Flor
                </button>
              )}

              {vistaActiva === 'contenedores' && (
                <button
                  onClick={() => setModalContenedorAbierto(true)}
                  className="px-4 py-2 rounded-lg font-medium bg-blue-600 text-white hover:bg-blue-700 transition-colors flex items-center gap-2"
                >
                  <Plus className="h-4 w-4" />
                  Nuevo Contenedor
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Tabla de Flores */}
        {vistaActiva === 'flores' && (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-purple-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-purple-900 uppercase tracking-wider">Nombre</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-purple-900 uppercase tracking-wider">Color</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-purple-900 uppercase tracking-wider">Costo/u</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-purple-900 uppercase tracking-wider">Sector</th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-purple-900 uppercase tracking-wider">Stock Total</th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-purple-900 uppercase tracking-wider">En Uso</th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-purple-900 uppercase tracking-wider">En Evento</th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-purple-900 uppercase tracking-wider">Disponible</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {floresFiltradas.map((flor) => (
                  <tr key={flor.id} className="hover:bg-purple-50 transition-colors">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <Flower className="h-4 w-4 text-purple-600" />
                        <span className="text-sm font-medium text-gray-900">{flor.nombre}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <select
                        value={flor.color || ''}
                        onChange={(e) => actualizarFlor(flor.id, 'color', e.target.value)}
                        className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-purple-500 bg-white"
                      >
                        <option value="">Sin color</option>
                        {COLORES_FLORES.map(color => (
                          <option key={color} value={color}>{color}</option>
                        ))}
                      </select>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-1">
                        <span className="text-xs text-gray-500">$</span>
                        <input
                          type="number"
                          min="0"
                          step="100"
                          value={flor.costo_unitario || 0}
                          onChange={(e) => actualizarFlor(flor.id, 'costo_unitario', e.target.value)}
                          className="w-24 px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-purple-500"
                        />
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <input
                        type="text"
                        value={flor.ubicacion || ''}
                        onChange={(e) => actualizarFlor(flor.id, 'ubicacion', e.target.value)}
                        placeholder="Taller, Bodega 1..."
                        className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-purple-500"
                      />
                    </td>
                    <td className="px-4 py-3 text-center">
                      <input
                        type="number"
                        min="0"
                        value={flor.cantidad_stock || 0}
                        onChange={(e) => actualizarFlor(flor.id, 'cantidad_stock', e.target.value)}
                        className="w-20 px-2 py-1 text-sm text-center border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-purple-500"
                      />
                    </td>
                    <td className="px-4 py-3 text-center">
                      <input
                        type="number"
                        min="0"
                        value={flor.cantidad_en_uso || 0}
                        onChange={(e) => actualizarFlor(flor.id, 'cantidad_en_uso', e.target.value)}
                        className="w-20 px-2 py-1 text-sm text-center border border-blue-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50"
                      />
                    </td>
                    <td className="px-4 py-3 text-center">
                      <input
                        type="number"
                        min="0"
                        value={flor.cantidad_en_evento || 0}
                        onChange={(e) => actualizarFlor(flor.id, 'cantidad_en_evento', e.target.value)}
                        className="w-20 px-2 py-1 text-sm text-center border border-purple-300 rounded focus:outline-none focus:ring-2 focus:ring-purple-500 bg-purple-50"
                      />
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span className={`text-sm font-semibold ${getStockColor(flor.cantidad_disponible, flor.cantidad_stock)}`}>
                        {flor.cantidad_disponible || 0}
                      </span>
                      {guardando[`flor-${flor.id}`] && (
                        <span className="ml-2 text-xs text-gray-500">💾</span>
                      )}
                    </td>
                  </tr>
                ))}
                {floresFiltradas.length === 0 && (
                  <tr>
                    <td colSpan="8" className="px-4 py-8 text-center text-gray-500">
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
                  <th className="px-4 py-3 text-left text-xs font-medium text-blue-900 uppercase tracking-wider">Nombre</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-blue-900 uppercase tracking-wider">Tipo</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-blue-900 uppercase tracking-wider">Costo</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-blue-900 uppercase tracking-wider">Sector</th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-blue-900 uppercase tracking-wider">Stock Total</th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-blue-900 uppercase tracking-wider">En Uso</th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-blue-900 uppercase tracking-wider">En Evento</th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-blue-900 uppercase tracking-wider">Disponible</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {contenedoresFiltrados.map((contenedor) => (
                  <tr key={contenedor.id} className="hover:bg-blue-50 transition-colors">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <Package className="h-4 w-4 text-blue-600" />
                        <span className="text-sm font-medium text-gray-900">{contenedor.nombre}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-sm text-gray-700">{contenedor.tipo || '-'}</span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-1">
                        <span className="text-xs text-gray-500">$</span>
                        <input
                          type="number"
                          min="0"
                          step="100"
                          value={contenedor.costo || 0}
                          onChange={(e) => actualizarContenedor(contenedor.id, 'costo', e.target.value)}
                          className="w-24 px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <input
                        type="text"
                        value={contenedor.ubicacion || ''}
                        onChange={(e) => actualizarContenedor(contenedor.id, 'ubicacion', e.target.value)}
                        placeholder="Bodega 1, Bodega 2..."
                        className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </td>
                    <td className="px-4 py-3 text-center">
                      <input
                        type="number"
                        min="0"
                        value={contenedor.cantidad_stock || 0}
                        onChange={(e) => actualizarContenedor(contenedor.id, 'cantidad_stock', e.target.value)}
                        className="w-20 px-2 py-1 text-sm text-center border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </td>
                    <td className="px-4 py-3 text-center">
                      <input
                        type="number"
                        min="0"
                        value={contenedor.cantidad_en_uso || 0}
                        onChange={(e) => actualizarContenedor(contenedor.id, 'cantidad_en_uso', e.target.value)}
                        className="w-20 px-2 py-1 text-sm text-center border border-blue-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 bg-blue-50"
                      />
                    </td>
                    <td className="px-4 py-3 text-center">
                      <input
                        type="number"
                        min="0"
                        value={contenedor.cantidad_en_evento || 0}
                        onChange={(e) => actualizarContenedor(contenedor.id, 'cantidad_en_evento', e.target.value)}
                        className="w-20 px-2 py-1 text-sm text-center border border-purple-300 rounded focus:outline-none focus:ring-2 focus:ring-purple-500 bg-purple-50"
                      />
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span className={`text-sm font-semibold ${getStockColor(contenedor.cantidad_disponible, contenedor.cantidad_stock)}`}>
                        {contenedor.cantidad_disponible || 0}
                      </span>
                      {guardando[`contenedor-${contenedor.id}`] && (
                        <span className="ml-2 text-xs text-gray-500">💾</span>
                      )}
                    </td>
                  </tr>
                ))}
                {contenedoresFiltrados.length === 0 && (
                  <tr>
                    <td colSpan="8" className="px-4 py-8 text-center text-gray-500">
                      No se encontraron contenedores
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
                  type="number"
                  min="0"
                  step="100"
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
                  type="number"
                  min="0"
                  value={nuevaFlor.cantidad_stock}
                  onChange={(e) => setNuevaFlor({ ...nuevaFlor, cantidad_stock: parseInt(e.target.value) || 0 })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
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
                  type="number"
                  min="0"
                  step="100"
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
                  type="number"
                  min="0"
                  value={nuevoContenedor.cantidad_stock}
                  onChange={(e) => setNuevoContenedor({ ...nuevoContenedor, cantidad_stock: parseInt(e.target.value) || 0 })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
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
    </div>
  )
}

export default InsumosPage

