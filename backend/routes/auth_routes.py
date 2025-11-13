"""
Rutas de autenticación y gestión de usuarios
"""
from flask import Blueprint, request, jsonify, session
from extensions import db
from models.usuario import Usuario
from datetime import datetime
import functools

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def require_auth(f):
    """Decorador para requerir autenticación"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'No autenticado'}), 401
        return f(*args, **kwargs)
    return decorated_function

def require_role(*roles):
    """Decorador para requerir un rol específico"""
    def decorator(f):
        @functools.wraps(f)
        @require_auth
        def decorated_function(*args, **kwargs):
            user_id = session.get('user_id')
            if not user_id:
                return jsonify({'success': False, 'error': 'No autenticado'}), 401
            
            user = Usuario.query.get(user_id)
            if not user or not user.activo:
                return jsonify({'success': False, 'error': 'Usuario inactivo'}), 403
            
            if user.rol not in roles:
                return jsonify({'success': False, 'error': 'Acceso denegado'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@bp.route('/login', methods=['POST'])
def login():
    """Iniciar sesión"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'error': 'Usuario y contraseña requeridos'
            }), 400
        
        user = Usuario.query.filter_by(username=username).first()
        
        if not user or not user.activo:
            return jsonify({
                'success': False,
                'error': 'Usuario o contraseña incorrectos'
            }), 401
        
        if not user.check_password(password):
            return jsonify({
                'success': False,
                'error': 'Usuario o contraseña incorrectos'
            }), 401
        
        # Actualizar último acceso
        user.ultimo_acceso = datetime.utcnow()
        db.session.commit()
        
        # Crear sesión
        session['user_id'] = user.id
        session['username'] = user.username
        session['rol'] = user.rol
        
        return jsonify({
            'success': True,
            'data': {
                'user': user.to_dict(),
                'message': 'Login exitoso'
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Error al iniciar sesión: {str(e)}'
        }), 500

@bp.route('/logout', methods=['POST'])
def logout():
    """Cerrar sesión"""
    session.clear()
    return jsonify({
        'success': True,
        'message': 'Sesión cerrada'
    })

@bp.route('/me', methods=['GET'])
@require_auth
def get_current_user():
    """Obtener usuario actual"""
    try:
        user_id = session.get('user_id')
        user = Usuario.query.get(user_id)
        
        if not user or not user.activo:
            return jsonify({
                'success': False,
                'error': 'Usuario no encontrado o inactivo'
            }), 404
        
        return jsonify({
            'success': True,
            'data': user.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al obtener usuario: {str(e)}'
        }), 500

@bp.route('/usuarios', methods=['GET'])
@require_role('admin')
def listar_usuarios():
    """Listar todos los usuarios (solo admin)"""
    try:
        usuarios = Usuario.query.all()
        return jsonify({
            'success': True,
            'data': [u.to_dict() for u in usuarios]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al listar usuarios: {str(e)}'
        }), 500

@bp.route('/usuarios', methods=['POST'])
@require_role('admin')
def crear_usuario():
    """Crear nuevo usuario (solo admin)"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        rol = data.get('rol', 'taller')
        nombre = data.get('nombre', username)
        
        if not username or not password:
            return jsonify({
                'success': False,
                'error': 'Usuario y contraseña requeridos'
            }), 400
        
        if rol not in ['admin', 'secretaria', 'taller']:
            return jsonify({
                'success': False,
                'error': 'Rol inválido'
            }), 400
        
        # Verificar si el usuario ya existe
        if Usuario.query.filter_by(username=username).first():
            return jsonify({
                'success': False,
                'error': 'El usuario ya existe'
            }), 400
        
        nuevo_usuario = Usuario(
            username=username,
            rol=rol,
            nombre=nombre,
            activo=True
        )
        nuevo_usuario.set_password(password)
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': nuevo_usuario.to_dict(),
            'message': 'Usuario creado exitosamente'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Error al crear usuario: {str(e)}'
        }), 500

