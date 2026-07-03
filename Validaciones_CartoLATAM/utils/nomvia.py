"""
Validaciones para el campo nomvia.
Reglas:
- Puede contener letras y números
- Sin caracteres especiales (comilla simple permitida)
- Siempre en mayúscula
- Sin espacios extremos ni dobles espacios
- Debe tener información si tipovia o nomvtotal tienen información
- Si tiene información, no debe contener el valor de tipovia como palabra
"""
from ._generales import (
    sin_espacios_extremos,
    sin_doble_espacio,
    sin_caracteres_especiales_con_numeros,
    en_mayusculas,
    sin_numerales_alfabeticos,
    sin_ordinales_alfabeticos,
    sin_numero_pegado_a_letra,
    sin_letra_pegada_a_numero,
    sin_titulos_abreviados,
)


def validar_coherencia(nomvia, tipovia, nomvtotal):
    """
    Si tipovia o nomvtotal tienen información, nomvia también debe tenerla.
    """
    tipovia_tiene_info   = tipovia   is not None and str(tipovia).strip()   != ""
    nomvtotal_tiene_info = nomvtotal is not None and str(nomvtotal).strip() != ""
    nomvia_tiene_info    = nomvia    is not None and str(nomvia).strip()    != ""

    if (tipovia_tiene_info or nomvtotal_tiene_info) and not nomvia_tiene_info:
        return False, "Si tipovia o nomvtotal tienen información, nomvia también debe tenerla"
    return True, ""


def validar_no_contiene_tipovia(nomvia, tipovia):
    """
    Si nomvia tiene información, no debe contener el valor de tipovia como palabra.
    """
    if nomvia is None or str(nomvia).strip() == "":
        return True, ""
    if tipovia is None or str(tipovia).strip() == "":
        return True, ""

    nomvia_str  = str(nomvia).strip().upper()
    tipovia_str = str(tipovia).strip().upper()

    palabras = nomvia_str.split()
    if tipovia_str in palabras:
        return (
            False,
            f"El nomvia '{nomvia}' no debe contener el valor del tipovia '{tipovia}'",
        )
    return True, ""


def validar(valor, tipovia=None, nomvtotal=None, pais="default", tipo_dir=None):
    """
    Ejecuta todas las validaciones del campo nomvia.

    :param valor:     valor del campo nomvia
    :param tipovia:   valor del campo tipovia (para coherencia y verificar que no se repita)
    :param nomvtotal: valor del campo nomvtotal (para coherencia)
    :param pais:      nombre del país para aplicar reglas de caracteres y numerales
    :param tipo_dir:  valor del campo tipo_dir (para excepción Guatemala MZCASA)
    """
    errores = []
    nombre = "nomvia"

    # Guatemala MZCASA: nomvia puede estar vacío
    _mzcasa = pais == "Guatemala" and tipo_dir and str(tipo_dir).strip().upper() == "MZCASA"

    if not _mzcasa:
        valido, msg = validar_coherencia(valor, tipovia, nomvtotal)
        if not valido:
            errores.append(msg)

    if valor is None or str(valor).strip() == "":
        return errores

    valido, msg = sin_espacios_extremos(valor, nombre)
    if not valido:
        errores.append(msg)

    valido, msg = sin_doble_espacio(valor, nombre)
    if not valido:
        errores.append(msg)

    valido, msg = sin_caracteres_especiales_con_numeros(valor, nombre, pais=pais)
    if not valido:
        errores.append(msg)

    valido, msg = en_mayusculas(valor, nombre)
    if not valido:
        errores.append(msg)

    # En Guatemala nomvia puede contener la abreviatura de tipovia (ej: "7 AV", "RU 5")
    if pais != "Guatemala":
        valido, msg = validar_no_contiene_tipovia(valor, tipovia)
        if not valido:
            errores.append(msg)

    # Formato de nombre de vía (numerales y ordinales según idioma del país)
    for fn in (sin_numero_pegado_a_letra, sin_letra_pegada_a_numero, sin_titulos_abreviados):
        valido, msg = fn(valor, nombre)
        if not valido:
            errores.append(msg)

    valido, msg = sin_numerales_alfabeticos(valor, nombre, pais=pais)
    if not valido:
        errores.append(msg)

    valido, msg = sin_ordinales_alfabeticos(valor, nombre, pais=pais)
    if not valido:
        errores.append(msg)

    return errores
