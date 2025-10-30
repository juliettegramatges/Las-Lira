"""
Normaliza el tipo de arreglo en `pedidos` directamente con sqlite3, sin cargar Flask.

Objetivo: para pedidos de personalización o con "ARREGLO FLORAL ..." en `arreglo_pedido`,
extraer el tipo específico y guardarlo en `arreglo_pedido` (Title Case). Si existe
la columna `tipo_personalizacion`, también la actualiza.
"""

import os
import re
import sqlite3
from typing import Optional


DB_PATHS = [
    # Preferida por app.py
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "instance", "laslira.db")),
    # Alternativas encontradas en el repo
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "las_lira.db")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "instance", "las_lira.db")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "instance", "laslira.db")),
]


def pick_db_path() -> str:
    for p in DB_PATHS:
        if os.path.exists(p):
            return p
    # Fallback al más probable por configuración
    return DB_PATHS[0]


def _clean_spaces(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def extract_tipo_from_arreglo(arreglo_texto: str) -> Optional[str]:
    if not arreglo_texto:
        return None
    texto = arreglo_texto.strip()

    patron = re.compile(r"(?i)^\s*arreglo\s*floral\s*(?:[-:–—·]*\s*)?(?P<tipo>.+?)\s*$")
    m = patron.match(texto)
    if not m:
        m2 = re.search(r"(?i)arreglo\s*floral\s*(?:[-:–—·]*\s*)?(?P<tipo>.+)$", texto)
        if not m2:
            return None
        candidato = m2.group("tipo").strip()
    else:
        candidato = m.group("tipo").strip()

    candidato = re.sub(r"(?i)^(tipo\s*(de)?\s*|de\s+)", "", candidato).strip()
    candidato = _clean_spaces(candidato)
    if len(candidato) < 2:
        return None
    tipo_title = " ".join([
        w.upper() if w.isupper() and len(w) <= 4 else w.capitalize() for w in candidato.split(" ")
    ])
    return tipo_title


def column_exists(cursor: sqlite3.Cursor, table: str, column: str) -> bool:
    cursor.execute(f"PRAGMA table_info({table})")
    cols = [row[1] for row in cursor.fetchall()]
    return column in cols


def run():
    db_path = pick_db_path()
    print(f"Usando DB: {db_path}")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    has_tipo_personalizacion = column_exists(cur, "pedidos", "tipo_personalizacion")

    # Seleccionar candidatos
    cur.execute(
        """
        SELECT id, arreglo_pedido, tipo_pedido, COALESCE(tipo_personalizacion, '')
        FROM pedidos
        WHERE (
            LOWER(COALESCE(tipo_pedido, '')) LIKE '%personal%'
            OR LOWER(COALESCE(arreglo_pedido, '')) LIKE '%arreglo floral%'
        )
        """
    )
    rows = cur.fetchall()

    evaluados = 0
    actualizados = 0

    for row in rows:
        evaluados += 1
        pedido_id, arreglo_pedido, tipo_pedido, tipo_pers = row
        nuevo_tipo = extract_tipo_from_arreglo(arreglo_pedido or "")
        if nuevo_tipo and nuevo_tipo.lower() not in ("arreglo floral", "arreglo", "floral"):
            # Evitar escribir si no cambia
            if nuevo_tipo != (arreglo_pedido or ""):
                if has_tipo_personalizacion:
                    cur.execute(
                        "UPDATE pedidos SET arreglo_pedido = ?, tipo_personalizacion = ? WHERE id = ?",
                        (nuevo_tipo, (tipo_pers or nuevo_tipo), pedido_id),
                    )
                else:
                    cur.execute(
                        "UPDATE pedidos SET arreglo_pedido = ? WHERE id = ?",
                        (nuevo_tipo, pedido_id),
                    )
                actualizados += 1

    if actualizados:
        conn.commit()

    conn.close()
    print(f"Evaluados: {evaluados}")
    print(f"Actualizados: {actualizados}")


if __name__ == "__main__":
    run()


