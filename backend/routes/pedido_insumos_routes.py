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


@bp.route('/<pedido_id>/insumos-detallados', methods=['GET'])
def obtener_insumos_detallados(pedido_id):
    """
    Obtiene los insumos seleccionados con la nueva estructura de colores.
    Retorna las flores seleccionadas organizadas por color y los contenedores.
    """
    try:
        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            return jsonify({'success': False, 'error': 'Pedido no encontrado'}), 404
        
        # Obtener flores seleccionadas
        flores_seleccionadas = PedidoFlorSeleccionada.query.filter_by(pedido_id=pedido_id).all()
        
        # Obtener contenedor seleccionado
        contenedor_seleccionado = PedidoContenedorSeleccionado.query.filter_by(pedido_id=pedido_id).first()
        
        # Formatear respuesta
        flores_data = []
        for flor_sel in flores_seleccionadas:
            flor = Flor.query.get(flor_sel.flor_id)
            flores_data.append({
                'id': flor_sel.id,
                'color_nombre': flor_sel.color_nombre,
                'flor_id': flor_sel.flor_id,
                'flor_nombre': f"{flor.tipo} {flor.color}" if flor else flor_sel.flor_id,
                'flor_foto': flor.foto_url if flor else None,
                'cantidad': flor_sel.cantidad,
                'costo_unitario': float(flor_sel.costo_unitario),
                'costo_total': float(flor_sel.costo_total),
                'stock_disponible': flor.cantidad_stock if flor else 0,
                'descontado_stock': flor_sel.descontado_stock,
                'stock_suficiente': (flor.cantidad_stock if flor else 0) >= flor_sel.cantidad
            })
        
        contenedor_data = None
        if contenedor_seleccionado:
            contenedor = Contenedor.query.get(contenedor_seleccionado.contenedor_id)
            contenedor_data = {
                'id': contenedor_seleccionado.id,
                'contenedor_id': contenedor_seleccionado.contenedor_id,
                'contenedor_nombre': f"{contenedor.tipo} {contenedor.material}" if contenedor else contenedor_seleccionado.contenedor_id,
                'contenedor_foto': contenedor.foto_url if contenedor else None,
                'cantidad': contenedor_seleccionado.cantidad,
                'costo_unitario': float(contenedor_seleccionado.costo_unitario),
                'costo_total': float(contenedor_seleccionado.costo_total),
                'stock_disponible': contenedor.cantidad_stock if contenedor else 0,
                'descontado_stock': contenedor_seleccionado.descontado_stock,
                'stock_suficiente': (contenedor.cantidad_stock if contenedor else 0) >= contenedor_seleccionado.cantidad
            }
        
        return jsonify({
            'success': True,
            'data': {
                'flores': flores_data,
                'contenedor': contenedor_data,
                'todos_confirmados': all(f['descontado_stock'] for f in flores_data) and (contenedor_data is None or contenedor_data['descontado_stock']),
                'hay_stock_completo': all(f['stock_suficiente'] for f in flores_data) and (contenedor_data is None or contenedor_data['stock_suficiente'])
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<pedido_id>/confirmar-insumos-detallados', methods=['POST'])
def confirmar_insumos_detallados(pedido_id):
    """
    Confirma los insumos seleccionados y descuenta del stock.
    También mueve el pedido a 'Listo para Despacho'.
    """
    try:
        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            return jsonify({'success': False, 'error': 'Pedido no encontrado'}), 404
        
        # Obtener insumos
        flores_seleccionadas = PedidoFlorSeleccionada.query.filter_by(pedido_id=pedido_id).all()
        contenedor_seleccionado = PedidoContenedorSeleccionado.query.filter_by(pedido_id=pedido_id).first()
        
        # Validar stock
        errores = []
        for flor_sel in flores_seleccionadas:
            if flor_sel.descontado_stock:
                continue  # Ya fue descontado
                
            flor = Flor.query.get(flor_sel.flor_id)
            if not flor:
                errores.append(f"Flor {flor_sel.flor_id} no encontrada")
            elif flor.cantidad_stock < flor_sel.cantidad:
                errores.append(f"{flor.tipo} {flor.color}: Stock insuficiente ({flor.cantidad_stock} disponibles, se necesitan {flor_sel.cantidad})")
        
        if contenedor_seleccionado and not contenedor_seleccionado.descontado_stock:
            contenedor = Contenedor.query.get(contenedor_seleccionado.contenedor_id)
            if not contenedor:
                errores.append(f"Contenedor {contenedor_seleccionado.contenedor_id} no encontrado")
            elif contenedor.cantidad_stock < contenedor_seleccionado.cantidad:
                errores.append(f"{contenedor.tipo}: Stock insuficiente ({contenedor.cantidad_stock} disponibles, se necesitan {contenedor_seleccionado.cantidad})")
        
        if errores:
            return jsonify({'success': False, 'error': '\n'.join(errores)}), 400
        
        # Descontar stock
        for flor_sel in flores_seleccionadas:
            if flor_sel.descontado_stock:
                continue
                
            flor = Flor.query.get(flor_sel.flor_id)
            flor.cantidad_stock -= flor_sel.cantidad
            flor_sel.descontado_stock = True
        
        if contenedor_seleccionado and not contenedor_seleccionado.descontado_stock:
            contenedor = Contenedor.query.get(contenedor_seleccionado.contenedor_id)
            contenedor.cantidad_stock -= contenedor_seleccionado.cantidad
            contenedor_seleccionado.descontado_stock = True
        
        # Cambiar estado del pedido
        pedido.estado = 'Listo para Despacho'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Insumos confirmados y stock descontado exitosamente'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

