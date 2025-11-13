"""
Servicio de gestión de pedidos
Contiene toda la lógica de negocio relacionada con pedidos
"""

from extensions import db
from models.pedido import Pedido, PedidoInsumo
from models.cliente import Cliente
from models.inventario import Flor, Contenedor
from config.plazos_pago import obtener_plazo_pago
from utils.fecha_helpers import clasificar_pedido
from utils.telefono_helpers import normalizar_telefono
from datetime import datetime, timedelta
from sqlalchemy import or_, and_, func


class PedidosService:
    """Servicio para operaciones de negocio de pedidos"""

    @staticmethod
    def listar_pedidos(filtros=None, buscar=None, page=1, limit=100):
        """
        Lista pedidos con filtros, búsqueda y paginación

        Args:
            filtros: dict con estado, canal, fecha_desde, fecha_hasta
            buscar: término de búsqueda libre
            page: número de página
            limit: registros por página

        Returns:
            tuple: (pedidos, total, total_pages)
        """
        query = Pedido.query

        # Aplicar filtros
        if filtros:
            if filtros.get('estado'):
                query = query.filter_by(estado=filtros['estado'])
            if filtros.get('canal'):
                query = query.filter_by(canal=filtros['canal'])
            if filtros.get('fecha_desde'):
                query = query.filter(Pedido.fecha_pedido >= datetime.fromisoformat(filtros['fecha_desde']))
            if filtros.get('fecha_hasta'):
                query = query.filter(Pedido.fecha_pedido <= datetime.fromisoformat(filtros['fecha_hasta']))

        # Aplicar búsqueda
        if buscar:
            termino = f"%{buscar}%"
            condiciones = []
            if buscar.isdigit():
                condiciones.append(Pedido.id == int(buscar))
            condiciones.extend([
                Pedido.shopify_order_number.ilike(termino),
                Pedido.cliente_nombre.ilike(termino),
                Pedido.cliente_telefono.ilike(termino),
                Pedido.arreglo_pedido.ilike(termino),
                Pedido.direccion_entrega.ilike(termino),
                Pedido.comuna.ilike(termino),
                Pedido.destinatario.ilike(termino),
                Pedido.motivo.ilike(termino),
            ])
            query = query.filter(or_(*condiciones))

        # Contar total
        total = query.count()
        total_pages = (total + limit - 1) // limit

        # Paginar
        pedidos = query.order_by(Pedido.fecha_pedido.desc()).limit(limit).offset((page - 1) * limit).all()

        return pedidos, total, total_pages

    @staticmethod
    def listar_pagados(buscar=None, page=1, limit=50):
        """Lista pedidos pagados con búsqueda y paginación"""
        query = Pedido.query.filter(
            Pedido.estado_pago == 'Pagado',
            Pedido.estado != 'Cancelado'
        )

        if buscar:
            termino = f"%{buscar}%"
            condiciones = [
                Pedido.numero_pedido.ilike(termino),
                Pedido.shopify_order_number.ilike(termino),
                Pedido.cliente_nombre.ilike(termino),
                Pedido.cliente_telefono.ilike(termino),
                Pedido.direccion_entrega.ilike(termino)
            ]
            query = query.filter(or_(*condiciones))

        total = query.count()
        total_pages = (total + limit - 1) // limit

        pedidos = query.order_by(Pedido.fecha_entrega.desc()).limit(limit).offset((page - 1) * limit).all()

        return pedidos, total, total_pages

    @staticmethod
    def obtener_pedido(pedido_id):
        """Obtiene un pedido por ID"""
        return Pedido.query.get(pedido_id)

    @staticmethod
    def buscar_o_crear_cliente(data):
        """
        Busca un cliente existente por teléfono o crea uno nuevo

        Args:
            data: dict con cliente_id, cliente_nombre, cliente_telefono, cliente_email

        Returns:
            Cliente: instancia del cliente
        """
        telefono_normalizado = normalizar_telefono(data['cliente_telefono'])

        # Si viene cliente_id, buscar por ID
        if data.get('cliente_id'):
            cliente = Cliente.query.get(data['cliente_id'])
            if cliente:
                return cliente

        # Buscar por teléfono normalizado
        todos_clientes = Cliente.query.all()
        for c in todos_clientes:
            if normalizar_telefono(c.telefono) == telefono_normalizado:
                return c

        # Cliente no existe, crear uno nuevo
        # Generar ID del cliente
        import re
        clientes = Cliente.query.all()
        numeros = []
        for c in clientes:
            if c.id.startswith('CLI'):
                # Extraer solo los dígitos del ID
                match = re.search(r'\d+', c.id[3:])
                if match:
                    numeros.append(int(match.group()))

        if numeros:
            numero = max(numeros) + 1
        else:
            numero = 1

        nuevo_id = f"CLI{numero:03d}"

        cliente = Cliente(
            id=nuevo_id,
            nombre=data['cliente_nombre'],
            telefono=telefono_normalizado,
            email=data.get('cliente_email'),
            tipo_cliente='Nuevo'
        )
        db.session.add(cliente)
        db.session.flush()  # Para obtener el ID

        return cliente

    @staticmethod
    def calcular_plazo_pago(data, cliente):
        """
        Calcula el plazo de pago según el tipo de cliente

        Args:
            data: dict del request (puede contener plazo_pago_dias manual)
            cliente: instancia del Cliente

        Returns:
            int: días de plazo de pago
        """
        if 'plazo_pago_dias' in data:
            return int(data['plazo_pago_dias'])
        elif cliente:
            return obtener_plazo_pago(cliente.tipo_cliente)
        else:
            return 0

    @staticmethod
    def calcular_fecha_maxima_pago(plazo_pago):
        """Calcula la fecha máxima de pago según el plazo en días"""
        if plazo_pago > 0:
            return datetime.utcnow() + timedelta(days=plazo_pago)
        return None

    @staticmethod
    def crear_pedido(data):
        """
        Crea un nuevo pedido

        Args:
            data: dict con todos los datos del pedido

        Returns:
            tuple: (success, pedido/error, mensaje)
        """
        try:
            # Gestionar cliente
            cliente = PedidosService.buscar_o_crear_cliente(data)

            # Calcular plazo de pago
            plazo_pago = PedidosService.calcular_plazo_pago(data, cliente)
            fecha_maxima_pago = PedidosService.calcular_fecha_maxima_pago(plazo_pago)

            # Parsear fecha de entrega
            fecha_entrega = datetime.fromisoformat(data['fecha_entrega'].replace('Z', '+00:00'))

            # Clasificación automática del pedido
            clasificacion = clasificar_pedido(fecha_entrega)

            # Normalizar teléfono
            telefono_normalizado = normalizar_telefono(data['cliente_telefono'])

            # Lógica para pedidos de Shopify: automáticamente pagados y solo necesitan boleta
            canal_lower = (data.get('canal') or '').lower()
            tiene_shopify_order = bool(data.get('shopify_order_number'))
            es_shopify = canal_lower == 'shopify' or tiene_shopify_order
            
            # Si es de Shopify, marcar como pagado automáticamente
            if es_shopify:
                estado_pago_shopify = 'Pagado'
                documento_shopify = 'Hacer boleta'
            else:
                estado_pago_shopify = data.get('estado_pago', 'No Pagado')
                documento_shopify = data.get('documento_tributario', 'Hacer boleta')

            # Crear pedido
            pedido = Pedido(
                canal=data['canal'],
                shopify_order_number=data.get('shopify_order_number'),
                cliente_id=cliente.id if cliente else None,
                cliente_nombre=data['cliente_nombre'],
                cliente_telefono=telefono_normalizado,
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
                fecha_maxima_pago=fecha_maxima_pago,
                fecha_entrega=fecha_entrega,
                estado=clasificacion['estado'],
                dia_entrega=clasificacion['dia_entrega'],
                # Para pedidos de Shopify: automáticamente pagados
                estado_pago=estado_pago_shopify,
                documento_tributario=documento_shopify,
                retiro_en_tienda=data.get('retiro_en_tienda', False)
            )

            db.session.add(pedido)
            db.session.flush()  # Obtener el ID del pedido antes de commit

            # Procesar múltiples productos con sus insumos
            if 'productos' in data and isinstance(data['productos'], list):
                from models.pedido import PedidoProducto, PedidoInsumo

                for producto_data in data['productos']:
                    # Crear relación pedido-producto
                    pedido_producto = PedidoProducto(
                        pedido_id=pedido.id,
                        producto_id=producto_data['producto_id'],
                        producto_nombre=producto_data.get('producto_nombre', ''),
                        precio=producto_data.get('precio', 0),
                        cantidad=1  # Por ahora, siempre 1
                    )
                    db.session.add(pedido_producto)
                    db.session.flush()  # Obtener ID de pedido_producto

                    # Guardar insumos de este producto
                    if 'insumos' in producto_data and isinstance(producto_data['insumos'], list):
                        for insumo in producto_data['insumos']:
                            # Validar que insumo_id esté presente
                            insumo_id = insumo.get('insumo_id') or insumo.get('flor_id') or insumo.get('contenedor_id')
                            if not insumo_id:
                                # Si no hay insumo_id, saltar este insumo
                                continue
                            
                            cantidad = insumo.get('cantidad', 1)
                            costo_unitario = insumo.get('costo_unitario', 0)
                            costo_total = cantidad * costo_unitario
                            insumo_tipo = insumo.get('insumo_tipo', 'Flor')
                            
                            # Si no se especifica el tipo, intentar inferirlo
                            if not insumo_tipo or insumo_tipo == 'Flor':
                                # Verificar si es flor o contenedor basándose en el ID
                                if insumo.get('flor_id') or (isinstance(insumo_id, str) and insumo_id.startswith('F')):
                                    insumo_tipo = 'Flor'
                                elif insumo.get('contenedor_id') or (isinstance(insumo_id, str) and insumo_id.startswith('C')):
                                    insumo_tipo = 'Contenedor'

                            pedido_insumo = PedidoInsumo(
                                pedido_id=pedido.id,
                                pedido_producto_id=pedido_producto.id,
                                insumo_tipo=insumo_tipo,
                                insumo_id=str(insumo_id),  # Asegurar que sea string
                                insumo_nombre=insumo.get('insumo_nombre', ''),
                                cantidad=cantidad,
                                costo_unitario=costo_unitario,
                                costo_total=costo_total
                            )
                            db.session.add(pedido_insumo)

            # Actualizar estadísticas del cliente
            if cliente:
                cliente.total_pedidos += 1
                cliente.total_gastado = (cliente.total_gastado or 0) + pedido.precio_total
                cliente.ultima_compra = datetime.now()

            # 📦 Reservar insumos automáticamente al crear el pedido
            # Esto incrementa cantidad_en_uso para reflejar que están comprometidos
            success_reserva, msg_reserva = PedidosService._reservar_insumos_pedido(pedido.id)
            if not success_reserva:
                # Si falla la reserva, hacer rollback completo
                db.session.rollback()
                return False, None, f'Error al reservar insumos: {msg_reserva}'

            db.session.commit()

            mensaje_final = f'Pedido #{pedido.id} creado exitosamente'
            if success_reserva:
                mensaje_final += f' | {msg_reserva}'

            return True, pedido, mensaje_final

        except Exception as e:
            db.session.rollback()
            return False, None, str(e)

    @staticmethod
    def _reservar_insumos_pedido(pedido_id):
        """
        Reserva los insumos de un pedido (incrementa cantidad_en_uso)
        Se llama al CREAR un pedido

        NOTA: NO hace commit, debe ser parte de una transacción mayor

        Args:
            pedido_id: ID del pedido

        Returns:
            tuple: (success, mensaje)
        """
        try:
            # Obtener todos los insumos del pedido
            insumos = PedidoInsumo.query.filter_by(pedido_id=pedido_id).all()

            reservados = []
            for insumo in insumos:
                if insumo.insumo_tipo == 'Flor':
                    flor = Flor.query.get(insumo.insumo_id)
                    if flor:
                        flor.cantidad_en_uso += insumo.cantidad
                        reservados.append(f"{insumo.cantidad} {flor.nombre}")
                elif insumo.insumo_tipo == 'Contenedor':
                    contenedor = Contenedor.query.get(insumo.insumo_id)
                    if contenedor:
                        contenedor.cantidad_en_uso += insumo.cantidad
                        reservados.append(f"{insumo.cantidad} {contenedor.nombre or contenedor.tipo}")

            # NO hacer commit aquí - será parte de la transacción del caller

            if reservados:
                return True, f"Insumos reservados: {', '.join(reservados)}"
            else:
                return True, "No hay insumos para reservar"

        except Exception as e:
            return False, f"Error al reservar insumos: {str(e)}"

    @staticmethod
    def _liberar_insumos_pedido(pedido_id):
        """
        Libera los insumos reservados de un pedido (decrementa cantidad_en_uso)
        Se llama cuando un pedido es cancelado o eliminado

        NOTA: NO hace commit, debe ser parte de una transacción mayor

        Args:
            pedido_id: ID del pedido

        Returns:
            tuple: (success, mensaje)
        """
        try:
            # Obtener todos los insumos del pedido que NO han sido descontados del stock
            insumos = PedidoInsumo.query.filter_by(pedido_id=pedido_id, descontado_stock=False).all()

            liberados = []
            for insumo in insumos:
                if insumo.insumo_tipo == 'Flor':
                    flor = Flor.query.get(insumo.insumo_id)
                    if flor:
                        # Liberar la reserva
                        flor.cantidad_en_uso = max(0, flor.cantidad_en_uso - insumo.cantidad)
                        liberados.append(f"{insumo.cantidad} {flor.nombre}")
                elif insumo.insumo_tipo == 'Contenedor':
                    contenedor = Contenedor.query.get(insumo.insumo_id)
                    if contenedor:
                        # Liberar la reserva
                        contenedor.cantidad_en_uso = max(0, contenedor.cantidad_en_uso - insumo.cantidad)
                        liberados.append(f"{insumo.cantidad} {contenedor.nombre or contenedor.tipo}")

            # NO hacer commit aquí - será parte de la transacción del caller

            if liberados:
                return True, f"Insumos liberados: {', '.join(liberados)}"
            else:
                return True, "No hay insumos reservados para liberar"

        except Exception as e:
            return False, f"Error al liberar insumos: {str(e)}"

    @staticmethod
    def _consumir_insumos_pedido(pedido_id):
        """
        Consume los insumos de un pedido (decrementa cantidad_stock Y cantidad_en_uso)
        Se llama cuando un pedido pasa a "Listo para Despacho"

        Esto representa el uso FÍSICO de los insumos al armar el pedido.
        Decrementamos AMBOS: stock (consumo real) y en_uso (liberamos la reserva)
        De esta forma cantidad_disponible se mantiene correcta sin doble descuento.

        NOTA: NO hace commit, debe ser parte de una transacción mayor

        Args:
            pedido_id: ID del pedido

        Returns:
            tuple: (success, mensaje)
        """
        try:
            # Obtener todos los insumos del pedido
            insumos = PedidoInsumo.query.filter_by(pedido_id=pedido_id).all()

            consumidos = []
            for insumo in insumos:
                if insumo.insumo_tipo == 'Flor':
                    flor = Flor.query.get(insumo.insumo_id)
                    if flor:
                        # Consumir del stock real
                        flor.cantidad_stock = max(0, flor.cantidad_stock - insumo.cantidad)
                        # Liberar la reserva
                        flor.cantidad_en_uso = max(0, flor.cantidad_en_uso - insumo.cantidad)
                        consumidos.append(f"{insumo.cantidad} {flor.nombre}")
                        # Marcar como descontado
                        insumo.descontado_stock = True
                elif insumo.insumo_tipo == 'Contenedor':
                    contenedor = Contenedor.query.get(insumo.insumo_id)
                    if contenedor:
                        # Consumir del stock real
                        contenedor.cantidad_stock = max(0, contenedor.cantidad_stock - insumo.cantidad)
                        # Liberar la reserva
                        contenedor.cantidad_en_uso = max(0, contenedor.cantidad_en_uso - insumo.cantidad)
                        consumidos.append(f"{insumo.cantidad} {contenedor.nombre or contenedor.tipo}")
                        # Marcar como descontado
                        insumo.descontado_stock = True

            # NO hacer commit aquí - será parte de la transacción del caller

            if consumidos:
                return True, f"Insumos consumidos del stock: {', '.join(consumidos)}"
            else:
                return True, "No hay insumos para consumir"

        except Exception as e:
            return False, f"Error al consumir insumos: {str(e)}"

    @staticmethod
    def actualizar_estado(pedido_id, nuevo_estado):
        """
        Actualiza el estado de un pedido

        Args:
            pedido_id: ID del pedido
            nuevo_estado: nuevo estado del pedido

        Returns:
            tuple: (success, pedido/error, mensaje)
        """
        try:
            pedido = Pedido.query.get(pedido_id)
            if not pedido:
                return False, None, 'Pedido no encontrado'

            estado_anterior = pedido.estado
            pedido.estado = nuevo_estado
            pedido.fecha_actualizacion = datetime.now()  # Actualizar timestamp

            # Registrar en historial (marcar como cambio manual)
            from models.pedido import HistorialEstado
            historial = HistorialEstado(
                pedido_id=pedido_id,
                estado_anterior=estado_anterior,
                estado_nuevo=nuevo_estado,
                fecha_cambio=datetime.now(),
                notas='Cambio manual desde tablero'
            )
            db.session.add(historial)

            # 🔄 Gestión de consumo de insumos según cambio de estado
            mensaje_insumos = ""

            # Cuando el pedido pasa a "Listo para Despacho" → consumir insumos físicamente
            if nuevo_estado == "Listo para Despacho" and estado_anterior != "Listo para Despacho":
                # Verificar que los insumos no hayan sido ya descontados
                insumos = PedidoInsumo.query.filter_by(pedido_id=pedido_id).all()
                ya_descontados = all(insumo.descontado_stock for insumo in insumos) if insumos else False

                if not ya_descontados:
                    success_consumo, msg_consumo = PedidosService._consumir_insumos_pedido(pedido_id)
                    if success_consumo:
                        mensaje_insumos = f" | {msg_consumo}"
                    else:
                        # Si falla el consumo, hacer rollback del cambio de estado también
                        db.session.rollback()
                        return False, None, msg_consumo

            db.session.commit()

            return True, pedido, f'Estado actualizado de "{estado_anterior}" a "{nuevo_estado}"{mensaje_insumos}'

        except Exception as e:
            db.session.rollback()
            return False, None, str(e)

    @staticmethod
    def cancelar_pedido(pedido_id, motivo_cancelacion=None):
        """
        Cancela un pedido y devuelve el stock si fue descontado

        Args:
            pedido_id: ID del pedido
            motivo_cancelacion: motivo de la cancelación

        Returns:
            tuple: (success, pedido/error, mensaje)
        """
        try:
            pedido = Pedido.query.get(pedido_id)
            if not pedido:
                return False, None, 'Pedido no encontrado'

            # Devolver stock si fue descontado (insumos que ya pasaron por "Listo para Despacho")
            from services.inventario_service import InventarioService
            success_devolucion, mensaje_stock = InventarioService.devolver_stock_pedido(pedido_id)

            # Liberar insumos reservados (insumos que no fueron descontados aún)
            success_liberacion, mensaje_liberacion = PedidosService._liberar_insumos_pedido(pedido_id)

            # Cambiar estado a cancelado
            pedido.estado = 'Cancelado'
            if motivo_cancelacion:
                pedido.detalles_adicionales = f"{pedido.detalles_adicionales or ''}\n[CANCELADO: {motivo_cancelacion}]"

            # Actualizar estadísticas del cliente (recalcular desde pedidos activos)
            if pedido.cliente_id:
                from services.clientes_service import ClientesService
                ClientesService.actualizar_estadisticas_cliente(pedido.cliente_id)
            
            db.session.commit()

            mensajes = []
            if success_devolucion and mensaje_stock:
                mensajes.append(mensaje_stock)
            if success_liberacion and mensaje_liberacion:
                mensajes.append(mensaje_liberacion)

            mensaje_final = f'Pedido #{pedido_id} cancelado'
            if mensajes:
                mensaje_final += f'. {" | ".join(mensajes)}'

            return True, pedido, mensaje_final

        except Exception as e:
            db.session.rollback()
            return False, None, str(e)

    @staticmethod
    def eliminar_pedido(pedido_id):
        """
        Elimina un pedido y libera/devuelve sus insumos

        Args:
            pedido_id: ID del pedido

        Returns:
            tuple: (success, mensaje)
        """
        try:
            pedido = Pedido.query.get(pedido_id)
            if not pedido:
                return False, 'Pedido no encontrado'

            # Devolver stock si fue descontado (insumos consumidos físicamente)
            from services.inventario_service import InventarioService
            InventarioService.devolver_stock_pedido(pedido_id)

            # Liberar insumos reservados (insumos que no fueron descontados aún)
            PedidosService._liberar_insumos_pedido(pedido_id)

            # Guardar información del cliente antes de eliminar
            cliente_id = pedido.cliente_id
            precio_total_pedido = (pedido.precio_ramo or 0) + (pedido.precio_envio or 0)

            # Eliminar historial de estados (debe hacerse antes de eliminar el pedido)
            from models.pedido import HistorialEstado
            HistorialEstado.query.filter_by(pedido_id=pedido_id).delete()

            # Eliminar productos del pedido (si existen)
            from models.pedido import PedidoProducto
            PedidoProducto.query.filter_by(pedido_id=pedido_id).delete()

            # Eliminar insumos asociados
            PedidoInsumo.query.filter_by(pedido_id=pedido_id).delete()

            # Eliminar pedido
            db.session.delete(pedido)
            
            # Actualizar estadísticas del cliente (recalcular desde pedidos activos)
            if cliente_id:
                from services.clientes_service import ClientesService
                ClientesService.actualizar_estadisticas_cliente(cliente_id)
            
            db.session.commit()

            return True, f'Pedido #{pedido_id} eliminado correctamente'

        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def actualizar_pedido(pedido_id, data):
        """
        Actualiza los datos de un pedido existente

        Args:
            pedido_id: ID del pedido
            data: dict con los campos a actualizar

        Returns:
            tuple: (success, pedido/error, mensaje)
        """
        try:
            pedido = Pedido.query.get(pedido_id)
            if not pedido:
                return False, None, 'Pedido no encontrado'

            # Actualizar campos permitidos
            campos_actualizables = [
                'cliente_nombre', 'cliente_telefono', 'cliente_email',
                'arreglo_pedido', 'detalles_adicionales', 'precio_ramo', 'precio_envio',
                'destinatario', 'mensaje', 'firma', 'direccion_entrega', 'comuna',
                'motivo', 'estado', 'estado_pago', 'metodo_pago', 'documento_tributario',
                'fecha_entrega', 'dia_entrega'
            ]

            for campo in campos_actualizables:
                if campo in data:
                    setattr(pedido, campo, data[campo])

            # Reclasificar si cambia la fecha de entrega
            if 'fecha_entrega' in data:
                try:
                    # Si viene como string ISO, parsearlo
                    if isinstance(data['fecha_entrega'], str):
                        fecha_entrega = datetime.fromisoformat(data['fecha_entrega'].replace('Z', '+00:00'))
                    else:
                        fecha_entrega = data['fecha_entrega']
                    
                    # Si también viene hora_entrega, combinarla con la fecha
                    if 'hora_entrega' in data and data['hora_entrega']:
                        try:
                            from datetime import time
                            hora_parts = data['hora_entrega'].split(':')
                            if len(hora_parts) >= 2:
                                hora = int(hora_parts[0])
                                minuto = int(hora_parts[1])
                                fecha_entrega = fecha_entrega.replace(hour=hora, minute=minuto, second=0, microsecond=0)
                        except (ValueError, AttributeError) as e:
                            print(f'[WARNING] Error al parsear hora_entrega: {e}')
                    
                    pedido.fecha_entrega = fecha_entrega
                    clasificacion = clasificar_pedido(fecha_entrega)
                    pedido.estado = clasificacion['estado']
                    pedido.dia_entrega = clasificacion['dia_entrega']
                except Exception as e:
                    print(f'[ERROR] Error al actualizar fecha_entrega: {e}')
                    # Si hay error, intentar asignar directamente
                    if isinstance(data['fecha_entrega'], str):
                        try:
                            pedido.fecha_entrega = datetime.fromisoformat(data['fecha_entrega'].replace('Z', '+00:00'))
                        except:
                            pass

            db.session.commit()

            return True, pedido, f'Pedido #{pedido_id} actualizado'

        except Exception as e:
            db.session.rollback()
            return False, None, str(e)

    @staticmethod
    def obtener_pedidos_tablero(filtros=None):
        """
        Obtiene pedidos para vista de tablero Kanban

        Args:
            filtros: dict con estado, dia_entrega, estado_pago, tipo_pedido, incluir_despachados

        Returns:
            list: pedidos organizados por estado
        """
        query = Pedido.query.filter(Pedido.estado != 'Cancelado')

        # Por defecto, excluir pedidos despachados ANTIGUOS (más de 7 días)
        # Esto permite ver despachados recientes sin cargar todo el historial
        incluir_despachados = filtros and filtros.get('incluir_despachados', False) if filtros else False

        if not incluir_despachados:
            # Excluir despachados según el número de semanas solicitado
            # Por defecto muestra 1 semana (7 días), pero puede incrementarse con semanas_despachados
            semanas = filtros.get('semanas_despachados', 1) if filtros else 1
            fecha_limite_despachados = datetime.now() - timedelta(weeks=semanas)
            print(f'[DEBUG] Fecha límite despachados: {fecha_limite_despachados}')
            query = query.filter(
                or_(
                    Pedido.estado != 'Despachados',
                    and_(
                        Pedido.estado == 'Despachados',
                        Pedido.fecha_entrega >= fecha_limite_despachados
                    )
                )
            )
            print(f'[DEBUG] Query despachados aplicada')

        # Excluir pedidos con fecha de entrega muy pasada (más de 30 días atrás)
        # IMPORTANTE: NO aplicar este filtro a Despachados, ellos tienen su propio filtro por semanas
        fecha_limite_pasada = datetime.now() - timedelta(days=30)
        query = query.filter(
            or_(
                Pedido.estado == 'Despachados',  # Despachados se filtran por semanas, no por 30 días
                Pedido.fecha_entrega.is_(None),
                Pedido.fecha_entrega >= fecha_limite_pasada
            )
        )
        
        if incluir_despachados:
            # Cuando se incluyen despachados, solo mostrar los de las últimas 2 semanas
            fecha_limite = datetime.now() - timedelta(weeks=2)
            # Filtrar despachados solo de las últimas 2 semanas
            query = query.filter(
                or_(
                    Pedido.estado != 'Despachados',
                    and_(
                        Pedido.estado == 'Despachados',
                        or_(
                            Pedido.fecha_entrega >= fecha_limite,
                            Pedido.fecha_pedido >= fecha_limite
                        )
                    )
                )
            )

        if filtros:
            if filtros.get('estado'):
                query = query.filter_by(estado=filtros['estado'])
            if filtros.get('dia_entrega'):
                query = query.filter_by(dia_entrega=filtros['dia_entrega'])
            if filtros.get('estado_pago'):
                query = query.filter_by(estado_pago=filtros['estado_pago'])
            if filtros.get('tipo_pedido'):
                query = query.filter_by(tipo_pedido=filtros['tipo_pedido'])

        pedidos = query.order_by(Pedido.fecha_entrega.asc()).all()

        # Inicializar tablero con todos los estados posibles
        tablero = {
            'Entregas de Hoy': [],
            'Entregas para Mañana': [],
            'Entregas Semana': [],
            'Entregas Próx Semana': [],
            'Entregas Este Mes': [],
            'Entregas Próx Mes': [],
            'Entregas Futuras': [],
            'En Proceso': [],
            'Listo para Despacho': [],
            'Retiro en Tienda': [],
            'Despachados': []
        }

        # Agrupar por estado
        # NOTA: NO filtrar despachados aquí porque ya se filtró en la consulta SQL
        # según la fecha (los recientes sí se incluyen, los antiguos no)
        # NOTA: Los pedidos con retiro_en_tienda siguen el flujo normal hasta que se confirman insumos
        # Solo se separan en "Retiro en Tienda" cuando su estado es "Retiro en Tienda"
        for pedido in pedidos:
            estado = pedido.estado or 'Sin Estado'
            if estado not in tablero:
                tablero[estado] = []
            tablero[estado].append(pedido.to_dict())

        # Ya no necesitamos filtrar despachados aquí porque la consulta SQL
        # ya los filtró correctamente según la fecha
        if False:  # Código anterior deshabilitado
            for estado, pedidos_lista in tablero.items():
                if estado != 'Despachados':
                    # Filtrar cualquier pedido que tenga estado "Despachados"
                    tablero[estado] = [p for p in pedidos_lista if p.get('estado') != 'Despachados']

        return tablero

    @staticmethod
    def actualizar_cobranza(pedido_id, data):
        """
        Actualiza información de cobranza/pago de un pedido

        Args:
            pedido_id: ID del pedido
            data: dict con estado_pago, metodo_pago, documento_tributario, etc.

        Returns:
            tuple: (success, pedido/error, mensaje)
        """
        try:
            pedido = Pedido.query.get(pedido_id)
            if not pedido:
                return False, None, 'Pedido no encontrado'

            # Actualizar campos de cobranza
            if 'estado_pago' in data:
                pedido.estado_pago = data['estado_pago']
            if 'metodo_pago' in data:
                pedido.metodo_pago = data['metodo_pago']
            if 'documento_tributario' in data:
                pedido.documento_tributario = data['documento_tributario']
            if 'numero_documento' in data:
                pedido.numero_documento = data['numero_documento']
                # Si se agrega un número de documento, automáticamente marcar como emitido
                if data['numero_documento'] and data['numero_documento'].strip():
                    if pedido.documento_tributario == 'Hacer boleta':
                        pedido.documento_tributario = 'Boleta emitida'
                    elif pedido.documento_tributario == 'Hacer factura':
                        pedido.documento_tributario = 'Factura emitida'
            if 'monto_pagado' in data:
                pedido.monto_pagado = data['monto_pago']
            if 'fecha_pago' in data:
                pedido.fecha_pago = datetime.fromisoformat(data['fecha_pago'])
            if 'cobranza' in data or 'notas' in data:
                # Aceptar tanto 'cobranza' como 'notas' para compatibilidad
                pedido.cobranza = data.get('cobranza') or data.get('notas') or None
            
            # Lógica automática: Si está pagado con BICE, automáticamente marcar documento como "No requiere"
            # Esto se aplica tanto si se actualiza el método de pago como si ya estaba pagado con BICE
            if pedido.estado_pago == 'Pagado' and pedido.metodo_pago == 'Tr. BICE':
                if pedido.documento_tributario in ['Hacer boleta', 'Hacer factura', 'Falta boleta o factura', None]:
                    pedido.documento_tributario = 'No requiere'
            
            # Lógica adicional: Si tiene número de documento pero el estado sigue siendo "Hacer boleta/factura", actualizar
            if pedido.numero_documento and pedido.numero_documento.strip():
                if pedido.documento_tributario == 'Hacer boleta':
                    pedido.documento_tributario = 'Boleta emitida'
                elif pedido.documento_tributario == 'Hacer factura':
                    pedido.documento_tributario = 'Factura emitida'

            db.session.commit()

            return True, pedido, f'Cobranza actualizada para pedido #{pedido_id}'

        except Exception as e:
            db.session.rollback()
            return False, None, str(e)

    @staticmethod
    def obtener_resumen_cobranza():
        """
        Obtiene resumen de cobranza: pagados, pendientes, vencidos, sin documentar

        Returns:
            dict: resumen con totales, montos y listas de pedidos
        """
        hoy = datetime.now()

        # Pedidos pagados
        pagados = Pedido.query.filter_by(estado_pago='Pagado').count()
        monto_pagado = db.session.query(func.sum(Pedido.precio_ramo + Pedido.precio_envio))\
            .filter_by(estado_pago='Pagado').scalar() or 0

        # Pedidos sin pagar (pendientes)
        # Incluir todos los que NO están pagados (incluyendo NULL)
        pedidos_sin_pagar = Pedido.query.filter(
            or_(
                Pedido.estado_pago != 'Pagado',
                Pedido.estado_pago.is_(None)
            ),
            Pedido.estado != 'Cancelado'
        ).order_by(
            Pedido.fecha_maxima_pago.asc().nullslast()
        ).all()
        
        pendientes = len(pedidos_sin_pagar)
        monto_pendiente = db.session.query(func.sum(Pedido.precio_ramo + Pedido.precio_envio))\
            .filter(Pedido.estado_pago != 'Pagado', Pedido.estado != 'Cancelado').scalar() or 0

        # Pedidos vencidos
        vencidos = Pedido.query.filter(
            Pedido.estado_pago != 'Pagado',
            Pedido.fecha_maxima_pago < hoy,
            Pedido.estado != 'Cancelado'
        ).count()
        monto_vencido = db.session.query(func.sum(Pedido.precio_ramo + Pedido.precio_envio))\
            .filter(Pedido.estado_pago != 'Pagado',
                   Pedido.fecha_maxima_pago < hoy,
                   Pedido.estado != 'Cancelado').scalar() or 0

        # Pedidos sin documentar
        # Lógica: Si está pagado con BICE, no requiere documento
        # Solo mostrar como pendiente de documento si:
        # 1. Está pagado Y
        # 2. No es pagado con BICE Y
        # 3. El documento está en estado pendiente ("Hacer boleta", "Hacer factura", "Falta boleta o factura", NULL)
        # 4. NO está ya emitido ("Boleta emitida", "Factura emitida", "No requiere")
        pedidos_sin_documentar = Pedido.query.filter(
            Pedido.estado_pago == 'Pagado',
            Pedido.estado != 'Cancelado',
            # Excluir pagos con BICE (no requieren documento)
            or_(
                Pedido.metodo_pago.is_(None),
                Pedido.metodo_pago != 'Tr. BICE'
            ),
            # Solo los que necesitan documento (pendientes) Y que NO están ya emitidos
            and_(
                or_(
                    Pedido.documento_tributario == 'Hacer boleta',
                    Pedido.documento_tributario == 'Hacer factura',
                    Pedido.documento_tributario == 'Falta boleta o factura',
                    Pedido.documento_tributario.is_(None)
                ),
                # Excluir explícitamente los que ya están completados
                or_(
                    Pedido.documento_tributario.is_(None),
                    and_(
                        Pedido.documento_tributario != 'Boleta emitida',
                        Pedido.documento_tributario != 'Factura emitida',
                        Pedido.documento_tributario != 'No requiere'
                    )
                )
            )
        ).order_by(Pedido.fecha_pedido.desc()).all()

        sin_documentar = len(pedidos_sin_documentar)
        monto_sin_documentar = sum(
            float((p.precio_ramo or 0) + (p.precio_envio or 0))
            for p in pedidos_sin_documentar
        )

        return {
            'pagados': {
                'cantidad': pagados,
                'monto': float(monto_pagado)
            },
            'pendientes': {
                'cantidad': pendientes,
                'monto': float(monto_pendiente)
            },
            'vencidos': {
                'cantidad': vencidos,
                'monto': float(monto_vencido)
            },
            'sin_pagar': {
                'cantidad': pendientes,
                'total': float(monto_pendiente),
                'pedidos': [p.to_dict() for p in pedidos_sin_pagar]
            },
            'sin_documentar': {
                'cantidad': sin_documentar,
                'total': float(monto_sin_documentar),
                'pedidos': [p.to_dict() for p in pedidos_sin_documentar]
            }
        }

    @staticmethod
    def actualizar_estados_por_fecha():
        """
        Actualiza automáticamente los estados de pedidos según su fecha de entrega.
        Solo reclasifica pedidos que están en estados planificables (Pedidos Semana, etc.)
        No modifica estados de trabajo activo (En Proceso, Listo para Despacho) ni finales (Despachados, Entregado, Cancelado)

        Returns:
            tuple: (success, cantidad_actualizados, mensaje)
        """
        try:
            # Estados que pueden ser reclasificados automáticamente según fecha
            estados_reclasificables = [
                'Pedidos Semana',  # Estado antiguo, por compatibilidad
                'Entregas de Hoy',
                'Entregas para Mañana',
                'Entregas Semana',
                'Entregas Próx Semana',
                'Entregas Este Mes',
                'Entregas Próx Mes',
                'Entregas Futuras'
            ]
            
            # Obtener pedidos que están en estados reclasificables o que no tienen estado de trabajo activo
            # Excluir pedidos muy pasados (más de 30 días) para no clasificar pedidos antiguos
            # IMPORTANTE: Excluir estados de trabajo completado para que nunca se reclasifiquen automáticamente
            fecha_limite_pasada = datetime.now() - timedelta(days=30)
            from sqlalchemy.orm import joinedload
            pedidos = Pedido.query.options(
                joinedload(Pedido.historial_estados)
            ).filter(
                Pedido.estado != 'Cancelado',
                Pedido.estado != 'Entregado',
                Pedido.estado != 'Despachados',  # NUNCA reclasificar despachados
                Pedido.fecha_entrega.isnot(None),
                Pedido.fecha_entrega >= fecha_limite_pasada
            ).all()

            actualizados = 0

            # Estados de trabajo activo que NO deben ser sobrescritos automáticamente
            # Estos estados representan trabajo en progreso y deben respetarse si fueron cambiados manualmente
            estados_trabajo_activo = ['En Proceso', 'Listo para Despacho']
            
            for pedido in pedidos:
                if pedido.fecha_entrega:
                    clasificacion = clasificar_pedido(pedido.fecha_entrega)
                    nuevo_estado = clasificacion['estado']
                    estado_actual = pedido.estado
                    
                    # Verificar si el cambio fue manual reciente (últimas 24 horas)
                    cambio_manual_reciente = False
                    if pedido.historial_estados:
                        ultimo_cambio = max(pedido.historial_estados, key=lambda h: h.fecha_cambio)
                        horas_desde_cambio = (datetime.now() - ultimo_cambio.fecha_cambio).total_seconds() / 3600
                        # Si el cambio fue hace menos de 24 horas, considerarlo manual
                        if horas_desde_cambio < 24:
                            cambio_manual_reciente = True
                    
                    # Lógica de actualización:
                    # 1. Si el estado actual es reclasificable (Pedidos Semana, Entregas de Hoy, etc.), actualizar siempre
                    # 2. Si el estado actual es de trabajo activo ("En Proceso", "Listo para Despacho", "Taller"):
                    #    - NO actualizar si el cambio fue manual reciente (últimas 24 horas)
                    #    - Solo actualizar si la fecha es HOY o MAÑANA (urgencia crítica)
                    # 3. Nunca retroceder de estados de trabajo a estados planificables
                    debe_actualizar = False
                    
                    if estado_actual in estados_reclasificables:
                        # Siempre actualizar estados reclasificables
                        debe_actualizar = True
                    elif estado_actual in estados_trabajo_activo:
                        # Estados de trabajo activo: solo actualizar si:
                        # - NO fue un cambio manual reciente (últimas 24h)
                        # - Y la fecha es HOY o MAÑANA (urgencia crítica)
                        if not cambio_manual_reciente and nuevo_estado in ['Entregas de Hoy', 'Entregas para Mañana']:
                            debe_actualizar = True
                        else:
                            # No actualizar: respetar el estado de trabajo manual
                            debe_actualizar = False
                    elif nuevo_estado in ['Entregas de Hoy', 'Entregas para Mañana']:
                        # Si la fecha requiere urgencia y NO es un estado de trabajo, actualizar
                        debe_actualizar = True
                    
                    if debe_actualizar and (estado_actual != nuevo_estado or pedido.dia_entrega != clasificacion['dia_entrega']):
                        pedido.estado = nuevo_estado
                        pedido.dia_entrega = clasificacion['dia_entrega']
                        actualizados += 1

            db.session.commit()

            return True, actualizados, f'{actualizados} pedidos actualizados'

        except Exception as e:
            db.session.rollback()
            return False, 0, str(e)
    @staticmethod
    def obtener_pedidos_retiro_tienda(fecha_objetivo):
        """
        Obtiene pedidos con retiro en tienda para una fecha específica
        
        Args:
            fecha_objetivo: date - fecha de entrega objetivo
            
        Returns:
            tuple: (success, pedidos_list, mensaje)
        """
        try:
            from datetime import datetime, time
            from models.pedido import Pedido
            
            # Obtener pedidos con retiro en tienda para la fecha objetivo
            inicio_dia = datetime.combine(fecha_objetivo, time.min)
            fin_dia = datetime.combine(fecha_objetivo, time.max)
            
            pedidos = Pedido.query.filter(
                and_(
                    Pedido.fecha_entrega >= inicio_dia,
                    Pedido.fecha_entrega <= fin_dia,
                    Pedido.estado.notin_(['Despachados', 'Cancelado']),
                    Pedido.retiro_en_tienda == True
                )
            ).order_by(Pedido.es_urgente.desc(), Pedido.fecha_entrega.asc()).all()
            
            # Convertir a lista de diccionarios
            pedidos_list = []
            for pedido in pedidos:
                hora_llegada = pedido.fecha_entrega.strftime('%H:%M') if pedido.fecha_entrega and pedido.fecha_entrega.hour != 0 else 'Sin hora'
                
                pedido_dict = pedido.to_dict()
                pedido_dict['hora_llegada'] = hora_llegada
                pedidos_list.append(pedido_dict)
            
            return True, pedidos_list, f'{len(pedidos_list)} pedidos con retiro en tienda'
            
        except Exception as e:
            return False, [], f"Error al obtener pedidos con retiro en tienda: {str(e)}"

    @staticmethod
    def obtener_rutas_por_comuna(fecha_objetivo):
        """
        Obtiene pedidos agrupados por comuna para planificar rutas

        Args:
            fecha_objetivo: date - fecha de entrega objetivo

        Returns:
            tuple: (success, rutas_dict, mensaje)
        """
        try:
            from datetime import datetime, time
            from sqlalchemy import and_, or_
            from models.pedido import Pedido

            # Obtener pedidos para la fecha objetivo (no despachados ni cancelados)
            # Excluir retiro en tienda (se manejan por separado)
            inicio_dia = datetime.combine(fecha_objetivo, time.min)
            fin_dia = datetime.combine(fecha_objetivo, time.max)

            pedidos = Pedido.query.filter(
                and_(
                    Pedido.fecha_entrega >= inicio_dia,
                    Pedido.fecha_entrega <= fin_dia,
                    Pedido.estado.notin_(['Despachados', 'Cancelado']),
                    or_(Pedido.retiro_en_tienda == False, Pedido.retiro_en_tienda.is_(None))  # Excluir retiro en tienda
                )
            ).order_by(Pedido.es_urgente.desc(), Pedido.fecha_entrega.asc()).all()

            # Agrupar por comuna
            rutas = {}
            for pedido in pedidos:
                comuna = pedido.comuna or 'Sin Comuna'

                if comuna not in rutas:
                    rutas[comuna] = {
                        'comuna': comuna,
                        'pedidos': [],
                        'total_pedidos': 0,
                        'urgentes': 0
                    }

                # Calcular hora de llegada
                hora_llegada = pedido.fecha_entrega.strftime('%H:%M') if pedido.fecha_entrega and pedido.fecha_entrega.hour != 0 else 'Sin hora'

                # Obtener foto de respaldo del pedido
                foto_respaldo = None
                # Primero intentar desde el pedido directamente
                if hasattr(pedido, 'foto_enviado_url') and pedido.foto_enviado_url:
                    foto_respaldo = pedido.foto_enviado_url
                # Si no, buscar en los productos asociados usando query directa para evitar problemas de lazy loading
                else:
                    try:
                        from models.pedido import PedidoProducto
                        # Buscar productos del pedido usando query directa
                        pedido_productos = PedidoProducto.query.filter_by(pedido_id=pedido.id).all()
                        for pp in pedido_productos:
                            if pp.foto_respaldo:
                                foto_respaldo = pp.foto_respaldo
                                break
                    except Exception:
                        # Si hay algún error, simplemente continuar sin foto
                        pass

                pedido_data = {
                    'id': pedido.id,
                    'cliente_nombre': pedido.cliente_nombre,
                    'direccion': pedido.direccion_entrega,
                    'telefono': pedido.cliente_telefono,
                    'hora_llegada': hora_llegada,
                    'motivo': pedido.motivo,
                    'es_urgente': pedido.es_urgente or False,
                    'arreglo': pedido.arreglo_pedido,
                    'estado': pedido.estado,
                    'destinatario': pedido.destinatario,
                    'mensaje': pedido.mensaje,
                    'detalles_adicionales': pedido.detalles_adicionales,
                    'foto_respaldo': foto_respaldo
                }

                rutas[comuna]['pedidos'].append(pedido_data)
                rutas[comuna]['total_pedidos'] += 1
                if pedido.es_urgente:
                    rutas[comuna]['urgentes'] += 1

            # Convertir a lista y ordenar por urgentes (más urgentes primero)
            rutas_lista = list(rutas.values())
            rutas_lista.sort(key=lambda x: x['urgentes'], reverse=True)

            return True, rutas_lista, f'{len(pedidos)} pedidos encontrados'

        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            # Log el error completo para debugging
            print(f"ERROR en obtener_rutas_por_comuna: {str(e)}")
            print(f"Traceback completo:\n{error_trace}")
            return False, [], str(e)

    @staticmethod
    def marcar_urgente(pedido_id, es_urgente):
        """
        Marca o desmarca un pedido como urgente

        Args:
            pedido_id: ID del pedido
            es_urgente: boolean - True para marcar como urgente

        Returns:
            tuple: (success, pedido, mensaje)
        """
        try:
            from models.pedido import Pedido

            pedido = Pedido.query.get(pedido_id)
            if not pedido:
                return False, None, 'Pedido no encontrado'

            pedido.es_urgente = es_urgente
            db.session.commit()

            mensaje = f'Pedido #{pedido_id} marcado como urgente' if es_urgente else f'Pedido #{pedido_id} desmarcado como urgente'
            return True, pedido, mensaje

        except Exception as e:
            db.session.rollback()
            return False, None, str(e)

    @staticmethod
    def marcar_multiples_despachados(pedidos_ids):
        """
        Marca múltiples pedidos como despachados

        Args:
            pedidos_ids: list - lista de IDs de pedidos

        Returns:
            tuple: (success, resultado_dict, mensaje)
        """
        try:
            from models.pedido import Pedido

            actualizados = 0
            no_encontrados = []

            for pedido_id in pedidos_ids:
                pedido = Pedido.query.get(pedido_id)
                if pedido:
                    pedido.estado = 'Despachados'
                    actualizados += 1
                else:
                    no_encontrados.append(pedido_id)

            db.session.commit()

            resultado = {
                'actualizados': actualizados,
                'no_encontrados': no_encontrados,
                'total': len(pedidos_ids)
            }

            mensaje = f'{actualizados} pedidos marcados como despachados'
            if no_encontrados:
                mensaje += f', {len(no_encontrados)} no encontrados'

            return True, resultado, mensaje

        except Exception as e:
            db.session.rollback()
            return False, {}, str(e)

    @staticmethod
    def generar_documento_repartidor(fecha_objetivo):
        """
        Genera estructura de datos para documento del repartidor

        Args:
            fecha_objetivo: date - fecha de entrega objetivo

        Returns:
            tuple: (success, documento_dict, mensaje)
        """
        try:
            # Reutilizar función de rutas
            success, rutas, mensaje = PedidosService.obtener_rutas_por_comuna(fecha_objetivo)

            if not success:
                return False, {}, mensaje

            documento = {
                'fecha': fecha_objetivo.isoformat(),
                'fecha_formateada': fecha_objetivo.strftime('%d/%m/%Y'),
                'rutas': rutas,
                'total_pedidos': sum(r['total_pedidos'] for r in rutas),
                'total_urgentes': sum(r['urgentes'] for r in rutas)
            }

            return True, documento, 'Documento generado exitosamente'

        except Exception as e:
            return False, {}, str(e)

    @staticmethod
    def generar_html_documento_repartidor(documento, fecha_objetivo):
        """
        Genera HTML imprimible para el repartidor

        Args:
            documento: dict - estructura del documento
            fecha_objetivo: date - fecha objetivo

        Returns:
            str: HTML
        """
        html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rutas de Entrega - {fecha_objetivo.strftime('%d/%m/%Y')}</title>
    <style>
        @media print {{
            @page {{ margin: 1cm; }}
            body {{ margin: 0; }}
        }}
        body {{
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            font-size: 12px;
        }}
        h1 {{
            text-align: center;
            color: #2c5282;
            margin-bottom: 10px;
        }}
        .fecha {{
            text-align: center;
            font-size: 18px;
            margin-bottom: 20px;
            font-weight: bold;
        }}
        .resumen {{
            background: #edf2f7;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        .resumen p {{
            margin: 5px 0;
            font-size: 14px;
        }}
        .comuna {{
            border: 2px solid #2c5282;
            border-radius: 8px;
            margin-bottom: 20px;
            page-break-inside: avoid;
        }}
        .comuna-header {{
            background: #2c5282;
            color: white;
            padding: 12px 15px;
            font-size: 16px;
            font-weight: bold;
            display: flex;
            justify-content: space-between;
        }}
        .pedido {{
            border-bottom: 1px solid #e2e8f0;
            padding: 12px 15px;
            display: grid;
            grid-template-columns: 60px 1fr 120px;
            gap: 15px;
            align-items: start;
        }}
        .pedido:last-child {{
            border-bottom: none;
        }}
        .pedido.urgente {{
            background: #fff5f5;
            border-left: 4px solid #fc8181;
        }}
        .pedido-numero {{
            font-weight: bold;
            font-size: 16px;
            color: #2c5282;
        }}
        .pedido-info {{
            flex: 1;
        }}
        .pedido-info strong {{
            color: #2d3748;
        }}
        .pedido-info p {{
            margin: 3px 0;
            line-height: 1.4;
        }}
        .hora {{
            text-align: right;
            font-size: 16px;
            font-weight: bold;
            color: #2c5282;
        }}
        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 10px;
            font-weight: bold;
            margin-right: 5px;
        }}
        .badge-urgente {{
            background: #fc8181;
            color: white;
        }}
        .badge-motivo {{
            background: #90cdf4;
            color: #1a365d;
        }}
        .foto-respaldo {{
            max-width: 150px;
            max-height: 150px;
            margin-top: 8px;
            border-radius: 8px;
            border: 2px solid #e2e8f0;
        }}
    </style>
