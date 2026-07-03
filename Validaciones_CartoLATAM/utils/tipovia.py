"""
Validaciones para el campo tipovia.
Reglas:
- Sin caracteres especiales (comilla simple permitida)
- Siempre en mayúscula
- Debe pertenecer a la lista de abreviaturas válidas para el país
- Debe tener información si nomvia o nomvtotal tienen información,
  salvo que nomvia == nomvtotal (vía sin tipo de vía explícito).

Las abreviaturas válidas se cargan desde Google Sheets a través de
utils.sheets_loader y se pasan como parámetro desde validar_capa.py.
"""
from ._generales import en_mayusculas, sin_espacios_extremos


def validar_abreviatura(valor, abreviaturas_validas):
    """Valida que el valor sea una abreviatura válida del conjunto dado."""
    if valor is None or str(valor).strip() == "":
        return True, ""
    if not abreviaturas_validas:
        return True, ""  # sin conjunto cargado, no se puede validar
    if valor not in abreviaturas_validas:
        return False, f"El tipovia '{valor}' no es una abreviatura válida"
    return True, ""


def validar_coherencia(tipovia, nomvia, nomvtotal, tipo_dir=None, pais="default"):
    """
    Si nomvia o nomvtotal tienen información, tipovia también debe tenerla.

    Excepción 1 — sin tipo de vía: si nomvia y nomvtotal tienen el mismo valor,
    la dirección no usa tipo de vía; tipovia puede estar vacío.

    Excepción 2 — Guatemala MZCASA: todos los campos de vía pueden estar vacíos.
    """
    if pais == "Guatemala" and tipo_dir and str(tipo_dir).strip().upper() == "MZCASA":
        return True, ""

    nomvia_tiene_info    = nomvia    is not None and str(nomvia).strip()    != ""
    nomvtotal_tiene_info = nomvtotal is not None and str(nomvtotal).strip() != ""
    tipovia_tiene_info   = tipovia   is not None and str(tipovia).strip()   != ""

    if tipovia_tiene_info or not (nomvia_tiene_info or nomvtotal_tiene_info):
        return True, ""

    # Excepción: nomvia == nomvtotal → calle sin tipo de vía, tipovia puede estar vacío
    if nomvia_tiene_info and nomvtotal_tiene_info:
        if str(nomvia).strip().upper() == str(nomvtotal).strip().upper():
            return True, ""

    return False, "Si nomvia o nomvtotal tienen información, tipovia también debe tenerla"


def validar(valor, nomvia=None, nomvtotal=None, pais="Brasil", abreviaturas=None,
            tipo_dir=None):
    """
    Ejecuta todas las validaciones del campo tipovia.

    :param valor:       valor del campo tipovia
    :param nomvia:      valor del campo nomvia (para coherencia)
    :param nomvtotal:   valor del campo nomvtotal (para coherencia)
    :param pais:        nombre del país
    :param abreviaturas: set de abreviaturas válidas cargado desde Sheets
    :param tipo_dir:    valor del campo tipo_dir (para excepción Guatemala MZCASA)
    """
    errores = []
    nombre  = "tipovia"

    valido, msg = validar_coherencia(valor, nomvia, nomvtotal, tipo_dir=tipo_dir, pais=pais)
    if not valido:
        errores.append(msg)

    if valor is None or str(valor).strip() == "":
        return errores

    valido, msg = sin_espacios_extremos(valor, nombre)
    if not valido:
        errores.append(msg)

    valido, msg = en_mayusculas(valor, nombre)
    if not valido:
        errores.append(msg)

    valido, msg = validar_abreviatura(valor, abreviaturas or set())
    if not valido:
        errores.append(msg)

    return errores
