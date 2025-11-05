"""
Utilidades para manejo de ubicaciones y direcciones
"""

from config.comunas import COMUNAS_PRECIOS


def extraer_comuna(direccion):
    """
    Extrae el nombre de la comuna de una dirección
    Intenta identificar la comuna en el texto de la dirección

    Args:
        direccion (str): Dirección completa de entrega

    Returns:
        str: Nombre de la comuna identificada o 'Sin especificar'

    Examples:
        >>> extraer_comuna("Av. Principal 123, Santiago")
        'Santiago'
        >>> extraer_comuna("Calle Falsa 456, Las Condes")
        'Las Condes'
    """
    if not direccion:
        return 'Sin especificar'

    direccion_lower = direccion.lower()

    # Buscar coincidencias con comunas conocidas
    for comuna in COMUNAS_PRECIOS.keys():
        if comuna.lower() in direccion_lower:
            return comuna

    # Si no se encuentra, intentar extraer la última parte de la dirección
    # que típicamente es la comuna
    partes = direccion.split(',')
    if len(partes) >= 2:
        posible_comuna = partes[-1].strip()

        # Buscar coincidencia parcial
        for comuna in COMUNAS_PRECIOS.keys():
            if posible_comuna.lower() in comuna.lower() or comuna.lower() in posible_comuna.lower():
                return comuna

        return posible_comuna

    return 'Sin especificar'