</head>
<body>
    <h1>🚚 Rutas de Entrega - Las Lira</h1>
    <div class="fecha">{fecha_objetivo.strftime('%A, %d de %B de %Y')}</div>

    <div class="resumen">
        <p><strong>Total de Pedidos:</strong> {documento['total_pedidos']}</p>
        <p><strong>Pedidos Urgentes:</strong> {documento['total_urgentes']}</p>
        <p><strong>Comunas a Visitar:</strong> {len(documento['rutas'])}</p>
    </div>
"""

        for ruta in documento['rutas']:
            html += f"""
    <div class="comuna">
        <div class="comuna-header">
            <span>{ruta['comuna']}</span>
            <span>{ruta['total_pedidos']} pedido(s)"""

            if ruta['urgentes'] > 0:
                html += f" - {ruta['urgentes']} urgente(s)"

            html += """</span>
        </div>
"""

            for pedido in ruta['pedidos']:
                urgente_class = ' urgente' if pedido['es_urgente'] else ''
                pedido_id = pedido['id']
                html += f"""
        <div class="pedido{urgente_class}">
            <div class="pedido-numero">#{pedido_id}</div>
            <div class="pedido-info">"""

                if pedido['es_urgente']:
                    html += '<span class="badge badge-urgente">URGENTE</span>'

                if pedido['motivo']:
                    motivo = pedido['motivo']
                    html += f'<span class="badge badge-motivo">{motivo}</span>'

                cliente = pedido['cliente_nombre']
                direccion = pedido['direccion']
                telefono = pedido['telefono']
                html += f"""
                <p><strong>{cliente}</strong></p>
                <p>📍 {direccion}</p>
                <p>📞 {telefono}</p>"""

                # Línea con destinatario, mensaje y detalles (si existen)
                info_linea = []
                if pedido.get('destinatario'):
                    info_linea.append(f"👤 Para: {pedido['destinatario']}")
                if pedido.get('mensaje'):
                    info_linea.append(f"💬 {pedido['mensaje']}")
                if pedido.get('detalles_adicionales'):
                    info_linea.append(f"📝 {pedido['detalles_adicionales']}")
                
                if info_linea:
                    html += f"<p>{' | '.join(info_linea)}</p>"

                if pedido.get('arreglo'):
                    arreglo = pedido['arreglo']
                    html += f"<p>🌸 {arreglo}</p>"

                # Agregar foto de respaldo si existe
                if pedido.get('foto_respaldo'):
                    foto_url = f"/api/upload/imagen/{pedido['foto_respaldo']}"
                    html += f'<p><img src="{foto_url}" class="foto-respaldo" alt="Foto de respaldo"></p>'

                hora = pedido['hora_llegada']
                html += f"""
            </div>
            <div class="hora">⏰ {hora}</div>
        </div>
"""

            html += """
    </div>
"""

        html += """
</body>
</html>
"""

        return html

    @staticmethod
    def generar_pdf_desde_html(html):
        """
        Genera un PDF desde HTML usando WeasyPrint
        
        Args:
            html: str - HTML a convertir
            
        Returns:
            bytes: PDF en formato bytes
        """
        try:
            from weasyprint import HTML
            from io import BytesIO
            
            pdf_buffer = BytesIO()
            HTML(string=html).write_pdf(pdf_buffer)
            pdf_buffer.seek(0)
            return pdf_buffer.getvalue()
        except Exception as e:
            raise Exception(f"Error al generar PDF: {str(e)}")
