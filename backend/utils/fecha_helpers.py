"""
Utilidades para manejo de fechas y clasificación de pedidos
"""

from datetime import datetime, timedelta

def obtener_estado_por_fecha(fecha_entrega):
    """
    Determina el estado inicial del pedido según su fecha de entrega

    Flujo de estados automáticos:
    1. "Entregas de Hoy" → fecha_entrega es HOY
    2. "Entregas para Mañana" → fecha_entrega es MAÑANA
    3. "Entregas Semana" → fecha_entrega es esta semana (pero no hoy ni mañana)
    4. "Entregas Próx Semana" → fecha_entrega es la próxima semana
    5. "Entregas Este Mes" → fecha_entrega es este mes (pero no esta ni próxima semana)
    6. "Entregas Próx Mes" → fecha_entrega es el próximo mes
    7. "Entregas Futuras" → fecha_entrega más allá del próximo mes

    Después manualmente:
    8. "En Proceso" → se está preparando
    9. "Listo para Despacho" → terminado, listo para enviar
    10. "Despachados" → ya fue entregado
    """
    ahora = datetime.now()
    hoy = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
    manana = hoy + timedelta(days=1)

    # Calcular fin de semana actual (domingo)
    fin_semana_actual = hoy + timedelta(days=(6 - hoy.weekday()))

    # Calcular fin de próxima semana (domingo de próxima semana)
    fin_proxima_semana = fin_semana_actual + timedelta(days=7)

    # Calcular fin de este mes
    if hoy.month == 12:
        fin_este_mes = hoy.replace(year=hoy.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        fin_este_mes = hoy.replace(month=hoy.month + 1, day=1) - timedelta(days=1)

    # Calcular fin del próximo mes
    # Primero obtenemos el inicio del mes siguiente
    if hoy.month == 12:
        inicio_mes_siguiente = hoy.replace(year=hoy.year + 1, month=1, day=1)
    else:
        inicio_mes_siguiente = hoy.replace(month=hoy.month + 1, day=1)

    # Luego el fin del mes después de ese
    if inicio_mes_siguiente.month == 12:
        fin_proximo_mes = inicio_mes_siguiente.replace(year=inicio_mes_siguiente.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        fin_proximo_mes = inicio_mes_siguiente.replace(month=inicio_mes_siguiente.month + 1, day=1) - timedelta(days=1)

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
    elif fecha_entrega_date > manana and fecha_entrega_date <= fin_semana_actual:
        # Resto de esta semana (no hoy ni mañana)
        return 'Entregas Semana'
    elif fecha_entrega_date > fin_semana_actual and fecha_entrega_date <= fin_proxima_semana:
        # Próxima semana
        return 'Entregas Próx Semana'
    elif fecha_entrega_date > fin_proxima_semana and fecha_entrega_date <= fin_este_mes:
        # Este mes (después de próxima semana)
        return 'Entregas Este Mes'
    elif fecha_entrega_date > fin_este_mes and fecha_entrega_date <= fin_proximo_mes:
        # Próximo mes
        return 'Entregas Próx Mes'
    elif fecha_entrega_date > fin_proximo_mes:
        # Más allá del próximo mes
        return 'Entregas Futuras'
    else:
        # Fecha pasada (antes de hoy) - van a "Entregas de Hoy" para revisión urgente
        return 'Entregas de Hoy'


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

