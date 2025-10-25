#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de migración de base de datos para soportar datos históricos
RECREACIÓN COMPLETA: Borra y recrea todas las tablas desde cero
"""

import sys
from pathlib import Path
import os

# Agregar el directorio backend al path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app import app
from extensions import db

print("=" * 80)
print("🔄 RECREACIÓN DE BASE DE DATOS")
print("=" * 80)

with app.app_context():
    print("\n⚠️  ADVERTENCIA: Se borrarán y recrearán TODAS las tablas")
    print("   (Esto es necesario para aplicar los cambios de modelo correctamente)")
    
    try:
        # Borrar todas las tablas
        print("\n   1. Borrando tablas existentes...")
        db.drop_all()
        print("      ✅ Tablas eliminadas")
        
        # Recrear todas las tablas con la estructura actualizada
        print("\n   2. Recreando tablas con estructura actualizada...")
        db.create_all()
        print("      ✅ Tablas creadas")
        
        db.session.commit()
        
        print("\n" + "=" * 80)
        print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 80)
        print("\n   💡 Siguiente paso:")
        print("      • Ejecutar: python scripts/importar_datos_historicos.py")
        print("\n" + "=" * 80)
        
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Error durante la migración: {e}")
        print(f"\n   Detalles: {str(e)}")

