"""
Validaciones para el campo velocidad.
Reglas:
- Dígitos numéricos
- Empieza en 0 y va de 10 en 10 (0, 10, 20, 30, ...)
- No puede superar 200 km/h
"""
from ._generales import solo_numeros

VELOCIDAD_MAXIMA = 200


def validar_multiplo_diez(valor):
    """Valida que la velocidad sea múltiplo de 10 y no supere el máximo permitido."""
    try:
        numero = int(str(valor).strip())
    except (ValueError, TypeError):
        return False, "La velocidad debe ser un número entero"

    if numero < 0:
        return False, f"La velocidad no puede ser negativa, recibido '{valor}'"

    if numero % 10 != 0:
        return False, f"La velocidad debe ir de 10 en 10 (0, 10, 20, ...), recibido '{valor}'"

    if numero > VELOCIDAD_MAXIMA:
        return False, f"La velocidad no puede superar {VELOCIDAD_MAXIMA} km/h, recibido '{valor}'"

    return True, ""


def validar(valor):
    """
    Ejecuta todas las validaciones del campo velocidad.
    """
    errores = []
    nombre = "velocidad"

    if valor is None or str(valor).strip() == "":
        errores.append(f"El {nombre} no puede estar vacío")
        return errores

    valido, msg = solo_numeros(valor, nombre)
    if not valido:
        errores.append(msg)
        return errores

    valido, msg = validar_multiplo_diez(valor)
    if not valido:
        errores.append(msg)

    return errores
