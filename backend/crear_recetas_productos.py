#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para crear asociaciones automáticas entre productos e insumos
"""

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from app import app
from extensions import db
from models.producto import Producto, RecetaProducto
from models.inventario import Flor, Contenedor
from difflib import SequenceMatcher

def similitud(a, b):
    """Calcula similitud entre dos strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def buscar_insumo_similar(nombre_buscar, lista_insumos, threshold=0.6):
    """Busca un insumo similar por nombre"""
    mejor_match = None
    mejor_score = 0
    
    for insumo in lista_insumos:
        score = similitud(nombre_buscar, insumo['nombre'])
        if score > mejor_score and score >= threshold:
            mejor_score = score
            mejor_match = insumo
    
    return mejor_match, mejor_score

def crear_recetas():
    """Crea recetas automáticas basándose en flores_asociadas y tipos_macetero"""
    
    with app.app_context():
        print("=" * 80)
        print("🌸 CREANDO RECETAS DE PRODUCTOS")
        print("=" * 80)
        
        # Cargar todos los insumos
        flores = Flor.query.all()
        contenedores = Contenedor.query.all()
        
        flores_dict = [{'id': f.id, 'nombre': f.nombre or f"{f.tipo or ''} {f.color or ''}".strip()} for f in flores]
        contenedores_dict = [{'id': c.id, 'nombre': c.nombre or f"{c.tipo or ''}".strip()} for c in contenedores]
        
        print(f"\n📦 Insumos disponibles:")
        print(f"   - {len(flores_dict)} flores")
        print(f"   - {len(contenedores_dict)} contenedores")
        
        # Procesar todos los productos
        productos = Producto.query.all()
        print(f"\n🌺 Procesando {len(productos)} productos...")
        
        recetas_creadas = 0
        productos_procesados = 0
        
        for producto in productos:
            print(f"\n   Procesando: {producto.nombre} (ID: {producto.id})")
            recetas_producto = 0
            
            # 1. Asociar flores
            if producto.flores_asociadas:
                flores_texto = producto.flores_asociadas
                print(f"      Flores asociadas: {flores_texto[:80]}...")
                
                # Dividir por comas y procesar cada flor
                flores_lista = [f.strip() for f in flores_texto.split(',')]
                
                for flor_nombre in flores_lista[:5]:  # Limitar a 5 flores principales
                    if not flor_nombre:
                        continue
                    
                    match, score = buscar_insumo_similar(flor_nombre, flores_dict, threshold=0.5)
                    
                    if match:
                        # Verificar si ya existe la receta
                        existe = RecetaProducto.query.filter_by(
                            producto_id=producto.id,
                            insumo_tipo='Flor',
                            insumo_id=match['id']
                        ).first()
                        
                        if not existe:
                            receta = RecetaProducto(
                                producto_id=producto.id,
                                insumo_tipo='Flor',
                                insumo_id=match['id'],
                                cantidad=10,  # Cantidad por defecto
                                unidad='Tallos',
                                es_opcional=False
                            )
                            db.session.add(receta)
                            recetas_producto += 1
                            print(f"         ✅ Flor: '{flor_nombre}' → {match['nombre']} (score: {score:.2f})")
            
            # 2. Asociar contenedor
            if producto.tipos_macetero and producto.tipos_macetero.lower() not in ['sin contenedor', 'ninguno', '']:
                contenedor_texto = producto.tipos_macetero
                print(f"      Contenedor: {contenedor_texto}")
                
                match, score = buscar_insumo_similar(contenedor_texto, contenedores_dict, threshold=0.4)
                
                if match:
                    # Verificar si ya existe
                    existe = RecetaProducto.query.filter_by(
                        producto_id=producto.id,
                        insumo_tipo='Contenedor',
                        insumo_id=match['id']
                    ).first()
                    
                    if not existe:
                        receta = RecetaProducto(
                            producto_id=producto.id,
                            insumo_tipo='Contenedor',
                            insumo_id=match['id'],
                            cantidad=1,
                            unidad='Unidad',
                            es_opcional=False
                        )
                        db.session.add(receta)
                        recetas_producto += 1
                        print(f"         ✅ Contenedor: {match['nombre']} (score: {score:.2f})")
            
            if recetas_producto > 0:
                productos_procesados += 1
                recetas_creadas += recetas_producto
        
        # Commit
        db.session.commit()
        
        print("\n" + "=" * 80)
        print(f"✅ PROCESO COMPLETADO")
        print("=" * 80)
        print(f"\n   📊 Estadísticas:")
        print(f"      - Productos procesados: {productos_procesados}/{len(productos)}")
        print(f"      - Recetas creadas: {recetas_creadas}")
        print(f"      - Promedio de recetas por producto: {recetas_creadas/productos_procesados if productos_procesados > 0 else 0:.1f}")
        print("\n" + "=" * 80)

if __name__ == '__main__':
    crear_recetas()

