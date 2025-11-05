"""
Servicio de exportación de datos a Excel
Contiene lógica de negocio para generar archivos Excel
"""

from io import BytesIO
from datetime import datetime
from extensions import db
from models.pedido import Pedido
from models.producto import Producto
from models.cliente import Cliente
from utils.excel_helpers import crear_workbook_con_encabezado, ajustar_ancho_columnas


class ExportarService:
    """Servicio para exportación de datos a Excel"""

    @staticmethod
    def crear_excel_pedidos():
        """
        Genera archivo Excel con todos los pedidos

        Returns:
            BytesIO: Buffer con el archivo Excel generado
        """
        headers = [
            'ID', 'Fecha Pedido', 'Fecha Entrega', 'Canal', 'N° Shopify',
            'Cliente', 'Teléfono', 'Arreglo', 'Detalles', 'Precio Ramo',
            'Precio Envío', 'Destinatario', 'Mensaje', 'Firma', 'Dirección',
            'Comuna', 'Motivo', 'Estado', 'Pagado'
        ]

        wb, ws = crear_workbook_con_encabezado("Pedidos", headers)

        # Obtener datos
        pedidos = Pedido.query.order_by(Pedido.fecha_pedido.desc()).all()

        # Llenar datos
        for row_num, pedido in enumerate(pedidos, 2):
            ws.cell(row=row_num, column=1, value=pedido.id)
            ws.cell(row=row_num, column=2, value=pedido.fecha_pedido.strftime('%Y-%m-%d') if pedido.fecha_pedido else '')
            ws.cell(row=row_num, column=3, value=pedido.fecha_entrega.strftime('%Y-%m-%d') if pedido.fecha_entrega else '')
            ws.cell(row=row_num, column=4, value=pedido.canal or '')
            ws.cell(row=row_num, column=5, value=pedido.shopify_order_number or '')
            ws.cell(row=row_num, column=6, value=pedido.cliente_nombre or '')
            ws.cell(row=row_num, column=7, value=pedido.cliente_telefono or '')
            ws.cell(row=row_num, column=8, value=pedido.arreglo_pedido or '')
            ws.cell(row=row_num, column=9, value=pedido.detalles_adicionales or '')
            ws.cell(row=row_num, column=10, value=float(pedido.precio_ramo) if pedido.precio_ramo else 0)
            ws.cell(row=row_num, column=11, value=float(pedido.precio_envio) if pedido.precio_envio else 0)
            ws.cell(row=row_num, column=12, value=pedido.destinatario or '')
            ws.cell(row=row_num, column=13, value=pedido.mensaje or '')
            ws.cell(row=row_num, column=14, value=pedido.firma or '')
            ws.cell(row=row_num, column=15, value=pedido.direccion_entrega or '')
            ws.cell(row=row_num, column=16, value=pedido.comuna or '')
            ws.cell(row=row_num, column=17, value=pedido.motivo or '')
            ws.cell(row=row_num, column=18, value=pedido.estado or '')
            ws.cell(row=row_num, column=19, value=pedido.estado_pago or '')

        # Ajustar anchos
        ajustar_ancho_columnas(ws)

        # Guardar en memoria
        output = BytesIO()
        wb.save(output)
        output.seek(0)

        return output

    @staticmethod
    def crear_excel_productos():
        """
        Genera archivo Excel con todos los productos

        Returns:
            BytesIO: Buffer con el archivo Excel generado
        """
        headers = [
            'ID', 'Nombre', 'Descripción', 'Precio', 'Categoría',
            'Tipo', 'SKU', 'Peso', 'Tags', 'Activo', 'Fecha Creación'
        ]

        wb, ws = crear_workbook_con_encabezado("Productos", headers)

        # Obtener datos
        productos = Producto.query.order_by(Producto.nombre).all()

        # Llenar datos
        for row_num, producto in enumerate(productos, 2):
            ws.cell(row=row_num, column=1, value=producto.id)
            ws.cell(row=row_num, column=2, value=producto.nombre or '')
            ws.cell(row=row_num, column=3, value=producto.descripcion or '')
            ws.cell(row=row_num, column=4, value=float(producto.precio) if producto.precio else 0)
            ws.cell(row=row_num, column=5, value=producto.categoria or '')
            ws.cell(row=row_num, column=6, value=producto.tipo or '')
            ws.cell(row=row_num, column=7, value=producto.sku or '')
            ws.cell(row=row_num, column=8, value=float(producto.peso) if producto.peso else 0)
            ws.cell(row=row_num, column=9, value=producto.tags or '')
            ws.cell(row=row_num, column=10, value='Sí' if producto.activo else 'No')
            ws.cell(row=row_num, column=11, value=producto.fecha_creacion.strftime('%Y-%m-%d') if producto.fecha_creacion else '')

        # Ajustar anchos
        ajustar_ancho_columnas(ws)

        # Guardar en memoria
        output = BytesIO()
        wb.save(output)
        output.seek(0)

        return output

    @staticmethod
    def crear_excel_clientes():
        """
        Genera archivo Excel con todos los clientes

        Returns:
            BytesIO: Buffer con el archivo Excel generado
        """
        headers = [
            'ID', 'Nombre', 'Teléfono', 'Email', 'Tipo Cliente',
            'Total Pedidos', 'Total Gastado', 'Última Compra', 'Fecha Registro'
        ]

        wb, ws = crear_workbook_con_encabezado("Clientes", headers)

        # Obtener datos
        clientes = Cliente.query.order_by(Cliente.nombre).all()

        # Llenar datos
        for row_num, cliente in enumerate(clientes, 2):
            ws.cell(row=row_num, column=1, value=cliente.id)
            ws.cell(row=row_num, column=2, value=cliente.nombre or '')
            ws.cell(row=row_num, column=3, value=cliente.telefono or '')
            ws.cell(row=row_num, column=4, value=cliente.email or '')
            ws.cell(row=row_num, column=5, value=cliente.tipo_cliente or '')
            ws.cell(row=row_num, column=6, value=cliente.total_pedidos or 0)
            ws.cell(row=row_num, column=7, value=float(cliente.total_gastado) if cliente.total_gastado else 0)
            ws.cell(row=row_num, column=8, value=cliente.ultima_compra.strftime('%Y-%m-%d') if cliente.ultima_compra else '')
            ws.cell(row=row_num, column=9, value=cliente.fecha_registro.strftime('%Y-%m-%d') if cliente.fecha_registro else '')

        # Ajustar anchos
        ajustar_ancho_columnas(ws)

        # Guardar en memoria
        output = BytesIO()
        wb.save(output)
        output.seek(0)

        return output
