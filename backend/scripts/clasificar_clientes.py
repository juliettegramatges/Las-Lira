#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para clasificar automáticamente clientes con etiquetas múltiples
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

backend_dir = Path(__file__).resolve().parent.parent
db_path = backend_dir / 'instance' / 'laslira.db'

print("=" * 80)
print("🤖 CLASIFICACIÓN AUTOMÁTICA DE CLIENTES")
print("=" * 80)

if not db_path.exists():
    print(f"❌ ERROR: Base de datos no encontrada en {db_path}")
    exit(1)

print(f"\n📂 Conectando a: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

def asignar_etiqueta(cursor, cliente_id, etiqueta_nombre, etiquetas_map):
    """Asigna una etiqueta a un cliente"""
    if etiqueta_nombre not in etiquetas_map:
        return 0
    
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO cliente_etiquetas 
            (cliente_id, etiqueta_id, asignacion_automatica)
            VALUES (?, ?, 1)
        ''', (cliente_id, etiquetas_map[etiqueta_nombre]))
        return 1 if cursor.rowcount > 0 else 0
    except:
        return 0

# Obtener IDs de etiquetas
etiquetas_map = {}
cursor.execute('SELECT id, nombre FROM etiquetas_cliente WHERE activa = 1')
for etiq_id, nombre in cursor.fetchall():
    etiquetas_map[nombre] = etiq_id

print(f"✓ {len(etiquetas_map)} etiquetas cargadas")

# Limpiar asignaciones automáticas anteriores
cursor.execute('DELETE FROM cliente_etiquetas WHERE asignacion_automatica = 1')
conn.commit()
print("✓ Asignaciones anteriores eliminadas")

# Obtener todos los clientes
cursor.execute('SELECT id FROM clientes')
clientes = [row[0] for row in cursor.fetchall()]

print(f"\n📊 Clasificando {len(clientes)} clientes...")

clasificados = 0
etiquetas_asignadas = 0

for cliente_id in clientes:
    # ========================================
    # OBTENER DATOS DEL CLIENTE
    # ========================================
    
    # Total de pedidos
    cursor.execute('''
        SELECT COUNT(*), 
               AVG(precio_ramo + precio_envio),
               SUM(precio_ramo + precio_envio),
               MIN(fecha_pedido),
               MAX(fecha_pedido)
        FROM pedidos
        WHERE cliente_id = ?
    ''', (cliente_id,))
    
    result = cursor.fetchone()
    if not result or result[0] == 0:
        continue
    
    total_pedidos, ticket_promedio, gasto_total, primera_compra, ultima_compra = result
    ticket_promedio = float(ticket_promedio or 0)
    gasto_total = float(gasto_total or 0)
    
    # Pedidos de eventos
    cursor.execute('''
        SELECT COUNT(*) FROM pedidos
        WHERE cliente_id = ? AND es_evento = 1
    ''', (cliente_id,))
    pedidos_eventos = cursor.fetchone()[0]
    
    # Canales usados
    cursor.execute('''
        SELECT canal, COUNT(*) as cantidad
        FROM pedidos
        WHERE cliente_id = ?
        GROUP BY canal
        ORDER BY cantidad DESC
    ''', (cliente_id,))
    canales = cursor.fetchall()
    total_canales = len(canales)
    canal_principal = canales[0][0] if canales else None
    porcentaje_canal_principal = (canales[0][1] / total_pedidos * 100) if canales else 0
    
    # Estado de pago
    cursor.execute('''
        SELECT 
            SUM(CASE WHEN estado_pago = 'Pagado' THEN 1 ELSE 0 END) as pagados,
            COUNT(*) as total
        FROM pedidos
        WHERE cliente_id = ?
    ''', (cliente_id,))
    pagados, total_con_pago = cursor.fetchone()
    porcentaje_pago = (pagados / total_con_pago * 100) if total_con_pago > 0 else 100
    
    # Tipos de evento
    cursor.execute('''
        SELECT tipo_evento, COUNT(*) as cantidad
        FROM pedidos
        WHERE cliente_id = ? AND tipo_evento IS NOT NULL
        GROUP BY tipo_evento
        ORDER BY cantidad DESC
        LIMIT 1
    ''', (cliente_id,))
    evento_principal = cursor.fetchone()
    
    # ========================================
    # CLASIFICAR POR FRECUENCIA
    # ========================================
    if total_pedidos >= 4:
        etiquetas_asignadas += asignar_etiqueta(cursor, cliente_id, 'Recurrente', etiquetas_map)
    elif total_pedidos >= 2:
        etiquetas_asignadas += asignar_etiqueta(cursor, cliente_id, 'Esporádico', etiquetas_map)
    else:
        etiquetas_asignadas += asignar_etiqueta(cursor, cliente_id, 'Puntual', etiquetas_map)
    
    # ========================================
    # CLASIFICAR POR TIPO DE COMPRA
    # ========================================
    porcentaje_eventos = (pedidos_eventos / total_pedidos * 100) if total_pedidos > 0 else 0
    
    if porcentaje_eventos > 70:
        etiquetas_asignadas += asignar_etiqueta(cursor, cliente_id, 'Cliente de Eventos', etiquetas_map)
    elif porcentaje_eventos < 30:
        etiquetas_asignadas += asignar_etiqueta(cursor, cliente_id, 'Cliente Individual', etiquetas_map)
    else:
        etiquetas_asignadas += asignar_etiqueta(cursor, cliente_id, 'Cliente Mixto', etiquetas_map)
    
    # ========================================
    # CLASIFICAR POR VALOR
    # ========================================
    # Alto Valor: muchos pedidos + ticket alto
    if total_pedidos >= 3 and ticket_promedio >= 150000:
        etiquetas_asignadas += asignar_etiqueta(cursor, cliente_id, 'Alto Valor', etiquetas_map)
    elif ticket_promedio >= 80000:
        etiquetas_asignadas += asignar_etiqueta(cursor, cliente_id, 'Valor Medio', etiquetas_map)
    else:
        etiquetas_asignadas += asignar_etiqueta(cursor, cliente_id, 'Valor Estándar', etiquetas_map)
    
    # ========================================
    # CLASIFICAR POR COMPORTAMIENTO DE PAGO
    # ========================================
    if porcentaje_pago >= 90:
        etiquetas_asignadas += asignar_etiqueta(cursor, cliente_id, 'Cumplidor', etiquetas_map)
    elif porcentaje_pago >= 50:
        etiquetas_asignadas += asignar_etiqueta(cursor, cliente_id, 'Con Retrasos', etiquetas_map)
    else:
        etiquetas_asignadas += asignar_etiqueta(cursor, cliente_id, 'Moroso', etiquetas_map)
    
    # ========================================
    # CLASIFICAR POR CANAL
    # ========================================
    if canal_principal and porcentaje_canal_principal > 70:
        if 'shopify' in canal_principal.lower() or 'online' in canal_principal.lower():
            etiquetas_asignadas += asignar_etiqueta(cursor, cliente_id, 'Cliente Shopify', etiquetas_map)
        elif 'whatsapp' in canal_principal.lower() or 'wa' in canal_principal.lower():
            etiquetas_asignadas += asignar_etiqueta(cursor, cliente_id, 'Cliente WhatsApp', etiquetas_map)
    
    if total_canales >= 2:
        etiquetas_asignadas += asignar_etiqueta(cursor, cliente_id, 'Multicanal', etiquetas_map)
    
    # ========================================
    # CLASIFICAR POR SEGMENTO
    # ========================================
    
    # Buscar patrones en nombres/descripciones
    cursor.execute('''
        SELECT arreglo_pedido, detalles_adicionales, tipo_evento
        FROM pedidos
        WHERE cliente_id = ?
    ''', (cliente_id,))
    
    textos = ' '.join([str(t).lower() for row in cursor.fetchall() for t in row if t])
    
    # Corporativo: términos empresariales
    if any(term in textos for term in ['empresa', 'corporativo', 'oficina', 'compañía', 'negocio']):
        etiquetas_asignadas += asignar_etiqueta(cursor, cliente_id, 'Corporativo', etiquetas_map)
    
    # Novias: matrimonios frecuentes
    if pedidos_eventos > 0 and evento_principal:
        tipo_evento = evento_principal[0].lower() if evento_principal[0] else ''
        if 'matrimonio' in tipo_evento or 'boda' in tipo_evento:
            etiquetas_asignadas += asignar_etiqueta(cursor, cliente_id, 'Novias', etiquetas_map)
        elif 'funeral' in tipo_evento or 'difunto' in tipo_evento:
            etiquetas_asignadas += asignar_etiqueta(cursor, cliente_id, 'Funerales', etiquetas_map)
    
    # Si no es corporativo ni eventos especiales, es personal
    cursor.execute('''
        SELECT COUNT(*) FROM cliente_etiquetas ce
        JOIN etiquetas_cliente e ON e.id = ce.etiqueta_id
        WHERE ce.cliente_id = ? 
          AND e.categoria = 'Segmento'
    ''', (cliente_id,))
    
    if cursor.fetchone()[0] == 0:
        etiquetas_asignadas += asignar_etiqueta(cursor, cliente_id, 'Personal', etiquetas_map)
    
    clasificados += 1
    
    if clasificados % 100 == 0:
        conn.commit()
        print(f"   Procesados: {clasificados} clientes...")

# Commit final
conn.commit()

print("\n" + "=" * 80)
print("✅ CLASIFICACIÓN COMPLETADA")
print("=" * 80)

print(f"\n📊 RESULTADOS:")
print(f"   • Clientes clasificados: {clasificados}")
print(f"   • Etiquetas asignadas: {etiquetas_asignadas}")
print(f"   • Promedio etiquetas por cliente: {etiquetas_asignadas / clasificados:.1f}")

# Estadísticas por etiqueta
print("\n🏷️  DISTRIBUCIÓN POR ETIQUETA:\n")

cursor.execute('''
    SELECT e.categoria, e.nombre, e.icono, COUNT(ce.cliente_id) as cantidad
    FROM etiquetas_cliente e
    LEFT JOIN cliente_etiquetas ce ON ce.etiqueta_id = e.id
    WHERE e.activa = 1
    GROUP BY e.id
    ORDER BY e.orden
''')

categoria_actual = None
for categoria, nombre, icono, cantidad in cursor.fetchall():
    if categoria != categoria_actual:
        print(f"\n📌 {categoria.upper()}:")
        categoria_actual = categoria
    print(f"   {icono} {nombre}: {cantidad} clientes")

conn.close()

print("\n" + "=" * 80)
print("🎉 ¡CLASIFICACIÓN FINALIZADA!")
print("=" * 80)
print("\n📖 Ahora los clientes tienen etiquetas múltiples que reflejan:")
print("   • Su frecuencia de compra")
print("   • Tipo de compras (eventos vs individuales)")
print("   • Nivel de gasto")
print("   • Comportamiento de pago")
print("   • Canal preferido")
print("   • Segmento (corporativo, personal, novias, etc.)")
print("\n")

