import { useState } from 'react'

/**
 * Componente para mostrar una etiqueta de cliente con tooltip
 */
function EtiquetaCliente({ etiqueta, mostrarDescripcion = true, size = 'md' }) {
  const [showTooltip, setShowTooltip] = useState(false)
  
  // Tamaños
  const sizes = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-2.5 py-1',
    lg: 'text-base px-3 py-1.5'
  }
  
  const iconSizes = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base'
  }
  
  if (!etiqueta) return null
  
  return (
    <div className="relative inline-block">
      <span
        className={`
          inline-flex items-center gap-1.5 rounded-full font-medium
          transition-all duration-200 cursor-help
          ${sizes[size]}
        `}
        style={{
          backgroundColor: `${etiqueta.color}15`,
          color: etiqueta.color,
          border: `1px solid ${etiqueta.color}30`
        }}
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
      >
        {etiqueta.icono && (
          <span className={iconSizes[size]}>{etiqueta.icono}</span>
        )}
        <span>{etiqueta.nombre}</span>
      </span>
      
      {/* Tooltip con descripción */}
      {mostrarDescripcion && showTooltip && etiqueta.descripcion && (
        <div 
          className="absolute z-[9999] bottom-full left-1/2 -translate-x-1/2 mb-2 w-64 pointer-events-none"
          style={{ minWidth: '200px' }}
        >
          <div 
            className="rounded-lg shadow-xl p-3 border-2"
            style={{
              backgroundColor: 'white',
              borderColor: etiqueta.color
            }}
          >
            <div className="flex items-center gap-2 mb-2 pb-2 border-b" style={{ borderColor: `${etiqueta.color}30` }}>
              <span className="text-lg">{etiqueta.icono}</span>
              <span className="font-bold text-sm" style={{ color: etiqueta.color }}>
                {etiqueta.nombre}
              </span>
            </div>
            <p className="text-xs text-gray-600 leading-relaxed">
              {etiqueta.descripcion}
            </p>
            {etiqueta.categoria && (
              <p className="text-xs text-gray-400 mt-2 pt-2 border-t border-gray-100">
                Categoría: <span className="font-medium">{etiqueta.categoria}</span>
              </p>
            )}
          </div>
          {/* Flecha del tooltip */}
          <div 
            className="absolute top-full left-1/2 -translate-x-1/2 -mt-1"
            style={{
              width: 0,
              height: 0,
              borderLeft: '6px solid transparent',
              borderRight: '6px solid transparent',
              borderTop: `6px solid ${etiqueta.color}`
            }}
          />
        </div>
      )}
    </div>
  )
}

export default EtiquetaCliente

