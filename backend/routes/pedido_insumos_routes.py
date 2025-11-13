"""
Rutas API para gestión de insumos de pedidos
"""
from flask import Blueprint, jsonify, request
from extensions import db
from models.pedido import PedidoInsumo, Pedido
from models.inventario import Flor, Contenedor
from models.producto_detallado import PedidoFlorSeleccionada, PedidoContenedorSeleccionado

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
                    insumo_dict['precio_unitario'] = float(flor.costo_unitario or 0)
                    insumo_dict['flor_id'] = insumo.insumo_id  # Para frontend
            elif insumo.insumo_tipo == 'Contenedor':
                contenedor = Contenedor.query.get(insumo.insumo_id)
                if contenedor:
                    insumo_dict['insumo_nombre'] = contenedor.tipo
                    insumo_dict['insumo_material'] = contenedor.material
                    insumo_dict['insumo_foto'] = contenedor.foto_url
                    insumo_dict['stock_disponible'] = contenedor.cantidad_disponible
                    insumo_dict['precio_unitario'] = float(contenedor.costo or 0)
                    insumo_dict['contenedor_id'] = insumo.insumo_id  # Para frontend
            
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
        
        # Primero, liberar stock de insumos anteriores si existen
        insumos_anteriores = PedidoInsumo.query.filter_by(pedido_id=pedido_id).all()
        for insumo_anterior in insumos_anteriores:
            if not insumo_anterior.descontado_stock:
                # Liberar de "en uso" solo si no se descontó
                if insumo_anterior.insumo_tipo == 'Flor':
                    flor = Flor.query.get(insumo_anterior.insumo_id)
                    if flor:
                        flor.cantidad_en_uso = max(0, flor.cantidad_en_uso - insumo_anterior.cantidad)
                elif insumo_anterior.insumo_tipo == 'Contenedor':
                    contenedor = Contenedor.query.get(insumo_anterior.insumo_id)
                    if contenedor:
                        contenedor.cantidad_en_uso = max(0, contenedor.cantidad_en_uso - insumo_anterior.cantidad)
        
        # Eliminar insumos anteriores
        PedidoInsumo.query.filter_by(pedido_id=pedido_id).delete()
        
        # Crear nuevos insumos Y RESERVAR STOCK
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
            
            # RESERVAR: Incrementar cantidad_en_uso
            cantidad = int(insumo_data['cantidad'])
            if insumo_data['insumo_tipo'] == 'Flor':
                flor = Flor.query.get(insumo_data['insumo_id'])
                if flor:
                    flor.cantidad_en_uso += cantidad
            elif insumo_data['insumo_tipo'] == 'Contenedor':
                contenedor = Contenedor.query.get(insumo_data['insumo_id'])
                if contenedor:
                    contenedor.cantidad_en_uso += cantidad
        
        db.session.commit()
        
        # Registrar en auditoría
        try:
            from utils.auditoria_helper import registrar_accion
            from models.pedido import Pedido
            pedido = Pedido.query.get(pedido_id)
            if pedido:
                registrar_accion('agregar_insumos', 'pedido', pedido_id, {
                    'cantidad_insumos': len(insumos_data),
                    'cliente': pedido.cliente_nombre
                })
        except Exception as e:
            print(f'Error al registrar acción de auditoría: {e}')
        
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
    
    Puede recibir cantidades modificadas:
    {
        "cantidades": {
            "1": 10,  // insumo_id: cantidad_usada
            "2": 5
        }
    }
    """
    try:
        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            return jsonify({'error': 'Pedido no encontrado'}), 404
        
        # Verificar que el pedido esté en estado "En Proceso"
        if pedido.estado != 'En Proceso':
            return jsonify({'error': 'El pedido debe estar en estado "En Proceso" para confirmar insumos'}), 400
        
        # Obtener cantidades modificadas si las hay
        data = request.get_json() or {}
        cantidades_modificadas = data.get('cantidades', {})
        
        # Obtener insumos del pedido
        insumos = PedidoInsumo.query.filter_by(pedido_id=pedido_id, descontado_stock=False).all()
        
        print(f'[DEBUG] Pedido {pedido_id}: {len(insumos)} insumos encontrados (descontado_stock=False)')
        
        # Permitir confirmar pedidos sin insumos (solo cambiar estado)
        if not insumos:
            print(f'[DEBUG] Pedido {pedido_id}: No hay insumos, confirmando sin insumos. retiro_en_tienda={pedido.retiro_en_tienda}')
            # Cambiar estado del pedido según retiro_en_tienda
            if pedido.retiro_en_tienda:
                pedido.estado = 'Retiro en Tienda'
            else:
                pedido.estado = 'Listo para Despacho'
            
            db.session.commit()
            
            # Registrar en auditoría
            try:
                from utils.auditoria_helper import registrar_accion
                registrar_accion('confirmar_insumos', 'pedido', pedido_id, {
                    'insumos_procesados': 0,
                    'nuevo_estado': pedido.estado,
                    'cliente': pedido.cliente_nombre,
                    'sin_insumos': True
                })
            except Exception as e:
                print(f'Error al registrar acción de auditoría: {e}')
            
            return jsonify({
                'success': True,
                'message': 'Pedido confirmado sin insumos',
                'pedido_id': pedido_id,
                'nuevo_estado': pedido.estado,
                'insumos_procesados': 0
            })
        
        # Actualizar cantidades si fueron modificadas
        for insumo in insumos:
            str_id = str(insumo.id)
            if str_id in cantidades_modificadas:
                nueva_cantidad = int(cantidades_modificadas[str_id])
                insumo.cantidad = nueva_cantidad
                insumo.costo_total = insumo.costo_unitario * nueva_cantidad
        
        db.session.flush()  # Guardar cambios de cantidades
        
        # Verificar disponibilidad de stock
        # IMPORTANTE: El stock disponible DEBE incluir lo que este pedido ya tiene en uso
        # Porque al confirmar, primero liberamos el "en uso" de este pedido, luego descontamos del total
        errores_stock = []
        for insumo in insumos:
            if insumo.insumo_tipo == 'Flor':
                flor = Flor.query.get(insumo.insumo_id)
                if not flor:
                    errores_stock.append(f'Flor {insumo.insumo_id} no encontrada')
                else:
                    # Calcular cuánto de este insumo está reservado por ESTE pedido
                    reservado_este_pedido = sum(
                        i.cantidad for i in insumos 
                        if i.insumo_tipo == 'Flor' and i.insumo_id == insumo.insumo_id
                    )
                    
                    # Stock realmente disponible = disponible general + lo que este pedido tiene reservado
                    # (porque al confirmar, liberamos primero lo de este pedido)
                    stock_real_disponible = flor.cantidad_disponible + reservado_este_pedido
                    
                    if stock_real_disponible < insumo.cantidad:
                        errores_stock.append(
                            f'{flor.tipo} {flor.color}: Stock insuficiente '                            
                            f'(Disponible: {flor.cantidad_disponible}, En este pedido: {reservado_este_pedido}, '
                            f'Total disponible: {stock_real_disponible}, Requerido: {insumo.cantidad})'
                        )
            
            elif insumo.insumo_tipo == 'Contenedor':
                contenedor = Contenedor.query.get(insumo.insumo_id)
                if not contenedor:
                    errores_stock.append(f'Contenedor {insumo.insumo_id} no encontrado')
                else:
                    # Calcular cuánto de este insumo está reservado por ESTE pedido
                    reservado_este_pedido = sum(
                        i.cantidad for i in insumos 
                        if i.insumo_tipo == 'Contenedor' and i.insumo_id == insumo.insumo_id
                    )
                    
                    # Stock realmente disponible = disponible general + lo que este pedido tiene reservado
                    stock_real_disponible = contenedor.cantidad_disponible + reservado_este_pedido
                    
                    if stock_real_disponible < insumo.cantidad:
                        errores_stock.append(
                            f'{contenedor.tipo}: Stock insuficiente '
                            f'(Disponible: {contenedor.cantidad_disponible}, En este pedido: {reservado_este_pedido}, '
                            f'Total disponible: {stock_real_disponible}, Requerido: {insumo.cantidad})'
                        )
        
        if errores_stock:
            return jsonify({
                'error': 'Stock insuficiente',
                'detalles': errores_stock
            }), 400
        
        # CONFIRMAR USO: Descontar del stock total Y liberar de "en uso"
        # Los insumos ya estaban reservados (en_uso), ahora los consumimos realmente
        for insumo in insumos:
            if insumo.insumo_tipo == 'Flor':
                flor = Flor.query.get(insumo.insumo_id)
                if flor:
                    # Descontar del stock total
                    flor.cantidad_stock -= insumo.cantidad
                    # Liberar de "en uso" (ya se usó realmente)
                    flor.cantidad_en_uso = max(0, flor.cantidad_en_uso - insumo.cantidad)

            elif insumo.insumo_tipo == 'Contenedor':
                contenedor = Contenedor.query.get(insumo.insumo_id)
                if contenedor:
                    # Descontar del stock total
                    contenedor.stock -= insumo.cantidad
                    # Liberar de "en uso" (ya se usó realmente)
                    contenedor.cantidad_en_uso = max(0, contenedor.cantidad_en_uso - insumo.cantidad)

            # Marcar como descontado
            insumo.descontado_stock = True
        
        # Cambiar estado del pedido
        # Si es retiro en tienda, va a "Retiro en Tienda", sino a "Listo para Despacho"
        print(f'[DEBUG] Pedido {pedido_id}: Cambiando estado. retiro_en_tienda={pedido.retiro_en_tienda}, tipo={type(pedido.retiro_en_tienda)}')
        if pedido.retiro_en_tienda:
            pedido.estado = 'Retiro en Tienda'
            print(f'[DEBUG] Pedido {pedido_id}: Estado cambiado a "Retiro en Tienda"')
        else:
            pedido.estado = 'Listo para Despacho'
            print(f'[DEBUG] Pedido {pedido_id}: Estado cambiado a "Listo para Despacho"')
        
        db.session.commit()
        
        # Registrar en auditoría
        try:
            from utils.auditoria_helper import registrar_accion
            registrar_accion('confirmar_insumos', 'pedido', pedido_id, {
                'insumos_procesados': len(insumos),
                'nuevo_estado': pedido.estado,
                'cliente': pedido.cliente_nombre
            })
        except Exception as e:
            print(f'Error al registrar acción de auditoría: {e}')
        
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
    IMPORTANTE: También RESERVA el stock (marca como "En Uso").
    
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
        
        # PASO 1: Validar que haya stock disponible
        errores_validacion = []
        
        if 'flores' in data and data['flores']:
            for flor_data in data['flores']:
                flor = Flor.query.get(flor_data.get('flor_id'))
                if not flor:
                    errores_validacion.append(f"Flor {flor_data.get('flor_id')} no encontrada")
                elif flor.cantidad_disponible < flor_data.get('cantidad'):
                    errores_validacion.append(
                        f"{flor.tipo} {flor.color}: Solo hay {flor.cantidad_disponible} disponibles "
                        f"({flor.cantidad_stock} en stock, {flor.cantidad_en_uso} en uso), "
                        f"se necesitan {flor_data.get('cantidad')}"
                    )
        
        if 'contenedor' in data and data['contenedor']:
            cont_data = data['contenedor']
            contenedor = Contenedor.query.get(cont_data.get('contenedor_id'))
            if not contenedor:
                errores_validacion.append(f"Contenedor {cont_data.get('contenedor_id')} no encontrado")
            elif contenedor.cantidad_disponible < cont_data.get('cantidad', 1):
                errores_validacion.append(
                    f"{contenedor.tipo} {contenedor.material}: Solo hay {contenedor.cantidad_disponible} disponibles "
                    f"({contenedor.stock} en stock, {contenedor.cantidad_en_uso} en uso), "
                    f"se necesitan {cont_data.get('cantidad', 1)}"
                )
        
        if errores_validacion:
            return jsonify({
                'success': False,
                'error': 'Stock insuficiente',
                'detalles': errores_validacion
            }), 400
        
        # PASO 2: Guardar flores seleccionadas Y RESERVAR STOCK
        if 'flores' in data and data['flores']:
            for flor_data in data['flores']:
                # Guardar relación
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
                
                # RESERVAR: Incrementar cantidad_en_uso
                flor = Flor.query.get(flor_data.get('flor_id'))
                flor.cantidad_en_uso += flor_data.get('cantidad')
        
        # PASO 3: Guardar contenedor seleccionado Y RESERVAR STOCK
        if 'contenedor' in data and data['contenedor']:
            cont_data = data['contenedor']
            
            # Guardar relación
            contenedor_seleccionado = PedidoContenedorSeleccionado(
                pedido_id=pedido_id,
                contenedor_id=cont_data.get('contenedor_id'),
                cantidad=cont_data.get('cantidad', 1),
                costo_unitario=cont_data.get('costo_unitario'),
                costo_total=cont_data.get('costo_total'),
                descontado_stock=False
            )
            db.session.add(contenedor_seleccionado)
            
            # RESERVAR: Incrementar cantidad_en_uso
            contenedor = Contenedor.query.get(cont_data.get('contenedor_id'))
            contenedor.cantidad_en_uso += cont_data.get('cantidad', 1)
        
        db.session.commit()
        
        # Registrar en auditoría
        try:
            from utils.auditoria_helper import registrar_accion
            from models.pedido import Pedido
            pedido = Pedido.query.get(pedido_id)
            if pedido:
                cantidad_flores = len(data.get('flores', []))
                tiene_contenedor = bool(data.get('contenedor'))
                registrar_accion('agregar_insumos', 'pedido', pedido_id, {
                    'cantidad_flores': cantidad_flores,
                    'tiene_contenedor': tiene_contenedor,
                    'cliente': pedido.cliente_nombre
                })
        except Exception as e:
            print(f'Error al registrar acción de auditoría: {e}')
        
        return jsonify({
            'success': True,
            'message': 'Insumos guardados y stock reservado ("En Uso") exitosamente'
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
                'stock_total': flor.cantidad_stock if flor else 0,
                'stock_en_uso': flor.cantidad_en_uso if flor else 0,
                'stock_disponible': flor.cantidad_disponible if flor else 0,
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
                'stock_total': contenedor.stock if contenedor else 0,
                'stock_en_uso': contenedor.cantidad_en_uso if contenedor else 0,
                'stock_disponible': contenedor.cantidad_disponible if contenedor else 0,
                'descontado_stock': contenedor_seleccionado.descontado_stock,
                'stock_suficiente': (contenedor.stock if contenedor else 0) >= contenedor_seleccionado.cantidad
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
    Confirma los insumos utilizados en el Taller.
    
    NUEVA LÓGICA:
    1. Descuenta del STOCK TOTAL lo que realmente se usó
    2. Libera del "En Uso" lo que estaba reservado
    3. Lo que no se usó vuelve automáticamente a "Disponible"
    4. Mueve el pedido a 'Listo para Despacho'
    
    Puede recibir cantidades modificadas (ej: se reservaron 12, solo se usaron 10).
    Si no se envían cantidades, usa las cantidades originales.
    """
    try:
        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            return jsonify({'success': False, 'error': 'Pedido no encontrado'}), 404
        
        # Obtener datos de confirmación (pueden incluir cantidades modificadas)
        data = request.get_json() or {}
        cantidades_usadas = data.get('cantidades_usadas', {})  # { 'flores': {id: cantidad}, 'contenedor': cantidad }
        
        # Obtener insumos
        flores_seleccionadas = PedidoFlorSeleccionada.query.filter_by(pedido_id=pedido_id).all()
        contenedor_seleccionado = PedidoContenedorSeleccionado.query.filter_by(pedido_id=pedido_id).first()
        
        # Validar que no se haya confirmado ya
        if all(f.descontado_stock for f in flores_seleccionadas) and (not contenedor_seleccionado or contenedor_seleccionado.descontado_stock):
            return jsonify({'success': False, 'error': 'Los insumos de este pedido ya fueron confirmados'}), 400
        
        # PROCESAR FLORES
        errores = []
        for flor_sel in flores_seleccionadas:
            if flor_sel.descontado_stock:
                continue  # Ya fue procesada

            flor = Flor.query.get(flor_sel.flor_id)
            if not flor:
                errores.append(f"Flor {flor_sel.flor_id} no encontrada")
                continue

            # Cantidad a usar (puede ser modificada en Taller)
            cantidad_a_usar = cantidades_usadas.get('flores', {}).get(str(flor_sel.id), flor_sel.cantidad)
            cantidad_reservada = flor_sel.cantidad

            # Validar que la cantidad a usar sea válida
            if cantidad_a_usar < 0:
                errores.append(f"{flor.tipo} {flor.color}: Cantidad inválida ({cantidad_a_usar})")
                continue

            # LÓGICA CORRECTA: Calcular cuánto de esta flor está reservado por ESTE pedido
            # (puede haber múltiples líneas de la misma flor en el pedido)
            total_reservado_esta_flor = sum(
                f.cantidad for f in flores_seleccionadas
                if f.flor_id == flor_sel.flor_id and not f.descontado_stock
            )

            # Stock realmente disponible = stock disponible actual + lo que este pedido tiene reservado
            # Esto es correcto porque al confirmar, primero liberamos la reserva y luego descontamos del stock
            stock_real_disponible = flor.cantidad_disponible + total_reservado_esta_flor

            # Validar si estoy usando MÁS de lo que tenía disponible (considerando mi reserva)
            if cantidad_a_usar > stock_real_disponible:
                errores.append(
                    f"{flor.tipo} {flor.color}: Stock insuficiente. "
                    f"Disponible: {flor.cantidad_disponible}, Reservado por este pedido: {total_reservado_esta_flor}, "
                    f"Total disponible: {stock_real_disponible}, Solicitado: {cantidad_a_usar}"
                )
                continue
            
            # APLICAR CAMBIOS:
            # 1. Descontar del stock total lo que se usó
            flor.cantidad_stock -= cantidad_a_usar
            
            # 2. Liberar del "En Uso" lo que estaba reservado
            flor.cantidad_en_uso -= cantidad_reservada
            
            # 3. Lo no usado (cantidad_reservada - cantidad_a_usar) vuelve automáticamente a disponible
            
            # 4. Marcar como procesado
            flor_sel.descontado_stock = True
            
            # 5. Actualizar la cantidad real usada en el registro (para historial)
            flor_sel.cantidad = cantidad_a_usar
            flor_sel.costo_total = flor_sel.costo_unitario * cantidad_a_usar
        
        # PROCESAR CONTENEDOR
        if contenedor_seleccionado and not contenedor_seleccionado.descontado_stock:
            contenedor = Contenedor.query.get(contenedor_seleccionado.contenedor_id)
            if not contenedor:
                errores.append(f"Contenedor {contenedor_seleccionado.contenedor_id} no encontrado")
            else:
                # Cantidad a usar (normalmente 1, pero puede variar)
                cantidad_a_usar = cantidades_usadas.get('contenedor', contenedor_seleccionado.cantidad)
                cantidad_reservada = contenedor_seleccionado.cantidad

                # Validar cantidad inválida
                if cantidad_a_usar < 0:
                    errores.append(f"{contenedor.tipo}: Cantidad inválida ({cantidad_a_usar})")
                else:
                    # LÓGICA CORRECTA: El contenedor ya está reservado por este pedido
                    # Stock realmente disponible = stock disponible actual + lo reservado por este pedido
                    stock_real_disponible = contenedor.cantidad_disponible + cantidad_reservada

                    # Validar si estoy usando MÁS de lo que tenía disponible (considerando mi reserva)
                    if cantidad_a_usar > stock_real_disponible:
                        errores.append(
                            f"{contenedor.tipo}: Stock insuficiente. "
                            f"Disponible: {contenedor.cantidad_disponible}, Reservado por este pedido: {cantidad_reservada}, "
                            f"Total disponible: {stock_real_disponible}, Solicitado: {cantidad_a_usar}"
                        )
                    else:
                        # APLICAR CAMBIOS
                        contenedor.stock -= cantidad_a_usar
                        contenedor.cantidad_en_uso -= cantidad_reservada
                        contenedor_seleccionado.descontado_stock = True
                        contenedor_seleccionado.cantidad = cantidad_a_usar
                        contenedor_seleccionado.costo_total = contenedor_seleccionado.costo_unitario * cantidad_a_usar
        
        if errores:
            return jsonify({'success': False, 'error': 'Errores de validación', 'detalles': errores}), 400
        
        # Cambiar estado del pedido
        # Si es retiro en tienda, va a "Retiro en Tienda", sino a "Listo para Despacho"
        print(f'[DEBUG] Pedido {pedido_id} (detallado): Cambiando estado. retiro_en_tienda={pedido.retiro_en_tienda}, tipo={type(pedido.retiro_en_tienda)}')
        if pedido.retiro_en_tienda:
            pedido.estado = 'Retiro en Tienda'
            print(f'[DEBUG] Pedido {pedido_id} (detallado): Estado cambiado a "Retiro en Tienda"')
        else:
            pedido.estado = 'Listo para Despacho'
            print(f'[DEBUG] Pedido {pedido_id} (detallado): Estado cambiado a "Listo para Despacho"')
        
        db.session.commit()
        
        # Registrar en auditoría
        try:
            from utils.auditoria_helper import registrar_accion
            registrar_accion('confirmar_insumos', 'pedido', pedido_id, {
                'nuevo_estado': pedido.estado,
                'cliente': pedido.cliente_nombre,
                'tipo': 'detallado'
            })
        except Exception as e:
            print(f'Error al registrar acción de auditoría: {e}')
        
        return jsonify({
            'success': True,
            'message': 'Insumos confirmados. Stock descontado y cantidades no usadas liberadas exitosamente.'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

