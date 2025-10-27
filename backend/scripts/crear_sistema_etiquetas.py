#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para crear sistema de etiquetas múltiples para clientes
"""

import sqlite3
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
db_path = backend_dir / 'instance' / 'laslira.db'

print("=" * 80)
print("🏷️  CREANDO SISTEMA DE ETIQUETAS PARA CLIENTES")
print("=" * 80)

if not db_path.exists():
    print(f"❌ ERROR: Base de datos no encontrada en {db_path}")
    exit(1)

print(f"\n📂 Conectando a: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # ========================================
    # 1. CREAR TABLA DE ETIQUETAS
    # ========================================
    print("\n🏷️  Creando tabla de etiquetas...")
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS etiquetas_cliente (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre VARCHAR(50) NOT NULL UNIQUE,
            categoria VARCHAR(50) NOT NULL,
            descripcion TEXT,
            color VARCHAR(20),
            icono VARCHAR(20),
            activa BOOLEAN DEFAULT 1,
            orden INTEGER DEFAULT 0,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    print("   ✓ Tabla 'etiquetas_cliente' creada")
    
    # ========================================
    # 2. CREAR TABLA DE RELACIÓN
    # ========================================
    print("\n🔗 Creando tabla de relación cliente-etiquetas...")
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cliente_etiquetas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id VARCHAR(10) NOT NULL,
            etiqueta_id INTEGER NOT NULL,
            fecha_asignacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            asignacion_automatica BOOLEAN DEFAULT 1,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
            FOREIGN KEY (etiqueta_id) REFERENCES etiquetas_cliente(id) ON DELETE CASCADE,
            UNIQUE(cliente_id, etiqueta_id)
        )
    ''')
    conn.commit()
    print("   ✓ Tabla 'cliente_etiquetas' creada")
    
    # ========================================
    # 3. INSERTAR ETIQUETAS PREDEFINIDAS
    # ========================================
    print("\n📝 Insertando etiquetas predefinidas...")
    
    etiquetas = [
        # FRECUENCIA
        ('Recurrente', 'Frecuencia', 'Compra 4+ veces al año', '#10B981', '🔄', 1),
        ('Esporádico', 'Frecuencia', 'Compra 1-3 veces al año', '#F59E0B', '📅', 2),
        ('Puntual', 'Frecuencia', 'Compra única', '#6B7280', '⚡', 3),
        
        # TIPO DE COMPRA
        ('Cliente de Eventos', 'Tipo', '>70% compras para eventos', '#8B5CF6', '🎉', 4),
        ('Cliente Individual', 'Tipo', '>70% compras personales', '#EC4899', '🌸', 5),
        ('Cliente Mixto', 'Tipo', 'Mezcla de eventos e individuales', '#3B82F6', '🎭', 6),
        
        # VALOR
        ('Alto Valor', 'Valor', 'Ticket promedio > $50,000', '#EF4444', '💎', 7),
        ('Valor Medio', 'Valor', 'Ticket $20,000-$50,000', '#F59E0B', '💰', 8),
        ('Valor Estándar', 'Valor', 'Ticket < $20,000', '#10B981', '🪙', 9),
        
        # COMPORTAMIENTO PAGO
        ('Cumplidor', 'Pago', 'Paga a tiempo (90%+)', '#10B981', '✅', 10),
        ('Con Retrasos', 'Pago', 'Retrasos ocasionales', '#F59E0B', '⚠️', 11),
        ('Moroso', 'Pago', 'Retrasos frecuentes', '#EF4444', '❌', 12),
        
        # CANAL
        ('Cliente Shopify', 'Canal', '>70% compras online', '#7C3AED', '🛒', 13),
        ('Cliente WhatsApp', 'Canal', '>70% compras por WhatsApp', '#10B981', '💬', 14),
        ('Multicanal', 'Canal', 'Usa varios canales', '#3B82F6', '🔀', 15),
        
        # SEGMENTO
        ('Corporativo', 'Segmento', 'Compras empresariales', '#1F2937', '🏢', 16),
        ('Personal', 'Segmento', 'Compras personales', '#EC4899', '👤', 17),
        ('Novias', 'Segmento', 'Cliente de matrimonios', '#FDE68A', '💍', 18),
        ('Funerales', 'Segmento', 'Cliente de servicios fúnebres', '#6B7280', '🕊️', 19),
    ]
    
    for nombre, categoria, desc, color, icono, orden in etiquetas:
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO etiquetas_cliente 
                (nombre, categoria, descripcion, color, icono, orden)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (nombre, categoria, desc, color, icono, orden))
        except Exception as e:
            print(f"   ⚠️  Error insertando {nombre}: {e}")
    
    conn.commit()
    
    # Contar etiquetas insertadas
    cursor.execute('SELECT COUNT(*) FROM etiquetas_cliente')
    total_etiquetas = cursor.fetchone()[0]
    print(f"   ✓ {total_etiquetas} etiquetas disponibles")
    
    # ========================================
    # 4. RESUMEN POR CATEGORÍA
    # ========================================
    print("\n📊 ETIQUETAS POR CATEGORÍA:\n")
    
    cursor.execute('''
        SELECT categoria, COUNT(*) as cantidad
        FROM etiquetas_cliente
        WHERE activa = 1
        GROUP BY categoria
        ORDER BY MIN(orden)
    ''')
    
    for categoria, cantidad in cursor.fetchall():
        cursor.execute('''
            SELECT nombre, icono, descripcion
            FROM etiquetas_cliente
            WHERE categoria = ? AND activa = 1
            ORDER BY orden
        ''', (categoria,))
        
        print(f"🏷️  {categoria.upper()}:")
        for nombre, icono, desc in cursor.fetchall():
            print(f"   {icono} {nombre}: {desc}")
        print()
    
    print("=" * 80)
    print("✅ SISTEMA DE ETIQUETAS CREADO")
    print("=" * 80)
    
    print("\n📌 PRÓXIMO PASO:")
    print("   Ejecuta: python3 backend/scripts/clasificar_clientes.py")
    print("   Para clasificar automáticamente a todos los clientes")
    
    conn.close()
    print("\n✅ Script finalizado\n")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    conn.rollback()
    conn.close()
    exit(1)

