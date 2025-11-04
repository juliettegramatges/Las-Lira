#!/usr/bin/env python3
"""
Script para sincronizar productos de la base de datos consolidada a la base de datos principal
"""

import sqlite3
import os

def sincronizar_productos():
    """Sincroniza productos de las_lira.db a laslira.db"""
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
        
        print("🔄 Sincronizando productos...")
        
        # Obtener productos de la base consolidada
        cursor_consolidada.execute('''
            SELECT id, nombre, descripcion, precio, categoria, tipo, 
                   imagen_principal, sku, peso, tags, metafields, activo
            FROM productos 
            WHERE activo = 1
        ''')
        
        productos = cursor_consolidada.fetchall()
        print(f"📦 Encontrados {len(productos)} productos en la base consolidada")
        
        # Actualizar productos en la base principal
        actualizados = 0
        for producto in productos:
            id_prod, nombre, descripcion, precio, categoria, tipo, imagen_principal, sku, peso, tags, metafields, activo = producto
            
            # Usar tipo como tipo_arreglo si no existe
            tipo_arreglo = tipo or 'Arreglo'
            # Usar precio como precio_venta
            precio_venta = precio or 0
            
            # Verificar si el producto existe en la base principal
            cursor_principal.execute('SELECT id FROM productos WHERE id = ?', (id_prod,))
            existe = cursor_principal.fetchone()
            
            if existe:
                # Actualizar producto existente
                cursor_principal.execute('''
                    UPDATE productos SET 
                        nombre = ?, descripcion = ?, tipo_arreglo = ?, precio_venta = ?, precio = ?, categoria = ?, 
                        tipo = ?, imagen_principal = ?, sku = ?, peso = ?, 
                        tags = ?, metafields = ?, activo = ?
                    WHERE id = ?
                ''', (nombre, descripcion, tipo_arreglo, precio_venta, precio, categoria, tipo, imagen_principal, 
                      sku, peso, tags, metafields, activo, id_prod))
                actualizados += 1
            else:
                # Insertar nuevo producto
                cursor_principal.execute('''
                    INSERT INTO productos 
                    (id, nombre, descripcion, tipo_arreglo, precio_venta, precio, categoria, tipo, 
                     imagen_principal, sku, peso, tags, metafields, activo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (id_prod, nombre, descripcion, tipo_arreglo, precio_venta, precio, categoria, tipo, 
                      imagen_principal, sku, peso, tags, metafields, activo))
                actualizados += 1
        
        conn_principal.commit()
        conn_consolidada.close()
        conn_principal.close()
        
        print(f"✅ Sincronizados {actualizados} productos")
        print("🎉 ¡Sincronización completada!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn_consolidada' in locals():
            conn_consolidada.close()
        if 'conn_principal' in locals():
            conn_principal.close()

if __name__ == "__main__":
    sincronizar_productos()
