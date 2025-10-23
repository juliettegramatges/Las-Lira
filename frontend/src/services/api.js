import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Exportar API_URL para uso directo
export const API_URL = API_BASE_URL;

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// === PEDIDOS ===
export const pedidosAPI = {
  listar: (filtros = {}) => api.get('/pedidos', { params: filtros }),
  obtener: (id) => api.get(`/pedidos/${id}`),
  crear: (data) => api.post('/pedidos', data),
  actualizarEstado: (id, estado) => api.patch(`/pedidos/${id}/estado`, { estado }),
  eliminar: (id) => api.delete(`/pedidos/${id}`),
  obtenerTablero: () => api.get('/pedidos/tablero'),
  actualizarEstadosPorFecha: () => api.post('/pedidos/actualizar-estados-por-fecha'),
};

// === INVENTARIO ===
export const inventarioAPI = {
  // Flores
  listarFlores: (filtros = {}) => api.get('/inventario/flores', { params: filtros }),
  obtenerFlor: (id) => api.get(`/inventario/flores/${id}`),
  actualizarStockFlor: (id, cantidad, operacion = 'set') => 
    api.patch(`/inventario/flores/${id}/stock`, { cantidad, operacion }),
  
  // Contenedores
  listarContenedores: (filtros = {}) => api.get('/inventario/contenedores', { params: filtros }),
  obtenerContenedor: (id) => api.get(`/inventario/contenedores/${id}`),
  actualizarStockContenedor: (id, cantidad, operacion = 'set') => 
    api.patch(`/inventario/contenedores/${id}/stock`, { cantidad, operacion }),
  
  // Bodegas
  listarBodegas: () => api.get('/inventario/bodegas'),
  
  // Resumen
  obtenerResumen: () => api.get('/inventario/resumen'),
};

// === PRODUCTOS ===
export const productosAPI = {
  listar: (filtros = {}) => api.get('/productos', { params: filtros }),
  obtener: (id) => api.get(`/productos/${id}`),
  verificarStock: (id) => api.get(`/productos/${id}/verificar-stock`),
  estimarCosto: (data) => api.post('/productos/estimar-costo', data),
};

export default api;

