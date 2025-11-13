"""
Servicio de Auditoría
Registra y consulta acciones de usuarios
"""

from extensions import db
from models.auditoria import Auditoria
from models.usuario import Usuario
from datetime import datetime, timedelta
from flask import request
import json


class AuditoriaService:
    """Servicio para operaciones de auditoría"""
    
    @staticmethod
    def registrar_accion(usuario_id, accion, entidad, entidad_id=None, detalles=None):
        """
        Registra una acción en el historial de auditoría
        
        Args:
            usuario_id: ID del usuario que realiza la acción
            accion: Tipo de acción ('crear', 'actualizar', 'eliminar', 'cambiar_estado', etc.)
            entidad: Tipo de entidad ('pedido', 'cliente', 'producto', 'cobranza', etc.)
            entidad_id: ID de la entidad afectada (opcional)
            detalles: Dict con detalles adicionales (opcional)
        
        Returns:
            bool: True si se registró correctamente
        """
        try:
            # Obtener información del usuario
            usuario = Usuario.query.get(usuario_id)
            usuario_nombre = usuario.nombre if usuario else 'Usuario Desconocido'
            
            # Obtener información de la solicitud
            ip_address = request.remote_addr if request else None
            user_agent = request.headers.get('User-Agent') if request else None
            
            # Convertir detalles a JSON string si es un dict
            detalles_str = None
            if detalles:
                if isinstance(detalles, dict):
                    detalles_str = json.dumps(detalles, ensure_ascii=False)
                else:
                    detalles_str = str(detalles)
            
            # Crear registro de auditoría
            registro = Auditoria(
                usuario_id=usuario_id,
                usuario_nombre=usuario_nombre,
                accion=accion,
                entidad=entidad,
                entidad_id=str(entidad_id) if entidad_id else None,
                detalles=detalles_str,
                ip_address=ip_address,
                user_agent=user_agent,
                fecha_accion=datetime.utcnow()
            )
            
            db.session.add(registro)
            db.session.commit()
            
            return True
        except Exception as e:
            db.session.rollback()
            print(f'Error al registrar acción de auditoría: {str(e)}')
            return False
    
    @staticmethod
    def listar_acciones(filtros=None, page=1, limit=100):
        """
        Lista acciones de auditoría con filtros y paginación
        
        Args:
            filtros: dict con usuario_id, accion, entidad, fecha_desde, fecha_hasta
            page: número de página
            limit: registros por página
        
        Returns:
            tuple: (acciones, total, total_pages)
        """
        query = Auditoria.query
        
        # Aplicar filtros
        if filtros:
            if filtros.get('usuario_id'):
                query = query.filter_by(usuario_id=filtros['usuario_id'])
            if filtros.get('accion'):
                query = query.filter_by(accion=filtros['accion'])
            if filtros.get('entidad'):
                query = query.filter_by(entidad=filtros['entidad'])
            if filtros.get('fecha_desde'):
                fecha_desde = datetime.fromisoformat(filtros['fecha_desde'])
                query = query.filter(Auditoria.fecha_accion >= fecha_desde)
            if filtros.get('fecha_hasta'):
                fecha_hasta = datetime.fromisoformat(filtros['fecha_hasta'])
                query = query.filter(Auditoria.fecha_accion <= fecha_hasta)
        
        # Contar total
        total = query.count()
        total_pages = (total + limit - 1) // limit
        
        # Paginar y ordenar por fecha descendente
        acciones = query.order_by(Auditoria.fecha_accion.desc()).limit(limit).offset((page - 1) * limit).all()
        
        return acciones, total, total_pages
    
    @staticmethod
    def obtener_estadisticas(filtros=None):
        """
        Obtiene estadísticas de acciones
        
        Args:
            filtros: dict con fecha_desde, fecha_hasta
        
        Returns:
            dict: Estadísticas de acciones
        """
        query = Auditoria.query
        
        if filtros:
            if filtros.get('fecha_desde'):
                fecha_desde = datetime.fromisoformat(filtros['fecha_desde'])
                query = query.filter(Auditoria.fecha_accion >= fecha_desde)
            if filtros.get('fecha_hasta'):
                fecha_hasta = datetime.fromisoformat(filtros['fecha_hasta'])
                query = query.filter(Auditoria.fecha_accion <= fecha_hasta)
        
        total_acciones = query.count()
        
        # Acciones por tipo
        acciones_por_tipo = db.session.query(
            Auditoria.accion,
            db.func.count(Auditoria.id).label('cantidad')
        ).group_by(Auditoria.accion).all()
        
        # Acciones por entidad
        acciones_por_entidad = db.session.query(
            Auditoria.entidad,
            db.func.count(Auditoria.id).label('cantidad')
        ).group_by(Auditoria.entidad).all()
        
        # Acciones por usuario
        acciones_por_usuario = db.session.query(
            Auditoria.usuario_nombre,
            db.func.count(Auditoria.id).label('cantidad')
        ).group_by(Auditoria.usuario_nombre).all()
        
        return {
            'total_acciones': total_acciones,
            'acciones_por_tipo': {tipo: cantidad for tipo, cantidad in acciones_por_tipo},
            'acciones_por_entidad': {entidad: cantidad for entidad, cantidad in acciones_por_entidad},
            'acciones_por_usuario': {usuario: cantidad for usuario, cantidad in acciones_por_usuario}
        }

