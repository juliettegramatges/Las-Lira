#!/usr/bin/env python3
"""
Script para actualizar las imágenes de productos en la base principal
"""

import sqlite3
import os

def actualizar_imagenes_productos():
    """Actualiza las imágenes de productos en la base principal"""
    try:
        # Obtener rutas dinámicamente
        script_dir = os.path.dirname(os.path.abspath(__file__))
        db_consolidada = os.path.join(script_dir, 'las_lira.db')
        db_principal = os.path.join(script_dir, 'backend', 'instance', 'laslira.db')

        # Conectar a ambas bases de datos
        conn_consolidada = sqlite3.connect(db_consolidada)
        conn_principal = sqlite3.connect(db_principal)
        
        cursor_consolidada = conn_consolidada.cursor()
        cursor_principal = conn_principal.cursor()
        
        print("🔄 Actualizando imágenes de productos...")
        
        # Obtener imágenes de la base consolidada
        cursor_consolidada.execute('''
            SELECT producto_id, url, es_principal
            FROM imagenes_productos 
            ORDER BY producto_id, es_principal DESC, posicion
        ''')
        
        imagenes = cursor_consolidada.fetchall()
        print(f"📸 Encontradas {len(imagenes)} imágenes en la base consolidada")
        
        # Agrupar por producto y obtener la imagen principal
        imagenes_por_producto = {}
        for producto_id, url, es_principal in imagenes:
            if producto_id not in imagenes_por_producto:
                imagenes_por_producto[producto_id] = {'principal': None, 'cualquiera': None}
            
            if es_principal:
                imagenes_por_producto[producto_id]['principal'] = url
            elif imagenes_por_producto[producto_id]['cualquiera'] is None:
                imagenes_por_producto[producto_id]['cualquiera'] = url
        
        # Actualizar productos en la base principal
        actualizados = 0
        for producto_id, imagenes_info in imagenes_por_producto.items():
            # Usar imagen principal si existe, sino cualquier imagen
            imagen_url = imagenes_info['principal'] or imagenes_info['cualquiera']
            
            if imagen_url:
                cursor_principal.execute('''
                    UPDATE productos SET 
                        imagen_principal = ?, imagen_url = ?
                    WHERE id = ?
                ''', (imagen_url, imagen_url, producto_id))
                
                if cursor_principal.rowcount > 0:
                    actualizados += 1
        
        conn_principal.commit()
        conn_consolidada.close()
        conn_principal.close()
        
        print(f"✅ Actualizadas {actualizados} imágenes de productos")
        print("🎉 ¡Actualización de imágenes completada!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn_consolidada' in locals():
            conn_consolidada.close()
        if 'conn_principal' in locals():
            conn_principal.close()

if __name__ == "__main__":
    actualizar_imagenes_productos()



