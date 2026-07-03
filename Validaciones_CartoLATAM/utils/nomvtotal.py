"""
Validaciones para el campo nomvtotal.
Reglas:
- Puede contener letras y números
- Sin caracteres especiales (comilla simple permitida)
- Siempre en mayúscula
- Si nomvtotal tiene info y nomvia == nomvtotal, tipovia puede estar vacío (vía sin tipo).
- Si nomvtotal tiene info y nomvtotal ≠ nomvia, tipovia y nomvia también deben tener info.
- No debe contener un prefijo de tipo de vía cuando tipovia está vacío.
- Es la unión de tipovia (estandarizado) + nomvia cuando tipovia está presente.
- Si tipovia está en nomvtotal, debe aparecer estandarizado según el diccionario.

El diccionario de estandarización (abreviatura → nombre completo) se carga
desde Google Sheets y se pasa como parámetro desde validar_capa.py.
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
)


def validar_tipovia_y_nomvtotal_con_info(nomvtotal, tipovia, nomvia,
                                          tipo_dir=None, pais="default"):
    """
    Si nomvtotal tiene información, valida la coherencia con tipovia y nomvia.

    - Si nomvia == nomvtotal → dirección sin tipo de vía; tipovia puede estar vacío.
    - En cualquier otro caso con nomvtotal ≠ nomvia: tipovia y nomvia deben tener info.
    - Guatemala MZCASA: sin restricciones.
    """
    if pais == "Guatemala" and tipo_dir and str(tipo_dir).strip().upper() == "MZCASA":
        return []

    if nomvtotal is None or str(nomvtotal).strip() == "":
        return []

    nomvtotal_u = str(nomvtotal).strip().upper()
    nomvia_u    = str(nomvia).strip().upper()  if nomvia   is not None else ""
    tipovia_str = str(tipovia).strip().upper() if tipovia  is not None else ""

    # Excepción: nomvia == nomvtotal → vía sin tipo, tipovia puede estar vacío
    if nomvia_u and nomvtotal_u == nomvia_u:
        return []

    errores = []
    if not tipovia_str:
        errores.append("Si nomvtotal tiene información, tipovia también debe tenerla")
    if not nomvia_u:
        errores.append("Si nomvtotal tiene información, nomvia también debe tenerla")
    return errores


def validar_tipo_via_en_nomvtotal(nomvtotal, nomvia, tipovia):
    """
    Cuando tipovia está vacío, detecta si nomvtotal contiene un prefijo de tipo de
    vía que debería figurar en tipovia.

    ERROR:  tipovia=NULL, nomvia=CARLOS,  nomvtotal=AVENIDA CARLOS
    OK:     tipovia=NULL, nomvia=CARLOS,  nomvtotal=CARLOS
    """
    tipovia_str   = str(tipovia).strip().upper()   if tipovia   is not None else ""
    nomvia_str    = str(nomvia).strip().upper()    if nomvia    is not None else ""
    nomvtotal_str = str(nomvtotal).strip().upper() if nomvtotal is not None else ""

    if tipovia_str:
        return True, ""  # tipovia tiene valor → no aplica esta regla

    if not nomvia_str or not nomvtotal_str:
        return True, ""  # otros validadores ya cubren los vacíos

    if nomvtotal_str == nomvia_str:
        return True, ""  # OK: sin tipo de vía

    # nomvtotal = "PREFIX nomvia" → PREFIX debería estar en tipovia
    if nomvtotal_str.endswith(" " + nomvia_str):
        prefijo = nomvtotal_str[:-(len(nomvia_str) + 1)].strip()
        if prefijo:
            return (
                False,
                f"nomvtotal contiene '{prefijo}' que debería figurar en tipovia; "
                f"tipovia está vacío",
            )

    return True, ""


def validar_estandarizacion(nomvtotal, tipovia, estandarizacion):
    """
    Si tipovia tiene información, debe aparecer estandarizado en nomvtotal.
    estandarizacion: dict {ABREVIATURA: NOMVTOTAL} cargado desde Sheets.
    """
    if not estandarizacion:
        return True, ""
    if tipovia is None or str(tipovia).strip() == "":
        return True, ""
    if nomvtotal is None or str(nomvtotal).strip() == "":
        return True, ""

    tipovia_str   = str(tipovia).strip().upper()
    nomvtotal_str = str(nomvtotal).strip().upper()

    forma_estandarizada = estandarizacion.get(tipovia_str)
    if forma_estandarizada is None:
        return True, ""  # tipovia no está en el dict, ya se valida en tipovia.py

    palabras = nomvtotal_str.split()

    if tipovia_str in palabras and forma_estandarizada not in nomvtotal_str:
        return (
            False,
            f"El nomvtotal debe contener '{forma_estandarizada}' "
            f"(forma estandarizada de '{tipovia_str}'), no la abreviatura",
        )

    if forma_estandarizada not in nomvtotal_str:
        return (
            False,
            f"El nomvtotal debe contener '{forma_estandarizada}' "
            f"(forma estandarizada del tipovia '{tipovia_str}')",
        )

    return True, ""


def validar_union_tipovia_nomvia(nomvtotal, tipovia, nomvia, estandarizacion, pais="default"):
    """
    nomvtotal debe ser la unión de tipovia (estandarizado) + nomvia.
    estandarizacion: dict {ABREVIATURA: NOMVTOTAL} cargado desde Sheets.
    Si el dict está vacío o no tiene la clave, no se valida la unión.

    Guatemala: si la abreviatura aparece dentro de nomvia (ej: "7 AV", "RU 5"),
    nomvtotal debe ser nomvia con la abreviatura reemplazada en su misma posición
    (ej: "7 AVENIDA", "RUTA 5"). Si nomvia no contiene la abreviatura, se aplica
    la regla general.
    """
    if nomvtotal is None or nomvia is None or tipovia is None:
        return True, ""

    nomvia_str    = str(nomvia).strip().upper()
    tipovia_str   = str(tipovia).strip().upper()
    nomvtotal_str = str(nomvtotal).strip().upper()

    if nomvia_str == "" or tipovia_str == "":
        return True, ""

    # Si no hay diccionario o la abreviatura no está, no podemos validar la unión
    if not estandarizacion or tipovia_str not in estandarizacion:
        return True, ""

    forma_estandarizada = estandarizacion[tipovia_str]

    # Guatemala: la abreviatura puede estar embebida en nomvia manteniendo el orden
    if pais == "Guatemala":
        palabras_nomvia = nomvia_str.split()
        if tipovia_str in palabras_nomvia:
            esperado = " ".join(
                forma_estandarizada if p == tipovia_str else p
                for p in palabras_nomvia
            )
            if nomvtotal_str != esperado:
                return (
                    False,
                    f"El nomvtotal debería ser '{esperado}' "
                    f"(tipovía estandarizada en la misma posición que en nomvia), "
                    f"pero es '{nomvtotal_str}'",
                )
            return True, ""
        # nomvia no contiene la abreviatura → regla general abajo

    esperado = f"{forma_estandarizada} {nomvia_str}"

    if nomvtotal_str != esperado:
        return (
            False,
            f"El nomvtotal debería ser '{esperado}' "
            f"(unión de tipovia estandarizado + nomvia), pero es '{nomvtotal_str}'",
        )
    return True, ""


def validar(valor, tipovia=None, nomvia=None, estandarizacion=None, pais="default",
            tipo_dir=None):
    """
    Ejecuta todas las validaciones del campo nomvtotal.

    :param valor:          valor del campo nomvtotal
    :param tipovia:        valor del campo tipovia
    :param nomvia:         valor del campo nomvia
    :param estandarizacion: dict {ABREVIATURA: NOMVTOTAL} cargado desde Sheets
    :param pais:           nombre del país para aplicar reglas de caracteres y numerales
    :param tipo_dir:       valor del campo tipo_dir (para excepción Guatemala MZCASA)
    """
    errores = []
    nombre  = "nomvtotal"

    _mzcasa = pais == "Guatemala" and tipo_dir and str(tipo_dir).strip().upper() == "MZCASA"

    errores.extend(
        validar_tipovia_y_nomvtotal_con_info(valor, tipovia, nomvia, tipo_dir=tipo_dir, pais=pais)
    )

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

    for fn in (sin_numero_pegado_a_letra, sin_letra_pegada_a_numero):
        valido, msg = fn(valor, nombre)
        if not valido:
            errores.append(msg)

    valido, msg = sin_numerales_alfabeticos(valor, nombre, pais=pais)
    if not valido:
        errores.append(msg)

    valido, msg = sin_ordinales_alfabeticos(valor, nombre, pais=pais)
    if not valido:
        errores.append(msg)

    if not _mzcasa:
        # Verificar prefijo de tipo de vía cuando tipovia está vacío
        valido, msg = validar_tipo_via_en_nomvtotal(valor, nomvia, tipovia)
        if not valido:
            errores.append(msg)

        if tipovia is not None:
            valido, msg = validar_estandarizacion(valor, tipovia, estandarizacion or {})
            if not valido:
                errores.append(msg)

        if tipovia is not None and nomvia is not None:
            valido, msg = validar_union_tipovia_nomvia(
                valor, tipovia, nomvia, estandarizacion or {}, pais=pais
            )
            if not valido:
                errores.append(msg)

    return errores
