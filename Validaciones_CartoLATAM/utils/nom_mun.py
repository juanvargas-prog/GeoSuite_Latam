"""
Validaciones para el campo nom_mun.
Reglas:
- Debe ser en mayúscula
- Letras, números, espacios y comilla simple (según país)
- El nombre debe corresponder al mismo código del cod_mun
"""
from ._generales import en_mayusculas, sin_espacios_extremos, sin_caracteres_especiales_con_numeros


def validar_corresponde_codigo(nom_mun, cod_mun, mapa_municipios):
    """
    Valida que el nombre del municipio corresponda al cod_mun.

    :param mapa_municipios: dict {cod_mun: nom_mun} con la correspondencia oficial
    """
    if mapa_municipios is None:
        return True, ""  # sin mapa de referencia no se puede validar
    if cod_mun is None or str(cod_mun).strip() == "":
        return True, ""

    cod_mun_str = str(cod_mun).strip()
    nombre_esperado = mapa_municipios.get(cod_mun_str)

    if nombre_esperado is None:
        return False, f"El cod_mun '{cod_mun_str}' no se encuentra en el catálogo de municipios"

    if str(nom_mun).strip().upper() != nombre_esperado.upper():
        return (
            False,
            f"El nom_mun '{nom_mun}' no corresponde al cod_mun '{cod_mun_str}' "
            f"(esperado: '{nombre_esperado}')",
        )
    return True, ""


def validar(valor, cod_mun=None, mapa_municipios=None):
    """
    Ejecuta todas las validaciones del campo nom_mun.

    :param valor: valor del campo nom_mun
    :param cod_mun: valor del campo cod_mun
    :param mapa_municipios: dict {cod_mun: nom_mun} con la correspondencia oficial
    """
    errores = []
    nombre = "nom_mun"

    if valor is None or str(valor).strip() == "":
        errores.append(f"El {nombre} no puede estar vacío")
        return errores

    valido, msg = sin_espacios_extremos(valor, nombre)
    if not valido:
        errores.append(msg)

    valido, msg = sin_caracteres_especiales_con_numeros(valor, nombre)
    if not valido:
        errores.append(msg)

    valido, msg = en_mayusculas(valor, nombre)
    if not valido:
        errores.append(msg)

    if cod_mun is not None and mapa_municipios is not None:
        valido, msg = validar_corresponde_codigo(valor, cod_mun, mapa_municipios)
        if not valido:
            errores.append(msg)

    return errores
