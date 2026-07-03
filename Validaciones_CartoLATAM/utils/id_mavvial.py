"""
Validaciones para el campo id_mavvial.
Reglas:
- Debe contener solo números
"""
from ._generales import solo_numeros


def validar(valor):
    """
    Ejecuta todas las validaciones del campo id_mavvial.
    """
    errores = []
    nombre = "id_mavvial"

    if valor is None or str(valor).strip() == "":
        errores.append(f"El {nombre} no puede estar vacío")
        return errores

    valido, msg = solo_numeros(valor, nombre)
    if not valido:
        errores.append(msg)

    return errores
