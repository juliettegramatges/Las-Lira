"""
Configuración de precios sugeridos para flores y contenedores
Valores aproximados del mercado chileno en CLP
"""

# Precios unitarios sugeridos por tipo de flor (por tallo)
PRECIOS_FLORES = {
    'Rosa': 1200,
    'Rosa Premium': 1800,
    'Clavel': 500,
    'Clavelina': 400,
    'Lirio': 2200,
    'Alstroemeria': 800,
    'Girasol': 1500,
    'Gerbera': 1000,
    'Crisantemo': 700,
    'Tulipán': 1800,
    'Hortensia': 3500,
    'Eucalipto': 600,
    'Helecho': 500,
    'Hypericum': 900,
    'Astromelia': 800,
    'Limonium': 600,
}

# Precio default si no se encuentra el tipo
PRECIO_FLORES_DEFAULT = 900

# Precios sugeridos por tipo de contenedor
PRECIOS_CONTENEDORES = {
    'Florero': 3500,
    'Macetero': 2500,
    'Canasto': 2000,
    'Base': 1500,
    'Caja': 1800,
}

# Precio default si no se encuentra el tipo
PRECIO_CONTENEDORES_DEFAULT = 2000


def obtener_precio_flor(tipo_flor):
    """
    Obtiene el precio sugerido para un tipo de flor

    Args:
        tipo_flor (str): Tipo de flor

    Returns:
        int: Precio sugerido en CLP
    """
    if not tipo_flor:
        return PRECIO_FLORES_DEFAULT

    tipo_lower = tipo_flor.lower()

    # Buscar coincidencia exacta o parcial
    for clave, precio in PRECIOS_FLORES.items():
        if clave.lower() in tipo_lower:
            return precio

    return PRECIO_FLORES_DEFAULT


def obtener_precio_contenedor(tipo_contenedor):
    """
    Obtiene el precio sugerido para un tipo de contenedor

    Args:
        tipo_contenedor (str): Tipo de contenedor

    Returns:
        int: Precio sugerido en CLP
    """
    if not tipo_contenedor:
        return PRECIO_CONTENEDORES_DEFAULT

    tipo_lower = tipo_contenedor.lower()

    # Buscar coincidencia exacta o parcial
    for clave, precio in PRECIOS_CONTENEDORES.items():
        if clave.lower() in tipo_lower:
            return precio

    return PRECIO_CONTENEDORES_DEFAULT
