"""
Validaciones para el campo oneway.
Reglas:
- Solo valores permitidos para Brasil: B (ambos sentidos) y F (un sentido)
- Siempre en mayúsculas
"""
from ._generales import en_mayusculas, sin_espacios_extremos

VALORES_VALIDOS = {"B", "F", "N"}


def validar_valor_permitido(valor):
    """Valida que el valor sea B o F."""
    if str(valor).strip().upper() not in VALORES_VALIDOS:
        return (
            False,
            f"El oneway '{valor}' no es válido. Valores permitidos: B (ambos sentidos), F (un sentido), N (no aplica)",
        )
    return True, ""


def validar(valor):
    """
    Ejecuta todas las validaciones del campo oneway.
    """
    errores = []
    nombre = "oneway"

    if valor is None or str(valor).strip() == "":
        return errores

    valido, msg = sin_espacios_extremos(valor, nombre)
    if not valido:
        errores.append(msg)

    valido, msg = en_mayusculas(valor, nombre)
    if not valido:
        errores.append(msg)

    valido, msg = validar_valor_permitido(valor)
    if not valido:
        errores.append(msg)

    return errores