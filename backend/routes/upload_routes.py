"""
Rutas para subida y gestión de imágenes
"""

from flask import Blueprint, request, jsonify, send_from_directory, session
from werkzeug.utils import secure_filename
from utils.file_helpers import allowed_file
import os
import sqlite3
from extensions import db
from models.inventario import Flor, Contenedor
from models.producto import Producto
from routes.auth_routes import require_auth
from config.database_paths import get_legacy_db_path, get_main_db_path

bp = Blueprint('upload', __name__)

# Configuración de carpeta de uploads
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Crear carpeta si no existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


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
@require_auth
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
                # Actualizar tanto imagen_url como imagen_principal para mantener consistencia
                producto.imagen_url = filename
                producto.imagen_principal = filename
                
                # También actualizar en la base de datos principal (SQLite) para que se refleje en el listado
                try:
                    conn_legacy = sqlite3.connect(get_main_db_path())
                    cursor_legacy = conn_legacy.cursor()
                    
                    # Actualizar imagen_url en la tabla productos
                    # Usar el filename completo para que se pueda construir la URL
                    cursor_legacy.execute('''
                        UPDATE productos 
                        SET imagen_url = ? 
                        WHERE id = ?
                    ''', (filename, producto_id))
                    
                    print(f"✅ Actualizado imagen_url en base legacy: {filename} para producto {producto_id}")
                    
                    # Actualizar o insertar en imagenes_productos si la tabla existe
                    try:
                        # Verificar si existe una imagen principal
                        cursor_legacy.execute('''
                            SELECT id FROM imagenes_productos 
                            WHERE producto_id = ? AND es_principal = 1
                            LIMIT 1
                        ''', (producto_id,))
                        existe_principal = cursor_legacy.fetchone()
                        
                        # Guardar solo el filename, no la URL completa (el frontend construirá la URL)
                        # Esto es más consistente con cómo se guarda en la tabla productos
                        imagen_url_completa = filename
                        
                        if existe_principal:
                            # Actualizar la imagen principal existente
                            cursor_legacy.execute('''
                                UPDATE imagenes_productos 
                                SET url = ? 
                                WHERE producto_id = ? AND es_principal = 1
                            ''', (imagen_url_completa, producto_id))
                            print(f"✅ Actualizada imagen principal en imagenes_productos: {filename} para producto {producto_id}")
                        else:
                            # Insertar nueva imagen principal
                            # Primero verificar si hay otras imágenes para este producto
                            cursor_legacy.execute('''
                                SELECT MAX(posicion) FROM imagenes_productos 
                                WHERE producto_id = ?
                            ''', (producto_id,))
                            max_pos = cursor_legacy.fetchone()[0] or -1
                            nueva_posicion = max_pos + 1
                            
                            cursor_legacy.execute('''
                                INSERT INTO imagenes_productos (producto_id, url, posicion, es_principal)
                                VALUES (?, ?, ?, 1)
                            ''', (producto_id, imagen_url_completa, nueva_posicion))
                            print(f"✅ Insertada nueva imagen principal en imagenes_productos: {filename} para producto {producto_id}")
                    except sqlite3.OperationalError as e:
                        # Si la tabla no existe, solo continuar
                        print(f"⚠️ Tabla imagenes_productos no existe o error: {str(e)}")
                    
                    conn_legacy.commit()
                    conn_legacy.close()
                except Exception as e:
                    print(f"⚠️ Advertencia: No se pudo actualizar la base de datos legacy: {str(e)}")
                    # Continuar de todas formas, ya que el modelo SQLAlchemy se actualizó
            else:
                return jsonify({'success': False, 'error': 'Archivo no válido'}), 400
        
        # Si viene URL o null (para eliminar)
        elif request.content_type and 'application/json' in request.content_type:
            if request.json and 'imagen_url' in request.json:
                # Actualizar tanto imagen_url como imagen_principal para mantener consistencia
                producto.imagen_url = request.json['imagen_url']
                producto.imagen_principal = request.json['imagen_url']
        else:
            return jsonify({'success': False, 'error': 'No se envió ningún archivo'}), 400
        
        db.session.commit()
        
        # Construir la respuesta con la URL completa de la imagen
        producto_dict = producto.to_dict()
        if producto_dict.get('imagen_url'):
            # Si es solo un filename, construir la URL completa
            if not producto_dict['imagen_url'].startswith('http') and not producto_dict['imagen_url'].startswith('/'):
                producto_dict['imagen_url'] = f'/api/upload/imagen/{producto_dict["imagen_url"]}'
            if not producto_dict.get('imagen_principal') or (producto_dict.get('imagen_principal') and not producto_dict['imagen_principal'].startswith('http') and not producto_dict['imagen_principal'].startswith('/')):
                producto_dict['imagen_principal'] = producto_dict['imagen_url']
        
        return jsonify({
            'success': True,
            'data': producto_dict,
            'message': 'Foto actualizada correctamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

