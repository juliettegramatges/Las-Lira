import { useState, useEffect } from 'react'
import { Wrench, Package, CheckCircle, AlertCircle, Edit, Image as ImageIcon, Plus, Trash2, X } from 'lucide-react'
import { pedidoInsumosAPI, inventarioAPI, productosAPI, API_URL } from '../services/api'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'

function TallerPage() {
  const [pedidos, setPedidos] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [pedidoSeleccionado, setPedidoSeleccionado] = useState(null)
  const [insumos, setInsumos] = useState([])
  const [loadingInsumos, setLoadingInsumos] = useState(false)
  const [confirmando, setConfirmando] = useState(false)
  
  // Estados para agregar insumos
  const [mostrarSelectorInsumo, setMostrarSelectorInsumo] = useState(false)
  const [flores, setFlores] = useState([])
  const [contenedores, setContenedores] = useState([])
  const [nuevoInsumo, setNuevoInsumo] = useState({
    tipo: 'Flor',
    id: '',
    cantidad: 1
  })

  useEffect(() => {
    cargarPedidosTaller()
  }, [])

  const cargarPedidosTaller = async () => {
    try {
      setLoading(true)
      const response = await pedidoInsumosAPI.obtenerPedidosTaller()
      setPedidos(response.data)
    } catch (err) {
      console.error('Error al cargar pedidos del taller:', err)
      setError('Error al cargar los pedidos')
    } finally {
      setLoading(false)
    }
  }

  const cargarInsumosDisponibles = async () => {
    try {
      const [floresRes, contenedoresRes] = await Promise.all([
        inventarioAPI.listarFlores(),
        inventarioAPI.listarContenedores()
      ])
      console.log('📦 Flores recibidas:', floresRes.data)
      console.log('📦 Contenedores recibidos:', contenedoresRes.data)
      
      // La respuesta tiene estructura {data: Array, success: true, total: N}
      const floresArray = floresRes.data.data || floresRes.data
      const contenedoresArray = contenedoresRes.data.data || contenedoresRes.data
      
      setFlores(Array.isArray(floresArray) ? floresArray : [])
      setContenedores(Array.isArray(contenedoresArray) ? contenedoresArray : [])
      
      console.log('✅ Estados actualizados - Flores:', floresArray?.length, 'Contenedores:', contenedoresArray?.length)
    } catch (err) {
      console.error('Error al cargar insumos disponibles:', err)
    }
  }

  const handleVerInsumos = async (pedido) => {
    try {
      setLoadingInsumos(true)
      setPedidoSeleccionado(pedido)

      const response = await pedidoInsumosAPI.obtenerInsumos(pedido.id)
      // Guardar cantidad original para cálculo de stock disponible
      const insumosConOriginal = (response.data.insumos || []).map(insumo => ({
        ...insumo,
        cantidad_original: insumo.cantidad  // Guardar la cantidad original reservada
      }))
      setInsumos(insumosConOriginal)

      // Cargar flores y contenedores disponibles para poder agregar
      await cargarInsumosDisponibles()
    } catch (err) {
      console.error('Error al cargar insumos:', err)
      alert('Error al cargar los insumos del pedido')
    } finally {
      setLoadingInsumos(false)
    }
  }

  const handleCantidadChange = (insumoId, nuevaCantidad) => {
    setInsumos(prevInsumos => 
      prevInsumos.map(insumo => 
        insumo.id === insumoId 
          ? { 
              ...insumo, 
              cantidad: parseInt(nuevaCantidad) || 0,
              costo_total: insumo.costo_unitario * (parseInt(nuevaCantidad) || 0)
            }
          : insumo
      )
    )
  }

  const handleAbrirModalAgregar = async () => {
    // Cargar insumos disponibles si no están cargados
    if (!flores || flores.length === 0 || !contenedores || contenedores.length === 0) {
      console.log('🔄 Cargando insumos disponibles...')
      await cargarInsumosDisponibles()
    }
    setMostrarSelectorInsumo(true)
  }

  const handleAgregarInsumo = () => {
    if (!nuevoInsumo.id || !nuevoInsumo.cantidad) {
      alert('Por favor selecciona un insumo y especifica la cantidad')
      return
    }

    const listaInsumos = nuevoInsumo.tipo === 'Flor' ? flores : contenedores
    
    // Los IDs pueden ser strings (como 'F0023') o números
    // Intentamos comparar directamente primero, luego con conversión
    let insumoSeleccionado = listaInsumos.find(i => i.id === nuevoInsumo.id)
    
    // Si no encontramos con comparación directa, intentamos con conversión a número
    if (!insumoSeleccionado && !isNaN(parseInt(nuevoInsumo.id))) {
      insumoSeleccionado = listaInsumos.find(i => i.id === parseInt(nuevoInsumo.id))
    }
    
    // Si aún no encontramos, intentamos comparar ambos como strings
    if (!insumoSeleccionado) {
      insumoSeleccionado = listaInsumos.find(i => String(i.id) === String(nuevoInsumo.id))
    }
    
    if (!insumoSeleccionado) {
      console.error('❌ No encontrado. ID buscado:', nuevoInsumo.id, 'IDs disponibles:', listaInsumos.map(i => i.id))
      alert('Insumo no encontrado')
      return
    }

    // Verificar si ya existe (comparar con el ID del insumo seleccionado)
    const yaExiste = insumos.some(i => 
      i.insumo_tipo === nuevoInsumo.tipo && 
      (nuevoInsumo.tipo === 'Flor' ? i.flor_id : i.contenedor_id) === insumoSeleccionado.id
    )
    
    if (yaExiste) {
      alert('Este insumo ya está agregado. Puedes modificar su cantidad en la lista.')
      return
    }

    // Calcular el stock realmente disponible para este pedido
    // IMPORTANTE: Usar cantidad_original (lo reservado) no cantidad (que puede estar modificada)
    const reservadoEnEstePedido = insumos
      .filter(i => i.insumo_tipo === nuevoInsumo.tipo)
      .filter(i => (nuevoInsumo.tipo === 'Flor' ? i.flor_id : i.contenedor_id) === insumoSeleccionado.id)
      .reduce((sum, i) => sum + (i.cantidad_original || i.cantidad || 0), 0)

    const stockDisponibleReal = (insumoSeleccionado.cantidad_disponible || 0) + reservadoEnEstePedido

    // Crear nuevo insumo para la lista
    const nuevoInsumoItem = {
      id: `temp-${Date.now()}`, // ID temporal para el frontend
      insumo_tipo: nuevoInsumo.tipo,
      insumo_nombre: insumoSeleccionado.nombre || insumoSeleccionado.tipo,
      insumo_color: insumoSeleccionado.color || null,
      insumo_foto: insumoSeleccionado.imagen || null,
      cantidad: parseInt(nuevoInsumo.cantidad),
      cantidad_original: parseInt(nuevoInsumo.cantidad), // Para nuevos insumos, cantidad_original = cantidad
      costo_unitario: insumoSeleccionado.costo_unitario || insumoSeleccionado.costo || 0,
      costo_total: (insumoSeleccionado.costo_unitario || insumoSeleccionado.costo || 0) * parseInt(nuevoInsumo.cantidad),
      stock_disponible: stockDisponibleReal, // Stock real incluyendo lo reservado en este pedido
      flor_id: nuevoInsumo.tipo === 'Flor' ? insumoSeleccionado.id : null,
      contenedor_id: nuevoInsumo.tipo === 'Contenedor' ? insumoSeleccionado.id : null,
      es_nuevo: true // Marcar como nuevo para el backend
    }

    setInsumos([...insumos, nuevoInsumoItem])
    setMostrarSelectorInsumo(false)
    setNuevoInsumo({ tipo: 'Flor', id: '', cantidad: 1 })
  }

  const handleEliminarInsumo = (insumoId) => {
    if (!confirm('¿Estás seguro de eliminar este insumo?')) return
    setInsumos(insumos.filter(i => i.id !== insumoId))
  }

  const handleConfirmarInsumos = async () => {
    if (!pedidoSeleccionado) return

    // Validar stock antes de confirmar
    // IMPORTANTE: Debemos considerar que los insumos YA están reservados (en cantidad_en_uso)
    // El stock disponible real = cantidad_disponible + lo reservado por ESTE pedido
    const insumosConStockActualizado = insumos.map(insumo => {
      const lista = insumo.insumo_tipo === 'Flor' ? flores : contenedores
      const insumoInventario = lista?.find(i => i.id === (insumo.flor_id || insumo.contenedor_id))

      if (insumoInventario) {
        // Calcular cuánto de este insumo está reservado en ESTE pedido
        // IMPORTANTE: Usar cantidad_original (lo reservado), no cantidad (que puede estar modificada)
        const reservadoEnEstePedido = insumos
          .filter(i => i.insumo_tipo === insumo.insumo_tipo)
          .filter(i => (i.flor_id || i.contenedor_id) === (insumo.flor_id || insumo.contenedor_id))
          .reduce((sum, i) => sum + (i.cantidad_original || i.cantidad || 0), 0)

        // Stock real disponible = lo que está libre + lo que este pedido tiene reservado
        const stockDisponibleReal = (insumoInventario.cantidad_disponible || 0) + reservadoEnEstePedido

        return {
          ...insumo,
          stock_disponible: stockDisponibleReal
        }
      }
      return insumo
    })

    const faltaStock = insumosConStockActualizado.some(i => i.cantidad > i.stock_disponible)
    if (faltaStock) {
      const detalles = insumosConStockActualizado
        .filter(i => i.cantidad > i.stock_disponible)
        .map(i => `${i.insumo_nombre}: necesita ${i.cantidad}, disponible ${i.stock_disponible}`)
        .join('\n')

      if (!confirm(`⚠️ ADVERTENCIA: Algunos insumos superan el stock disponible:\n\n${detalles}\n\n¿Deseas continuar de todos modos?`)) {
        return
      }
    }
    
    if (!confirm(`¿Confirmar insumos y descontar stock para el pedido ${pedidoSeleccionado.id}?\n\nEsto moverá el pedido a "Listo para Despacho" y descontará el inventario.`)) {
      return
    }

    try {
      setConfirmando(true)
      
      // PASO 1: Guardar los insumos actualizados (incluyendo nuevos y eliminados)
      // Filtrar insumos incompletos: requieren insumo_id y cantidad > 0
      const insumosParaGuardar = insumos
        .map(i => {
          const idSeleccionado = i.insumo_id || i.flor_id || i.contenedor_id
          return {
            insumo_tipo: i.insumo_tipo,
            insumo_id: idSeleccionado,
            cantidad: parseInt(i.cantidad) || 0,
            costo_unitario: i.costo_unitario || 0
          }
        })
        .filter(i => i.insumo_id && i.cantidad > 0)

      if (insumosParaGuardar.length === 0) {
        alert('❌ Agrega al menos un insumo válido antes de confirmar.')
        setConfirmando(false)
        return
      }
      
      await pedidoInsumosAPI.guardarInsumos(pedidoSeleccionado.id, insumosParaGuardar)
      
      // PASO 2: Confirmar y descontar stock
      const response = await pedidoInsumosAPI.confirmarYDescontar(
        pedidoSeleccionado.id,
        {}
      )
      
      alert(`✅ ${response.data.message}\n\n${response.data.insumos_procesados} insumos procesados`)
      
      // Recargar lista y cerrar modal
      await cargarPedidosTaller()
      setPedidoSeleccionado(null)
      setInsumos([])
    } catch (err) {
      console.error('Error al confirmar insumos:', err)
      const errorMsg = err.response?.data?.detalles 
        ? `❌ Error:\n\n${err.response.data.detalles.join('\n')}`
        : `❌ Error: ${err.response?.data?.error || err.message}`
      alert(errorMsg)
    } finally {
      setConfirmando(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Cargando pedidos del taller...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-red-500">{error}</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Wrench className="h-7 w-7 text-primary-600" />
            Taller
          </h1>
          <p className="text-gray-600 mt-1">
            Pedidos en proceso - Confirma insumos antes de despachar
          </p>
        </div>
        <div className="bg-primary-50 px-4 py-2 rounded-lg">
          <span className="text-primary-900 font-semibold">{pedidos.length}</span>
          <span className="text-primary-700 ml-1">en proceso</span>
        </div>
      </div>

      {/* Lista de pedidos */}
      {pedidos.length === 0 ? (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
          <Package className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 text-lg">No hay pedidos en proceso</p>
          <p className="text-gray-400 text-sm mt-2">
            Los pedidos aparecerán aquí cuando estén listos para trabajar
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {pedidos.map((pedido) => (
            <div
              key={pedido.id}
              className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow"
            >
              {/* Imagen del producto */}
              {pedido.producto_imagen && (
                <div className="h-32 bg-gradient-to-br from-primary-100 to-primary-200 flex items-center justify-center">
                  <img
                    src={pedido.producto_imagen.startsWith('http') ? pedido.producto_imagen : `${API_URL}/upload/imagen/${pedido.producto_imagen}`}
                    alt={pedido.producto_nombre}
                    className="w-full h-full object-contain p-2"
                  />
                </div>
              )}

              <div className="p-4">
                {/* Header */}
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="font-semibold text-gray-900">{pedido.cliente_nombre}</h3>
                    <p className="text-xs text-gray-500 font-mono">{pedido.id}</p>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    pedido.tiene_insumos 
                      ? 'bg-green-100 text-green-700' 
                      : 'bg-yellow-100 text-yellow-700'
                  }`}>
                    {pedido.tiene_insumos ? '✓ Con insumos' : '⚠ Sin insumos'}
                  </span>
                </div>

                {/* Producto */}
                {pedido.producto_nombre && (
                  <p className="text-sm text-gray-700 mb-2">
                    📦 {pedido.producto_nombre}
                  </p>
                )}

                {/* Fecha de entrega */}
                {pedido.fecha_entrega && (
                  <p className="text-sm text-gray-600 mb-3">
                    📅 {format(new Date(pedido.fecha_entrega), "d 'de' MMMM", { locale: es })}
                  </p>
                )}

                {/* Precio */}
                <div className="text-lg font-bold text-primary-600 mb-3">
                  ${(pedido.precio_ramo || 0).toLocaleString()}
                </div>

                {/* Botón de acción */}
                <button
                  onClick={() => handleVerInsumos(pedido)}
                  className="w-full bg-primary-600 text-white py-2 px-4 rounded-lg hover:bg-primary-700 transition-colors flex items-center justify-center gap-2"
                >
                  <Edit className="h-4 w-4" />
                  {pedido.tiene_insumos ? 'Ver/Confirmar Insumos' : 'Definir Insumos'}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal de insumos */}
      {pedidoSeleccionado && (
        <div
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
          onClick={() => setPedidoSeleccionado(null)}
        >
          <div
            className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="bg-primary-600 text-white px-6 py-4">
              <h2 className="text-xl font-bold">
                Insumos - {pedidoSeleccionado.producto_nombre || pedidoSeleccionado.cliente_nombre}
              </h2>
              <p className="text-primary-100 text-sm">{pedidoSeleccionado.id}</p>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-6">
              {loadingInsumos ? (
                <div className="text-center py-12">
                  <div className="text-gray-500">Cargando insumos...</div>
                </div>
              ) : (
                <div className="space-y-6">
                  {/* Botón para agregar insumo - SIEMPRE VISIBLE */}
                  <div className="flex justify-end">
                    <button
                      onClick={handleAbrirModalAgregar}
                      className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                    >
                      <Plus className="h-4 w-4" />
                      Agregar Insumo
                    </button>
                  </div>

                  {insumos.length === 0 ? (
                    <div className="text-center py-12">
                      <AlertCircle className="h-16 w-16 text-yellow-400 mx-auto mb-4" />
                      <p className="text-gray-600">Este pedido aún no tiene insumos definidos</p>
                      <p className="text-gray-400 text-sm mt-2">
                        Usa el botón "Agregar Insumo" para comenzar
                      </p>
                    </div>
                  ) : (
                    <>
                      {/* Tabla de insumos */}
                      <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                            Insumo
                          </th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                            Tipo
                          </th>
                          <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                            Cantidad
                          </th>
                          <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                            Stock Disp.
                          </th>
                          <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                            Costo Unit.
                          </th>
                          <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                            Total
                          </th>
                          <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                            Acciones
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {insumos.map((insumo) => {
                          // Calcular el stock real disponible (incluyendo lo reservado para este pedido)
                          const lista = insumo.insumo_tipo === 'Flor' ? flores : contenedores
                          const insumoInventario = lista?.find(i => i.id === (insumo.flor_id || insumo.contenedor_id))

                          // Calcular cuánto de este insumo está reservado en ESTE pedido
                          // IMPORTANTE: Usar cantidad_original, no cantidad (que puede estar modificada)
                          const reservadoEnEstePedido = insumos
                            .filter(i => i.insumo_tipo === insumo.insumo_tipo)
                            .filter(i => (i.flor_id || i.contenedor_id) === (insumo.flor_id || insumo.contenedor_id))
                            .reduce((sum, i) => sum + (i.cantidad_original || i.cantidad || 0), 0)

                          // Stock real = disponible en inventario + lo que ya tenemos reservado
                          const stockDisponibleReal = insumoInventario
                            ? (insumoInventario.cantidad_disponible || 0) + reservadoEnEstePedido
                            : (insumo.stock_disponible || 0)

                          const stockSuficiente = stockDisponibleReal >= insumo.cantidad
                          
                          return (
                            <tr key={insumo.id} className={!stockSuficiente ? 'bg-red-50' : ''}>
                              <td className="px-4 py-3">
                                <div className="flex items-center gap-2">
                                  {insumo.insumo_foto ? (
                                    <img
                                      src={`${API_URL}/upload/imagen/${insumo.insumo_foto}`}
                                      alt={insumo.insumo_nombre}
                                      className="w-10 h-10 rounded object-cover"
                                      onError={(e) => {
                                        e.target.style.display = 'none'
                                      }}
                                    />
                                  ) : (
                                    <div className="w-10 h-10 bg-gray-200 rounded flex items-center justify-center">
                                      <ImageIcon className="h-5 w-5 text-gray-400" />
                                    </div>
                                  )}
                                  <div>
                                    <div className="font-medium text-gray-900">
                                      {insumo.insumo_nombre}
                                    </div>
                                    {insumo.insumo_color && (
                                      <div className="text-xs text-gray-500">{insumo.insumo_color}</div>
                                    )}
                                  </div>
                                </div>
                              </td>
                              <td className="px-4 py-3">
                                <span className={`px-2 py-1 rounded text-xs font-medium ${
                                  insumo.insumo_tipo === 'Flor' 
                                    ? 'bg-green-100 text-green-700' 
                                    : 'bg-blue-100 text-blue-700'
                                }`}>
                                  {insumo.insumo_tipo}
                                </span>
                              </td>
                              <td className="px-4 py-3">
                                <input
                                  type="number"
                                  min="0"
                                  value={insumo.cantidad}
                                  onChange={(e) => handleCantidadChange(insumo.id, e.target.value)}
                                  className="w-20 px-2 py-1 border border-gray-300 rounded text-right font-medium focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                                />
                              </td>
                              <td className={`px-4 py-3 text-right ${!stockSuficiente ? 'text-red-600 font-bold' : 'text-gray-600'}`}>
                                {stockDisponibleReal}
                                {reservadoEnEstePedido > 0 && insumoInventario && (
                                  <span className="text-xs text-blue-600 block">
                                    ({insumoInventario.cantidad_disponible} + {reservadoEnEstePedido})
                                  </span>
                                )}
                                {!stockSuficiente && ' ⚠️'}
                              </td>
                              <td className="px-4 py-3 text-right text-gray-600">
                                ${insumo.costo_unitario.toLocaleString()}
                              </td>
                              <td className="px-4 py-3 text-right font-medium text-gray-900">
                                ${insumo.costo_total.toLocaleString()}
                              </td>
                              <td className="px-4 py-3 text-center">
                                <button
                                  onClick={() => handleEliminarInsumo(insumo.id)}
                                  className="p-1.5 rounded-lg hover:bg-red-50 text-red-600 hover:text-red-700 transition-all duration-200"
                                  title="Eliminar insumo"
                                >
                                  <Trash2 className="h-4 w-4" />
                                </button>
                              </td>
                            </tr>
                          )
                        })}
                      </tbody>
                      <tfoot className="bg-gray-50">
                        <tr>
                          <td colSpan="5" className="px-4 py-3 text-right font-semibold text-gray-700">
                            Total Insumos:
                          </td>
                          <td className="px-4 py-3 text-right font-bold text-primary-600 text-lg">
                            ${insumos.reduce((sum, i) => sum + i.costo_total, 0).toLocaleString()}
                          </td>
                          <td></td>
                        </tr>
                      </tfoot>
                    </table>
                  </div>

                  {/* Alertas */}
                  {(() => {
                    // Calcular si hay stock insuficiente considerando lo reservado por ESTE pedido
                    const hayStockInsuficiente = insumos.some(insumo => {
                      const lista = insumo.insumo_tipo === 'Flor' ? flores : contenedores
                      const insumoInventario = lista?.find(i => i.id === (insumo.flor_id || insumo.contenedor_id))

                      // Usar cantidad_original (lo que está reservado) no cantidad (que puede estar modificada)
                      const reservadoEnEstePedido = insumos
                        .filter(i => i.insumo_tipo === insumo.insumo_tipo)
                        .filter(i => (i.flor_id || i.contenedor_id) === (insumo.flor_id || insumo.contenedor_id))
                        .reduce((sum, i) => sum + (i.cantidad_original || i.cantidad || 0), 0)

                      const stockDisponibleReal = insumoInventario
                        ? (insumoInventario.cantidad_disponible || 0) + reservadoEnEstePedido
                        : (insumo.stock_disponible || 0)

                      return insumo.cantidad > stockDisponibleReal
                    })

                    return hayStockInsuficiente && (
                      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                        <div className="flex items-start gap-3">
                          <AlertCircle className="h-5 w-5 text-red-600 mt-0.5" />
                          <div>
                            <h3 className="font-semibold text-red-900">Stock insuficiente</h3>
                            <p className="text-red-700 text-sm mt-1">
                              Algunos insumos no tienen stock suficiente. Debes reponer inventario antes de confirmar este pedido.
                            </p>
                          </div>
                        </div>
                      </div>
                    )
                  })()}
                </>
              )}
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="border-t border-gray-200 px-6 py-4 bg-gray-50 flex justify-end gap-3">
              <button
                onClick={() => setPedidoSeleccionado(null)}
                className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors"
              >
                Cerrar
              </button>
              {insumos.length > 0 && (
                <button
                  onClick={handleConfirmarInsumos}
                  disabled={confirmando || (() => {
                    // Validar considerando lo reservado por ESTE pedido
                    return insumos.some(insumo => {
                      const lista = insumo.insumo_tipo === 'Flor' ? flores : contenedores
                      const insumoInventario = lista?.find(i => i.id === (insumo.flor_id || insumo.contenedor_id))

                      // Usar cantidad_original (lo que está reservado) no cantidad (que puede estar modificada)
                      const reservadoEnEstePedido = insumos
                        .filter(i => i.insumo_tipo === insumo.insumo_tipo)
                        .filter(i => (i.flor_id || i.contenedor_id) === (insumo.flor_id || insumo.contenedor_id))
                        .reduce((sum, i) => sum + (i.cantidad_original || i.cantidad || 0), 0)

                      const stockDisponibleReal = insumoInventario
                        ? (insumoInventario.cantidad_disponible || 0) + reservadoEnEstePedido
                        : (insumo.stock_disponible || 0)

                      return insumo.cantidad > stockDisponibleReal
                    })
                  })()}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  <CheckCircle className="h-4 w-4" />
                  {confirmando ? 'Confirmando...' : 'Confirmar y Descontar Stock'}
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Modal para agregar insumo */}
      {mostrarSelectorInsumo && (
        <div
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-[60] p-4"
          onClick={() => setMostrarSelectorInsumo(false)}
        >
          <div
            className="bg-white rounded-lg shadow-xl max-w-md w-full"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="bg-primary-600 text-white px-6 py-4 flex items-center justify-between rounded-t-lg">
              <h3 className="text-lg font-bold">Agregar Insumo</h3>
              <button
                onClick={() => setMostrarSelectorInsumo(false)}
                className="p-1 hover:bg-primary-700 rounded transition-colors"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Content */}
            <div className="p-6 space-y-4">
              {/* Tipo de insumo */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tipo de Insumo
                </label>
                <select
                  value={nuevoInsumo.tipo}
                  onChange={(e) => setNuevoInsumo({ ...nuevoInsumo, tipo: e.target.value, id: '' })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="Flor">Flor / Follaje</option>
                  <option value="Contenedor">Contenedor</option>
                </select>
              </div>

              {/* Selector de insumo */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {nuevoInsumo.tipo === 'Flor' ? 'Flor / Follaje' : 'Contenedor'}
                </label>
                <select
                  value={nuevoInsumo.id}
                  onChange={(e) => setNuevoInsumo({ ...nuevoInsumo, id: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="">Seleccionar...</option>
                  {(() => {
                    const lista = nuevoInsumo.tipo === 'Flor' ? flores : contenedores
                    const listaSegura = Array.isArray(lista) ? lista : []
                    
                    return listaSegura.map((insumo) => {
                      // Calcular cuánto de este insumo ya está reservado en ESTE pedido
                      // IMPORTANTE: Usar cantidad_original (lo reservado) no cantidad (que puede estar modificada)
                      const reservadoEnEstePedido = insumos
                        .filter(i => i.insumo_tipo === nuevoInsumo.tipo)
                        .filter(i => (nuevoInsumo.tipo === 'Flor' ? i.flor_id : i.contenedor_id) === insumo.id)
                        .reduce((sum, i) => sum + (i.cantidad_original || i.cantidad || 0), 0)

                      // El stock "realmente disponible" incluye lo que ya tenemos reservado
                      const stockDisponibleReal = (insumo.cantidad_disponible || 0) + reservadoEnEstePedido
                      
                      const stockInfo = reservadoEnEstePedido > 0
                        ? `Stock: ${insumo.cantidad_disponible || 0} + ${reservadoEnEstePedido} en pedido = ${stockDisponibleReal}`
                        : `Stock: ${insumo.cantidad_disponible || 0}`
                      
                      return (
                        <option key={insumo.id} value={insumo.id}>
                          {insumo.nombre || insumo.tipo}
                          {insumo.color && ` - ${insumo.color}`}
                          {' '}
                          ({stockInfo})
                        </option>
                      )
                    })
                  })()}
                </select>
              </div>

              {/* Cantidad */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Cantidad
                </label>
                <input
                  type="number"
                  min="1"
                  value={nuevoInsumo.cantidad}
                  onChange={(e) => setNuevoInsumo({ ...nuevoInsumo, cantidad: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
            </div>

            {/* Footer */}
            <div className="border-t border-gray-200 px-6 py-4 bg-gray-50 flex justify-end gap-3 rounded-b-lg">
              <button
                onClick={() => setMostrarSelectorInsumo(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={handleAgregarInsumo}
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors flex items-center gap-2"
              >
                <Plus className="h-4 w-4" />
                Agregar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default TallerPage

