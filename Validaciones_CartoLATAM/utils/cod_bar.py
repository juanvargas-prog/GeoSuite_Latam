"""
Validaciones para el campo cod_bar.
Reglas:
- (Pendiente de definir reglas específicas)
- Se aplican las generales: sin espacios extremos
"""
from ._generales import sin_espacios_extremos


def validar(valor):
    """
    Ejecuta todas las validaciones del campo cod_bar.
    Por ahora solo aplica validaciones generales.
    """
    errores = []
    nombre = "cod_bar"

    if valor is None or str(valor).strip() == "":
        return errores

    valido, msg = sin_espacios_extremos(valor, nombre)
    if not valido:
        errores.append(msg)

    return errores
