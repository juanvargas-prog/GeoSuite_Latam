"""
Validaciones para el campo id_capa.
Reglas:
- No debe estar vacío
- Debe ser identificador único
- Solo números

Nota: para la validación de unicidad se recibe un Counter (collections.Counter)
en lugar de una lista, para que el lookup sea O(1) en vez de O(n).
"""
from ._generales import no_vacio, solo_numeros


def validar(valor, contador_ids=None):
    """
    Ejecuta todas las validaciones del campo id_capa.
    Retorna lista de errores (vacía si todo está correcto).

    :param valor: valor del campo a validar
    :param contador_ids: collections.Counter con todos los id_capa de la capa
    """
    errores = []
    nombre = "id_capa"

    valido, msg = no_vacio(valor, nombre)
    if not valido:
        errores.append(msg)
        return errores

    valido, msg = solo_numeros(valor, nombre)
    if not valido:
        errores.append(msg)

    if contador_ids is not None:
        if contador_ids[valor] > 1:
            errores.append(f"El id_capa '{valor}' está duplicado, debe ser único")

    return errores
