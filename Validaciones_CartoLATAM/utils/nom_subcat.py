"""
nom_subcat.py
-------------
Validaciones para el campo nom_subcat (subcategoría de POI).

Reglas:
- No puede estar vacío.
- Debe estar en MAYÚSCULAS.
- Debe existir dentro de las subcategorías válidas de su categoría padre.
  Si la categoría padre no es válida, este campo no se valida contra el catálogo.
- Sin caracteres especiales (letras, números, espacios y Ñ).

La lista válida se recibe como parámetro (dict {CATEGORIA: set(SUBCATEGORIAS)})
para evitar una conexión a Sheets por cada fila validada.
"""

from ._generales import en_mayusculas, sin_espacios_extremos


def validar(valor, categoria=None, categorias_validas=None, pais="default"):
    """
    Valida el campo nom_subcat.

    :param valor:             valor del campo
    :param categoria:         valor del campo categoria de la misma fila
    :param categorias_validas: dict {CATEGORIA: set(SUBCATEGORIAS)} cargado desde Sheets.
                               Si es None, solo se validan formato y mayúsculas.
    :param pais:              nombre del país (para mensajes de error)
    """
    errores = []
    nombre  = "nom_subcat"

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

    # Validar contra catálogo solo si tenemos la categoría padre
    if categorias_validas is not None and categoria is not None:
        cat_upper = str(categoria).strip().upper()

        if cat_upper not in categorias_validas:
            # La categoría ya reportará su propio error — no duplicamos
            return errores

        subcats_validas = categorias_validas[cat_upper]
        if valor not in subcats_validas:
            errores.append(
                f"La subcategoría '{valor}' no es válida para la categoría "
                f"'{cat_upper}' en {pais}. "
                f"Subcategorías válidas: {', '.join(sorted(subcats_validas))}"
            )

    return errores
