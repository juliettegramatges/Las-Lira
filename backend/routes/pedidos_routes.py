"""
Rutas para gestión de pedidos (Refactorizado)
Las rutas ahora delegan la lógica de negocio al PedidosService
"""

from flask import Blueprint, request, jsonify
from services.pedidos_service import PedidosService

bp = Blueprint('pedidos', __name__)


@bp.route('/', methods=['GET'], strict_slashes=False)
def listar_pedidos():
    """Listar pedidos con filtros opcionales y paginación"""
    try:
        # Recoger parámetros
        filtros = {
            'estado': request.args.get('estado'),
            'canal': request.args.get('canal'),
            'fecha_desde': request.args.get('fecha_desde'),
            'fecha_hasta': request.args.get('fecha_hasta')
        }
        buscar = request.args.get('buscar', '').strip()
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 100))

        # Delegar al servicio
        pedidos, total, total_pages = PedidosService.listar_pedidos(filtros, buscar, page, limit)

        return jsonify({
            'success': True,
            'data': [p.to_dict() for p in pedidos],
            'total': total,
            'page': page,
            'limit': limit,
            'total_pages': total_pages
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/pagados', methods=['GET'], strict_slashes=False)
def listar_pagados():
    """Listar pedidos pagados con búsqueda y paginación"""
    try:
        buscar = request.args.get('buscar', '').strip()
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))

        # Delegar al servicio
        pedidos, total, total_pages = PedidosService.listar_pagados(buscar, page, limit)

        return jsonify({
            'success': True,
            'data': [p.to_dict() for p in pedidos],
            'total': total,
            'page': page,
            'limit': limit,
            'total_pages': total_pages
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<pedido_id>', methods=['GET'])
def obtener_pedido(pedido_id):
    """Obtiene un pedido específico por ID"""
    try:
        pedido = PedidosService.obtener_pedido(pedido_id)

        if not pedido:
            return jsonify({'success': False, 'error': 'Pedido no encontrado'}), 404

        return jsonify({
            'success': True,
            'data': pedido.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/', methods=['POST'], strict_slashes=False)
def crear_pedido():
    """Crear un nuevo pedido"""
    try:
        data = request.json

        # Validar campos requeridos
        campos_requeridos = ['canal', 'cliente_nombre', 'cliente_telefono',
                            'precio_ramo', 'direccion_entrega', 'fecha_entrega']
        for campo in campos_requeridos:
            if campo not in data:
                return jsonify({
                    'success': False,
                    'error': f'Campo requerido: {campo}'
                }), 400

        # Delegar al servicio
        success, resultado, mensaje = PedidosService.crear_pedido(data)

        if success:
            return jsonify({
                'success': True,
                'data': resultado.to_dict(),
                'message': mensaje
            }), 201
        else:
            return jsonify({'success': False, 'error': mensaje}), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<pedido_id>/estado', methods=['PATCH'])
def actualizar_estado(pedido_id):
    """Actualiza el estado de un pedido"""
    try:
        data = request.json
        nuevo_estado = data.get('estado')

        if not nuevo_estado:
            return jsonify({'success': False, 'error': 'Estado requerido'}), 400

        # Delegar al servicio
        success, resultado, mensaje = PedidosService.actualizar_estado(pedido_id, nuevo_estado)

        if success:
            return jsonify({
                'success': True,
                'data': resultado.to_dict(),
                'message': mensaje
            })
        else:
            return jsonify({'success': False, 'error': mensaje}), 404 if 'no encontrado' in mensaje else 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<pedido_id>/cancelar', methods=['PATCH'])
def cancelar_pedido(pedido_id):
    """Cancela un pedido y devuelve el stock"""
    try:
        data = request.json or {}
        motivo = data.get('motivo_cancelacion')

        # Delegar al servicio
        success, resultado, mensaje = PedidosService.cancelar_pedido(pedido_id, motivo)

        if success:
            return jsonify({
                'success': True,
                'data': resultado.to_dict(),
                'message': mensaje
            })
        else:
            return jsonify({'success': False, 'error': mensaje}), 404 if 'no encontrado' in mensaje else 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<pedido_id>', methods=['DELETE'])
def eliminar_pedido(pedido_id):
    """Elimina un pedido"""
    try:
        # Delegar al servicio
        success, mensaje = PedidosService.eliminar_pedido(pedido_id)

        if success:
            return jsonify({
                'success': True,
                'message': mensaje
            })
        else:
            return jsonify({'success': False, 'error': mensaje}), 404 if 'no encontrado' in mensaje else 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<int:pedido_id>', methods=['PUT'])
def actualizar_pedido(pedido_id):
    """Actualiza un pedido existente"""
    try:
        data = request.json

        # Delegar al servicio
        success, resultado, mensaje = PedidosService.actualizar_pedido(pedido_id, data)

        if success:
            return jsonify({
                'success': True,
                'data': resultado.to_dict(),
                'message': mensaje
            })
        else:
            return jsonify({'success': False, 'error': mensaje}), 404 if 'no encontrado' in mensaje else 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/tablero', methods=['GET'])
def obtener_tablero():
    """Obtiene pedidos organizados para vista Kanban"""
    try:
        from extensions import db
        # Forzar refresh de la sesión para evitar datos en caché
        db.session.expire_all()
        
        # Convertir incluir_despachados a booleano
        incluir_despachados = request.args.get('incluir_despachados', 'false').lower() == 'true'
        
        filtros = {
            'estado': request.args.get('estado'),
            'dia_entrega': request.args.get('dia_entrega'),
            'estado_pago': request.args.get('estado_pago'),
            'tipo_pedido': request.args.get('tipo_pedido'),
            'incluir_despachados': incluir_despachados
        }

        # Delegar al servicio
        tablero = PedidosService.obtener_pedidos_tablero(filtros)

        return jsonify({
            'success': True,
            'data': tablero
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<pedido_id>/cobranza', methods=['PATCH'], strict_slashes=False)
def actualizar_cobranza(pedido_id):
    """Actualiza información de cobranza de un pedido"""
    try:
        data = request.json

        # Delegar al servicio
        success, resultado, mensaje = PedidosService.actualizar_cobranza(pedido_id, data)

        if success:
            return jsonify({
                'success': True,
                'data': resultado.to_dict(),
                'message': mensaje
            })
        else:
            return jsonify({'success': False, 'error': mensaje}), 404 if 'no encontrado' in mensaje else 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/resumen-cobranza', methods=['GET'], strict_slashes=False)
def obtener_resumen_cobranza():
    """Obtiene resumen de cobranza"""
    try:
        # Delegar al servicio
        resumen = PedidosService.obtener_resumen_cobranza()

        return jsonify({
            'success': True,
            'data': resumen
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/actualizar-estados-por-fecha', methods=['POST'], strict_slashes=False)
def actualizar_estados_por_fecha():
    """Actualiza automáticamente los estados de pedidos según su fecha de entrega"""
    try:
        # Delegar al servicio
        success, cantidad, mensaje = PedidosService.actualizar_estados_por_fecha()

        if success:
            return jsonify({
                'success': True,
                'actualizados': cantidad,
                'message': mensaje
            })
        else:
            return jsonify({'success': False, 'error': mensaje}), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<pedido_id>/foto-respaldo', methods=['POST'])
def subir_foto_respaldo(pedido_id):
    """Sube una foto de respaldo del pedido"""
    try:
        # Esta funcionalidad de upload requiere manejo especial de archivos
        # Por ahora dejamos un placeholder
        # TODO: Implementar servicio de uploads

        return jsonify({
            'success': False,
            'error': 'Funcionalidad de upload pendiente de refactorización'
        }), 501

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
