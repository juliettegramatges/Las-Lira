#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simple para agregar el producto Personalización
"""

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app import app
from extensions import db
from models.producto import Producto

print("🌸 Agregando producto 'Personalización'...")

with app.app_context():
    # Verificar si ya existe
    existe = Producto.query.filter_by(nombre='Personalización').first()
    
    if existe:
        print(f"✅ El producto 'Personalización' ya existe (ID: {existe.id})")
        print(f"   Precio: ${existe.precio_venta:,}")
    else:
        # Crear nuevo producto
        nuevo = Producto(
            nombre='Personalización',
            descripcion='Arreglo personalizado según las preferencias del cliente',
            categoria='Flores en Plantas',
            tipo_arreglo='Ramo',
            precio_venta=0,  # Variable
            activo=True
        )
        db.session.add(nuevo)
        db.session.commit()
        
        print(f"✅ Producto 'Personalización' creado exitosamente (ID: {nuevo.id})")
    
    # Mostrar total de productos
    total = Producto.query.count()
    print(f"\n📦 Total de productos en la base de datos: {total}")


