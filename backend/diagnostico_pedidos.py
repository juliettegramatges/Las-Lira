#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico para verificar estados de pedidos
"""

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from app import app
from extensions import db
from models.pedido import Pedido
from datetime import datetime, date

with app.app_context():
    print("=" * 80)
    print("🔍 DIAGNÓSTICO DE PEDIDOS")
    print("=" * 80)
    
    # Contar pedidos por estado
    print("\n📊 PEDIDOS POR ESTADO:")
    estados = db.session.query(Pedido.estado, db.func.count(Pedido.id)).group_by(Pedido.estado).all()
    
    for estado, count in sorted(estados, key=lambda x: x[1], reverse=True):
        print(f"   {estado}: {count:,} pedidos")
    
    # Total
    total = Pedido.query.count()
    print(f"\n   TOTAL: {total:,} pedidos")
    
    # Pedidos con fecha pasada
    hoy = date.today()
    print(f"\n📅 HOY: {hoy}")
    
    pasados = Pedido.query.filter(Pedido.fecha_entrega < datetime.combine(hoy, datetime.min.time())).count()
    print(f"\n   Pedidos con fecha pasada: {pasados:,}")
    
    # Pedidos archivados con fecha pasada
    archivados_pasados = Pedido.query.filter(
        Pedido.estado == 'Archivado',
        Pedido.fecha_entrega < datetime.combine(hoy, datetime.min.time())
    ).count()
    print(f"   Archivados con fecha pasada: {archivados_pasados:,}")
    
    # Pedidos despachados
    despachados = Pedido.query.filter_by(estado='Despachados').count()
    print(f"   Despachados: {despachados:,}")
    
    # Muestra de pedidos archivados (primeros 5)
    print("\n📦 MUESTRA DE PEDIDOS ARCHIVADOS (5 primeros):")
    archivados_muestra = Pedido.query.filter_by(estado='Archivado').order_by(Pedido.fecha_entrega.desc()).limit(5).all()
    
    for p in archivados_muestra:
        print(f"   - {p.numero_pedido or p.id}: {p.cliente_nombre} | {p.fecha_entrega.date()} | {p.estado}")
    
    print("\n" + "=" * 80)


