"""
Validaciones para el campo placa.
Reglas:
- Debe tener solo números
- Los dígitos únicos deben tener un 0 a la izquierda (1 → 01, 5 → 05, etc.)
"""
from ._generales import solo_numeros


def validar_cero_izquierda(valor):
    """
    Valida que los dígitos de un solo carácter tengan 0 a la izquierda.
    Es decir, no se permite '1', '5', etc. — deben ser '01', '05', etc.
    """
    valor_str = str(valor).strip()
    if len(valor_str) == 1:
        return (
            False,
            f"La placa '{valor_str}' debe tener 0 a la izquierda (ej: '0{valor_str}')",
        )
    return True, ""


def validar(valor):
    """
    Ejecuta todas las validaciones del campo placa.
    """
    errores = []
    nombre = "placa"

    if valor is None or str(valor).strip() == "":
        errores.append(f"El {nombre} no puede estar vacío")
        return errores

    valido, msg = solo_numeros(valor, nombre)
    if not valido:
        errores.append(msg)
        return errores

    valido, msg = validar_cero_izquierda(valor)
    if not valido:
        errores.append(msg)

    return errores
