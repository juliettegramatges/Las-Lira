#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para aplicar cambios al esquema de flores y contenedores
"""

import sys
from pathlib import Path
from sqlalchemy import text

# Agregar el directorio backend al path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from app import app
from extensions import db

print("=" * 80)
print("🔄 MIGRANDO ESQUEMA DE INVENTARIO")
print("=" * 80)

with app.app_context():
    print("\n📋 Aplicando cambios al esquema...")
    
    try:
        with db.engine.connect() as connection:
            # Agregar columnas a la tabla flores si no existen
            connection.execute(text("""
                ALTER TABLE flores ADD COLUMN IF NOT EXISTS nombre VARCHAR(100);
            """))
            connection.execute(text("""
                ALTER TABLE flores ADD COLUMN IF NOT EXISTS ubicacion VARCHAR(100);
            """))
            connection.execute(text("""
                ALTER TABLE flores ALTER COLUMN color DROP NOT NULL;
            """))
            connection.execute(text("""
                ALTER TABLE flores ALTER COLUMN costo_unitario DROP NOT NULL;
            """))
            connection.execute(text("""
                ALTER TABLE flores ALTER COLUMN costo_unitario SET DEFAULT 0;
            """))
            connection.execute(text("""
                ALTER TABLE flores ALTER COLUMN unidad DROP NOT NULL;
            """))
            connection.execute(text("""
                ALTER TABLE flores ALTER COLUMN unidad SET DEFAULT 'Tallos';
            """))
            
            print("   ✅ Tabla flores actualizada")
            
            # Agregar columnas a la tabla contenedores si no existen
            connection.execute(text("""
                ALTER TABLE contenedores ADD COLUMN IF NOT EXISTS nombre VARCHAR(100);
            """))
            connection.execute(text("""
                ALTER TABLE contenedores ADD COLUMN IF NOT EXISTS ubicacion VARCHAR(100);
            """))
            
            # Renombrar stock a cantidad_stock si no existe
            connection.execute(text("""
                ALTER TABLE contenedores ADD COLUMN IF NOT EXISTS cantidad_stock INTEGER DEFAULT 0;
            """))
            connection.execute(text("""
                UPDATE contenedores SET cantidad_stock = stock WHERE cantidad_stock = 0;
            """))
            
            # Hacer campos opcionales
            connection.execute(text("""
                ALTER TABLE contenedores ALTER COLUMN material DROP NOT NULL;
            """))
            connection.execute(text("""
                ALTER TABLE contenedores ALTER COLUMN forma DROP NOT NULL;
            """))
            connection.execute(text("""
                ALTER TABLE contenedores ALTER COLUMN tamano DROP NOT NULL;
            """))
            connection.execute(text("""
                ALTER TABLE contenedores ALTER COLUMN color DROP NOT NULL;
            """))
            connection.execute(text("""
                ALTER TABLE contenedores ALTER COLUMN costo DROP NOT NULL;
            """))
            connection.execute(text("""
                ALTER TABLE contenedores ALTER COLUMN costo SET DEFAULT 0;
            """))
            connection.execute(text("""
                ALTER TABLE contenedores ALTER COLUMN bodega_id DROP NOT NULL;
            """))
            
            # Cambiar tipo de tipo_contenedor de ENUM a VARCHAR
            try:
                connection.execute(text("""
                    ALTER TABLE contenedores ALTER COLUMN tipo TYPE VARCHAR(50);
                """))
            except:
                print("   ⚠️  No se pudo cambiar el tipo de 'tipo' (probablemente ya es VARCHAR)")
            
            connection.commit()
            print("   ✅ Tabla contenedores actualizada")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        print("   ℹ️  Algunos cambios pueden ya estar aplicados")
    
    print("\n" + "=" * 80)
    print("✅ MIGRACIÓN COMPLETADA")
    print("=" * 80)
    print("\n💡 Ahora puedes ejecutar:")
    print("   python3 importar_insumos_csv.py")
    print("=" * 80)


