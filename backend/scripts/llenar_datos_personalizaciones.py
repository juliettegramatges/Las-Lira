#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para llenar datos de personalización desde pedidos_trello_COMPLETO.csv
"""

import csv
import json
import sqlite3
from pathlib import Path

# Rutas
backend_dir = Path(__file__).resolve().parent.parent
base_dir = backend_dir.parent
csv_path = base_dir / 'pedidos_trello_COMPLETO.csv'
db_path = backend_dir / 'instance' / 'laslira.db'

print("=" * 80)
print("🎨 LLENANDO DATOS DE PERSONALIZACIÓN DESDE TRELLO")
print("=" * 80)

if not csv_path.exists():
    print(f"❌ ERROR: No se encontró {csv_path}")
    exit(1)

if not db_path.exists():
    print(f"❌ ERROR: No se encontró la base de datos en {db_path}")
    exit(1)

print(f"\n📂 Leyendo CSV: {csv_path}")
print(f"📂 Base de datos: {db_path}")

# Conectar a la base de datos
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Obtener ID del producto "Personalización"
cursor.execute("SELECT id FROM productos WHERE es_personalizacion = 1")
producto_personalizacion = cursor.fetchone()

if not producto_personalizacion:
    print("\n⚠️  No se encontró producto de personalización marcado.")
    print("    Ejecuta primero: python3 backend/migrar_personalizaciones.py")
    conn.close()
    exit(1)

producto_pers_id = producto_personalizacion[0]
print(f"\n✓ Producto personalización encontrado: {producto_pers_id}")

# Estadísticas
pedidos_actualizados = 0
pedidos_con_colores = 0
pedidos_con_tipo = 0
pedidos_con_notas = 0
pedidos_totales = 0

def limpiar_texto(texto):
    """Limpia y normaliza texto"""
    if not texto or texto.strip() in ['', 'nan', 'None', 'NULL']:
        return None
    return texto.strip()

def extraer_colores(colores_str):
    """Extrae lista de colores desde string"""
    if not colores_str or colores_str.strip() in ['', 'nan', 'None', 'NULL']:
        return None
    
    # Limpiar y separar colores
    colores = []
    colores_str = colores_str.strip()
    
    # Separar por comas, "y", "con", etc.
    separadores = [',', ' y ', ' con ', '+', '/', ' - ']
    partes = [colores_str]
    
    for sep in separadores:
        nuevas_partes = []
        for parte in partes:
            nuevas_partes.extend(parte.split(sep))
        partes = nuevas_partes
    
    # Limpiar cada color
    for color in partes:
        color = color.strip().title()
        if color and color not in ['', 'Y', 'Con', 'De']:
            colores.append(color)
    
    return json.dumps(colores, ensure_ascii=False) if colores else None

print("\n📊 Analizando pedidos...")

# Leer CSV
with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    
    for row in reader:
        pedidos_totales += 1
        
        # Obtener datos del CSV
        id_pedido = limpiar_texto(row.get('id_pedido'))
        producto_catalogo = limpiar_texto(row.get('producto_catalogo', ''))
        colores_str = limpiar_texto(row.get('colores', ''))
        tipo_producto = limpiar_texto(row.get('tipo_producto', ''))
        tipo_arreglo = limpiar_texto(row.get('tipo_arreglo', ''))
        detalles_cliente = limpiar_texto(row.get('detalles_cliente', ''))
        
        if not id_pedido:
            continue
        
        # Determinar si es personalización
        # Criterio: producto_catalogo vacío o match_score bajo, o tiene colores/tipos específicos
        match_score = row.get('match_score', '')
        
        es_personalizacion = False
        
        # 1. Si no tiene producto del catálogo o match score bajo
        if not producto_catalogo or match_score == '' or match_score == 'nan':
            es_personalizacion = True
        
        # 2. Si tiene "personaliz" en alguna descripción
        if producto_catalogo and 'personaliz' in producto_catalogo.lower():
            es_personalizacion = True
        
        # 3. Si tiene colores y tipo de arreglo pero no producto específico
        if colores_str and tipo_arreglo and not producto_catalogo:
            es_personalizacion = True
        
        # Si no es personalización, saltar
        if not es_personalizacion:
            continue
        
        # Buscar el pedido en la base de datos
        cursor.execute('''
            SELECT id FROM pedidos 
            WHERE numero_pedido = ? OR id = ?
        ''', (id_pedido, id_pedido))
        
        pedido_db = cursor.fetchone()
        
        if not pedido_db:
            continue
        
        pedido_id = pedido_db[0]
        
        # Preparar datos para actualizar
        colores_json = extraer_colores(colores_str)
        tipo_pers = tipo_producto or tipo_arreglo
        notas_pers = detalles_cliente
        
        # Actualizar el pedido
        updates = []
        values = []
        
        # Siempre marcar como producto personalización
        updates.append("producto_id = ?")
        values.append(producto_pers_id)
        
        if colores_json:
            updates.append("colores_solicitados = ?")
            values.append(colores_json)
            pedidos_con_colores += 1
        
        if tipo_pers:
            updates.append("tipo_personalizacion = ?")
            values.append(tipo_pers)
            pedidos_con_tipo += 1
        
        if notas_pers:
            updates.append("notas_personalizacion = ?")
            values.append(notas_pers)
            pedidos_con_notas += 1
        
        if updates:
            values.append(pedido_id)
            query = f'''
                UPDATE pedidos 
                SET {', '.join(updates)}
                WHERE id = ?
            '''
            cursor.execute(query, values)
            pedidos_actualizados += 1
            
            if pedidos_actualizados % 100 == 0:
                print(f"   Procesados: {pedidos_actualizados} pedidos...")

# Commit de cambios
conn.commit()

print("\n" + "=" * 80)
print("✅ ACTUALIZACIÓN COMPLETADA")
print("=" * 80)

print(f"\n📊 ESTADÍSTICAS:")
print(f"   • Total de pedidos en CSV: {pedidos_totales}")
print(f"   • Pedidos actualizados: {pedidos_actualizados}")
print(f"   • Con colores: {pedidos_con_colores}")
print(f"   • Con tipo: {pedidos_con_tipo}")
print(f"   • Con notas: {pedidos_con_notas}")

# Verificar resultado final
cursor.execute('''
    SELECT COUNT(*) FROM pedidos 
    WHERE producto_id = ?
''', (producto_pers_id,))

total_personalizaciones = cursor.fetchone()[0]

print(f"\n🎨 Total de personalizaciones en DB: {total_personalizaciones}")

# Ejemplos de colores más comunes
print("\n🎨 TOP 10 COLORES MÁS USADOS:")
cursor.execute('''
    SELECT colores_solicitados, COUNT(*) as cantidad
    FROM pedidos
    WHERE colores_solicitados IS NOT NULL
    GROUP BY colores_solicitados
    ORDER BY cantidad DESC
    LIMIT 10
''')

for i, (colores, cant) in enumerate(cursor.fetchall(), 1):
    try:
        colores_list = json.loads(colores)
        colores_str = ', '.join(colores_list[:3])  # Mostrar máximo 3 colores
        print(f"   {i}. {colores_str}: {cant} pedidos")
    except:
        pass

# Ejemplos de tipos más comunes
print("\n📦 TOP 10 TIPOS MÁS COMUNES:")
cursor.execute('''
    SELECT tipo_personalizacion, COUNT(*) as cantidad
    FROM pedidos
    WHERE tipo_personalizacion IS NOT NULL
    GROUP BY tipo_personalizacion
    ORDER BY cantidad DESC
    LIMIT 10
''')

for i, (tipo, cant) in enumerate(cursor.fetchall(), 1):
    print(f"   {i}. {tipo}: {cant} pedidos")

conn.close()

print("\n" + "=" * 80)
print("🎉 ¡LISTO! Datos de personalización cargados")
print("=" * 80)
print("\n🚀 Ahora puedes usar:")
print("   GET /api/analisis/personalizaciones")
print("   GET /api/analisis/personalizaciones/detalle")
print("\n")

