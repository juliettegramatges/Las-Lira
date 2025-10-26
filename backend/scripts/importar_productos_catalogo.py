#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para importar productos del catálogo al sistema web
"""

import sys
import os
from pathlib import Path

# Agregar el directorio backend al path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app import app
from extensions import db
from models.producto import Producto

import csv
from decimal import Decimal

# Ruta del archivo CSV
BASE_DIR = backend_dir.parent
PRODUCTOS_CSV = BASE_DIR / 'catalogo_productos_completo.csv'

def parse_precio(precio_str):
    """Extrae el primer precio de un string como 'Mini — $9.500, S — $18.000'"""
    if not precio_str or precio_str in ['', 'nan', 'None', 'Variable']:
        return 0
    
    # Si tiene múltiples precios, tomar el primero
    if '—' in precio_str or '-' in precio_str:
        # Extraer el primer precio
        import re
        precios = re.findall(r'\$?\s*(\d+[\.,]?\d*)', precio_str)
        if precios:
            precio_str = precios[0]
    
    # Limpiar y convertir
    precio_str = str(precio_str).replace('$', '').replace('.', '').replace(',', '').strip()
    try:
        return int(precio_str)
    except:
        return 0

def main():
    print("=" * 80)
    print("📦 IMPORTANDO PRODUCTOS DEL CATÁLOGO")
    print("=" * 80)
    
    if not PRODUCTOS_CSV.exists():
        print(f"❌ ERROR: No se encontró el archivo {PRODUCTOS_CSV}")
        return
    
    with app.app_context():
        print(f"\n📂 Leyendo: {PRODUCTOS_CSV}")
        
        productos_importados = 0
        productos_actualizados = 0
        
        with open(PRODUCTOS_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                nombre = row.get('Nombre', '').strip()
                
                if not nombre:
                    continue
                
                # Buscar si el producto ya existe
                producto = Producto.query.filter_by(nombre=nombre).first()
                
                if producto:
                    # Actualizar producto existente
                    producto.descripcion = row.get('Descripción', '')
                    producto.categoria = row.get('Categoría', 'Flores en Plantas')
                    producto.precio_venta = parse_precio(row.get('Precio', '0'))
                    productos_actualizados += 1
                    print(f"   ✏️  Actualizado: {nombre} - ${producto.precio_venta:,}")
                else:
                    # Crear nuevo producto
                    nuevo_producto = Producto(
                        nombre=nombre,
                        descripcion=row.get('Descripción', ''),
                        categoria=row.get('Categoría', 'Flores en Plantas'),
                        tipo_arreglo='Ramo',  # Valor por defecto
                        precio_venta=parse_precio(row.get('Precio', '0')),
                        activo=True
                    )
                    db.session.add(nuevo_producto)
                    productos_importados += 1
                    print(f"   ✅ Nuevo: {nombre} - ${nuevo_producto.precio_venta:,}")
        
        # Commit de todos los cambios
        db.session.commit()
        
        print("\n" + "=" * 80)
        print(f"✅ IMPORTACIÓN COMPLETADA")
        print(f"   • Productos nuevos: {productos_importados}")
        print(f"   • Productos actualizados: {productos_actualizados}")
        print(f"   • Total en base de datos: {Producto.query.count()}")
        print("=" * 80)

if __name__ == '__main__':
    main()

