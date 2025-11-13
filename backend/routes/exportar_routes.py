"""
Rutas para exportar datos a Excel
"""
from flask import Blueprint, send_file, jsonify, request
from datetime import datetime
from services.exportar_service import ExportarService

bp = Blueprint('exportar', __name__)


@bp.route('/pedidos', methods=['GET'])
def exportar_pedidos():
    """Exportar pedidos a Excel con filtros opcionales de fecha y columnas"""
    try:
        
        # Obtener parámetros de fecha
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        # Obtener columnas seleccionadas (separadas por comas)
        columnas_str = request.args.get('columnas')
        columnas_seleccionadas = None
        if columnas_str:
            columnas_seleccionadas = [col.strip() for col in columnas_str.split(',') if col.strip()]

        # Convertir fechas si vienen como strings
        if fecha_inicio:
            try:
                fecha_inicio = datetime.fromisoformat(fecha_inicio.replace('Z', '+00:00'))
            except:
                fecha_inicio = None
        
        if fecha_fin:
            try:
                fecha_fin = datetime.fromisoformat(fecha_fin.replace('Z', '+00:00'))
            except:
                fecha_fin = None

        excel_file = ExportarService.crear_excel_pedidos(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            columnas_seleccionadas=columnas_seleccionadas
        )

        # Generar nombre de archivo con rango de fechas si aplica
        fecha_str = ""
        if fecha_inicio and fecha_fin:
            fecha_str = f"_{fecha_inicio.strftime('%Y%m%d')}_{fecha_fin.strftime('%Y%m%d')}"
        elif fecha_inicio:
            fecha_str = f"_desde_{fecha_inicio.strftime('%Y%m%d')}"
        elif fecha_fin:
            fecha_str = f"_hasta_{fecha_fin.strftime('%Y%m%d')}"

        filename = f"pedidos{fecha_str}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        return send_file(
            excel_file,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al exportar pedidos: {str(e)}'
        }), 500


@bp.route('/productos', methods=['GET'])
def exportar_productos():
    """Exportar todos los productos a Excel"""
    try:
        excel_file = ExportarService.crear_excel_productos()

        filename = f"productos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        return send_file(
            excel_file,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al exportar productos: {str(e)}'
        }), 500


@bp.route('/clientes', methods=['GET'])
def exportar_clientes():
    """Exportar todos los clientes a Excel"""
    try:
        excel_file = ExportarService.crear_excel_clientes()

        filename = f"clientes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        return send_file(
            excel_file,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al exportar clientes: {str(e)}'
        }), 500
