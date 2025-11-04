#!/usr/bin/env python3
"""
Script para actualizar la tabla productos con los nuevos campos de la estructura consolidada
"""

import sqlite3
import os

def actualizar_tabla_productos():
    """Actualiza la tabla productos con los nuevos campos"""
    try:
        # Obtener ruta dinámica de la base de datos
        script_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(script_dir, 'backend', 'instance', 'laslira.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 Actualizando tabla productos...")
        
        # Verificar qué columnas ya existen
        cursor.execute("PRAGMA table_info(productos)")
        columnas_existentes = [col[1] for col in cursor.fetchall()]
        print(f"Columnas existentes: {columnas_existentes}")
        
        # Agregar nuevas columnas si no existen
        nuevas_columnas = [
            ("imagen_principal", "VARCHAR(500)"),
            ("precio", "NUMERIC(10, 2)"),
            ("categoria", "VARCHAR(100)"),
            ("tipo", "VARCHAR(100)"),
            ("sku", "VARCHAR(100)"),
            ("peso", "NUMERIC(10, 2)"),
            ("tags", "TEXT"),
            ("metafields", "TEXT")
        ]
        
        for columna, tipo in nuevas_columnas:
            if columna not in columnas_existentes:
                try:
                    cursor.execute(f"ALTER TABLE productos ADD COLUMN {columna} {tipo}")
                    print(f"✅ Agregada columna: {columna}")
                except sqlite3.Error as e:
                    print(f"⚠️  Error al agregar {columna}: {e}")
            else:
                print(f"ℹ️  Columna {columna} ya existe")
        
        # Actualizar imagen_principal con datos de la tabla imagenes_productos
        print("\n🔄 Actualizando imagen_principal con datos de imagenes_productos...")
        
        cursor.execute('''
            UPDATE productos 
            SET imagen_principal = (
                SELECT url 
                FROM imagenes_productos 
                WHERE imagenes_productos.producto_id = productos.id 
                AND imagenes_productos.es_principal = 1 
                LIMIT 1
            )
            WHERE imagen_principal IS NULL
        ''')
        
        actualizados = cursor.rowcount
        print(f"✅ Actualizadas {actualizados} imágenes principales")
        
        # Actualizar precio con precio_venta si no existe
        print("\n🔄 Actualizando precio con precio_venta...")
        
        cursor.execute('''
            UPDATE productos 
            SET precio = precio_venta 
            WHERE precio IS NULL AND precio_venta IS NOT NULL
        ''')
        
        actualizados = cursor.rowcount
        print(f"✅ Actualizados {actualizados} precios")
        
        # Actualizar tipo con tipo_arreglo si no existe
        print("\n🔄 Actualizando tipo con tipo_arreglo...")
        
        cursor.execute('''
            UPDATE productos 
            SET tipo = tipo_arreglo 
            WHERE tipo IS NULL AND tipo_arreglo IS NOT NULL
        ''')
        
        actualizados = cursor.rowcount
        print(f"✅ Actualizados {actualizados} tipos")
        
        conn.commit()
        conn.close()
        
        print("\n🎉 ¡Actualización completada!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if conn:
            conn.close()

if __name__ == "__main__":
    actualizar_tabla_productos()
