#!/usr/bin/env python3
"""
Script para recrear la base de datos desde cero
"""
import sys
import os

# Agregar el directorio raíz al path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

from backend.app import app, db

with app.app_context():
    print("🗑️  Eliminando tablas existentes...")
    db.drop_all()
    print("✅ Tablas eliminadas")
    
    print("📊 Creando tablas con nueva estructura...")
    db.create_all()
    print("✅ Tablas creadas exitosamente")
    print("\n✨ Base de datos lista para importar datos")

