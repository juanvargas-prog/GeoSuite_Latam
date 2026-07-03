"""
manzana.py
----------
Validaciones para el campo manzana.

Reglas:
- Campo opcional: se permite vacío/nulo sin error.
- Alfanumérico, todo en MAYÚSCULAS.
- Debe comenzar con el prefijo estandarizado "MZ" seguido de
  un espacio y un identificador (letra, número o combinación).
  Ejemplos válidos: "MZ A", "MZ 12", "MZ B3"
- Sin caracteres especiales (solo letras, números y espacios).
"""

import re

_PATRON_MANZANA = re.compile(r'^MZ\s+[A-Z0-9]+$')


def validar(valor):
    """
    Valida el campo manzana.
    Retorna lista de errores (vacía si todo está correcto).
    """
    errores = []
    nombre = "manzana"

    if valor is None or str(valor).strip() == "":
        return errores  # campo opcional

    valor = str(valor).strip()

    if valor != valor.upper():
        errores.append(f"El {nombre} debe estar en MAYÚSCULAS, recibido: '{valor}'")
        return errores

    if not _PATRON_MANZANA.match(valor):
        errores.append(
            f"El {nombre} debe tener el formato 'MZ <identificador>' "
            f"(ej: 'MZ A', 'MZ 12', 'MZ B3'), recibido: '{valor}'"
        )

    return errores
