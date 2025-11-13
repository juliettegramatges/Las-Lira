import { useState, useEffect } from 'react'
import axios from 'axios'
import { Calendar, Users, DollarSign, Package, Plus, X, CheckCircle, Clock, FileText, Trash2, AlertTriangle, Edit2 } from 'lucide-react'

import { API_URL } from '../services/api'
import { ESTADOS_EVENTO } from '../utils/constants'

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
  const [loadingFormulario, setLoadingFormulario] = useState(false)
  const [mostrarFormulario, setMostrarFormulario] = useState(false)
  const [eventoSeleccionado, setEventoSeleccionado] = useState(null)
  const [modoEdicion, setModoEdicion] = useState(false)
  const [eventoEditando, setEventoEditando] = useState(null)
  
  // Catálogos para los selectores
  const [flores, setFlores] = useState([])
  const [contenedores, setContenedores] = useState([])
  const [productos, setProductos] = useState([])
  const [productosEvento, setProductosEvento] = useState([])
  
  // Estados para búsqueda de clientes
  const [clienteEncontrado, setClienteEncontrado] = useState(null)
  const [buscandoCliente, setBuscandoCliente] = useState(false)
  const [sugerenciasClientes, setSugerenciasClientes] = useState([])
  const [mostrarSugerencias, setMostrarSugerencias] = useState(false)
  const [mostrarCrearCliente, setMostrarCrearCliente] = useState(false)
  const [creandoCliente, setCreandoCliente] = useState(false)
  const [nuevoClienteData, setNuevoClienteData] = useState({
    tipo_cliente: 'Nuevo',
    direccion_principal: '',
    notas: ''
  })
  
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
      // Productos puede venir en data o productos según el endpoint
      if (resProductos.data.success) {
        setProductos(resProductos.data.data || resProductos.data.productos || [])
      }
      if (resProductosEvento.data.success) setProductosEvento(resProductosEvento.data.data)
    } catch (err) {
      console.error('Error cargando catálogos:', err)
    }
  }
  
  const buscarClientesPorNombre = async (nombre) => {
    if (!nombre || nombre.length < 1) {
      setSugerenciasClientes([])
      setMostrarSugerencias(false)
      return
    }

    try {
      setBuscandoCliente(true)
      const response = await axios.get(`${API_URL}/clientes/buscar-por-nombre`, {
        params: { nombre }
      })

      if (response.data.success && response.data.clientes.length > 0) {
        setSugerenciasClientes(response.data.clientes)
        setMostrarSugerencias(true)
      } else {
        setSugerenciasClientes([])
        setMostrarSugerencias(true)
      }
    } catch (err) {
      console.error('Error al buscar clientes:', err)
      setSugerenciasClientes([])
      setMostrarSugerencias(true)
    } finally {
      setBuscandoCliente(false)
    }
  }
  
  const seleccionarCliente = (cliente) => {
    setClienteEncontrado(cliente)
    setMostrarSugerencias(false)
    setSugerenciasClientes([])
    setMostrarCrearCliente(false)

    // Autocompletar datos del cliente
    setFormData(prev => ({
      ...prev,
      cliente_nombre: cliente.nombre,
      cliente_telefono: cliente.telefono,
      cliente_email: cliente.email || ''
    }))
  }
  
  const handleCrearNuevoCliente = async () => {
    if (!formData.cliente_nombre || !formData.cliente_telefono) {
      alert('❌ Nombre y teléfono son obligatorios para crear un cliente')
      return
    }

    try {
      setCreandoCliente(true)

      const clienteData = {
        nombre: formData.cliente_nombre,
        telefono: formData.cliente_telefono,
        email: formData.cliente_email || null,
        tipo_cliente: nuevoClienteData.tipo_cliente,
        direccion_principal: nuevoClienteData.direccion_principal || null,
        notas: nuevoClienteData.notas || null
      }

      const response = await axios.post(`${API_URL}/clientes`, clienteData)

      if (response.data.success) {
        const nuevoCliente = response.data.data
        alert(`✅ Cliente ${nuevoCliente.id} creado exitosamente`)
        seleccionarCliente(nuevoCliente)
        setMostrarCrearCliente(false)
        setNuevoClienteData({
          tipo_cliente: 'Nuevo',
          direccion_principal: '',
          notas: ''
        })
      }
    } catch (err) {
      console.error('Error al crear cliente:', err)
      if (err.response?.data?.cliente_existente) {
        const clienteExistente = err.response.data.cliente_existente
        if (confirm(`Ya existe un cliente con ese teléfono: ${clienteExistente.nombre}.\n¿Deseas usar ese cliente?`)) {
          seleccionarCliente(clienteExistente)
          setMostrarCrearCliente(false)
        }
      } else {
        alert('❌ Error al crear cliente: ' + (err.response?.data?.error || err.message))
      }
    } finally {
      setCreandoCliente(false)
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
              nuevaLinea.costo_unitario = Number(itemSeleccionado.costo_unitario) || 0
            }
          } else if (linea.tipo === 'contenedor') {
            itemSeleccionado = contenedores.find(c => c.id === valor)
            if (itemSeleccionado) {
              nuevaLinea.nombre = itemSeleccionado.nombre
              nuevaLinea.costo_unitario = Number(itemSeleccionado.costo) || 0
            }
          } else if (linea.tipo === 'producto') {
            // Buscar producto por ID (puede ser string o número)
            itemSeleccionado = productos.find(p => {
              const pId = String(p.id)
              const vId = String(valor)
              return pId === vId || p.id === valor
            })
            if (itemSeleccionado) {
              nuevaLinea.nombre = itemSeleccionado.nombre
              // Usar precio_venta o precio como costo estimado
              const costo = itemSeleccionado.costo_estimado || itemSeleccionado.precio_venta || itemSeleccionado.precio || 0
              const costoNum = Number(costo)
              nuevaLinea.costo_unitario = isNaN(costoNum) ? 0 : costoNum
            }
          } else if (linea.tipo === 'producto_evento') {
            itemSeleccionado = productosEvento.find(pe => pe.codigo === valor)
            if (itemSeleccionado) {
              nuevaLinea.nombre = itemSeleccionado.nombre
              const costo = itemSeleccionado.costo_alquiler || itemSeleccionado.costo_compra || 0
              nuevaLinea.costo_unitario = Number(costo) || 0
            }
          }
        }
        
        // Si cambia cantidad o costo_unitario, permitir strings vacíos temporalmente
        if (campo === 'cantidad') {
          // Permitir string vacío para edición, pero convertir a número al final
          nuevaLinea.cantidad = valor === '' ? '' : valor
        }
        if (campo === 'costo_unitario') {
          // Permitir string vacío para edición, pero convertir a número al final
          nuevaLinea.costo_unitario = valor === '' ? '' : valor
        }
        
        return nuevaLinea
      }
      return linea
    }))
  }
  
  const calcularCostoTotal = () => {
    return lineasCosto.reduce((total, linea) => {
      const cantidad = Number(linea.cantidad) || 0
      const costoUnitario = Number(linea.costo_unitario) || 0
      return total + (cantidad * costoUnitario)
    }, 0)
  }
  
  const calcularPrecioPropuesta = () => {
    const costoTotal = calcularCostoTotal()
    const margen = Number(formData.margen_porcentaje) || 30
    const margenDecimal = margen / 100
    // Precio = Costo / (1 - margen) para obtener el precio con margen incluido
    return margenDecimal < 1 ? costoTotal / (1 - margenDecimal) : costoTotal
  }
  
  const handleSubmit = async (e) => {
    e.preventDefault()
    
    // Validar campos requeridos manualmente (más control que HTML5)
    if (!formData.cliente_nombre || formData.cliente_nombre.trim() === '') {
      alert('⚠️ El nombre del cliente es requerido')
      return
    }
    
    if (!formData.cliente_telefono || formData.cliente_telefono.trim() === '') {
      alert('⚠️ El teléfono del cliente es requerido')
      return
    }
    
    if (!formData.nombre_evento || formData.nombre_evento.trim() === '') {
      alert('⚠️ El nombre del evento es requerido')
      return
    }
    
    // Validar que haya al menos una línea con costo
    const totalCosto = calcularCostoTotal()
    if (totalCosto === 0) {
      alert('⚠️ Debe agregar al menos un costo al evento')
      return
    }
    
    // Validar que todas las líneas de costo tengan datos válidos
    for (const linea of lineasCosto) {
      if (['flor', 'contenedor', 'producto', 'producto_evento'].includes(linea.tipo) && !linea.item_id) {
        alert(`⚠️ La línea #${lineasCosto.indexOf(linea) + 1} necesita seleccionar un item del inventario`)
        return
      }
      if (!['flor', 'contenedor', 'producto', 'producto_evento'].includes(linea.tipo) && !linea.nombre) {
        alert(`⚠️ La línea #${lineasCosto.indexOf(linea) + 1} necesita una descripción`)
        return
      }
      const cantidad = Number(linea.cantidad) || 0
      const costoUnitario = Number(linea.costo_unitario) || 0
      if (cantidad <= 0) {
        alert(`⚠️ La línea #${lineasCosto.indexOf(linea) + 1} debe tener una cantidad mayor a 0`)
        return
      }
      if (costoUnitario < 0) {
        alert(`⚠️ La línea #${lineasCosto.indexOf(linea) + 1} debe tener un costo unitario válido`)
        return
      }
    }
    
    try {
      setLoadingFormulario(true)
      
      if (modoEdicion && eventoEditando) {
        // MODO EDICIÓN: Actualizar evento existente
        const costoTotal = calcularCostoTotal()
        const precioPropuesta = calcularPrecioPropuesta()
        
        const eventoPayload = {
          cliente_nombre: formData.cliente_nombre || '',
          cliente_telefono: formData.cliente_telefono || '',
          cliente_email: formData.cliente_email || '',
          nombre_evento: formData.nombre_evento || '',
          tipo_evento: formData.tipo_evento || 'Boda',
          fecha_evento: formData.fecha_evento || null,
          hora_evento: formData.hora_evento || '',
          lugar_evento: formData.lugar_evento || '',
          cantidad_personas: Number(formData.cantidad_personas) || 0,
          margen_porcentaje: Number(formData.margen_porcentaje) || 30,
          costo_total: costoTotal,
          precio_propuesta: precioPropuesta,
          notas_cotizacion: formData.notas_cotizacion || ''
        }
        
        // Actualizar evento
        const response = await axios.put(`${API_URL}/eventos/${eventoEditando.id}`, eventoPayload)
        
        if (response.data.success) {
          // Eliminar todos los insumos existentes
          if (eventoEditando.insumos && eventoEditando.insumos.length > 0) {
            for (const insumo of eventoEditando.insumos) {
              try {
                if (insumo.id) {
                  await axios.delete(`${API_URL}/eventos/${eventoEditando.id}/insumos/${insumo.id}`)
                }
              } catch (err) {
                console.error('Error eliminando insumo:', err)
                // Continuar aunque falle la eliminación de un insumo
              }
            }
          }
          
          // Agregar nuevos insumos
          const erroresInsumos = []
          for (let i = 0; i < lineasCosto.length; i++) {
            const linea = lineasCosto[i]
            
            if (!linea.tipo) {
              erroresInsumos.push(`Línea #${i + 1}: Falta el tipo de insumo`)
              continue
            }
            
            const insumoPayload = {
              tipo_insumo: linea.tipo,
              insumo_tipo: linea.tipo,
              cantidad: Number(linea.cantidad) || 1,
              costo_unitario: Number(linea.costo_unitario) || 0,
              notas: ''
            }
            
            if (linea.tipo === 'flor' && linea.item_id) {
              insumoPayload.flor_id = String(linea.item_id)
            } else if (linea.tipo === 'contenedor' && linea.item_id) {
              insumoPayload.contenedor_id = String(linea.item_id)
            } else if (linea.tipo === 'producto' && linea.item_id) {
              insumoPayload.producto_id = String(linea.item_id)
            } else if (linea.tipo === 'producto_evento' && linea.item_id) {
              const pe = productosEvento.find(p => p.codigo === linea.item_id)
              if (pe) {
                insumoPayload.producto_evento_id = pe.id
              } else {
                erroresInsumos.push(`Línea #${i + 1}: Producto evento no encontrado`)
                continue
              }
            } else if (!['flor', 'contenedor', 'producto', 'producto_evento'].includes(linea.tipo)) {
              insumoPayload.nombre_otro = linea.nombre || ''
            } else {
              erroresInsumos.push(`Línea #${i + 1}: Falta seleccionar item del inventario`)
              continue
            }
            
            try {
              await axios.post(`${API_URL}/eventos/${eventoEditando.id}/insumos`, insumoPayload)
            } catch (err) {
              const errorMsg = err.response?.data?.error || err.message || 'Error desconocido'
              erroresInsumos.push(`Línea #${i + 1} (${linea.tipo}): ${errorMsg}`)
            }
          }
          
          if (erroresInsumos.length > 0) {
            alert(`⚠️ Evento actualizado (${eventoEditando.id}) pero hubo errores al actualizar algunos insumos:\n\n${erroresInsumos.join('\n')}`)
          } else {
            alert(`✅ Evento actualizado exitosamente: ${eventoEditando.id}`)
          }
          
          setMostrarFormulario(false)
          setModoEdicion(false)
          setEventoEditando(null)
          resetForm()
          cargarEventos()
        }
      } else {
        // MODO CREACIÓN: Crear nuevo evento
        const eventoPayload = {
          cliente_nombre: formData.cliente_nombre || '',
          cliente_telefono: formData.cliente_telefono || '',
          cliente_email: formData.cliente_email || '',
          nombre_evento: formData.nombre_evento || '',
          tipo_evento: formData.tipo_evento || 'Boda',
          fecha_evento: formData.fecha_evento || null,
          hora_evento: formData.hora_evento || '',
          lugar_evento: formData.lugar_evento || '',
          cantidad_personas: Number(formData.cantidad_personas) || 0,
          margen_porcentaje: Number(formData.margen_porcentaje) || 30,
          costo_total: totalCosto,
          precio_propuesta: calcularPrecioPropuesta(),
          notas_cotizacion: formData.notas_cotizacion || ''
        }
        
        const response = await axios.post(`${API_URL}/eventos`, eventoPayload)
        
        if (response.data.success) {
          const eventoId = response.data.data.id
        
        // 2. Agregar cada línea de costo como insumo
        const erroresInsumos = []
        for (let i = 0; i < lineasCosto.length; i++) {
          const linea = lineasCosto[i]
          
          // Validar que el tipo esté presente
          if (!linea.tipo) {
            erroresInsumos.push(`Línea #${i + 1}: Falta el tipo de insumo`)
            continue
          }
          
          const insumoPayload = {
            tipo_insumo: linea.tipo,
            insumo_tipo: linea.tipo, // Enviar ambos para compatibilidad
            cantidad: Number(linea.cantidad) || 1,
            costo_unitario: Number(linea.costo_unitario) || 0,
            notas: ''
          }
          
          // Asignar referencia según tipo
          if (linea.tipo === 'flor' && linea.item_id) {
            insumoPayload.flor_id = String(linea.item_id)
          } else if (linea.tipo === 'contenedor' && linea.item_id) {
            insumoPayload.contenedor_id = String(linea.item_id)
          } else if (linea.tipo === 'producto' && linea.item_id) {
            insumoPayload.producto_id = String(linea.item_id)
          } else if (linea.tipo === 'producto_evento' && linea.item_id) {
            const pe = productosEvento.find(p => p.codigo === linea.item_id)
            if (pe) {
              insumoPayload.producto_evento_id = pe.id
            } else {
              erroresInsumos.push(`Línea #${i + 1}: Producto evento no encontrado`)
              continue
            }
          } else if (!['flor', 'contenedor', 'producto', 'producto_evento'].includes(linea.tipo)) {
            insumoPayload.nombre_otro = linea.nombre || ''
          } else {
            erroresInsumos.push(`Línea #${i + 1}: Falta seleccionar item del inventario`)
            continue
          }
          
          try {
            await axios.post(`${API_URL}/eventos/${eventoId}/insumos`, insumoPayload)
          } catch (err) {
            const errorMsg = err.response?.data?.error || err.message || 'Error desconocido'
            erroresInsumos.push(`Línea #${i + 1} (${linea.tipo}): ${errorMsg}`)
            console.error(`Error agregando insumo ${linea.tipo}:`, err)
          }
        }
        
        if (erroresInsumos.length > 0) {
          alert(`⚠️ Evento creado (${eventoId}) pero hubo errores al agregar algunos insumos:\n\n${erroresInsumos.join('\n')}`)
        }
        
        // Recargar el evento para obtener los costos recalculados
        const eventoActualizado = await axios.get(`${API_URL}/eventos/${eventoId}`)
        if (eventoActualizado.data.success) {
          alert(`✅ Evento creado: ${eventoId}\nCosto Total: $${(eventoActualizado.data.data.costo_total || 0).toLocaleString('es-CL')}\nPrecio Propuesta: $${(eventoActualizado.data.data.precio_propuesta || 0).toLocaleString('es-CL')}`)
        } else {
          alert(`✅ Evento creado: ${eventoId}`)
        }
        
          setMostrarFormulario(false)
          resetForm()
          cargarEventos()
        }
      }
    } catch (err) {
      console.error('Error al guardar evento:', err)
      const errorMessage = err.response?.data?.error || err.message || 'Error desconocido'
      alert(`❌ Error al guardar evento: ${errorMessage}\n\nPor favor, verifica que todos los campos requeridos estén completos.`)
    } finally {
      setLoadingFormulario(false)
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
    
    // Limpiar estados de cliente
    setClienteEncontrado(null)
    setSugerenciasClientes([])
    setMostrarSugerencias(false)
    setMostrarCrearCliente(false)
    
    // Limpiar modo edición
    setModoEdicion(false)
    setEventoEditando(null)
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
  
  const editarEvento = async (evento) => {
    try {
      // Cargar evento completo con insumos
      const response = await axios.get(`${API_URL}/eventos/${evento.id}`)
      if (response.data.success) {
        const eventoCompleto = response.data.data
        
        // Cargar insumos como líneas de costo
        const lineas = eventoCompleto.insumos.map(insumo => ({
          id: Date.now() + Math.random(),
          tipo: insumo.tipo_insumo || insumo.insumo_tipo,
          item_id: insumo.flor_id || insumo.contenedor_id || insumo.producto_id || insumo.producto_evento_id || null,
          nombre: insumo.nombre_otro || '',
          cantidad: insumo.cantidad || 1,
          costo_unitario: insumo.costo_unitario || 0
        }))
        
        // Si no hay insumos, agregar una línea por defecto
        if (lineas.length === 0) {
          lineas.push({
            id: Date.now(),
            tipo: 'mano_obra',
            item_id: null,
            nombre: '',
            cantidad: 1,
            costo_unitario: 0
          })
        }
        
        // Llenar formulario con datos del evento
        setFormData({
          cliente_nombre: eventoCompleto.cliente_nombre || '',
          cliente_telefono: eventoCompleto.cliente_telefono || '',
          cliente_email: eventoCompleto.cliente_email || '',
          nombre_evento: eventoCompleto.nombre_evento || '',
          tipo_evento: eventoCompleto.tipo_evento || 'Boda',
          fecha_evento: eventoCompleto.fecha_evento ? eventoCompleto.fecha_evento.split('T')[0] : '',
          hora_evento: eventoCompleto.hora_evento || '',
          lugar_evento: eventoCompleto.lugar_evento || '',
          cantidad_personas: eventoCompleto.cantidad_personas || 0,
          margen_porcentaje: eventoCompleto.margen_porcentaje || 30,
          notas_cotizacion: eventoCompleto.notas_cotizacion || ''
        })
        
        setLineasCosto(lineas)
        setEventoEditando(eventoCompleto)
        setModoEdicion(true)
        setMostrarFormulario(true)
      }
    } catch (err) {
      console.error('Error al cargar evento para editar:', err)
      alert('❌ Error al cargar el evento para editar')
    }
  }
  
  const confirmarEvento = async (eventoId) => {
    if (!confirm('¿Estás seguro de confirmar este evento? Esto cambiará su estado de "Cotización" a "Confirmado".')) {
      return
    }
    
    try {
      const response = await axios.put(`${API_URL}/eventos/${eventoId}/estado`, {
        estado: 'Confirmado'
      })
      
      if (response.data.success) {
        alert('✅ Evento confirmado exitosamente')
        cargarEventos()
      } else {
        alert('❌ Error al confirmar el evento: ' + (response.data.error || 'Error desconocido'))
      }
    } catch (err) {
      console.error('Error al confirmar evento:', err)
      alert('❌ Error al confirmar el evento: ' + (err.response?.data?.error || err.message))
    }
  }
  
  const eliminarEvento = async (eventoId, nombreEvento) => {
    if (!confirm(`¿Estás seguro de eliminar el evento "${nombreEvento}"?\n\nEsta acción NO se puede deshacer.`)) {
      return
    }
    
    // Segunda confirmación
    if (!confirm('⚠️ ÚLTIMA CONFIRMACIÓN\n\n¿Realmente deseas ELIMINAR este evento?\n\nTodos los insumos asociados también serán eliminados.')) {
      return
    }
    
    try {
      console.log('🗑️ Eliminando evento:', eventoId)
      const response = await axios.delete(`${API_URL}/eventos/${eventoId}`)
      console.log('📥 Respuesta del servidor:', response.data)
      
      if (response.data && response.data.success) {
        alert('✅ Evento eliminado exitosamente')
        // Cerrar modal de detalles si está abierto
        if (eventoSeleccionado && eventoSeleccionado.id === eventoId) {
          setEventoSeleccionado(null)
        }
        cargarEventos()
      } else {
        const errorMsg = response.data?.error || response.data?.message || 'Error desconocido'
        alert('❌ Error al eliminar el evento: ' + errorMsg)
      }
    } catch (err) {
      console.error('❌ Error completo al eliminar evento:', err)
      console.error('❌ Error response:', err.response)
      console.error('❌ Error data:', err.response?.data)
      console.error('❌ Error status:', err.response?.status)
      
      let errorMsg = 'Error desconocido'
      if (err.response) {
        // El servidor respondió con un código de error
        errorMsg = err.response.data?.error || err.response.data?.message || `Error ${err.response.status}: ${err.response.statusText}`
      } else if (err.request) {
        // La petición se hizo pero no hubo respuesta
        errorMsg = 'No se pudo conectar con el servidor. Verifica tu conexión.'
      } else {
        // Algo pasó al configurar la petición
        errorMsg = err.message || 'Error al configurar la petición'
      }
      
      alert(`❌ Error al eliminar el evento:\n\n${errorMsg}`)
    }
  }
  
  const renderSelectorItem = (linea) => {
    const tipo = linea.tipo
    
    if (tipo === 'flor') {
      return (
        <select
          value={linea.item_id || ''}
          onChange={(e) => actualizarLineaCosto(linea.id, 'item_id', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
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
        >
          <option value="">Seleccione un arreglo...</option>
          {productos.map(prod => (
            <option key={prod.id} value={String(prod.id)}>
              {prod.nombre} - ${(prod.costo_estimado || prod.precio_venta || prod.precio || 0).toLocaleString()}
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
          className="bg-primary-600 hover:bg-primary-700 text-white px-3 py-2 rounded-lg font-semibold flex items-center gap-2 shadow-lg hover:shadow-xl transition-all"
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
            className="bg-primary-600 hover:bg-primary-700 text-white px-3 py-2 rounded-lg font-semibold inline-flex items-center gap-2"
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
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Evento
                </th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Cliente
                </th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Fecha
                </th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Estado
                </th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Precio
                </th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
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
                    <div className="flex items-center gap-2">
                      <button
                        onClick={async () => {
                          // Cargar evento completo con insumos
                          try {
                            const response = await axios.get(`${API_URL}/eventos/${evento.id}`)
                            if (response.data.success) {
                              setEventoSeleccionado(response.data.data)
                            } else {
                              setEventoSeleccionado(evento)
                            }
                          } catch (err) {
                            console.error('Error al cargar evento:', err)
                            setEventoSeleccionado(evento)
                          }
                        }}
                        className="text-primary-600 hover:text-primary-900"
                      >
                        Ver Detalles
                      </button>
                      {evento.estado === 'Cotización' && (
                        <>
                          <button
                            onClick={() => editarEvento(evento)}
                            className="text-blue-600 hover:text-blue-900"
                            title="Editar evento"
                          >
                            <Edit2 className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => confirmarEvento(evento.id)}
                            className="text-green-600 hover:text-green-900"
                            title="Confirmar evento"
                          >
                            <CheckCircle className="h-4 w-4" />
                          </button>
                        </>
                      )}
                      <button
                        onClick={() => eliminarEvento(evento.id, evento.nombre_evento)}
                        className="text-red-600 hover:text-red-900"
                        title="Eliminar evento"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
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
              <h2 className="text-2xl font-bold text-gray-900">
                {modoEdicion ? `Editar Evento: ${eventoEditando?.id || ''}` : 'Nueva Cotización de Evento'}
              </h2>
              <button onClick={() => {
                setMostrarFormulario(false)
                resetForm()
              }} className="text-gray-400 hover:text-gray-600">
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
                  <div className="relative">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Nombre *</label>
                    <div className="relative">
                      <input
                        type="text"
                        value={formData.cliente_nombre}
                        onChange={(e) => {
                          const nombre = e.target.value
                          setFormData({...formData, cliente_nombre: nombre})
                          if (nombre.length >= 1) {
                            buscarClientesPorNombre(nombre)
                          } else {
                            setMostrarSugerencias(false)
                            setSugerenciasClientes([])
                            setClienteEncontrado(null)
                          }
                        }}
                        onFocus={() => {
                          if (formData.cliente_nombre.length >= 1) {
                            buscarClientesPorNombre(formData.cliente_nombre)
                          }
                        }}
                        onBlur={() => {
                          setTimeout(() => setMostrarSugerencias(false), 200)
                        }}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                        placeholder="Buscar o crear cliente..."
                      />
                      {buscandoCliente && (
                        <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-600"></div>
                        </div>
                      )}
                    </div>
                    
                    {/* Dropdown de sugerencias */}
                    {mostrarSugerencias && (
                      <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                        {sugerenciasClientes.length > 0 ? (
                          sugerenciasClientes.map(cliente => (
                            <div
                              key={cliente.id}
                              onMouseDown={(e) => {
                                e.preventDefault()
                                seleccionarCliente(cliente)
                              }}
                              className="px-3 py-2 hover:bg-gray-100 cursor-pointer border-b border-gray-100 last:border-b-0"
                            >
                              <div className="font-medium text-gray-900">{cliente.nombre}</div>
                              <div className="text-sm text-gray-500">
                                {cliente.telefono} {cliente.email ? `• ${cliente.email}` : ''}
                              </div>
                              <div className="text-xs text-gray-400 mt-1">
                                {cliente.tipo_cliente} {cliente.id ? `• ${cliente.id}` : ''}
                              </div>
                            </div>
                          ))
                        ) : (
                          <div className="px-3 py-2">
                            <p className="text-sm text-gray-600 mb-3">
                              No se encontró ningún cliente con ese nombre
                            </p>
                            <button
                              type="button"
                              onMouseDown={(e) => {
                                e.preventDefault()
                                e.stopPropagation()
                                setMostrarCrearCliente(true)
                                setMostrarSugerencias(false)
                              }}
                              className="w-full px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-lg hover:from-green-600 hover:to-emerald-600 font-medium flex items-center justify-center gap-2"
                            >
                              <Plus className="h-4 w-4" />
                              Crear nuevo cliente "{formData.cliente_nombre}"
                            </button>
                          </div>
                        )}
                      </div>
                    )}
                    
                    {/* Información del cliente encontrado */}
                    {clienteEncontrado && (
                      <div className="mt-2 p-2 bg-green-50 border border-green-200 rounded-lg">
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="text-sm font-medium text-green-900">
                              ✓ Cliente: {clienteEncontrado.nombre}
                            </div>
                            <div className="text-xs text-green-700">
                              {clienteEncontrado.tipo_cliente} • {clienteEncontrado.id}
                            </div>
                          </div>
                          <button
                            type="button"
                            onClick={() => {
                              setClienteEncontrado(null)
                              setFormData(prev => ({
                                ...prev,
                                cliente_nombre: '',
                                cliente_telefono: '',
                                cliente_email: ''
                              }))
                            }}
                            className="text-green-600 hover:text-green-800"
                          >
                            <X className="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Teléfono *</label>
                    <input
                      type="tel"
                      value={formData.cliente_telefono}
                      onChange={(e) => setFormData({...formData, cliente_telefono: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      disabled={!!clienteEncontrado}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                    <input
                      type="email"
                      value={formData.cliente_email}
                      onChange={(e) => setFormData({...formData, cliente_email: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      disabled={!!clienteEncontrado}
                    />
                  </div>
                  
                  {/* Modal para crear nuevo cliente */}
                  {mostrarCrearCliente && (
                    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                      <div className="bg-white rounded-lg shadow-xl w-full max-w-md" onClick={(e) => e.stopPropagation()}>
                        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
                          <h3 className="text-lg font-semibold text-gray-900">Crear Nuevo Cliente</h3>
                          <button
                            onClick={() => setMostrarCrearCliente(false)}
                            className="text-gray-400 hover:text-gray-600"
                          >
                            <X className="h-5 w-5" />
                          </button>
                        </div>
                        
                        <div className="p-6 space-y-4">
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Nombre *</label>
                            <input
                              type="text"
                              value={formData.cliente_nombre}
                              disabled
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
                            />
                          </div>
                          
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Teléfono *</label>
                            <input
                              type="tel"
                              value={formData.cliente_telefono}
                              disabled
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
                            />
                          </div>
                          
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                            <input
                              type="email"
                              value={formData.cliente_email}
                              disabled
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
                            />
                          </div>
                          
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Tipo de Cliente</label>
                            <select
                              value={nuevoClienteData.tipo_cliente}
                              onChange={(e) => setNuevoClienteData({...nuevoClienteData, tipo_cliente: e.target.value})}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                            >
                              <option value="Nuevo">Nuevo</option>
                              <option value="Ocasional">Ocasional</option>
                              <option value="Fiel">Fiel</option>
                              <option value="VIP">VIP</option>
                            </select>
                          </div>
                          
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Dirección Principal (opcional)</label>
                            <input
                              type="text"
                              value={nuevoClienteData.direccion_principal}
                              onChange={(e) => setNuevoClienteData({...nuevoClienteData, direccion_principal: e.target.value})}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                              placeholder="Dirección frecuente del cliente"
                            />
                          </div>
                          
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Notas (opcional)</label>
                            <textarea
                              value={nuevoClienteData.notas}
                              onChange={(e) => setNuevoClienteData({...nuevoClienteData, notas: e.target.value})}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                              rows="3"
                              placeholder="Información adicional del cliente"
                            />
                          </div>
                          
                          <div className="flex gap-3 pt-4">
                            <button
                              type="button"
                              onClick={() => setMostrarCrearCliente(false)}
                              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                            >
                              Cancelar
                            </button>
                            <button
                              type="button"
                              onClick={handleCrearNuevoCliente}
                              disabled={creandoCliente}
                              className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                              {creandoCliente ? 'Creando...' : 'Crear Cliente'}
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
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
                      value={formData.nombre_evento}
                      onChange={(e) => setFormData({...formData, nombre_evento: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      placeholder="Ej: Boda María & Juan"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Tipo de Evento *</label>
                    <select
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
                      type="text"
                      value={formData.cantidad_personas}
                      onChange={(e) => {
                        const valor = e.target.value === '' ? '' : (parseInt(e.target.value) || 0)
                        setFormData({...formData, cantidad_personas: valor})
                      }}
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
                            type="text"
                            value={linea.cantidad}
                            onChange={(e) => {
                              const valor = e.target.value
                              actualizarLineaCosto(linea.id, 'cantidad', valor)
                            }}
                            onBlur={(e) => {
                              // Al perder el foco, asegurar que sea un número válido
                              const valor = e.target.value === '' ? 1 : (parseInt(e.target.value) || 1)
                              actualizarLineaCosto(linea.id, 'cantidad', valor)
                            }}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 text-sm"
                          />
                        </div>
                        
                        <div className="col-span-6 md:col-span-2">
                          <label className="block text-xs font-medium text-gray-700 mb-1">Costo Unit. *</label>
                          <input
                            type="text"
                            value={linea.costo_unitario}
                            onChange={(e) => {
                              const valor = e.target.value
                              actualizarLineaCosto(linea.id, 'costo_unitario', valor)
                            }}
                            onBlur={(e) => {
                              // Al perder el foco, asegurar que sea un número válido
                              const valor = e.target.value === '' ? 0 : (parseFloat(e.target.value) || 0)
                              actualizarLineaCosto(linea.id, 'costo_unitario', valor)
                            }}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 text-sm"
                            disabled={['flor', 'contenedor', 'producto', 'producto_evento'].includes(linea.tipo) && linea.item_id}
                          />
                        </div>
                        
                        <div className="col-span-10 md:col-span-2 flex items-center">
                          <div className="w-full">
                            <label className="block text-xs font-medium text-gray-700 mb-1">Total</label>
                            <div className="text-sm font-bold text-gray-900 px-3 py-2 bg-white rounded-lg border border-gray-300">
                              ${((Number(linea.cantidad) || 0) * (Number(linea.costo_unitario) || 0)).toLocaleString('es-CL', {minimumFractionDigits: 0, maximumFractionDigits: 0})}
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
                        type="text"
                        value={formData.margen_porcentaje}
                        onChange={(e) => {
                          const valor = e.target.value === '' ? '' : (parseFloat(e.target.value) || 30)
                          setFormData({...formData, margen_porcentaje: valor})
                        }}
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
                  className="flex-1 px-3 py-2 border border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 transition-colors"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="flex-1 px-3 py-2 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 transition-colors"
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
              
              {/* Desglose de Insumos */}
              {eventoSeleccionado.insumos && eventoSeleccionado.insumos.length > 0 && (
                <div className="bg-white rounded-lg p-4 border-2 border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                    <Package className="h-5 w-5 text-primary-600" />
                    Desglose de Insumos
                  </h3>
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tipo</th>
                          <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Descripción</th>
                          <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Cantidad</th>
                          <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Costo Unit.</th>
                          <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Total</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {eventoSeleccionado.insumos.map((insumo, index) => {
                          const tipo = insumo.tipo_insumo || insumo.insumo_tipo || 'otro'
                          let descripcion = insumo.nombre_otro || ''
                          
                          // Obtener descripción según tipo
                          if (tipo === 'flor' && insumo.flor_id) {
                            const flor = flores.find(f => f.id === insumo.flor_id)
                            descripcion = flor ? `${flor.nombre} - ${flor.color}` : `Flor ID: ${insumo.flor_id}`
                          } else if (tipo === 'contenedor' && insumo.contenedor_id) {
                            const contenedor = contenedores.find(c => c.id === insumo.contenedor_id)
                            descripcion = contenedor ? contenedor.nombre : `Contenedor ID: ${insumo.contenedor_id}`
                          } else if (tipo === 'producto' && insumo.producto_id) {
                            const producto = productos.find(p => p.id === insumo.producto_id)
                            descripcion = producto ? producto.nombre : `Producto ID: ${insumo.producto_id}`
                          } else if (tipo === 'producto_evento' && insumo.producto_evento_id) {
                            const pe = productosEvento.find(p => p.id === insumo.producto_evento_id)
                            descripcion = pe ? pe.nombre : `Producto Evento ID: ${insumo.producto_evento_id}`
                          }
                          
                          const total = (insumo.cantidad || 0) * (insumo.costo_unitario || 0)
                          
                          return (
                            <tr key={insumo.id || index} className="hover:bg-gray-50">
                              <td className="px-3 py-2 whitespace-nowrap">
                                <span className="text-sm text-gray-900 capitalize">{tipo.replace('_', ' ')}</span>
                              </td>
                              <td className="px-3 py-2">
                                <span className="text-sm text-gray-900">{descripcion || '-'}</span>
                              </td>
                              <td className="px-3 py-2 whitespace-nowrap text-right">
                                <span className="text-sm text-gray-900">{insumo.cantidad || 0}</span>
                              </td>
                              <td className="px-3 py-2 whitespace-nowrap text-right">
                                <span className="text-sm text-gray-900">${(insumo.costo_unitario || 0).toLocaleString('es-CL')}</span>
                              </td>
                              <td className="px-3 py-2 whitespace-nowrap text-right">
                                <span className="text-sm font-semibold text-gray-900">${total.toLocaleString('es-CL')}</span>
                              </td>
                            </tr>
                          )
                        })}
                        <tr className="bg-gray-50 font-semibold">
                          <td colSpan="4" className="px-3 py-2 text-right text-sm text-gray-700">
                            TOTAL COSTO INSUMOS:
                          </td>
                          <td className="px-3 py-2 text-right text-lg font-bold text-gray-900">
                            ${(eventoSeleccionado.costo_total || 0).toLocaleString('es-CL')}
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
              
              {/* Costos y Financiero */}
              <div className="bg-primary-50 rounded-lg p-4 border-2 border-primary-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <DollarSign className="h-5 w-5 text-primary-600" />
                  Información Financiera
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">Costo Total</p>
                    <p className="text-xl font-bold text-gray-900">
                      ${(eventoSeleccionado.costo_total || 0).toLocaleString('es-CL')}
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

