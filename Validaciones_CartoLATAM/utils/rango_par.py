"""
Validaciones para el campo rango_par.
Reglas:
- Formato aceptado: "numero" o "numero-numero"
  Ejemplos válidos: "200", "100-400"
- Los números deben ser pares
- Si hay rango (dos números), el primero debe ser ≤ al segundo
"""
import re

# Acepta un número solo ("200") o un rango ("100-400")
PATRON_RANGO = re.compile(r"^\d+(-\d+)?$")


def validar_formato(valor):
    """Valida que tenga el formato 'numero' o 'numero-numero'."""
    if not isinstance(valor, str):
        valor = str(valor)
    if not PATRON_RANGO.match(valor.strip()):
        return False, (
            f"El rango_par debe tener formato 'numero' o 'numero-numero', "
            f"recibido '{valor}'"
        )
    return True, ""


def _parsear(valor):
    """Retorna (num1, num2) donde num2 puede ser None si es valor único."""
    partes = str(valor).strip().split("-")
    num1 = int(partes[0])
    num2 = int(partes[1]) if len(partes) == 2 else None
    return num1, num2


def validar_pares(valor):
    """Valida que el/los números del rango sean pares."""
    try:
        num1, num2 = _parsear(valor)
    except (ValueError, IndexError):
        return False, f"No se pudo interpretar el rango_par '{valor}'"

    impares = []
    if num1 % 2 != 0:
        impares.append(str(num1))
    if num2 is not None and num2 % 2 != 0:
        impares.append(str(num2))

    if impares:
        return False, (
            f"Los números del rango_par deben ser pares; "
            f"{'valor impar' if len(impares) == 1 else 'valores impares'}: "
            f"{', '.join(impares)}"
        )
    return True, ""


def validar_orden(valor):
    """Valida que el primer número sea ≤ al segundo (solo aplica con rango)."""
    try:
        num1, num2 = _parsear(valor)
    except (ValueError, IndexError):
        return False, f"No se pudo interpretar el rango_par '{valor}'"

    if num2 is not None and num1 > num2:
        return (
            False,
            f"El primer número del rango_par ({num1}) debe ser ≤ al segundo ({num2})",
        )
    return True, ""


def validar(valor):
    """Ejecuta todas las validaciones del campo rango_par."""
    errores = []
    nombre = "rango_par"

    if valor is None or str(valor).strip() == "":
        errores.append(f"El {nombre} no puede estar vacío")
        return errores

    valido, msg = validar_formato(valor)
    if not valido:
        errores.append(msg)
        return errores

    valido, msg = validar_pares(valor)
    if not valido:
        errores.append(msg)

    valido, msg = validar_orden(valor)
    if not valido:
        errores.append(msg)

    return errores
