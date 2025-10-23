"""
Configuración de etiquetas para el sistema (según Trello de Las-Lira)
"""

# Días de la semana con sus colores (según Trello)
DIAS_SEMANA = {
    'LUNES': {'color': '#f2d600', 'emoji': '🟡'},
    'MARTES': {'color': '#ff9f1a', 'emoji': '🟠'},
    'MIERCOLES': {'color': '#eb5a46', 'emoji': '🔴'},
    'JUEVES': {'color': '#c377e0', 'emoji': '🟣'},
    'VIERNES': {'color': '#0079bf', 'emoji': '🔵'},
    'SABADO': {'color': '#00c2e0', 'emoji': '🟦'},
    'DOMINGO': {'color': '#61bd4f', 'emoji': '🟢'}
}

# Estados de pago
ESTADOS_PAGO = {
    'Pagado': {'color': '#61bd4f', 'emoji': '🟢'},
    'No Pagado': {'color': '#eb5a46', 'emoji': '🔴'},
    'Falta Boleta o Factura': {'color': '#ff9f1a', 'emoji': '🟠'}
}

# Tipos de pedido
TIPOS_PEDIDO = [
    'EVENTO',
    'MANTENCIONES',
    'Normal'
]

def obtener_color_dia(dia):
    """Retorna el color de un día de la semana"""
    return DIAS_SEMANA.get(dia.upper(), {}).get('color', '#gray')

def obtener_emoji_dia(dia):
    """Retorna el emoji de un día de la semana"""
    return DIAS_SEMANA.get(dia.upper(), {}).get('emoji', '📅')

def obtener_color_pago(estado):
    """Retorna el color del estado de pago"""
    return ESTADOS_PAGO.get(estado, {}).get('color', '#gray')

def obtener_emoji_pago(estado):
    """Retorna el emoji del estado de pago"""
    return ESTADOS_PAGO.get(estado, {}).get('emoji', '⚪')

