#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para poblar flores y contenedores de demostración
"""

import sys
from pathlib import Path

# Agregar el directorio backend al path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from app import app
from extensions import db
from models.inventario import Flor, Contenedor

print("=" * 80)
print("🌸 POBLANDO FLORES Y CONTENEDORES DE DEMOSTRACIÓN")
print("=" * 80)

with app.app_context():
    # Verificar si ya hay datos
    flores_existentes = Flor.query.count()
    contenedores_existentes = Contenedor.query.count()
    
    print(f"\n📊 Estado actual:")
    print(f"   • Flores en DB: {flores_existentes}")
    print(f"   • Contenedores en DB: {contenedores_existentes}")
    
    if flores_existentes > 0 or contenedores_existentes > 0:
        respuesta = input("\n⚠️  Ya hay datos. ¿Quieres agregar más? (s/n): ")
        if respuesta.lower() != 's':
            print("\n❌ Operación cancelada")
            sys.exit(0)
    
    print("\n🌸 Creando flores de demostración...")
    
    flores_demo = [
        # Rosas
        {'nombre': 'Rosa', 'tipo': 'Rosa', 'color': 'Roja', 'costo_unitario': 800, 'ubicacion': 'Taller'},
        {'nombre': 'Rosa', 'tipo': 'Rosa', 'color': 'Blanca', 'costo_unitario': 800, 'ubicacion': 'Taller'},
        {'nombre': 'Rosa', 'tipo': 'Rosa', 'color': 'Rosada', 'costo_unitario': 800, 'ubicacion': 'Taller'},
        {'nombre': 'Rosa', 'tipo': 'Rosa', 'color': 'Amarilla', 'costo_unitario': 800, 'ubicacion': 'Taller'},
        {'nombre': 'Rosa', 'tipo': 'Rosa', 'color': 'Naranja', 'costo_unitario': 800, 'ubicacion': 'Taller'},
        
        # Liliums
        {'nombre': 'Lilium', 'tipo': 'Lilium', 'color': 'Blanco', 'costo_unitario': 1500, 'ubicacion': 'Taller'},
        {'nombre': 'Lilium', 'tipo': 'Lilium', 'color': 'Rosado', 'costo_unitario': 1500, 'ubicacion': 'Taller'},
        
        # Tulipanes
        {'nombre': 'Tulipán', 'tipo': 'Tulipán', 'color': 'Rojo', 'costo_unitario': 1200, 'ubicacion': 'Taller'},
        {'nombre': 'Tulipán', 'tipo': 'Tulipán', 'color': 'Amarillo', 'costo_unitario': 1200, 'ubicacion': 'Taller'},
        {'nombre': 'Tulipán', 'tipo': 'Tulipán', 'color': 'Rosado', 'costo_unitario': 1200, 'ubicacion': 'Taller'},
        
        # Claveles
        {'nombre': 'Clavel', 'tipo': 'Clavel', 'color': 'Blanco', 'costo_unitario': 400, 'ubicacion': 'Taller'},
        {'nombre': 'Clavel', 'tipo': 'Clavel', 'color': 'Rojo', 'costo_unitario': 400, 'ubicacion': 'Taller'},
        {'nombre': 'Clavel', 'tipo': 'Clavel', 'color': 'Rosado', 'costo_unitario': 400, 'ubicacion': 'Taller'},
        
        # Girasoles
        {'nombre': 'Girasol', 'tipo': 'Girasol', 'color': 'Amarillo', 'costo_unitario': 2000, 'ubicacion': 'Taller'},
        
        # Peonías
        {'nombre': 'Peonía', 'tipo': 'Peonía', 'color': 'Rosada', 'costo_unitario': 3500, 'ubicacion': 'Taller'},
        {'nombre': 'Peonía', 'tipo': 'Peonía', 'color': 'Blanca', 'costo_unitario': 3500, 'ubicacion': 'Taller'},
        
        # Orquídeas
        {'nombre': 'Orquídea', 'tipo': 'Orquídea', 'color': 'Blanca', 'costo_unitario': 4000, 'ubicacion': 'Taller'},
        {'nombre': 'Orquídea', 'tipo': 'Orquídea', 'color': 'Morada', 'costo_unitario': 4000, 'ubicacion': 'Taller'},
        
        # Hortensias
        {'nombre': 'Hortensia', 'tipo': 'Hortensia', 'color': 'Azul', 'costo_unitario': 2500, 'ubicacion': 'Taller'},
        {'nombre': 'Hortensia', 'tipo': 'Hortensia', 'color': 'Rosada', 'costo_unitario': 2500, 'ubicacion': 'Taller'},
        
        # Gerberas
        {'nombre': 'Gerbera', 'tipo': 'Gerbera', 'color': 'Naranja', 'costo_unitario': 800, 'ubicacion': 'Taller'},
        {'nombre': 'Gerbera', 'tipo': 'Gerbera', 'color': 'Rosada', 'costo_unitario': 800, 'ubicacion': 'Taller'},
        {'nombre': 'Gerbera', 'tipo': 'Gerbera', 'color': 'Amarilla', 'costo_unitario': 800, 'ubicacion': 'Taller'},
    ]
    
    flores_creadas = 0
    for flor_data in flores_demo:
        # Verificar si ya existe
        existe = Flor.query.filter_by(
            tipo=flor_data['tipo'],
            color=flor_data['color']
        ).first()
        
        if not existe:
            flor = Flor(**flor_data)
            db.session.add(flor)
            flores_creadas += 1
            print(f"   ✅ {flor_data['tipo']} {flor_data['color']}")
    
    print(f"\n📦 Creando contenedores de demostración...")
    
    contenedores_demo = [
        # Floreros
        {'nombre': 'Florero Cilíndrico', 'tipo': 'Florero', 'tamano': '20cm', 'costo': 5000, 'ubicacion': 'Bodega 1'},
        {'nombre': 'Florero Cilíndrico', 'tipo': 'Florero', 'tamano': '30cm', 'costo': 7000, 'ubicacion': 'Bodega 1'},
        {'nombre': 'Florero Cuadrado', 'tipo': 'Florero', 'tamano': '15cm', 'costo': 4500, 'ubicacion': 'Bodega 1'},
        {'nombre': 'Florero Cuadrado', 'tipo': 'Florero', 'tamano': '20cm', 'costo': 6000, 'ubicacion': 'Bodega 1'},
        
        # Maceteros
        {'nombre': 'Macetero Greda', 'tipo': 'Macetero', 'tamano': '20x20cm', 'costo': 3500, 'ubicacion': 'Bodega 2'},
        {'nombre': 'Macetero Cemento', 'tipo': 'Macetero', 'tamano': '25x25cm', 'costo': 8000, 'ubicacion': 'Bodega 2'},
        
        # Canastos
        {'nombre': 'Canasto Mimbre', 'tipo': 'Canasto', 'tamano': 'Mediano', 'costo': 4000, 'ubicacion': 'Bodega 1'},
        {'nombre': 'Canasto Mimbre', 'tipo': 'Canasto', 'tamano': 'Grande', 'costo': 6000, 'ubicacion': 'Bodega 1'},
        
        # Cajas
        {'nombre': 'Caja Hat Box', 'tipo': 'Caja', 'tamano': 'Chica', 'costo': 3000, 'ubicacion': 'Bodega 1'},
        {'nombre': 'Caja Hat Box', 'tipo': 'Caja', 'tamano': 'Mediana', 'costo': 4500, 'ubicacion': 'Bodega 1'},
        {'nombre': 'Caja Hat Box', 'tipo': 'Caja', 'tamano': 'Grande', 'costo': 6000, 'ubicacion': 'Bodega 1'},
        
        # Jardineras
        {'nombre': 'Jardinera', 'tipo': 'Jardinera', 'tamano': '60cm', 'costo': 8000, 'ubicacion': 'Bodega 2'},
        {'nombre': 'Jardinera', 'tipo': 'Jardinera', 'tamano': '90cm', 'costo': 12000, 'ubicacion': 'Bodega 2'},
        
        # Copas/Ánforas
        {'nombre': 'Copa Vidrio', 'tipo': 'Copa', 'tamano': '25cm', 'costo': 5500, 'ubicacion': 'Bodega 1'},
        {'nombre': 'Ánfora Cerámica', 'tipo': 'Ánfora', 'tamano': '30cm', 'costo': 9000, 'ubicacion': 'Bodega 2'},
    ]
    
    contenedores_creados = 0
    for contenedor_data in contenedores_demo:
        # Verificar si ya existe
        existe = Contenedor.query.filter_by(
            tipo=contenedor_data['tipo'],
            tamano=contenedor_data['tamano']
        ).first()
        
        if not existe:
            contenedor = Contenedor(**contenedor_data)
            db.session.add(contenedor)
            contenedores_creados += 1
            print(f"   ✅ {contenedor_data['nombre']} {contenedor_data['tamano']}")
    
    # Guardar todos los cambios
    db.session.commit()
    
    print("\n" + "=" * 80)
    print("✅ DATOS DE DEMOSTRACIÓN CREADOS EXITOSAMENTE")
    print("=" * 80)
    print(f"\n📊 Resumen:")
    print(f"   • Flores creadas: {flores_creadas}")
    print(f"   • Contenedores creados: {contenedores_creados}")
    print(f"   • Total flores en DB: {Flor.query.count()}")
    print(f"   • Total contenedores en DB: {Contenedor.query.count()}")
    print("\n💡 Recarga la página de Insumos en el navegador para verlos")
    print("=" * 80)


