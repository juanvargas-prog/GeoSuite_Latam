"""
tipo_urb.py
-----------
Valida el campo tipo_urb contra el catálogo de tipos urbanos del país.
Los tipos se obtienen del mismo Google Sheet que tipovia,
filtrando las filas donde TIPO == "URB".

Reglas:
- Siempre en mayúsculas
- Sin espacios al inicio o final
- Debe pertenecer a la lista de abreviaturas URB válidas para el país
- Campo opcional: si está vacío no genera error
"""
from ._generales import en_mayusculas, sin_espacios_extremos


def validar_abreviatura_urb(valor, abreviaturas_validas):
    """Valida que el valor sea una abreviatura URB válida del conjunto dado."""
    if not abreviaturas_validas:
        return True, ""   # sin catálogo cargado, no se puede validar
    if valor not in abreviaturas_validas:
        muestra = ", ".join(sorted(abreviaturas_validas)[:8])
        sufijo  = " …" if len(abreviaturas_validas) > 8 else ""
        return False, (
            f"El tipo_urb '{valor}' no es una abreviatura urbana válida. "
            f"Valores aceptados: {muestra}{sufijo}"
        )
    return True, ""


def validar(valor, pais="", abreviaturas_urb=None):
    """
    Ejecuta todas las validaciones del campo tipo_urb.

    :param valor           : valor del campo tipo_urb
    :param pais            : nombre del país (informativo)
    :param abreviaturas_urb: set de abreviaturas URB válidas cargadas desde Sheets
    :returns               : lista de mensajes de error (vacía = válido)
    """
    errores = []

    if valor is None or str(valor).strip() == "":
        return errores  # campo opcional — vacío es válido

    valido, msg = sin_espacios_extremos(valor, "tipo_urb")
    if not valido:
        errores.append(msg)

    valido, msg = en_mayusculas(valor, "tipo_urb")
    if not valido:
        errores.append(msg)

    valido, msg = validar_abreviatura_urb(valor, abreviaturas_urb or set())
    if not valido:
        errores.append(msg)

    return errores
