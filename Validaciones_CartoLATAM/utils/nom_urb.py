"""
nom_urb.py
----------
Validaciones para el campo nom_urb (nombre de urbanización).

Reglas:
- Campo opcional: se permite vacío/nulo sin error.
- Texto en MAYÚSCULAS.
- Sin caracteres especiales (se permiten letras, números, espacios
  y comilla simple para nombres como "URB LAS FLORES").
- Sin espacios al inicio o al final.
- Sin doble espacio.
"""

from ._generales import (
    en_mayusculas,
    sin_espacios_extremos,
    sin_doble_espacio,
    sin_caracteres_especiales_con_numeros,
)


def validar(valor, pais="default"):
    """
    Valida el campo nom_urb.
    Retorna lista de errores (vacía si todo está correcto).
    """
    errores = []
    nombre = "nom_urb"

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
