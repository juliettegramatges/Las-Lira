#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para resetear la base de datos e importar todos los datos
Ejecuta migración + importación en un solo comando
"""

import sys
from pathlib import Path

# Agregar el directorio backend al path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app import app
from extensions import db

print("=" * 80)
print("🔄 RESETEAR E IMPORTAR DATOS")
print("=" * 80)

with app.app_context():
    print("\n1️⃣  Borrando tablas existentes...")
    db.drop_all()
    print("   ✅ Tablas eliminadas")
    
    print("\n2️⃣  Creando tablas con nueva estructura...")
    db.create_all()
    print("   ✅ Tablas creadas")
    
    print("\n" + "=" * 80)
    print("✅ BASE DE DATOS LISTA")
    print("=" * 80)
    print("\n💡 Ahora ejecuta:")
    print("   python3 scripts/importar_datos_historicos.py")
    print("")

