"""
Configuración de stock sugerido para flores y contenedores
Valores razonables por rotación aproximada
"""

# Stock sugerido por tipo de flor (unidades)
STOCK_FLORES = {
    'Clavel': 50,
    'Clavelina': 60,
    'Alstroemeria': 40,
    'Astromelia': 40,
    'Rosa Premium': 24,
    'Rosa': 30,
    'Gerbera': 24,
    'Girasol': 18,
    'Lirio': 18,
    'Tulipán': 18,
    'Crisantemo': 30,
    'Hortensia': 12,
    'Eucalipto': 60,
    'Helecho': 40,
    'Hypericum': 24,
    'Limonium': 40,
    'Anémona': 20,
    'Amaryllis': 12,
}

# Stock default si no se encuentra el tipo
STOCK_FLORES_DEFAULT = 20

# Stock sugerido por tipo de contenedor (unidades)
STOCK_CONTENEDORES = {
    'Florero': 8,
    'Macetero': 10,
    'Canasto': 6,
    'Base': 12,
    'Caja': 8,
}

# Stock default si no se encuentra el tipo
STOCK_CONTENEDORES_DEFAULT = 8


def obtener_stock_flor(tipo_flor):
    """
    Obtiene el stock sugerido para un tipo de flor

    Args:
        tipo_flor (str): Tipo de flor

    Returns:
        int: Stock sugerido en unidades
    """
    if not tipo_flor:
        return STOCK_FLORES_DEFAULT

    tipo_lower = tipo_flor.lower()

    # Buscar coincidencia exacta o parcial
    for clave, stock in STOCK_FLORES.items():
        if clave.lower() in tipo_lower:
            return stock

    return STOCK_FLORES_DEFAULT


def obtener_stock_contenedor(tipo_contenedor):
    """
    Obtiene el stock sugerido para un tipo de contenedor

    Args:
        tipo_contenedor (str): Tipo de contenedor

    Returns:
        int: Stock sugerido en unidades
    """
    if not tipo_contenedor:
        return STOCK_CONTENEDORES_DEFAULT

    tipo_lower = tipo_contenedor.lower()

    # Buscar coincidencia exacta o parcial
    for clave, stock in STOCK_CONTENEDORES.items():
        if clave.lower() in tipo_lower:
            return stock

    return STOCK_CONTENEDORES_DEFAULT
