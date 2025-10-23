"""
Rutas API para gestión de insumos de pedidos
"""
from flask import Blueprint, jsonify, request
from backend.app import db
from backend.models.pedido import PedidoInsumo, Pedido
from backend.models.inventario import Flor, Contenedor
from backend.models.producto_detallado import PedidoFlorSeleccionada, PedidoContenedorSeleccionado

bp = Blueprint('pedido_insumos', __name__, url_prefix='/api/pedidos')


@bp.route('/<pedido_id>/insumos', methods=['GET'])
def obtener_insumos_pedido(pedido_id):
    """Obtener todos los insumos de un pedido con detalles completos"""
    try:
        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            return jsonify({'error': 'Pedido no encontrado'}), 404
        
        insumos = PedidoInsumo.query.filter_by(pedido_id=pedido_id).all()
        
        # Enriquecer con información del insumo
        insumos_detallados = []
        for insumo in insumos:
            insumo_dict = insumo.to_dict()
            
            if insumo.insumo_tipo == 'Flor':
                flor = Flor.query.get(insumo.insumo_id)
                if flor:
                    insumo_dict['insumo_nombre'] = flor.tipo
                    insumo_dict['insumo_color'] = flor.color
                    insumo_dict['insumo_foto'] = flor.foto_url
                    insumo_dict['stock_disponible'] = flor.cantidad_disponible
            elif insumo.insumo_tipo == 'Contenedor':
                contenedor = Contenedor.query.get(insumo.insumo_id)
                if contenedor:
                    insumo_dict['insumo_nombre'] = contenedor.tipo
                    insumo_dict['insumo_material'] = contenedor.material
                    insumo_dict['insumo_foto'] = contenedor.foto_url
                    insumo_dict['stock_disponible'] = contenedor.cantidad_disponible
            
            insumos_detallados.append(insumo_dict)
        
        return jsonify({
            'pedido_id': pedido_id,
            'insumos': insumos_detallados
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<pedido_id>/insumos', methods=['POST'])
def guardar_insumos_pedido(pedido_id):
    """Guardar o actualizar los insumos de un pedido"""
    try:
        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            return jsonify({'error': 'Pedido no encontrado'}), 404
        
        data = request.json
        insumos_data = data.get('insumos', [])
        
        # Eliminar insumos anteriores (si existen)
        PedidoInsumo.query.filter_by(pedido_id=pedido_id).delete()
        
        # Crear nuevos insumos
        for insumo_data in insumos_data:
            nuevo_insumo = PedidoInsumo(
                pedido_id=pedido_id,
                insumo_tipo=insumo_data['insumo_tipo'],
                insumo_id=insumo_data['insumo_id'],
                cantidad=int(insumo_data['cantidad']),
                costo_unitario=float(insumo_data['costo_unitario']),
                costo_total=float(insumo_data['cantidad']) * float(insumo_data['costo_unitario']),
                descontado_stock=False
            )
            db.session.add(nuevo_insumo)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{len(insumos_data)} insumos guardados correctamente'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<pedido_id>/confirmar-insumos', methods=['POST'], strict_slashes=False)
def confirmar_insumos_y_descontar(pedido_id):
    """
    Confirmar los insumos de un pedido y descontar del stock.
    Cambia el estado del pedido a 'Listo para Despacho'.
    """
    try:
        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            return jsonify({'error': 'Pedido no encontrado'}), 404
        
        # Verificar que el pedido esté en estado "En Proceso"
        if pedido.estado != 'En Proceso':
            return jsonify({'error': 'El pedido debe estar en estado "En Proceso" para confirmar insumos'}), 400
        
        # Obtener insumos del pedido
        insumos = PedidoInsumo.query.filter_by(pedido_id=pedido_id, descontado_stock=False).all()
        
        if not insumos:
            return jsonify({'error': 'No hay insumos para confirmar'}), 400
        
        # Verificar disponibilidad de stock
        errores_stock = []
        for insumo in insumos:
            if insumo.insumo_tipo == 'Flor':
                flor = Flor.query.get(insumo.insumo_id)
                if not flor:
                    errores_stock.append(f'Flor {insumo.insumo_id} no encontrada')
                elif flor.cantidad_disponible < insumo.cantidad:
                    errores_stock.append(f'{flor.tipo} {flor.color}: Stock insuficiente (Disponible: {flor.cantidad_disponible}, Requerido: {insumo.cantidad})')
            
            elif insumo.insumo_tipo == 'Contenedor':
                contenedor = Contenedor.query.get(insumo.insumo_id)
                if not contenedor:
                    errores_stock.append(f'Contenedor {insumo.insumo_id} no encontrado')
                elif contenedor.cantidad_disponible < insumo.cantidad:
                    errores_stock.append(f'{contenedor.tipo}: Stock insuficiente (Disponible: {contenedor.cantidad_disponible}, Requerido: {insumo.cantidad})')
        
        if errores_stock:
            return jsonify({
                'error': 'Stock insuficiente',
                'detalles': errores_stock
            }), 400
        
        # Descontar stock
        for insumo in insumos:
            if insumo.insumo_tipo == 'Flor':
                flor = Flor.query.get(insumo.insumo_id)
                flor.cantidad_disponible -= insumo.cantidad
            elif insumo.insumo_tipo == 'Contenedor':
                contenedor = Contenedor.query.get(insumo.insumo_id)
                contenedor.cantidad_disponible -= insumo.cantidad
            
            # Marcar como descontado
            insumo.descontado_stock = True
        
        # Cambiar estado del pedido
        pedido.estado = 'Listo para Despacho'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Insumos confirmados y stock descontado correctamente',
            'pedido_id': pedido_id,
            'nuevo_estado': pedido.estado,
            'insumos_procesados': len(insumos)
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/taller', methods=['GET'])
def obtener_pedidos_taller():
    """Obtener pedidos en proceso para la sección de taller"""
    try:
        pedidos = Pedido.query.filter_by(estado='En Proceso').order_by(Pedido.fecha_entrega).all()
        
        pedidos_taller = []
        for pedido in pedidos:
            pedido_dict = pedido.to_dict()
            
            # Contar insumos
            insumos = PedidoInsumo.query.filter_by(pedido_id=pedido.id).all()
            pedido_dict['tiene_insumos'] = len(insumos) > 0
            pedido_dict['total_insumos'] = len(insumos)
            pedido_dict['insumos_confirmados'] = all(i.descontado_stock for i in insumos) if insumos else False
            
            pedidos_taller.append(pedido_dict)
        
        return jsonify(pedidos_taller)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<pedido_id>/insumos-detallados', methods=['POST'])
def guardar_insumos_detallados(pedido_id):
    """
    Guarda los insumos seleccionados por color para un pedido.
    Recibe la estructura:
    {
      "flores": [
        {
          "color_id": 1,
          "color_nombre": "Rojo",
          "flor_id": "FL001",
          "cantidad": 12,
          "costo_unitario": 1500,
          "costo_total": 18000
        }
      ],
      "contenedor": {
        "contenedor_id": "CO001",
        "cantidad": 1,
        "costo_unitario": 5000,
        "costo_total": 5000
      }
    }
    """
    try:
        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            return jsonify({'success': False, 'error': 'Pedido no encontrado'}), 404
        
        data = request.get_json()
        
        # Guardar flores seleccionadas
        if 'flores' in data and data['flores']:
            for flor_data in data['flores']:
                flor_seleccionada = PedidoFlorSeleccionada(
                    pedido_id=pedido_id,
                    producto_color_id=flor_data.get('color_id'),
                    color_nombre=flor_data.get('color_nombre'),
                    flor_id=flor_data.get('flor_id'),
                    cantidad=flor_data.get('cantidad'),
                    costo_unitario=flor_data.get('costo_unitario'),
                    costo_total=flor_data.get('costo_total'),
                    descontado_stock=False
                )
                db.session.add(flor_seleccionada)
        
        # Guardar contenedor seleccionado
        if 'contenedor' in data and data['contenedor']:
            cont_data = data['contenedor']
            contenedor_seleccionado = PedidoContenedorSeleccionado(
                pedido_id=pedido_id,
                contenedor_id=cont_data.get('contenedor_id'),
                cantidad=cont_data.get('cantidad', 1),
                costo_unitario=cont_data.get('costo_unitario'),
                costo_total=cont_data.get('costo_total'),
                descontado_stock=False
            )
            db.session.add(contenedor_seleccionado)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Insumos guardados exitosamente'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

