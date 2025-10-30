#!/usr/bin/env python3
"""
Script para verificar el estado actual de los productos
"""

import sqlite3
import json

def verificar_estado():
    """
    Verifica el estado actual de los productos
    """
    print("🔍 Verificando estado de productos...")
    
    try:
        conn = sqlite3.connect('las_lira.db')
        cursor = conn.cursor()
        
        # Obtener todos los productos
        cursor.execute('''
            SELECT id, nombre, descripcion, precio, categoria, tipo, 
                   imagen_url, sku, peso, tags, metafields, activo
            FROM productos 
            WHERE activo = 1
            ORDER BY nombre
        ''')
        
        productos = cursor.fetchall()
        
        print(f"📦 Total productos activos: {len(productos)}")
        
        # Categorizar productos
        productos_con_sku = []
        productos_sin_sku = []
        
        for producto in productos:
            id_prod, nombre, descripcion, precio, categoria, tipo, imagen_url, sku, peso, tags, metafields, activo = producto
            
            if sku and sku.strip():
                productos_con_sku.append(producto)
            else:
                productos_sin_sku.append(producto)
        
        print(f"🛍️  Productos con SKU (Shopify): {len(productos_con_sku)}")
        print(f"📝 Productos sin SKU (existentes): {len(productos_sin_sku)}")
        
        # Mostrar algunos ejemplos
        print(f"\n🛍️  EJEMPLOS DE PRODUCTOS SHOPIFY:")
        for i, producto in enumerate(productos_con_sku[:5]):
            id_prod, nombre, descripcion, precio, categoria, tipo, imagen_url, sku, peso, tags, metafields, activo = producto
            print(f"   {i+1}. {nombre} (SKU: {sku}) - ${precio:,.0f}")
        
        print(f"\n📝 EJEMPLOS DE PRODUCTOS EXISTENTES:")
        for i, producto in enumerate(productos_sin_sku[:5]):
            id_prod, nombre, descripcion, precio, categoria, tipo, imagen_url, sku, peso, tags, metafields, activo = producto
            print(f"   {i+1}. {nombre} - ${precio:,.0f}")
        
        # Verificar imágenes
        cursor.execute('SELECT COUNT(*) FROM imagenes_productos')
        total_imagenes = cursor.fetchone()[0]
        
        print(f"\n🖼️  Total imágenes en sistema: {total_imagenes}")
        
        # Verificar pedidos que usan productos
        cursor.execute('''
            SELECT DISTINCT p.nombre, COUNT(ped.id) as total_pedidos
            FROM productos p
            LEFT JOIN pedidos ped ON ped.producto_id = p.id
            WHERE p.activo = 1
            GROUP BY p.id, p.nombre
            HAVING total_pedidos > 0
            ORDER BY total_pedidos DESC
            LIMIT 10
        ''')
        
        productos_con_pedidos = cursor.fetchall()
        
        if productos_con_pedidos:
            print(f"\n📋 PRODUCTOS CON PEDIDOS ASOCIADOS:")
            for nombre, total in productos_con_pedidos:
                print(f"   - {nombre}: {total} pedidos")
        else:
            print(f"\n⚠️  No se encontraron pedidos asociados a productos")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verificar_estado()



