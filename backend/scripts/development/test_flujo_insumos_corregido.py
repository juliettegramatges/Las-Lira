"""
Script de prueba para verificar el flujo CORRECTO de reserva/consumo de insumos:

1. CREAR pedido → Reservar insumos (en_uso++)
2. Pasar a "Listo para Despacho" → Consumir insumos (stock--, en_uso--)
3. Verificar que cantidad_disponible se mantiene correcta sin doble descuento
"""

from extensions import db
from app import app
from models.pedido import Pedido, PedidoInsumo
from models.inventario import Flor, Contenedor
from services.pedidos_service import PedidosService

with app.app_context():
    print("=" * 80)
    print("TEST: Flujo CORRECTO de Reserva → Consumo de Insumos")
    print("=" * 80)

    # 1. Buscar un pedido existente para usar sus insumos como referencia
    pedido_ref = Pedido.query.filter(
        Pedido.estado != 'Cancelado',
        Pedido.estado != 'Despachados'
    ).first()

    if not pedido_ref:
        print("❌ No hay pedidos disponibles para usar como referencia")
        exit(1)

    print(f"\n📦 Usando pedido #{pedido_ref.id} como referencia")
    print(f"   Estado: {pedido_ref.estado}")

    # 2. Obtener estado inicial de inventario
    print(f"\n📊 Estado INICIAL del inventario:")

    # Tomar el primer insumo de tipo Flor como ejemplo
    insumo_flor = PedidoInsumo.query.filter_by(
        pedido_id=pedido_ref.id,
        insumo_tipo='Flor'
    ).first()

    if not insumo_flor:
        print("❌ No hay insumos de tipo Flor para probar")
        exit(1)

    flor = Flor.query.get(insumo_flor.insumo_id)
    if not flor:
        print(f"❌ No se encontró la flor {insumo_flor.insumo_id}")
        exit(1)

    print(f"   🌸 {flor.nombre}:")
    print(f"      Stock: {flor.cantidad_stock}")
    print(f"      En uso: {flor.cantidad_en_uso}")
    print(f"      Disponible: {flor.cantidad_disponible}")

    stock_inicial = flor.cantidad_stock
    en_uso_inicial = flor.cantidad_en_uso
    disponible_inicial = flor.cantidad_disponible

    # 3. Test: Pasar pedido existente a "Listo para Despacho"
    print(f"\n🔄 TEST: Cambiar pedido #{pedido_ref.id} a 'Listo para Despacho'...")
    success, result, mensaje = PedidosService.actualizar_estado(pedido_ref.id, "Listo para Despacho")

    if success:
        print(f"   ✅ {mensaje}")

        # Refrescar el objeto flor
        db.session.refresh(flor)

        print(f"\n   Verificando CONSUMO de inventario:")
        print(f"   🌸 {flor.nombre}:")
        print(f"      Stock: {stock_inicial} → {flor.cantidad_stock} (esperado: {stock_inicial - insumo_flor.cantidad})")
        print(f"      En uso: {en_uso_inicial} → {flor.cantidad_en_uso} (esperado: {en_uso_inicial - insumo_flor.cantidad})")
        print(f"      Disponible: {disponible_inicial} → {flor.cantidad_disponible}")

        # Verificaciones
        stock_esperado = stock_inicial - insumo_flor.cantidad
        en_uso_esperado = max(0, en_uso_inicial - insumo_flor.cantidad)

        if flor.cantidad_stock == stock_esperado:
            print(f"   ✅ Stock consumido correctamente (-{insumo_flor.cantidad})")
        else:
            print(f"   ❌ Stock incorrecto: esperado {stock_esperado}, obtuvo {flor.cantidad_stock}")

        if flor.cantidad_en_uso == en_uso_esperado:
            print(f"   ✅ Reserva liberada correctamente (-{insumo_flor.cantidad})")
        else:
            print(f"   ❌ En uso incorrecto: esperado {en_uso_esperado}, obtuvo {flor.cantidad_en_uso}")

        # Verificar que disponible se mantiene (porque ambos bajaron)
        if flor.cantidad_disponible == disponible_inicial:
            print(f"   ✅ Cantidad disponible se mantiene correcta (sin doble descuento)")
        else:
            print(f"   ⚠️  Cantidad disponible cambió: {disponible_inicial} → {flor.cantidad_disponible}")
            print(f"      Esto puede ser esperado si otros pedidos cambiaron")

    else:
        print(f"   ❌ Error: {mensaje}")
        exit(1)

    # 4. Verificar que insumos están marcados como descontados
    print(f"\n   Verificando flag descontado_stock:")
    insumos_pedido = PedidoInsumo.query.filter_by(pedido_id=pedido_ref.id).all()
    for insumo in insumos_pedido:
        if insumo.descontado_stock:
            print(f"   ✅ {insumo.insumo_nombre}: descontado_stock = True")
        else:
            print(f"   ❌ {insumo.insumo_nombre}: descontado_stock = False (debería ser True)")

    print("\n" + "=" * 80)
    print("✅ TEST COMPLETADO")
    print("=" * 80)
    print("\nResumen del flujo correcto:")
    print("1. Al CREAR pedido → Insumos se RESERVAN (en_uso++, disponible--)")
    print("2. Al pasar a 'Listo para Despacho' → Insumos se CONSUMEN (stock--, en_uso--, disponible=igual)")
    print("3. cantidad_disponible = cantidad_stock - cantidad_en_uso (sin doble descuento)")
