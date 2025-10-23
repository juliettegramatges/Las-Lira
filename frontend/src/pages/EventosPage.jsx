import { useState, useEffect } from 'react'
import axios from 'axios'
import { Calendar, Users, DollarSign, Package, Plus, X, CheckCircle, Clock, FileText } from 'lucide-react'

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

function EventosPage() {
  const [eventos, setEventos] = useState([])
  const [loading, setLoading] = useState(true)
  const [mostrarFormulario, setMostrarFormulario] = useState(false)
  const [eventoSeleccionado, setEventoSeleccionado] = useState(null)
  
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
    costo_mano_obra: 0,
    costo_transporte: 0,
    costo_otros: 0,
    notas_cotizacion: ''
  })
  
  useEffect(() => {
    cargarEventos()
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
  
  const handleSubmit = async (e) => {
    e.preventDefault()
    
    try {
      const response = await axios.post(`${API_URL}/eventos`, formData)
      
      if (response.data.success) {
        alert(`✅ Evento creado: ${response.data.data.id}`)
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
      costo_mano_obra: 0,
      costo_transporte: 0,
      costo_otros: 0,
      notas_cotizacion: ''
    })
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
                        <div className="text-sm font-medium text-gray-900">{evento.nombre_evento}</div>
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
          <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
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
              
              {/* Costos */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <DollarSign className="h-5 w-5 text-primary-600" />
                  Costos Estimados
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Mano de Obra</label>
                    <input
                      type="number"
                      min="0"
                      value={formData.costo_mano_obra}
                      onChange={(e) => setFormData({...formData, costo_mano_obra: parseFloat(e.target.value) || 0})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Transporte</label>
                    <input
                      type="number"
                      min="0"
                      value={formData.costo_transporte}
                      onChange={(e) => setFormData({...formData, costo_transporte: parseFloat(e.target.value) || 0})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Otros Costos</label>
                    <input
                      type="number"
                      min="0"
                      value={formData.costo_otros}
                      onChange={(e) => setFormData({...formData, costo_otros: parseFloat(e.target.value) || 0})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Margen Deseado (%)</label>
                    <input
                      type="number"
                      min="0"
                      max="100"
                      value={formData.margen_porcentaje}
                      onChange={(e) => setFormData({...formData, margen_porcentaje: parseFloat(e.target.value) || 30})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    />
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
    </div>
  )
}

export default EventosPage

