#!/usr/bin/env python3
"""
Script para migrar proveedores: agregar columna empresa y tablas de relación muchos-a-muchos
"""

import sys
import os

# Agregar el directorio backend al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
import sqlite3

def migrar_proveedores():
    """Agrega columna empresa y crea tablas de relación"""
    with app.app_context():
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        
        if not os.path.exists(db_path):
            print(f"❌ Base de datos no encontrada en: {db_path}")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Verificar si la columna empresa ya existe
            cursor.execute("PRAGMA table_info(proveedores)")
            columnas = [col[1] for col in cursor.fetchall()]
            
            if 'empresa' not in columnas:
                print("📝 Agregando columna empresa a tabla proveedores...")
                cursor.execute("ALTER TABLE proveedores ADD COLUMN empresa VARCHAR(100)")
                print("✅ Columna empresa agregada")
            else:
                print("ℹ️  Columna empresa ya existe")
            
            # Crear tabla de relación proveedor_flor si no existe
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='proveedor_flor'
            """)
            if not cursor.fetchone():
                print("📝 Creando tabla proveedor_flor...")
                cursor.execute("""
                    CREATE TABLE proveedor_flor (
                        proveedor_id VARCHAR(10) NOT NULL,
                        flor_id VARCHAR(10) NOT NULL,
                        PRIMARY KEY (proveedor_id, flor_id),
                        FOREIGN KEY(proveedor_id) REFERENCES proveedores(id),
                        FOREIGN KEY(flor_id) REFERENCES flores(id)
                    )
                """)
                print("✅ Tabla proveedor_flor creada")
            else:
                print("ℹ️  Tabla proveedor_flor ya existe")
            
            # Crear tabla de relación proveedor_contenedor si no existe
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='proveedor_contenedor'
            """)
            if not cursor.fetchone():
                print("📝 Creando tabla proveedor_contenedor...")
                cursor.execute("""
                    CREATE TABLE proveedor_contenedor (
                        proveedor_id VARCHAR(10) NOT NULL,
                        contenedor_id VARCHAR(10) NOT NULL,
                        PRIMARY KEY (proveedor_id, contenedor_id),
                        FOREIGN KEY(proveedor_id) REFERENCES proveedores(id),
                        FOREIGN KEY(contenedor_id) REFERENCES contenedores(id)
                    )
                """)
                print("✅ Tabla proveedor_contenedor creada")
            else:
                print("ℹ️  Tabla proveedor_contenedor ya existe")
            
            # Migrar datos de proveedor_id a la tabla de relación (si existe la columna)
            cursor.execute("PRAGMA table_info(flores)")
            columnas_flores = [col[1] for col in cursor.fetchall()]
            
            if 'proveedor_id' in columnas_flores:
                print("📝 Migrando relaciones existentes de proveedor_id a proveedor_flor...")
                cursor.execute("""
                    INSERT INTO proveedor_flor (proveedor_id, flor_id)
                    SELECT proveedor_id, id
                    FROM flores
                    WHERE proveedor_id IS NOT NULL
                    AND NOT EXISTS (
                        SELECT 1 FROM proveedor_flor 
                        WHERE proveedor_flor.proveedor_id = flores.proveedor_id 
                        AND proveedor_flor.flor_id = flores.id
                    )
                """)
                migrados = cursor.rowcount
                print(f"✅ {migrados} relaciones migradas")
            
            conn.commit()
            print("\n✅ Migración completada exitosamente")
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Error durante la migración: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            conn.close()

if __name__ == '__main__':
    print("=" * 60)
    print("🔄 MIGRACIÓN: Proveedores con empresa y relaciones muchos-a-muchos")
    print("=" * 60)
    print()
    
    if migrar_proveedores():
        print("\n✅ La migración se completó correctamente")
        sys.exit(0)
    else:
        print("\n❌ La migración falló")
        sys.exit(1)

