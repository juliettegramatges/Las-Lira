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
    def crear_excel_pedidos(fecha_inicio=None, fecha_fin=None, columnas_seleccionadas=None):
        """
        Genera archivo Excel con pedidos filtrados por fecha y columnas seleccionadas

        Args:
            fecha_inicio: Fecha de inicio para filtrar (datetime o string ISO)
            fecha_fin: Fecha de fin para filtrar (datetime o string ISO)
            columnas_seleccionadas: Lista de nombres de columnas a incluir (None = todas)

        Returns:
            BytesIO: Buffer con el archivo Excel generado
        """
        # Definir todas las columnas disponibles con sus claves
        todas_las_columnas = {
            'ID': ('id', lambda p: p.id),
            'Fecha Pedido': ('fecha_pedido', lambda p: p.fecha_pedido.strftime('%Y-%m-%d') if p.fecha_pedido else ''),
            'Fecha Entrega': ('fecha_entrega', lambda p: p.fecha_entrega.strftime('%Y-%m-%d') if p.fecha_entrega else ''),
            'Canal': ('canal', lambda p: p.canal or ''),
            'N° Shopify': ('shopify_order_number', lambda p: p.shopify_order_number or ''),
            'Cliente': ('cliente_nombre', lambda p: p.cliente_nombre or ''),
            'Teléfono': ('cliente_telefono', lambda p: p.cliente_telefono or ''),
            'Email Cliente': ('cliente_email', lambda p: p.cliente_email or ''),
            'Arreglo': ('arreglo_pedido', lambda p: p.arreglo_pedido or ''),
            'Detalles': ('detalles_adicionales', lambda p: p.detalles_adicionales or ''),
            'Precio Ramo': ('precio_ramo', lambda p: float(p.precio_ramo) if p.precio_ramo else 0),
            'Precio Envío': ('precio_envio', lambda p: float(p.precio_envio) if p.precio_envio else 0),
            'Precio Total': ('precio_total', lambda p: float(p.precio_total)),
            'Destinatario': ('destinatario', lambda p: p.destinatario or ''),
            'Mensaje': ('mensaje', lambda p: p.mensaje or ''),
            'Firma': ('firma', lambda p: p.firma or ''),
            'Dirección': ('direccion_entrega', lambda p: p.direccion_entrega or ''),
            'Comuna': ('comuna', lambda p: p.comuna or ''),
            'Motivo': ('motivo', lambda p: p.motivo or ''),
            'Estado': ('estado', lambda p: p.estado or ''),
            'Estado Pago': ('estado_pago', lambda p: p.estado_pago or ''),
            'Método Pago': ('metodo_pago', lambda p: p.metodo_pago or ''),
            'Documento Tributario': ('documento_tributario', lambda p: p.documento_tributario or ''),
            'N° Documento': ('numero_documento', lambda p: p.numero_documento or ''),
            'Día Entrega': ('dia_entrega', lambda p: p.dia_entrega or ''),
            'Tipo Pedido': ('tipo_pedido', lambda p: p.tipo_pedido or ''),
            'Es Evento': ('es_evento', lambda p: 'Sí' if p.es_evento else 'No'),
            'Tipo Evento': ('tipo_evento', lambda p: p.tipo_evento or ''),
        }

        # Determinar qué columnas incluir
        if columnas_seleccionadas and len(columnas_seleccionadas) > 0:
            # Filtrar solo las columnas seleccionadas que existen
            columnas_a_exportar = {k: v for k, v in todas_las_columnas.items() if k in columnas_seleccionadas}
            # Mantener el orden de selección
            headers = [col for col in columnas_seleccionadas if col in todas_las_columnas]
        else:
            # Si no se especifican, usar todas
            columnas_a_exportar = todas_las_columnas
            headers = list(todas_las_columnas.keys())

        wb, ws = crear_workbook_con_encabezado("Pedidos", headers)

        # Construir query con filtros de fecha
        from sqlalchemy import and_
        query = Pedido.query

        if fecha_inicio:
            if isinstance(fecha_inicio, str):
                try:
                    # Intentar parsear como fecha ISO
                    if 'T' in fecha_inicio:
                        fecha_inicio = datetime.fromisoformat(fecha_inicio.replace('Z', '+00:00'))
                    else:
                        # Si es solo fecha (YYYY-MM-DD), agregar hora 00:00:00
                        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
                except:
                    fecha_inicio = None
            if fecha_inicio:
                query = query.filter(Pedido.fecha_pedido >= fecha_inicio)

        if fecha_fin:
            if isinstance(fecha_fin, str):
                try:
                    # Intentar parsear como fecha ISO
                    if 'T' in fecha_fin:
                        fecha_fin = datetime.fromisoformat(fecha_fin.replace('Z', '+00:00'))
                    else:
                        # Si es solo fecha (YYYY-MM-DD), agregar hora 23:59:59
                        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
                        fecha_fin = fecha_fin.replace(hour=23, minute=59, second=59)
                except:
                    fecha_fin = None
            if fecha_fin:
                query = query.filter(Pedido.fecha_pedido <= fecha_fin)

        # Obtener datos ordenados
        pedidos = query.order_by(Pedido.fecha_pedido.desc()).all()

        # Llenar datos
        for row_num, pedido in enumerate(pedidos, 2):
            for col_num, header in enumerate(headers, 1):
                if header in columnas_a_exportar:
                    _, getter = columnas_a_exportar[header]
                    value = getter(pedido)
                    ws.cell(row=row_num, column=col_num, value=value)

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
