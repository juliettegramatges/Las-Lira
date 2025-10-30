"""
Actualiza tipo_personalizacion a partir de arreglo_pedido cuando:
- tipo_personalizacion es NULL o 'ARREGLO FLORAL' (genérico)
- arreglo_pedido comienza con 'ARREGLO ' y NO es 'ARREGLO FLORAL'

Mantiene el nombre completo (producto específico) y lo guarda en Title Case.
"""

import os
import re
import sqlite3


DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'instance', 'laslira.db'))


def title_keep_acronyms(text: str) -> str:
    return ' '.join([w.upper() if w.isupper() and len(w) <= 4 else w.capitalize() for w in text.split(' ')])


def is_specific_arreglo(nombre: str) -> bool:
    if not nombre:
        return False
    nombre = nombre.strip()
    if re.match(r"(?i)^arreglo\s+floral\b", nombre):
        return False
    return bool(re.match(r"(?i)^arreglo\s+.+", nombre))


def run():
    if not os.path.exists(DB_PATH):
        print(f"No existe la base: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Seleccionar candidatos
    cur.execute(
        """
        SELECT id, arreglo_pedido, tipo_personalizacion
        FROM pedidos
        WHERE arreglo_pedido IS NOT NULL
          AND TRIM(arreglo_pedido) != ''
          AND (
                tipo_personalizacion IS NULL
             OR UPPER(TRIM(tipo_personalizacion)) = 'ARREGLO FLORAL'
          )
        """
    )
    rows = cur.fetchall()

    actualizados = 0
    for pid, arreglo, tipo in rows:
        if is_specific_arreglo(arreglo):
            nuevo = re.sub(r"\s+", " ", arreglo.strip())
            nuevo = title_keep_acronyms(nuevo)
            cur.execute(
                "UPDATE pedidos SET tipo_personalizacion = ? WHERE id = ?",
                (nuevo, pid),
            )
            actualizados += 1

    if actualizados:
        conn.commit()
    conn.close()
    print(f"Actualizados: {actualizados}")


if __name__ == '__main__':
    run()


