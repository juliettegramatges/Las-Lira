"""
Script para agregar stock inicial a las flores creadas desde el CSV
"""

import sys
import os

# Añadir el directorio backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from extensions import db
from models.inventario import Flor, Contenedor
from app import app

def agregar_stock_inicial():
    """Agrega stock inicial a flores y contenedores del CSV que tienen stock 0"""

    with app.app_context():
        print("="*80)
        print("📦 AGREGANDO STOCK INICIAL A INSUMOS DEL RECETARIO")
        print("="*80)

        # Actualizar flores del CSV que tienen stock 0
        flores_csv = Flor.query.filter(
            Flor.id.like('FLO_%'),
            Flor.cantidad_stock == 0
        ).all()

        print(f"\n🌸 Flores del recetario sin stock: {len(flores_csv)}")

        for flor in flores_csv:
            flor.cantidad_stock = 100  # Stock inicial de 100 tallos
            flor.costo_unitario = 1000  # Costo inicial de $1000 por tallo
            print(f"   ✅ {flor.nombre}: 100 tallos @ $1,000")

        # Actualizar contenedores del CSV que tienen stock 0
        contenedores_csv = Contenedor.query.filter(
            Contenedor.id.like('CON_%'),
            Contenedor.cantidad_stock == 0
        ).all()

        print(f"\n🏺 Contenedores del recetario sin stock: {len(contenedores_csv)}")

        for contenedor in contenedores_csv:
            contenedor.cantidad_stock = 50  # Stock inicial de 50 unidades
            contenedor.costo = 2000  # Costo inicial de $2000 por unidad
            print(f"   ✅ {contenedor.nombre}: 50 unidades @ $2,000")

        # Commit todos los cambios
        db.session.commit()

        print("\n" + "="*80)
        print("✅ STOCK INICIAL AGREGADO EXITOSAMENTE")
        print("="*80)
        print(f"   Flores actualizadas: {len(flores_csv)}")
        print(f"   Contenedores actualizados: {len(contenedores_csv)}")
        print("="*80)

if __name__ == '__main__':
    agregar_stock_inicial()
