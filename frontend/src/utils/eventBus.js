/**
 * Sistema centralizado de eventos para sincronización entre usuarios
 * Emite eventos cuando hay cambios en la base de datos
 */

class EventBus {
  constructor() {
    this.listeners = new Map()
  }

  /**
   * Emite un evento de actualización
   * @param {string} eventType - Tipo de evento (pedidos, clientes, productos, cobranza, tablero, etc.)
   * @param {object} data - Datos adicionales del evento
   */
  emit(eventType, data = {}) {
    const event = new CustomEvent(`refetch-${eventType}`, { detail: data })
    window.dispatchEvent(event)
    
    // También emitir evento global para recargas generales
    if (eventType !== 'all') {
      window.dispatchEvent(new CustomEvent('refetch-all', { detail: { source: eventType } }))
    }
  }

  /**
   * Escucha eventos de actualización
   * @param {string} eventType - Tipo de evento a escuchar
   * @param {function} callback - Función a ejecutar cuando ocurre el evento
   */
  on(eventType, callback) {
    const handler = (event) => callback(event.detail)
    window.addEventListener(`refetch-${eventType}`, handler)
    
    // Guardar referencia para poder removerlo después
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, [])
    }
    this.listeners.get(eventType).push({ callback, handler })
    
    return () => this.off(eventType, callback)
  }

  /**
   * Deja de escuchar un evento
   * @param {string} eventType - Tipo de evento
   * @param {function} callback - Función a remover
   */
  off(eventType, callback) {
    const listeners = this.listeners.get(eventType) || []
    const index = listeners.findIndex(l => l.callback === callback)
    if (index !== -1) {
      const { handler } = listeners[index]
      window.removeEventListener(`refetch-${eventType}`, handler)
      listeners.splice(index, 1)
    }
  }

  /**
   * Limpia todos los listeners de un tipo de evento
   * @param {string} eventType - Tipo de evento
   */
  removeAllListeners(eventType) {
    const listeners = this.listeners.get(eventType) || []
    listeners.forEach(({ handler }) => {
      window.removeEventListener(`refetch-${eventType}`, handler)
    })
    this.listeners.delete(eventType)
  }
}

// Instancia singleton
export const eventBus = new EventBus()

// Tipos de eventos disponibles
export const EVENT_TYPES = {
  PEDIDOS: 'pedidos',
  CLIENTES: 'clientes',
  PRODUCTOS: 'productos',
  COBRANZA: 'cobranza',
  TABLERO: 'tablero',
  INVENTARIO: 'inventario',
  EVENTOS: 'eventos',
  RUTAS: 'rutas',
  TALLER: 'taller',
  ALL: 'all'
}

