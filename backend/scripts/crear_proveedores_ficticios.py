#!/usr/bin/env python3
"""
Script para crear proveedores ficticios iniciales
"""

import sys
import os

# Agregar el directorio backend al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from extensions import db
from app import app
from models.inventario import Proveedor

PROVEEDORES_FICTICIOS = [
    {
        'nombre': 'María González',
        'contacto': 'María González',
        'telefono': '+56 9 1234 5678',
        'empresa': 'Flores del Valle',
        'email': 'maria@floresdelvalle.cl',
        'especialidad': 'Flores frescas importadas y nacionales',
        'dias_entrega': 'Lunes a Viernes, 24-48 horas',
        'notas': 'Proveedor principal de rosas y liliums'
    },
    {
        'nombre': 'Carlos Ramírez',
        'contacto': 'Carlos Ramírez',
        'telefono': '+56 9 2345 6789',
        'empresa': 'Contenedores Premium',
        'email': 'carlos@contenedorespremium.cl',
        'especialidad': 'Contenedores de vidrio y cerámica',
        'dias_entrega': 'Martes y Jueves',
        'notas': 'Mayorista, pedidos mínimos de 10 unidades'
    },
    {
        'nombre': 'Ana Martínez',
        'contacto': 'Ana Martínez',
        'telefono': '+56 9 3456 7890',
        'empresa': 'Vivero Las Flores',
        'email': 'ana@viverolasflores.cl',
        'especialidad': 'Flores de temporada y plantas',
        'dias_entrega': 'Lunes a Sábado, mismo día si se ordena antes de 10am',
        'notas': 'Excelente calidad, precios competitivos'
    },
    {
        'nombre': 'Roberto Silva',
        'contacto': 'Roberto Silva',
        'telefono': '+56 9 4567 8901',
        'empresa': 'Decoraciones Silva',
        'email': 'roberto@decoracionessilva.cl',
        'especialidad': 'Contenedores de mimbre y materiales naturales',
        'dias_entrega': 'Miércoles y Viernes',
        'notas': 'Productos artesanales, entrega personalizada'
    },
    {
        'nombre': 'Laura Fernández',
        'contacto': 'Laura Fernández',
        'telefono': '+56 9 5678 9012',
        'empresa': 'Flores Exóticas S.A.',
        'email': 'laura@floresexoticas.cl',
        'especialidad': 'Flores exóticas e importadas de alta gama',
        'dias_entrega': 'Lunes, Miércoles y Viernes',
        'notas': 'Pedidos con 3 días de anticipación mínimo'
    }
]

def crear_proveedores_ficticios():
    """Crea proveedores ficticios si no existen"""
    with app.app_context():
        try:
            creados = 0
            existentes = 0
            
            for i, datos_proveedor in enumerate(PROVEEDORES_FICTICIOS, 1):
                proveedor_id = f'PR{str(i).zfill(3)}'
                
                # Verificar si ya existe
                proveedor_existente = Proveedor.query.get(proveedor_id)
                if proveedor_existente:
                    print(f"ℹ️  Proveedor {proveedor_id} ({datos_proveedor['nombre']}) ya existe")
                    existentes += 1
                    continue
                
                nuevo_proveedor = Proveedor(
                    id=proveedor_id,
                    nombre=datos_proveedor['nombre'],
                    contacto=datos_proveedor['contacto'],
                    telefono=datos_proveedor['telefono'],
                    empresa=datos_proveedor['empresa'],
                    email=datos_proveedor['email'],
                    especialidad=datos_proveedor['especialidad'],
                    dias_entrega=datos_proveedor['dias_entrega'],
                    notas=datos_proveedor['notas'],
                    activo=True
                )
                
                db.session.add(nuevo_proveedor)
                creados += 1
                print(f"✅ Creado proveedor {proveedor_id}: {datos_proveedor['nombre']}")
            
            db.session.commit()
            
            print(f"\n✅ Proceso completado:")
            print(f"   - Creados: {creados}")
            print(f"   - Existentes: {existentes}")
            print(f"   - Total: {creados + existentes}")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al crear proveedores: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("=" * 60)
    print("🌺 CREAR PROVEEDORES FICTICIOS")
    print("=" * 60)
    print()
    
    if crear_proveedores_ficticios():
        print("\n✅ Proveedores ficticios creados exitosamente")
        sys.exit(0)
    else:
        print("\n❌ Error al crear proveedores ficticios")
        sys.exit(1)

