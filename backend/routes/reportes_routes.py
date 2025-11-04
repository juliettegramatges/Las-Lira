"""
Rutas API para reportes y analytics (Refactorizado)
Las rutas ahora delegan la lógica de negocio al ReportesService
"""

from flask import Blueprint, request, jsonify
from services.reportes_service import ReportesService

bp = Blueprint('reportes', __name__)


@bp.route('/kpis', methods=['GET'])
def obtener_kpis():
    """Obtener KPIs principales del dashboard"""
    try:
        kpis = ReportesService.obtener_kpis()
        return jsonify({
            'success': True,
            'data': kpis
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/ventas-mensuales', methods=['GET'])
def obtener_ventas_mensuales():
    """Obtiene ventas agrupadas por mes"""
    try:
        meses = int(request.args.get('meses', 6))
        ventas = ReportesService.obtener_ventas_mensuales(meses)

        return jsonify({
            'success': True,
            'data': ventas
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/top-productos', methods=['GET'])
def obtener_top_productos():
    """Obtiene los productos más vendidos"""
    try:
        limite = int(request.args.get('limite', 10))
        productos = ReportesService.obtener_top_productos(limite)

        return jsonify({
            'success': True,
            'data': productos
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/distribucion-tipos', methods=['GET'])
def obtener_distribucion_tipos():
    """Obtiene la distribución de pedidos por tipo"""
    try:
        distribucion = ReportesService.obtener_distribucion_tipos()

        return jsonify({
            'success': True,
            'data': distribucion
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/top-clientes', methods=['GET'])
def obtener_top_clientes():
    """Obtiene los mejores clientes por gasto total"""
    try:
        limite = int(request.args.get('limite', 10))
        clientes = ReportesService.obtener_top_clientes(limite)

        return jsonify({
            'success': True,
            'data': clientes
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/distribucion-clientes', methods=['GET'])
def obtener_distribucion_clientes():
    """Obtiene la distribución de clientes por tipo"""
    try:
        distribucion = ReportesService.obtener_distribucion_clientes()

        return jsonify({
            'success': True,
            'data': distribucion
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/comunas-frecuentes', methods=['GET'])
def obtener_comunas_frecuentes():
    """Obtiene las comunas con más pedidos"""
    try:
        limite = int(request.args.get('limite', 10))
        comunas = ReportesService.obtener_comunas_frecuentes(limite)

        return jsonify({
            'success': True,
            'data': comunas
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/analisis-eventos', methods=['GET'])
def analisis_eventos():
    """Analiza eventos y sus estados"""
    try:
        analisis = ReportesService.analisis_eventos()

        return jsonify({
            'success': True,
            'data': analisis
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/analisis-cobranza', methods=['GET'])
def analisis_cobranza():
    """Analiza el estado de cobranza de pedidos"""
    try:
        analisis = ReportesService.analisis_cobranza()

        return jsonify({
            'success': True,
            'data': analisis
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/personalizaciones', methods=['GET'])
def obtener_personalizaciones():
    """Obtiene resumen de personalizaciones de pedidos"""
    try:
        personalizaciones = ReportesService.obtener_personalizaciones()

        return jsonify({
            'success': True,
            'data': personalizaciones
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/ventas-dia-semana', methods=['GET'])
def ventas_por_dia_semana():
    """Analiza ventas agrupadas por día de la semana"""
    try:
        ventas = ReportesService.ventas_por_dia_semana()

        return jsonify({
            'success': True,
            'data': ventas
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/canales-venta', methods=['GET'])
def obtener_canales_venta():
    """Obtiene distribución de ventas por canal"""
    try:
        canales = ReportesService.obtener_canales_venta()

        return jsonify({
            'success': True,
            'data': canales
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/arreglos-por-motivo', methods=['GET'])
def arreglos_por_motivo():
    """Obtiene los arreglos más solicitados por cada motivo"""
    try:
        arreglos = ReportesService.arreglos_por_motivo()

        return jsonify({
            'success': True,
            'data': arreglos
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/anticipacion-pedidos', methods=['GET'])
def analisis_anticipacion_pedidos():
    """Analiza con cuánta anticipación se hacen los pedidos"""
    try:
        analisis = ReportesService.analisis_anticipacion_pedidos()

        return jsonify({
            'success': True,
            'data': analisis
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/colores-frecuentes', methods=['GET'])
def obtener_colores_frecuentes():
    """Obtiene los colores más solicitados en pedidos personalizados"""
    try:
        colores = ReportesService.obtener_colores_frecuentes()

        return jsonify({
            'success': True,
            'data': colores
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/analisis-personalizaciones', methods=['GET'])
def analisis_personalizaciones():
    """Análisis detallado de personalizaciones"""
    try:
        analisis = ReportesService.analisis_personalizaciones_detallado()

        return jsonify({
            'success': True,
            'data': analisis
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
