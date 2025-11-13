/**
 * Utilidades comunes reutilizables
 */

import { format } from 'date-fns'
import { es } from 'date-fns/locale'

/**
 * Formatea una fecha a formato legible
 * @param {string|Date} fecha - Fecha a formatear
 * @param {string} formato - Formato deseado (default: 'dd MMM yyyy')
 * @returns {string} Fecha formateada o '-'
 */
export const formatFecha = (fecha, formato = 'dd MMM yyyy') => {
  if (!fecha) return '-'
  try {
    return format(new Date(fecha), formato, { locale: es })
  } catch {
    return '-'
  }
}

/**
 * Limpia HTML de un string y devuelve solo texto
 * @param {string} html - String con HTML
 * @returns {string} Texto limpio
 */
export const limpiarHTML = (html) => {
  if (!html) return ''
  const temp = document.createElement('div')
  temp.innerHTML = html
  return temp.textContent || temp.innerText || ''
}

/**
 * Formatea un número como moneda
 * @param {number} cantidad - Cantidad a formatear
 * @param {string} moneda - Código de moneda (default: 'CLP')
 * @returns {string} Cantidad formateada
 */
export const formatMoneda = (cantidad, moneda = 'CLP') => {
  if (cantidad === null || cantidad === undefined) return '$0'
  return new Intl.NumberFormat('es-CL', {
    style: 'currency',
    currency: moneda,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(cantidad)
}

/**
 * Trunca un texto a una longitud máxima
 * @param {string} texto - Texto a truncar
 * @param {number} maxLength - Longitud máxima
 * @returns {string} Texto truncado
 */
export const truncarTexto = (texto, maxLength = 50) => {
  if (!texto) return ''
  if (texto.length <= maxLength) return texto
  return texto.substring(0, maxLength) + '...'
}

/**
 * Valida un email
 * @param {string} email - Email a validar
 * @returns {boolean} true si es válido
 */
export const validarEmail = (email) => {
  if (!email) return false
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return re.test(email)
}

/**
 * Valida un teléfono chileno
 * @param {string} telefono - Teléfono a validar
 * @returns {boolean} true si es válido
 */
export const validarTelefono = (telefono) => {
  if (!telefono) return false
  // Acepta formatos: +56912345678, 56912345678, 912345678, 12345678
  const re = /^(\+?56)?9?\d{8}$/
  return re.test(telefono.replace(/\s/g, ''))
}

