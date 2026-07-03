"""
Validaciones para el campo generadora.
Reglas:
- No puede estar vacío (salvo Guatemala con tipo_dir=MZCASA)
- Puede ser cualquier combinación de letras, números y guion (-)
  Ejemplos válidos: 100, 200, A, B, 3A, MZ-A, LT-5
"""
from ._generales import en_mayusculas, sin_espacios_extremos
import re

_RE_GENERADORA = re.compile(r"^[A-Za-z0-9\-]+$")


def validar(valor, tipo_dir=None, pais="default"):
    """Valida el campo generadora: alfanumérico con guion, no vacío."""
    errores = []
    nombre = "generadora"

    if valor is None or str(valor).strip() == "":
        # Guatemala MZCASA: generadora puede estar vacía
        if pais == "Guatemala" and tipo_dir and str(tipo_dir).strip().upper() == "MZCASA":
            return errores
        errores.append(f"El {nombre} no puede estar vacío")
        return errores

    val_str = str(valor).strip()

    valido, msg = sin_espacios_extremos(val_str, nombre)
    if not valido:
        errores.append(msg)

    if not _RE_GENERADORA.match(val_str):
        errores.append(
            f"El {nombre} solo puede contener letras, números y guion (-), "
            f"recibido '{val_str}'"
        )

    valido, msg = en_mayusculas(val_str, nombre)
    if not valido:
        errores.append(msg)

    return errores
