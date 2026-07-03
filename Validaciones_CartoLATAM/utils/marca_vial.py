"""
Validaciones para el campo marca_vial.
Reglas:
- Siempre en mayúscula
"""
from ._generales import en_mayusculas, sin_espacios_extremos


def validar(valor):
    """
    Ejecuta todas las validaciones del campo marca_vial.
    """
    errores = []
    nombre = "marca_vial"

    if valor is None or str(valor).strip() == "":
        return errores

    valido, msg = sin_espacios_extremos(valor, nombre)
    if not valido:
        errores.append(msg)

    valido, msg = en_mayusculas(valor, nombre)
    if not valido:
        errores.append(msg)

    return errores
