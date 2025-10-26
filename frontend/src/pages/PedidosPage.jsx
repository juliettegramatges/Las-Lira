import { useState, useEffect, useMemo } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import axios from 'axios'
import { Search, Filter, Plus, Edit, MapPin, Package, DollarSign, Calendar, User, MessageSquare, X, CheckCircle, Download, ShoppingBag, Palette, Ruler, Image as ImageIcon, Phone, Mail, Trash2, XCircle } from 'lucide-react'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import SelectorInsumosColores from '../components/Pedidos/SelectorInsumosColores'

const API_URL = 'http://localhost:5001/api'

// Colores comunes para personalización
const COLORES_DISPONIBLES = [
  'Blanco', 'Rojo', 'Rosado', 'Fucsia', 'Naranja', 'Amarillo',
  'Verde', 'Azul', 'Morado', 'Lila', 'Celeste', 'Durazno',
  'Salmón', 'Coral', 'Burdeo', 'Mixto', 'Pastel', 'Vibrantes'
]

// Motivos comunes de pedidos
const MOTIVOS_PEDIDO = [
  // Celebraciones personales
  'Cumpleaños',
  'Aniversario',
  'Graduación',
  'Primera Comunión',
  'Bautizo',
  'Confirmación',
  
  // Amor y romance
  'San Valentín',
  'Amor / Cariño',
  'Pedida de Mano',
  'Boda / Matrimonio',
  'Aniversario de Matrimonio',
  
  // Días especiales
  'Día de la Madre',
  'Día del Padre',
  'Día de la Mujer',
  'Día del Profesor',
  'Día de los Abuelos',
  
  // Nacimientos y bebés
  'Nacimiento',
  'Baby Shower',
  'Recién Nacido',
  
  // Felicitaciones
  'Felicitaciones',
  'Éxito / Logro',
  'Nuevo Trabajo',
  'Nuevo Hogar',
  'Jubilación',
  
  // Recuperación y ánimo
  'Mejórate Pronto',
  'Recuperación',
  'Apoyo',
  
  // Agradecimiento
  'Agradecimiento',
  'Disculpas',
  
  // Ceremonial
  'Difunto',
  'Condolencias',
  'Funeral',
  'Velorio',
  'Misa',
  
  // Fechas especiales
  'Navidad',
  'Año Nuevo',
  'Fiestas Patrias',
  'Pascua',
  'Día de la Independencia',
  
  // Otros
  'Decoración',
  'Evento Corporativo',
  'Regalo Corporativo',
  'Solo porque sí',
  'Sin motivo específico',
  'Otro'
]

function PedidosPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const [pedidos, setPedidos] = useState([])
  const [loading, setLoading] = useState(true)
  const [busqueda, setBusqueda] = useState('')
  const [filtroEstado, setFiltroEstado] = useState('')
  const [filtroCanal, setFiltroCanal] = useState('')
  const [pedidoDetalle, setPedidoDetalle] = useState(null)
  const [clienteDetalle, setClienteDetalle] = useState(null)
  const [historialCliente, setHistorialCliente] = useState([])
  const [loadingCliente, setLoadingCliente] = useState(false)
  const [modoEdicion, setModoEdicion] = useState(false)
  const [pedidoEditado, setPedidoEditado] = useState(null)
  
  // Estados de paginación
  const [paginaActual, setPaginaActual] = useState(1)
  const [totalPaginas, setTotalPaginas] = useState(1)
  const [totalPedidos, setTotalPedidos] = useState(0)
  const [limitePorPagina] = useState(100)
  const [mostrarFormulario, setMostrarFormulario] = useState(false)
  const [productos, setProductos] = useState([])
  const [comunas, setComunas] = useState([])
  const [loadingFormulario, setLoadingFormulario] = useState(false)
  const [clienteEncontrado, setClienteEncontrado] = useState(null)
  const [buscandoCliente, setBuscandoCliente] = useState(false)
  
  // Estados para personalización
  const [esPersonalizacion, setEsPersonalizacion] = useState(false)
  const [datosPersonalizacion, setDatosPersonalizacion] = useState({
    producto_shopify_referencia: ''
  })
  const [plazoPagoManual, setPlazoPagoManual] = useState(false)
  const [sugerenciasClientes, setSugerenciasClientes] = useState([])
  const [mostrarSugerencias, setMostrarSugerencias] = useState(false)
  const [historialPedidos, setHistorialPedidos] = useState([])
  const [cargandoHistorial, setCargandoHistorial] = useState(false)
  
  // Estados para insumos
  const [receta, setReceta] = useState([])
  const [insumosModificados, setInsumosModificados] = useState([])
  const [loadingReceta, setLoadingReceta] = useState(false)
  const [flores, setFlores] = useState([])
  const [contenedores, setContenedores] = useState([])
  
  // Estados para selector de insumos por color
  const [insumosSeleccionados, setInsumosSeleccionados] = useState(null)
  const [costoCalculado, setCostoCalculado] = useState(null)
  
  // Estado del formulario
  const [formData, setFormData] = useState({
    canal: 'WhatsApp',
    shopify_order_number: '',
    cliente_id: '',
    cliente_nombre: '',
    cliente_telefono: '',
    cliente_email: '',
    arreglo_pedido: '',
    producto_id: '',
    detalles_adicionales: '',
    precio_ramo: '',
    precio_envio: '',
    lleva_mensaje: false,
    destinatario: '',
    mensaje: '',
    firma: '',
    direccion_entrega: '',
    comuna: '',
    motivo: '',
    fecha_entrega: '',
    plazo_pago_dias: 0
  })
  
  const cargarPedidos = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (filtroEstado) params.append('estado', filtroEstado)
      if (filtroCanal) params.append('canal', filtroCanal)
      params.append('page', paginaActual)
      params.append('limit', limitePorPagina)
      
      const response = await axios.get(`${API_URL}/pedidos?${params}`)
      if (response.data.success) {
        setPedidos(response.data.data)
        setTotalPedidos(response.data.total)
        setTotalPaginas(response.data.total_pages)
      }
    } catch (err) {
      console.error('Error al cargar pedidos:', err)
      alert('❌ No se pudo conectar con el servidor')
    } finally {
      setLoading(false)
    }
  }
  
  const cargarInfoCliente = async (clienteId) => {
    if (!clienteId) return
    
    try {
      setLoadingCliente(true)
      // Cargar información del cliente y su historial en paralelo
      const [clienteRes, historialRes] = await Promise.all([
        axios.get(`${API_URL}/clientes/${clienteId}`),
        axios.get(`${API_URL}/clientes/${clienteId}/pedidos`)
      ])
      
      if (clienteRes.data.success) {
        setClienteDetalle(clienteRes.data.data)
      }
      
      if (historialRes.data.success) {
        setHistorialCliente(historialRes.data.data.pedidos || [])
      }
    } catch (error) {
      console.error('Error al cargar información del cliente:', error)
    } finally {
      setLoadingCliente(false)
    }
  }
  
  const handleAbrirPedido = (pedido) => {
    setPedidoDetalle(pedido)
    setPedidoEditado({...pedido})
    setModoEdicion(true) // Abrir directamente en modo edición
    setClienteDetalle(null)
    setHistorialCliente([])
    
    // Cargar información del cliente si tiene ID
    if (pedido.cliente_id) {
      cargarInfoCliente(pedido.cliente_id)
    }
  }
  
  const handleActivarEdicion = () => {
    setModoEdicion(true)
    setPedidoEditado({...pedidoDetalle})
  }
  
  const handleCancelarEdicion = () => {
    setModoEdicion(false)
    setPedidoEditado({...pedidoDetalle})
  }
  
  const handleCampoEdicion = (campo, valor) => {
    setPedidoEditado(prev => ({
      ...prev,
      [campo]: valor
    }))
  }
  
  const handleGuardarEdicion = async () => {
    try {
      const response = await axios.put(`${API_URL}/pedidos/${pedidoDetalle.id}`, pedidoEditado)
      
      if (response.data.success) {
        alert('✅ Pedido actualizado correctamente')
        setPedidoDetalle(response.data.data)
        setPedidoEditado(response.data.data)
        setModoEdicion(false)
        
        // Recargar la lista de pedidos
        cargarPedidos()
      }
    } catch (error) {
      console.error('Error al guardar pedido:', error)
      alert('❌ Error al guardar los cambios')
    }
  }
  
  const handleCancelarPedido = async () => {
    if (!confirm('⚠️ ¿Estás seguro de cancelar este pedido? Se cambiará su estado a "Cancelado".')) {
      return
    }
    
    try {
      const response = await axios.patch(`${API_URL}/pedidos/${pedidoDetalle.id}/cancelar`)
      
      if (response.data.success) {
        alert('✅ Pedido cancelado correctamente')
        setPedidoDetalle(null)
        cargarPedidos()
      }
    } catch (error) {
      console.error('Error al cancelar pedido:', error)
      alert('❌ Error al cancelar el pedido')
    }
  }
  
  const handleEliminarPedido = async () => {
    if (!confirm('🗑️ ¿CONFIRMAS ELIMINAR PERMANENTEMENTE este pedido?\n\nEsta acción NO se puede deshacer.\nEl pedido será borrado de la base de datos.')) {
      return
    }
    
    // Segunda confirmación para mayor seguridad
    if (!confirm('⚠️ ÚLTIMA CONFIRMACIÓN\n\n¿Realmente deseas ELIMINAR PERMANENTEMENTE este pedido?\n\nEscribe "ELIMINAR" para confirmar o cancela.')) {
      return
    }
    
    try {
      const response = await axios.delete(`${API_URL}/pedidos/${pedidoDetalle.id}`)
      
      if (response.data.success) {
        alert('✅ Pedido eliminado permanentemente')
        setPedidoDetalle(null)
        cargarPedidos()
      }
    } catch (error) {
      console.error('Error al eliminar pedido:', error)
      alert('❌ Error al eliminar el pedido')
    }
  }
  
  const cargarDatosFormulario = async () => {
    try {
      // Cargar productos
      const prodResponse = await axios.get(`${API_URL}/productos`)
      if (prodResponse.data.success) {
        setProductos(prodResponse.data.data)
      }
      
      // Cargar flores
      const floresResponse = await axios.get(`${API_URL}/inventario/flores`)
      if (floresResponse.data.success) {
        setFlores(floresResponse.data.data)
      }
      
      // Cargar contenedores
      const contResponse = await axios.get(`${API_URL}/inventario/contenedores`)
      if (contResponse.data.success) {
        setContenedores(contResponse.data.data)
      }
      
      // Cargar comunas
      const comunasResponse = await axios.get(`${API_URL}/rutas/comunas`)
      if (comunasResponse.data.success) {
        setComunas(comunasResponse.data.data)
      }
    } catch (err) {
      console.error('Error al cargar datos del formulario:', err)
    }
  }
  
  const handleComunaChange = (comunaNombre) => {
    const comunaData = comunas.find(c => c.comuna === comunaNombre)
    setFormData(prev => ({
      ...prev,
      comuna: comunaNombre,
      precio_envio: comunaData?.precio || prev.precio_envio
    }))
  }
  
  const handleProductoChange = async (productoId) => {
    const productoSeleccionado = productos.find(p => p.id === productoId)
    
    // Detectar si es una personalización
    const esProductoPersonalizado = productoSeleccionado?.nombre?.toLowerCase().includes('personaliz')
    setEsPersonalizacion(esProductoPersonalizado)
    
    setFormData(prev => ({
      ...prev,
      producto_id: productoId,
      arreglo_pedido: productoSeleccionado?.nombre || prev.arreglo_pedido,
      precio_ramo: productoSeleccionado?.precio_venta || prev.precio_ramo
    }))
    
    // Cargar recetario del producto
    if (productoId) {
      try {
        setLoadingReceta(true)
        const response = await axios.get(`${API_URL}/productos/${productoId}/receta`)
        
        // El backend devuelve: { success: true, data: { receta: [...] } }
        const recetaData = response.data?.data?.receta || response.data?.receta || []
        
        if (response.data.success && Array.isArray(recetaData) && recetaData.length > 0) {
          // Convertir receta a formato editable para insumos
          const insumosIniciales = recetaData.map(item => ({
            insumo_tipo: item.tipo === 'Flor' || item.tipo_insumo === 'Flor' ? 'Flor' : 'Contenedor',
            insumo_id: item.insumo_id,
            insumo_nombre: item.nombre || item.insumo_nombre || 'Sin nombre',
            insumo_color: item.color || '',
            insumo_foto: item.foto_url || null,
            cantidad: item.cantidad || 1,
            costo_unitario: item.costo_unitario || 0,
            stock_disponible: item.stock_disponible || 0
          }))
          setReceta(insumosIniciales)
          setInsumosModificados(JSON.parse(JSON.stringify(insumosIniciales))) // Copia profunda
        } else {
          // Producto sin receta o respuesta vacía
          setReceta([])
          setInsumosModificados([])
        }
      } catch (err) {
        console.error('Error al cargar recetario:', err)
        // En caso de error, limpiar los insumos
        setReceta([])
        setInsumosModificados([])
      } finally {
        setLoadingReceta(false)
      }
    } else {
      setReceta([])
      setInsumosModificados([])
    }
  }
  
  const handleInsumosChange = (insumos) => {
    setInsumosSeleccionados(insumos)
  }
  
  const handleCostoChange = (costo) => {
    setCostoCalculado(costo)
    // Auto-actualizar el precio del ramo con el costo calculado
    if (costo && costo.total > 0) {
      setFormData(prev => ({
        ...prev,
        precio_ramo: Math.ceil(costo.total * 1.5) // Margen sugerido del 50%
      }))
    }
  }
  
  // Función para personalización
  const handlePersonalizacionChange = (campo, valor) => {
    setDatosPersonalizacion(prev => ({
      ...prev,
      [campo]: valor
    }))
  }
  
  const handleCerrarFormulario = () => {
    setMostrarFormulario(false)
    setClienteEncontrado(null)
    setPlazoPagoManual(false)
    setSugerenciasClientes([])
    setMostrarSugerencias(false)
    setHistorialPedidos([])
    setCargandoHistorial(false)
    setReceta([])
    setInsumosModificados([])
    setInsumosSeleccionados(null)
    setCostoCalculado(null)
    setEsPersonalizacion(false)
    setDatosPersonalizacion({
      producto_shopify_referencia: ''
    })
    setFormData({
      canal: 'WhatsApp',
      shopify_order_number: '',
      cliente_id: '',
      cliente_nombre: '',
      cliente_telefono: '',
      cliente_email: '',
      arreglo_pedido: '',
      producto_id: '',
      detalles_adicionales: '',
      precio_ramo: '',
      precio_envio: '',
      lleva_mensaje: false,
      destinatario: '',
      mensaje: '',
      firma: '',
      direccion_entrega: '',
      comuna: '',
      motivo: '',
      fecha_entrega: '',
      plazo_pago_dias: 0
    })
  }
  
  // Plazos de pago según tipo de cliente
  const PLAZOS_PAGO = {
    'Nuevo': 0,
    'Fiel': 15,
    'Cumplidor': 30,
    'No Cumplidor': 0,
    'VIP': 45,
    'Ocasional': 7
  }
  
  // Buscar clientes por nombre
  const buscarClientesPorNombre = async (nombre) => {
    if (!nombre || nombre.length < 2) {
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
        console.log(`🔍 Encontrados ${response.data.clientes.length} clientes`)
      } else {
        setSugerenciasClientes([])
        setMostrarSugerencias(false)
        console.log('ℹ️ No se encontraron clientes')
      }
    } catch (err) {
      console.error('Error al buscar clientes:', err)
      setSugerenciasClientes([])
    } finally {
      setBuscandoCliente(false)
    }
  }
  
  const cargarHistorialPedidos = async (clienteId) => {
    try {
      setCargandoHistorial(true)
      const response = await axios.get(`${API_URL}/clientes/${clienteId}/pedidos`)
      if (response.data.success) {
        setHistorialPedidos(response.data.data.pedidos)
      }
    } catch (err) {
      console.error('Error al cargar historial de pedidos:', err)
      setHistorialPedidos([])
    } finally {
      setCargandoHistorial(false)
    }
  }

  const seleccionarCliente = (cliente) => {
    console.log('✅ Cliente seleccionado:', cliente.nombre, `(${cliente.tipo_cliente})`)
    
    setClienteEncontrado(cliente)
    setMostrarSugerencias(false)
    setSugerenciasClientes([])
    
    // Cargar historial de pedidos del cliente
    cargarHistorialPedidos(cliente.id)
    
    // Autocompletar TODOS los datos del cliente
    setFormData(prev => ({
      ...prev,
      cliente_id: cliente.id,
      cliente_nombre: cliente.nombre,
      cliente_telefono: cliente.telefono,
      cliente_email: cliente.email || '',
      direccion_entrega: cliente.direccion_principal || prev.direccion_entrega
    }))
    
    // Calcular plazo de pago automático si no es manual
    if (!plazoPagoManual) {
      const plazo = PLAZOS_PAGO[cliente.tipo_cliente] || 0
      setFormData(prev => ({
        ...prev,
        plazo_pago_dias: plazo
      }))
    }
  }
  
  const handleNombreChange = (nombre) => {
    setFormData(prev => ({ ...prev, cliente_nombre: nombre }))
    
    // Limpiar cliente seleccionado si empieza a escribir de nuevo
    if (clienteEncontrado) {
      setClienteEncontrado(null)
      setHistorialPedidos([])
      setFormData(prev => ({
        ...prev,
        cliente_id: '',
        cliente_telefono: '',
        cliente_email: '',
        plazo_pago_dias: 0
      }))
    }
    
    // Buscar clientes mientras escribe
    if (nombre.length >= 2) {
      // Cancelar búsqueda anterior si existe
      if (window.busquedaClienteTimeout) {
        clearTimeout(window.busquedaClienteTimeout)
      }
      
      // Buscar después de 300ms
      window.busquedaClienteTimeout = setTimeout(() => {
        buscarClientesPorNombre(nombre)
      }, 300)
    } else {
      setSugerenciasClientes([])
      setMostrarSugerencias(false)
    }
  }
  
  // Funciones para modificar insumos
  const handleCantidadInsumo = (index, nuevaCantidad) => {
    const nuevosInsumos = [...insumosModificados]
    nuevosInsumos[index].cantidad = parseInt(nuevaCantidad) || 0
    setInsumosModificados(nuevosInsumos)
  }
  
  const handleCambiarInsumo = (index, nuevoInsumoId, tipo) => {
    const nuevosInsumos = [...insumosModificados]
    
    if (tipo === 'Flor') {
      const florSeleccionada = flores.find(f => f.id === nuevoInsumoId)
      if (florSeleccionada) {
        nuevosInsumos[index] = {
          ...nuevosInsumos[index],
          insumo_id: florSeleccionada.id,
          insumo_nombre: florSeleccionada.tipo,
          insumo_color: florSeleccionada.color,
          insumo_foto: florSeleccionada.foto_url,
          costo_unitario: florSeleccionada.costo_unitario,
          stock_disponible: florSeleccionada.cantidad_disponible
        }
      }
    } else if (tipo === 'Contenedor') {
      const contenedorSeleccionado = contenedores.find(c => c.id === nuevoInsumoId)
      if (contenedorSeleccionado) {
        nuevosInsumos[index] = {
          ...nuevosInsumos[index],
          insumo_id: contenedorSeleccionado.id,
          insumo_nombre: contenedorSeleccionado.tipo,
          insumo_color: contenedorSeleccionado.material,
          insumo_foto: contenedorSeleccionado.foto_url,
          costo_unitario: contenedorSeleccionado.costo_unitario,
          stock_disponible: contenedorSeleccionado.cantidad_disponible
        }
      }
    }
    
    setInsumosModificados(nuevosInsumos)
  }
  
  const handleEliminarInsumo = (index) => {
    const nuevosInsumos = insumosModificados.filter((_, i) => i !== index)
    setInsumosModificados(nuevosInsumos)
  }
  
  const handleAgregarInsumo = (tipo) => {
    const nuevoInsumo = {
      insumo_tipo: tipo,
      insumo_id: '',
      insumo_nombre: '',
      insumo_color: '',
      insumo_foto: '',
      cantidad: 1,
      costo_unitario: 0,
      stock_disponible: 0
    }
    setInsumosModificados([...insumosModificados, nuevoInsumo])
  }
  
  const handleSubmitPedido = async (e) => {
    e.preventDefault()
    
    // Validaciones
    if (!formData.cliente_nombre || !formData.cliente_telefono) {
      alert('❌ Nombre y teléfono del cliente son obligatorios')
      return
    }
    
    if (!formData.fecha_entrega) {
      alert('❌ La fecha de entrega es obligatoria')
      return
    }
    
    if (!formData.direccion_entrega) {
      alert('❌ La dirección de entrega es obligatoria')
      return
    }
    
    const precioRamo = parseFloat(formData.precio_ramo) || 0
    const precioEnvio = parseFloat(formData.precio_envio) || 0
    
    if (precioRamo <= 0) {
      alert('❌ El precio del ramo debe ser mayor a 0')
      return
    }
    
    try {
      setLoadingFormulario(true)
      
      // Construir detalles adicionales incluyendo datos de personalización
      let detallesCompletos = formData.detalles_adicionales || ''
      
      if (esPersonalizacion && datosPersonalizacion.producto_shopify_referencia) {
        const refShopify = `🛍️ Ref Shopify: ${datosPersonalizacion.producto_shopify_referencia}`
        detallesCompletos = detallesCompletos 
          ? `${detallesCompletos}\n\n${refShopify}`
          : refShopify
      }
      
      const pedidoData = {
        canal: formData.canal,
        shopify_order_number: formData.shopify_order_number || null,
        cliente_nombre: formData.cliente_nombre,
        cliente_telefono: formData.cliente_telefono,
        cliente_email: formData.cliente_email || null,
        arreglo_pedido: formData.arreglo_pedido || null,
        producto_id: formData.producto_id || null,
        detalles_adicionales: detallesCompletos || null,
        precio_ramo: precioRamo,
        precio_envio: precioEnvio,
        precio_total: precioRamo + precioEnvio,
        destinatario: formData.destinatario || null,
        mensaje: formData.mensaje || null,
        firma: formData.firma || null,
        direccion_entrega: formData.direccion_entrega,
        comuna: formData.comuna || null,
        motivo: formData.motivo || null,
        fecha_entrega: new Date(formData.fecha_entrega).toISOString()
      }
      
      const response = await axios.post(`${API_URL}/pedidos`, pedidoData)
      
      if (response.data.success) {
        const nuevoPedidoId = response.data.data.id
        
        // Si hay insumos seleccionados (nueva estructura por color), guardarlos
        if (insumosSeleccionados && (insumosSeleccionados.flores?.length > 0 || insumosSeleccionados.contenedor)) {
          try {
            await axios.post(`${API_URL}/pedidos/${nuevoPedidoId}/insumos-detallados`, insumosSeleccionados)
          } catch (insumosErr) {
            console.error('Error al guardar insumos:', insumosErr)
            alert('⚠️ Pedido creado pero error al guardar insumos: ' + (insumosErr.response?.data?.error || insumosErr.message))
          }
        }
        // Si hay insumos modificados (estructura antigua), guardarlos también
        else if (insumosModificados.length > 0) {
          try {
            await axios.post(`${API_URL}/pedidos/${nuevoPedidoId}/insumos`, {
              insumos: insumosModificados
            })
          } catch (insumosErr) {
            console.error('Error al guardar insumos:', insumosErr)
            alert('⚠️ Pedido creado pero error al guardar insumos: ' + (insumosErr.response?.data?.error || insumosErr.message))
          }
        }
        
        alert('✅ Pedido creado exitosamente: ' + nuevoPedidoId)
        handleCerrarFormulario()
        cargarPedidos()
      }
    } catch (err) {
      console.error('Error al crear pedido:', err)
      alert('❌ Error al crear pedido: ' + (err.response?.data?.error || err.message))
    } finally {
      setLoadingFormulario(false)
    }
  }
  
  // Filtrar pedidos por búsqueda
  const pedidosFiltrados = useMemo(() => {
    if (!busqueda.trim()) return pedidos
    
    const termino = busqueda.toLowerCase().trim()
    
    return pedidos.filter(pedido => {
      // Buscar por ID de pedido
      if (pedido.id?.toLowerCase().includes(termino)) return true
      
      // Buscar por número de Shopify
      if (pedido.shopify_order_number?.toLowerCase().includes(termino)) return true
      
      // Buscar por nombre de cliente
      if (pedido.cliente_nombre?.toLowerCase().includes(termino)) return true
      
      // Buscar por teléfono
      if (pedido.cliente_telefono?.toLowerCase().includes(termino)) return true
      
      // Buscar por tipo de arreglo
      if (pedido.arreglo_pedido?.toLowerCase().includes(termino)) return true
      
      // Buscar por comuna
      if (pedido.comuna?.toLowerCase().includes(termino)) return true
      
      // Buscar por dirección
      if (pedido.direccion_entrega?.toLowerCase().includes(termino)) return true
      
      // Buscar por destinatario
      if (pedido.destinatario?.toLowerCase().includes(termino)) return true
      
      // Buscar por motivo
      if (pedido.motivo?.toLowerCase().includes(termino)) return true
      
      return false
    })
  }, [pedidos, busqueda])
  
  useEffect(() => {
    cargarPedidos()
  }, [filtroEstado, filtroCanal, paginaActual])
  
  useEffect(() => {
    cargarDatosFormulario()
  }, [])
  
  // Detectar si se navega desde el tablero con un pedido a abrir
  useEffect(() => {
    if (location.state?.pedidoAAbrir) {
      handleAbrirPedido(location.state.pedidoAAbrir)
      // Limpiar el state para que no se abra de nuevo si recarga
      navigate(location.pathname, { replace: true, state: {} })
    }
  }, [location.state])
  
  const estadoColor = {
    'Pedido': 'bg-blue-100 text-blue-800',
    'Pedidos Semana': 'bg-indigo-100 text-indigo-800',
    'Entregas para Mañana': 'bg-orange-100 text-orange-800',
    'Entregas de Hoy': 'bg-red-100 text-red-800',
    'En Proceso': 'bg-yellow-100 text-yellow-800',
    'Listo para Despacho': 'bg-green-100 text-green-800',
    'Despachados': 'bg-purple-100 text-purple-800',
    'Archivado': 'bg-gray-100 text-gray-800',
    'Cancelado': 'bg-red-200 text-red-900',
  }
  
  const formatFecha = (fechaStr) => {
    try {
      const fecha = new Date(fechaStr)
      return format(fecha, "dd/MM/yyyy HH:mm", { locale: es })
    } catch {
      return fechaStr
    }
  }
  
  // Calcular total en tiempo real
  const totalPedido = useMemo(() => {
    const precioRamo = parseFloat(formData.precio_ramo) || 0
    const precioEnvio = parseFloat(formData.precio_envio) || 0
    return precioRamo + precioEnvio
  }, [formData.precio_ramo, formData.precio_envio])
  
  return (
    <div className="px-4 sm:px-0">
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Pedidos</h1>
          <p className="mt-1 text-sm text-gray-600">
            {totalPedidos.toLocaleString()} pedidos en total • Página {paginaActual} de {totalPaginas}
          </p>
        </div>
        <div className="flex gap-3">
          <button 
            onClick={() => {
              window.open(`${API_URL}/exportar/pedidos`, '_blank')
            }}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center"
          >
            <Download className="h-5 w-5 mr-2" />
            Descargar Excel
          </button>
          <button 
            onClick={() => setMostrarFormulario(true)}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 flex items-center"
          >
            <Plus className="h-5 w-5 mr-2" />
            Nuevo Pedido
          </button>
        </div>
      </div>
      
      {/* Barra de búsqueda */}
      <div className="mb-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
            placeholder="Buscar por ID, cliente, teléfono, arreglo, comuna, destinatario..."
            className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
          {busqueda && (
            <button
              onClick={() => setBusqueda('')}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              <X className="h-5 w-5" />
            </button>
          )}
        </div>
        {busqueda && (
          <p className="mt-2 text-sm text-gray-600">
            📊 Mostrando {pedidosFiltrados.length} de {pedidos.length} pedidos
          </p>
        )}
      </div>

      {/* Filtros */}
      <div className="mb-6 flex gap-4">
        <select
          value={filtroEstado}
          onChange={(e) => {
            setFiltroEstado(e.target.value)
            setPaginaActual(1)
          }}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <option value="">Todos los estados</option>
          <option value="Entregas de Hoy">Entregas de Hoy</option>
          <option value="Entregas para Mañana">Entregas para Mañana</option>
          <option value="En Proceso">En Proceso</option>
          <option value="Listo para Despacho">Listo para Despacho</option>
          <option value="Despachados">Despachados</option>
          <option value="Pedidos Semana">Pedidos Semana</option>
          <option value="Eventos">Eventos</option>
          <option value="Archivado">Archivado</option>
          <option value="Cancelado">Cancelado</option>
        </select>
        
        <select
          value={filtroCanal}
          onChange={(e) => {
            setFiltroCanal(e.target.value)
            setPaginaActual(1)
          }}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <option value="">Todos los canales</option>
          <option value="Shopify">Shopify</option>
          <option value="WhatsApp">WhatsApp</option>
        </select>
      </div>
      
      {/* Controles de Paginación */}
      <div className="mb-4 flex items-center justify-between bg-gray-50 px-4 py-3 rounded-lg">
        <div className="text-sm text-gray-700">
          Mostrando <span className="font-medium">{((paginaActual - 1) * limitePorPagina) + 1}</span> a{' '}
          <span className="font-medium">{Math.min(paginaActual * limitePorPagina, totalPedidos)}</span> de{' '}
          <span className="font-medium">{totalPedidos.toLocaleString()}</span> pedidos
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setPaginaActual(1)}
            disabled={paginaActual === 1}
            className="px-3 py-1 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Primero
          </button>
          <button
            onClick={() => setPaginaActual(prev => Math.max(1, prev - 1))}
            disabled={paginaActual === 1}
            className="px-3 py-1 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Anterior
          </button>
          <span className="px-4 py-1 border border-gray-300 rounded-md text-sm font-medium bg-white">
            {paginaActual} / {totalPaginas}
          </span>
          <button
            onClick={() => setPaginaActual(prev => Math.min(totalPaginas, prev + 1))}
            disabled={paginaActual === totalPaginas}
            className="px-3 py-1 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Siguiente
          </button>
          <button
            onClick={() => setPaginaActual(totalPaginas)}
            disabled={paginaActual === totalPaginas}
            className="px-3 py-1 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Último
          </button>
        </div>
      </div>
      
      {/* Tabla de pedidos */}
      <div className="bg-white shadow-sm rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  ID / Cliente
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Arreglo / Para
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Comuna / Dirección
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Precio Ramo / Envío
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  💰 Cobranza
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Motivo
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Mensaje
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Estado
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Entrega
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {loading ? (
                <tr>
                  <td colSpan="8" className="px-6 py-8 text-center text-sm text-gray-500">
                    Cargando pedidos...
                  </td>
                </tr>
              ) : pedidosFiltrados.length === 0 ? (
                <tr>
                  <td colSpan="8" className="px-6 py-8 text-center">
                    {busqueda ? (
                      <>
                        <p className="text-gray-500 mb-2">🔍 No se encontraron pedidos</p>
                        <p className="text-xs text-gray-400">
                          No hay resultados para "{busqueda}"
                        </p>
                      </>
                    ) : (
                      <>
                        <p className="text-gray-500 mb-2">No hay pedidos</p>
                        <p className="text-xs text-gray-400">
                          Ejecuta <code className="bg-gray-100 px-2 py-1 rounded">python3 importar_datos_demo.py</code> para cargar datos
                        </p>
                      </>
                    )}
                  </td>
                </tr>
              ) : (
                pedidosFiltrados.map((pedido) => (
                  <tr 
                    key={pedido.id} 
                    onClick={() => handleAbrirPedido(pedido)}
                    className="hover:bg-primary-50 cursor-pointer transition-colors border-b border-gray-200"
                  >
                    <td className="px-6 py-4">
                      <div className="text-sm font-medium text-gray-900">{pedido.id}</div>
                      <div className="text-sm text-gray-500">{pedido.cliente_nombre}</div>
                      <div className="text-xs text-gray-400">{pedido.cliente_telefono}</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900">{pedido.arreglo_pedido || 'Sin especificar'}</div>
                      {pedido.destinatario && (
                        <div className="text-xs text-gray-500">Para: {pedido.destinatario}</div>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm font-medium text-gray-900">{pedido.comuna || 'Sin comuna'}</div>
                      <div className="text-xs text-gray-500 max-w-xs truncate" title={pedido.direccion_entrega}>
                        {pedido.direccion_entrega}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm font-semibold text-gray-900">
                        ${pedido.precio_ramo?.toLocaleString('es-CL') || '0'}
                      </div>
                      <div className="text-xs text-gray-500">
                        + ${pedido.precio_envio?.toLocaleString('es-CL') || '0'} envío
                      </div>
                      <div className="text-xs font-medium text-primary-600">
                        Total: ${pedido.precio_total?.toLocaleString('es-CL') || '0'}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      {/* Estado de Pago */}
                      <div className="flex items-center gap-1 mb-1">
                        {pedido.estado_pago === 'Pagado' ? (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                            ✅ Pagado
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
                            ❌ No Pagado
                          </span>
                        )}
                      </div>
                      {/* Método de Pago */}
                      {pedido.metodo_pago && (
                        <div className="text-xs text-gray-600">
                          💳 {pedido.metodo_pago}
                        </div>
                      )}
                      {/* Documento */}
                      <div className="text-xs text-gray-500 mt-1">
                        {pedido.documento_tributario === 'Boleta emitida' && pedido.numero_documento ? (
                          <span>🧾 Bol. N° {pedido.numero_documento}</span>
                        ) : pedido.documento_tributario === 'Factura emitida' && pedido.numero_documento ? (
                          <span>🧾 Fact. N° {pedido.numero_documento}</span>
                        ) : (
                          <span>🧾 {pedido.documento_tributario}</span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-700">{pedido.motivo || '-'}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-center">
                      {pedido.mensaje || pedido.destinatario || pedido.firma ? (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          💌 Sí
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
                          ✗ No
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${estadoColor[pedido.estado]}`}>
                        {pedido.estado}
                      </span>
                      {pedido.canal && (
                        <div className="text-xs text-gray-500 mt-1">{pedido.canal}</div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {pedido.fecha_entrega ? formatFecha(pedido.fecha_entrega) : '-'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
      
      {/* Modal de Detalles del Pedido */}
      {pedidoDetalle && (
        <div 
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
          onClick={() => setPedidoDetalle(null)}
        >
          <div 
            className="bg-white rounded-lg shadow-xl max-w-5xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="sticky top-0 bg-gradient-to-r from-primary-600 to-primary-700 text-white px-6 py-5 flex items-center justify-between z-10 shadow-lg rounded-t-lg">
              <div className="flex items-center gap-4">
                <div>
                  <h2 className="text-2xl font-bold">Pedido #{pedidoDetalle.id}</h2>
                  <p className="text-sm text-primary-100 mt-1">
                    {pedidoDetalle.numero_pedido ? `Nº ${pedidoDetalle.numero_pedido}` : 'Sin número de pedido'}
                  </p>
                </div>
                <span className={`px-4 py-2 text-xs leading-5 font-bold rounded-full shadow-md ${estadoColor[pedidoDetalle.estado]}`}>
                  {pedidoDetalle.estado}
                </span>
              </div>
              <button 
                onClick={() => setPedidoDetalle(null)}
                className="text-white hover:text-primary-100 transition-colors p-2 hover:bg-white/10 rounded-lg"
              >
                <X className="h-6 w-6" />
              </button>
            </div>
            
            {/* Contenido */}
            <div className="p-6 space-y-6">
              {/* Grid de 2 columnas para organizar mejor */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                
                {/* Columna Izquierda: Producto y Arreglo */}
                <div className="space-y-6">
                  
                  {/* Producto del Catálogo (si existe) */}
                  {pedidoDetalle.producto_nombre && (
                    <div className="bg-gradient-to-br from-primary-50 to-primary-100 p-5 rounded-lg border-2 border-primary-200 shadow-sm">
                      <h3 className="text-sm font-bold text-primary-800 uppercase mb-4 flex items-center">
                        <ShoppingBag className="h-5 w-5 mr-2" />
                        Producto del Catálogo
                      </h3>
                      
                      {/* Imagen del producto si existe */}
                      {pedidoDetalle.producto_imagen && (
                        <div className="mb-4">
                          <img 
                            src={pedidoDetalle.producto_imagen} 
                            alt={pedidoDetalle.producto_nombre}
                            className="w-full h-48 object-cover rounded-lg shadow-md border border-primary-200"
                          />
                        </div>
                      )}
                      
                      <div className="space-y-3">
                        <div>
                          <p className="text-xs text-primary-700 font-semibold uppercase mb-1">Nombre del Producto</p>
                          <p className="text-base font-bold text-primary-900">{pedidoDetalle.producto_nombre}</p>
                        </div>
                        
                        {pedidoDetalle.producto_id && (
                          <div>
                            <p className="text-xs text-primary-700 font-semibold uppercase mb-1">ID Producto</p>
                            <p className="text-sm text-primary-800 font-mono">{pedidoDetalle.producto_id}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                  
                  {/* Arreglo Pedido */}
                  <div className="bg-white border-2 border-gray-200 p-5 rounded-lg shadow-sm">
                    <h3 className="text-sm font-bold text-gray-700 uppercase mb-4 flex items-center">
                      <Package className="h-5 w-5 mr-2 text-gray-600" />
                      Detalles del Arreglo
                    </h3>
                    <div className="space-y-3">
                      <div>
                        <p className="text-xs text-gray-500 font-semibold uppercase mb-1">Arreglo Solicitado</p>
                        {modoEdicion ? (
                          <input
                            type="text"
                            value={pedidoEditado.arreglo_pedido || ''}
                            onChange={(e) => handleCampoEdicion('arreglo_pedido', e.target.value)}
                            className="w-full text-base font-medium text-gray-900 bg-white p-3 rounded border-2 border-primary-300 focus:border-primary-500 focus:outline-none"
                          />
                        ) : (
                          <p className="text-base font-medium text-gray-900 bg-gray-50 p-3 rounded border border-gray-200">
                            {pedidoDetalle.arreglo_pedido || 'Sin especificar'}
                          </p>
                        )}
                      </div>
                      
                      <div>
                        <p className="text-xs text-gray-500 font-semibold uppercase mb-1">Detalles Adicionales</p>
                        {modoEdicion ? (
                          <textarea
                            value={pedidoEditado.detalles_adicionales || ''}
                            onChange={(e) => handleCampoEdicion('detalles_adicionales', e.target.value)}
                            rows="3"
                            className="w-full text-sm text-gray-700 bg-white p-3 rounded border-2 border-yellow-300 focus:border-yellow-500 focus:outline-none"
                          />
                        ) : pedidoDetalle.detalles_adicionales && (
                          <p className="text-sm text-gray-700 bg-yellow-50 p-3 rounded border border-yellow-200">
                            {pedidoDetalle.detalles_adicionales}
                          </p>
                        )}
                      </div>
                      
                      <div>
                        <p className="text-xs text-gray-500 font-semibold uppercase mb-1">Motivo</p>
                        {modoEdicion ? (
                          <select
                            value={pedidoEditado.motivo || ''}
                            onChange={(e) => handleCampoEdicion('motivo', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500"
                          >
                            <option value="">-- Sin motivo --</option>
                            {MOTIVOS_PEDIDO.map(motivo => (
                              <option key={motivo} value={motivo}>{motivo}</option>
                            ))}
                          </select>
                        ) : pedidoDetalle.motivo ? (
                          <span className="inline-flex px-3 py-1.5 bg-pink-100 text-pink-800 rounded-full text-sm font-medium border border-pink-200">
                            💐 {pedidoDetalle.motivo}
                          </span>
                        ) : (
                          <span className="text-sm text-gray-400 italic">Sin motivo especificado</span>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  {/* Mensaje y Destinatario */}
                  {(pedidoDetalle.destinatario || pedidoDetalle.mensaje || pedidoDetalle.firma) && (
                    <div className="bg-gradient-to-br from-pink-50 to-rose-50 p-5 rounded-lg border-2 border-pink-200 shadow-sm">
                      <h3 className="text-sm font-bold text-pink-800 uppercase mb-4 flex items-center">
                        <MessageSquare className="h-5 w-5 mr-2" />
                        Mensaje y Destinatario
                      </h3>
                      <div className="space-y-3">
                        <div>
                          <p className="text-xs text-pink-700 font-semibold uppercase mb-1">Para</p>
                          {modoEdicion ? (
                            <input
                              type="text"
                              value={pedidoEditado.destinatario || ''}
                              onChange={(e) => handleCampoEdicion('destinatario', e.target.value)}
                              placeholder="Nombre del destinatario"
                              className="w-full text-base font-medium text-pink-900 bg-white p-2 rounded border-2 border-pink-300 focus:border-pink-500 focus:outline-none"
                            />
                          ) : pedidoDetalle.destinatario && (
                            <p className="text-base font-medium text-pink-900 bg-white p-2 rounded border border-pink-200">
                              {pedidoDetalle.destinatario}
                            </p>
                          )}
                        </div>
                        <div>
                          <p className="text-xs text-pink-700 font-semibold uppercase mb-1">Mensaje</p>
                          {modoEdicion ? (
                            <textarea
                              value={pedidoEditado.mensaje || ''}
                              onChange={(e) => handleCampoEdicion('mensaje', e.target.value)}
                              placeholder="Mensaje de la tarjeta"
                              rows="3"
                              className="w-full text-sm text-pink-900 bg-white p-3 rounded border-2 border-pink-300 focus:border-pink-500 focus:outline-none"
                            />
                          ) : pedidoDetalle.mensaje && (
                            <p className="text-sm text-pink-900 italic bg-white p-3 rounded border border-pink-200">
                              "{pedidoDetalle.mensaje}"
                            </p>
                          )}
                        </div>
                        <div>
                          <p className="text-xs text-pink-700 font-semibold uppercase mb-1">Firma</p>
                          {modoEdicion ? (
                            <input
                              type="text"
                              value={pedidoEditado.firma || ''}
                              onChange={(e) => handleCampoEdicion('firma', e.target.value)}
                              placeholder="Firma del mensaje"
                              className="w-full text-sm text-pink-900 bg-white p-2 rounded border-2 border-pink-300 focus:border-pink-500 focus:outline-none"
                            />
                          ) : pedidoDetalle.firma && (
                            <p className="text-sm text-pink-900 bg-white p-2 rounded border border-pink-200">
                              {pedidoDetalle.firma}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
                
                {/* Columna Derecha: Cliente, Entrega y Pago */}
                <div className="space-y-6">
                  
                  {/* Cliente */}
                  <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-5 rounded-lg border-2 border-blue-200 shadow-sm">
                    <h3 className="text-sm font-bold text-blue-800 uppercase mb-4 flex items-center">
                      <User className="h-5 w-5 mr-2" />
                      Información del Cliente
                    </h3>
                    <div className="space-y-3">
                      <div>
                        <p className="text-xs text-blue-700 font-semibold uppercase mb-1">Nombre Completo</p>
                        <p className="text-base font-bold text-blue-900">{pedidoDetalle.cliente_nombre}</p>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <p className="text-xs text-blue-700 font-semibold uppercase mb-1 flex items-center">
                            <Phone className="h-3 w-3 mr-1" /> Teléfono
                          </p>
                          {modoEdicion ? (
                            <input
                              type="tel"
                              value={pedidoEditado.cliente_telefono || ''}
                              onChange={(e) => handleCampoEdicion('cliente_telefono', e.target.value)}
                              className="w-full px-3 py-2 text-sm border border-blue-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                              placeholder="+56 9 1234 5678"
                            />
                          ) : (
                            <p className="text-sm font-medium text-blue-900 bg-white p-2 rounded border border-blue-200">
                              {pedidoDetalle.cliente_telefono}
                            </p>
                          )}
                        </div>
                        
                        <div>
                          <p className="text-xs text-blue-700 font-semibold uppercase mb-1 flex items-center">
                            <Mail className="h-3 w-3 mr-1" /> Email
                          </p>
                          {modoEdicion ? (
                            <input
                              type="email"
                              value={pedidoEditado.cliente_email || ''}
                              onChange={(e) => handleCampoEdicion('cliente_email', e.target.value)}
                              className="w-full px-3 py-2 text-sm border border-blue-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                              placeholder="cliente@ejemplo.com"
                            />
                          ) : pedidoDetalle.cliente_email ? (
                            <p className="text-sm font-medium text-blue-900 bg-white p-2 rounded border border-blue-200 truncate">
                              {pedidoDetalle.cliente_email}
                            </p>
                          ) : (
                            <p className="text-sm text-gray-400 italic bg-white p-2 rounded border border-blue-200">
                              Sin email
                            </p>
                          )}
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <p className="text-xs text-blue-700 font-semibold uppercase mb-1">Canal</p>
                          <span className={`inline-flex px-3 py-1.5 rounded-full text-xs font-bold ${
                            pedidoDetalle.canal === 'Shopify' ? 'bg-green-100 text-green-800 border border-green-300' : 
                            'bg-emerald-100 text-emerald-800 border border-emerald-300'
                          }`}>
                            {pedidoDetalle.canal}
                          </span>
                        </div>
                        
                        {pedidoDetalle.cliente_tipo && (
                          <div>
                            <p className="text-xs text-blue-700 font-semibold uppercase mb-1">Tipo Cliente</p>
                            <span className="inline-flex px-3 py-1.5 bg-purple-100 text-purple-800 rounded-full text-xs font-bold border border-purple-300">
                              {pedidoDetalle.cliente_tipo}
                            </span>
                          </div>
                        )}
                      </div>
                      
                      {pedidoDetalle.shopify_order_number && (
                        <div>
                          <p className="text-xs text-blue-700 font-semibold uppercase mb-1">Nº Orden Shopify</p>
                          <p className="text-sm font-mono font-medium text-blue-900 bg-white p-2 rounded border border-blue-200">
                            {pedidoDetalle.shopify_order_number}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                  
                  {/* Entrega */}
                  <div className="bg-gradient-to-br from-green-50 to-emerald-50 p-5 rounded-lg border-2 border-green-200 shadow-sm">
                    <h3 className="text-sm font-bold text-green-800 uppercase mb-4 flex items-center">
                      <MapPin className="h-5 w-5 mr-2" />
                      Información de Entrega
                    </h3>
                    <div className="space-y-3">
                      <div>
                        <p className="text-xs text-green-700 font-semibold uppercase mb-1">Dirección Completa</p>
                        {modoEdicion ? (
                          <textarea
                            value={pedidoEditado.direccion_entrega || ''}
                            onChange={(e) => handleCampoEdicion('direccion_entrega', e.target.value)}
                            rows="2"
                            className="w-full text-sm font-medium text-green-900 bg-white p-3 rounded border-2 border-green-300 focus:border-green-500 focus:outline-none"
                          />
                        ) : (
                          <p className="text-sm font-medium text-green-900 bg-white p-3 rounded border border-green-200">
                            {pedidoDetalle.direccion_entrega}
                          </p>
                        )}
                      </div>
                      
                      <div>
                        <p className="text-xs text-green-700 font-semibold uppercase mb-1">Comuna</p>
                        {modoEdicion ? (
                          <input
                            type="text"
                            value={pedidoEditado.comuna || ''}
                            onChange={(e) => handleCampoEdicion('comuna', e.target.value)}
                            className="w-full px-3 py-1.5 bg-white text-green-800 rounded-full text-sm font-bold border-2 border-green-300 focus:border-green-500 focus:outline-none"
                          />
                        ) : pedidoDetalle.comuna && (
                          <span className="inline-flex px-3 py-1.5 bg-green-100 text-green-800 rounded-full text-sm font-bold border border-green-300">
                            📍 {pedidoDetalle.comuna}
                          </span>
                        )}
                      </div>
                      
                      <div className="grid grid-cols-2 gap-3 pt-2">
                        <div>
                          <p className="text-xs text-green-700 font-semibold uppercase mb-1 flex items-center">
                            <Calendar className="h-3 w-3 mr-1" /> Fecha Pedido
                          </p>
                          <p className="text-sm text-green-900 bg-white p-2 rounded border border-green-200">
                            {formatFecha(pedidoDetalle.fecha_pedido)}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-green-700 font-semibold uppercase mb-1 flex items-center">
                            <Calendar className="h-3 w-3 mr-1" /> Fecha Entrega
                          </p>
                          <p className="text-sm font-bold text-green-900 bg-green-100 p-2 rounded border-2 border-green-300">
                            {formatFecha(pedidoDetalle.fecha_entrega)}
                          </p>
                        </div>
                      </div>
                      
                      {pedidoDetalle.dia_entrega && (
                        <div>
                          <p className="text-xs text-green-700 font-semibold uppercase mb-1">Día de Entrega</p>
                          <span className="inline-flex px-3 py-1.5 bg-blue-100 text-blue-800 rounded-full text-sm font-bold border border-blue-300">
                            {pedidoDetalle.dia_entrega}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                  
                  {/* Precios y Pago */}
                  <div className="bg-gradient-to-br from-amber-50 to-yellow-50 p-5 rounded-lg border-2 border-amber-300 shadow-sm">
                    <h3 className="text-sm font-bold text-amber-900 uppercase mb-4 flex items-center">
                      <DollarSign className="h-5 w-5 mr-2" />
                      Información de Pago
                    </h3>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center bg-white p-3 rounded border border-amber-200">
                        <span className="text-sm text-gray-700">Precio del Arreglo:</span>
                        {modoEdicion ? (
                          <div className="flex items-center gap-1">
                            <span className="text-base font-bold text-gray-900">$</span>
                            <input
                              type="number"
                              value={pedidoEditado.precio_ramo || 0}
                              onChange={(e) => handleCampoEdicion('precio_ramo', parseInt(e.target.value) || 0)}
                              className="w-32 text-base font-bold text-gray-900 bg-amber-50 p-2 rounded border-2 border-amber-300 focus:border-amber-500 focus:outline-none text-right"
                            />
                          </div>
                        ) : (
                          <span className="text-base font-bold text-gray-900">
                            ${pedidoDetalle.precio_ramo?.toLocaleString('es-CL') || '0'}
                          </span>
                        )}
                      </div>
                      <div className="flex justify-between items-center bg-white p-3 rounded border border-amber-200">
                        <span className="text-sm text-gray-700">Costo de Envío:</span>
                        {modoEdicion ? (
                          <div className="flex items-center gap-1">
                            <span className="text-base font-bold text-gray-900">$</span>
                            <input
                              type="number"
                              value={pedidoEditado.precio_envio || 0}
                              onChange={(e) => handleCampoEdicion('precio_envio', parseInt(e.target.value) || 0)}
                              className="w-32 text-base font-bold text-gray-900 bg-amber-50 p-2 rounded border-2 border-amber-300 focus:border-amber-500 focus:outline-none text-right"
                            />
                          </div>
                        ) : (
                          <span className="text-base font-bold text-gray-900">
                            ${pedidoDetalle.precio_envio?.toLocaleString('es-CL') || '0'}
                          </span>
                        )}
                      </div>
                      <div className="flex justify-between items-center bg-gradient-to-r from-amber-200 to-yellow-200 p-4 rounded-lg border-2 border-amber-400 shadow-md">
                        <span className="text-base font-bold text-amber-900">TOTAL:</span>
                        <span className="text-2xl font-black text-amber-900">
                          ${((pedidoEditado.precio_ramo || 0) + (pedidoEditado.precio_envio || 0)).toLocaleString('es-CL')}
                        </span>
                      </div>
                      
                      {/* Estado de Pago */}
                      <div className="pt-3 border-t border-amber-300">
                        <div className="grid grid-cols-2 gap-3">
                          {pedidoDetalle.estado_pago && (
                            <div>
                              <p className="text-xs text-amber-800 font-semibold uppercase mb-1">Estado Pago</p>
                              <span className={`inline-flex px-3 py-1.5 rounded-full text-xs font-bold border-2 ${
                                pedidoDetalle.estado_pago === 'Pagado' 
                                  ? 'bg-green-100 text-green-800 border-green-300' 
                                  : 'bg-red-100 text-red-800 border-red-300'
                              }`}>
                                {pedidoDetalle.estado_pago === 'Pagado' ? '✓ Pagado' : '⏳ Pendiente'}
                              </span>
                            </div>
                          )}
                          
                          {pedidoDetalle.metodo_pago && pedidoDetalle.metodo_pago !== 'Pendiente' && (
                            <div>
                              <p className="text-xs text-amber-800 font-semibold uppercase mb-1">Método Pago</p>
                              <span className="inline-flex px-3 py-1.5 bg-purple-100 text-purple-800 rounded-full text-xs font-bold border-2 border-purple-300">
                                {pedidoDetalle.metodo_pago}
                              </span>
                            </div>
                          )}
                        </div>
                        
                        {pedidoDetalle.documento_tributario && (
                          <div className="mt-3">
                            <p className="text-xs text-amber-800 font-semibold uppercase mb-1">Documento</p>
                            <span className="inline-flex px-3 py-1.5 bg-gray-100 text-gray-800 rounded-full text-xs font-bold border-2 border-gray-300">
                              📄 {pedidoDetalle.documento_tributario}
                            </span>
                          </div>
                        )}
                        
                        {pedidoDetalle.numero_documento && (
                          <div className="mt-2">
                            <p className="text-xs text-amber-800 font-semibold uppercase mb-1">Nº Documento</p>
                            <p className="text-sm font-mono font-bold text-amber-900 bg-white p-2 rounded border border-amber-200">
                              {pedidoDetalle.numero_documento}
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  {/* Etiquetas y Notas */}
                  {(pedidoDetalle.tipo_pedido || pedidoDetalle.cobranza) && (
                    <div className="bg-gray-50 p-5 rounded-lg border-2 border-gray-200 shadow-sm">
                      <h3 className="text-sm font-bold text-gray-700 uppercase mb-3">Información Adicional</h3>
                      <div className="space-y-3">
                        {pedidoDetalle.tipo_pedido && (
                          <div>
                            <p className="text-xs text-gray-500 font-semibold uppercase mb-1">Tipo de Pedido</p>
                            <span className="inline-flex px-3 py-1.5 bg-purple-100 text-purple-800 rounded-full text-sm font-bold border border-purple-300">
                              {pedidoDetalle.tipo_pedido}
                            </span>
                          </div>
                        )}
                        
                        {pedidoDetalle.cobranza && (
                          <div>
                            <p className="text-xs text-gray-500 font-semibold uppercase mb-1">Notas de Cobranza</p>
                            <p className="text-sm text-gray-700 bg-white p-3 rounded border border-gray-300">
                              {pedidoDetalle.cobranza}
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
            
            {/* Información Completa del Cliente */}
            {pedidoDetalle.cliente_id && (
              <div className="p-6 bg-gradient-to-br from-indigo-50 to-purple-50 border-t-4 border-indigo-500">
                <h2 className="text-xl font-bold text-indigo-900 mb-4 flex items-center">
                  <User className="h-6 w-6 mr-2" />
                  Perfil Completo del Cliente
                </h2>
                
                {loadingCliente ? (
                  <div className="text-center py-8">
                    <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-indigo-500 border-t-transparent"></div>
                    <p className="text-sm text-indigo-600 mt-2">Cargando información del cliente...</p>
                  </div>
                ) : clienteDetalle ? (
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Estadísticas del Cliente */}
                    <div className="bg-white p-5 rounded-lg shadow-md border-2 border-indigo-200">
                      <h3 className="text-sm font-bold text-indigo-800 uppercase mb-4">
                        📊 Estadísticas
                      </h3>
                      <div className="space-y-3">
                        <div className="flex justify-between items-center p-3 bg-indigo-50 rounded">
                          <span className="text-sm text-indigo-700 font-medium">Total de Pedidos:</span>
                          <span className="text-lg font-bold text-indigo-900">{clienteDetalle.total_pedidos || 0}</span>
                        </div>
                        <div className="flex justify-between items-center p-3 bg-purple-50 rounded">
                          <span className="text-sm text-purple-700 font-medium">Total Gastado:</span>
                          <span className="text-lg font-bold text-purple-900">
                            ${(clienteDetalle.total_gastado || 0).toLocaleString('es-CL')}
                          </span>
                        </div>
                        {clienteDetalle.total_pedidos > 0 && (
                          <div className="flex justify-between items-center p-3 bg-pink-50 rounded">
                            <span className="text-sm text-pink-700 font-medium">Ticket Promedio:</span>
                            <span className="text-lg font-bold text-pink-900">
                              ${Math.round((clienteDetalle.total_gastado || 0) / (clienteDetalle.total_pedidos || 1)).toLocaleString('es-CL')}
                            </span>
                          </div>
                        )}
                        {clienteDetalle.tipo_cliente && (
                          <div className="pt-3 border-t border-indigo-200">
                            <span className="text-xs text-indigo-700 font-semibold uppercase mb-2 block">Segmento</span>
                            <span className={`inline-flex px-4 py-2 rounded-full text-sm font-bold shadow-sm ${
                              clienteDetalle.tipo_cliente === 'VIP' ? 'bg-yellow-400 text-yellow-900' :
                              clienteDetalle.tipo_cliente === 'Fiel' ? 'bg-green-400 text-green-900' :
                              clienteDetalle.tipo_cliente === 'Cumplidor' ? 'bg-blue-400 text-blue-900' :
                              'bg-gray-300 text-gray-800'
                            }`}>
                              ⭐ {clienteDetalle.tipo_cliente}
                            </span>
                          </div>
                        )}
                        {clienteDetalle.ultima_compra && (
                          <div className="text-xs text-indigo-600 pt-2 border-t border-indigo-200">
                            Última compra: {formatFecha(clienteDetalle.ultima_compra)}
                          </div>
                        )}
                      </div>
                    </div>
                    
                    {/* Historial de Pedidos */}
                    <div className="bg-white p-5 rounded-lg shadow-md border-2 border-purple-200">
                      <h3 className="text-sm font-bold text-purple-800 uppercase mb-4 flex items-center justify-between">
                        <span>📋 Historial de Pedidos</span>
                        <span className="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded-full">
                          {historialCliente.length} pedidos
                        </span>
                      </h3>
                      <div className="max-h-64 overflow-y-auto space-y-2 custom-scrollbar">
                        {historialCliente.length > 0 ? (
                          historialCliente.slice(0, 10).map((ped) => (
                            <div 
                              key={ped.id} 
                              className={`p-3 rounded-lg border-2 transition-all ${
                                ped.id === pedidoDetalle.id 
                                  ? 'bg-indigo-100 border-indigo-400 shadow-md' 
                                  : 'bg-gray-50 border-gray-200 hover:bg-gray-100'
                              }`}
                            >
                              <div className="flex justify-between items-start mb-1">
                                <span className="text-xs font-bold text-gray-800">
                                  {ped.id === pedidoDetalle.id && '➤ '}Pedido #{ped.id}
                                </span>
                                <span className="text-xs font-semibold text-primary-600">
                                  ${(ped.precio_total || 0).toLocaleString('es-CL')}
                                </span>
                              </div>
                              <p className="text-xs text-gray-600 truncate mb-1">
                                {ped.arreglo_pedido || 'Sin descripción'}
                              </p>
                              <div className="flex justify-between items-center text-xs">
                                <span className="text-gray-500">
                                  📅 {formatFecha(ped.fecha_pedido)}
                                </span>
                                <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                                  ped.estado_pago === 'Pagado' 
                                    ? 'bg-green-100 text-green-800' 
                                    : 'bg-red-100 text-red-800'
                                }`}>
                                  {ped.estado_pago === 'Pagado' ? '✓' : '⏳'}
                                </span>
                              </div>
                            </div>
                          ))
                        ) : (
                          <p className="text-sm text-gray-500 text-center py-4">
                            No hay historial de pedidos
                          </p>
                        )}
                        {historialCliente.length > 10 && (
                          <p className="text-xs text-center text-indigo-600 pt-2 italic">
                            Mostrando últimos 10 de {historialCliente.length} pedidos
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-4 text-sm text-gray-500">
                    No se pudo cargar la información del cliente
                  </div>
                )}
              </div>
            )}
            
            {/* Footer del Modal */}
            <div className="sticky bottom-0 bg-gray-100 px-6 py-4 flex justify-between items-center rounded-b-lg border-t border-gray-200">
              <div className="flex gap-3">
                <button
                  onClick={() => setPedidoDetalle(null)}
                  className="px-6 py-2.5 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors font-medium"
                >
                  Cerrar
                </button>
                
                {/* Botones de Cancelar y Eliminar */}
                {pedidoDetalle?.estado !== 'Cancelado' && (
                  <button
                    onClick={handleCancelarPedido}
                    className="px-6 py-2.5 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors font-medium flex items-center gap-2"
                    title="Cambiar estado a Cancelado"
                  >
                    <XCircle className="h-4 w-4" />
                    Cancelar Pedido
                  </button>
                )}
                
                <button
                  onClick={handleEliminarPedido}
                  className="px-6 py-2.5 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium flex items-center gap-2"
                  title="Eliminar permanentemente de la base de datos"
                >
                  <Trash2 className="h-4 w-4" />
                  Eliminar
                </button>
              </div>
              
              <div className="flex gap-3">
                {modoEdicion ? (
                  <>
                    <button
                      onClick={handleCancelarEdicion}
                      className="px-6 py-2.5 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors font-medium"
                    >
                      Cancelar Edición
                    </button>
                    <button
                      onClick={handleGuardarEdicion}
                      className="px-6 py-2.5 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium flex items-center gap-2"
                    >
                      <CheckCircle className="h-4 w-4" />
                      Guardar Cambios
                    </button>
                  </>
                ) : (
                  <button
                    onClick={handleActivarEdicion}
                    className="px-6 py-2.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium flex items-center gap-2"
                  >
                    <Edit className="h-4 w-4" />
                    Editar Pedido
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Modal de Formulario de Nuevo Pedido */}
      {mostrarFormulario && (
        <div 
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
          onClick={handleCerrarFormulario}
        >
          <div 
            className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] flex flex-col"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header - Fijo */}
            <div className="flex-shrink-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between rounded-t-lg">
              <h2 className="text-2xl font-bold text-gray-900">Nuevo Pedido</h2>
              <button 
                onClick={handleCerrarFormulario}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <X className="h-6 w-6" />
              </button>
            </div>
            
            {/* Formulario - Con scroll */}
            <form id="form-nuevo-pedido" onSubmit={handleSubmitPedido} className="flex-1 overflow-y-auto p-6">
              <div className="space-y-6">
                {/* Canal */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Canal <span className="text-red-500">*</span>
                  </label>
                  <div className="flex gap-4">
                    <label className="flex items-center">
                      <input
                        type="radio"
                        name="canal"
                        value="WhatsApp"
                        checked={formData.canal === 'WhatsApp'}
                        onChange={(e) => setFormData({...formData, canal: e.target.value})}
                        className="mr-2"
                      />
                      WhatsApp
                    </label>
                    <label className="flex items-center">
                      <input
                        type="radio"
                        name="canal"
                        value="Shopify"
                        checked={formData.canal === 'Shopify'}
                        onChange={(e) => setFormData({...formData, canal: e.target.value})}
                        className="mr-2"
                      />
                      Shopify
                    </label>
                  </div>
                </div>
                
                {/* Nº Shopify (solo si es Shopify) */}
                {formData.canal === 'Shopify' && (
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Nº Pedido Shopify
                    </label>
                    <input
                      type="text"
                      value={formData.shopify_order_number}
                      onChange={(e) => setFormData({...formData, shopify_order_number: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                      placeholder="#1234"
                    />
                  </div>
                )}
                
                {/* Información del Cliente con Búsqueda Inteligente */}
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-4 rounded-lg border-2 border-blue-200">
                  <h3 className="text-sm font-semibold text-gray-700 uppercase mb-3">
                    👤 Información del Cliente
                  </h3>
                  <div className="space-y-4">
                    {/* Nombre con búsqueda inteligente */}
                    <div className="relative">
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Nombre del Cliente <span className="text-red-500">*</span>
                        {buscandoCliente && <span className="ml-2 text-xs text-blue-600">Buscando...</span>}
                      </label>
                      <input
                        type="text"
                        required
                        value={formData.cliente_nombre}
                        onChange={(e) => handleNombreChange(e.target.value)}
                        onFocus={() => {
                          if (sugerenciasClientes.length > 0) {
                            setMostrarSugerencias(true)
                          }
                        }}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Escribe el nombre para buscar..."
                        autoComplete="off"
                      />
                      
                      {/* Dropdown de sugerencias */}
                      {mostrarSugerencias && sugerenciasClientes.length > 0 && (
                        <div 
                          className="absolute z-[9999] w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-xl max-h-64 overflow-y-auto"
                          onMouseDown={(e) => {
                            e.preventDefault()
                            e.stopPropagation()
                          }}
                          onClick={(e) => {
                            e.preventDefault()
                            e.stopPropagation()
                          }}
                        >
                          {sugerenciasClientes.map((cliente) => (
                            <div
                              key={cliente.id}
                              role="button"
                              tabIndex={0}
                              onMouseDown={(e) => {
                                e.preventDefault()
                                e.stopPropagation()
                                seleccionarCliente(cliente)
                                return false
                              }}
                              onClick={(e) => {
                                e.preventDefault()
                                e.stopPropagation()
                                return false
                              }}
                              className="w-full text-left px-4 py-3 hover:bg-blue-50 cursor-pointer border-b border-gray-100 last:border-b-0"
                            >
                              <div className="flex items-center justify-between">
                                <div className="flex-1">
                                  <p className="font-semibold text-gray-900">{cliente.nombre}</p>
                                  <p className="text-sm text-gray-600">{cliente.telefono}</p>
                                </div>
                                <div className="flex items-center gap-2">
                                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                                    cliente.tipo_cliente === 'VIP' ? 'bg-purple-100 text-purple-700' :
                                    cliente.tipo_cliente === 'Fiel' ? 'bg-blue-100 text-blue-700' :
                                    cliente.tipo_cliente === 'Cumplidor' ? 'bg-green-100 text-green-700' :
                                    cliente.tipo_cliente === 'No Cumplidor' ? 'bg-red-100 text-red-700' :
                                    'bg-gray-100 text-gray-700'
                                  }`}>
                                    {cliente.tipo_cliente}
                                  </span>
                                  <span className="text-xs text-gray-500">
                                    {cliente.total_pedidos} pedidos
                                  </span>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                    
                    {/* Información del cliente encontrado */}
                    {clienteEncontrado && (
                      <div className="bg-green-50 p-4 rounded-lg border-2 border-green-300">
                        <div className="flex items-center gap-2 mb-3">
                          <CheckCircle className="h-5 w-5 text-green-600" />
                          <span className="font-semibold text-green-700">Cliente Encontrado</span>
                          <span className={`ml-auto px-3 py-1 rounded-full text-xs font-medium ${
                            clienteEncontrado.tipo_cliente === 'VIP' ? 'bg-purple-100 text-purple-700' :
                            clienteEncontrado.tipo_cliente === 'Fiel' ? 'bg-blue-100 text-blue-700' :
                            clienteEncontrado.tipo_cliente === 'Cumplidor' ? 'bg-green-100 text-green-700' :
                            clienteEncontrado.tipo_cliente === 'No Cumplidor' ? 'bg-red-100 text-red-700' :
                            'bg-gray-100 text-gray-700'
                          }`}>
                            {clienteEncontrado.tipo_cliente}
                          </span>
                        </div>
                        <div className="grid grid-cols-2 gap-3 text-sm">
                          <div>
                            <p className="text-gray-600"><strong>ID:</strong> {clienteEncontrado.id}</p>
                            <p className="text-gray-600"><strong>Teléfono:</strong> {clienteEncontrado.telefono}</p>
                          </div>
                          <div>
                            <p className="text-gray-600"><strong>Pedidos:</strong> {clienteEncontrado.total_pedidos}</p>
                            <p className="text-gray-600"><strong>Total:</strong> ${clienteEncontrado.total_gastado?.toLocaleString('es-CL')}</p>
                          </div>
                        </div>
                        {clienteEncontrado.notas && (
                          <p className="text-xs italic mt-3 text-gray-700 bg-white p-2 rounded">📝 {clienteEncontrado.notas}</p>
                        )}
                      </div>
                    )}
                    
                    {/* Historial de Pedidos */}
                    {clienteEncontrado && (
                      <div className="bg-gradient-to-r from-indigo-50 to-purple-50 border-2 border-indigo-200 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-3">
                          <h4 className="text-sm font-semibold text-gray-700 flex items-center gap-2">
                            📦 Historial de Pedidos
                          </h4>
                          {cargandoHistorial && (
                            <span className="text-xs text-gray-500">Cargando...</span>
                          )}
                        </div>
                        
                        {!cargandoHistorial && historialPedidos.length === 0 && (
                          <p className="text-xs text-gray-500 italic">Este cliente no tiene pedidos anteriores</p>
                        )}
                        
                        {!cargandoHistorial && historialPedidos.length > 0 && (
                          <div className="space-y-2 max-h-96 overflow-y-auto">
                            {historialPedidos.map((pedido) => (
                              <div key={pedido.id} className="bg-white p-3 rounded-lg shadow-sm text-xs border border-indigo-100">
                                <div className="flex justify-between items-start mb-1">
                                  <span className="font-semibold text-gray-800">{pedido.id}</span>
                                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                                    pedido.estado === 'Despachados' ? 'bg-purple-100 text-purple-700' :
                                    pedido.estado === 'En Proceso' ? 'bg-yellow-100 text-yellow-700' :
                                    pedido.estado === 'Archivado' ? 'bg-gray-100 text-gray-600' :
                                    'bg-blue-100 text-blue-700'
                                  }`}>
                                    {pedido.estado}
                                  </span>
                                </div>
                                <p className="text-gray-700 font-medium">{pedido.arreglo_pedido}</p>
                                <div className="flex justify-between items-center mt-1 text-gray-500">
                                  <span>{new Date(pedido.fecha_pedido).toLocaleDateString('es-CL')}</span>
                                  <span className="font-semibold text-primary-600">${pedido.precio_total?.toLocaleString('es-CL')}</span>
                                </div>
                              </div>
                            ))}
                            <p className="text-xs text-center text-gray-500 italic pt-2">
                              📦 Total: {historialPedidos.length} pedido(s)
                            </p>
                          </div>
                        )}
                      </div>
                    )}
                    
                    {/* Teléfono y Email */}
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Teléfono <span className="text-red-500">*</span>
                          {clienteEncontrado && <span className="ml-2 text-xs text-blue-600">✏️ Editable</span>}
                        </label>
                        <input
                          type="tel"
                          required
                          value={formData.cliente_telefono}
                          onChange={(e) => setFormData({...formData, cliente_telefono: e.target.value})}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder="+56 9 1234 5678"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Email
                        </label>
                        <input
                          type="email"
                          value={formData.cliente_email}
                          onChange={(e) => setFormData({...formData, cliente_email: e.target.value})}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder="cliente@ejemplo.com"
                        />
                      </div>
                    </div>
                    
                    {/* Plazo de Pago */}
                    <div className="bg-yellow-50 p-3 rounded-lg border border-yellow-200">
                      <div className="flex items-center justify-between mb-2">
                        <label className="block text-sm font-semibold text-gray-700">
                          💳 Plazo de Pago
                        </label>
                        <label className="flex items-center text-xs">
                          <input
                            type="checkbox"
                            checked={plazoPagoManual}
                            onChange={(e) => setPlazoPagoManual(e.target.checked)}
                            className="mr-1"
                          />
                          Manual
                        </label>
                      </div>
                      <div className="flex items-center gap-2">
                        <input
                          type="number"
                          min="0"
                          value={formData.plazo_pago_dias}
                          onChange={(e) => setFormData({...formData, plazo_pago_dias: parseInt(e.target.value) || 0})}
                          disabled={!plazoPagoManual}
                          className={`w-24 px-3 py-2 border rounded-lg ${
                            plazoPagoManual ? 'border-gray-300' : 'bg-gray-100 border-gray-200'
                          }`}
                        />
                        <span className="text-sm text-gray-700">días</span>
                        {!plazoPagoManual && clienteEncontrado && (
                          <span className="text-xs text-gray-500 ml-2">
                            (Automático según tipo: {clienteEncontrado.tipo_cliente})
                          </span>
                        )}
                      </div>
                      {formData.plazo_pago_dias === 0 && (
                        <p className="text-xs text-orange-600 mt-1">⚠️ Pago inmediato</p>
                      )}
                    </div>
                  </div>
                </div>
                
                {/* Arreglo / Producto */}
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="text-sm font-semibold text-gray-700 uppercase mb-3">
                    Arreglo Solicitado
                  </h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Nombre del Arreglo
                      </label>
                      <input
                        type="text"
                        value={formData.arreglo_pedido}
                        onChange={(e) => setFormData({...formData, arreglo_pedido: e.target.value})}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                        placeholder="Pasión Roja, Ramo de Rosas, etc."
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Producto de Catálogo (opcional)
                        {formData.producto_id && (
                          <span className="ml-2 text-xs text-green-600">✓ Precio auto-rellenado</span>
                        )}
                      </label>
                      <select
                        value={formData.producto_id}
                        onChange={(e) => handleProductoChange(e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                      >
                        <option value="">-- Sin producto asociado --</option>
                        {productos.map(prod => (
                          <option key={prod.id} value={prod.id}>
                            {prod.nombre} - ${prod.precio_venta?.toLocaleString('es-CL')}
                          </option>
                        ))}
                      </select>
                      {formData.producto_id && (
                        <p className="text-xs text-gray-500 mt-1">
                          💡 El nombre y precio se rellenaron automáticamente, pero puedes modificarlos
                        </p>
                      )}
                    </div>
                    
                    {/* Campo para Personalización */}
                    {esPersonalizacion && (
                      <div className="p-3 bg-purple-50 rounded-lg border border-purple-200">
                        <label className="block text-sm font-semibold text-purple-900 mb-2 flex items-center gap-2">
                          <Palette className="h-4 w-4" />
                          Producto en Shopify Parecido (opcional)
                        </label>
                        <input
                          type="text"
                          value={datosPersonalizacion.producto_shopify_referencia}
                          onChange={(e) => handlePersonalizacionChange('producto_shopify_referencia', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                          placeholder="Ej: Ramo Pasión, Bouquet XL, URL del producto..."
                        />
                        <p className="text-xs text-gray-500 mt-1">
                          💡 Referencia visual para el taller
                        </p>
                      </div>
                    )}
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Detalles Adicionales
                      </label>
                      <textarea
                        value={formData.detalles_adicionales}
                        onChange={(e) => setFormData({...formData, detalles_adicionales: e.target.value})}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                        rows="3"
                        placeholder="Colores específicos, flores especiales, etc."
                      />
                    </div>
                  </div>
                </div>
                
                {/* Selector de Insumos por Color */}
                <div className="bg-white p-4 rounded-lg border-2 border-primary-300">
                  <h3 className="text-sm font-semibold text-gray-700 uppercase mb-3 flex items-center gap-2">
                    <Package className="h-5 w-5" />
                    Selecciona los Insumos
                  </h3>
                  <SelectorInsumosColores
                    productoId={formData.producto_id}
                    onInsumosChange={handleInsumosChange}
                    onCostoChange={handleCostoChange}
                  />
                  
                  {costoCalculado && (
                    <div className="mt-4 bg-primary-50 p-3 rounded-lg">
                      <div className="text-sm space-y-1">
                        <div className="flex justify-between">
                          <span className="text-gray-700">Costo Flores:</span>
                          <span className="font-semibold">${costoCalculado.flores?.toLocaleString('es-CL')}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-700">Costo Contenedor:</span>
                          <span className="font-semibold">${costoCalculado.contenedor?.toLocaleString('es-CL')}</span>
                        </div>
                        <div className="flex justify-between border-t border-primary-200 pt-1 mt-1">
                          <span className="text-gray-900 font-semibold">Costo Total:</span>
                          <span className="text-primary-600 font-bold text-lg">${costoCalculado.total?.toLocaleString('es-CL')}</span>
                        </div>
                        <p className="text-xs text-gray-500 mt-2">
                          💡 El precio del ramo se calculó automáticamente con un margen del 50%
                        </p>
                      </div>
                    </div>
                  )}
                </div>
                
                {/* Insumos del pedido */}
                {formData.producto_id && (
                  <div className="bg-yellow-50 p-4 rounded-lg border-2 border-yellow-300">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-sm font-semibold text-gray-700 uppercase flex items-center gap-2">
                        <Package className="h-4 w-4" />
                        Insumos del Pedido
                      </h3>
                      <div className="flex gap-2">
                        <button
                          type="button"
                          onClick={() => handleAgregarInsumo('Flor')}
                          className="text-xs px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700"
                        >
                          + Flor
                        </button>
                        <button
                          type="button"
                          onClick={() => handleAgregarInsumo('Contenedor')}
                          className="text-xs px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700"
                        >
                          + Contenedor
                        </button>
                      </div>
                    </div>
                    
                    {loadingReceta ? (
                      <div className="text-center py-4 text-gray-500">
                        <div className="animate-pulse">⏳ Cargando insumos del producto...</div>
                      </div>
                    ) : insumosModificados.length === 0 && receta.length === 0 ? (
                      <div className="text-center py-6 bg-white rounded-lg border-2 border-dashed border-yellow-300">
                        <div className="mb-3">
                          <Package className="h-12 w-12 mx-auto text-yellow-400" />
                        </div>
                        <p className="text-gray-700 font-medium mb-1">
                          {esPersonalizacion
                            ? '✨ Personalización: Empieza agregando insumos'
                            : 'Este producto no tiene insumos predefinidos'}
                        </p>
                        <p className="text-sm text-gray-500 mb-3">
                          Usa los botones <span className="font-semibold text-green-600">+ Flor</span> o <span className="font-semibold text-blue-600">+ Contenedor</span> arriba para agregar insumos al pedido
                        </p>
                        <p className="text-xs text-gray-400">
                          💡 Los insumos te ayudan a gestionar el stock automáticamente
                        </p>
                      </div>
                    ) : insumosModificados.length > 0 ? (
                      <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-300">
                          <thead className="bg-yellow-100">
                            <tr>
                              <th className="px-3 py-2 text-left text-xs font-medium text-gray-600">Tipo</th>
                              <th className="px-3 py-2 text-left text-xs font-medium text-gray-600">Insumo</th>
                              <th className="px-3 py-2 text-center text-xs font-medium text-gray-600">Cantidad</th>
                              <th className="px-3 py-2 text-right text-xs font-medium text-gray-600">Stock</th>
                              <th className="px-3 py-2 text-right text-xs font-medium text-gray-600">Costo Unit.</th>
                              <th className="px-3 py-2 text-right text-xs font-medium text-gray-600">Total</th>
                              <th className="px-3 py-2 text-center text-xs font-medium text-gray-600">Acciones</th>
                            </tr>
                          </thead>
                          <tbody className="bg-white divide-y divide-gray-200">
                            {insumosModificados.map((insumo, index) => {
                              const stockSuficiente = insumo.stock_disponible >= insumo.cantidad
                              const totalInsumo = insumo.cantidad * insumo.costo_unitario
                              
                              return (
                                <tr key={index} className={!stockSuficiente ? 'bg-red-50' : ''}>
                                  <td className="px-3 py-2">
                                    <span className={`px-2 py-1 rounded text-xs ${insumo.insumo_tipo === 'Flor' ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'}`}>
                                      {insumo.insumo_tipo}
                                    </span>
                                  </td>
                                  <td className="px-3 py-2">
                                    <select
                                      value={insumo.insumo_id}
                                      onChange={(e) => handleCambiarInsumo(index, e.target.value, insumo.insumo_tipo)}
                                      className="text-sm border border-gray-300 rounded px-2 py-1 w-full"
                                    >
                                      <option value="">-- Seleccionar --</option>
                                      {insumo.insumo_tipo === 'Flor' ? (
                                        flores.map(flor => (
                                          <option key={flor.id} value={flor.id}>
                                            {flor.tipo} - {flor.color}
                                          </option>
                                        ))
                                      ) : (
                                        contenedores.map(cont => (
                                          <option key={cont.id} value={cont.id}>
                                            {cont.tipo} - {cont.material}
                                          </option>
                                        ))
                                      )}
                                    </select>
                                  </td>
                                  <td className="px-3 py-2 text-center">
                                    <input
                                      type="number"
                                      min="1"
                                      value={insumo.cantidad}
                                      onChange={(e) => handleCantidadInsumo(index, e.target.value)}
                                      className="w-16 text-center border border-gray-300 rounded px-2 py-1"
                                    />
                                  </td>
                                  <td className={`px-3 py-2 text-right text-sm ${!stockSuficiente ? 'text-red-600 font-bold' : 'text-gray-600'}`}>
                                    {insumo.stock_disponible || 0}
                                    {!stockSuficiente && ' ⚠️'}
                                  </td>
                                  <td className="px-3 py-2 text-right text-sm text-gray-600">
                                    ${(insumo.costo_unitario || 0).toLocaleString()}
                                  </td>
                                  <td className="px-3 py-2 text-right text-sm font-medium">
                                    ${totalInsumo.toLocaleString()}
                                  </td>
                                  <td className="px-3 py-2 text-center">
                                    <button
                                      type="button"
                                      onClick={() => handleEliminarInsumo(index)}
                                      className="text-red-600 hover:text-red-800"
                                    >
                                      <X className="h-4 w-4" />
                                    </button>
                                  </td>
                                </tr>
                              )
                            })}
                          </tbody>
                          <tfoot className="bg-yellow-50">
                            <tr>
                              <td colSpan="5" className="px-3 py-2 text-right text-sm font-semibold text-gray-700">
                                Total Costo Insumos:
                              </td>
                              <td className="px-3 py-2 text-right text-sm font-bold text-gray-900">
                                ${insumosModificados.reduce((sum, i) => sum + (i.cantidad * i.costo_unitario), 0).toLocaleString()}
                              </td>
                              <td></td>
                            </tr>
                          </tfoot>
                        </table>
                      </div>
                    ) : receta.length > 0 ? (
                      <div className="text-center py-6 bg-white rounded-lg border-2 border-dashed border-green-300">
                        <div className="mb-3">
                          <CheckCircle className="h-12 w-12 mx-auto text-green-500" />
                        </div>
                        <p className="text-gray-700 font-medium mb-1">
                          ✅ Receta cargada: {receta.length} insumo{receta.length > 1 ? 's' : ''}
                        </p>
                        <p className="text-sm text-gray-500 mb-3">
                          La receta del producto está lista. Estos insumos se usarán automáticamente.
                        </p>
                        <div className="max-w-md mx-auto text-left bg-gray-50 p-3 rounded">
                          {receta.map((insumo, idx) => (
                            <div key={idx} className="flex justify-between items-center text-sm py-1 border-b border-gray-200 last:border-b-0">
                              <span className="text-gray-700">
                                <span className={`inline-block w-16 text-xs px-2 py-0.5 rounded ${insumo.insumo_tipo === 'Flor' ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'}`}>
                                  {insumo.insumo_tipo}
                                </span>
                                {' '}{insumo.insumo_nombre}
                              </span>
                              <span className="font-semibold text-gray-900">x{insumo.cantidad}</span>
                            </div>
                          ))}
                        </div>
                        <p className="text-xs text-gray-400 mt-3">
                          💡 Puedes agregar más insumos usando los botones arriba
                        </p>
                      </div>
                    ) : null}
                    
                    <p className="text-xs text-gray-600 mt-2">
                      💡 Estos insumos se guardarán con el pedido y se usarán en el Taller para confirmar y descontar stock.
                    </p>
                  </div>
                )}
                
                {/* Mensaje y Destinatario */}
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-sm font-semibold text-gray-700 uppercase">
                      💌 Tarjeta con Mensaje
                    </h3>
                    <label className="flex items-center cursor-pointer">
                      <div className="relative">
                        <input
                          type="checkbox"
                          checked={formData.lleva_mensaje}
                          onChange={(e) => setFormData({...formData, lleva_mensaje: e.target.checked})}
                          className="sr-only"
                        />
                        <div className={`block w-14 h-8 rounded-full transition ${
                          formData.lleva_mensaje ? 'bg-green-500' : 'bg-gray-300'
                        }`}></div>
                        <div className={`dot absolute left-1 top-1 bg-white w-6 h-6 rounded-full transition ${
                          formData.lleva_mensaje ? 'transform translate-x-6' : ''
                        }`}></div>
                      </div>
                      <span className={`ml-3 text-sm font-medium ${
                        formData.lleva_mensaje ? 'text-green-700' : 'text-gray-500'
                      }`}>
                        {formData.lleva_mensaje ? '✓ Lleva mensaje' : '✗ Sin mensaje'}
                      </span>
                    </label>
                  </div>
                  
                  <div className={`space-y-4 transition-all ${
                    !formData.lleva_mensaje ? 'opacity-30 pointer-events-none blur-sm' : ''
                  }`}>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Para (Destinatario)
                      </label>
                      <input
                        type="text"
                        value={formData.destinatario}
                        onChange={(e) => setFormData({...formData, destinatario: e.target.value})}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                        placeholder="Ana López"
                        disabled={!formData.lleva_mensaje}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Mensaje
                      </label>
                      <textarea
                        value={formData.mensaje}
                        onChange={(e) => setFormData({...formData, mensaje: e.target.value})}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                        rows="3"
                        placeholder="Feliz cumpleaños! Que tengas un día maravilloso..."
                        disabled={!formData.lleva_mensaje}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Firma
                      </label>
                      <input
                        type="text"
                        value={formData.firma}
                        onChange={(e) => setFormData({...formData, firma: e.target.value})}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                        placeholder="Con cariño, Juan"
                        disabled={!formData.lleva_mensaje}
                      />
                    </div>
                  </div>
                  
                  {!formData.lleva_mensaje && (
                    <p className="text-xs text-gray-500 italic mt-2 text-center">
                      ℹ️ Activa el interruptor para agregar un mensaje personalizado
                    </p>
                  )}
                </div>
                
                {/* Entrega */}
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="text-sm font-semibold text-gray-700 uppercase mb-3">
                    Información de Entrega
                  </h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Dirección Completa <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="text"
                        required
                        value={formData.direccion_entrega}
                        onChange={(e) => setFormData({...formData, direccion_entrega: e.target.value})}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                        placeholder="Av. Apoquindo 1234, Depto 501"
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Comuna
                          {formData.comuna && (
                            <span className="ml-2 text-xs text-green-600">✓ Precio envío auto-rellenado</span>
                          )}
                        </label>
                        <select
                          value={formData.comuna}
                          onChange={(e) => handleComunaChange(e.target.value)}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                        >
                          <option value="">-- Seleccionar comuna --</option>
                          {comunas.map(com => (
                            <option key={com.comuna} value={com.comuna}>
                              {com.comuna} - ${com.precio.toLocaleString('es-CL')}
                            </option>
                          ))}
                        </select>
                        {formData.comuna && (
                          <p className="text-xs text-gray-500 mt-1">
                            💡 Precio de envío actualizado, pero puedes modificarlo abajo
                          </p>
                        )}
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Fecha de Entrega <span className="text-red-500">*</span>
                        </label>
                        <input
                          type="datetime-local"
                          required
                          value={formData.fecha_entrega}
                          onChange={(e) => setFormData({...formData, fecha_entrega: e.target.value})}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                        />
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* Motivo */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Motivo
                  </label>
                  <select
                    value={formData.motivo}
                    onChange={(e) => setFormData({...formData, motivo: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="">-- Seleccionar motivo --</option>
                    {MOTIVOS_PEDIDO.map(motivo => (
                      <option key={motivo} value={motivo}>{motivo}</option>
                    ))}
                  </select>
                </div>
                
                {/* Precios - Al Final */}
                <div className="bg-gradient-to-r from-amber-50 to-yellow-50 p-5 rounded-lg border-2 border-amber-400 shadow-md">
                  <h3 className="text-sm font-bold text-amber-900 uppercase mb-4 flex items-center">
                    <DollarSign className="h-5 w-5 mr-2" />
                    💰 Precios del Pedido
                  </h3>
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">
                        Precio Ramo <span className="text-red-500">*</span>
                      </label>
                      <div className="relative">
                        <span className="absolute left-3 top-3 text-gray-500 font-bold">$</span>
                        <input
                          type="number"
                          required
                          min="0"
                          step="1000"
                          value={formData.precio_ramo}
                          onChange={(e) => setFormData({...formData, precio_ramo: e.target.value})}
                          className="w-full pl-8 pr-4 py-2 border-2 border-amber-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500 bg-white font-semibold"
                          placeholder="35000"
                        />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">
                        Precio Envío
                      </label>
                      <div className="relative">
                        <span className="absolute left-3 top-3 text-gray-500 font-bold">$</span>
                        <input
                          type="number"
                          min="0"
                          step="1000"
                          value={formData.precio_envio}
                          onChange={(e) => setFormData({...formData, precio_envio: e.target.value})}
                          className="w-full pl-8 pr-4 py-2 border-2 border-amber-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500 bg-white font-semibold"
                          placeholder="7000"
                        />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">
                        💵 Total a Cobrar
                      </label>
                      <div className="w-full px-4 py-2 bg-gradient-to-r from-amber-200 to-yellow-200 border-2 border-amber-500 rounded-lg font-black text-amber-900 text-2xl text-center shadow-inner">
                        ${totalPedido.toLocaleString('es-CL')}
                      </div>
                    </div>
                  </div>
                  {costoCalculado && (
                    <div className="mt-3 p-3 bg-white rounded border border-amber-200">
                      <p className="text-xs text-gray-600">
                        💡 <strong>Costo de insumos:</strong> ${costoCalculado.total?.toLocaleString('es-CL')} 
                        <span className="ml-2">•</span> 
                        <strong className="ml-2">Margen:</strong> ${(formData.precio_ramo - (costoCalculado.total || 0)).toLocaleString('es-CL')} 
                        ({Math.round(((formData.precio_ramo - (costoCalculado.total || 0)) / (costoCalculado.total || 1)) * 100)}%)
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </form>
            
            {/* Botones - Fijos en la parte inferior */}
            <div className="flex-shrink-0 bg-white border-t border-gray-200 px-6 py-4 flex justify-end gap-3 rounded-b-lg">
              <button
                type="button"
                onClick={() => setMostrarFormulario(false)}
                className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                disabled={loadingFormulario}
              >
                Cancelar
              </button>
              <button
                type="submit"
                form="form-nuevo-pedido"
                className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
                disabled={loadingFormulario}
              >
                {loadingFormulario ? 'Creando...' : 'Crear Pedido'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default PedidosPage
