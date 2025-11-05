"""
Utilidades para manejo de números de teléfono
"""

import re


def normalizar_telefono(telefono):
    """
    Normaliza un número de teléfono eliminando caracteres no numéricos

    Args:
        telefono: Número de teléfono a normalizar (str o None)

    Returns:
        str: Teléfono normalizado (solo dígitos y +)

    Examples:
        >>> normalizar_telefono("+56 9 1234 5678")
        '+56912345678'
        >>> normalizar_telefono("(56) 912-345-678")
        '56912345678'
        >>> normalizar_telefono(None)
        ''
    """
    if not telefono:
        return ""
    # Eliminar todo excepto dígitos y +
    return re.sub(r'[^\d+]', '', str(telefono))
