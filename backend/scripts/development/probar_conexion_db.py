#!/usr/bin/env python3
"""
Script para probar la conexión a la base de datos
"""

import sqlite3
import os

def probar_conexion():
    """
    Prueba la conexión a la base de datos
    """
    print("🔍 Probando conexión a la base de datos...")

    # Obtener ruta dinámica de la base de datos
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, 'las_lira.db')
    
    print(f"📁 Ruta de la base de datos: {db_path}")
    print(f"📁 ¿Existe el archivo? {os.path.exists(db_path)}")
    
    if not os.path.exists(db_path):
        print("❌ El archivo de base de datos no existe")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tablas = cursor.fetchall()
        print(f"📋 Tablas encontradas: {[t[0] for t in tablas]}")
        
        # Verificar productos
        cursor.execute("SELECT COUNT(*) FROM productos WHERE activo = 1")
        total_productos = cursor.fetchone()[0]
        print(f"📦 Productos activos: {total_productos}")
        
        # Verificar imágenes
        cursor.execute("SELECT COUNT(*) FROM imagenes_productos")
        total_imagenes = cursor.fetchone()[0]
        print(f"🖼️  Total imágenes: {total_imagenes}")
        
        # Probar query específica
        cursor.execute('''
            SELECT id, nombre, precio, categoria
            FROM productos 
            WHERE activo = 1
            LIMIT 3
        ''')
        
        productos = cursor.fetchall()
        print(f"\n📋 Primeros 3 productos:")
        for producto in productos:
            print(f"   - {producto[1]} (ID: {producto[0]}) - ${producto[2]:,.0f}")
        
        conn.close()
        print("✅ Conexión exitosa")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    probar_conexion()



