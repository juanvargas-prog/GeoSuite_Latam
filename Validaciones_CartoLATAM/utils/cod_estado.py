"""
Validaciones para el campo cod_estado.
Reglas:
- Debe tener solo dos dígitos numéricos
"""
from ._generales import solo_numeros, cantidad_digitos


def validar(valor):
    """
    Ejecuta todas las validaciones del campo cod_estado.
    """
    errores = []
    nombre = "cod_estado"

    if valor is None or str(valor).strip() == "":
        errores.append(f"El {nombre} no puede estar vacío")
        return errores

    valido, msg = solo_numeros(valor, nombre)
    if not valido:
        errores.append(msg)
        return errores

    valido, msg = cantidad_digitos(valor, 2, nombre)
    if not valido:
        errores.append(msg)

    return errores
