"""
Servicio de gestión de colores de productos y sus flores asociadas
Contiene toda la lógica de negocio relacionada con la configuración de colores
"""

from extensions import db
from models.producto_detallado import ProductoColor, ProductoColorFlor
from models.producto import Producto
from models.inventario import Flor
import re


class ProductoColoresService:
    """Servicio para operaciones de negocio de colores de productos"""

    @staticmethod
    def obtener_colores_sugeridos(producto_id):
        """
        Obtiene y parsea los colores sugeridos desde el campo colores_asociados del producto

        Args:
            producto_id: ID del producto

        Returns:
            tuple: (success, data/error, message)
        """
        try:
            producto = Producto.query.get(producto_id)
            if not producto:
                return False, None, 'Producto no encontrado'

            colores_sugeridos = []

            if producto.colores_asociados:
                # Dividir por comas
                colores_lista = producto.colores_asociados.split(',')

                for color in colores_lista:
                    color_limpio = color.strip()

                    # Remover paréntesis finales mal formados
                    color_limpio = re.sub(r'\)$', '', color_limpio).strip()

                    # Si contiene "y", dividir
                    if ' y ' in color_limpio:
                        partes = color_limpio.split(' y ')
                        for parte in partes:
                            if parte.strip():
                                colores_sugeridos.append(parte.strip().capitalize())
                    else:
                        if color_limpio:
                            colores_sugeridos.append(color_limpio.capitalize())

            # Eliminar duplicados manteniendo orden, filtrar valores no deseados
            colores_unicos = []
            valores_excluir = ['', '—', 'A elección', 'Mixtos', 'Variable']
            for color in colores_sugeridos:
                if color not in colores_unicos and color not in valores_excluir:
                    colores_unicos.append(color)

            return True, colores_unicos, 'Colores obtenidos'

        except Exception as e:
            return False, None, str(e)

    @staticmethod
    def listar_colores_producto(producto_id):
        """
        Lista todos los colores configurados para un producto

        Args:
            producto_id: ID del producto

        Returns:
            tuple: (success, data/error, message)
        """
        try:
            producto = Producto.query.get(producto_id)
            if not producto:
                return False, None, 'Producto no encontrado'

            colores = ProductoColor.query.filter_by(
                producto_id=producto_id,
                activo=True
            ).order_by(ProductoColor.orden).all()

            return True, [color.to_dict() for color in colores], 'Colores listados'

        except Exception as e:
            return False, None, str(e)

    @staticmethod
    def crear_color_producto(producto_id, data):
        """
        Crea un nuevo color para un producto

        Args:
            producto_id: ID del producto
            data: dict con nombre_color, cantidad_flores_sugerida, orden, notas

        Returns:
            tuple: (success, color/error, message)
        """
        try:
            # Validar producto existe
            producto = Producto.query.get(producto_id)
            if not producto:
                return False, None, 'Producto no encontrado'

            # Crear color
            color = ProductoColor(
                producto_id=producto_id,
                nombre_color=data.get('nombre_color'),
                cantidad_flores_sugerida=data.get('cantidad_flores_sugerida', 0),
                orden=data.get('orden', 0),
                notas=data.get('notas')
            )

            db.session.add(color)
            db.session.commit()

            return True, color.to_dict(), f'Color "{color.nombre_color}" creado'

        except Exception as e:
            db.session.rollback()
            return False, None, str(e)

    @staticmethod
    def actualizar_color(color_id, data):
        """
        Actualiza un color existente

        Args:
            color_id: ID del color
            data: dict con campos a actualizar

        Returns:
            tuple: (success, color/error, message)
        """
        try:
            color = ProductoColor.query.get(color_id)
            if not color:
                return False, None, 'Color no encontrado'

            # Actualizar campos
            if 'nombre_color' in data:
                color.nombre_color = data['nombre_color']
            if 'cantidad_flores_sugerida' in data:
                color.cantidad_flores_sugerida = data['cantidad_flores_sugerida']
            if 'orden' in data:
                color.orden = data['orden']
            if 'notas' in data:
                color.notas = data['notas']

            db.session.commit()

            return True, color.to_dict(), f'Color "{color.nombre_color}" actualizado'

        except Exception as e:
            db.session.rollback()
            return False, None, str(e)

    @staticmethod
    def eliminar_color(color_id):
        """
        Elimina (desactiva) un color

        Args:
            color_id: ID del color

        Returns:
            tuple: (success, message, message)
        """
        try:
            color = ProductoColor.query.get(color_id)
            if not color:
                return False, None, 'Color no encontrado'

            color.activo = False
            db.session.commit()

            return True, None, f'Color "{color.nombre_color}" eliminado'

        except Exception as e:
            db.session.rollback()
            return False, None, str(e)

    @staticmethod
    def agregar_flor_a_color(color_id, data):
        """
        Agrega una flor a un color

        Args:
            color_id: ID del color
            data: dict con flor_id, es_predeterminada

        Returns:
            tuple: (success, color_flor/error, message)
        """
        try:
            color = ProductoColor.query.get(color_id)
            if not color:
                return False, None, 'Color no encontrado'

            flor_id = data.get('flor_id')
            flor = Flor.query.get(flor_id)
            if not flor:
                return False, None, 'Flor no encontrada'

            # Verificar si ya existe
            color_flor_existente = ProductoColorFlor.query.filter_by(
                producto_color_id=color_id,
                flor_id=flor_id,
                activo=True
            ).first()

            if color_flor_existente:
                return False, None, 'Esta flor ya está asociada a este color'

            # Si es predeterminada, quitar predeterminada de las demás
            es_predeterminada = data.get('es_predeterminada', False)
            if es_predeterminada:
                ProductoColorFlor.query.filter_by(
                    producto_color_id=color_id
                ).update({'es_predeterminada': False})

            # Crear asociación
            color_flor = ProductoColorFlor(
                producto_color_id=color_id,
                flor_id=flor_id,
                es_predeterminada=es_predeterminada
            )

            db.session.add(color_flor)
            db.session.commit()

            return True, color_flor.to_dict(), f'Flor {flor.nombre} agregada al color {color.nombre_color}'

        except Exception as e:
            db.session.rollback()
            return False, None, str(e)

    @staticmethod
    def eliminar_flor_de_color(color_flor_id):
        """
        Elimina (desactiva) una flor de un color

        Args:
            color_flor_id: ID de la asociación color-flor

        Returns:
            tuple: (success, message, message)
        """
        try:
            color_flor = ProductoColorFlor.query.get(color_flor_id)
            if not color_flor:
                return False, None, 'Asociación no encontrada'

            color_flor.activo = False
            db.session.commit()

            return True, None, 'Flor eliminada del color'

        except Exception as e:
            db.session.rollback()
            return False, None, str(e)

    @staticmethod
    def marcar_flor_predeterminada(color_flor_id):
        """
        Marca una flor como predeterminada para su color

        Args:
            color_flor_id: ID de la asociación color-flor

        Returns:
            tuple: (success, color_flor/error, message)
        """
        try:
            color_flor = ProductoColorFlor.query.get(color_flor_id)
            if not color_flor:
                return False, None, 'Asociación no encontrada'

            # Quitar predeterminada de las demás del mismo color
            ProductoColorFlor.query.filter_by(
                producto_color_id=color_flor.producto_color_id
            ).update({'es_predeterminada': False})

            # Marcar esta como predeterminada
            color_flor.es_predeterminada = True
            db.session.commit()

            return True, color_flor.to_dict(), 'Flor marcada como predeterminada'

        except Exception as e:
            db.session.rollback()
            return False, None, str(e)

    @staticmethod
    def obtener_configuracion_completa(producto_id):
        """
        Obtiene la configuración completa de colores y flores de un producto

        Args:
            producto_id: ID del producto

        Returns:
            tuple: (success, data/error, message)
        """
        try:
            producto = Producto.query.get(producto_id)
            if not producto:
                return False, None, 'Producto no encontrado'

            colores = ProductoColor.query.filter_by(
                producto_id=producto_id,
                activo=True
            ).order_by(ProductoColor.orden).all()

            configuracion = {
                'producto_id': producto_id,
                'producto_nombre': producto.nombre,
                'precio_venta': float(producto.precio) if producto.precio else 0,
                'colores': []
            }

            for color in colores:
                flores_activas = [cf for cf in color.flores if cf.activo]

                configuracion['colores'].append({
                    'id': color.id,
                    'nombre_color': color.nombre_color,
                    'cantidad_flores_sugerida': color.cantidad_flores_sugerida,
                    'orden': color.orden,
                    'notas': color.notas,
                    'flores': [
                        {
                            'id': cf.id,
                            'flor_id': cf.flor_id,
                            'flor_nombre': cf.flor.nombre if cf.flor else None,
                            'flor_color': cf.flor.color if cf.flor else None,
                            'es_predeterminada': cf.es_predeterminada,
                            'costo_unitario': float(cf.flor.costo_unitario) if cf.flor and cf.flor.costo_unitario else 0
                        }
                        for cf in flores_activas
                    ]
                })

            return True, configuracion, 'Configuración obtenida'

        except Exception as e:
            return False, None, str(e)

    @staticmethod
    def guardar_receta_completa(producto_id, data):
        """
        Guarda la configuración completa del recetario desde el simulador.
        Actualiza colores, flores asociadas, flores predeterminadas y precio de venta.

        Args:
            producto_id: ID del producto
            data: dict con colores[] y precio_venta

        Returns:
            tuple: (success, result/error, message)
        """
        try:
            # Validar producto existe
            producto = Producto.query.get(producto_id)
            if not producto:
                return False, None, 'Producto no encontrado'

            colores_nuevos = data.get('colores', [])
            precio_venta = data.get('precio_venta')

            # Validar que haya al menos un color
            if not colores_nuevos or len(colores_nuevos) == 0:
                return False, None, 'Debe haber al menos un color'

            # ===== PASO 1: Actualizar precio de venta =====
            if precio_venta is not None:
                producto.precio = precio_venta

            # ===== PASO 2: Obtener colores existentes =====
            colores_existentes = ProductoColor.query.filter_by(
                producto_id=producto_id,
                activo=True
            ).all()

            # Mapear por ID para fácil acceso
            colores_existentes_map = {str(c.id): c for c in colores_existentes}

            # IDs de colores en la nueva configuración
            colores_nuevos_ids = set()

            # ===== PASO 3: Crear/actualizar colores =====
            orden = 0
            for color_data in colores_nuevos:
                color_id = str(color_data.get('id', ''))
                es_nuevo = color_id.startswith('nuevo-')

                if es_nuevo:
                    # Crear nuevo color
                    nuevo_color = ProductoColor(
                        producto_id=producto_id,
                        nombre_color=color_data.get('nombre_color', 'Sin nombre'),
                        cantidad_flores_sugerida=color_data.get('cantidad_flores_sugerida', 12),
                        orden=orden
                    )
                    db.session.add(nuevo_color)
                    db.session.flush()  # Para obtener el ID

                    color_obj = nuevo_color
                    color_id_real = nuevo_color.id
                else:
                    # Actualizar color existente
                    color_obj = colores_existentes_map.get(color_id)
                    if color_obj:
                        color_obj.nombre_color = color_data.get('nombre_color', color_obj.nombre_color)
                        color_obj.cantidad_flores_sugerida = color_data.get('cantidad_flores_sugerida', color_obj.cantidad_flores_sugerida)
                        color_obj.orden = orden
                        color_id_real = color_obj.id
                    else:
                        continue  # Color no encontrado, saltar

                colores_nuevos_ids.add(str(color_id_real))

                # ===== PASO 4: Actualizar flores del color =====
                flores_data = color_data.get('flores', [])

                # Desactivar todas las flores actuales del color
                ProductoColorFlor.query.filter_by(
                    producto_color_id=color_id_real
                ).update({'activo': False, 'es_predeterminada': False})

                # Agregar/reactivar flores
                for flor_data in flores_data:
                    flor_id = flor_data.get('flor_id')
                    es_predeterminada = flor_data.get('es_predeterminada', False)

                    # Buscar si ya existe esta asociación
                    color_flor_existente = ProductoColorFlor.query.filter_by(
                        producto_color_id=color_id_real,
                        flor_id=flor_id
                    ).first()

                    if color_flor_existente:
                        # Reactivar
                        color_flor_existente.activo = True
                        color_flor_existente.es_predeterminada = es_predeterminada
                    else:
                        # Crear nueva
                        nueva_color_flor = ProductoColorFlor(
                            producto_color_id=color_id_real,
                            flor_id=flor_id,
                            es_predeterminada=es_predeterminada
                        )
                        db.session.add(nueva_color_flor)

                orden += 1

            # ===== PASO 5: Desactivar colores que ya no están =====
            for color_id_existente, color_obj in colores_existentes_map.items():
                if str(color_obj.id) not in colores_nuevos_ids:
                    color_obj.activo = False

            # ===== COMMIT =====
            db.session.commit()

            result = {
                'producto_id': producto_id,
                'colores_actualizados': len(colores_nuevos),
                'precio_venta': float(producto.precio) if producto.precio else 0
            }

            return True, result, f'Receta de {producto.nombre} guardada exitosamente'

        except Exception as e:
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return False, None, f'Error al guardar: {str(e)}'
