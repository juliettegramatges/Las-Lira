"""
Helper para registrar acciones de auditoría automáticamente
"""

from flask import session
from services.auditoria_service import AuditoriaService


def registrar_accion(accion, entidad, entidad_id=None, detalles=None):
    """
    Helper para registrar una acción de auditoría automáticamente
    Obtiene el usuario de la sesión actual
    
    Args:
        accion: Tipo de acción ('crear', 'actualizar', 'eliminar', 'cambiar_estado', etc.)
        entidad: Tipo de entidad ('pedido', 'cliente', 'producto', 'cobranza', etc.)
        entidad_id: ID de la entidad afectada (opcional)
        detalles: Dict con detalles adicionales (opcional)
    """
    try:
        user_id = session.get('user_id')
        if user_id:
            AuditoriaService.registrar_accion(
                usuario_id=user_id,
                accion=accion,
                entidad=entidad,
                entidad_id=entidad_id,
                detalles=detalles
            )
    except Exception as e:
        # No fallar si hay error en auditoría
        pass

