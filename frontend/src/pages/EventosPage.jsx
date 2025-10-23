import { useState, useEffect } from 'react'
import axios from 'axios'
import { Calendar, Users, DollarSign, Package, Plus, X, CheckCircle, Clock, FileText, Trash2, AlertTriangle } from 'lucide-react'

const API_URL = 'http://localhost:8000/api'

const ESTADOS_EVENTO = [
  'Cotización',
  'Propuesta Enviada',
  'Confirmado',
  'En Preparación',
  'En Evento',
  'Finalizado',
  'Retirado'
]

const TIPOS_EVENTO = [
  'Boda',
  'Cumpleaños',
  'Aniversario',
  'Corporativo',
  'Baby Shower',
  'Graduación',
  'Otro'
]

const TIPOS_COSTO = [
  { value: 'flor', label: '🌸 Flor (del inventario)' },
  { value: 'contenedor', label: '🏺 Contenedor (del inventario)' },
  { value: 'producto', label: '💐 Arreglo (del catálogo)' },
  { value: 'producto_evento', label: '🎁 Producto Evento (manteles, velas, etc.)' },
  { value: 'mano_obra', label: '👷 Mano de Obra (HH)' },
  { value: 'transporte', label: '🚚 Transporte' },
  { value: 'otro', label: '📦 Otro' }
]

