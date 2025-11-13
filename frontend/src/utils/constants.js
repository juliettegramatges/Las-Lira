/**
 * Constantes compartidas en toda la aplicación
 */

// Colores comunes para productos y personalizaciones
export const COLORES_DISPONIBLES = [
  'Blanco', 'Rojo', 'Rosado', 'Fucsia', 'Naranja', 'Amarillo',
  'Verde', 'Azul', 'Morado', 'Lila', 'Celeste', 'Durazno',
  'Salmón', 'Coral', 'Burdeo', 'Mixto', 'Pastel', 'Vibrantes'
]

// Colores comunes para productos
export const COLORES_PRODUCTOS = [
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
  'Natural',
  'Blancos',
  'Rojos',
  'Rosados',
  'Verdes',
  'Azules',
  'Naranjos'
]

// Motivos comunes de pedidos
export const MOTIVOS_PEDIDO = [
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

// Estados de pago
export const ESTADOS_PAGO = ['No Pagado', 'Pagado']

// Métodos de pago
export const METODOS_PAGO = [
  'Tr. BICE',
  'Tr. Santander',
  'Tr. Itaú',
  'Pago con tarjeta',
  'Efectivo',
  'Otro',
]

// Documentos tributarios
export const DOCUMENTOS_TRIBUTARIOS = [
  'Hacer boleta',
  'Hacer factura',
  'Boleta emitida',
  'Factura emitida',
  'No requiere',
]

// Estados de evento
export const ESTADOS_EVENTO = [
  'Cotización',
  'Propuesta Enviada',
  'Confirmado',
  'En Preparación',
  'En Evento',
  'Finalizado',
  'Retirado'
]

// Colores para gráficos
export const COLORS_CHART = ['#EC4899', '#8B5CF6', '#3B82F6', '#10B981', '#F59E0B', '#EF4444']

// Meses del año
export const MESES = [
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

// Generar opciones de años dinámicamente
export const generarOpcionesAnios = () => {
  const añoActual = new Date().getFullYear()
  const años = []
  // Desde 2022 hasta 2 años en el futuro
  for (let año = 2022; año <= añoActual + 2; año++) {
    años.push(año)
  }
  return años
}

