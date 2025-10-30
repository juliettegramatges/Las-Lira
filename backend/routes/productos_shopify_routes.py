from flask import Blueprint, jsonify, request
import sqlite3
import json

bp = Blueprint('productos_shopify', __name__)

@bp.route('/', methods=['GET'])
def listar_productos():
    """Lista todos los productos con sus imágenes"""
    try:
        conn = sqlite3.connect('/Users/juliettegramatges/Las-Lira/las_lira.db')
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
        conn = sqlite3.connect('/Users/juliettegramatges/Las-Lira/las_lira.db')
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
        conn = sqlite3.connect('/Users/juliettegramatges/Las-Lira/las_lira.db')
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