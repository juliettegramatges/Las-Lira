"""
Rutas para gestionar colores y flores de productos
"""

from flask import Blueprint, request, jsonify
from services.producto_colores_service import ProductoColoresService

bp = Blueprint('producto_colores', __name__)


@bp.route('/<producto_id>/colores-sugeridos', methods=['GET'])
def obtener_colores_sugeridos(producto_id):
    """Obtiene los colores sugeridos desde colores_asociados del producto"""
    success, data, message = ProductoColoresService.obtener_colores_sugeridos(producto_id)

    if success:
        return jsonify({'success': True, 'data': data})
    else:
        status_code = 404 if 'no encontrado' in message.lower() else 500
        return jsonify({'success': False, 'error': message}), status_code


@bp.route('/<producto_id>/colores', methods=['GET'])
def obtener_colores_producto(producto_id):
    """Obtiene todos los colores configurados para un producto"""
    success, data, message = ProductoColoresService.listar_colores_producto(producto_id)

    if success:
        return jsonify({'success': True, 'data': data})
    else:
        status_code = 404 if 'no encontrado' in message.lower() else 500
        return jsonify({'success': False, 'error': message}), status_code


@bp.route('/<producto_id>/colores', methods=['POST'])
def crear_color_producto(producto_id):
    """Crea un nuevo color para un producto"""
    data = request.get_json()
    success, result, message = ProductoColoresService.crear_color_producto(producto_id, data)

    if success:
        return jsonify({'success': True, 'data': result, 'message': message}), 201
    else:
        status_code = 404 if 'no encontrado' in message.lower() else 400
        return jsonify({'success': False, 'error': message}), status_code


@bp.route('/colores/<int:color_id>', methods=['PUT'])
def actualizar_color(color_id):
    """Actualiza un color existente"""
    data = request.get_json()
    success, result, message = ProductoColoresService.actualizar_color(color_id, data)

    if success:
        return jsonify({'success': True, 'data': result, 'message': message})
    else:
        status_code = 404 if 'no encontrado' in message.lower() else 400
        return jsonify({'success': False, 'error': message}), status_code


@bp.route('/colores/<int:color_id>', methods=['DELETE'])
def eliminar_color(color_id):
    """Elimina (desactiva) un color"""
    success, _, message = ProductoColoresService.eliminar_color(color_id)

    if success:
        return jsonify({'success': True, 'message': message})
    else:
        status_code = 404 if 'no encontrado' in message.lower() else 400
        return jsonify({'success': False, 'error': message}), status_code


@bp.route('/colores/<int:color_id>/flores', methods=['POST'])
def agregar_flor_a_color(color_id):
    """Agrega una flor a un color"""
    data = request.get_json()
    success, result, message = ProductoColoresService.agregar_flor_a_color(color_id, data)

    if success:
        return jsonify({'success': True, 'data': result, 'message': message}), 201
    else:
        status_code = 404 if 'no encontrado' in message.lower() else 400
        return jsonify({'success': False, 'error': message}), status_code


@bp.route('/colores/flores/<int:color_flor_id>', methods=['DELETE'])
def eliminar_flor_de_color(color_flor_id):
    """Elimina una flor de un color"""
    success, _, message = ProductoColoresService.eliminar_flor_de_color(color_flor_id)

    if success:
        return jsonify({'success': True, 'message': message})
    else:
        status_code = 404 if 'no encontrado' in message.lower() else 400
        return jsonify({'success': False, 'error': message}), status_code


@bp.route('/colores/flores/<int:color_flor_id>/predeterminada', methods=['PUT'])
def marcar_flor_predeterminada(color_flor_id):
    """Marca una flor como predeterminada para su color"""
    success, result, message = ProductoColoresService.marcar_flor_predeterminada(color_flor_id)

    if success:
        return jsonify({'success': True, 'data': result, 'message': message})
    else:
        status_code = 404 if 'no encontrado' in message.lower() else 400
        return jsonify({'success': False, 'error': message}), status_code


@bp.route('/<producto_id>/configuracion-completa', methods=['GET'])
def obtener_configuracion_completa(producto_id):
    """Obtiene la configuración completa de colores y flores de un producto"""
    success, data, message = ProductoColoresService.obtener_configuracion_completa(producto_id)

    if success:
        return jsonify({'success': True, 'data': data})
    else:
        status_code = 404 if 'no encontrado' in message.lower() else 500
        return jsonify({'success': False, 'error': message}), status_code


@bp.route('/<producto_id>/guardar-receta-completa', methods=['POST'])
def guardar_receta_completa(producto_id):
    """
    Guarda la configuración completa del recetario desde el simulador.
    Actualiza colores, flores asociadas, flores predeterminadas y precio de venta.

    Body esperado:
    {
        "colores": [
            {
                "id": "color-123" o "nuevo-timestamp",
                "nombre_color": "Rojo",
                "cantidad_flores_sugerida": 12,
                "flores": [
                    {
                        "flor_id": "FL001",
                        "es_predeterminada": true
                    }
                ]
            }
        ],
        "precio_venta": 25000
    }
    """
    data = request.get_json()
    success, result, message = ProductoColoresService.guardar_receta_completa(producto_id, data)

    if success:
        return jsonify({'success': True, 'data': result, 'message': message})
    else:
        status_code = 404 if 'no encontrado' in message.lower() else 400
        return jsonify({'success': False, 'error': message}), status_code
