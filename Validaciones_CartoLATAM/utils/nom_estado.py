"""
Validaciones para el campo nom_estado.
Reglas:
- Deben ser mayúsculas
- Son siglas del nombre del estado (letras y/o números, sin espacios)
"""
from ._generales import en_mayusculas, sin_espacios_extremos


def validar_es_sigla(valor):
    """Valida que sea una sigla alfanumérica en mayúscula sin espacios (ej: SP, RJ, 01)."""
    if not isinstance(valor, str):
        valor = str(valor)
    valor = valor.strip()
    if not valor.isalnum():
        return False, (
            f"El nom_estado debe ser una sigla (letras y/o números, sin espacios), "
            f"recibido '{valor}'"
        )
    return True, ""


def validar(valor):
    """
    Ejecuta todas las validaciones del campo nom_estado.
    """
    errores = []
    nombre = "nom_estado"

    if valor is None or str(valor).strip() == "":
        errores.append(f"El {nombre} no puede estar vacío")
        return errores

    valido, msg = sin_espacios_extremos(valor, nombre)
    if not valido:
        errores.append(msg)

    valido, msg = validar_es_sigla(valor)
    if not valido:
        errores.append(msg)

    valido, msg = en_mayusculas(valor, nombre)
    if not valido:
        errores.append(msg)

    return errores
