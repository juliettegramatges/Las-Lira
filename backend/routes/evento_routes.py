"""
Rutas para gestión de eventos (Refactorizado)
Las rutas ahora delegan la lógica de negocio al EventosService
"""

from flask import Blueprint, request, jsonify
from services.eventos_service import EventosService

bp = Blueprint('eventos', __name__)


@bp.route('/', methods=['GET'])
def obtener_eventos():
    """Obtiene todos los eventos"""
    try:
        eventos = EventosService.listar_eventos()
        return jsonify({
            'success': True,
            'data': [evento.to_dict() for evento in eventos]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<evento_id>', methods=['GET'])
def obtener_evento(evento_id):
    """Obtiene un evento específico con sus insumos"""
    try:
        evento = EventosService.obtener_evento(evento_id)
        if not evento:
            return jsonify({'success': False, 'error': 'Evento no encontrado'}), 404

        evento_dict = evento.to_dict()
        evento_dict['insumos'] = [insumo.to_dict() for insumo in evento.insumos]

        return jsonify({
            'success': True,
            'data': evento_dict
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<evento_id>', methods=['PUT'])
def actualizar_evento(evento_id):
    """Actualiza un evento existente"""
    try:
        data = request.get_json()

        # Delegar al servicio
        success, resultado, mensaje = EventosService.actualizar_evento(evento_id, data)

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


@bp.route('/<evento_id>', methods=['DELETE'])
def eliminar_evento(evento_id):
    """Elimina un evento y todos sus insumos"""
    try:
        print(f"🗑️ Eliminando evento: {evento_id}")
        # Delegar al servicio
        success, mensaje = EventosService.eliminar_evento(evento_id)

        if success:
            print(f"✅ Evento {evento_id} eliminado exitosamente")
            return jsonify({
                'success': True,
                'message': mensaje
            })
        else:
            print(f"❌ Error al eliminar evento {evento_id}: {mensaje}")
            return jsonify({'success': False, 'error': mensaje}), 404 if 'no encontrado' in mensaje.lower() else 500

    except Exception as e:
        print(f"❌ Excepción al eliminar evento {evento_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/', methods=['POST'])
def crear_evento():
    """Crea un nuevo evento (Cotización)"""
    try:
        data = request.get_json()

        # Validar campos requeridos
        if not data.get('cliente_nombre'):
            return jsonify({
                'success': False,
                'error': 'Campo requerido: cliente_nombre'
            }), 400

        # Delegar al servicio
        success, resultado, mensaje = EventosService.crear_evento(data)

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


@bp.route('/<evento_id>/insumos', methods=['POST'])
def agregar_insumo(evento_id):
    """Agrega un insumo al evento"""
    try:
        data = request.get_json()

        # Validar campos requeridos
        tipo_insumo = data.get('tipo_insumo') or data.get('insumo_tipo')
        if not tipo_insumo:
            return jsonify({
                'success': False,
                'error': 'Campo requerido: tipo_insumo'
            }), 400

        if 'cantidad' not in data:
            return jsonify({
                'success': False,
                'error': 'Campo requerido: cantidad'
            }), 400

        # Delegar al servicio
        success, resultado, mensaje = EventosService.agregar_insumo(evento_id, data)

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


@bp.route('/<evento_id>/insumos/<int:insumo_id>', methods=['DELETE'])
def eliminar_insumo(evento_id, insumo_id):
    """Elimina un insumo del evento"""
    try:
        # Delegar al servicio
        success, resultado, mensaje = EventosService.eliminar_insumo(evento_id, insumo_id)

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


@bp.route('/<evento_id>/estado', methods=['PUT'])
def cambiar_estado(evento_id):
    """Cambia el estado de un evento"""
    try:
        data = request.get_json()
        nuevo_estado = data.get('estado')

        if not nuevo_estado:
            return jsonify({'success': False, 'error': 'Campo requerido: estado'}), 400

        # Delegar al servicio
        success, resultado, mensaje = EventosService.cambiar_estado(evento_id, nuevo_estado)

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


@bp.route('/<evento_id>/reservar-insumos', methods=['POST'])
def reservar_insumos(evento_id):
    """Reserva los insumos del evento"""
    try:
        # Delegar al servicio
        success, detalle, mensaje = EventosService.reservar_insumos(evento_id)

        if success:
            return jsonify({
                'success': True,
                'reservados': detalle,
                'message': mensaje
            })
        else:
            return jsonify({
                'success': False,
                'error': mensaje,
                'faltantes': detalle
            }), 400 if detalle else 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<evento_id>/descontar-stock', methods=['POST'])
def descontar_stock(evento_id):
    """Descuenta el stock de los insumos del evento"""
    try:
        # Delegar al servicio
        success, detalle, mensaje = EventosService.descontar_stock(evento_id)

        if success:
            return jsonify({
                'success': True,
                'descontados': detalle,
                'message': mensaje
            })
        else:
            return jsonify({'success': False, 'error': mensaje}), 404 if 'no encontrado' in mensaje else 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<evento_id>/marcar-devuelto', methods=['POST'])
def marcar_devuelto(evento_id):
    """Marca los insumos como devueltos"""
    try:
        # Delegar al servicio
        success, detalle, mensaje = EventosService.marcar_devuelto(evento_id)

        if success:
            return jsonify({
                'success': True,
                'devueltos': detalle,
                'message': mensaje
            })
        else:
            return jsonify({'success': False, 'error': mensaje}), 404 if 'no encontrado' in mensaje else 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/productos-evento', methods=['GET'])
def obtener_productos_evento():
    """Obtiene todos los productos de eventos"""
    try:
        productos = EventosService.obtener_productos_evento()

        return jsonify({
            'success': True,
            'data': [p.to_dict() for p in productos]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
