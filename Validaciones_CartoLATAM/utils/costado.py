"""
Validaciones para el campo costado.
Reglas según tipo de capa:
- Líneas: debe ser 1 o 2
- Puntos: debe ser PAR o IMPAR (texto en mayúsculas)
"""

VALORES_VALIDOS_LINEA  = {"1", "2", 1, 2}
VALORES_VALIDOS_PUNTO  = {"PAR", "IMPAR"}


def validar_linea(valor):
    """Valida que el valor sea 1 o 2 (para capas de líneas)."""
    errores = []
    nombre = "costado"

    if valor is None or str(valor).strip() == "":
        errores.append(f"El {nombre} no puede estar vacío")
        return errores

    if valor not in VALORES_VALIDOS_LINEA:
        errores.append(f"El {nombre} debe ser 1 o 2, recibido '{valor}'")

    return errores


def validar_punto(valor):
    """Valida que el valor sea PAR o IMPAR (para capas de puntos)."""
    errores = []
    nombre = "costado"

    if valor is None or str(valor).strip() == "":
        errores.append(f"El {nombre} no puede estar vacío")
        return errores

    if str(valor).strip().upper() not in VALORES_VALIDOS_PUNTO:
        errores.append(
            f"El {nombre} debe ser PAR o IMPAR, recibido '{valor}'"
        )

    return errores


def validar(valor, es_punto=False):
    """
    Ejecuta las validaciones del campo costado según el tipo de capa.

    :param valor: valor del campo costado
    :param es_punto: True si la capa es de puntos, False si es de líneas
    """
    if es_punto:
        return validar_punto(valor)
    return validar_linea(valor)
