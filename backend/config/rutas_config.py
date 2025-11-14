"""
Configuración para optimización de rutas
"""

# Punto de inicio predeterminado: Gran Vía 8113, Vitacura, Santiago
PUNTO_INICIO = {
    'nombre': 'Las Lira - Tienda',
    'direccion': 'Gran Vía 8113, Vitacura, Región Metropolitana, Chile',
    'latitud': -33.3730812,
    'longitud': -70.560421,
    'comuna': 'Vitacura'
}

# Configuración de horarios
HORA_INICIO_DEFAULT = '09:00'  # Hora de inicio de rutas por defecto

# Configuración de optimización
TIEMPO_ENTREGA_PROMEDIO = 10  # Minutos promedio por entrega
VELOCIDAD_PROMEDIO_KMH = 25  # Velocidad promedio en Santiago (km/h)
