"""
Rutas para exportar datos a Excel
"""
from flask import Blueprint, send_file, jsonify
from datetime import datetime
from services.exportar_service import ExportarService

bp = Blueprint('exportar', __name__)


@bp.route('/pedidos', methods=['GET'])
def exportar_pedidos():
    """Exportar todos los pedidos a Excel"""
    try:
        excel_file = ExportarService.crear_excel_pedidos()

        filename = f"pedidos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

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
