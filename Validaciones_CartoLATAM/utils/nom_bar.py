"""
Validaciones para el campo nom_bar.
Reglas:
- Admite letras Y números (alfanumérico), además de espacios y comilla simple (')
- Sin espacios al inicio o al final
- Sin doble espacio
- En mayúsculas
- Sin caracteres especiales (salvo los permitidos por país)
- Campo opcional: se omite si está vacío
"""
from ._generales import (
    sin_espacios_extremos,
    sin_doble_espacio,
    sin_caracteres_especiales_con_numeros,
    en_mayusculas,
)


def validar(valor, pais="default"):
    """
    Ejecuta todas las validaciones del campo nom_bar.

    :param valor: valor del campo nom_bar
    :param pais:  nombre del país (afecta los caracteres permitidos)
    """
    errores = []
    nombre = "nom_bar"

    if valor is None or str(valor).strip() == "":
        return errores  # campo opcional

    valor = str(valor)

    valido, msg = sin_espacios_extremos(valor, nombre)
    if not valido: errores.append(msg)

    valido, msg = sin_doble_espacio(valor, nombre)
    if not valido: errores.append(msg)

    valido, msg = sin_caracteres_especiales_con_numeros(valor, nombre, pais=pais)
    if not valido: errores.append(msg)

    valido, msg = en_mayusculas(valor, nombre)
    if not valido: errores.append(msg)

    return errores
