"""
Rutas para gestión de pedidos
"""

from flask import Blueprint, request, jsonify
from backend.app import db
from backend.models.pedido import Pedido, PedidoInsumo
from backend.models.cliente import Cliente
from backend.config.plazos_pago import obtener_plazo_pago
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
        
        # Gestionar cliente (buscar o crear)
        cliente_id = data.get('cliente_id')
        cliente = None
        
        if cliente_id:
            # Cliente ya existe, usar ese
            cliente = Cliente.query.get(cliente_id)
        else:
            # Buscar por teléfono
            telefono = data['cliente_telefono']
            cliente = Cliente.query.filter_by(telefono=telefono).first()
            
            if not cliente:
                # Cliente no existe, crear uno nuevo
                ultimo_cliente = Cliente.query.order_by(Cliente.id.desc()).first()
                if ultimo_cliente:
                    numero = int(ultimo_cliente.id[3:]) + 1
                    nuevo_cliente_id = f"CLI{numero:03d}"
                else:
                    nuevo_cliente_id = "CLI001"
                
                cliente = Cliente(
                    id=nuevo_cliente_id,
                    nombre=data['cliente_nombre'],
                    telefono=telefono,
                    email=data.get('cliente_email'),
                    tipo_cliente='Nuevo'
                )
                db.session.add(cliente)
                db.session.flush()  # Para obtener el ID
        
        # Generar ID del pedido
        ultimo_pedido = Pedido.query.order_by(Pedido.id.desc()).first()
        if ultimo_pedido:
            numero = int(ultimo_pedido.id[3:]) + 1
            nuevo_id = f"PED{numero:03d}"
        else:
            nuevo_id = "PED001"
        
        # Calcular plazo de pago
        # Si viene manual en el request, usar ese; sino calcularlo por tipo de cliente
        if 'plazo_pago_dias' in data:
            plazo_pago = int(data['plazo_pago_dias'])
        elif cliente:
            plazo_pago = obtener_plazo_pago(cliente.tipo_cliente)
        else:
            plazo_pago = 0  # Sin cliente, pago inmediato
        
        # Crear pedido
        pedido = Pedido(
            id=nuevo_id,
            canal=data['canal'],
            shopify_order_number=data.get('shopify_order_number'),
            cliente_id=cliente.id if cliente else None,
            cliente_nombre=data['cliente_nombre'],
            cliente_telefono=data['cliente_telefono'],
            cliente_email=data.get('cliente_email'),
            producto_id=data.get('producto_id'),
            arreglo_pedido=data.get('arreglo_pedido'),
            detalles_adicionales=data.get('detalles_adicionales'),
            precio_ramo=data['precio_ramo'],
            precio_envio=data.get('precio_envio', 0),
            destinatario=data.get('destinatario'),
            mensaje=data.get('mensaje'),
            firma=data.get('firma'),
            direccion_entrega=data['direccion_entrega'],
            comuna=data.get('comuna'),
            motivo=data.get('motivo'),
            plazo_pago_dias=plazo_pago,
            fecha_entrega=datetime.fromisoformat(data['fecha_entrega'])
        )
        
        db.session.add(pedido)
        
        # Actualizar estadísticas del cliente
        if cliente:
            cliente.total_pedidos += 1
            cliente.total_gastado = (cliente.total_gastado or 0) + pedido.precio_total
            cliente.ultima_compra = datetime.now()
        
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
    """Obtener pedidos organizados por estado (formato Kanban estilo Trello Las-Lira)"""
    try:
        # Estados según el flujo del Trello
        estados = [
            'Pedido',
            'Pedidos Semana', 
            'Entregas para Mañana', 
            'Entregas de Hoy',
            'En Proceso', 
            'Listo para Despacho',
            'Despachados'
        ]
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

