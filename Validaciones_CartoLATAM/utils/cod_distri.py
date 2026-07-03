"""
Validaciones para el campo cod_distri.
Reglas:
- Se compone de 9 dígitos numéricos (Brasil) o 6 dígitos (Perú, El Salvador, Costa Rica)
- Los primeros dígitos deben coincidir con el código padre según el país

Nota: la validación de jerarquía (prefijo con cod_mun u otro padre) se realiza
de forma centralizada en geo_codigos.py para todos los países.
"""
from ._generales import solo_numeros


def validar(valor):
    """
    Ejecuta las validaciones básicas del campo cod_distri.
    La cantidad de dígitos varía por país y se valida en geo_codigos.py.

    :param valor: valor del campo cod_distri
    """
    errores = []
    nombre = "cod_distri"

    if valor is None or str(valor).strip() == "":
        errores.append(f"El {nombre} no puede estar vacío")
        return errores

    valido, msg = solo_numeros(valor, nombre)
    if not valido:
        errores.append(msg)

    return errores
