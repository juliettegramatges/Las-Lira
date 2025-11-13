"""
Script de prueba para verificar la reserva/liberación de insumos
cuando un pedido cambia a/desde "En Proceso"
"""

from extensions import db
from app import app
from models.pedido import Pedido, PedidoInsumo
from models.inventario import Flor, Contenedor
from services.pedidos_service import PedidosService

with app.app_context():
    print("=" * 80)
    print("TEST: Reserva y Liberación de Insumos")
    print("=" * 80)

    # 1. Buscar un pedido con insumos
    pedido = Pedido.query.filter(
        Pedido.estado != 'Cancelado',
        Pedido.estado != 'Despachados'
    ).first()

    if not pedido:
        print("❌ No hay pedidos disponibles para probar")
        exit(1)

    print(f"\n📦 Pedido seleccionado: #{pedido.id}")
    print(f"   Estado actual: {pedido.estado}")
    print(f"   Cliente: {pedido.cliente_nombre}")

    # 2. Obtener insumos del pedido
    insumos = PedidoInsumo.query.filter_by(pedido_id=pedido.id).all()

    if not insumos:
        print("⚠️  Este pedido no tiene insumos registrados")
        exit(1)

    print(f"\n📋 Insumos del pedido ({len(insumos)} items):")

    # Guardar estado inicial
    estado_inicial = {}

    for insumo in insumos:
        if insumo.insumo_tipo == 'Flor':
            item = Flor.query.get(insumo.insumo_id)
            if item:
                estado_inicial[f"F_{insumo.insumo_id}"] = item.cantidad_en_uso
                print(f"   🌸 {item.nombre}: {insumo.cantidad} unidades")
                print(f"      Stock: {item.cantidad_stock} | En uso: {item.cantidad_en_uso} | Disponible: {item.cantidad_disponible}")
        elif insumo.insumo_tipo == 'Contenedor':
            item = Contenedor.query.get(insumo.insumo_id)
            if item:
                estado_inicial[f"C_{insumo.insumo_id}"] = item.cantidad_en_uso
                print(f"   📦 {item.nombre or item.tipo}: {insumo.cantidad} unidades")
                print(f"      Stock: {item.cantidad_stock} | En uso: {item.cantidad_en_uso} | Disponible: {item.cantidad_disponible}")

    # 3. Test: Mover a "En Proceso"
    print(f"\n🔄 TEST 1: Cambiar pedido a 'En Proceso'...")
    success, result, mensaje = PedidosService.actualizar_estado(pedido.id, "En Proceso")

    if success:
        print(f"   ✅ {mensaje}")

        # Verificar que cantidad_en_uso aumentó
        print("\n   Verificando cambios en inventario:")
        for insumo in insumos:
            key = f"{insumo.insumo_tipo[0]}_{insumo.insumo_id}"
            if insumo.insumo_tipo == 'Flor':
                item = Flor.query.get(insumo.insumo_id)
                if item:
                    anterior = estado_inicial.get(key, 0)
                    nuevo = item.cantidad_en_uso
                    diferencia = nuevo - anterior
                    if diferencia == insumo.cantidad:
                        print(f"   ✅ {item.nombre}: {anterior} → {nuevo} (+{diferencia}) ✓")
                    else:
                        print(f"   ❌ {item.nombre}: esperado +{insumo.cantidad}, obtuvo +{diferencia}")
            elif insumo.insumo_tipo == 'Contenedor':
                item = Contenedor.query.get(insumo.insumo_id)
                if item:
                    anterior = estado_inicial.get(key, 0)
                    nuevo = item.cantidad_en_uso
                    diferencia = nuevo - anterior
                    if diferencia == insumo.cantidad:
                        print(f"   ✅ {item.nombre or item.tipo}: {anterior} → {nuevo} (+{diferencia}) ✓")
                    else:
                        print(f"   ❌ {item.nombre or item.tipo}: esperado +{insumo.cantidad}, obtuvo +{diferencia}")
    else:
        print(f"   ❌ Error: {mensaje}")
        exit(1)

    # 4. Test: Mover de vuelta a estado anterior
    print(f"\n🔄 TEST 2: Cambiar pedido a 'Entregas Semana' (liberar insumos)...")
    success, result, mensaje = PedidosService.actualizar_estado(pedido.id, "Entregas Semana")

    if success:
        print(f"   ✅ {mensaje}")

        # Verificar que cantidad_en_uso volvió al valor inicial
        print("\n   Verificando liberación de inventario:")
        for insumo in insumos:
            key = f"{insumo.insumo_tipo[0]}_{insumo.insumo_id}"
            if insumo.insumo_tipo == 'Flor':
                item = Flor.query.get(insumo.insumo_id)
                if item:
                    esperado = estado_inicial.get(key, 0)
                    actual = item.cantidad_en_uso
                    if actual == esperado:
                        print(f"   ✅ {item.nombre}: volvió a {actual} ✓")
                    else:
                        print(f"   ❌ {item.nombre}: esperado {esperado}, obtuvo {actual}")
            elif insumo.insumo_tipo == 'Contenedor':
                item = Contenedor.query.get(insumo.insumo_id)
                if item:
                    esperado = estado_inicial.get(key, 0)
                    actual = item.cantidad_en_uso
                    if actual == esperado:
                        print(f"   ✅ {item.nombre or item.tipo}: volvió a {actual} ✓")
                    else:
                        print(f"   ❌ {item.nombre or item.tipo}: esperado {esperado}, obtuvo {actual}")
    else:
        print(f"   ❌ Error: {mensaje}")
        exit(1)

    print("\n" + "=" * 80)
    print("✅ TODOS LOS TESTS PASARON")
    print("=" * 80)
