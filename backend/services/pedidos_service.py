"""
Servicio de gestión de pedidos
Contiene toda la lógica de negocio relacionada con pedidos
"""

from extensions import db
from models.pedido import Pedido, PedidoInsumo
from models.cliente import Cliente
from config.plazos_pago import obtener_plazo_pago
from utils.fecha_helpers import clasificar_pedido
from datetime import datetime, timedelta
from sqlalchemy import or_, and_, func
import re


class PedidosService:
    """Servicio para operaciones de negocio de pedidos"""

    @staticmethod
    def normalizar_telefono(telefono):
        """Normaliza un número de teléfono eliminando caracteres no numéricos"""
        if not telefono:
            return ""
        # Eliminar todo excepto dígitos y +
        return re.sub(r'[^\d+]', '', str(telefono))

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
        telefono_normalizado = PedidosService.normalizar_telefono(data['cliente_telefono'])

        # Si viene cliente_id, buscar por ID
        if data.get('cliente_id'):
            cliente = Cliente.query.get(data['cliente_id'])
            if cliente:
                return cliente

        # Buscar por teléfono normalizado
        todos_clientes = Cliente.query.all()
        for c in todos_clientes:
            if PedidosService.normalizar_telefono(c.telefono) == telefono_normalizado:
                return c

        # Cliente no existe, crear uno nuevo
        cliente = Cliente(
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
            telefono_normalizado = PedidosService.normalizar_telefono(data['cliente_telefono'])

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
                dia_entrega=clasificacion['dia_entrega']
            )

            db.session.add(pedido)

            # Actualizar estadísticas del cliente
            if cliente:
                cliente.total_pedidos += 1
                cliente.total_gastado = (cliente.total_gastado or 0) + pedido.precio_total
                cliente.ultima_compra = datetime.now()

            db.session.commit()

            return True, pedido, f'Pedido #{pedido.id} creado exitosamente'

        except Exception as e:
            db.session.rollback()
            return False, None, str(e)

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

            # Registrar en historial
            from models.pedido import HistorialEstado
            historial = HistorialEstado(
                pedido_id=pedido_id,
                estado_anterior=estado_anterior,
                estado_nuevo=nuevo_estado,
                fecha_cambio=datetime.now()
            )
            db.session.add(historial)

            db.session.commit()

            return True, pedido, f'Estado actualizado de "{estado_anterior}" a "{nuevo_estado}"'

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

            # Devolver stock si fue descontado
            from services.inventario_service import InventarioService
            success, mensaje_stock = InventarioService.devolver_stock_pedido(pedido_id)

            # Cambiar estado a cancelado
            pedido.estado = 'Cancelado'
            if motivo_cancelacion:
                pedido.detalles_adicionales = f"{pedido.detalles_adicionales or ''}\n[CANCELADO: {motivo_cancelacion}]"

            db.session.commit()

            mensaje_final = f'Pedido #{pedido_id} cancelado. {mensaje_stock if success else ""}'
            return True, pedido, mensaje_final

        except Exception as e:
            db.session.rollback()
            return False, None, str(e)

    @staticmethod
    def eliminar_pedido(pedido_id):
        """
        Elimina un pedido (soft delete o hard delete)

        Args:
            pedido_id: ID del pedido

        Returns:
            tuple: (success, mensaje)
        """
        try:
            pedido = Pedido.query.get(pedido_id)
            if not pedido:
                return False, 'Pedido no encontrado'

            # Eliminar insumos asociados
            PedidoInsumo.query.filter_by(pedido_id=pedido_id).delete()

            # Eliminar pedido
            db.session.delete(pedido)
            db.session.commit()

            return True, f'Pedido #{pedido_id} eliminado'

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
                fecha_entrega = datetime.fromisoformat(data['fecha_entrega'].replace('Z', '+00:00'))
                clasificacion = clasificar_pedido(fecha_entrega)
                pedido.estado = clasificacion['estado']
                pedido.dia_entrega = clasificacion['dia_entrega']

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
        
        # Por defecto, excluir pedidos despachados para mejorar rendimiento
        # Solo incluirlos si se solicita explícitamente con incluir_despachados=True
        incluir_despachados = filtros and filtros.get('incluir_despachados', False) if filtros else False
        
        # PRIMERO: Excluir despachados si no se solicitan explícitamente
        if not incluir_despachados:
            query = query.filter(Pedido.estado != 'Despachados')
        
        # Excluir pedidos con fecha de entrega muy pasada (más de 30 días atrás)
        # Solo mostrar pedidos futuros o recientes en el tablero activo
        fecha_limite_pasada = datetime.now() - timedelta(days=30)
        query = query.filter(
            or_(
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

        # Agrupar por estado (excluyendo despachados si no se solicitan)
        tablero = {}
        pedidos_filtrados = 0
        for pedido in pedidos:
            estado = pedido.estado or 'Sin Estado'
            # Doble verificación: nunca incluir despachados si no se solicitan explícitamente
            if not incluir_despachados and estado == 'Despachados':
                pedidos_filtrados += 1
                continue
            if estado not in tablero:
                tablero[estado] = []
            tablero[estado].append(pedido.to_dict())
        
        # FORZAR: Si no se solicitan despachados, eliminarlos completamente del resultado
        # Esto es una medida de seguridad adicional
        if not incluir_despachados:
            if 'Despachados' in tablero:
                del tablero['Despachados']
            # También verificar que no haya ningún pedido con estado "Despachados" en ningún estado
            tablero_limpio = {}
            for estado, pedidos_lista in tablero.items():
                if estado != 'Despachados':
                    pedidos_filtrados = [p for p in pedidos_lista if p.get('estado') != 'Despachados']
                    if pedidos_filtrados:
                        tablero_limpio[estado] = pedidos_filtrados
            tablero = tablero_limpio

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
            if 'monto_pagado' in data:
                pedido.monto_pagado = data['monto_pagado']
            if 'fecha_pago' in data:
                pedido.fecha_pago = datetime.fromisoformat(data['fecha_pago'])

            db.session.commit()

            return True, pedido, f'Cobranza actualizada para pedido #{pedido_id}'

        except Exception as e:
            db.session.rollback()
            return False, None, str(e)

    @staticmethod
    def obtener_resumen_cobranza():
        """
        Obtiene resumen de cobranza: pagados, pendientes, vencidos

        Returns:
            dict: resumen con totales y montos
        """
        hoy = datetime.now()

        # Pedidos pagados
        pagados = Pedido.query.filter_by(estado_pago='Pagado').count()
        monto_pagado = db.session.query(func.sum(Pedido.precio_ramo + Pedido.precio_envio))\
            .filter_by(estado_pago='Pagado').scalar() or 0

        # Pedidos pendientes
        pendientes = Pedido.query.filter(
            Pedido.estado_pago != 'Pagado',
            Pedido.estado != 'Cancelado'
        ).count()
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
                'Pedidos Semana',
                'Entregas de Hoy',
                'Entregas para Mañana'
            ]
            
            # Obtener pedidos que están en estados reclasificables o que no tienen estado de trabajo activo
            # Excluir pedidos muy pasados (más de 30 días) para no clasificar pedidos antiguos
            # IMPORTANTE: Excluir "Despachados" para que nunca se reclasifiquen automáticamente
            fecha_limite_pasada = datetime.now() - timedelta(days=30)
            pedidos = Pedido.query.filter(
                Pedido.estado != 'Cancelado',
                Pedido.estado != 'Entregado',
                Pedido.estado != 'Despachados',  # NUNCA reclasificar despachados
                Pedido.fecha_entrega.isnot(None),
                Pedido.fecha_entrega >= fecha_limite_pasada
            ).all()

            actualizados = 0

            for pedido in pedidos:
                if pedido.fecha_entrega:
                    clasificacion = clasificar_pedido(pedido.fecha_entrega)
                    nuevo_estado = clasificacion['estado']
                    estado_actual = pedido.estado
                    
                    # Lógica de actualización:
                    # 1. Si el estado actual es reclasificable (Pedidos Semana, Entregas de Hoy, Entregas para Mañana), actualizar siempre
                    # 2. Si el nuevo estado es urgente (Entregas de Hoy o Entregas para Mañana), actualizar siempre
                    #    (esto mueve pedidos de "En Proceso" o "Listo para Despacho" a estados urgentes si corresponde)
                    # 3. Si el estado actual es "En Proceso" o "Listo para Despacho" y el nuevo estado es "Pedidos Semana",
                    #    NO actualizar (no retroceder el flujo de trabajo)
                    debe_actualizar = False
                    
                    if estado_actual in estados_reclasificables:
                        # Siempre actualizar estados reclasificables
                        debe_actualizar = True
                    elif nuevo_estado in ['Entregas de Hoy', 'Entregas para Mañana']:
                        # Si la fecha requiere urgencia, actualizar (incluso si está en "En Proceso" o "Listo para Despacho")
                        debe_actualizar = True
                    elif estado_actual in ['En Proceso', 'Listo para Despacho'] and nuevo_estado == 'Pedidos Semana':
                        # No retroceder: si está en proceso y la fecha es futura, mantener el estado de trabajo
                        debe_actualizar = False
                    
                    if debe_actualizar and (estado_actual != nuevo_estado or pedido.dia_entrega != clasificacion['dia_entrega']):
                        pedido.estado = nuevo_estado
                        pedido.dia_entrega = clasificacion['dia_entrega']
                        actualizados += 1

            db.session.commit()

            return True, actualizados, f'{actualizados} pedidos actualizados'

        except Exception as e:
            db.session.rollback()
            return False, 0, str(e)
