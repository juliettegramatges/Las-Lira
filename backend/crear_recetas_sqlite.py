#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para crear asociaciones entre productos e insumos usando SQLite directo
"""

import sqlite3
from difflib import SequenceMatcher

DB_PATH = 'instance/laslira.db'

def similitud(a, b):
    """Calcula similitud entre dos strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def buscar_flor_por_nombre(cursor, nombre_buscar, threshold=0.5):
    """Busca una flor similar por nombre"""
    cursor.execute("SELECT id, nombre, tipo, color FROM flores")
    flores = cursor.fetchall()
    
    mejor_match = None
    mejor_score = 0
    
    for flor in flores:
        flor_id, nombre, tipo, color = flor
        nombre_flor = nombre or f"{tipo or ''} {color or ''}".strip()
        
        score = similitud(nombre_buscar, nombre_flor)
        if score > mejor_score and score >= threshold:
            mejor_score = score
            mejor_match = (flor_id, nombre_flor)
    
    return mejor_match, mejor_score

def buscar_contenedor_por_nombre(cursor, nombre_buscar, threshold=0.4):
    """Busca un contenedor similar por nombre"""
    cursor.execute("SELECT id, nombre, tipo FROM contenedores")
    contenedores = cursor.fetchall()
    
    mejor_match = None
    mejor_score = 0
    
    for contenedor in contenedores:
        cont_id, nombre, tipo = contenedor
        nombre_cont = nombre or tipo or ''
        
        score = similitud(nombre_buscar, nombre_cont)
        if score > mejor_score and score >= threshold:
            mejor_score = score
            mejor_match = (cont_id, nombre_cont)
    
    return mejor_match, mejor_score

def crear_recetas():
    """Crea recetas automáticas"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("🌸 CREANDO RECETAS DE PRODUCTOS")
    print("=" * 80)
    
    # Contar insumos
    cursor.execute("SELECT COUNT(*) FROM flores")
    total_flores = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM contenedores")
    total_contenedores = cursor.fetchone()[0]
    
    print(f"\n📦 Insumos disponibles:")
    print(f"   - {total_flores} flores")
    print(f"   - {total_contenedores} contenedores")
    
    # Obtener todos los productos
    cursor.execute("SELECT id, nombre, flores_asociadas, tipos_macetero FROM productos")
    productos = cursor.fetchall()
    
    print(f"\n🌺 Procesando {len(productos)} productos...")
    
    recetas_creadas = 0
    productos_procesados = 0
    
    for producto in productos:
        prod_id, prod_nombre, flores_asociadas, tipos_macetero = producto
        print(f"\n   Procesando: {prod_nombre} (ID: {prod_id})")
        recetas_producto = 0
        
        # 1. Asociar flores
        if flores_asociadas:
            flores_lista = [f.strip() for f in flores_asociadas.split(',')[:5]]
            
            for flor_nombre in flores_lista:
                if not flor_nombre:
                    continue
                
                match, score = buscar_flor_por_nombre(cursor, flor_nombre)
                
                if match:
                    flor_id, flor_nombre_match = match
                    
                    # Verificar si ya existe
                    cursor.execute("""
                        SELECT COUNT(*) FROM recetas_productos 
                        WHERE producto_id = ? AND insumo_tipo = 'Flor' AND insumo_id = ?
                    """, (prod_id, flor_id))
                    
                    if cursor.fetchone()[0] == 0:
                        cursor.execute("""
                            INSERT INTO recetas_productos 
                            (producto_id, insumo_tipo, insumo_id, cantidad, unidad, es_opcional)
                            VALUES (?, 'Flor', ?, 10, 'Tallos', 0)
                        """, (prod_id, flor_id))
                        recetas_producto += 1
                        print(f"         ✅ Flor: '{flor_nombre}' → {flor_nombre_match} (score: {score:.2f})")
        
        # 2. Asociar contenedor
        if tipos_macetero and tipos_macetero.lower() not in ['sin contenedor', 'ninguno', '', 'papel / hilo']:
            match, score = buscar_contenedor_por_nombre(cursor, tipos_macetero)
            
            if match:
                cont_id, cont_nombre = match
                
                # Verificar si ya existe
                cursor.execute("""
                    SELECT COUNT(*) FROM recetas_productos 
                    WHERE producto_id = ? AND insumo_tipo = 'Contenedor' AND insumo_id = ?
                """, (prod_id, cont_id))
                
                if cursor.fetchone()[0] == 0:
                    cursor.execute("""
                        INSERT INTO recetas_productos 
                        (producto_id, insumo_tipo, insumo_id, cantidad, unidad, es_opcional)
                        VALUES (?, 'Contenedor', ?, 1, 'Unidad', 0)
                    """, (prod_id, cont_id))
                    recetas_producto += 1
                    print(f"         ✅ Contenedor: {cont_nombre} (score: {score:.2f})")
        
        if recetas_producto > 0:
            productos_procesados += 1
            recetas_creadas += recetas_producto
    
    # Commit
    conn.commit()
    
    # Verificar recetas creadas
    cursor.execute("SELECT COUNT(*) FROM recetas_productos")
    total_recetas = cursor.fetchone()[0]
    
    conn.close()
    
    print("\n" + "=" * 80)
    print(f"✅ PROCESO COMPLETADO")
    print("=" * 80)
    print(f"\n   📊 Estadísticas:")
    print(f"      - Productos procesados: {productos_procesados}/{len(productos)}")
    print(f"      - Recetas creadas: {recetas_creadas}")
    print(f"      - Total recetas en DB: {total_recetas}")
    print(f"      - Promedio de recetas por producto: {recetas_creadas/productos_procesados if productos_procesados > 0 else 0:.1f}")
    print("\n" + "=" * 80)

if __name__ == '__main__':
    crear_recetas()

