import { useState, useEffect } from 'react'
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area
} from 'recharts'
import {
  TrendingUp, TrendingDown, DollarSign, ShoppingBag, Users, Clock,
  Calendar, MapPin, Award, Package, Tag, CreditCard, Smartphone
} from 'lucide-react'
import axios from 'axios'
import { API_URL } from '../services/api'

const COLORS = ['#EC4899', '#8B5CF6', '#3B82F6', '#10B981', '#F59E0B', '#EF4444']

// Función helper para generar opciones de años dinámicamente
const generarOpcionesAnios = () => {
  const añoActual = new Date().getFullYear()
  const años = []
  // Desde 2022 hasta 2 años en el futuro
  for (let año = 2022; año <= añoActual + 2; año++) {
    años.push(año)
  }
  return años
}

const AÑOS_DISPONIBLES = generarOpcionesAnios()

const MESES = [
  { valor: 1, nombre: 'Enero' },
  { valor: 2, nombre: 'Febrero' },
  { valor: 3, nombre: 'Marzo' },
  { valor: 4, nombre: 'Abril' },
  { valor: 5, nombre: 'Mayo' },
  { valor: 6, nombre: 'Junio' },
  { valor: 7, nombre: 'Julio' },
  { valor: 8, nombre: 'Agosto' },
  { valor: 9, nombre: 'Septiembre' },
  { valor: 10, nombre: 'Octubre' },
  { valor: 11, nombre: 'Noviembre' },
  { valor: 12, nombre: 'Diciembre' }
]

