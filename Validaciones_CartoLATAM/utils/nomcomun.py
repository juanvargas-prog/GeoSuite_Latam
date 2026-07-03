"""
Validaciones para el campo nomcomun.
Reglas:
- Aplica las validaciones generales de texto: sin caracteres especiales, mayúsculas, sin espacios extremos
"""
from ._generales import validar_texto_estandar


def validar(valor):
    """
    Ejecuta todas las validaciones del campo nomcomun.
    """
    errores = []
    nombre = "nomcomun"

    if valor is None or str(valor).strip() == "":
        return errores

    errores.extend(validar_texto_estandar(valor, nombre))
    return errores
