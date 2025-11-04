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
    - Si es dentro de esta SEMANA (días 3-7, no hoy ni mañana) → "Pedidos Semana"
    - Si es más allá de esta semana → "Pedidos Semana" (planificación futura)
    - Si es PASADO → "Pedidos Semana" (por ahora, pero idealmente deberían estar en otro estado)
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
    
    # Comparar fechas correctamente
    if fecha_entrega_date == hoy:
        return 'Entregas de Hoy'
    elif fecha_entrega_date == manana:
        return 'Entregas para Mañana'
    elif fecha_entrega_date > manana and fecha_entrega_date <= fin_semana:
        # Días 3-7 de esta semana (no hoy ni mañana)
        return 'Pedidos Semana'
    elif fecha_entrega_date > fin_semana:
        # Más allá de esta semana
        return 'Pedidos Semana'
    else:
        # Fecha pasada (antes de hoy) - también ir a "Pedidos Semana" por ahora
        # TODO: Estos deberían estar en otro estado o no aparecer en el tablero
        return 'Pedidos Semana'


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

