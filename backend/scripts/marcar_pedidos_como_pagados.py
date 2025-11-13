#!/usr/bin/env python3
"""
Script para marcar todos los pedidos como pagados y con documento emitido,
excepto los dos últimos pedidos creados.
"""

import sys
import os

# Agregar el directorio backend al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from extensions import db
from models.pedido import Pedido
from datetime import datetime

def main():
    with app.app_context():
        # Obtener los dos últimos pedidos (por ID, que es autoincremental)
        ultimos_pedidos = Pedido.query.order_by(Pedido.id.desc()).limit(2).all()
        ids_excluir = [p.id for p in ultimos_pedidos]
        
        print(f"📋 Excluyendo los siguientes pedidos del proceso:")
        for p in ultimos_pedidos:
            print(f"   - ID: {p.id}, Número: {p.numero_pedido or 'N/A'}, Fecha: {p.fecha_pedido}")
        
        # Contar pedidos a actualizar
        total_pedidos = Pedido.query.filter(
            Pedido.id.notin_(ids_excluir),
            Pedido.estado != 'Cancelado'
        ).count()
        
        print(f"\n🔄 Actualizando {total_pedidos} pedidos...")
        
        # Actualizar todos los pedidos excepto los dos últimos
        pedidos_actualizados = Pedido.query.filter(
            Pedido.id.notin_(ids_excluir),
            Pedido.estado != 'Cancelado'
        ).all()
        
        actualizados = 0
        for pedido in pedidos_actualizados:
            # Marcar como pagado si no está pagado
            if pedido.estado_pago != 'Pagado':
                pedido.estado_pago = 'Pagado'
                actualizados += 1
            
            # Marcar documento como emitido si no está emitido
            # Si no tiene método de pago, asignar uno por defecto
            if not pedido.metodo_pago or pedido.metodo_pago == 'Pendiente':
                # Si es BICE, no necesita documento, pero igual lo marcamos como pagado
                if 'BICE' not in (pedido.metodo_pago or ''):
                    pedido.metodo_pago = 'Tr. BICE'  # Asignar BICE por defecto para evitar documentos
            
            # Actualizar documento tributario
            if pedido.documento_tributario in ['Hacer boleta', 'Hacer factura', 'Falta boleta o factura', None]:
                # Si es BICE, no requiere documento
                if pedido.metodo_pago and 'BICE' in pedido.metodo_pago:
                    pedido.documento_tributario = 'No requiere'
                else:
                    # Marcar como boleta emitida por defecto
                    pedido.documento_tributario = 'Boleta emitida'
                    # Si no tiene número de documento, asignar uno genérico
                    if not pedido.numero_documento:
                        pedido.numero_documento = f"BOL-{pedido.id}"
        
        try:
            db.session.commit()
            print(f"✅ {actualizados} pedidos actualizados como pagados")
            print(f"✅ Todos los pedidos (excepto los 2 últimos) marcados con documento emitido")
            print(f"\n📊 Resumen:")
            print(f"   - Total pedidos procesados: {len(pedidos_actualizados)}")
            print(f"   - Pedidos excluidos: {len(ids_excluir)}")
            print(f"   - Pedidos actualizados: {actualizados}")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al actualizar: {str(e)}")
            return 1
    
    return 0

if __name__ == '__main__':
    exit(main())

