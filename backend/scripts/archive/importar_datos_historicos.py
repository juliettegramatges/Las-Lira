#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para importar datos históricos de Trello al sistema web
"""

import sys
import os
from pathlib import Path

# Agregar el directorio backend al path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app import app
from extensions import db
from models.cliente import Cliente
from models.pedido import Pedido, PedidoInsumo
from models.producto import Producto
from models.inventario import Flor, Contenedor

import csv
from datetime import datetime
from decimal import Decimal
import re

# Rutas de los archivos CSV
BASE_DIR = backend_dir.parent
CLIENTES_CSV = BASE_DIR / 'base_clientes_completa.csv'
PEDIDOS_CSV = BASE_DIR / 'pedidos_trello_COMPLETO.csv'
PRODUCTOS_CSV = BASE_DIR / 'catalogo_productos_completo.csv'
INSUMOS_CSV = BASE_DIR / 'insumos_las_lira.csv'

def parse_decimal(value_str):
    """Convierte string de precio a Decimal"""
    if not value_str or value_str in ['', 'nan', 'None', 'Variable']:
        return Decimal('0')
    # Remover símbolos y espacios
    value_str = str(value_str).replace('$', '').replace('.', '').replace(',', '.').strip()
    try:
        return Decimal(value_str)
    except:
        return Decimal('0')

def parse_fecha(fecha_str, formato='%Y-%m-%d'):
    """Convierte string de fecha a datetime"""
    if not fecha_str or fecha_str in ['', 'nan', 'None']:
        return None
    try:
        return datetime.strptime(fecha_str, formato)
    except:
        try:
            # Intentar formato alternativo
            return datetime.strptime(fecha_str, '%d/%m/%Y')
        except:
            return None

def limpiar_string(value):
    """Limpia y normaliza strings"""
    if not value or value in ['', 'nan', 'None', 'null']:
        return None
    return str(value).strip()

def generar_id_unico(base, existentes):
    """Genera un ID único"""
    contador = 1
    while True:
        nuevo_id = f"{base}{contador:04d}"
        if nuevo_id not in existentes:
            return nuevo_id
        contador += 1

print("=" * 80)
print("🚀 IMPORTACIÓN DE DATOS HISTÓRICOS AL SISTEMA WEB")
print("=" * 80)

with app.app_context():
    # 1. Limpiar tablas existentes (opcional - comentar si no quieres limpiar)
    print("\n⚠️  Limpiando tablas existentes...")
    PedidoInsumo.query.delete()
    Pedido.query.delete()
    Cliente.query.delete()
    # No limpiar Producto ni inventario si ya están cargados
    # Producto.query.delete()
    # Flor.query.delete()
    # Contenedor.query.delete()
    db.session.commit()
    print("   ✅ Tablas limpiadas")
    
    # 2. IMPORTAR CLIENTES
    print("\n" + "=" * 80)
    print("👥 IMPORTANDO CLIENTES")
    print("=" * 80)
    
    clientes_importados = 0
    clientes_errores = 0
    clientes_map = {}  # Mapeo de nombre -> id de cliente
    
    with open(CLIENTES_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # Mapear segmento a tipo_cliente
                segmento = row.get('segmento', 'Regular')
                tipo_cliente_map = {
                    'VIP': 'VIP',
                    'Premium': 'Fiel',
                    'Regular': 'Ocasional',
                    'Nuevo': 'Nuevo',
                    'Inactivo': 'Ocasional'
                }
                tipo_cliente = tipo_cliente_map.get(segmento, 'Ocasional')
                
                # Obtener contacto y correo
                contactos = limpiar_string(row.get('contacto', ''))
                primer_contacto = contactos.split(',')[0].strip() if contactos else None
                
                if not primer_contacto:
                    primer_contacto = f"SIN_TEL_{clientes_importados:04d}"
                
                correos = limpiar_string(row.get('correo', ''))
                primer_correo = correos.split(',')[0].strip() if correos else None
                
                cliente = Cliente(
                    id=row['id_cliente'],
                    nombre=limpiar_string(row['nombre']) or 'Sin nombre',
                    telefono=primer_contacto,
                    email=primer_correo,
                    tipo_cliente=tipo_cliente,
                    direccion_principal=limpiar_string(row.get('direcciones', '')),
                    total_pedidos=int(row.get('total_pedidos', 0)),
                    total_gastado=parse_decimal(row.get('total_gastado', '0')),
                    fecha_registro=parse_fecha(row.get('fecha_primer_pedido', '')) or datetime.now(),
                    ultima_compra=parse_fecha(row.get('fecha_ultimo_pedido', ''))
                )
                
                db.session.add(cliente)
                clientes_map[cliente.nombre.upper()] = cliente.id
                clientes_importados += 1
                
                if clientes_importados % 100 == 0:
                    print(f"   Procesados: {clientes_importados} clientes...")
                    db.session.commit()
            
            except Exception as e:
                clientes_errores += 1
                print(f"   ❌ Error al importar cliente: {e}")
                continue
    
    db.session.commit()
    print(f"\n   ✅ Clientes importados: {clientes_importados}")
    print(f"   ❌ Errores: {clientes_errores}")
    
    # 3. IMPORTAR PEDIDOS
    print("\n" + "=" * 80)
    print("📦 IMPORTANDO PEDIDOS")
    print("=" * 80)
    
    pedidos_importados = 0
    pedidos_errores = 0
    
    with open(PEDIDOS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # Buscar cliente
                nombre_cliente = limpiar_string(row.get('cliente', ''))
                cliente_id = None
                if nombre_cliente:
                    cliente_id = clientes_map.get(nombre_cliente.upper())
                
                # Canal
                canal_raw = limpiar_string(row.get('canal', 'WhatsApp'))
                canal = 'Shopify' if canal_raw and 'shopify' in canal_raw.lower() else 'WhatsApp'
                
                # Estado del pedido
                estado_pedido = limpiar_string(row.get('estado_pedido', 'ARCHIVADO'))
                estado_map = {
                    'ARCHIVADO': 'Archivado',
                    'ACTIVO': 'Pedidos Semana'
                }
                estado = estado_map.get(estado_pedido, 'Archivado')
                
                # Estado de pago
                estado_pago_raw = limpiar_string(row.get('estado_pago', 'PAGADO'))
                estado_pago_map = {
                    'PAGADO': 'Pagado',
                    'PENDIENTE': 'No Pagado'
                }
                estado_pago = estado_pago_map.get(estado_pago_raw, 'Pagado')
                
                # Tipo de entrega
                tipo_entrega = limpiar_string(row.get('tipo_entrega', ''))
                direccion = limpiar_string(row.get('direccion', ''))
                if tipo_entrega == 'RETIRO' or (direccion and 'RETIRO' in direccion.upper()):
                    direccion = 'RETIRO EN TIENDA'
                elif not direccion:
                    direccion = 'Sin dirección'
                
                pedido = Pedido(
                    numero_pedido=row.get('id_pedido'),  # ID de referencia (puede repetirse)
                    fecha_pedido=parse_fecha(row.get('fecha_creacion', '')) or datetime.now(),
                    fecha_entrega=parse_fecha(row.get('fecha_entrega', '')) or datetime.now(),
                    canal=canal,
                    shopify_order_number=limpiar_string(row.get('n_pedido', '')),
                    cliente_id=cliente_id,
                    cliente_nombre=nombre_cliente or 'Cliente sin nombre',
                    cliente_telefono=limpiar_string(row.get('contacto', '')) or 'Sin teléfono',
                    cliente_email=limpiar_string(row.get('correo_cliente', '')),
                    # producto_id se asignará después si existe en la tabla productos
                    arreglo_pedido=limpiar_string(row.get('producto_catalogo', '')) or limpiar_string(row.get('producto', '')),
                    detalles_adicionales=limpiar_string(row.get('detalles_cliente', '')),
                    precio_ramo=parse_decimal(row.get('precio', '0')),
                    precio_envio=parse_decimal(row.get('envio', '0')),
                    destinatario=limpiar_string(row.get('para', '')),
                    mensaje=limpiar_string(row.get('mensaje', '')),
                    firma=limpiar_string(row.get('firma', '')),
                    direccion_entrega=direccion,
                    comuna=limpiar_string(row.get('comuna', '')),
                    motivo=limpiar_string(row.get('motivo_pedido', '')),
                    estado=estado,
                    estado_pago=estado_pago,
                    tipo_pedido=limpiar_string(row.get('tipo_producto', '')),
                    cobranza=limpiar_string(row.get('notas_cobranza', '')),
                    metodo_pago=limpiar_string(row.get('metodo_pago', 'Pendiente')),
                    documento_tributario=limpiar_string(row.get('tipo_documento', 'No requiere')),
                )
                
                db.session.add(pedido)
                pedidos_importados += 1
                
                if pedidos_importados % 500 == 0:
                    print(f"   Procesados: {pedidos_importados} pedidos...")
                    db.session.commit()
            
            except Exception as e:
                pedidos_errores += 1
                if pedidos_errores <= 10:  # Mostrar solo los primeros 10 errores
                    print(f"   ❌ Error al importar pedido {row.get('id_pedido', 'ID desconocido')}: {e}")
                continue
    
    db.session.commit()
    print(f"\n   ✅ Pedidos importados: {pedidos_importados}")
    print(f"   ❌ Errores: {pedidos_errores}")
    
    # 4. RESUMEN FINAL
    print("\n" + "=" * 80)
    print("📊 RESUMEN DE IMPORTACIÓN")
    print("=" * 80)
    print(f"\n   👥 Clientes: {clientes_importados}")
    print(f"   📦 Pedidos: {pedidos_importados}")
    print(f"\n   Total de registros: {clientes_importados + pedidos_importados}")
    print("\n" + "=" * 80)
    print("✅ IMPORTACIÓN COMPLETADA")
    print("=" * 80)
    print("\n   💡 Siguiente paso:")
    print("      • Verificar los datos en el sistema web")
    print("      • Importar productos e insumos si aún no están cargados")
    print("      • Asociar pedidos con productos existentes")
    print("\n" + "=" * 80)

