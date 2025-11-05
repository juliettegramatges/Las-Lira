"""
Utilidades para manejo de archivos
"""

import os


def allowed_file(filename, allowed_extensions=None):
    """
    Verifica si un archivo tiene una extensión permitida

    Args:
        filename (str): Nombre del archivo a verificar
        allowed_extensions (set): Set de extensiones permitidas (sin punto)
                                 Por defecto: {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    Returns:
        bool: True si la extensión está permitida, False en caso contrario

    Examples:
        >>> allowed_file('imagen.jpg')
        True
        >>> allowed_file('documento.pdf')
        False
        >>> allowed_file('archivo.xlsx', {'xlsx', 'csv'})
        True
    """
    if allowed_extensions is None:
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def get_file_extension(filename):
    """
    Obtiene la extensión de un archivo

    Args:
        filename (str): Nombre del archivo

    Returns:
        str: Extensión del archivo (sin punto) en minúsculas, o '' si no tiene

    Examples:
        >>> get_file_extension('documento.PDF')
        'pdf'
        >>> get_file_extension('archivo')
        ''
    """
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return ''


def generar_nombre_archivo_unico(filename, prefix='', timestamp=True):
    """
    Genera un nombre de archivo único agregando un prefijo y/o timestamp

    Args:
        filename (str): Nombre original del archivo
        prefix (str): Prefijo a agregar (ej: 'producto_', 'pedido_')
        timestamp (bool): Si agregar timestamp para evitar colisiones

    Returns:
        str: Nombre de archivo único

    Examples:
        >>> generar_nombre_archivo_unico('foto.jpg', prefix='producto_')
        'producto_20250104_210830_foto.jpg'
    """
    from datetime import datetime
    import uuid

    name, ext = os.path.splitext(filename)
    name = name.replace(' ', '_')  # Reemplazar espacios

    parts = []

    if prefix:
        parts.append(prefix.rstrip('_'))

    if timestamp:
        parts.append(datetime.now().strftime('%Y%m%d_%H%M%S'))

    # Agregar ID corto para mayor unicidad
    parts.append(str(uuid.uuid4())[:8])

    parts.append(name)

    return '_'.join(parts) + ext
