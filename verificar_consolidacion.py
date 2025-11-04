#!/usr/bin/env python3
"""
Script para verificar el resultado de la consolidación
"""

import sqlite3
import json
import os

def verificar_consolidacion():
    """
    Verifica el resultado de la consolidación
    """
    print("🔍 Verificando consolidación de catálogos...")

    try:
        # Obtener ruta dinámica de la base de datos
        script_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(script_dir, 'las_lira.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Estadísticas generales
        cursor.execute('SELECT COUNT(*) FROM productos WHERE activo = 1')
        total_productos = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM mapeo_productos')
        total_mapeos = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM imagenes_productos')
        total_imagenes = cursor.fetchone()[0]
        
        print(f"📊 ESTADÍSTICAS GENERALES:")
        print(f"   📦 Total productos activos: {total_productos}")
        print(f"   🗺️  Total mapeos Shopify: {total_mapeos}")
        print(f"   🖼️  Total imágenes: {total_imagenes}")
        
        # 2. Productos con mapeo Shopify
        cursor.execute('''
            SELECT p.nombre, p.sku, p.precio, m.shopify_handle, m.metodo_asociacion, m.similitud
            FROM productos p
            JOIN mapeo_productos m ON p.id = m.producto_id
            WHERE p.activo = 1
            ORDER BY p.nombre
        ''')
        
        productos_con_shopify = cursor.fetchall()
        
        print(f"\n🛍️  PRODUCTOS CON MAPEO SHOPIFY ({len(productos_con_shopify)}):")
        for producto in productos_con_shopify[:10]:  # Mostrar solo los primeros 10
            nombre, sku, precio, handle, metodo, similitud = producto
            print(f"   - {nombre} (SKU: {sku}) - ${precio:,.0f} - {metodo} ({similitud:.2f})")
        
        if len(productos_con_shopify) > 10:
            print(f"   ... y {len(productos_con_shopify) - 10} más")
        
        # 3. Productos sin mapeo Shopify
        cursor.execute('''
            SELECT p.nombre, p.sku, p.precio
            FROM productos p
            LEFT JOIN mapeo_productos m ON p.id = m.producto_id
            WHERE p.activo = 1 AND m.id IS NULL
            ORDER BY p.nombre
        ''')
        
        productos_sin_shopify = cursor.fetchall()
        
        print(f"\n⚠️  PRODUCTOS SIN MAPEO SHOPIFY ({len(productos_sin_shopify)}):")
        for producto in productos_sin_shopify[:10]:  # Mostrar solo los primeros 10
            nombre, sku, precio = producto
            print(f"   - {nombre} (SKU: {sku}) - ${precio:,.0f}")
        
        if len(productos_sin_shopify) > 10:
            print(f"   ... y {len(productos_sin_shopify) - 10} más")
        
        # 4. Distribución por categorías
        cursor.execute('''
            SELECT categoria, COUNT(*) as total
            FROM productos 
            WHERE activo = 1 AND categoria IS NOT NULL AND categoria != ''
            GROUP BY categoria
            ORDER BY total DESC
        ''')
        
        categorias = cursor.fetchall()
        
        print(f"\n📂 DISTRIBUCIÓN POR CATEGORÍAS:")
        for categoria, total in categorias[:10]:  # Mostrar solo las top 10
            print(f"   - {categoria}: {total}")
        
        # 5. Distribución por tipos
        cursor.execute('''
            SELECT tipo, COUNT(*) as total
            FROM productos 
            WHERE activo = 1 AND tipo IS NOT NULL AND tipo != ''
            GROUP BY tipo
            ORDER BY total DESC
        ''')
        
        tipos = cursor.fetchall()
        
        print(f"\n🏷️  DISTRIBUCIÓN POR TIPOS:")
        for tipo, total in tipos[:10]:  # Mostrar solo las top 10
            print(f"   - {tipo}: {total}")
        
        # 6. Rango de precios
        cursor.execute('''
            SELECT MIN(precio), MAX(precio), AVG(precio)
            FROM productos 
            WHERE activo = 1 AND precio > 0
        ''')
        
        min_precio, max_precio, avg_precio = cursor.fetchone()
        
        print(f"\n💰 RANGO DE PRECIOS:")
        print(f"   - Mínimo: ${min_precio:,.0f}")
        print(f"   - Máximo: ${max_precio:,.0f}")
        print(f"   - Promedio: ${avg_precio:,.0f}")
        
        # 7. Productos con imágenes
        cursor.execute('''
            SELECT COUNT(DISTINCT p.id)
            FROM productos p
            JOIN imagenes_productos i ON p.id = i.producto_id
            WHERE p.activo = 1
        ''')
        
        productos_con_imagenes = cursor.fetchone()[0]
        
        print(f"\n🖼️  PRODUCTOS CON IMÁGENES: {productos_con_imagenes}/{total_productos} ({productos_con_imagenes/total_productos*100:.1f}%)")
        
        conn.close()
        
        print(f"\n✅ ¡Verificación completada!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verificar_consolidacion()



