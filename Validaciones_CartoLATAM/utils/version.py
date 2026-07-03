"""
Validaciones para el campo version.
Reglas:
- No debe estar vacío si fecha o marca tienen información
- Debe estar compuesto por V#-AA (ej: V1-26, V2-25)
- Debe estar en mayúscula
"""
import re

# V seguido de uno o más dígitos, guion y exactamente 2 dígitos del año
PATRON_VERSION = re.compile(r"^V\d+-\d{2}$")


def validar_formato(valor):
    """Valida que la version tenga el formato V#-AA (ej: V1-26)."""
    if not isinstance(valor, str):
        valor = str(valor)
    if not PATRON_VERSION.match(valor.strip()):
        return False, f"La version debe tener formato V#-AA (ej: V1-26, V2-25), recibido '{valor}'"
    return True, ""


def validar_mayuscula(valor):
    """Valida que la version esté en mayúsculas."""
    if not isinstance(valor, str):
        valor = str(valor)
    if valor != valor.upper():
        return False, f"La version debe estar en mayúsculas, recibido '{valor}'"
    return True, ""


def validar_coherencia(version, fecha, marca):
    """Si fecha o marca tienen información, version no debe estar vacío."""
    fecha_tiene_info = fecha is not None and str(fecha).strip() != ""
    marca_tiene_info = marca is not None and str(marca).strip() != ""
    version_vacio = version is None or str(version).strip() == ""

    if (fecha_tiene_info or marca_tiene_info) and version_vacio:
        return False, "La version no debe estar vacía si fecha o marca tienen información"
    return True, ""


def validar(valor, fecha=None, marca=None):
    """
    Ejecuta todas las validaciones del campo version.

    :param valor: valor del campo version
    :param fecha: valor del campo fecha
    :param marca: valor del campo marca
    """
    errores = []

    valido, msg = validar_coherencia(valor, fecha, marca)
    if not valido:
        errores.append(msg)

    if valor is None or str(valor).strip() == "":
        return errores

    valido, msg = validar_mayuscula(valor)
    if not valido:
        errores.append(msg)

    valido, msg = validar_formato(valor)
    if not valido:
        errores.append(msg)

    return errores
