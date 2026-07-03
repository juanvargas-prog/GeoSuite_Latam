"""
Validaciones para el campo cod_mun.
Reglas:
- Se compone de 7 dígitos numéricos
- Los 2 primeros corresponden al cod_estado
- Los 5 dígitos restantes son códigos del municipio dentro del estado

Nota: la validación de jerarquía (prefijo con cod_estado) se realiza
de forma centralizada en geo_codigos.py para todos los países.
"""
from ._generales import solo_numeros, cantidad_digitos


def validar(valor):
    """
    Ejecuta todas las validaciones del campo cod_mun.

    :param valor: valor del campo cod_mun
    """
    errores = []
    nombre = "cod_mun"

    if valor is None or str(valor).strip() == "":
        errores.append(f"El {nombre} no puede estar vacío")
        return errores

    valido, msg = solo_numeros(valor, nombre)
    if not valido:
        errores.append(msg)
        return errores

    valido, msg = cantidad_digitos(valor, 7, nombre)
    if not valido:
        errores.append(msg)

    return errores
