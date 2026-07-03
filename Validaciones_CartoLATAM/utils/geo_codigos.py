"""
geo_codigos.py
--------------
Reglas de validación de códigos geográficos por país.

Cada país define su jerarquía de campos cod_*/nom_* con:
- digitos: cantidad exacta de dígitos requeridos (None = longitud variable, solo numérico)
- prefijo_de: campo padre cuyo valor debe ser prefijo de este código (None = sin validación)
- obligatorio: si el campo no puede estar vacío

Estructura:
REGLAS_PAIS = {
    "NombrePais": {
        "cod_campo": {"digitos": N, "prefijo_de": "cod_padre", "obligatorio": True},
        "nom_campo": {"texto": True, "obligatorio": True},
        ...
    }
}
"""
from ._generales import (
    solo_numeros,
    cantidad_digitos,
    validar_texto_estandar,
    validar_texto_estandar_con_numeros,
    en_mayusculas,
    sin_espacios_extremos,
)


REGLAS_PAIS = {
    "Brasil": {
        "cod_estado": {"digitos": 2,  "prefijo_de": None,        "obligatorio": True},
        "nom_estado": {"sigla": True, "obligatorio": True},
        "cod_mun":    {"digitos": 7,  "prefijo_de": "cod_estado", "obligatorio": True},
        "nom_mun":    {"texto": True, "obligatorio": True},
        "cod_distri": {"digitos": 9,  "prefijo_de": "cod_mun",    "obligatorio": True},
        "nom_distri": {"texto": True, "obligatorio": True},
        "cod_bar":    {"digitos": None, "prefijo_de": None,       "obligatorio": False},
        "nom_bar":    {"alfanumerico_texto": True, "obligatorio": False},
        # Brasil usa cep (8 dígitos), no cod_postal — se valida en cep.py
    },
    "Chile": {
        "cod_reg":    {"digitos": 2,  "prefijo_de": None,        "obligatorio": True},
        "nom_reg":    {"texto": True, "obligatorio": True},
        "cod_prov":   {"digitos": 3,  "prefijo_de": "cod_reg",   "obligatorio": True},
        "nom_prov":   {"texto": True, "obligatorio": True},
        "cod_com":    {"digitos": 5,  "prefijo_de": "cod_prov",  "obligatorio": True},
        "nom_com":    {"texto": True, "obligatorio": True},
        "cod_postal": {"digitos": 7,  "prefijo_de": None,        "obligatorio": False},
    },
    "Perú": {
        "cod_dep":    {"digitos": 2,    "prefijo_de": None,       "obligatorio": True},
        "nom_dep":    {"texto": True,   "obligatorio": True},
        "cod_prov":   {"digitos": 4,    "prefijo_de": "cod_dep",  "obligatorio": True},
        "nom_prov":   {"texto": True,   "obligatorio": True},
        "cod_distri": {"digitos": 6,    "prefijo_de": "cod_prov", "obligatorio": True},
        "nom_distri": {"texto": True,   "obligatorio": True},
        "cod_postal": {"digitos": None, "prefijo_de": None,       "obligatorio": False},
    },
    "Argentina": {
        "cod_prov":   {"digitos": 2,  "prefijo_de": None,        "obligatorio": True},
        "nom_prov":   {"texto": True, "obligatorio": True},
        "cod_dep":    {"digitos": 5,  "prefijo_de": "cod_prov",  "obligatorio": True},
        "nom_dep":    {"texto": True, "obligatorio": True},
        "cod_mun":    {"digitos": 6,  "prefijo_de": "cod_dep",   "obligatorio": True},
        "nom_mun":    {"texto": True, "obligatorio": True},
        # CPA argentino es alfanumérico (ej: B1900, C1002AAA) — solo validamos no vacío
        "cod_postal": {"alfanumerico": True, "prefijo_de": None, "obligatorio": False},
    },
    "Guatemala": {
        "cod_dep":    {"digitos": 2,    "prefijo_de": None,       "obligatorio": True},
        "nom_dep":    {"texto": True,   "obligatorio": True},
        "cod_mun":    {"digitos": 4,    "prefijo_de": "cod_dep",  "obligatorio": True},
        "nom_mun":    {"texto": True,   "obligatorio": True},
        "cod_zona":   {"digitos": None, "prefijo_de": None,       "obligatorio": False},
        "nom_zona":   {"texto": True,   "obligatorio": False},
        "cod_postal": {"digitos": 5,    "prefijo_de": None,       "obligatorio": False},
    },
    "Mexico": {
        "cod_estado": {"digitos": 2,    "prefijo_de": None,       "obligatorio": True},
        "nom_estado": {"texto": True,   "obligatorio": True},
        "cod_mun":    {"digitos": 3,    "prefijo_de": None,       "obligatorio": True},
        "nom_mun":    {"texto": True,   "obligatorio": True},
        "cod_alc":    {"digitos": 3,    "prefijo_de": None,       "obligatorio": False},
        "nom_alc":    {"texto": True,   "obligatorio": False},
        "cod_loc":    {"digitos": None, "prefijo_de": None,       "obligatorio": False},
        "nom_loc":    {"texto": True,   "obligatorio": False},
        "cod_col":    {"digitos": None, "prefijo_de": None,       "obligatorio": False},
        "nom_col":    {"texto": True,   "obligatorio": False},
        "cod_postal": {"digitos": 5,    "prefijo_de": None,       "obligatorio": False},
    },
    "El Salvador": {
        "cod_dep":    {"digitos": 2,    "prefijo_de": None,       "obligatorio": True},
        "nom_dep":    {"texto": True,   "obligatorio": True},
        "cod_mun":    {"digitos": 4,    "prefijo_de": "cod_dep",  "obligatorio": True},
        "nom_mun":    {"texto": True,   "obligatorio": True},
        "cod_distri": {"digitos": 6,    "prefijo_de": "cod_mun",  "obligatorio": True},
        "nom_distri": {"texto": True,   "obligatorio": True},
        "cod_canton": {"digitos": None, "prefijo_de": None,       "obligatorio": False},
        "nom_canton": {"texto": True,   "obligatorio": False},
        "cod_col":    {"digitos": 8,    "prefijo_de": None,       "obligatorio": False},
        "nom_col":    {"texto": True,   "obligatorio": False},
        "cod_postal": {"digitos": 4,    "prefijo_de": None,       "obligatorio": False},
    },
    "Ecuador": {
        "cod_prov":   {"digitos": 2,  "prefijo_de": None,         "obligatorio": True},
        "nom_prov":   {"texto": True, "obligatorio": True},
        "cod_can":    {"digitos": 4,  "prefijo_de": "cod_prov",   "obligatorio": True},
        "nom_can":    {"texto": True, "obligatorio": True},
        "cod_parroq": {"digitos": 6,  "prefijo_de": "cod_can",    "obligatorio": True},
        "nom_parroq": {"texto": True, "obligatorio": True},
        # Ecuador usa cod_post (no cod_postal), 6 dígitos
        "cod_post":   {"digitos": 6,  "prefijo_de": None,         "obligatorio": False},
    },
    "Panamá": {
        "cod_prov":   {"digitos": 2,  "prefijo_de": None,         "obligatorio": True},
        "nom_prov":   {"texto": True, "obligatorio": True},
        "cod_distri": {"digitos": 2,  "prefijo_de": None,         "obligatorio": True},
        "nom_distri": {"texto": True, "obligatorio": True},
        "cod_correg": {"digitos": 2,  "prefijo_de": None,         "obligatorio": True},
        "nom_correg": {"texto": True, "obligatorio": True},
        "cod_postal": {"digitos": 4,  "prefijo_de": None,         "obligatorio": False},
    },
    "Honduras": {
        "cod_dep":    {"digitos": 2,  "prefijo_de": None,         "obligatorio": True},
        "nom_dep":    {"texto": True, "obligatorio": True},
        "cod_mun":    {"digitos": 4,  "prefijo_de": "cod_dep",    "obligatorio": True},
        "nom_mun":    {"texto": True, "obligatorio": True},
        "cod_col":    {"digitos": 6,  "prefijo_de": None,         "obligatorio": False},
        "nom_col":    {"texto": True, "obligatorio": False},
        "cod_postal": {"digitos": 5,  "prefijo_de": None,         "obligatorio": False},
    },
    "Republica Dominicana": {
        "cod_reg":    {"digitos": 2,  "prefijo_de": None,         "obligatorio": True},
        "nom_reg":    {"texto": True, "obligatorio": True},
        "cod_prov":   {"digitos": 2,  "prefijo_de": None,         "obligatorio": True},
        "nom_prov":   {"texto": True, "obligatorio": True},
        "cod_mun":    {"digitos": 4,  "prefijo_de": None,         "obligatorio": True},
        "nom_mun":    {"texto": True, "obligatorio": True},
        "cod_postal": {"digitos": 5,  "prefijo_de": None,         "obligatorio": False},
    },
    "Puerto Rico": {
        "cod_mun":    {"digitos": 4,  "prefijo_de": None,         "obligatorio": True},
        "nom_mun":    {"texto": True, "obligatorio": True},
        "cod_postal": {"digitos": 5,  "prefijo_de": None,         "obligatorio": False},
    },
    "Costa Rica": {
        "cod_prov":   {"digitos": 1,  "prefijo_de": None,          "obligatorio": True},
        "nom_prov":   {"texto": True, "obligatorio": True},
        "cod_canton": {"digitos": 3,  "prefijo_de": "cod_prov",    "obligatorio": True},
        "nom_canton": {"texto": True, "obligatorio": True},
        "cod_distri": {"digitos": 5,  "prefijo_de": "cod_canton",  "obligatorio": True},
        "nom_distri": {"texto": True, "obligatorio": True},
        "cod_postal": {"digitos": 5,  "prefijo_de": None,          "obligatorio": False},
    },
    "Venezuela": {
        "cod_estado": {"digitos": 2,  "prefijo_de": None,          "obligatorio": True},
        "nom_estado": {"texto": True, "obligatorio": True},
        "cod_mun":    {"digitos": 4,  "prefijo_de": "cod_estado",  "obligatorio": True},
        "nom_mun":    {"texto": True, "obligatorio": True},
        "cod_parr":   {"digitos": 6,  "prefijo_de": "cod_mun",     "obligatorio": True},
        "nom_parr":   {"texto": True, "obligatorio": True},
        "cod_postal": {"digitos": 4,  "prefijo_de": None,          "obligatorio": True},
    },
}


