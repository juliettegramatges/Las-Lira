#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para identificar y marcar eventos desde CSVs de Trello
"""

import csv
import sqlite3
from pathlib import Path
import re

backend_dir = Path(__file__).resolve().parent.parent
base_dir = backend_dir.parent
db_path = backend_dir / 'instance' / 'laslira.db'

# CSVs
pedidos_csv = base_dir / 'pedidos_trello_COMPLETO.csv'
eventos_csv = base_dir / 'eventos_trello.csv'

print("=" * 80)
print("🎉 IDENTIFICANDO Y MARCANDO EVENTOS")
print("=" * 80)

if not db_path.exists():
    print(f"❌ ERROR: Base de datos no encontrada")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Estadísticas
eventos_marcados = 0
pedidos_actualizados = 0

# Mapeo de patrones a tipos de evento
PATRONES_EVENTOS = {
    'Matrimonio': [
        'matrimonio', 'boda', 'nupcial', 'novia', 'novio', 'casamiento',
        'enlace', 'wedding', 'bride', 'groom'
    ],
    'Funeral': [
        'funeral', 'difunto', 'difunta', 'fallecido', 'fallecida',
        'velorio', 'sepelio', 'condolencia', 'pésame', 'urna',
        'cementerio', 'duelo', 'luto'
    ],
    'Cumpleaños': [
        'cumpleaños', 'cumple', 'birthday', 'aniversario nacimiento',
        'celebración edad', 'feliz cumpleaños'
    ],
    'Aniversario': [
        'aniversario', 'anniversary', 'años de matrimonio',
        'bodas de', 'celebración anual'
    ],
    'Bautizo': [
        'bautizo', 'bautismo', 'baptism', 'christening',
        'sacramento bautismal'
    ],
    'Primera Comunión': [
        'primera comunión', 'comunión', 'first communion',
        'confirmación', 'sacramento'
    ],
    'Corporativo': [
        'corporativo', 'empresa', 'corporate', 'oficina',
        'compañía', 'negocio', 'inauguración empresa',
        'evento empresarial', 'cliente corporativo'
    ],
    'Inauguración': [
        'inauguración', 'opening', 'apertura', 'estreno',
        'lanzamiento', 'gran apertura'
    ],
    'Graduación': [
        'graduación', 'graduation', 'titulación', 'egreso',
        'licenciatura', 'grado'
    ],
    'Nacimiento': [
        'nacimiento', 'baby shower', 'nació', 'bebé',
        'recién nacido', 'maternidad', 'parto'
    ],
    'Otro': [
        'evento', 'celebración', 'fiesta', 'party',
        'celebration', 'agasajo'
    ]
}

# Patrones específicos en tipo_producto que indican evento
TIPOS_EVENTO = {
    'MATRIMONIO': 'Matrimonio',
    'DIFUNTO': 'Funeral',
    'CENTRO DE MESA': 'Otro',  # Puede ser cualquier evento
    'NACIMIENTO': 'Nacimiento',
    'CORONA': 'Funeral',
    'FUNERAL': 'Funeral',
    'CUMPLEAÑOS': 'Cumpleaños',
    'BAUTIZO': 'Bautizo',
    'COMUNION': 'Primera Comunión',
    'PRIMERA COMUNION': 'Primera Comunión',
    'GRADUACION': 'Graduación',
    'CORPORATIVO': 'Corporativo',
    'INAUGURACION': 'Inauguración',
}

def limpiar_texto(texto):
    """Limpia y normaliza texto"""
    if not texto or str(texto).strip() in ['', 'nan', 'None', 'NULL']:
        return ''
    return str(texto).strip().lower()

def detectar_tipo_evento(texto_completo):
    """Detecta el tipo de evento basado en patrones - SOLO eventos verdaderos"""
    texto = limpiar_texto(texto_completo)
    
    if not texto:
        return None
    
    # Solo considerar como eventos verdaderos:
    # 1. Funerales/Difuntos
    # 2. Matrimonios/Bodas
    # 3. Corporativos
    
    # Prioridad: Funerales y Matrimonios
    for tipo in ['Funeral', 'Matrimonio']:
        for patron in PATRONES_EVENTOS[tipo]:
            if patron in texto:
                return tipo
    
    # Corporativo
    for patron in PATRONES_EVENTOS['Corporativo']:
        if patron in texto:
            return 'Corporativo'
    
    # NO considerar cumpleaños, aniversarios, nacimientos, etc. como eventos
    return None

print("\n📊 PASO 1: Procesando eventos_trello.csv...")

if eventos_csv.exists():
    with open(eventos_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        eventos_explícitos = 0
        
        for row in reader:
            cliente = limpiar_texto(row.get('cliente', ''))
            producto = limpiar_texto(row.get('producto', ''))
            detalles = limpiar_texto(row.get('detalles_cliente', ''))
            para = limpiar_texto(row.get('para', ''))
            
            # Texto completo para análisis
            texto_completo = f"{cliente} {producto} {detalles} {para}"
            
            # Detectar tipo de evento
            tipo_evento = detectar_tipo_evento(texto_completo)
            
            if tipo_evento:
                eventos_explícitos += 1
                
                # Buscar pedidos de este cliente en fechas similares
                fecha_entrega = row.get('fecha_entrega', '')
                
                if fecha_entrega and cliente:
                    cursor.execute('''
                        UPDATE pedidos
                        SET es_evento = 1,
                            tipo_evento = ?
                        WHERE cliente_nombre LIKE ?
                          AND date(fecha_entrega) = date(?)
                          AND (es_evento IS NULL OR es_evento = 0)
                    ''', (tipo_evento, f'%{cliente}%', fecha_entrega))
                    
                    if cursor.rowcount > 0:
                        eventos_marcados += cursor.rowcount
        
        print(f"   ✓ Eventos explícitos procesados: {eventos_explícitos}")
        print(f"   ✓ Pedidos marcados desde eventos.csv: {eventos_marcados}")
else:
    print("   ⚠️  eventos_trello.csv no encontrado, saltando...")

print("\n📊 PASO 2: Analizando pedidos_trello_COMPLETO.csv...")

with open(pedidos_csv, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    pedidos_analizados = 0
    
    for row in reader:
        pedidos_analizados += 1
        
        id_pedido = row.get('id_pedido', '').strip()
        tipo_producto = limpiar_texto(row.get('tipo_producto', ''))
        motivo = limpiar_texto(row.get('motivo', ''))
        motivo_pedido = limpiar_texto(row.get('motivo_pedido', ''))
        producto = limpiar_texto(row.get('producto', ''))
        detalles = limpiar_texto(row.get('detalles_cliente', ''))
        para = limpiar_texto(row.get('para', ''))
        
        if not id_pedido:
            continue
        
        # Verificar si ya está marcado
        cursor.execute('''
            SELECT es_evento FROM pedidos
            WHERE numero_pedido = ? OR id = ?
        ''', (id_pedido, id_pedido))
        
        result = cursor.fetchone()
        if not result:
            continue
        
        ya_marcado = result[0]
        if ya_marcado:
            continue  # Ya está marcado, saltar
        
        # Detectar evento - SOLO verdaderos eventos
        es_evento = False
        tipo_evento_detectado = None
        
        # Solo eventos verdaderos: Funeral, Matrimonio, Corporativo
        TIPOS_EVENTO_VALIDOS = {
            'MATRIMONIO': 'Matrimonio',
            'DIFUNTO': 'Funeral',
            'CORONA': 'Funeral',
            'FUNERAL': 'Funeral',
            'CORPORATIVO': 'Corporativo',
        }
        
        # 1. Por tipo_producto exacto
        for clave, tipo in TIPOS_EVENTO_VALIDOS.items():
            if clave in tipo_producto:
                es_evento = True
                tipo_evento_detectado = tipo
                break
        
        # 2. Por patrones en texto completo
        if not es_evento:
            texto_completo = f"{tipo_producto} {motivo} {motivo_pedido} {producto} {detalles} {para}"
            tipo_evento_detectado = detectar_tipo_evento(texto_completo)
            es_evento = tipo_evento_detectado is not None
        
        # NO marcar centros de mesa automáticamente como evento
        # Solo si tiene palabras clave de eventos verdaderos
        
        # Actualizar si es evento
        if es_evento and tipo_evento_detectado:
            cursor.execute('''
                UPDATE pedidos
                SET es_evento = 1,
                    tipo_evento = ?
                WHERE (numero_pedido = ? OR id = ?)
                  AND (es_evento IS NULL OR es_evento = 0)
            ''', (tipo_evento_detectado, id_pedido, id_pedido))
            
            if cursor.rowcount > 0:
                pedidos_actualizados += 1
        
        if pedidos_analizados % 1000 == 0:
            print(f"   Analizados: {pedidos_analizados} pedidos...")
            conn.commit()

# Commit final
conn.commit()

print(f"\n   ✓ Total pedidos analizados: {pedidos_analizados}")
print(f"   ✓ Pedidos marcados como evento: {pedidos_actualizados}")

# Estadísticas finales
print("\n" + "=" * 80)
print("✅ ANÁLISIS COMPLETADO")
print("=" * 80)

cursor.execute('SELECT COUNT(*) FROM pedidos WHERE es_evento = 1')
total_eventos = cursor.fetchone()[0]

print(f"\n🎉 TOTAL DE EVENTOS EN BASE DE DATOS: {total_eventos}")

print("\n📊 DISTRIBUCIÓN POR TIPO DE EVENTO:\n")
cursor.execute('''
    SELECT tipo_evento, COUNT(*) as cantidad
    FROM pedidos
    WHERE es_evento = 1
    GROUP BY tipo_evento
    ORDER BY cantidad DESC
''')

for tipo, cantidad in cursor.fetchall():
    print(f"   🎭 {tipo or 'Sin especificar'}: {cantidad} pedidos")

conn.close()

print("\n" + "=" * 80)
print("🎯 PRÓXIMO PASO:")
print("   Ejecuta: python3 backend/scripts/clasificar_clientes.py")
print("   Para reclasificar clientes con eventos")
print("=" * 80)
print("\n")

