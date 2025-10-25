#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de inicio del backend con mejor manejo de errores
"""

import sys
import traceback

print("=" * 80)
print("🌸 INICIANDO BACKEND LAS-LIRA")
print("=" * 80)

try:
    print("\n1️⃣  Importando aplicación...")
    from app import app
    print("   ✅ Aplicación importada correctamente")
    
    print("\n2️⃣  Verificando base de datos...")
    from extensions import db
    with app.app_context():
        # Verificar conexión a la base de datos
        from models.producto import Producto
        count = Producto.query.count()
        print(f"   ✅ Base de datos conectada ({count} productos)")
    
    print("\n3️⃣  Iniciando servidor Flask...")
    print("   📍 URL: http://127.0.0.1:5001")
    print("   📍 API: http://127.0.0.1:5001/api")
    print("\n   ⚠️  Presiona CTRL+C para detener el servidor")
    print("=" * 80)
    
    app.run(host='0.0.0.0', port=5001, debug=False)
    
except ImportError as e:
    print(f"\n❌ ERROR DE IMPORTACIÓN:")
    print(f"   {str(e)}")
    print("\n💡 Solución: Instala las dependencias:")
    print("   pip3 install -r requirements.txt")
    traceback.print_exc()
    sys.exit(1)

except Exception as e:
    print(f"\n❌ ERROR AL INICIAR:")
    print(f"   {str(e)}")
    traceback.print_exc()
    sys.exit(1)

