"""
Validaciones para el campo nom_distri.
Reglas:
- El nombre debe corresponder al mismo código del cod_distri
- Letras, números, espacios y comilla simple (según país)
- Todo en mayúscula
"""
from ._generales import validar_texto_estandar_con_numeros


def validar_corresponde_codigo(nom_distri, cod_distri, mapa_distritos):
    """
    Valida que el nombre del distrito corresponda al cod_distri.

    :param mapa_distritos: dict {cod_distri: nom_distri} con la correspondencia oficial
    """
    if mapa_distritos is None:
        return True, ""
    if cod_distri is None or str(cod_distri).strip() == "":
        return True, ""

    cod_distri_str = str(cod_distri).strip()
    nombre_esperado = mapa_distritos.get(cod_distri_str)

    if nombre_esperado is None:
        return False, f"El cod_distri '{cod_distri_str}' no se encuentra en el catálogo de distritos"

    if str(nom_distri).strip().upper() != nombre_esperado.upper():
        return (
            False,
            f"El nom_distri '{nom_distri}' no corresponde al cod_distri '{cod_distri_str}' "
            f"(esperado: '{nombre_esperado}')",
        )
    return True, ""


def validar(valor, cod_distri=None, mapa_distritos=None):
    """
    Ejecuta todas las validaciones del campo nom_distri.

    :param valor: valor del campo nom_distri
    :param cod_distri: valor del campo cod_distri
    :param mapa_distritos: dict {cod_distri: nom_distri} con la correspondencia oficial
    """
    errores = []
    nombre = "nom_distri"

    if valor is None or str(valor).strip() == "":
        errores.append(f"El {nombre} no puede estar vacío")
        return errores

    errores.extend(validar_texto_estandar_con_numeros(valor, nombre))

    if cod_distri is not None and mapa_distritos is not None:
        valido, msg = validar_corresponde_codigo(valor, cod_distri, mapa_distritos)
        if not valido:
            errores.append(msg)

    return errores