def obtener_reglas(pais):
    """Retorna las reglas del país o dict vacío si no está definido."""
    return REGLAS_PAIS.get(pais, {})


def validar_geo_codigos(fila_dict, campos_capa, pais, reglas=None):
    """
    Valida todos los campos cod_*/nom_* presentes en la capa según las reglas del país.

    pais   : nombre del país — ignorado si reglas ya se pasa pre-computado.
    reglas : dict de reglas pre-computado (para evitar el lookup por feature).
             Si None, se obtiene de obtener_reglas(pais).
    """
    if reglas is None:
        reglas = obtener_reglas(pais)
    errores = {}

    def reg(campo, lista):
        if lista:
            if campo in errores:
                errores[campo].extend(lista)
            else:
                errores[campo] = list(lista)

    for campo, regla in reglas.items():
        if campo not in campos_capa:
            continue

        valor = fila_dict.get(campo)

        # Comprobación de vacío consciente del tipo: int/float nunca son vacíos
        if valor is None:
            es_vacio = True
        elif isinstance(valor, str):
            es_vacio = not valor.strip()
        else:
            es_vacio = False  # int, float → nunca vacío

        # Campo obligatorio vacío
        if regla.get("obligatorio") and es_vacio:
            reg(campo, [f"El {campo} no puede estar vacío"])
            continue

        # Si es opcional y está vacío, saltar
        if es_vacio:
            continue

        # Pre-computar str_valor una vez para todas las ramas
        str_valor = valor.strip() if isinstance(valor, str) else str(valor).strip()

        if regla.get("sigla"):
            errs = []
            valido, msg = sin_espacios_extremos(str_valor, campo)
            if not valido:
                errs.append(msg)
            valido, msg = en_mayusculas(str_valor, campo)
            if not valido:
                errs.append(msg)
            if not str_valor.isalpha():
                errs.append(f"El {campo} debe ser una sigla (solo letras, sin espacios ni números), recibido '{str_valor}'")
            reg(campo, errs)

        elif regla.get("alfanumerico_texto"):
            from .nom_bar import validar as _validar_nom_bar  # lazy: no todos los países lo usan
            reg(campo, _validar_nom_bar(str_valor, pais=pais))

        elif regla.get("texto"):
            # Los nom_* pueden contener números (ej: "SECTOR 12", "ZONA 3")
            errs = validar_texto_estandar_con_numeros(str_valor, campo, pais=pais)
            reg(campo, errs)

        elif regla.get("alfanumerico"):
            pass  # solo validamos que no esté vacío (ya verificado arriba)

        else:
            # Validación numérica
            valido, msg = solo_numeros(valor, campo)
            if not valido:
                reg(campo, [msg])
                continue

            digitos = regla.get("digitos")
            if digitos is not None:
                valido, msg = cantidad_digitos(valor, digitos, campo)
                if not valido:
                    reg(campo, [msg])
                    continue

            # Validar prefijo jerárquico
            padre = regla.get("prefijo_de")
            if padre and padre in campos_capa:
                valor_padre = fila_dict.get(padre)
                if valor_padre is not None:
                    padre_str = valor_padre.strip() if isinstance(valor_padre, str) else str(valor_padre).strip()
                    if padre_str:
                        n_padre = len(padre_str)
                        if not str_valor.startswith(padre_str):
                            reg(campo, [
                                f"Los primeros {n_padre} dígitos de {campo} ('{str_valor[:n_padre]}') "
                                f"deben coincidir con {padre} ('{padre_str}')"
                            ])

    return errores
