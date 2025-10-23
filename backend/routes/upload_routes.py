"""
Rutas para subida y gestión de imágenes
"""

from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
from app import db
from models.inventario import Flor, Contenedor
from models.producto import Producto

bp = Blueprint('upload', __name__)

# Configuración de carpeta de uploads
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Crear carpeta si no existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Verifica si el archivo tiene una extensión permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/imagen', methods=['POST'])
def subir_imagen():
    """Subir una imagen"""
    try:
        # Verificar que hay un archivo
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No se envió ningún archivo'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Nombre de archivo vacío'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Tipo de archivo no permitido'}), 400
        
        # Guardar archivo con nombre seguro
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # Si ya existe, agregar timestamp
        if os.path.exists(filepath):
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{int(os.time())}{ext}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        file.save(filepath)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'url': f'/api/upload/imagen/{filename}'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/imagen/<filename>', methods=['GET'])
def obtener_imagen(filename):
    """Servir una imagen subida"""
    try:
        return send_from_directory(UPLOAD_FOLDER, filename)
    except Exception as e:
        return jsonify({'success': False, 'error': 'Imagen no encontrada'}), 404


@bp.route('/flor/<flor_id>/foto', methods=['POST'])
def actualizar_foto_flor(flor_id):
    """Actualizar foto de una flor"""
    try:
        flor = Flor.query.get(flor_id)
        if not flor:
            return jsonify({'success': False, 'error': 'Flor no encontrada'}), 404
        
        # Si viene archivo
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(f"flor_{flor_id}_{file.filename}")
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                flor.foto_url = filename
            else:
                return jsonify({'success': False, 'error': 'Archivo no válido'}), 400
        
        # Si viene URL o null (para eliminar)
        elif request.content_type and 'application/json' in request.content_type:
            if request.json and 'foto_url' in request.json:
                flor.foto_url = request.json['foto_url']
        else:
            return jsonify({'success': False, 'error': 'No se envió ningún archivo'}), 400
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': flor.to_dict(),
            'message': 'Foto actualizada correctamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/contenedor/<contenedor_id>/foto', methods=['POST'])
def actualizar_foto_contenedor(contenedor_id):
    """Actualizar foto de un contenedor"""
    try:
        contenedor = Contenedor.query.get(contenedor_id)
        if not contenedor:
            return jsonify({'success': False, 'error': 'Contenedor no encontrado'}), 404
        
        # Si viene archivo
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(f"contenedor_{contenedor_id}_{file.filename}")
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                contenedor.foto_url = filename
            else:
                return jsonify({'success': False, 'error': 'Archivo no válido'}), 400
        
        # Si viene URL o null (para eliminar)
        elif request.content_type and 'application/json' in request.content_type:
            if request.json and 'foto_url' in request.json:
                contenedor.foto_url = request.json['foto_url']
        else:
            return jsonify({'success': False, 'error': 'No se envió ningún archivo'}), 400
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': contenedor.to_dict(),
            'message': 'Foto actualizada correctamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/producto/<producto_id>/foto', methods=['POST'])
def actualizar_foto_producto(producto_id):
    """Actualizar foto de un producto"""
    try:
        producto = Producto.query.get(producto_id)
        if not producto:
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404
        
        # Si viene archivo
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(f"producto_{producto_id}_{file.filename}")
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                producto.imagen_url = filename
            else:
                return jsonify({'success': False, 'error': 'Archivo no válido'}), 400
        
        # Si viene URL o null (para eliminar)
        elif request.content_type and 'application/json' in request.content_type:
            if request.json and 'imagen_url' in request.json:
                producto.imagen_url = request.json['imagen_url']
        else:
            return jsonify({'success': False, 'error': 'No se envió ningún archivo'}), 400
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': producto.to_dict(),
            'message': 'Foto actualizada correctamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

