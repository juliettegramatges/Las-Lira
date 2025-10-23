"""
Rutas para gestión de pedidos
"""

from flask import Blueprint, request, jsonify
from backend.app import db
from backend.models.pedido import Pedido, PedidoInsumo
from datetime import datetime

bp = Blueprint('pedidos', __name__)

@bp.route('/', methods=['GET'])
def listar_pedidos():
    """Listar todos los pedidos con filtros opcionales"""
    try:
        # Parámetros de filtro
        estado = request.args.get('estado')
        canal = request.args.get('canal')
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        
        query = Pedido.query
        
        if estado:
            query = query.filter_by(estado=estado)
        if canal:
            query = query.filter_by(canal=canal)
        if fecha_desde:
            query = query.filter(Pedido.fecha_pedido >= datetime.fromisoformat(fecha_desde))
        if fecha_hasta:
            query = query.filter(Pedido.fecha_pedido <= datetime.fromisoformat(fecha_hasta))
        
        pedidos = query.order_by(Pedido.fecha_pedido.desc()).all()
        
        return jsonify({
            'success': True,
            'data': [p.to_dict() for p in pedidos],
            'total': len(pedidos)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<pedido_id>', methods=['GET'])
def obtener_pedido(pedido_id):
    """Obtener detalles de un pedido específico"""
    try:
        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            return jsonify({'success': False, 'error': 'Pedido no encontrado'}), 404
        
        return jsonify({
            'success': True,
            'data': pedido.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/', methods=['POST'])
def crear_pedido():
    """Crear un nuevo pedido"""
    try:
        data = request.json
        
        # Generar ID del pedido
        ultimo_pedido = Pedido.query.order_by(Pedido.id.desc()).first()
        if ultimo_pedido:
            numero = int(ultimo_pedido.id[3:]) + 1
            nuevo_id = f"PED{numero:03d}"
        else:
            nuevo_id = "PED001"
        
        # Crear pedido
        pedido = Pedido(
            id=nuevo_id,
            canal=data['canal'],
            cliente_nombre=data['cliente_nombre'],
            cliente_telefono=data['cliente_telefono'],
            cliente_email=data.get('cliente_email'),
            producto_id=data.get('producto_id'),
            descripcion_personalizada=data.get('descripcion_personalizada'),
            precio_total=data['precio_total'],
            direccion_entrega=data['direccion_entrega'],
            comuna=data.get('comuna'),
            fecha_entrega=datetime.fromisoformat(data['fecha_entrega']),
            notas=data.get('notas')
        )
        
        db.session.add(pedido)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': pedido.to_dict(),
            'message': f'Pedido {nuevo_id} creado exitosamente'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<pedido_id>/estado', methods=['PATCH'])
def actualizar_estado(pedido_id):
    """Actualizar estado de un pedido"""
    try:
        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            return jsonify({'success': False, 'error': 'Pedido no encontrado'}), 404
        
        data = request.json
        nuevo_estado = data.get('estado')
        
        if nuevo_estado not in ['Recibido', 'En Preparación', 'Listo', 'Despachado', 'Entregado', 'Cancelado']:
            return jsonify({'success': False, 'error': 'Estado inválido'}), 400
        
        pedido.estado = nuevo_estado
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': pedido.to_dict(),
            'message': f'Estado actualizado a: {nuevo_estado}'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<pedido_id>', methods=['DELETE'])
def eliminar_pedido(pedido_id):
    """Eliminar (o cancelar) un pedido"""
    try:
        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            return jsonify({'success': False, 'error': 'Pedido no encontrado'}), 404
        
        # En lugar de eliminar, cambiar estado a Cancelado
        pedido.estado = 'Cancelado'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Pedido {pedido_id} cancelado'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/tablero', methods=['GET'])
def obtener_tablero():
    """Obtener pedidos organizados por estado (formato Kanban)"""
    try:
        estados = ['Recibido', 'En Preparación', 'Listo', 'Despachado']
        tablero = {}
        
        for estado in estados:
            pedidos = Pedido.query.filter_by(estado=estado).order_by(Pedido.fecha_entrega.asc()).all()
            tablero[estado] = [p.to_dict() for p in pedidos]
        
        return jsonify({
            'success': True,
            'data': tablero,
            'total_pendientes': sum(len(pedidos) for pedidos in tablero.values())
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

