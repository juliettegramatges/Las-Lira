#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para agregar la columna foto_enviado_url a la tabla pedidos si no existe.
"""

import sys
from pathlib import Path

# Agregar el directorio backend al path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app import app
from extensions import db
from sqlalchemy import text

print("=" * 80)
print("🔄 AGREGANDO COLUMNA FOTO_ENVIADO_URL")
print("=" * 80)

with app.app_context():
    try:
        # Verificar si la columna ya existe
        result = db.session.execute(text("PRAGMA table_info(pedidos)")).fetchall()
        columnas_existentes = [row[1] for row in result]
        
        print(f"\n📋 Columnas existentes en 'pedidos': {len(columnas_existentes)}")
        
        if 'foto_enviado_url' in columnas_existentes:
            print("   ✅ La columna 'foto_enviado_url' YA EXISTE en la tabla")
        else:
            print("   ⚠️  La columna 'foto_enviado_url' NO existe, agregándola...")
            
            # Agregar la columna
            db.session.execute(text("""
                ALTER TABLE pedidos 
                ADD COLUMN foto_enviado_url VARCHAR(500)
            """))
            
            db.session.commit()
            
            print("   ✅ Columna 'foto_enviado_url' agregada correctamente")
        
        # Verificar cuántos pedidos tienen foto
        result = db.session.execute(text("""
            SELECT COUNT(*) 
            FROM pedidos 
            WHERE foto_enviado_url IS NOT NULL
        """)).fetchone()
        
        pedidos_con_foto = result[0]
        
        print(f"\n📸 Pedidos con foto de respaldo: {pedidos_con_foto}")
        
        print("\n" + "=" * 80)
        print("✅ MIGRACIÓN COMPLETADA")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        db.session.rollback()
        sys.exit(1)

