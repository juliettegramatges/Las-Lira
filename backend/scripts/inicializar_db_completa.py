#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para inicializar la base de datos con todas las tablas y estructura correcta.
"""

import sys
from pathlib import Path

# Agregar el directorio backend al path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app import app
from extensions import db

print("=" * 80)
print("🔄 INICIALIZANDO BASE DE DATOS COMPLETA")
print("=" * 80)

with app.app_context():
    try:
        print("\n1️⃣  Eliminando tablas existentes (si las hay)...")
        db.drop_all()
        print("   ✅ Tablas eliminadas")
        
        print("\n2️⃣  Creando todas las tablas con estructura actualizada...")
        db.create_all()
        print("   ✅ Tablas creadas")
        
        # Verificar que la tabla pedidos tenga la columna foto_enviado_url
        from sqlalchemy import text
        result = db.session.execute(text("PRAGMA table_info(pedidos)")).fetchall()
        columnas = [row[1] for row in result]
        
        print(f"\n3️⃣  Verificando columnas de la tabla 'pedidos':")
        print(f"   📋 Total de columnas: {len(columnas)}")
        
        if 'foto_enviado_url' in columnas:
            print("   ✅ Columna 'foto_enviado_url' presente")
        else:
            print("   ❌ ERROR: Columna 'foto_enviado_url' no encontrada")
        
        print("\n4️⃣  Tablas creadas:")
        tables = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()
        for table in tables:
            print(f"   • {table[0]}")
        
        print("\n" + "=" * 80)
        print("✅ BASE DE DATOS INICIALIZADA CORRECTAMENTE")
        print("=" * 80)
        print("\n💡 Próximo paso: Ejecutar el script de importación de datos históricos")
        print("   python3 backend/scripts/importar_datos_historicos.py")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        sys.exit(1)

