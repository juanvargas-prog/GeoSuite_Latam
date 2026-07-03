"""
casa_lote.py
------------
Validaciones para el campo casa_lote.

Reglas:
- Campo opcional: se permite vacío/nulo sin error.
- Alfanumérico, todo en MAYÚSCULAS.
- Debe comenzar con el prefijo estandarizado "LT" seguido de
  un espacio y un identificador formado por tokens separados por espacio,
  donde cada token es solo letras o solo números (nunca pegados).
  Ejemplos válidos: "LT 5", "LT 12", "LT 3 A", "LT A 3"
  Ejemplos inválidos: "LT 3A", "LT A3"
- Sin caracteres especiales (solo letras, números y espacios).
"""

import re

# Cada token tras "LT " debe ser todo letras o todo números, separados por espacio
_PATRON_CASA_LOTE = re.compile(r'^LT\s+([A-Z]+|[0-9]+)(\s+([A-Z]+|[0-9]+))*$')


def validar(valor):
    """
    Valida el campo casa_lote.
    Retorna lista de errores (vacía si todo está correcto).
    """
    errores = []
    nombre = "casa_lote"

    if valor is None or str(valor).strip() == "":
        return errores  # campo opcional

    valor = str(valor).strip()

    if valor != valor.upper():
        errores.append(f"El {nombre} debe estar en MAYÚSCULAS, recibido: '{valor}'")
        return errores

    if not _PATRON_CASA_LOTE.match(valor):
        errores.append(
            f"El {nombre} debe tener el formato 'LT <identificador>' donde letras y números "
            f"van separados por espacio (ej: 'LT 5', 'LT 12', 'LT 3 A'), recibido: '{valor}'"
        )

    return errores
