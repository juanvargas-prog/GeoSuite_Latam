"""
categoria.py
------------
Validaciones para el campo categoria (POI).

Reglas:
- No puede estar vacío.
- Debe estar en MAYÚSCULAS.
- Debe existir en el catálogo de categorías del país cargado desde Google Sheets.
- Sin caracteres especiales (letras, números, espacios y Ñ).

La lista válida se recibe como parámetro (dict {CATEGORIA: set(SUBCATEGORIAS)})
para evitar una conexión a Sheets por cada fila validada.
"""

from ._generales import en_mayusculas, sin_espacios_extremos


def validar(valor, categorias_validas=None, pais="default"):
    """
    Valida el campo categoria.

    :param valor:             valor del campo
    :param categorias_validas: dict {CATEGORIA: set(SUBCATEGORIAS)} cargado desde Sheets.
                               Si es None, solo se validan formato y mayúsculas.
    :param pais:              nombre del país (para mensajes de error)
    """
    errores = []
    nombre  = "categoria"

    if valor is None or str(valor).strip() == "":
        errores.append(f"El {nombre} no puede estar vacío")
        return errores

    valor = str(valor).strip()

    valido, msg = sin_espacios_extremos(valor, nombre)
    if not valido:
        errores.append(msg)

    valido, msg = en_mayusculas(valor, nombre)
    if not valido:
        errores.append(msg)

    if errores:
        return errores

    # Validar contra catálogo
    if categorias_validas is not None:
        if valor not in categorias_validas:
            errores.append(
                f"La {nombre} '{valor}' no es válida para {pais}. "
                f"Categorías disponibles: {', '.join(sorted(categorias_validas.keys()))}"
            )

    return errores
