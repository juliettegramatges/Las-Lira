#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico para productos
"""

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from app import app
from extensions import db
from models.producto import Producto

print("=" * 80)
print("🔍 DIAGNÓSTICO DE PRODUCTOS")
print("=" * 80)

with app.app_context():
    try:
        # Verificar si la tabla existe
        print("\n1️⃣  Verificando si la tabla 'productos' existe...")
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'productos' in tables:
            print("   ✅ La tabla 'productos' existe")
            
            # Ver columnas
            columns = [col['name'] for col in inspector.get_columns('productos')]
            print(f"   📋 Columnas encontradas: {', '.join(columns)}")
            
            # Contar productos
            print("\n2️⃣  Contando productos...")
            total = Producto.query.count()
            print(f"   📊 Total de productos: {total}")
            
            if total > 0:
                print("\n3️⃣  Probando to_dict() en el primer producto...")
                producto = Producto.query.first()
                print(f"   🌸 Producto: {producto.nombre}")
                
                try:
                    producto_dict = producto.to_dict()
                    print("   ✅ to_dict() funciona correctamente")
                    print(f"   📦 Keys: {list(producto_dict.keys())}")
                except Exception as e:
                    print(f"   ❌ Error en to_dict(): {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("\n   ⚠️  No hay productos en la base de datos")
                print("   💡 Sugerencia: Ejecuta python3 scripts/importar_productos_catalogo.py")
        else:
            print("   ❌ La tabla 'productos' NO existe")
            print("   💡 Sugerencia: Ejecuta python3 scripts/inicializar_db_completa.py")
            
    except Exception as e:
        print(f"\n❌ Error durante el diagnóstico:")
        print(f"   {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 80)
print("✅ DIAGNÓSTICO COMPLETADO")
print("=" * 80)

