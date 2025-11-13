/**
 * Componente de botón estandarizado y escalable
 * Uso: <Button variant="primary" size="md" icon={Plus}>Texto</Button>
 */

import { forwardRef } from 'react'

const Button = forwardRef(({
  children,
  variant = 'primary',
  size = 'md',
  icon: Icon,
  iconPosition = 'left',
  disabled = false,
  loading = false,
  fullWidth = false,
  className = '',
  ...props
}, ref) => {
  // Variantes de estilo
  const variants = {
    primary: 'bg-gradient-to-r from-pink-500 to-rose-500 text-white hover:from-pink-600 hover:to-rose-600 shadow-sm hover:shadow-md',
    secondary: 'bg-white border-2 border-gray-200 text-gray-700 hover:bg-gray-50 hover:border-gray-300',
    success: 'bg-green-500 text-white hover:bg-green-600 shadow-sm hover:shadow-md',
    danger: 'bg-red-500 text-white hover:bg-red-600 shadow-sm hover:shadow-md',
    warning: 'bg-yellow-500 text-white hover:bg-yellow-600 shadow-sm hover:shadow-md',
    info: 'bg-blue-500 text-white hover:bg-blue-600 shadow-sm hover:shadow-md',
    ghost: 'text-gray-600 hover:bg-gray-100 hover:text-gray-900',
    gray: 'bg-gray-600 text-white hover:bg-gray-700'
  }

  // Tamaños
  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-5 py-2.5 text-base',
    lg: 'px-6 py-3 text-lg'
  }

  // Clases base
  const baseClasses = 'inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2'
  
  // Clases de estado
  const stateClasses = disabled || loading
    ? 'opacity-50 cursor-not-allowed'
    : 'cursor-pointer'

  // Clases de ancho
  const widthClasses = fullWidth ? 'w-full' : ''

  // Clases de focus ring según variante
  const focusRingClasses = {
    primary: 'focus:ring-pink-500',
    secondary: 'focus:ring-gray-500',
    success: 'focus:ring-green-500',
    danger: 'focus:ring-red-500',
    warning: 'focus:ring-yellow-500',
    info: 'focus:ring-blue-500',
    ghost: 'focus:ring-gray-500',
    gray: 'focus:ring-gray-500'
  }

  const classes = `
    ${baseClasses}
    ${variants[variant] || variants.primary}
    ${sizes[size] || sizes.md}
    ${stateClasses}
    ${widthClasses}
    ${focusRingClasses[variant] || focusRingClasses.primary}
    ${className}
  `.trim().replace(/\s+/g, ' ')

  const iconSize = size === 'sm' ? 'h-4 w-4' : size === 'lg' ? 'h-6 w-6' : 'h-5 w-5'

  return (
    <button
      ref={ref}
      className={classes}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <>
          <svg className={`animate-spin ${iconSize}`} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {children}
        </>
      ) : (
        <>
          {Icon && iconPosition === 'left' && <Icon className={iconSize} />}
          {children}
          {Icon && iconPosition === 'right' && <Icon className={iconSize} />}
        </>
      )}
    </button>
  )
})

Button.displayName = 'Button'

export default Button

