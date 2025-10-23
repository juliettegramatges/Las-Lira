"""
Configuración de etiquetas estandarizadas para cobranza

FLUJO:
1. ¿Está pagado? → Pagado / No Pagado
2. Si está pagado, ¿cómo? → Tr. BICE, Tr. Santander, etc.
3. ¿Documento? → Hacer boleta → Boleta N° XXX
"""

# 💰 ETAPA 1: Estado de Pago (¿Está pagado o no?)
ESTADOS_PAGO = [
    'No Pagado',  # DEFAULT
    'Pagado',
]

# 💳 ETAPA 2: Métodos de Pago (solo si está pagado)
METODOS_PAGO = [
    'Tr. BICE',
    'Tr. Santander',
    'Tr. Itaú',
    'Pago con tarjeta',
    'Efectivo',
    'Otro',
]

# 🧾 ETAPA 3: Documentos Tributarios
DOCUMENTOS_TRIBUTARIOS = [
    'Hacer boleta',      # DEFAULT
    'Hacer factura',
    'Boleta emitida',
    'Factura emitida',
    'No requiere',
]

def get_label_pago(metodo, numero_doc=None):
    """
    Retorna el label formateado del método de pago
    """
    return f"💰 {metodo}"

def get_label_documento(documento, numero=None):
    """
    Retorna el label formateado del documento
    """
    if documento in ['Boleta emitida', 'Factura emitida'] and numero:
        tipo = 'Boleta' if 'Boleta' in documento else 'Factura'
        return f"🧾 {tipo} N° {numero}"
    return f"🧾 {documento}"

def validar_metodo_pago(metodo):
    """Valida que el método de pago sea válido"""
    return metodo in METODOS_PAGO

def validar_documento(documento):
    """Valida que el documento sea válido"""
    return documento in DOCUMENTOS_TRIBUTARIOS