function EventosPage() {
  const [eventos, setEventos] = useState([])
  const [loading, setLoading] = useState(true)
  const [mostrarFormulario, setMostrarFormulario] = useState(false)
  const [eventoSeleccionado, setEventoSeleccionado] = useState(null)
  
  // Catálogos para los selectores
  const [flores, setFlores] = useState([])
  const [contenedores, setContenedores] = useState([])
  const [productos, setProductos] = useState([])
  const [productosEvento, setProductosEvento] = useState([])
  
  // Form state
  const [formData, setFormData] = useState({
    cliente_nombre: '',
    cliente_telefono: '',
    cliente_email: '',
    nombre_evento: '',
    tipo_evento: 'Boda',
    fecha_evento: '',
    hora_evento: '',
    lugar_evento: '',
    cantidad_personas: 0,
    margen_porcentaje: 30,
    notas_cotizacion: ''
  })
  
  // Líneas de costos dinámicas
  const [lineasCosto, setLineasCosto] = useState([
    {
      id: Date.now(),
      tipo: 'mano_obra',
      item_id: null,
      nombre: '',
      cantidad: 1,
      costo_unitario: 0
    }
  ])
  
  useEffect(() => {
    cargarEventos()
    cargarCatalogos()
  }, [])
  
  const cargarEventos = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`${API_URL}/eventos`)
      if (response.data.success) {
        setEventos(response.data.data)
      }
    } catch (err) {
      console.error('Error al cargar eventos:', err)
      alert('❌ Error al cargar eventos')
    } finally {
      setLoading(false)
    }
  }
  
  const cargarCatalogos = async () => {
    try {
      const [resFlores, resContenedores, resProductos, resProductosEvento] = await Promise.all([
        axios.get(`${API_URL}/inventario/flores`),
        axios.get(`${API_URL}/inventario/contenedores`),
        axios.get(`${API_URL}/productos`),
        axios.get(`${API_URL}/eventos/productos-evento`)
      ])
      
      if (resFlores.data.success) setFlores(resFlores.data.data)
      if (resContenedores.data.success) setContenedores(resContenedores.data.data)
      if (resProductos.data.success) setProductos(resProductos.data.data)
      if (resProductosEvento.data.success) setProductosEvento(resProductosEvento.data.data)
    } catch (err) {
      console.error('Error cargando catálogos:', err)
    }
  }
  
  const agregarLineaCosto = () => {
    setLineasCosto([...lineasCosto, {
      id: Date.now(),
      tipo: 'mano_obra',
      item_id: null,
      nombre: '',
      cantidad: 1,
      costo_unitario: 0
    }])
  }
  
  const eliminarLineaCosto = (id) => {
    if (lineasCosto.length === 1) {
      alert('⚠️ Debe haber al menos una línea de costo')
      return
    }
    setLineasCosto(lineasCosto.filter(linea => linea.id !== id))
  }
  
  const actualizarLineaCosto = (id, campo, valor) => {
    setLineasCosto(lineasCosto.map(linea => {
      if (linea.id === id) {
        const nuevaLinea = { ...linea, [campo]: valor }
        
        // Si cambia el tipo, resetear item_id y nombre
        if (campo === 'tipo') {
          nuevaLinea.item_id = null
          nuevaLinea.nombre = ''
          nuevaLinea.costo_unitario = 0
        }
        
        // Si selecciona un item del inventario, auto-llenar costo
        if (campo === 'item_id') {
          let itemSeleccionado = null
          if (linea.tipo === 'flor') {
            itemSeleccionado = flores.find(f => f.id === valor)
            if (itemSeleccionado) {
              nuevaLinea.nombre = itemSeleccionado.nombre
              nuevaLinea.costo_unitario = itemSeleccionado.costo_unitario
            }
          } else if (linea.tipo === 'contenedor') {
            itemSeleccionado = contenedores.find(c => c.id === valor)
            if (itemSeleccionado) {
              nuevaLinea.nombre = itemSeleccionado.nombre
              nuevaLinea.costo_unitario = itemSeleccionado.costo
            }
          } else if (linea.tipo === 'producto') {
            itemSeleccionado = productos.find(p => p.id === valor)
            if (itemSeleccionado) {
              nuevaLinea.nombre = itemSeleccionado.nombre
              nuevaLinea.costo_unitario = itemSeleccionado.costo_estimado || 0
            }
          } else if (linea.tipo === 'producto_evento') {
            itemSeleccionado = productosEvento.find(pe => pe.codigo === valor)
            if (itemSeleccionado) {
              nuevaLinea.nombre = itemSeleccionado.nombre
              nuevaLinea.costo_unitario = itemSeleccionado.costo_alquiler || itemSeleccionado.costo_compra || 0
            }
          }
        }
        
        return nuevaLinea
      }
      return linea
    }))
  }
  
  const calcularCostoTotal = () => {
    return lineasCosto.reduce((total, linea) => {
      return total + (linea.cantidad * linea.costo_unitario)
    }, 0)
  }
  
  const calcularPrecioPropuesta = () => {
    const costoTotal = calcularCostoTotal()
    const margen = formData.margen_porcentaje / 100
    return costoTotal * (1 + margen)
  }
  
  const handleSubmit = async (e) => {
    e.preventDefault()
    
    // Validar que haya al menos una línea con costo
    const totalCosto = calcularCostoTotal()
    if (totalCosto === 0) {
      alert('⚠️ Debe agregar al menos un costo al evento')
      return
    }
    
    try {
      // 1. Crear evento
      const eventoPayload = {
        ...formData,
        costo_total: totalCosto,
        precio_propuesta: calcularPrecioPropuesta()
      }
      
      const response = await axios.post(`${API_URL}/eventos`, eventoPayload)
      
      if (response.data.success) {
        const eventoId = response.data.data.id
        
        // 2. Agregar cada línea de costo como insumo
        for (const linea of lineasCosto) {
          const insumoPayload = {
            tipo_insumo: linea.tipo,
            cantidad: linea.cantidad,
            costo_unitario: linea.costo_unitario,
            notas: ''
          }
          
          // Asignar referencia según tipo
          if (linea.tipo === 'flor' && linea.item_id) {
            insumoPayload.flor_id = linea.item_id
          } else if (linea.tipo === 'contenedor' && linea.item_id) {
            insumoPayload.contenedor_id = linea.item_id
          } else if (linea.tipo === 'producto' && linea.item_id) {
            insumoPayload.producto_id = linea.item_id
          } else if (linea.tipo === 'producto_evento' && linea.item_id) {
            const pe = productosEvento.find(p => p.codigo === linea.item_id)
            if (pe) insumoPayload.producto_evento_id = pe.id
          } else {
            insumoPayload.nombre_otro = linea.nombre
          }
          
          await axios.post(`${API_URL}/eventos/${eventoId}/insumos`, insumoPayload)
        }
        
        alert(`✅ Evento creado: ${eventoId}`)
        setMostrarFormulario(false)
        resetForm()
        cargarEventos()
      }
    } catch (err) {
      console.error('Error al crear evento:', err)
      alert(`❌ Error: ${err.response?.data?.error || err.message}`)
    }
  }
  
  const resetForm = () => {
    setFormData({
      cliente_nombre: '',
      cliente_telefono: '',
      cliente_email: '',
      nombre_evento: '',
      tipo_evento: 'Boda',
      fecha_evento: '',
      hora_evento: '',
      lugar_evento: '',
      cantidad_personas: 0,
      margen_porcentaje: 30,
      notas_cotizacion: ''
    })
    
    setLineasCosto([{
      id: Date.now(),
      tipo: 'mano_obra',
      item_id: null,
      nombre: '',
      cantidad: 1,
      costo_unitario: 0
    }])
  }
  
  const getEstadoColor = (estado) => {
    const colores = {
      'Cotización': 'bg-gray-100 text-gray-800',
      'Propuesta Enviada': 'bg-blue-100 text-blue-800',
      'Confirmado': 'bg-green-100 text-green-800',
      'En Preparación': 'bg-yellow-100 text-yellow-800',
      'En Evento': 'bg-purple-100 text-purple-800',
      'Finalizado': 'bg-indigo-100 text-indigo-800',
      'Retirado': 'bg-gray-200 text-gray-600'
    }
    return colores[estado] || 'bg-gray-100 text-gray-800'
  }
  
  const renderSelectorItem = (linea) => {
    const tipo = linea.tipo
    
    if (tipo === 'flor') {
      return (
        <select
          value={linea.item_id || ''}
          onChange={(e) => actualizarLineaCosto(linea.id, 'item_id', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
          required
        >
          <option value="">Seleccione una flor...</option>
          {flores.map(flor => (
            <option key={flor.id} value={flor.id}>
              {flor.nombre} - ${flor.costo_unitario.toLocaleString()} (Stock: {flor.cantidad_disponible})
            </option>
          ))}
        </select>
      )
    }
    
    if (tipo === 'contenedor') {
      return (
        <select
          value={linea.item_id || ''}
          onChange={(e) => actualizarLineaCosto(linea.id, 'item_id', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
          required
        >
          <option value="">Seleccione un contenedor...</option>
          {contenedores.map(cont => (
            <option key={cont.id} value={cont.id}>
              {cont.nombre} - ${cont.costo.toLocaleString()} (Stock: {cont.cantidad_disponible})
            </option>
          ))}
        </select>
      )
    }
    
    if (tipo === 'producto') {
      return (
        <select
          value={linea.item_id || ''}
          onChange={(e) => actualizarLineaCosto(linea.id, 'item_id', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
          required
        >
          <option value="">Seleccione un arreglo...</option>
          {productos.map(prod => (
            <option key={prod.id} value={prod.id}>
              {prod.nombre} - ${(prod.costo_estimado || 0).toLocaleString()}
            </option>
          ))}
        </select>
      )
    }
    
    if (tipo === 'producto_evento') {
      return (
        <select
          value={linea.item_id || ''}
          onChange={(e) => actualizarLineaCosto(linea.id, 'item_id', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
          required
        >
          <option value="">Seleccione un producto evento...</option>
          {productosEvento.map(pe => (
            <option key={pe.codigo} value={pe.codigo}>
              {pe.nombre} - Alquiler ${(pe.costo_alquiler || 0).toLocaleString()} (Disponible: {pe.cantidad_disponible})
            </option>
          ))}
        </select>
      )
    }
    
    // Para mano_obra, transporte, otro
    return (
      <input
        type="text"
        value={linea.nombre}
        onChange={(e) => actualizarLineaCosto(linea.id, 'nombre', e.target.value)}
        placeholder="Ej: Montaje y desmontaje 4 horas"
        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
        required
      />
    )
  }
  
  return (
    <div className="px-4 sm:px-0">
      {/* Header */}
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Calendar className="h-8 w-8 text-primary-600" />
            Gestión de Eventos
          </h1>
          <p className="mt-1 text-sm text-gray-600">
            {eventos.length} evento{eventos.length !== 1 ? 's' : ''} registrado{eventos.length !== 1 ? 's' : ''}
          </p>
        </div>
        
        <button
          onClick={() => setMostrarFormulario(true)}
          className="bg-primary-600 hover:bg-primary-700 text-white px-6 py-3 rounded-lg font-semibold flex items-center gap-2 shadow-lg hover:shadow-xl transition-all"
        >
          <Plus className="h-5 w-5" />
          Nueva Cotización
        </button>
      </div>
      
      {/* Estadísticas Rápidas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-gray-400">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Cotizaciones</p>
              <p className="text-2xl font-bold text-gray-900">
                {eventos.filter(e => e.estado === 'Cotización').length}
              </p>
            </div>
            <FileText className="h-8 w-8 text-gray-400" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-blue-400">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Propuestas</p>
              <p className="text-2xl font-bold text-blue-900">
                {eventos.filter(e => e.estado === 'Propuesta Enviada').length}
              </p>
            </div>
            <Clock className="h-8 w-8 text-blue-400" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-green-400">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Confirmados</p>
              <p className="text-2xl font-bold text-green-900">
                {eventos.filter(e => e.estado === 'Confirmado').length}
              </p>
            </div>
            <CheckCircle className="h-8 w-8 text-green-400" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-purple-400">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">En Proceso</p>
              <p className="text-2xl font-bold text-purple-900">
                {eventos.filter(e => ['En Preparación', 'En Evento'].includes(e.estado)).length}
              </p>
            </div>
            <Package className="h-8 w-8 text-purple-400" />
          </div>
        </div>
      </div>
      
      {/* Lista de Eventos */}
      {loading ? (
        <div className="text-center py-12 text-gray-500">
          Cargando eventos...
        </div>
      ) : eventos.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <Calendar className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No hay eventos registrados</h3>
          <p className="text-gray-600 mb-6">Crea tu primera cotización para comenzar</p>
          <button
            onClick={() => setMostrarFormulario(true)}
            className="bg-primary-600 hover:bg-primary-700 text-white px-6 py-3 rounded-lg font-semibold inline-flex items-center gap-2"
          >
            <Plus className="h-5 w-5" />
            Nueva Cotización
          </button>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Evento
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Cliente
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Fecha
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Estado
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Precio
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {eventos.map((evento) => (
                <tr key={evento.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <Calendar className="h-5 w-5 text-gray-400 mr-3" />
                      <div>
                        <div className="text-sm font-medium text-gray-900 flex items-center gap-2">
                          {evento.nombre_evento}
                          {evento.insumos_faltantes && (
                            <AlertTriangle className="h-4 w-4 text-red-500" title="⚠️ Insumos faltantes" />
                          )}
                        </div>
                        <div className="text-sm text-gray-500">{evento.tipo_evento}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{evento.cliente_nombre}</div>
                    <div className="text-sm text-gray-500">{evento.cliente_telefono}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {evento.fecha_evento ? new Date(evento.fecha_evento).toLocaleDateString('es-CL') : '-'}
                    </div>
                    <div className="text-sm text-gray-500">{evento.hora_evento || '-'}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getEstadoColor(evento.estado)}`}>
                      {evento.estado}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      ${(evento.precio_propuesta || 0).toLocaleString('es-CL')}
                    </div>
                    <div className="text-sm text-gray-500">
                      Costo: ${(evento.costo_total || 0).toLocaleString('es-CL')}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      onClick={() => setEventoSeleccionado(evento)}
                      className="text-primary-600 hover:text-primary-900"
                    >
                      Ver Detalles
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      
      {/* Modal Formulario Nueva Cotización */}
      {mostrarFormulario && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={() => setMostrarFormulario(false)}>
          <div className="bg-white rounded-lg shadow-xl w-full max-w-6xl max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between z-10">
              <h2 className="text-2xl font-bold text-gray-900">Nueva Cotización de Evento</h2>
              <button onClick={() => setMostrarFormulario(false)} className="text-gray-400 hover:text-gray-600">
                <X className="h-6 w-6" />
              </button>
            </div>
            
            <form onSubmit={handleSubmit} className="p-6 space-y-6">
              {/* Información del Cliente */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <Users className="h-5 w-5 text-primary-600" />
                  Información del Cliente
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Nombre *</label>
                    <input
                      type="text"
                      required
                      value={formData.cliente_nombre}
                      onChange={(e) => setFormData({...formData, cliente_nombre: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Teléfono *</label>
                    <input
                      type="tel"
                      required
                      value={formData.cliente_telefono}
                      onChange={(e) => setFormData({...formData, cliente_telefono: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                    <input
                      type="email"
                      value={formData.cliente_email}
                      onChange={(e) => setFormData({...formData, cliente_email: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    />
                  </div>
                </div>
              </div>
              
              {/* Información del Evento */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <Calendar className="h-5 w-5 text-primary-600" />
                  Información del Evento
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Nombre del Evento *</label>
                    <input
                      type="text"
                      required
                      value={formData.nombre_evento}
                      onChange={(e) => setFormData({...formData, nombre_evento: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      placeholder="Ej: Boda María & Juan"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Tipo de Evento *</label>
                    <select
                      required
                      value={formData.tipo_evento}
                      onChange={(e) => setFormData({...formData, tipo_evento: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    >
                      {TIPOS_EVENTO.map(tipo => (
                        <option key={tipo} value={tipo}>{tipo}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Fecha del Evento</label>
                    <input
                      type="date"
                      value={formData.fecha_evento}
                      onChange={(e) => setFormData({...formData, fecha_evento: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Hora</label>
                    <input
                      type="time"
                      value={formData.hora_evento}
                      onChange={(e) => setFormData({...formData, hora_evento: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    />
                  </div>
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Lugar del Evento</label>
                    <input
                      type="text"
                      value={formData.lugar_evento}
                      onChange={(e) => setFormData({...formData, lugar_evento: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      placeholder="Ej: Parque Araucano, Santiago"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Cantidad de Personas</label>
                    <input
                      type="number"
                      min="0"
                      value={formData.cantidad_personas}
                      onChange={(e) => setFormData({...formData, cantidad_personas: parseInt(e.target.value) || 0})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    />
                  </div>
                </div>
              </div>
              
              {/* Líneas de Costos Dinámicas */}
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                    <DollarSign className="h-5 w-5 text-primary-600" />
                    Detalle de Costos
                  </h3>
                  <button
                    type="button"
                    onClick={agregarLineaCosto}
                    className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-semibold flex items-center gap-2 text-sm"
                  >
                    <Plus className="h-4 w-4" />
                    Agregar Línea
                  </button>
                </div>
                
                <div className="space-y-3">
                  {lineasCosto.map((linea, index) => (
                    <div key={linea.id} className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                      <div className="grid grid-cols-12 gap-3 items-start">
                        <div className="col-span-12 md:col-span-1 flex items-center">
                          <span className="text-sm font-medium text-gray-700">#{index + 1}</span>
                        </div>
                        
                        <div className="col-span-12 md:col-span-3">
                          <label className="block text-xs font-medium text-gray-700 mb-1">Tipo de Costo *</label>
                          <select
                            value={linea.tipo}
                            onChange={(e) => actualizarLineaCosto(linea.id, 'tipo', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 text-sm"
                          >
                            {TIPOS_COSTO.map(tipo => (
                              <option key={tipo.value} value={tipo.value}>{tipo.label}</option>
                            ))}
                          </select>
                        </div>
                        
                        <div className="col-span-12 md:col-span-4">
                          <label className="block text-xs font-medium text-gray-700 mb-1">
                            {['flor', 'contenedor', 'producto', 'producto_evento'].includes(linea.tipo) ? 'Seleccione del inventario *' : 'Descripción *'}
                          </label>
                          {renderSelectorItem(linea)}
                        </div>
                        
                        <div className="col-span-6 md:col-span-2">
                          <label className="block text-xs font-medium text-gray-700 mb-1">Cantidad *</label>
                          <input
                            type="number"
                            min="1"
                            value={linea.cantidad}
                            onChange={(e) => actualizarLineaCosto(linea.id, 'cantidad', parseInt(e.target.value) || 1)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 text-sm"
                          />
                        </div>
                        
                        <div className="col-span-6 md:col-span-2">
                          <label className="block text-xs font-medium text-gray-700 mb-1">Costo Unit. *</label>
                          <input
                            type="number"
                            min="0"
                            value={linea.costo_unitario}
                            onChange={(e) => actualizarLineaCosto(linea.id, 'costo_unitario', parseFloat(e.target.value) || 0)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 text-sm"
                            disabled={['flor', 'contenedor', 'producto', 'producto_evento'].includes(linea.tipo) && linea.item_id}
                          />
                        </div>
                        
                        <div className="col-span-10 md:col-span-2 flex items-center">
                          <div className="w-full">
                            <label className="block text-xs font-medium text-gray-700 mb-1">Total</label>
                            <div className="text-sm font-bold text-gray-900 px-3 py-2 bg-white rounded-lg border border-gray-300">
                              ${(linea.cantidad * linea.costo_unitario).toLocaleString('es-CL')}
                            </div>
                          </div>
                        </div>
                        
                        <div className="col-span-2 md:col-span-1 flex items-end justify-center">
                          <button
                            type="button"
                            onClick={() => eliminarLineaCosto(linea.id)}
                            className="text-red-600 hover:text-red-800 p-2"
                            title="Eliminar línea"
                          >
                            <Trash2 className="h-5 w-5" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                
                {/* Resumen de Costos */}
                <div className="mt-6 bg-primary-50 border-2 border-primary-200 rounded-lg p-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Costo Total</label>
                      <div className="text-2xl font-bold text-gray-900">
                        ${calcularCostoTotal().toLocaleString('es-CL')}
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Margen Deseado (%)</label>
                      <input
                        type="number"
                        min="0"
                        max="100"
                        value={formData.margen_porcentaje}
                        onChange={(e) => setFormData({...formData, margen_porcentaje: parseFloat(e.target.value) || 30})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Precio Propuesta</label>
                      <div className="text-2xl font-bold text-primary-700">
                        ${calcularPrecioPropuesta().toLocaleString('es-CL')}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Notas */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Notas de Cotización</label>
                <textarea
                  rows="3"
                  value={formData.notas_cotizacion}
                  onChange={(e) => setFormData({...formData, notas_cotizacion: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  placeholder="Detalles adicionales, requerimientos especiales, etc."
                />
              </div>
              
              {/* Botones */}
              <div className="flex gap-3 pt-4 border-t border-gray-200">
                <button
                  type="button"
                  onClick={() => setMostrarFormulario(false)}
                  className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 transition-colors"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="flex-1 px-6 py-3 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 transition-colors"
                >
                  Crear Cotización
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      
      {/* Modal Detalles del Evento */}
      {eventoSeleccionado && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={() => setEventoSeleccionado(null)}>
          <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between z-10">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{eventoSeleccionado.nombre_evento}</h2>
                <p className="text-sm text-gray-600">{eventoSeleccionado.id} - {eventoSeleccionado.tipo_evento}</p>
              </div>
              <button onClick={() => setEventoSeleccionado(null)} className="text-gray-400 hover:text-gray-600">
                <X className="h-6 w-6" />
              </button>
            </div>
            
            <div className="p-6 space-y-6">
              {/* Estado y Alertas */}
              <div className="flex items-center gap-3">
                <span className={`px-4 py-2 inline-flex text-sm font-semibold rounded-full ${getEstadoColor(eventoSeleccionado.estado)}`}>
                  {eventoSeleccionado.estado}
                </span>
                {eventoSeleccionado.insumos_faltantes && (
                  <div className="flex items-center gap-2 bg-red-100 text-red-800 px-4 py-2 rounded-lg">
                    <AlertTriangle className="h-5 w-5" />
                    <span className="font-semibold">Insumos faltantes</span>
                  </div>
                )}
                {eventoSeleccionado.pagado && (
                  <div className="flex items-center gap-2 bg-green-100 text-green-800 px-4 py-2 rounded-lg">
                    <CheckCircle className="h-5 w-5" />
                    <span className="font-semibold">Pagado</span>
                  </div>
                )}
              </div>
              
              {/* Información del Cliente */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <Users className="h-5 w-5 text-primary-600" />
                  Cliente
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">Nombre</p>
                    <p className="font-medium text-gray-900">{eventoSeleccionado.cliente_nombre}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Teléfono</p>
                    <p className="font-medium text-gray-900">{eventoSeleccionado.cliente_telefono}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Email</p>
                    <p className="font-medium text-gray-900">{eventoSeleccionado.cliente_email || '-'}</p>
                  </div>
                </div>
              </div>
              
              {/* Información del Evento */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <Calendar className="h-5 w-5 text-primary-600" />
                  Detalles del Evento
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">Fecha</p>
                    <p className="font-medium text-gray-900">
                      {eventoSeleccionado.fecha_evento 
                        ? new Date(eventoSeleccionado.fecha_evento).toLocaleDateString('es-CL', { 
                            weekday: 'long', 
                            year: 'numeric', 
                            month: 'long', 
                            day: 'numeric' 
                          })
                        : '-'}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Hora</p>
                    <p className="font-medium text-gray-900">{eventoSeleccionado.hora_evento || '-'}</p>
                  </div>
                  <div className="md:col-span-2">
                    <p className="text-sm text-gray-600">Lugar</p>
                    <p className="font-medium text-gray-900">{eventoSeleccionado.lugar_evento || '-'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Cantidad de Personas</p>
                    <p className="font-medium text-gray-900">{eventoSeleccionado.cantidad_personas || '-'}</p>
                  </div>
                </div>
              </div>
              
              {/* Costos y Financiero */}
              <div className="bg-primary-50 rounded-lg p-4 border-2 border-primary-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <DollarSign className="h-5 w-5 text-primary-600" />
                  Información Financiera
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">Costo Total</p>
                    <p className="text-xl font-bold text-gray-900">
                      ${(eventoSeleccionado.costo_total || 0).toLocaleString('es-CL')}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Margen</p>
                    <p className="text-xl font-bold text-primary-700">
                      {eventoSeleccionado.margen_porcentaje || 0}%
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Precio Propuesta</p>
                    <p className="text-xl font-bold text-primary-900">
                      ${(eventoSeleccionado.precio_propuesta || 0).toLocaleString('es-CL')}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Precio Final</p>
                    <p className="text-xl font-bold text-green-700">
                      ${(eventoSeleccionado.precio_final || 0).toLocaleString('es-CL')}
                    </p>
                  </div>
                </div>
                
                {eventoSeleccionado.precio_final > 0 && (
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mt-4 pt-4 border-t border-primary-300">
                    <div>
                      <p className="text-sm text-gray-600">Anticipo</p>
                      <p className="text-lg font-bold text-gray-900">
                        ${(eventoSeleccionado.anticipo || 0).toLocaleString('es-CL')}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Saldo</p>
                      <p className="text-lg font-bold text-orange-600">
                        ${(eventoSeleccionado.saldo || 0).toLocaleString('es-CL')}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Estado de Pago</p>
                      <p className={`text-lg font-bold ${eventoSeleccionado.pagado ? 'text-green-600' : 'text-red-600'}`}>
                        {eventoSeleccionado.pagado ? 'Pagado' : 'Pendiente'}
                      </p>
                    </div>
                  </div>
                )}
              </div>
              
              {/* Estado de Insumos */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <Package className="h-5 w-5 text-primary-600" />
                  Estado de Insumos
                </h3>
                <div className="grid grid-cols-3 gap-4">
                  <div className="flex items-center gap-3">
                    <div className={`w-3 h-3 rounded-full ${eventoSeleccionado.insumos_reservados ? 'bg-green-500' : 'bg-gray-300'}`}></div>
                    <span className="text-sm text-gray-700">Reservados</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className={`w-3 h-3 rounded-full ${eventoSeleccionado.insumos_descontados ? 'bg-blue-500' : 'bg-gray-300'}`}></div>
                    <span className="text-sm text-gray-700">Descontados</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className={`w-3 h-3 rounded-full ${eventoSeleccionado.insumos_faltantes ? 'bg-red-500' : 'bg-green-500'}`}></div>
                    <span className="text-sm text-gray-700">{eventoSeleccionado.insumos_faltantes ? 'Con Faltantes' : 'Completo'}</span>
                  </div>
                </div>
              </div>
              
              {/* Notas */}
              {eventoSeleccionado.notas_cotizacion && (
                <div className="bg-yellow-50 rounded-lg p-4 border border-yellow-200">
                  <h3 className="text-sm font-semibold text-gray-900 mb-2">Notas</h3>
                  <p className="text-sm text-gray-700 whitespace-pre-wrap">{eventoSeleccionado.notas_cotizacion}</p>
                </div>
              )}
              
              {/* Fechas */}
              <div className="grid grid-cols-2 gap-4 text-xs text-gray-500">
                <div>
                  <p>Cotización creada:</p>
                  <p className="font-medium">
                    {eventoSeleccionado.fecha_cotizacion 
                      ? new Date(eventoSeleccionado.fecha_cotizacion).toLocaleString('es-CL')
                      : '-'}
                  </p>
                </div>
                <div>
                  <p>Última actualización:</p>
                  <p className="font-medium">
                    {eventoSeleccionado.fecha_actualizacion 
                      ? new Date(eventoSeleccionado.fecha_actualizacion).toLocaleString('es-CL')
                      : '-'}
                  </p>
                </div>
              </div>
            </div>
            
            <div className="sticky bottom-0 bg-gray-50 border-t border-gray-200 px-6 py-4 flex justify-end">
              <button
                onClick={() => setEventoSeleccionado(null)}
                className="px-6 py-2 bg-gray-600 text-white rounded-lg font-semibold hover:bg-gray-700 transition-colors"
              >
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default EventosPage
