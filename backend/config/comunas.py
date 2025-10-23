"""
Configuración de comunas de Santiago y sus precios de envío
"""

# Diccionario de comunas con sus precios estándar de envío
COMUNAS_PRECIOS = {
    # $7,000
    "Las Condes": 7000,
    "Lo Barnechea bajo": 7000,
    "Vitacura": 7000,
    
    # $9,000
    "El Arrayán bajo": 9000,
    
    # $10,000
    "Providencia": 10000,
    
    # $12,000
    "Clinica Alemana": 12000,
    "Clinica Las Condes": 12000,
    "Clinica Los Andes": 12000,
    "El Arrayán alto": 12000,
    "Lo Barnechea Alto": 12000,
    "Recoleta": 12000,
    
    # $15,000
    "Conchalí": 15000,
    "La Reina": 15000,
    "Parque del Recuerdo": 15000,
    "Santiago Centro": 15000,
    "Ñuñoa": 15000,
    
    # $18,000
    "Huechuraba": 18000,
    "Independencia": 18000,
    
    # $20,000
    "La Granja": 20000,
    "Lo Espejo": 20000,
    "Macul": 20000,
    "Quilicura": 20000,
    "Quinta Normal": 20000,
    "San Joaquín": 20000,
    
    # $22,000
    "Cerro Navia": 22000,
    "Lo Prado": 22000,
    
    # $25,000
    "Cerrillos": 25000,
    "El Bosque": 25000,
    "Estación Central": 25000,
    "La Cisterna": 25000,
    "La Florida": 25000,
    "Peñalolén": 25000,
    "Peñalolen": 25000,  # Variante sin tilde
    "Pudahuel": 25000,
    "Renca": 25000,
    "Carrascal": 25000,
    "Renca / Carrascal": 25000,
    "San Miguel": 25000,
    "San Ramón": 25000,
    
    # $30,000
    "Colina": 30000,
    "Chicureo": 30000,
    "Colina - Chicureo": 30000,
    "La Pintana": 30000,
    "Maipú": 30000,
    "Padre Hurtado": 30000,
    "Pedro Aguirre Cerda": 30000,
    "Peñaflor": 30000,
    "Puente Alto": 30000,
    "San Bernardo": 30000,
    "Talagante": 30000,
    
    # $35,000
    "Pirque": 35000,
}

# Lista de comunas ordenadas por precio (para dropdown/select)
COMUNAS_ORDENADAS = sorted(COMUNAS_PRECIOS.keys())

# Agrupar comunas por precio
def obtener_comunas_por_precio():
    """Retorna diccionario agrupando comunas por precio"""
    precios_comunas = {}
    for comuna, precio in COMUNAS_PRECIOS.items():
        if precio not in precios_comunas:
            precios_comunas[precio] = []
        precios_comunas[precio].append(comuna)
    return dict(sorted(precios_comunas.items()))

def obtener_precio_envio(comuna):
    """
    Obtiene el precio de envío para una comuna específica.
    Retorna None si la comuna no existe.
    """
    return COMUNAS_PRECIOS.get(comuna)

def buscar_comuna_similar(texto):
    """
    Busca una comuna que coincida parcialmente con el texto dado.
    Útil para encontrar comunas a partir de direcciones.
    """
    texto_lower = texto.lower()
    for comuna in COMUNAS_PRECIOS.keys():
        if comuna.lower() in texto_lower:
            return comuna
    return None

# Alias para compatibilidad con rutas_routes.py
def obtener_precio_comuna(comuna):
    """Alias para obtener_precio_envio"""
    return obtener_precio_envio(comuna)

# Zonas geográficas para organización
ZONAS = {
    "Zona Alta": ["Las Condes", "Vitacura", "Lo Barnechea bajo", "Lo Barnechea Alto", "El Arrayán bajo", "El Arrayán alto"],
    "Zona Centro": ["Providencia", "Ñuñoa", "Santiago Centro", "Recoleta", "Independencia"],
    "Zona Oriente": ["La Reina", "Peñalolén", "Peñalolen", "Macul", "La Florida"],
    "Zona Sur": ["San Miguel", "La Granja", "San Joaquín", "La Cisterna", "El Bosque", "San Ramón", 
                 "La Pintana", "Puente Alto", "San Bernardo", "Pedro Aguirre Cerda"],
    "Zona Poniente": ["Maipú", "Cerrillos", "Estación Central", "Quinta Normal", "Pudahuel", 
                      "Lo Prado", "Cerro Navia", "Renca", "Carrascal", "Renca / Carrascal"],
    "Zona Norte": ["Quilicura", "Huechuraba", "Conchalí", "Colina", "Chicureo", "Colina - Chicureo"],
    "Zona Periférica": ["Padre Hurtado", "Peñaflor", "Talagante", "Pirque", "Lo Espejo"],
    "Clínicas": ["Clinica Alemana", "Clinica Las Condes", "Clinica Los Andes", "Parque del Recuerdo"]
}

def obtener_zona_comuna(comuna):
    """
    Obtiene la zona geográfica de una comuna
    """
    for zona, comunas in ZONAS.items():
        if comuna in comunas:
            return zona
    return "Otra"
