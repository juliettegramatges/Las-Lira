from flask import Blueprint, jsonify, request
from config.database_paths import get_legacy_db_path, get_main_db_path
import sqlite3
import json

bp = Blueprint('productos', __name__)

@bp.route('/', methods=['GET'])
def listar_productos():
    """Lista todos los productos con sus imágenes (de ambas bases de datos)"""
    try:
        productos_con_imagenes = []

        # 1. Obtener productos de Shopify (base legacy)
        conn_shopify = sqlite3.connect(get_legacy_db_path())
        cursor_shopify = conn_shopify.cursor()

        cursor_shopify.execute('''
            SELECT id, nombre, descripcion, precio, categoria, tipo,
                   imagen_url, sku, peso, tags, metafields, activo
            FROM productos
            WHERE activo = 1
            ORDER BY nombre
        ''')

        for producto in cursor_shopify.fetchall():
            id_prod, nombre, descripcion, precio, categoria, tipo, imagen_url, sku, peso, tags, metafields, activo = producto

            # Obtener todas las imágenes del producto
            cursor_shopify.execute('''
                SELECT url, posicion, alt_text, es_principal
                FROM imagenes_productos
                WHERE producto_id = ?
                ORDER BY posicion
            ''', (id_prod,))

            imagenes = []
            for img_url, pos, alt, es_principal in cursor_shopify.fetchall():
                imagenes.append({
                    'url': img_url,
                    'posicion': pos,
                    'alt_text': alt,
                    'es_principal': bool(es_principal)
                })

            metafields_dict = json.loads(metafields) if metafields else {}

            productos_con_imagenes.append({
                'id': id_prod,
                'nombre': nombre,
                'descripcion': descripcion,
                'precio': precio,
                'categoria': categoria,
                'tipo': tipo,
                'imagen_principal': imagen_url,
                'imagenes': imagenes,
                'sku': sku,
                'peso': peso,
                'tags': tags.split(',') if tags else [],
                'metafields': metafields_dict,
                'activo': bool(activo),
                'origen': 'shopify'
            })

        conn_shopify.close()

        # 2. Obtener productos internos (laslira.db) que tienen recetas
        conn_internal = sqlite3.connect(get_main_db_path())
        cursor_internal = conn_internal.cursor()

        cursor_internal.execute('''
            SELECT id, nombre, descripcion, precio_venta, tipo_arreglo, tamano, activo
            FROM productos
            WHERE activo = 1
            ORDER BY nombre
        ''')

        for producto in cursor_internal.fetchall():
            id_prod, nombre, descripcion, precio_venta, tipo_arreglo, tamano, activo = producto

            productos_con_imagenes.append({
                'id': id_prod,  # Este es un string tipo "PR001"
                'nombre': nombre + ' 🌸',  # Agregar emoji para distinguir productos internos
                'descripcion': descripcion or '',
                'precio': precio_venta,
                'precio_venta': precio_venta,
                'categoria': 'Productos Las Lira',
                'tipo': tipo_arreglo or 'Arreglo Floral',
                'tamano': tamano or '',
                'imagen_principal': '',
                'imagenes': [],
                'sku': id_prod,
                'peso': 0,
                'tags': ['Producto Interno', 'Con Receta'],
                'metafields': {},
                'activo': bool(activo),
                'origen': 'interno'
            })

        conn_internal.close()

        # Ordenar todos los productos por nombre
        productos_con_imagenes.sort(key=lambda x: x['nombre'])

        return jsonify({
            'success': True,
            'productos': productos_con_imagenes,
            'total': len(productos_con_imagenes)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/', methods=['POST'])
def crear_producto():
    """Crea un nuevo producto"""
    try:
        data = request.json

        # Validar campos requeridos
        if not data.get('nombre'):
            return jsonify({'success': False, 'error': 'Campo requerido: nombre'}), 400

        conn = sqlite3.connect(get_legacy_db_path())
        cursor = conn.cursor()

        # Preparar campos
        nombre = data['nombre']
        descripcion = data.get('descripcion', '')
        precio = data.get('precio', 0)
        categoria = data.get('categoria', '')
        tipo = data.get('tipo', '')
        imagen_url = data.get('imagen_url')
        sku = data.get('sku', '')
        peso = data.get('peso', 0)
        tags = ','.join(data.get('tags', [])) if isinstance(data.get('tags'), list) else data.get('tags', '')
        metafields = json.dumps(data.get('metafields', {}))

        # Insertar producto
        cursor.execute('''
            INSERT INTO productos
            (nombre, descripcion, precio, categoria, tipo, imagen_url, sku, peso, tags, metafields, activo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        ''', (nombre, descripcion, precio, categoria, tipo, imagen_url, sku, peso, tags, metafields))

        producto_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'data': {
                'id': producto_id,
                'nombre': nombre,
                'descripcion': descripcion,
                'precio': precio,
                'categoria': categoria,
                'tipo': tipo,
                'imagen_principal': imagen_url,
                'sku': sku,
                'peso': peso,
                'tags': tags.split(',') if tags else [],
                'activo': True
            },
            'message': f'Producto "{nombre}" creado exitosamente'
        }), 201

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<int:producto_id>', methods=['GET'])
def obtener_producto(producto_id):
    """Obtiene un producto específico con sus imágenes"""
    try:
        conn = sqlite3.connect(get_legacy_db_path())
        cursor = conn.cursor()
        
        # Obtener producto
        cursor.execute('''
            SELECT id, nombre, descripcion, precio, categoria, tipo, 
                   imagen_url, sku, peso, tags, metafields, activo
            FROM productos 
            WHERE id = ? AND activo = 1
        ''', (producto_id,))
        
        producto = cursor.fetchone()
        
        if not producto:
            return jsonify({
                'success': False,
                'error': 'Producto no encontrado'
            }), 404
        
        id_prod, nombre, descripcion, precio, categoria, tipo, imagen_url, sku, peso, tags, metafields, activo = producto
        
        # Obtener imágenes
        cursor.execute('''
            SELECT url, posicion, alt_text, es_principal
            FROM imagenes_productos 
            WHERE producto_id = ?
            ORDER BY posicion
        ''', (id_prod,))
        
        imagenes = []
        for img_url, pos, alt, es_principal in cursor.fetchall():
            imagenes.append({
                'url': img_url,
                'posicion': pos,
                'alt_text': alt,
                'es_principal': bool(es_principal)
            })
        
        metafields_dict = json.loads(metafields) if metafields else {}
        
        conn.close()
        
        return jsonify({
            'success': True,
            'producto': {
                'id': id_prod,
                'nombre': nombre,
                'descripcion': descripcion,
                'precio': precio,
                'categoria': categoria,
                'tipo': tipo,
                'imagen_principal': imagen_url,
                'imagenes': imagenes,
                'sku': sku,
                'peso': peso,
                'tags': tags.split(',') if tags else [],
                'metafields': metafields_dict,
                'activo': bool(activo)
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/<int:producto_id>', methods=['PUT'])
def actualizar_producto(producto_id):
    """Actualiza un producto existente"""
    try:
        data = request.json

        conn = sqlite3.connect(get_legacy_db_path())
        cursor = conn.cursor()

        # Verificar que el producto existe
        cursor.execute('SELECT id, nombre FROM productos WHERE id = ?', (producto_id,))
        producto = cursor.fetchone()

        if not producto:
            conn.close()
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404

        # Construir UPDATE dinámicamente según los campos enviados
        campos_a_actualizar = []
        valores = []

        if 'nombre' in data:
            campos_a_actualizar.append('nombre = ?')
            valores.append(data['nombre'])
        if 'descripcion' in data:
            campos_a_actualizar.append('descripcion = ?')
            valores.append(data['descripcion'])
        if 'precio' in data:
            campos_a_actualizar.append('precio = ?')
            valores.append(data['precio'])
        if 'categoria' in data:
            campos_a_actualizar.append('categoria = ?')
            valores.append(data['categoria'])
        if 'tipo' in data:
            campos_a_actualizar.append('tipo = ?')
            valores.append(data['tipo'])
        if 'imagen_url' in data:
            campos_a_actualizar.append('imagen_url = ?')
            valores.append(data['imagen_url'])
        if 'sku' in data:
            campos_a_actualizar.append('sku = ?')
            valores.append(data['sku'])
        if 'peso' in data:
            campos_a_actualizar.append('peso = ?')
            valores.append(data['peso'])
        if 'tags' in data:
            tags = ','.join(data['tags']) if isinstance(data['tags'], list) else data['tags']
            campos_a_actualizar.append('tags = ?')
            valores.append(tags)
        if 'metafields' in data:
            campos_a_actualizar.append('metafields = ?')
            valores.append(json.dumps(data['metafields']))

        if not campos_a_actualizar:
            conn.close()
            return jsonify({'success': False, 'error': 'No hay campos para actualizar'}), 400

        # Agregar ID al final de valores
        valores.append(producto_id)

        # Ejecutar UPDATE
        query = f"UPDATE productos SET {', '.join(campos_a_actualizar)} WHERE id = ?"
        cursor.execute(query, valores)
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': f'Producto actualizado exitosamente'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<int:producto_id>', methods=['DELETE'])
def eliminar_producto(producto_id):
    """Elimina un producto (soft delete - marca como inactivo)"""
    try:
        conn = sqlite3.connect(get_legacy_db_path())
        cursor = conn.cursor()

        # Verificar que el producto existe
        cursor.execute('SELECT id, nombre FROM productos WHERE id = ? AND activo = 1', (producto_id,))
        producto = cursor.fetchone()

        if not producto:
            conn.close()
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404

        # Soft delete - marcar como inactivo
        cursor.execute('UPDATE productos SET activo = 0 WHERE id = ?', (producto_id,))
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': f'Producto "{producto[1]}" eliminado exitosamente'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/categoria/<categoria>', methods=['GET'])
def productos_por_categoria(categoria):
    """Obtiene productos filtrados por categoría"""
    try:
        conn = sqlite3.connect(get_legacy_db_path())
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, nombre, descripcion, precio, categoria, tipo, 
                   imagen_url, sku, peso, tags, metafields, activo
            FROM productos 
            WHERE activo = 1 AND categoria LIKE ?
            ORDER BY nombre
        ''', (f'%{categoria}%',))
        
        productos = cursor.fetchall()
        productos_con_imagenes = []
        
        for producto in productos:
            id_prod, nombre, descripcion, precio, categoria, tipo, imagen_url, sku, peso, tags, metafields, activo = producto
            
            # Obtener imagen principal
            cursor.execute('''
                SELECT url FROM imagenes_productos 
                WHERE producto_id = ? AND es_principal = 1
                LIMIT 1
            ''', (id_prod,))
            
            imagen_principal = cursor.fetchone()
            if imagen_principal:
                imagen_principal = imagen_principal[0]
            
            metafields_dict = json.loads(metafields) if metafields else {}
            
            productos_con_imagenes.append({
                'id': id_prod,
                'nombre': nombre,
                'descripcion': descripcion,
                'precio': precio,
                'categoria': categoria,
                'tipo': tipo,
                'imagen_principal': imagen_principal,
                'sku': sku,
                'peso': peso,
                'tags': tags.split(',') if tags else [],
                'metafields': metafields_dict,
                'activo': bool(activo)
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'productos': productos_con_imagenes,
            'total': len(productos_con_imagenes),
            'categoria': categoria
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/<producto_id>/receta', methods=['GET'])
def obtener_receta_producto(producto_id):
    """Obtiene la receta (insumos) de un producto.
    Lee desde instance/laslira.db en la tabla recetas_productos y enriquece con datos
    de flores y contenedores (costo, stock, foto, etc.).
    Acepta tanto IDs numéricos como strings (PR001, etc.)
    """
    try:
        # Preferir la base usada por la app
        conn = sqlite3.connect(get_main_db_path())
        cursor = conn.cursor()

        cursor.execute(
            '''
            SELECT insumo_tipo, insumo_id, cantidad, unidad, es_opcional
            FROM recetas_productos
            WHERE producto_id = ?
            ORDER BY insumo_tipo, insumo_id
            ''',
            (str(producto_id),)  # Convertir a string para soportar ambos tipos
        )

        receta = []
        costo_total_insumos = 0.0
        resultados = cursor.fetchall()
        for insumo_tipo, insumo_id, cantidad, unidad, es_opcional in resultados:
            item = {
                'id': insumo_id,
                'tipo': insumo_tipo,
                'cantidad': int(cantidad or 0),
                'unidad': unidad,
                'es_opcional': bool(es_opcional),
            }
            if insumo_tipo == 'Flor':
                cursor.execute('SELECT id, tipo, color, costo_unitario, cantidad_stock, foto_url FROM flores WHERE id = ?', (insumo_id,))
                row = cursor.fetchone()
                if row:
                    fid, tipo, color, costo_unitario, stock, foto = row
                    # Crear nombre descriptivo: "Tipo - Color"
                    nombre_descriptivo = f"{tipo} {color}" if color else tipo
                    item.update({
                        'nombre': nombre_descriptivo,
                        'insumo_nombre': nombre_descriptivo,
                        'tipo_insumo': tipo,
                        'color': color,
                        'costo_unitario': float(costo_unitario or 0),
                        'stock_disponible': int(stock or 0),
                        'foto_url': foto,
                        'unidad_stock': 'Tallos',
                    })
            elif insumo_tipo == 'Contenedor':
                cursor.execute('SELECT id, tipo, material, forma, tamano, color, costo, stock, foto_url FROM contenedores WHERE id = ?', (insumo_id,))
                row = cursor.fetchone()
                if row:
                    cid, tipo, material, forma, tamano, color, costo, stock, foto = row
                    # Crear nombre descriptivo: "Tipo Material Tamaño"
                    nombre_descriptivo = f"{tipo} {material} {tamano}".strip()
                    item.update({
                        'nombre': nombre_descriptivo,
                        'insumo_nombre': nombre_descriptivo,
                        'tipo_insumo': tipo,
                        'material': material,
                        'forma': forma,
                        'tamano': tamano,
                        'color': color,
                        'costo_unitario': float(costo or 0),
                        'stock_disponible': int(stock or 0),
                        'foto_url': foto,
                        'unidad_stock': 'Unidad',
                    })
            # Derivados
            item['costo_total'] = round((item.get('costo_unitario') or 0) * (item['cantidad'] or 0), 2)
            item['disponible'] = (item.get('stock_disponible', 0) or 0) >= (item['cantidad'] or 0)
            costo_total_insumos += item['costo_total']
            receta.append(item)

        # Precio de venta de referencia (best-effort)
        # Primero intentar en laslira.db (productos internos)
        try:
            cursor.execute('SELECT precio_venta FROM productos WHERE id = ?', (str(producto_id),))
            rowp = cursor.fetchone()
            precio_venta = float(rowp[0]) if rowp and rowp[0] is not None else None
        except Exception:
            precio_venta = None

        conn.close()

        # Si no se encontró en laslira.db, intentar en productos_shopify.db
        if precio_venta is None:
            try:
                conn2 = sqlite3.connect(get_legacy_db_path())
                c2 = conn2.cursor()
                c2.execute('SELECT precio FROM productos WHERE id = ?', (producto_id,))
                rowp = c2.fetchone()
                precio_venta = float(rowp[0]) if rowp and rowp[0] is not None else None
                conn2.close()
            except Exception:
                precio_venta = None

        ganancia = (precio_venta or 0) - costo_total_insumos
        margen = (ganancia / precio_venta * 100) if precio_venta and precio_venta > 0 else 0

        return jsonify({
            'success': True,
            'receta': receta,
            'producto_id': producto_id,
            'total': len(receta),
            'costo_total_insumos': round(costo_total_insumos, 2),
            'precio_venta': precio_venta,
            'ganancia': round(ganancia, 2),
            'margen_porcentaje': round(margen, 2)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<int:producto_id>/receta', methods=['POST'])
def agregar_insumo_receta(producto_id):
    """Agrega un insumo a la receta del producto"""
    try:
        data = request.json

        # Validar campos requeridos
        if not data.get('insumo_tipo') or not data.get('insumo_id'):
            return jsonify({'success': False, 'error': 'Campos requeridos: insumo_tipo, insumo_id'}), 400

        conn = sqlite3.connect(get_main_db_path())
        cursor = conn.cursor()

        # Insertar insumo en receta
        cursor.execute('''
            INSERT INTO recetas_productos
            (producto_id, insumo_tipo, insumo_id, cantidad, unidad, es_opcional, notas)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            producto_id,
            data['insumo_tipo'],
            data['insumo_id'],
            data.get('cantidad', 1),
            data.get('unidad', 'Unidad' if data['insumo_tipo'] == 'Contenedor' else 'Tallos'),
            data.get('es_opcional', False),
            data.get('notas')
        ))

        receta_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'data': {'id': receta_id},
            'message': 'Insumo agregado a la receta'
        }), 201

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<int:producto_id>/receta', methods=['PUT'])
def actualizar_receta_completa(producto_id):
    """Actualiza la receta completa del producto (reemplaza todos los insumos)"""
    try:
        data = request.json
        insumos = data.get('insumos', [])

        conn = sqlite3.connect(get_main_db_path())
        cursor = conn.cursor()

        # Eliminar receta actual
        cursor.execute('DELETE FROM recetas_productos WHERE producto_id = ?', (producto_id,))

        # Insertar nueva receta
        for insumo in insumos:
            cursor.execute('''
                INSERT INTO recetas_productos
                (producto_id, insumo_tipo, insumo_id, cantidad, unidad, es_opcional, notas)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                producto_id,
                insumo['insumo_tipo'],
                insumo['insumo_id'],
                insumo.get('cantidad', 1),
                insumo.get('unidad', 'Unidad' if insumo['insumo_tipo'] == 'Contenedor' else 'Tallos'),
                insumo.get('es_opcional', False),
                insumo.get('notas')
            ))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': f'Receta actualizada con {len(insumos)} insumos'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<int:producto_id>/receta/<int:receta_id>', methods=['DELETE'])
def eliminar_insumo_receta(producto_id, receta_id):
    """Elimina un insumo específico de la receta"""
    try:
        conn = sqlite3.connect(get_main_db_path())
        cursor = conn.cursor()

        # Verificar que el insumo pertenece al producto
        cursor.execute('''
            SELECT id FROM recetas_productos
            WHERE id = ? AND producto_id = ?
        ''', (receta_id, producto_id))

        if not cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'error': 'Insumo no encontrado en esta receta'}), 404

        # Eliminar insumo
        cursor.execute('DELETE FROM recetas_productos WHERE id = ?', (receta_id,))
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Insumo eliminado de la receta'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500