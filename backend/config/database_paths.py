"""
Configuración de rutas de bases de datos
"""

import os


def get_legacy_db_path():
    """
    Obtiene la ruta de la base de datos legacy (las_lira.db)
    Ubicada en el directorio raíz del proyecto

    Returns:
        str: Ruta completa a las_lira.db
    """
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(os.path.dirname(backend_dir), 'las_lira.db')


def get_main_db_path():
    """
    Obtiene la ruta de la base de datos principal (laslira.db)
    Ubicada en instance/ (raíz del proyecto)

    Returns:
        str: Ruta completa a laslira.db
    """
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    project_root = os.path.dirname(backend_dir)
    return os.path.join(project_root, 'instance', 'laslira.db')
