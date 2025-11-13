"""
Rutas de Auditoría
Solo accesibles para administradores
"""

from flask import Blueprint, jsonify, request
from extensions import db
from services.auditoria_service import AuditoriaService
from routes.auth_routes import require_auth, require_role
from models.auditoria import Auditoria

bp = Blueprint('auditoria', __name__, url_prefix='/api/auditoria')


@bp.route('/acciones', methods=['GET'])
@require_auth
@require_role('admin')
def listar_acciones():
    """Lista acciones de auditoría con filtros y paginación"""
    try:
        # Obtener parámetros de filtro
        filtros = {}
        if request.args.get('usuario_id'):
            filtros['usuario_id'] = request.args.get('usuario_id')
        if request.args.get('accion'):
            filtros['accion'] = request.args.get('accion')
        if request.args.get('entidad'):
            filtros['entidad'] = request.args.get('entidad')
        if request.args.get('fecha_desde'):
            filtros['fecha_desde'] = request.args.get('fecha_desde')
        if request.args.get('fecha_hasta'):
            filtros['fecha_hasta'] = request.args.get('fecha_hasta')
        
        # Paginación (máximo 50 por página para evitar sobrecarga)
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 50)), 50)  # Máximo 50
        
        # Obtener acciones
        acciones, total, total_pages = AuditoriaService.listar_acciones(filtros, page, limit)
        
        return jsonify({
            'success': True,
            'data': [accion.to_dict() for accion in acciones],
            'total': total,
            'page': page,
            'total_pages': total_pages
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/estadisticas', methods=['GET'])
@require_auth
@require_role('admin')
def obtener_estadisticas():
    """Obtiene estadísticas de acciones"""
    try:
        filtros = {}
        if request.args.get('fecha_desde'):
            filtros['fecha_desde'] = request.args.get('fecha_desde')
        if request.args.get('fecha_hasta'):
            filtros['fecha_hasta'] = request.args.get('fecha_hasta')
        
        estadisticas = AuditoriaService.obtener_estadisticas(filtros)
        
        return jsonify({
            'success': True,
            'data': estadisticas
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/usuarios', methods=['GET'])
@require_auth
@require_role('admin')
def listar_usuarios_activos():
    """Lista todos los usuarios activos para el filtro de auditoría"""
    try:
        from models.usuario import Usuario
        
        # Usar exactamente el mismo método que auth_routes.listar_usuarios
        usuarios = Usuario.query.all()
        
        return jsonify({
            'success': True,
            'data': [u.to_dict() for u in usuarios]
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

