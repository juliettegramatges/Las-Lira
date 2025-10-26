/**
 * 🎨 TEMA PROFESIONAL LAS LIRA
 * Paleta de colores minimalista y consistente
 */

// Paleta de colores principales
export const colors = {
  // Brand colors
  primary: {
    50: 'rgb(253, 242, 248)',
    100: 'rgb(252, 231, 243)',
    200: 'rgb(251, 207, 232)',
    300: 'rgb(249, 168, 212)',
    400: 'rgb(244, 114, 182)',
    500: 'rgb(236, 72, 153)',  // Rosa principal
    600: 'rgb(219, 39, 119)',
    700: 'rgb(190, 24, 93)',
    800: 'rgb(157, 23, 77)',
    900: 'rgb(131, 24, 67)',
  },
  
  // Semantic colors
  success: {
    light: 'rgb(220, 252, 231)',
    DEFAULT: 'rgb(34, 197, 94)',
    dark: 'rgb(21, 128, 61)',
  },
  
  warning: {
    light: 'rgb(254, 249, 195)',
    DEFAULT: 'rgb(234, 179, 8)',
    dark: 'rgb(161, 98, 7)',
  },
  
  danger: {
    light: 'rgb(254, 226, 226)',
    DEFAULT: 'rgb(239, 68, 68)',
    dark: 'rgb(185, 28, 28)',
  },
  
  info: {
    light: 'rgb(224, 242, 254)',
    DEFAULT: 'rgb(59, 130, 246)',
    dark: 'rgb(29, 78, 216)',
  },
  
  // Neutrals (minimalistas)
  gray: {
    50: 'rgb(249, 250, 251)',
    100: 'rgb(243, 244, 246)',
    200: 'rgb(229, 231, 235)',
    300: 'rgb(209, 213, 219)',
    400: 'rgb(156, 163, 175)',
    500: 'rgb(107, 114, 128)',
    600: 'rgb(75, 85, 99)',
    700: 'rgb(55, 65, 81)',
    800: 'rgb(31, 41, 55)',
    900: 'rgb(17, 24, 39)',
  },
}

// Clases de utilidad para botones
export const buttonStyles = {
  primary: 'bg-gradient-to-r from-pink-500 to-rose-500 text-white hover:from-pink-600 hover:to-rose-600 shadow-sm hover:shadow-md transition-all duration-200',
  secondary: 'bg-white border-2 border-gray-200 text-gray-700 hover:bg-gray-50 hover:border-gray-300 transition-all duration-200',
  success: 'bg-green-500 text-white hover:bg-green-600 shadow-sm hover:shadow-md transition-all duration-200',
  danger: 'bg-red-500 text-white hover:bg-red-600 shadow-sm hover:shadow-md transition-all duration-200',
  ghost: 'text-gray-600 hover:bg-gray-100 hover:text-gray-900 transition-all duration-200',
}

// Clases para badges/etiquetas
export const badgeStyles = {
  success: 'bg-green-50 text-green-700 border border-green-200',
  warning: 'bg-amber-50 text-amber-700 border border-amber-200',
  danger: 'bg-red-50 text-red-700 border border-red-200',
  info: 'bg-blue-50 text-blue-700 border border-blue-200',
  primary: 'bg-pink-50 text-pink-700 border border-pink-200',
  neutral: 'bg-gray-50 text-gray-700 border border-gray-200',
}

// Clases para cards
export const cardStyles = {
  base: 'bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-all duration-200',
  interactive: 'bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md hover:border-gray-300 cursor-pointer transition-all duration-200',
  highlight: 'bg-gradient-to-br from-pink-50 to-rose-50 rounded-xl border border-pink-200 shadow-sm',
}

// Clases para inputs
export const inputStyles = {
  base: 'w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent transition-all duration-200',
  error: 'w-full px-4 py-2.5 rounded-lg border-2 border-red-300 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent',
  success: 'w-full px-4 py-2.5 rounded-lg border-2 border-green-300 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent',
}

// Espaciado consistente
export const spacing = {
  section: 'mb-8',
  card: 'p-6',
  cardSmall: 'p-4',
  input: 'mb-4',
}

// Tipografía
export const typography = {
  pageTitle: 'text-3xl font-bold text-gray-900 mb-6',
  sectionTitle: 'text-xl font-semibold text-gray-800 mb-4',
  cardTitle: 'text-lg font-semibold text-gray-800 mb-3',
  label: 'block text-sm font-medium text-gray-700 mb-2',
  helperText: 'text-sm text-gray-500 mt-1',
  errorText: 'text-sm text-red-600 mt-1',
}

