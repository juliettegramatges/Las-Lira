#!/usr/bin/env python3
"""
Script simple para probar los productos de Shopify
"""

import sqlite3
import json

def probar_productos():
    """
    Prueba la base de datos de productos de Shopify
    """
    print("🛍️  Probando productos de Shopify...")
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect('las_lira.db')
        cursor = conn.cursor()
        
        # Verificar si existen las tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='productos'")
        if not cursor.fetchone():
            print("❌ Tabla 'productos' no existe")
            return
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='imagenes_productos'")
        if not cursor.fetchone():
            print("❌ Tabla 'imagenes_productos' no existe")
            return
        
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
        
        print(f"📦 Productos encontrados: {len(productos)}")
        
        for producto in productos:
            id_prod, nombre, descripcion, precio, categoria, tipo, imagen_url, sku, peso, tags, metafields, activo = producto
            
            print(f"\n🌸 {nombre}")
            print(f"   💰 Precio: ${precio:,.0f}")
            print(f"   📂 Categoría: {categoria}")
            print(f"   🏷️  Tipo: {tipo}")
            print(f"   🖼️  Imagen: {imagen_url}")
            
            # Obtener imágenes
            cursor.execute('''
                SELECT url, posicion, alt_text, es_principal
                FROM imagenes_productos 
                WHERE producto_id = ?
                ORDER BY posicion
            ''', (id_prod,))
            
            imagenes = cursor.fetchall()
            print(f"   📸 Total imágenes: {len(imagenes)}")
            
            for img_url, pos, alt, es_principal in imagenes:
                print(f"      {pos}. {img_url} {'(Principal)' if es_principal else ''}")
        
        # Estadísticas
        cursor.execute('SELECT COUNT(*) FROM productos WHERE activo = 1')
        total_productos = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM imagenes_productos')
        total_imagenes = cursor.fetchone()[0]
        
        print(f"\n📊 ESTADÍSTICAS:")
        print(f"   📦 Total productos activos: {total_productos}")
        print(f"   🖼️  Total imágenes: {total_imagenes}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    probar_productos()



