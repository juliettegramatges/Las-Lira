#!/usr/bin/env python3
"""
Script para probar el endpoint de productos directamente
"""

import sqlite3
import json

def probar_endpoint():
    """
    Simula el endpoint de productos
    """
    print("🔍 Probando endpoint de productos...")
    
    try:
        conn = sqlite3.connect('las_lira.db')
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
        
        print(f"✅ Productos encontrados: {len(productos_con_imagenes)}")
        
        # Mostrar algunos ejemplos
        for i, producto in enumerate(productos_con_imagenes[:3]):
            print(f"\n{i+1}. {producto['nombre']}")
            print(f"   💰 Precio: ${producto['precio']:,.0f}")
            print(f"   📂 Categoría: {producto['categoria']}")
            print(f"   🖼️  Imágenes: {len(producto['imagenes'])}")
            if producto['imagenes']:
                print(f"   🖼️  Principal: {producto['imagenes'][0]['url']}")
        
        return {
            'success': True,
            'productos': productos_con_imagenes,
            'total': len(productos_con_imagenes)
        }
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e)
        }

if __name__ == "__main__":
    resultado = probar_endpoint()
    print(f"\n📊 Resultado: {resultado['success']}")
    if resultado['success']:
        print(f"📦 Total productos: {resultado['total']}")
    else:
        print(f"❌ Error: {resultado['error']}")



