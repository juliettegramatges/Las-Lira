"""
Script para agregar columnas de latitud y longitud a la tabla pedidos
"""

import sys
import os

# Agregar el directorio backend al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from sqlalchemy import text

def agregar_coordenadas():
    """Agrega columnas latitud y longitud a la tabla pedidos"""
    with app.app_context():
        try:
            # Verificar si las columnas ya existen
            result = db.session.execute(text("PRAGMA table_info(pedidos)"))
            columns = [row[1] for row in result]

            if 'latitud' in columns and 'longitud' in columns:
                print("✅ Las columnas latitud y longitud ya existen en la tabla pedidos")
                return True

            # Agregar columnas si no existen
            if 'latitud' not in columns:
                print("➕ Agregando columna 'latitud'...")
                db.session.execute(text("ALTER TABLE pedidos ADD COLUMN latitud FLOAT"))
                print("✅ Columna 'latitud' agregada")

            if 'longitud' not in columns:
                print("➕ Agregando columna 'longitud'...")
                db.session.execute(text("ALTER TABLE pedidos ADD COLUMN longitud FLOAT"))
                print("✅ Columna 'longitud' agregada")

            db.session.commit()
            print("✅ Migración completada exitosamente")
            print("\nℹ️  Las coordenadas se agregarán automáticamente cuando:")
            print("   - Se creen nuevos pedidos usando el selector de dirección")
            print("   - Se editen pedidos existentes y se actualice la dirección")

            return True

        except Exception as e:
            print(f"❌ Error durante la migración: {e}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    print("=" * 60)
    print("MIGRACIÓN: Agregar coordenadas GPS a pedidos")
    print("=" * 60)
    print()

    if agregar_coordenadas():
        print("\n✅ Migración exitosa")
    else:
        print("\n❌ La migración falló")
        sys.exit(1)
