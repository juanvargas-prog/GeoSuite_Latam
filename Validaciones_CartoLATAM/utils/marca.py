"""
Validaciones para el campo marca.
Reglas:
- Las marcas deben ser 1, 2, 3 o 4
- No debe estar vacío si fecha o version tienen información
"""
VALORES_VALIDOS = {1, 2, 3, 4, "1", "2", "3", "4"}


def validar_valor_permitido(valor):
    """Valida que el valor sea 1, 2, 3 o 4."""
    if valor not in VALORES_VALIDOS:
        return False, f"La marca debe ser 1, 2, 3 o 4, recibido '{valor}'"
    return True, ""


def validar_coherencia(marca, fecha, version):
    """Si fecha o version tienen información, marca no debe estar vacío."""
    fecha_tiene_info = fecha is not None and str(fecha).strip() != ""
    version_tiene_info = version is not None and str(version).strip() != ""
    marca_vacio = marca is None or str(marca).strip() == ""

    if (fecha_tiene_info or version_tiene_info) and marca_vacio:
        return False, "La marca no debe estar vacía si fecha o version tienen información"
    return True, ""


def validar(valor, fecha=None, version=None):
    """
    Ejecuta todas las validaciones del campo marca.

    :param valor: valor del campo marca
    :param fecha: valor del campo fecha
    :param version: valor del campo version
    """
    errores = []

    valido, msg = validar_coherencia(valor, fecha, version)
    if not valido:
        errores.append(msg)

    if valor is None or str(valor).strip() == "":
        return errores

    valido, msg = validar_valor_permitido(valor)
    if not valido:
        errores.append(msg)

    return errores
