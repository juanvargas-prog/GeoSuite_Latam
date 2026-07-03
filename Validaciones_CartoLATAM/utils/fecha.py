"""
Validaciones para el campo fecha.
Reglas:
- Formato mm-aaaa
- No debe estar vacío si marca o version tienen información
"""
import re

PATRON_FECHA = re.compile(r"^(0[1-9]|1[0-2])-\d{4}$")


def validar_formato(valor):
    """Valida que la fecha tenga el formato mm-aaaa."""
    if not isinstance(valor, str):
        valor = str(valor)
    if not PATRON_FECHA.match(valor.strip()):
        return False, f"La fecha debe estar en formato mm-aaaa, recibido '{valor}'"
    return True, ""


def validar_coherencia(fecha, marca, version):
    """Si marca o version tienen información, fecha no debe estar vacío."""
    marca_tiene_info = marca is not None and str(marca).strip() != ""
    version_tiene_info = version is not None and str(version).strip() != ""
    fecha_vacio = fecha is None or str(fecha).strip() == ""

    if (marca_tiene_info or version_tiene_info) and fecha_vacio:
        return False, "La fecha no debe estar vacía si marca o version tienen información"
    return True, ""


def validar(valor, marca=None, version=None):
    """
    Ejecuta todas las validaciones del campo fecha.

    :param valor: valor del campo fecha
    :param marca: valor del campo marca
    :param version: valor del campo version
    """
    errores = []

    valido, msg = validar_coherencia(valor, marca, version)
    if not valido:
        errores.append(msg)

    if valor is None or str(valor).strip() == "":
        return errores

    valido, msg = validar_formato(valor)
    if not valido:
        errores.append(msg)

    return errores
