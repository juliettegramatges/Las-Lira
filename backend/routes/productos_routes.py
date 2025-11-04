from flask import Blueprint, jsonify, request
import sqlite3
import json
import os

bp = Blueprint('productos', __name__)

# Helper para obtener rutas de bases de datos
def get_legacy_db_path():
    """Obtiene la ruta de la base de datos legacy (las_lira.db)"""
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(os.path.dirname(backend_dir), 'las_lira.db')

def get_main_db_path():
    """Obtiene la ruta de la base de datos principal (laslira.db)"""
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(backend_dir, 'instance', 'laslira.db')

@bp.route('/', methods=['GET'])
def listar_productos():
    """Lista todos los productos con sus imágenes"""
    try:
        conn = sqlite3.connect(get_legacy_db_path())
        cursor = conn.cursor()
        
        # Obtener productos
        cursor.execute('''
            SELECT id, nombre, descripcion, precio, categoria, tipo, 
                   imagen_url, sku, peso, tags, metafields, activo
            FROM productos 
            WHERE activo = 1
            ORDER BY nombre
        ''')
        
        productos = cursor.fetchall()
        productos_con_imagenes = []
        
        for producto in productos:
            id_prod, nombre, descripcion, precio, categoria, tipo, imagen_url, sku, peso, tags, metafields, activo = producto
            
            # Obtener todas las imágenes del producto
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
                'activo': bool(activo)
            })
        
        conn.close()
        
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


@bp.route('/<int:producto_id>/receta', methods=['GET'])
def obtener_receta_producto(producto_id):
    """Obtiene la receta (insumos) de un producto.
    Lee desde instance/laslira.db en la tabla recetas_productos y enriquece con datos
    de flores y contenedores (costo, stock, foto, etc.).
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
            (producto_id,)
        )

        receta = []
        costo_total_insumos = 0.0
        for insumo_tipo, insumo_id, cantidad, unidad, es_opcional in cursor.fetchall():
            item = {
                'id': insumo_id,
                'tipo': insumo_tipo,
                'cantidad': int(cantidad or 0),
                'unidad': unidad,
                'es_opcional': bool(es_opcional),
            }
            if insumo_tipo == 'Flor':
                cursor.execute('SELECT id, nombre, tipo, color, costo_unitario, cantidad_disponible, foto_url FROM flores WHERE id = ?', (insumo_id,))
                row = cursor.fetchone()
                if row:
                    fid, nombre, tipo, color, costo_unitario, stock, foto = row
                    item.update({
                        'nombre': nombre or tipo,
                        'color': color,
                        'costo_unitario': float(costo_unitario or 0),
                        'stock_disponible': int(stock or 0),
                        'foto_url': foto,
                        'unidad_stock': 'Tallos',
                    })
            elif insumo_tipo == 'Contenedor':
                cursor.execute('SELECT id, nombre, tipo, material, costo, cantidad_disponible, foto_url FROM contenedores WHERE id = ?', (insumo_id,))
                row = cursor.fetchone()
                if row:
                    cid, nombre, tipo, material, costo, stock, foto = row
                    item.update({
                        'nombre': nombre or tipo,
                        'material': material,
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

        conn.close()

        # Precio de venta de referencia (best-effort)
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