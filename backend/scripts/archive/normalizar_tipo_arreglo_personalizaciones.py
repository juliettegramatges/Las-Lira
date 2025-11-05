"""
Normaliza el tipo de arreglo en pedidos de personalización.

Regla:
- Si `arreglo_pedido` contiene prefijos genéricos como "ARREGLO FLORAL", extraer el tipo
  específico que viene después y guardarlo en `arreglo_pedido` en formato Title Case.
- También actualiza `tipo_personalizacion` con el mismo valor cuando aplique.

Base de datos objetivo: backend/instance/laslira.db (configurada por app.py)
"""

import os
import sys
import re
from typing import Optional

from flask import Flask


def _clean_spaces(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def extract_tipo_from_arreglo(arreglo_texto: str) -> Optional[str]:
    """
    Dado un texto de `arreglo_pedido`, extrae el tipo específico eliminando el prefijo
    genérico "ARREGLO FLORAL" y variaciones, devolviendo Title Case.

    Ejemplos de entradas esperadas:
    - "ARREGLO FLORAL Redondo Grande"
    - "Arreglo floral - Clásico Redondo"
    - "arreglo floral: Bouquet Mediano"
    - "ARREGLO  FLORAL  –  Minimalista"
    """
    if not arreglo_texto:
        return None

    original = arreglo_texto
    texto = arreglo_texto.strip()

    # Normalizar separadores comunes tras el prefijo
    # Admitimos: -, :, –, —, ·
    # Capturamos lo que viene después del prefijo
    patron = re.compile(
        r"(?i)^\s*arreglo\s*floral\s*(?:[-:–—·]*\s*)?(?P<tipo>.+?)\s*$"
    )

    m = patron.match(texto)
    if not m:
        # Si no empieza con el prefijo, intentar cortar si contiene el prefijo en medio
        # p.ej: "Pedido Personalización | ARREGLO FLORAL: Redondo"
        m2 = re.search(r"(?i)arreglo\s*floral\s*(?:[-:–—·]*\s*)?(?P<tipo>.+)$", texto)
        if not m2:
            return None
        candidato = m2.group("tipo").strip()
    else:
        candidato = m.group("tipo").strip()

    # Limpiar frases de relleno comunes
    # Remover prefijos como "tipo", "de", etc. al inicio
    candidato = re.sub(r"(?i)^(tipo\s*(de)?\s*|de\s+)", "", candidato).strip()

    # Quitar espacios repetidos
    candidato = _clean_spaces(candidato)

    # Si tras limpiar quedó vacío o muy corto, abortar
    if len(candidato) < 2:
        return None

    # Devolver en Title Case, preservando acrónimos sencillos
    tipo_title = " ".join(
        [w.upper() if w.isupper() and len(w) <= 4 else w.capitalize() for w in candidato.split(" ")]
    )

    return tipo_title


def run():
    # Asegurar rutas de import para ejecutar el script directamente
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    root_dir = os.path.abspath(os.path.join(base_dir, ".."))
    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)  # /backend
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)  # /

    # Cargar app Flask y DB configurada (importando como si estuviéramos dentro de backend/)
    from app import app  # type: ignore
    from extensions import db  # type: ignore
    from models.pedido import Pedido  # type: ignore

    actualizados = 0
    evaluados = 0

    with app.app_context():
        # Candidatos: pedidos claramente marcados como personalización o que contienen el prefijo
        # Nota: flexible por si existen variaciones de escritura
        candidatos = (
            Pedido.query.filter(
                (
                    (Pedido.tipo_pedido.ilike("%personal%"))
                    | (Pedido.arreglo_pedido.ilike("%ARREGLO FLORAL%"))
                    | (Pedido.arreglo_pedido.ilike("%Arreglo floral%"))
                    | (Pedido.arreglo_pedido.ilike("%arreglo floral%"))
                )
            ).all()
        )

        for p in candidatos:
            evaluados += 1
            texto = (p.arreglo_pedido or "").strip()
            nuevo_tipo = extract_tipo_from_arreglo(texto)

            if nuevo_tipo and nuevo_tipo.lower() not in ("arreglo floral", "arreglo", "floral"):
                # Solo actualizar si cambia realmente y no es el genérico
                if nuevo_tipo != p.arreglo_pedido:
                    p.arreglo_pedido = nuevo_tipo
                    # Es útil reflejarlo también en tipo_personalizacion si está vacío o genérico
                    if not p.tipo_personalizacion or p.tipo_personalizacion.strip().lower() in ("", "arreglo floral", "arreglo", "floral"):
                        p.tipo_personalizacion = nuevo_tipo
                    actualizados += 1

        if actualizados:
            db.session.commit()

    print(f"Evaluados: {evaluados}")
    print(f"Actualizados: {actualizados}")


if __name__ == "__main__":
    run()


