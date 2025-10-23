"""
Script de migración para agregar campos cantidad_en_uso a la base de datos.
Este script es seguro de ejecutar múltiples veces.
"""

import sys
import os

# Agregar el directorio padre al path para poder importar backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import app, db
from sqlalchemy import text

def migrar_stock_en_uso():
    """Agrega los campos cantidad_en_uso a flores y contenedores"""
    
    with app.app_context():
        print("🔄 Iniciando migración: Agregar campos 'cantidad_en_uso'...")
        
        try:
            # Verificar si los campos ya existen
            inspector = db.inspect(db.engine)
            
            # MIGRACIÓN 1: Tabla flores
            flores_columns = [col['name'] for col in inspector.get_columns('flores')]
            if 'cantidad_en_uso' not in flores_columns:
                print("  📦 Agregando 'cantidad_en_uso' a tabla 'flores'...")
                db.session.execute(text(
                    "ALTER TABLE flores ADD COLUMN cantidad_en_uso INTEGER DEFAULT 0 NOT NULL"
                ))
                db.session.commit()
                print("    ✅ Campo 'cantidad_en_uso' agregado a 'flores'")
            else:
                print("    ℹ️  Campo 'cantidad_en_uso' ya existe en 'flores'")
            
            # MIGRACIÓN 2: Tabla contenedores
            contenedores_columns = [col['name'] for col in inspector.get_columns('contenedores')]
            if 'cantidad_en_uso' not in contenedores_columns:
                print("  🏺 Agregando 'cantidad_en_uso' a tabla 'contenedores'...")
                db.session.execute(text(
                    "ALTER TABLE contenedores ADD COLUMN cantidad_en_uso INTEGER DEFAULT 0 NOT NULL"
                ))
                db.session.commit()
                print("    ✅ Campo 'cantidad_en_uso' agregado a 'contenedores'")
            else:
                print("    ℹ️  Campo 'cantidad_en_uso' ya existe en 'contenedores'")
            
            print("\n✅ Migración completada exitosamente!")
            print("\n📊 Resumen de cambios:")
            print("   - Tabla 'flores' → cantidad_en_uso (INTEGER, DEFAULT 0)")
            print("   - Tabla 'contenedores' → cantidad_en_uso (INTEGER, DEFAULT 0)")
            print("\n💡 La aplicación ahora puede rastrear:")
            print("   • Stock total en bodega")
            print("   • Stock reservado (en uso) en pedidos")
            print("   • Stock disponible = total - en uso")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error durante la migración: {e}")
            raise

if __name__ == '__main__':
    migrar_stock_en_uso()

