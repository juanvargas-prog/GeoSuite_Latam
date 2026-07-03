"""
Validaciones para el campo rango_imp.
Reglas:
- Formato aceptado: "numero" o "numero-numero"
  Ejemplos válidos: "101", "101-399"
- Los números deben ser impares
- Si hay rango (dos números), el primero debe ser ≤ al segundo
"""
import re

# Acepta un número solo ("101") o un rango ("101-399")
PATRON_RANGO = re.compile(r"^\d+(-\d+)?$")


def validar_formato(valor):
    """Valida que tenga el formato 'numero' o 'numero-numero'."""
    if not isinstance(valor, str):
        valor = str(valor)
    if not PATRON_RANGO.match(valor.strip()):
        return False, (
            f"El rango_imp debe tener formato 'numero' o 'numero-numero', "
            f"recibido '{valor}'"
        )
    return True, ""


def _parsear(valor):
    """Retorna (num1, num2) donde num2 puede ser None si es valor único."""
    partes = str(valor).strip().split("-")
    num1 = int(partes[0])
    num2 = int(partes[1]) if len(partes) == 2 else None
    return num1, num2


def validar_impares(valor):
    """Valida que el/los números del rango sean impares."""
    try:
        num1, num2 = _parsear(valor)
    except (ValueError, IndexError):
        return False, f"No se pudo interpretar el rango_imp '{valor}'"

    pares = []
    if num1 % 2 == 0:
        pares.append(str(num1))
    if num2 is not None and num2 % 2 == 0:
        pares.append(str(num2))

    if pares:
        return False, (
            f"Los números del rango_imp deben ser impares; "
            f"{'valor par' if len(pares) == 1 else 'valores pares'}: "
            f"{', '.join(pares)}"
        )
    return True, ""


def validar_orden(valor):
    """Valida que el primer número sea ≤ al segundo (solo aplica con rango)."""
    try:
        num1, num2 = _parsear(valor)
    except (ValueError, IndexError):
        return False, f"No se pudo interpretar el rango_imp '{valor}'"

    if num2 is not None and num1 > num2:
        return (
            False,
            f"El primer número del rango_imp ({num1}) debe ser ≤ al segundo ({num2})",
        )
    return True, ""


def validar(valor):
    """Ejecuta todas las validaciones del campo rango_imp."""
    errores = []
    nombre = "rango_imp"

    if valor is None or str(valor).strip() == "":
        errores.append(f"El {nombre} no puede estar vacío")
        return errores

    valido, msg = validar_formato(valor)
    if not valido:
        errores.append(msg)
        return errores

    valido, msg = validar_impares(valor)
    if not valido:
        errores.append(msg)

    valido, msg = validar_orden(valor)
    if not valido:
        errores.append(msg)

    return errores
