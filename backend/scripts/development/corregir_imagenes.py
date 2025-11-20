#!/usr/bin/env python3
"""
Script para corregir la integración de imágenes de productos
"""

import sqlite3
import json

def corregir_imagenes():
    """
    Corrige la integración de imágenes de productos
    """
    print("🖼️  Corrigiendo integración de imágenes...")
    
    try:
        # Conectar a ambas bases de datos
        conn_shopify = sqlite3.connect('productos_shopify.db')
        conn_sistema = sqlite3.connect('las_lira.db')
        
        cursor_shopify = conn_shopify.cursor()
        cursor_sistema = conn_sistema.cursor()
        
        # Obtener productos de Shopify con imágenes
        cursor_shopify.execute('''
            SELECT p.handle, p.titulo, i.url, i.posicion, i.alt_text
            FROM productos_shopify p
            JOIN imagenes_productos i ON p.handle = i.producto_handle
            ORDER BY p.handle, i.posicion
        ''')
        
        imagenes_shopify = cursor_shopify.fetchall()
        print(f"📸 Imágenes encontradas en Shopify: {len(imagenes_shopify)}")
        
        # Limpiar imágenes existentes
        cursor_sistema.execute('DELETE FROM imagenes_productos')
        
        # Integrar imágenes
        imagenes_integradas = 0
        
        for handle, titulo, url, posicion, alt_text in imagenes_shopify:
            # Buscar el producto en el sistema por nombre
            cursor_sistema.execute('SELECT id FROM productos WHERE nombre = ?', (titulo,))
            producto_id = cursor_sistema.fetchone()
            
            if producto_id:
                # Insertar imagen
                cursor_sistema.execute('''
                    INSERT INTO imagenes_productos 
                    (producto_id, url, posicion, alt_text, es_principal)
                    VALUES (?, ?, ?, ?, ?)
                ''', (producto_id[0], url, posicion, alt_text, 1 if posicion == 1 else 0))
                imagenes_integradas += 1
            else:
                print(f"⚠️  Producto no encontrado: {titulo}")
        
        conn_sistema.commit()
        
        # Estadísticas finales
        cursor_sistema.execute('SELECT COUNT(*) FROM imagenes_productos')
        total_imagenes = cursor_sistema.fetchone()[0]
        
        print(f"✅ Imágenes integradas: {imagenes_integradas}")
        print(f"📊 Total imágenes en sistema: {total_imagenes}")
        
        conn_shopify.close()
        conn_sistema.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    corregir_imagenes()



