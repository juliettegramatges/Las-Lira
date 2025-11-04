"""
Servicio de gestión de clientes
Contiene la lógica de negocio relacionada con clientes
"""

from extensions import db
from models.cliente import Cliente
from sqlalchemy import func, or_
from datetime import datetime


class ClientesService:
    """Servicio para operaciones de negocio de clientes"""

    @staticmethod
    def listar_clientes(filtros=None, buscar=None, page=1, limit=100):
        """
        Lista clientes con filtros, búsqueda y paginación

        Args:
            filtros: dict con tipo, etiquetas
            buscar: término de búsqueda
            page: número de página
            limit: registros por página

        Returns:
            tuple: (clientes, total, total_pages, stats)
        """
        query = Cliente.query

        # Filtrar por etiquetas
        if filtros and filtros.get('etiquetas'):
            etiqueta_ids = filtros['etiquetas']
            if etiqueta_ids:
                etiquetas_sql = ','.join(map(str, etiqueta_ids))
                sql_query = f'''
                    SELECT DISTINCT cliente_id
                    FROM cliente_etiquetas
                    WHERE etiqueta_id IN ({etiquetas_sql})
                '''
                subquery = db.session.execute(db.text(sql_query))
                cliente_ids = [row[0] for row in subquery]
                if cliente_ids:
                    query = query.filter(Cliente.id.in_(cliente_ids))
                else:
                    query = query.filter(Cliente.id.in_([]))

        # Filtrar por tipo
        if filtros and filtros.get('tipo'):
            query = query.filter_by(tipo_cliente=filtros['tipo'])

        # Buscar
        if buscar:
            query = query.filter(
                or_(
                    Cliente.nombre.ilike(f'%{buscar}%'),
                    Cliente.telefono.ilike(f'%{buscar}%'),
                    Cliente.email.ilike(f'%{buscar}%')
                )
            )

        # Contar total
        total = query.count()
        total_pages = (total + limit - 1) // limit

        # Paginar
        clientes = query.order_by(Cliente.nombre).limit(limit).offset((page - 1) * limit).all()

        # Calcular estadísticas
        stats = ClientesService.obtener_estadisticas()

        return clientes, total, total_pages, stats

    @staticmethod
    def obtener_estadisticas():
        """Obtiene estadísticas globales de clientes"""
        total_global = Cliente.query.count()

        def calcular_promedio_gasto(tipo):
            resultado = db.session.query(func.avg(Cliente.total_gastado)).filter_by(tipo_cliente=tipo).scalar()
            return float(resultado) if resultado else 0

        def calcular_promedio_pedidos(tipo):
            resultado = db.session.query(func.avg(Cliente.total_pedidos)).filter_by(tipo_cliente=tipo).scalar()
            return float(resultado) if resultado else 0

        stats = {
            'total': total_global,
            'vip': Cliente.query.filter_by(tipo_cliente='VIP').count(),
            'fiel': Cliente.query.filter_by(tipo_cliente='Fiel').count(),
            'nuevo': Cliente.query.filter_by(tipo_cliente='Nuevo').count(),
            'ocasional': Cliente.query.filter_by(tipo_cliente='Ocasional').count(),
            'cumplidor': Cliente.query.filter_by(tipo_cliente='Cumplidor').count(),
            'no_cumplidor': Cliente.query.filter_by(tipo_cliente='No Cumplidor').count(),
            'promedios': {
                'VIP': {
                    'gasto': calcular_promedio_gasto('VIP'),
                    'pedidos': calcular_promedio_pedidos('VIP')
                },
                'Fiel': {
                    'gasto': calcular_promedio_gasto('Fiel'),
                    'pedidos': calcular_promedio_pedidos('Fiel')
                },
                'Nuevo': {
                    'gasto': calcular_promedio_gasto('Nuevo'),
                    'pedidos': calcular_promedio_pedidos('Nuevo')
                }
            }
        }

        return stats

    @staticmethod
    def obtener_cliente(cliente_id):
        """Obtiene un cliente por ID con sus pedidos"""
        return Cliente.query.get(cliente_id)

    @staticmethod
    def crear_cliente(data):
        """
        Crea un nuevo cliente

        Args:
            data: dict con datos del cliente

        Returns:
            tuple: (success, cliente/error, mensaje)
        """
        try:
            cliente = Cliente(
                nombre=data['nombre'],
                telefono=data.get('telefono'),
                email=data.get('email'),
                tipo_cliente=data.get('tipo_cliente', 'Nuevo'),
                direccion=data.get('direccion'),
                comuna=data.get('comuna'),
                notas=data.get('notas')
            )

            db.session.add(cliente)
            db.session.commit()

            return True, cliente, 'Cliente creado exitosamente'

        except Exception as e:
            db.session.rollback()
            return False, None, str(e)

    @staticmethod
    def actualizar_cliente(cliente_id, data):
        """
        Actualiza un cliente existente

        Args:
            cliente_id: ID del cliente
            data: dict con campos a actualizar

        Returns:
            tuple: (success, cliente/error, mensaje)
        """
        try:
            cliente = Cliente.query.get(cliente_id)
            if not cliente:
                return False, None, 'Cliente no encontrado'

            # Actualizar campos
            campos_actualizables = ['nombre', 'telefono', 'email', 'tipo_cliente',
                                   'direccion', 'comuna', 'notas']

            for campo in campos_actualizables:
                if campo in data:
                    setattr(cliente, campo, data[campo])

            db.session.commit()

            return True, cliente, 'Cliente actualizado exitosamente'

        except Exception as e:
            db.session.rollback()
            return False, None, str(e)

    @staticmethod
    def eliminar_cliente(cliente_id):
        """
        Elimina un cliente

        Args:
            cliente_id: ID del cliente

        Returns:
            tuple: (success, mensaje)
        """
        try:
            cliente = Cliente.query.get(cliente_id)
            if not cliente:
                return False, 'Cliente no encontrado'

            db.session.delete(cliente)
            db.session.commit()

            return True, f'Cliente {cliente_id} eliminado'

        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def reclasificar_clientes():
        """
        Reclasifica clientes según su comportamiento de compra

        Lógica:
        - VIP: > $500,000 gastado o > 10 pedidos
        - Fiel: > $200,000 gastado o > 5 pedidos
        - Ocasional: 2-4 pedidos
        - Nuevo: 1 pedido

        Returns:
            tuple: (success, cantidad_reclasificados, mensaje)
        """
        try:
            clientes = Cliente.query.all()
            reclasificados = 0

            for cliente in clientes:
                tipo_anterior = cliente.tipo_cliente

                # Lógica de clasificación
                if cliente.total_gastado > 500000 or cliente.total_pedidos > 10:
                    nuevo_tipo = 'VIP'
                elif cliente.total_gastado > 200000 or cliente.total_pedidos > 5:
                    nuevo_tipo = 'Fiel'
                elif cliente.total_pedidos >= 2:
                    nuevo_tipo = 'Ocasional'
                else:
                    nuevo_tipo = 'Nuevo'

                if tipo_anterior != nuevo_tipo:
                    cliente.tipo_cliente = nuevo_tipo
                    reclasificados += 1

            db.session.commit()

            return True, reclasificados, f'{reclasificados} clientes reclasificados'

        except Exception as e:
            db.session.rollback()
            return False, 0, str(e)

    @staticmethod
    def actualizar_estadisticas_cliente(cliente_id):
        """
        Actualiza las estadísticas de un cliente basándose en sus pedidos

        Args:
            cliente_id: ID del cliente

        Returns:
            tuple: (success, mensaje)
        """
        try:
            from models.pedido import Pedido

            cliente = Cliente.query.get(cliente_id)
            if not cliente:
                return False, 'Cliente no encontrado'

            # Contar pedidos
            pedidos = Pedido.query.filter_by(cliente_id=cliente_id).all()
            cliente.total_pedidos = len(pedidos)

            # Calcular total gastado
            total_gastado = sum(p.precio_total for p in pedidos)
            cliente.total_gastado = total_gastado

            # Última compra
            if pedidos:
                ultima_compra = max(p.fecha_pedido for p in pedidos)
                cliente.ultima_compra = ultima_compra

            db.session.commit()

            return True, 'Estadísticas actualizadas'

        except Exception as e:
            db.session.rollback()
            return False, str(e)
