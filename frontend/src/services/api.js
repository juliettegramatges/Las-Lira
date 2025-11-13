import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001/api';

// Exportar API_URL para uso directo
export const API_URL = API_BASE_URL;

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Importante para las sesiones
});

// === PEDIDOS ===
export const pedidosAPI = {
  listar: (filtros = {}) => api.get('/pedidos', { params: filtros }),
  obtener: (id) => api.get(`/pedidos/${id}`),
  crear: (data) => api.post('/pedidos', data),
  actualizar: (id, data) => api.put(`/pedidos/${id}`, data),
  actualizarEstado: (id, estado) => api.patch(`/pedidos/${id}/estado`, { estado }),
  eliminar: (id) => api.delete(`/pedidos/${id}`),
  cancelar: (id, motivo) => api.patch(`/pedidos/${id}/cancelar`, { motivo }),
  obtenerTablero: (incluirDespachados = false, semanasDespachados = 1) => api.get('/pedidos/tablero', { params: { incluir_despachados: incluirDespachados, semanas_despachados: semanasDespachados } }),
  actualizarEstadosPorFecha: () => api.post('/pedidos/actualizar-estados-por-fecha'),
};

// === INSUMOS DE PEDIDOS (TALLER) ===
export const pedidoInsumosAPI = {
  obtenerInsumos: (pedidoId) => api.get(`/pedidos/${pedidoId}/insumos`),
  guardarInsumos: (pedidoId, insumos) => api.post(`/pedidos/${pedidoId}/insumos`, { insumos }),
  confirmarYDescontar: (pedidoId, data = {}) => api.post(`/pedidos/${pedidoId}/confirmar-insumos`, data),
  obtenerPedidosTaller: () => api.get('/pedidos/taller'),
};

// === INVENTARIO ===
export const inventarioAPI = {
  // Flores
  listarFlores: (filtros = {}) => api.get('/inventario/flores', { params: filtros }),
  obtenerFlor: (id) => api.get(`/inventario/flores/${id}`),
  crearFlor: (data) => api.post('/inventario/flores', data),
  actualizarFlor: (id, data) => api.patch(`/inventario/flores/${id}`, data),
  eliminarFlor: (id) => api.delete(`/inventario/flores/${id}`),
  actualizarStockFlor: (id, cantidad, operacion = 'set') => 
    api.patch(`/inventario/flores/${id}/stock`, { cantidad, operacion }),
  
  // Contenedores
  listarContenedores: (filtros = {}) => api.get('/inventario/contenedores', { params: filtros }),
  obtenerContenedor: (id) => api.get(`/inventario/contenedores/${id}`),
  crearContenedor: (data) => api.post('/inventario/contenedores', data),
  actualizarContenedor: (id, data) => api.patch(`/inventario/contenedores/${id}`, data),
  eliminarContenedor: (id) => api.delete(`/inventario/contenedores/${id}`),
  actualizarStockContenedor: (id, cantidad, operacion = 'set') => 
    api.patch(`/inventario/contenedores/${id}/stock`, { cantidad, operacion }),
  
  // Proveedores
  listarProveedores: () => api.get('/inventario/proveedores'),
  obtenerProveedor: (id) => api.get(`/inventario/proveedores/${id}`),
  crearProveedor: (data) => api.post('/inventario/proveedores', data),
  actualizarProveedor: (id, data) => api.put(`/inventario/proveedores/${id}`, data),
  eliminarProveedor: (id) => api.delete(`/inventario/proveedores/${id}`),
  
  // Bodegas
  listarBodegas: () => api.get('/inventario/bodegas'),
  
  // Resumen
  obtenerResumen: () => api.get('/inventario/resumen'),
};

// === PRODUCTOS ===
export const productosAPI = {
  listar: (filtros = {}) => api.get('/productos', { params: filtros }),
  obtener: (id) => api.get(`/productos/${id}`),
  crear: (data) => api.post('/productos', data),
  actualizar: (id, data) => api.put(`/productos/${id}`, data),
  eliminar: (id) => api.delete(`/productos/${id}`),
  verificarStock: (id) => api.get(`/productos/${id}/verificar-stock`),
  estimarCosto: (data) => api.post('/productos/estimar-costo', data),
};

// === CLIENTES ===
export const clientesAPI = {
  listar: (filtros = {}) => api.get('/clientes', { params: filtros }),
  obtener: (id) => api.get(`/clientes/${id}`),
  crear: (data) => api.post('/clientes', data),
  actualizar: (id, data) => api.put(`/clientes/${id}`, data),
  eliminar: (id) => api.delete(`/clientes/${id}`),
  buscarPorNombre: (nombre) => api.get('/clientes/buscar-por-nombre', { params: { nombre } }),
  buscarPorTelefono: (telefono) => api.get('/clientes/buscar-por-telefono', { params: { telefono } }),
};

// === AUTENTICACIÓN ===
export const authAPI = {
  login: (username, password) => api.post('/auth/login', { username, password }),
  logout: () => api.post('/auth/logout'),
  getCurrentUser: () => api.get('/auth/me'),
  listarUsuarios: () => api.get('/auth/usuarios'),
  crearUsuario: (data) => api.post('/auth/usuarios', data),
};

export default api;

