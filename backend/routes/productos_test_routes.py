from flask import Blueprint, jsonify
import sqlite3
import json

bp = Blueprint('productos_test', __name__)

@bp.route('/productos-test', methods=['GET'])
def listar_productos_test():
    """Endpoint de prueba para productos"""
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
            LIMIT 5
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
