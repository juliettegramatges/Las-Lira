"""
Servicio para gestión de inventario y descuento automático de stock
"""

from backend.app import db
from backend.models.inventario import Flor, Contenedor
from backend.models.pedido import PedidoInsumo, Pedido
from backend.models.producto import RecetaProducto
from datetime import date

class InventarioService:
    
    @staticmethod
    def verificar_disponibilidad_producto(producto_id):
        """
        Verifica si hay stock suficiente para preparar un producto
        """
        recetas = RecetaProducto.query.filter_by(producto_id=producto_id).all()
        
        faltantes = []
        disponible = True
        
        for receta in recetas:
            if receta.es_opcional:
                continue
                
            if receta.insumo_tipo == 'Flor':
                flor = Flor.query.get(receta.insumo_id)
                stock_actual = flor.cantidad_stock if flor else 0
                
                if stock_actual < receta.cantidad:
                    disponible = False
                    faltantes.append({
                        'insumo_tipo': 'Flor',
                        'insumo_id': receta.insumo_id,
                        'necesario': receta.cantidad,
                        'disponible': stock_actual
                    })
            else:  # Contenedor
                contenedor = Contenedor.query.get(receta.insumo_id)
                stock_actual = contenedor.stock if contenedor else 0
                
                if stock_actual < receta.cantidad:
                    disponible = False
                    faltantes.append({
                        'insumo_tipo': 'Contenedor',
                        'insumo_id': receta.insumo_id,
                        'necesario': receta.cantidad,
                        'disponible': stock_actual
                    })
        
        return disponible, faltantes
    
    @staticmethod
    def registrar_insumos_pedido(pedido_id, producto_id=None, insumos_personalizados=None):
        """
        Registra los insumos necesarios para un pedido
        - Si tiene producto_id: usa la receta del producto
        - Si es personalizado: usa insumos_personalizados
        """
        try:
            if producto_id:
                # Usar receta del producto
                recetas = RecetaProducto.query.filter_by(producto_id=producto_id).all()
                
                for receta in recetas:
                    if receta.insumo_tipo == 'Flor':
                        flor = Flor.query.get(receta.insumo_id)
                        costo_unitario = flor.costo_unitario if flor else 0
                    else:
                        contenedor = Contenedor.query.get(receta.insumo_id)
                        costo_unitario = contenedor.costo if contenedor else 0
                    
                    pedido_insumo = PedidoInsumo(
                        pedido_id=pedido_id,
                        insumo_tipo=receta.insumo_tipo,
                        insumo_id=receta.insumo_id,
                        cantidad=receta.cantidad,
                        costo_unitario=costo_unitario,
                        costo_total=costo_unitario * receta.cantidad,
                        descontado_stock=False
                    )
                    db.session.add(pedido_insumo)
            
            elif insumos_personalizados:
                # Usar insumos personalizados (para pedidos de WhatsApp)
                for insumo in insumos_personalizados:
                    if insumo['tipo'] == 'Flor':
                        flor = Flor.query.get(insumo['id'])
                        costo_unitario = flor.costo_unitario if flor else 0
                    else:
                        contenedor = Contenedor.query.get(insumo['id'])
                        costo_unitario = contenedor.costo if contenedor else 0
                    
                    pedido_insumo = PedidoInsumo(
                        pedido_id=pedido_id,
                        insumo_tipo=insumo['tipo'],
                        insumo_id=insumo['id'],
                        cantidad=insumo['cantidad'],
                        costo_unitario=costo_unitario,
                        costo_total=costo_unitario * insumo['cantidad'],
                        descontado_stock=False
                    )
                    db.session.add(pedido_insumo)
            
            db.session.commit()
            return True, "Insumos registrados correctamente"
            
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def descontar_stock_pedido(pedido_id):
        """
        Descuenta el stock de los insumos de un pedido
        Se ejecuta cuando el pedido pasa a estado "En Preparación"
        """
        try:
            # Obtener insumos del pedido que no han sido descontados
            insumos = PedidoInsumo.query.filter_by(
                pedido_id=pedido_id,
                descontado_stock=False
            ).all()
            
            descontados = []
            
            for insumo in insumos:
                if insumo.insumo_tipo == 'Flor':
                    flor = Flor.query.get(insumo.insumo_id)
                    if flor:
                        if flor.cantidad_stock >= insumo.cantidad:
                            flor.cantidad_stock -= insumo.cantidad
                            flor.fecha_actualizacion = date.today()
                            insumo.descontado_stock = True
                            descontados.append(f"Flor: {flor.tipo} {flor.color} (-{insumo.cantidad})")
                        else:
                            raise Exception(f"Stock insuficiente de {flor.tipo} {flor.color}")
                
                else:  # Contenedor
                    contenedor = Contenedor.query.get(insumo.insumo_id)
                    if contenedor:
                        if contenedor.stock >= insumo.cantidad:
                            contenedor.stock -= insumo.cantidad
                            contenedor.fecha_actualizacion = date.today()
                            insumo.descontado_stock = True
                            descontados.append(f"Contenedor: {contenedor.tipo} {contenedor.forma} (-{insumo.cantidad})")
                        else:
                            raise Exception(f"Stock insuficiente de {contenedor.tipo} {contenedor.forma}")
            
            db.session.commit()
            return True, f"Stock descontado: {', '.join(descontados)}"
            
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def devolver_stock_pedido(pedido_id):
        """
        Devuelve el stock si un pedido es cancelado
        """
        try:
            # Obtener insumos que SÍ fueron descontados
            insumos = PedidoInsumo.query.filter_by(
                pedido_id=pedido_id,
                descontado_stock=True
            ).all()
            
            devueltos = []
            
            for insumo in insumos:
                if insumo.insumo_tipo == 'Flor':
                    flor = Flor.query.get(insumo.insumo_id)
                    if flor:
                        flor.cantidad_stock += insumo.cantidad
                        flor.fecha_actualizacion = date.today()
                        insumo.descontado_stock = False
                        devueltos.append(f"Flor: {flor.tipo} {flor.color} (+{insumo.cantidad})")
                
                else:  # Contenedor
                    contenedor = Contenedor.query.get(insumo.insumo_id)
                    if contenedor:
                        contenedor.stock += insumo.cantidad
                        contenedor.fecha_actualizacion = date.today()
                        insumo.descontado_stock = False
                        devueltos.append(f"Contenedor: {contenedor.tipo} (+{insumo.cantidad})")
            
            db.session.commit()
            return True, f"Stock devuelto: {', '.join(devueltos)}"
            
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def obtener_alertas_stock():
        """
        Obtiene alertas de productos con stock bajo
        """
        # Flores con stock bajo (menos de 20 unidades)
        flores_bajo_stock = Flor.query.filter(Flor.cantidad_stock < 20).all()
        
        # Contenedores con stock bajo (menos de 5 unidades)
        contenedores_bajo_stock = Contenedor.query.filter(Contenedor.stock < 5).all()
        
        alertas = []
        
        for flor in flores_bajo_stock:
            alertas.append({
                'tipo': 'Flor',
                'id': flor.id,
                'nombre': f"{flor.tipo} {flor.color}",
                'stock_actual': flor.cantidad_stock,
                'nivel': 'critico' if flor.cantidad_stock < 10 else 'bajo',
                'mensaje': f"Stock bajo de {flor.tipo} {flor.color}: {flor.cantidad_stock} unidades"
            })
        
        for contenedor in contenedores_bajo_stock:
            alertas.append({
                'tipo': 'Contenedor',
                'id': contenedor.id,
                'nombre': f"{contenedor.tipo} {contenedor.forma}",
                'stock_actual': contenedor.stock,
                'nivel': 'critico' if contenedor.stock < 3 else 'bajo',
                'mensaje': f"Stock bajo de {contenedor.tipo}: {contenedor.stock} unidades"
            })
        
        return alertas

