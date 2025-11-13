#!/usr/bin/env python3
"""
Script para agregar la columna stock_bajo a las tablas flores y contenedores
y establecer valores por defecto para registros existentes.
"""

import sys
import os

# Agregar el directorio backend al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from extensions import db
from app import app
import sqlite3

def agregar_stock_bajo():
    """Agrega la columna stock_bajo a las tablas si no existe"""
    with app.app_context():
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        
        if not os.path.exists(db_path):
            print(f"❌ Base de datos no encontrada en: {db_path}")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Verificar si la columna ya existe en flores
            cursor.execute("PRAGMA table_info(flores)")
            columnas_flores = [col[1] for col in cursor.fetchall()]
            
            if 'stock_bajo' not in columnas_flores:
                print("📝 Agregando columna stock_bajo a tabla flores...")
                cursor.execute("ALTER TABLE flores ADD COLUMN stock_bajo INTEGER DEFAULT 10 NOT NULL")
                # Actualizar registros existentes
                cursor.execute("UPDATE flores SET stock_bajo = 10 WHERE stock_bajo IS NULL")
                print("✅ Columna stock_bajo agregada a flores (valor por defecto: 10)")
            else:
                print("ℹ️  Columna stock_bajo ya existe en flores")
            
            # Verificar si la columna ya existe en contenedores
            cursor.execute("PRAGMA table_info(contenedores)")
            columnas_contenedores = [col[1] for col in cursor.fetchall()]
            
            if 'stock_bajo' not in columnas_contenedores:
                print("📝 Agregando columna stock_bajo a tabla contenedores...")
                cursor.execute("ALTER TABLE contenedores ADD COLUMN stock_bajo INTEGER DEFAULT 5 NOT NULL")
                # Actualizar registros existentes
                cursor.execute("UPDATE contenedores SET stock_bajo = 5 WHERE stock_bajo IS NULL")
                print("✅ Columna stock_bajo agregada a contenedores (valor por defecto: 5)")
            else:
                print("ℹ️  Columna stock_bajo ya existe en contenedores")
            
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
    print("🔄 MIGRACIÓN: Agregar stock_bajo a insumos")
    print("=" * 60)
    print()
    
    if agregar_stock_bajo():
        print("\n✅ La migración se completó correctamente")
        sys.exit(0)
    else:
        print("\n❌ La migración falló")
        sys.exit(1)

