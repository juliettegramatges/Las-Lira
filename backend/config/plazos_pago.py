"""
Configuración de plazos de pago según tipo de cliente
"""

# Plazos de pago en días según tipo de cliente
PLAZOS_PAGO = {
    'Nuevo': 0,           # Pago inmediato
    'Fiel': 15,           # 15 días de plazo
    'Cumplidor': 30,      # 30 días de plazo
    'No Cumplidor': 0,    # Sin plazo, pago inmediato
    'VIP': 45,            # 45 días de plazo
    'Ocasional': 7        # 7 días de plazo
}

def obtener_plazo_pago(tipo_cliente):
    """
    Obtiene el plazo de pago en días según el tipo de cliente
    
    Args:
        tipo_cliente (str): Tipo de cliente (Nuevo, Fiel, Cumplidor, etc.)
        
    Returns:
        int: Días de plazo para pagar
    """
    return PLAZOS_PAGO.get(tipo_cliente, 0)

def calcular_fecha_vencimiento(fecha_pedido, plazo_dias):
    """
    Calcula la fecha de vencimiento del pago
    
    Args:
        fecha_pedido (datetime): Fecha del pedido
        plazo_dias (int): Días de plazo
        
    Returns:
        datetime: Fecha de vencimiento
    """
    from datetime import timedelta
    return fecha_pedido + timedelta(days=plazo_dias)

