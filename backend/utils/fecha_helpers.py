"""
Utilidades para manejo de fechas y clasificación de pedidos
"""

from datetime import datetime, timedelta

def obtener_estado_por_fecha(fecha_entrega):
    """
    Determina el estado inicial del pedido según su fecha de entrega
    
    Reglas:
    - Si es para HOY → "Entregas de Hoy"
    - Si es para MAÑANA → "Entregas para Mañana"
    - Si es dentro de esta SEMANA (próximos 7 días) → "Pedidos Semana"
    - Resto → "Pedidos Semana" (estado inicial para planificación)
    """
    ahora = datetime.now()
    hoy = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
    manana = hoy + timedelta(days=1)
    fin_semana = hoy + timedelta(days=7)
    
    # Si la fecha_entrega es un datetime naive, convertirla a aware o viceversa
    if fecha_entrega.tzinfo is None:
        fecha_entrega_date = fecha_entrega.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        # Si viene con timezone, quitarla para comparar
        fecha_entrega_date = fecha_entrega.replace(tzinfo=None).replace(hour=0, minute=0, second=0, microsecond=0)
    
    if fecha_entrega_date == hoy:
        return 'Entregas de Hoy'
    elif fecha_entrega_date == manana:
        return 'Entregas para Mañana'
    elif hoy < fecha_entrega_date <= fin_semana:
        return 'Pedidos Semana'
    else:
        return 'Pedidos Semana'  # Pedidos futuros van a planificación semanal


def obtener_dia_semana(fecha):
    """
    Obtiene el nombre del día de la semana en español (mayúsculas)
    """
    dias = {
        0: 'LUNES',
        1: 'MARTES',
        2: 'MIERCOLES',
        3: 'JUEVES',
        4: 'VIERNES',
        5: 'SABADO',
        6: 'DOMINGO'
    }
    return dias[fecha.weekday()]


def clasificar_pedido(fecha_entrega):
    """
    Clasifica un pedido según su fecha de entrega
    Retorna dict con estado y día de la semana
    """
    estado = obtener_estado_por_fecha(fecha_entrega)
    dia_semana = obtener_dia_semana(fecha_entrega)
    
    return {
        'estado': estado,
        'dia_entrega': dia_semana
    }

