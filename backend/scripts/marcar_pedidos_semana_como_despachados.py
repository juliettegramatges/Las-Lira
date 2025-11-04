#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para marcar todos los pedidos en "Pedidos Semana" como "Despachados"
"""

import sys
import os

# Agregar el directorio del backend al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extensions import db
from models.pedido import Pedido

def marcar_como_despachados():
    """Marca todos los pedidos en estado 'Pedidos Semana' como 'Despachados'"""
    
    print("=" * 80)
    print("🔄 MARCANDO PEDIDOS SEMANA COMO DESPACHADOS")
    print("=" * 80)
    
    # Contar pedidos antes
    total_pedidos_semana = Pedido.query.filter_by(estado='Pedidos Semana').count()
    print(f"\n📊 Pedidos en 'Pedidos Semana': {total_pedidos_semana}")
    
    if total_pedidos_semana == 0:
        print("\n✅ No hay pedidos para actualizar")
        return
    
    # Confirmar (o usar --force para saltar confirmación)
    import sys
    force = '--force' in sys.argv or '-f' in sys.argv
    if not force:
        respuesta = input(f"\n⚠️  ¿Deseas marcar {total_pedidos_semana} pedidos como 'Despachados'? (s/n): ")
        if respuesta.lower() != 's':
            print("\n❌ Operación cancelada")
            return
    else:
        print(f"\n⚠️  Ejecutando en modo FORCE (sin confirmación)")
    
    # Actualizar
    try:
        pedidos_actualizados = Pedido.query.filter_by(estado='Pedidos Semana').update({
            'estado': 'Despachados'
        })
        
        db.session.commit()
        
        print(f"\n✅ {pedidos_actualizados} pedidos actualizados a 'Despachados'")
        print("\n" + "=" * 80)
        
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Error al actualizar: {str(e)}")
        print("\n" + "=" * 80)
        raise

if __name__ == '__main__':
    from app import app
    with app.app_context():
        marcar_como_despachados()

