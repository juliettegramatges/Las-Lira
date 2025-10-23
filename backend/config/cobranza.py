"""
Configuración de etiquetas estandarizadas para cobranza
"""

# 💰 Métodos de Pago (estandarizados)
METODOS_PAGO = [
    'Pendiente',
    'Tr. BICE',
    'Tr. Santander',
    'Tr. Itaú',
    'Tr. Falta transferencia',
    'Pago confirmado',
    'Pago con tarjeta',
]

# 🧾 Documentos Tributarios (estandarizados)
DOCUMENTOS_TRIBUTARIOS = [
    'Hacer boleta',
    'Hacer factura',
    'Falta boleta o factura',
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