function ReportesPage() {
  const [loading, setLoading] = useState(true)
  const [kpis, setKpis] = useState({})
  const [ventasMensuales, setVentasMensuales] = useState([])
  const [topProductos, setTopProductos] = useState([])
  const [distribucionTipos, setDistribucionTipos] = useState([])
  const [topClientes, setTopClientes] = useState([])
  const [distribucionClientes, setDistribucionClientes] = useState([])
  const [comunasFrecuentes, setComunasFrecuentes] = useState([])
  const [analisisEventos, setAnalisisEventos] = useState({})
  const [analisisCobranza, setAnalisisCobranza] = useState([])
  const [ventasDiaSemana, setVentasDiaSemana] = useState([])
  const [canalesVenta, setCanalesVenta] = useState([])

  // Filtros para ventas por día de semana
  const fechaActual = new Date()
  const [mesDiaSemana, setMesDiaSemana] = useState(fechaActual.getMonth() + 1)
  const [añoDiaSemana, setAñoDiaSemana] = useState(fechaActual.getFullYear())

  // Filtros para top productos
  const [mesTopProductos, setMesTopProductos] = useState(null) // null = todos los meses
  const [añoTopProductos, setAñoTopProductos] = useState(null) // null = todos los años

  // Estados y filtros para personalizaciones
  const [analisisPersonalizaciones, setAnalisisPersonalizaciones] = useState(null)
  const [mesPersonalizaciones, setMesPersonalizaciones] = useState(null)
  const [añoPersonalizaciones, setAñoPersonalizaciones] = useState(null)

  // Estados y filtros para arreglos por motivo (general)
  const [arreglosPorMotivo, setArreglosPorMotivo] = useState([])
  const [mesArreglosMotivo, setMesArreglosMotivo] = useState(null)
  const [añoArreglosMotivo, setAñoArreglosMotivo] = useState(null)

  // Estados y filtros para anticipación de pedidos
  const [anticipacionPedidos, setAnticipacionPedidos] = useState(null)
  const [mesAnticipacion, setMesAnticipacion] = useState(null)
  const [añoAnticipacion, setAñoAnticipacion] = useState(null)

  // Estados y filtros para colores frecuentes
  const [coloresFrecuentes, setColoresFrecuentes] = useState([])
  const [mesColores, setMesColores] = useState(null)
  const [añoColores, setAñoColores] = useState(null)

  // Filtro para distribución de clientes
  const [añoDistribucionClientes, setAñoDistribucionClientes] = useState(null)

  useEffect(() => {
    cargarDatos()
  }, [])

  useEffect(() => {
    cargarDistribucionClientes()
  }, [añoDistribucionClientes])
  
  useEffect(() => {
    cargarVentasDiaSemana()
  }, [mesDiaSemana, añoDiaSemana])
  
  useEffect(() => {
    cargarTopProductos()
  }, [mesTopProductos, añoTopProductos])
  
  useEffect(() => {
    cargarPersonalizaciones()
  }, [mesPersonalizaciones, añoPersonalizaciones])
  
  useEffect(() => {
    cargarArreglosPorMotivo()
  }, [mesArreglosMotivo, añoArreglosMotivo])
  
  useEffect(() => {
    cargarAnticipacionPedidos()
  }, [mesAnticipacion, añoAnticipacion])
  
  useEffect(() => {
    cargarColoresFrecuentes()
  }, [mesColores, añoColores])

  const cargarDatos = async () => {
    try {
      setLoading(true)
      
      // Cargar todos los datos en paralelo (excepto ventasDiaSemana, topProductos y distribucionClientes que se cargan separadamente)
      const [
        resKpis,
        resVentas,
        resTipos,
        resClientes,
        resComunas,
        resEventos,
        resCobranza,
        resCanales
      ] = await Promise.all([
        axios.get(`${API_URL}/reportes/kpis`),
        axios.get(`${API_URL}/reportes/ventas-mensuales`),
        axios.get(`${API_URL}/reportes/distribucion-tipos`),
        axios.get(`${API_URL}/reportes/top-clientes?limit=10`),
        axios.get(`${API_URL}/reportes/comunas-frecuentes?limit=15`),
        axios.get(`${API_URL}/reportes/analisis-eventos`),
        axios.get(`${API_URL}/reportes/analisis-cobranza`),
        axios.get(`${API_URL}/reportes/canales-venta`)
      ])

      if (resKpis.data.success) setKpis(resKpis.data.data)
      if (resVentas.data.success) setVentasMensuales(resVentas.data.data)
      if (resTipos.data.success) setDistribucionTipos(resTipos.data.data)
      if (resClientes.data.success) setTopClientes(resClientes.data.data)
      // Distribución de clientes se carga en useEffect separado con filtro de año
      if (resComunas.data.success) setComunasFrecuentes(resComunas.data.data)
      if (resEventos.data.success) setAnalisisEventos(resEventos.data.data)
      if (resCobranza.data.success) setAnalisisCobranza(resCobranza.data.data)
      if (resCanales.data.success) setCanalesVenta(resCanales.data.data)
      
    } catch (error) {
      console.error('Error al cargar datos:', error)
      alert('Error al cargar los reportes')
    } finally {
      setLoading(false)
    }
  }
  
  const cargarVentasDiaSemana = async () => {
    try {
      const response = await axios.get(
        `${API_URL}/reportes/ventas-dia-semana?año=${añoDiaSemana}&mes=${mesDiaSemana}`
      )
      if (response.data.success) {
        setVentasDiaSemana(response.data.data)
      }
    } catch (error) {
      console.error('Error al cargar ventas por día:', error)
    }
  }
  
  const cargarTopProductos = async () => {
    try {
      let url = `${API_URL}/reportes/top-productos?limit=10`
      if (añoTopProductos && mesTopProductos) {
        url += `&anio=${añoTopProductos}&mes=${mesTopProductos}`
      }
      
      const response = await axios.get(url)
      if (response.data.success) {
        setTopProductos(response.data.data)
      }
    } catch (error) {
      console.error('Error al cargar top productos:', error)
    }
  }
  
  const cargarPersonalizaciones = async () => {
    try {
      let url = `${API_URL}/reportes/analisis-personalizaciones`
      if (añoPersonalizaciones && mesPersonalizaciones) {
        url += `?anio=${añoPersonalizaciones}&mes=${mesPersonalizaciones}`
      }
      
      const response = await axios.get(url)
      if (response.data.success) {
        setAnalisisPersonalizaciones(response.data.data)
      }
    } catch (error) {
      console.error('Error al cargar análisis de personalizaciones:', error)
    }
  }
  
  const cargarArreglosPorMotivo = async () => {
    try {
      let url = `${API_URL}/reportes/arreglos-por-motivo`
      const params = []
      if (añoArreglosMotivo) params.push(`anio=${añoArreglosMotivo}`)
      if (mesArreglosMotivo) params.push(`mes=${mesArreglosMotivo}`)
      if (params.length > 0) url += `?${params.join('&')}`
      
      const response = await axios.get(url)
      if (response.data.success) {
        setArreglosPorMotivo(response.data.data)
      }
    } catch (error) {
      console.error('Error al cargar arreglos por motivo:', error)
    }
  }
  
  const cargarAnticipacionPedidos = async () => {
    try {
      let url = `${API_URL}/reportes/anticipacion-pedidos`
      const params = []
      if (añoAnticipacion) params.push(`anio=${añoAnticipacion}`)
      if (mesAnticipacion) params.push(`mes=${mesAnticipacion}`)
      if (params.length > 0) url += `?${params.join('&')}`
      
      const response = await axios.get(url)
      if (response.data.success) {
        setAnticipacionPedidos(response.data.data)
      }
    } catch (error) {
      console.error('Error al cargar anticipación de pedidos:', error)
    }
  }
  
  const cargarDistribucionClientes = async () => {
    try {
      const url = `${API_URL}/reportes/distribucion-clientes${añoDistribucionClientes ? `?año=${añoDistribucionClientes}` : ''}`
      const response = await axios.get(url)
      if (response.data.success) {
        setDistribucionClientes(response.data.data)
      }
    } catch (error) {
      console.error('Error al cargar distribución de clientes:', error)
    }
  }

  const cargarColoresFrecuentes = async () => {
    try {
      let url = `${API_URL}/reportes/colores-frecuentes`
      const params = []
      if (añoColores) params.push(`anio=${añoColores}`)
      if (mesColores) params.push(`mes=${mesColores}`)
      if (params.length > 0) url += `?${params.join('&')}`
      
      const response = await axios.get(url)
      if (response.data.success) {
        setColoresFrecuentes(response.data.data)
      }
    } catch (error) {
      console.error('Error al cargar colores frecuentes:', error)
    }
  }

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP',
      minimumFractionDigits: 0
    }).format(value)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-pink-600 mb-4"></div>
          <p className="text-gray-600">Cargando reportes...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="mb-8 bg-gradient-to-r from-pink-600 to-purple-600 rounded-2xl shadow-xl p-8 text-white">
        <h1 className="text-4xl font-bold mb-2 flex items-center gap-3">
          <TrendingUp className="h-10 w-10" />
          Reportes & Analytics
        </h1>
        <p className="text-pink-100 text-lg">Dashboard ejecutivo de rendimiento - Análisis en tiempo real</p>
        <p className="text-pink-200 text-sm mt-2">Última actualización: {new Date().toLocaleString('es-CL')}</p>
      </div>

      {/* KPIs Principales */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Ventas del mes */}
        <div className="bg-gradient-to-br from-pink-500 to-rose-500 rounded-xl p-6 text-white shadow-lg hover:shadow-xl transition-shadow">
          <div className="flex items-center justify-between mb-4">
            <DollarSign className="h-10 w-10 opacity-80" />
            <span className={`flex items-center text-sm ${kpis.crecimiento_ventas >= 0 ? 'bg-white/20' : 'bg-black/20'} px-2 py-1 rounded-full`}>
              {kpis.crecimiento_ventas >= 0 ? <TrendingUp className="h-4 w-4 mr-1" /> : <TrendingDown className="h-4 w-4 mr-1" />}
              {Math.abs(kpis.crecimiento_ventas || 0).toFixed(1)}%
            </span>
          </div>
          <p className="text-sm opacity-90 mb-1">Ventas del Mes</p>
          <p className="text-3xl font-bold">{formatCurrency(kpis.ventas_mes || 0)}</p>
          <p className="text-xs opacity-75 mt-2">vs {formatCurrency(kpis.ventas_mes_anterior || 0)} mes anterior</p>
        </div>

        {/* Pedidos del mes */}
        <div className="bg-gradient-to-br from-blue-500 to-indigo-500 rounded-xl p-6 text-white shadow-lg hover:shadow-xl transition-shadow">
          <div className="flex items-center justify-between mb-4">
            <ShoppingBag className="h-10 w-10 opacity-80" />
            <span className="text-sm bg-white/20 px-2 py-1 rounded-full">
              {kpis.pedidos_mes || 0} pedidos
            </span>
          </div>
          <p className="text-sm opacity-90 mb-1">Pedidos del Mes</p>
          <p className="text-3xl font-bold">{kpis.pedidos_mes || 0}</p>
          <p className="text-xs opacity-75 mt-2">vs {kpis.pedidos_mes_anterior || 0} mes anterior</p>
        </div>

        {/* Ticket promedio */}
        <div className="bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl p-6 text-white shadow-lg hover:shadow-xl transition-shadow">
          <div className="flex items-center justify-between mb-4">
            <Tag className="h-10 w-10 opacity-80" />
            <Award className="h-6 w-6 opacity-60" />
          </div>
          <p className="text-sm opacity-90 mb-1">Ticket Promedio</p>
          <p className="text-3xl font-bold">{formatCurrency(kpis.ticket_promedio || 0)}</p>
          <p className="text-xs opacity-75 mt-2">Por pedido</p>
        </div>

        {/* Clientes nuevos del mes */}
        <div className="bg-gradient-to-br from-green-500 to-emerald-500 rounded-xl p-6 text-white shadow-lg hover:shadow-xl transition-shadow">
          <div className="flex items-center justify-between mb-4">
            <Users className="h-10 w-10 opacity-80" />
            <span className={`flex items-center text-sm ${kpis.crecimiento_clientes >= 0 ? 'bg-white/20' : 'bg-black/20'} px-2 py-1 rounded-full`}>
              {kpis.crecimiento_clientes >= 0 ? <TrendingUp className="h-4 w-4 mr-1" /> : <TrendingDown className="h-4 w-4 mr-1" />}
              {Math.abs(kpis.crecimiento_clientes || 0).toFixed(1)}%
            </span>
          </div>
          <p className="text-sm opacity-90 mb-1">Clientes Nuevos del Mes</p>
          <p className="text-3xl font-bold">{kpis.clientes_nuevos_mes || 0}</p>
          <p className="text-xs opacity-75 mt-2">vs {kpis.clientes_nuevos_mes_anterior || 0} mes anterior • {kpis.tasa_entrega?.toFixed(1) || 0}% entrega a tiempo</p>
        </div>
      </div>

      {/* ==== SECCIÓN: VENTAS & RENDIMIENTO ==== */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="h-1 flex-1 bg-gradient-to-r from-pink-500 to-purple-500 rounded"></div>
          <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
            <TrendingUp className="h-7 w-7 text-pink-600" />
            Ventas & Rendimiento
          </h2>
          <div className="h-1 flex-1 bg-gradient-to-r from-purple-500 to-pink-500 rounded"></div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
        <h3 className="text-lg font-semibold text-gray-700 mb-6">Análisis de Ventas Mensuales</h3>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Ventas mensuales */}
          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-4">Ventas Mensuales (Últimos 12 meses)</h3>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={ventasMensuales}>
                <defs>
                  <linearGradient id="colorVentas" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#EC4899" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#EC4899" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="nombre" style={{ fontSize: '12px' }} />
                <YAxis style={{ fontSize: '12px' }} />
                <Tooltip 
                  formatter={(value) => formatCurrency(value)}
                  labelStyle={{ color: '#000' }}
                />
                <Area type="monotone" dataKey="ventas" stroke="#EC4899" fillOpacity={1} fill="url(#colorVentas)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Ventas por día de semana */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold text-gray-700">Ventas por Día de la Semana (Fecha de Entrega)</h3>
              <div className="flex items-center gap-2">
                <select
                  value={mesDiaSemana}
                  onChange={(e) => setMesDiaSemana(parseInt(e.target.value))}
                  className="text-xs border border-gray-300 rounded-md px-2 py-1 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                >
                  {MESES.map(mes => (
                    <option key={mes.valor} value={mes.valor}>{mes.nombre}</option>
                  ))}
                </select>
                <select
                  value={añoDiaSemana}
                  onChange={(e) => setAñoDiaSemana(parseInt(e.target.value))}
                  className="text-xs border border-gray-300 rounded-md px-2 py-1 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                >
                  {AÑOS_DISPONIBLES.map(año => (
                    <option key={año} value={año}>{año}</option>
                  ))}
                </select>
              </div>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={ventasDiaSemana}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="dia" style={{ fontSize: '12px' }} />
                <YAxis style={{ fontSize: '12px' }} />
                <Tooltip 
                  formatter={(value, name) => [
                    name === 'ventas' ? formatCurrency(value) : value,
                    name === 'ventas' ? 'Ventas' : 'Pedidos'
                  ]}
                  labelStyle={{ color: '#000' }}
                />
                <Legend />
                <Bar dataKey="ventas" fill="#8B5CF6" name="Ventas" />
                <Bar dataKey="cantidad" fill="#3B82F6" name="Pedidos" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* ==== SECCIÓN: PRODUCTOS & CLIENTES ==== */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="h-1 flex-1 bg-gradient-to-r from-blue-500 to-indigo-500 rounded"></div>
          <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
            <Package className="h-7 w-7 text-blue-600" />
            Productos & Clientes
          </h2>
          <div className="h-1 flex-1 bg-gradient-to-r from-indigo-500 to-blue-500 rounded"></div>
        </div>
      </div>

      {/* Grid de 2 columnas */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Top Productos */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-900 flex items-center">
              <Package className="h-6 w-6 text-pink-500 mr-2" />
              Top 10 Productos
            </h2>
            <div className="flex items-center gap-2">
              <select
                value={mesTopProductos || ''}
                onChange={(e) => setMesTopProductos(e.target.value ? parseInt(e.target.value) : null)}
                className="text-xs border border-gray-300 rounded-md px-2 py-1 focus:ring-2 focus:ring-pink-500 focus:border-pink-500"
              >
                <option value="">Todos los meses</option>
                {MESES.map(mes => (
                  <option key={mes.valor} value={mes.valor}>{mes.nombre}</option>
                ))}
              </select>
              <select
                value={añoTopProductos || ''}
                onChange={(e) => setAñoTopProductos(e.target.value ? parseInt(e.target.value) : null)}
                className="text-xs border border-gray-300 rounded-md px-2 py-1 focus:ring-2 focus:ring-pink-500 focus:border-pink-500"
              >
                <option value="">Todos los años</option>
                {AÑOS_DISPONIBLES.map(año => (
                  <option key={año} value={año}>{año}</option>
                ))}
              </select>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={topProductos} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" style={{ fontSize: '12px' }} />
              <YAxis dataKey="producto" type="category" width={150} style={{ fontSize: '11px' }} />
              <Tooltip 
                formatter={(value, name) => [
                  name === 'ventas' ? formatCurrency(value) : value,
                  name === 'ventas' ? 'Ventas' : 'Cantidad'
                ]}
                labelStyle={{ color: '#000' }}
              />
              <Legend />
              <Bar dataKey="cantidad" fill="#EC4899" name="Cantidad" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Distribución por tipo */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
            <Tag className="h-6 w-6 text-purple-500 mr-2" />
            Distribución por Tipo de Arreglo
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={distribucionTipos}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ tipo, percent }) => {
                  // Solo mostrar etiqueta si el porcentaje es >= 5%
                  if (percent * 100 < 5) return '';
                  return `${(percent * 100).toFixed(0)}%`;
                }}
                outerRadius={110}
                fill="#8884d8"
                dataKey="cantidad"
              >
                {distribucionTipos.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                formatter={(value, name, props) => [value, props.payload.tipo]}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="mt-4 space-y-2">
            {distribucionTipos.map((item, index) => (
              <div key={index} className="flex items-center justify-between text-sm">
                <div className="flex items-center">
                  <div className="w-3 h-3 rounded-full mr-2" style={{ backgroundColor: COLORS[index % COLORS.length] }}></div>
                  <span className="text-gray-700">{item.tipo}</span>
                </div>
                <span className="font-semibold text-gray-900">{item.cantidad}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Top Clientes */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
        <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
          <Award className="h-6 w-6 text-yellow-500 mr-2" />
          Top 10 Clientes VIP
        </h2>
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Ranking</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Cliente</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Tipo</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600 uppercase">Pedidos</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600 uppercase">Total Gastado</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {topClientes.map((cliente, index) => (
                <tr key={cliente.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-white ${
                      index === 0 ? 'bg-yellow-500' : index === 1 ? 'bg-gray-400' : index === 2 ? 'bg-orange-600' : 'bg-gray-300'
                    }`}>
                      {index + 1}
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center">
                      <div className="h-10 w-10 rounded-full bg-pink-100 flex items-center justify-center text-pink-600 font-semibold mr-3">
                        {cliente.nombre.charAt(0)}
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">{cliente.nombre}</p>
                        <p className="text-xs text-gray-500">{cliente.id}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 text-xs rounded-full font-semibold ${
                      cliente.tipo_cliente === 'VIP' ? 'bg-purple-100 text-purple-700' :
                      cliente.tipo_cliente === 'Fiel' ? 'bg-blue-100 text-blue-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {cliente.tipo_cliente}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right font-medium">{cliente.total_pedidos}</td>
                  <td className="px-4 py-3 text-right font-bold text-green-600">
                    {formatCurrency(cliente.total_gastado)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Grid de 3 columnas */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
        {/* Distribución de clientes */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-gray-900 flex items-center">
              <Users className="h-5 w-5 text-indigo-500 mr-2" />
              Distribución Clientes
            </h3>
            <select
              value={añoDistribucionClientes || ''}
              onChange={(e) => setAñoDistribucionClientes(e.target.value ? parseInt(e.target.value) : null)}
              className="text-xs border border-indigo-300 rounded-md px-2 py-1 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="">Todos los años</option>
              {AÑOS_DISPONIBLES.map(año => (
                <option key={año} value={año}>{año}</option>
              ))}
            </select>
          </div>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={distribucionClientes}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={90}
                fill="#8884d8"
                paddingAngle={5}
                dataKey="cantidad"
              >
                {distribucionClientes.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
          <div className="mt-4 space-y-2">
            {distribucionClientes.map((item, index) => (
              <div key={index} className="flex items-center justify-between text-sm">
                <div className="flex items-center">
                  <div className="w-3 h-3 rounded-full mr-2" style={{ backgroundColor: COLORS[index % COLORS.length] }}></div>
                  <span className="text-gray-700">{item.tipo}</span>
                </div>
                <span className="font-semibold text-gray-900">{item.cantidad}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Análisis de Eventos */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
            <Calendar className="h-5 w-5 text-purple-500 mr-2" />
            Análisis de Eventos
          </h3>
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">Eventos</span>
              <span className="text-2xl font-bold text-purple-600">{analisisEventos.pedidos_eventos || 0}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-purple-500 h-2 rounded-full transition-all"
                style={{ width: `${analisisEventos.porcentaje_eventos || 0}%` }}
              ></div>
            </div>
            <p className="text-xs text-gray-500 mt-1">{(analisisEventos.porcentaje_eventos || 0).toFixed(1)}% del total</p>
          </div>
          
          <div className="space-y-3 mt-6">
            {analisisEventos.tipos_evento?.map((tipo, index) => (
              <div key={index} className="border-l-4 border-pink-500 pl-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700">{tipo.tipo}</span>
                  <span className="text-sm font-bold text-gray-900">{tipo.cantidad}</span>
                </div>
                <p className="text-xs text-gray-500">{formatCurrency(tipo.ventas)}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Estado de Cobranza */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
            <CreditCard className="h-5 w-5 text-green-500 mr-2" />
            Estado de Cobranza
          </h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={analisisCobranza}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ estado, percent }) => `${(percent * 100).toFixed(0)}%`}
                outerRadius={90}
                fill="#8884d8"
                dataKey="cantidad"
              >
                {analisisCobranza.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={
                    entry.estado === 'Pagado' ? '#10B981' :
                    entry.estado === 'Pendiente' ? '#F59E0B' :
                    '#EF4444'
                  } />
                ))}
              </Pie>
              <Tooltip 
                formatter={(value, name, props) => [
                  formatCurrency(props.payload.monto),
                  `${value} pedidos`
                ]}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="mt-4 space-y-2">
            {analisisCobranza.map((item, index) => (
              <div key={index} className="flex items-center justify-between text-sm">
                <div className="flex items-center">
                  <div className={`w-3 h-3 rounded-full mr-2 ${
                    item.estado === 'Pagado' ? 'bg-green-500' :
                    item.estado === 'Pendiente' ? 'bg-yellow-500' :
                    'bg-red-500'
                  }`}></div>
                  <span className="text-gray-700">{item.estado}</span>
                </div>
                <span className="font-semibold text-gray-900">{formatCurrency(item.monto)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ==== SECCIÓN: ANÁLISIS GEOGRÁFICO & CANALES ==== */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="h-1 flex-1 bg-gradient-to-r from-green-500 to-teal-500 rounded"></div>
          <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
            <MapPin className="h-7 w-7 text-green-600" />
            Análisis Geográfico & Canales
          </h2>
          <div className="h-1 flex-1 bg-gradient-to-r from-teal-500 to-green-500 rounded"></div>
        </div>
      </div>

      {/* Análisis Geográfico y Canales */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Comunas más frecuentes */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
            <MapPin className="h-6 w-6 text-red-500 mr-2" />
            Comunas Más Frecuentadas
          </h2>
          <div className="space-y-3">
            {comunasFrecuentes.map((comuna, index) => (
              <div key={index} className="flex items-center">
                <div className="w-8 h-8 rounded-full bg-pink-100 text-pink-600 flex items-center justify-center font-bold text-sm mr-3">
                  {index + 1}
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium text-gray-900">{comuna.comuna}</span>
                    <span className="text-sm text-gray-600">{comuna.cantidad} pedidos</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-gradient-to-r from-pink-500 to-purple-500 h-2 rounded-full transition-all"
                      style={{ width: `${(comuna.cantidad / comunasFrecuentes[0]?.cantidad * 100) || 0}%` }}
                    ></div>
                  </div>
                </div>
                <span className="ml-4 font-bold text-green-600 text-sm">
                  {formatCurrency(comuna.total || 0)}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Canales de venta */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
            <Smartphone className="h-6 w-6 text-blue-500 mr-2" />
            Rendimiento por Canal
          </h2>
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={canalesVenta}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="canal" style={{ fontSize: '12px' }} />
              <YAxis style={{ fontSize: '12px' }} />
              <Tooltip 
                formatter={(value, name) => [
                  name === 'ventas' ? formatCurrency(value) : value,
                  name === 'ventas' ? 'Ventas' : 'Pedidos'
                ]}
                labelStyle={{ color: '#000' }}
              />
              <Legend />
              <Bar dataKey="ventas" fill="#3B82F6" name="Ventas" />
              <Bar dataKey="pedidos" fill="#10B981" name="Pedidos" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Sección: Arreglos Más Solicitados por Motivo (General) */}
      <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl shadow-lg border-2 border-blue-200 p-8 mb-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 flex items-center">
              <ShoppingBag className="h-7 w-7 text-blue-600 mr-3" />
              🎁 Arreglos Más Solicitados por Motivo
            </h2>
            <p className="text-sm text-gray-600 mt-1">Descubre qué productos se compran más para cada ocasión</p>
          </div>
          
          {/* Filtros mes y año */}
          <div className="flex gap-2">
            <select
              value={mesArreglosMotivo || ''}
              onChange={(e) => setMesArreglosMotivo(e.target.value ? parseInt(e.target.value) : null)}
              className="text-xs border border-blue-300 rounded-md px-2 py-1 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Todos los meses</option>
              <option value="1">Enero</option>
              <option value="2">Febrero</option>
              <option value="3">Marzo</option>
              <option value="4">Abril</option>
              <option value="5">Mayo</option>
              <option value="6">Junio</option>
              <option value="7">Julio</option>
              <option value="8">Agosto</option>
              <option value="9">Septiembre</option>
              <option value="10">Octubre</option>
              <option value="11">Noviembre</option>
              <option value="12">Diciembre</option>
            </select>
            <select
              value={añoArreglosMotivo || ''}
              onChange={(e) => setAñoArreglosMotivo(e.target.value ? parseInt(e.target.value) : null)}
              className="text-xs border border-blue-300 rounded-md px-2 py-1 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Todos los años</option>
              {AÑOS_DISPONIBLES.map(año => (
                <option key={año} value={año}>{año}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Grid de Motivos con sus Arreglos */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {arreglosPorMotivo.map((item, index) => (
            <div key={index} className="bg-white rounded-xl shadow-md border border-blue-100 p-5 hover:shadow-xl transition-all hover:scale-[1.02]">
              {/* Header del Motivo */}
              <div className="flex items-center justify-between mb-4 pb-3 border-b-2 border-blue-200">
                <h3 className="text-lg font-bold text-gray-900 flex items-center">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm text-white mr-2 ${
                    index === 0 ? 'bg-yellow-500' : 
                    index === 1 ? 'bg-gray-400' : 
                    index === 2 ? 'bg-orange-600' : 
                    'bg-blue-500'
                  }`}>
                    {index + 1}
                  </div>
                  <span className="text-sm truncate" title={item.motivo}>{item.motivo}</span>
                </h3>
                <span className="text-xs font-semibold text-blue-600 bg-blue-100 px-2 py-1 rounded-full whitespace-nowrap">
                  {item.total_pedidos} pedidos
                </span>
              </div>
              
              {/* Lista de Arreglos */}
              {item.arreglos && item.arreglos.length > 0 ? (
                <div className="space-y-2 max-h-[280px] overflow-y-auto custom-scrollbar">
                  {item.arreglos.map((arreglo, idx) => (
                    <div key={idx} className="flex items-center justify-between p-2 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg hover:from-blue-100 hover:to-indigo-100 transition-colors">
                      <div className="flex items-center flex-1 min-w-0">
                        <div className="w-2 h-2 rounded-full bg-blue-500 mr-2 flex-shrink-0"></div>
                        <span className="text-sm text-gray-700 truncate" title={arreglo.nombre}>
                          {arreglo.nombre}
                        </span>
                      </div>
                      <span className="text-sm font-bold text-blue-600 ml-2 flex-shrink-0">
                        {arreglo.cantidad}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center text-sm text-gray-400 py-4">
                  Sin datos de arreglos
                </div>
              )}
            </div>
          ))}
        </div>
        
        {arreglosPorMotivo.length === 0 && (
          <div className="text-center text-gray-500 py-12">
            <Package className="h-16 w-16 mx-auto text-gray-300 mb-4" />
            <p className="text-lg font-semibold">No hay datos disponibles</p>
            <p className="text-sm">Selecciona un periodo diferente</p>
          </div>
        )}
      </div>

      {/* Análisis de Personalizaciones */}
      {analisisPersonalizaciones && (
        <div className="bg-gradient-to-br from-pink-50 to-purple-50 rounded-xl shadow-lg border-2 border-pink-200 p-8 mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 flex items-center">
                <Package className="h-7 w-7 text-pink-600 mr-3" />
                📐 Análisis Profundo de Personalizaciones
              </h2>
              <p className="text-sm text-gray-600 mt-1">Explora colores, tipos y motivaciones más solicitadas</p>
            </div>
            <div className="flex items-center gap-2">
              <select
                value={mesPersonalizaciones || ''}
                onChange={(e) => setMesPersonalizaciones(e.target.value ? parseInt(e.target.value) : null)}
                className="text-xs border border-pink-300 rounded-md px-2 py-1 focus:ring-2 focus:ring-pink-500 focus:border-pink-500"
              >
                <option value="">Todos los meses</option>
                {MESES.map(mes => (
                  <option key={mes.valor} value={mes.valor}>{mes.nombre}</option>
                ))}
              </select>
              <select
                value={añoPersonalizaciones || ''}
                onChange={(e) => setAñoPersonalizaciones(e.target.value ? parseInt(e.target.value) : null)}
                className="text-xs border border-pink-300 rounded-md px-2 py-1 focus:ring-2 focus:ring-pink-500 focus:border-pink-500"
              >
                <option value="">Todos los años</option>
                {AÑOS_DISPONIBLES.map(año => (
                  <option key={año} value={año}>{año}</option>
                ))}
              </select>
            </div>
          </div>

          {/* KPIs de Personalizaciones */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <div className="bg-white rounded-lg p-4 shadow-sm border border-pink-100">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Personalizaciones</p>
                  <p className="text-3xl font-bold text-pink-600">{analisisPersonalizaciones.total_personalizaciones}</p>
                </div>
                <Package className="h-12 w-12 text-pink-300" />
              </div>
            </div>
            <div className="bg-white rounded-lg p-4 shadow-sm border border-purple-100">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Ventas Totales</p>
                  <p className="text-2xl font-bold text-purple-600">{formatCurrency(analisisPersonalizaciones.ventas_totales)}</p>
                </div>
                <DollarSign className="h-12 w-12 text-purple-300" />
              </div>
            </div>
            <div className="bg-white rounded-lg p-4 shadow-sm border border-indigo-100">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Ticket Promedio</p>
                  <p className="text-2xl font-bold text-indigo-600">{formatCurrency(analisisPersonalizaciones.ticket_promedio)}</p>
                </div>
                <Tag className="h-12 w-12 text-indigo-300" />
              </div>
            </div>
          </div>

          {/* Gráficos de Análisis */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Colores Más Frecuentes */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
                <div className="w-3 h-3 rounded-full bg-pink-500 mr-2"></div>
                Colores Más Solicitados
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={analisisPersonalizaciones.colores} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" style={{ fontSize: '11px' }} />
                  <YAxis dataKey="color" type="category" width={80} style={{ fontSize: '10px' }} />
                  <Tooltip />
                  <Bar dataKey="cantidad" fill="#EC4899" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Tipos Más Frecuentes */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
                <div className="w-3 h-3 rounded-full bg-purple-500 mr-2"></div>
                Tipos de Arreglo
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={analisisPersonalizaciones.tipos}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ tipo, percent }) => {
                      // Solo mostrar etiqueta si el porcentaje es >= 5%
                      if (percent * 100 < 5) return '';
                      return `${(percent * 100).toFixed(0)}%`;
                    }}
                    outerRadius={90}
                    fill="#8884d8"
                    dataKey="cantidad"
                  >
                    {analisisPersonalizaciones.tipos.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip 
                    formatter={(value, name, props) => [value, props.payload.tipo]}
                  />
                </PieChart>
              </ResponsiveContainer>
              <div className="mt-4 space-y-1 max-h-[120px] overflow-y-auto custom-scrollbar">
                {analisisPersonalizaciones.tipos.map((item, index) => (
                  <div key={index} className="flex items-center justify-between text-xs">
                    <div className="flex items-center">
                      <div className="w-3 h-3 rounded-full mr-2" style={{ backgroundColor: COLORS[index % COLORS.length] }}></div>
                      <span className="text-gray-700">{item.tipo}</span>
                    </div>
                    <span className="font-semibold text-gray-900">{item.cantidad}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Motivos Más Frecuentes */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
                <div className="w-3 h-3 rounded-full bg-indigo-500 mr-2"></div>
                Motivaciones
              </h3>
              <div className="space-y-2 max-h-[300px] overflow-y-auto custom-scrollbar">
                {analisisPersonalizaciones.motivos.map((motivo, index) => (
                  <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                    <div className="flex items-center">
                      <div className={`w-6 h-6 rounded-full flex items-center justify-center font-bold text-xs text-white mr-2 ${
                        index === 0 ? 'bg-yellow-500' : index === 1 ? 'bg-gray-400' : index === 2 ? 'bg-orange-600' : 'bg-indigo-500'
                      }`}>
                        {index + 1}
                      </div>
                      <span className="text-sm font-medium text-gray-700">{motivo.motivo}</span>
                    </div>
                    <span className="text-sm font-bold text-indigo-600">{motivo.cantidad}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Sección: Arreglos Más Frecuentes por Motivo */}
          <div className="mt-8">
            <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
              <Package className="mr-2 text-pink-500" />
              Arreglos Más Solicitados por Motivo
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {analisisPersonalizaciones.motivos_con_arreglos?.map((item, index) => (
                <div key={index} className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow">
                  {/* Header del Motivo */}
                  <div className="flex items-center justify-between mb-4 pb-3 border-b border-gray-200">
                    <h4 className="text-base font-bold text-gray-900 flex items-center">
                      <div className={`w-7 h-7 rounded-full flex items-center justify-center font-bold text-xs text-white mr-2 ${
                        index === 0 ? 'bg-yellow-500' : 
                        index === 1 ? 'bg-gray-400' : 
                        index === 2 ? 'bg-orange-600' : 
                        'bg-indigo-500'
                      }`}>
                        {index + 1}
                      </div>
                      {item.motivo}
                    </h4>
                    <span className="text-sm font-semibold text-gray-500 bg-gray-100 px-2 py-1 rounded">
                      {item.cantidad} pedidos
                    </span>
                  </div>
                  
                  {/* Lista de Arreglos */}
                  {item.arreglos && item.arreglos.length > 0 ? (
                    <div className="space-y-2">
                      {item.arreglos.map((arreglo, idx) => (
                        <div key={idx} className="flex items-center justify-between p-2 bg-gradient-to-r from-pink-50 to-purple-50 rounded-md">
                          <div className="flex items-center flex-1 min-w-0">
                            <div className="w-2 h-2 rounded-full bg-pink-500 mr-2 flex-shrink-0"></div>
                            <span className="text-sm text-gray-700 truncate" title={arreglo.tipo}>
                              {arreglo.tipo}
                            </span>
                          </div>
                          <span className="text-sm font-bold text-pink-600 ml-2 flex-shrink-0">
                            {arreglo.cantidad}
                          </span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center text-sm text-gray-400 py-2">
                      Sin datos de arreglos
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Sección: Anticipación de Pedidos por Canal */}
      {anticipacionPedidos && (
        <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl shadow-lg border-2 border-green-200 p-8 mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 flex items-center">
                <Clock className="h-7 w-7 text-green-600 mr-3" />
                ⏰ Anticipación de Pedidos
              </h2>
              <p className="text-sm text-gray-600 mt-1">¿Con cuánta anticipación hacen los pedidos los clientes?</p>
            </div>
            
            {/* Filtros mes y año */}
            <div className="flex gap-2">
              <select
                value={mesAnticipacion || ''}
                onChange={(e) => setMesAnticipacion(e.target.value ? parseInt(e.target.value) : null)}
                className="text-xs border border-green-300 rounded-md px-2 py-1 focus:ring-2 focus:ring-green-500 focus:border-green-500"
              >
                <option value="">Todos los meses</option>
                {MESES.map(mes => (
                  <option key={mes.valor} value={mes.valor}>{mes.nombre}</option>
                ))}
              </select>
              <select
                value={añoAnticipacion || ''}
                onChange={(e) => setAñoAnticipacion(e.target.value ? parseInt(e.target.value) : null)}
                className="text-xs border border-green-300 rounded-md px-2 py-1 focus:ring-2 focus:ring-green-500 focus:border-green-500"
              >
                <option value="">Todos los años</option>
                {AÑOS_DISPONIBLES.map(año => (
                  <option key={año} value={año}>{año}</option>
                ))}
              </select>
            </div>
          </div>

          {/* KPIs Generales */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <div className="bg-white rounded-lg p-4 shadow-sm border border-green-100">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Pedidos Analizados</p>
                  <p className="text-3xl font-bold text-green-600">{anticipacionPedidos.total_pedidos}</p>
                </div>
                <Package className="h-12 w-12 text-green-300" />
              </div>
            </div>
            <div className="bg-white rounded-lg p-4 shadow-sm border border-emerald-100">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Promedio de Anticipación</p>
                  <p className="text-3xl font-bold text-emerald-600">{anticipacionPedidos.promedio_general} días</p>
                </div>
                <Calendar className="h-12 w-12 text-emerald-300" />
              </div>
            </div>
            <div className="bg-white rounded-lg p-4 shadow-sm border border-teal-100">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Canales Activos</p>
                  <p className="text-3xl font-bold text-teal-600">{anticipacionPedidos.por_canal.length}</p>
                </div>
                <Smartphone className="h-12 w-12 text-teal-300" />
              </div>
            </div>
          </div>

          {/* Gráfico General */}
          <div className="bg-white rounded-xl shadow-md border border-green-100 p-6 mb-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
              <div className="w-3 h-3 rounded-full bg-green-500 mr-2"></div>
              Distribución General de Anticipación
            </h3>
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={anticipacionPedidos.general}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="categoria" 
                  style={{ fontSize: '11px' }}
                  angle={-15}
                  textAnchor="end"
                  height={80}
                />
                <YAxis style={{ fontSize: '11px' }} />
                <Tooltip />
                <Bar dataKey="cantidad" fill="#10B981" name="Cantidad de Pedidos" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Anticipación por Canal */}
          <div>
            <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
              <Smartphone className="mr-2 text-green-600" />
              Anticipación por Canal de Venta
            </h3>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {anticipacionPedidos.por_canal.map((canalData, index) => (
                <div key={index} className="bg-white rounded-xl shadow-md border border-green-100 p-5 hover:shadow-xl transition-all">
                  {/* Header del Canal */}
                  <div className="flex items-center justify-between mb-4 pb-3 border-b-2 border-green-200">
                    <h4 className="text-lg font-bold text-gray-900 flex items-center">
                      <div className="w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm text-white mr-2 bg-green-500">
                        {index + 1}
                      </div>
                      {canalData.canal}
                    </h4>
                    <div className="text-right">
                      <p className="text-xs text-gray-500">Promedio</p>
                      <p className="text-lg font-bold text-green-600">{canalData.promedio_dias} días</p>
                    </div>
                  </div>
                  
                  {/* Gráfico de Barras por Canal */}
                  <ResponsiveContainer width="100%" height={250}>
                    <BarChart data={canalData.categorias} layout="horizontal">
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis type="number" style={{ fontSize: '10px' }} />
                      <YAxis 
                        dataKey="categoria" 
                        type="category" 
                        width={90} 
                        style={{ fontSize: '9px' }}
                      />
                      <Tooltip />
                      <Bar dataKey="cantidad" fill="#059669" name="Pedidos" />
                    </BarChart>
                  </ResponsiveContainer>
                  
                  {/* Total de Pedidos del Canal */}
                  <div className="mt-3 pt-3 border-t border-gray-200 text-center">
                    <span className="text-sm text-gray-600">Total: </span>
                    <span className="text-base font-bold text-green-600">{canalData.total_pedidos} pedidos</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Sección: Colores Más Frecuentes */}
      <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl shadow-lg border-2 border-purple-200 p-8 mb-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 flex items-center">
              <Package className="h-7 w-7 text-purple-600 mr-3" />
              🎨 Colores Más Populares
            </h2>
            <p className="text-sm text-gray-600 mt-1">Colores más solicitados en todos los pedidos (normalizados)</p>
          </div>
          
          {/* Filtros mes y año */}
          <div className="flex gap-2">
            <select
              value={mesColores || ''}
              onChange={(e) => setMesColores(e.target.value ? parseInt(e.target.value) : null)}
              className="text-xs border border-purple-300 rounded-md px-2 py-1 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
            >
              <option value="">Todos los meses</option>
              <option value="1">Enero</option>
              <option value="2">Febrero</option>
              <option value="3">Marzo</option>
              <option value="4">Abril</option>
              <option value="5">Mayo</option>
              <option value="6">Junio</option>
              <option value="7">Julio</option>
              <option value="8">Agosto</option>
              <option value="9">Septiembre</option>
              <option value="10">Octubre</option>
              <option value="11">Noviembre</option>
              <option value="12">Diciembre</option>
            </select>
            <select
              value={añoColores || ''}
              onChange={(e) => setAñoColores(e.target.value ? parseInt(e.target.value) : null)}
              className="text-xs border border-purple-300 rounded-md px-2 py-1 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
            >
              <option value="">Todos los años</option>
              {AÑOS_DISPONIBLES.map(año => (
                <option key={año} value={año}>{año}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Lista de Colores */}
        {coloresFrecuentes.length > 0 ? (
          <div className="bg-white rounded-xl shadow-md border border-purple-100 p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Top 10 Colores</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3">
              {coloresFrecuentes.slice(0, 10).map((item, index) => (
                <div 
                  key={index} 
                  className="bg-gradient-to-br from-purple-100 to-pink-100 rounded-lg p-4 text-center hover:shadow-lg transition-all hover:scale-105"
                >
                  <div className={`w-10 h-10 rounded-full mx-auto mb-2 flex items-center justify-center font-bold text-white ${
                    index === 0 ? 'bg-yellow-500' : 
                    index === 1 ? 'bg-gray-400' : 
                    index === 2 ? 'bg-orange-600' : 
                    'bg-purple-500'
                  }`}>
                    {index + 1}
                  </div>
                  <p className="text-sm font-bold text-gray-900 mb-1">{item.color}</p>
                  <p className="text-2xl font-bold text-purple-600">{item.cantidad}</p>
                  <p className="text-xs text-gray-500">pedidos</p>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="text-center text-gray-500 py-12 bg-white rounded-xl shadow-md">
            <Package className="h-16 w-16 mx-auto text-gray-300 mb-4" />
            <p className="text-lg font-semibold">No hay datos disponibles</p>
            <p className="text-sm">Selecciona un periodo diferente</p>
          </div>
        )}
      </div>

    </div>
  )
}

export default ReportesPage

