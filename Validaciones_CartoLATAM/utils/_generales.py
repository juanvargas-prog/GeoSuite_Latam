"""
Validaciones generales reutilizables.
Aplican a múltiples campos: mayúsculas, espacios, caracteres especiales, etc.
Cada función retorna (valido: bool, mensaje: str)
"""
import re

# ── Conjuntos de caracteres por país ──────────────────────────────────────────

# Portugués base: vocales acentuadas + Ç
_CHARS_PORTUGUES = "ÁÀÂÃÉÊÍÓÔÕÚáàâãéêíóôõúÇçÑñ"

# Brasil: portugués + caracteres de lenguas de inmigración (alemán, italiano, polaco)
_CHARS_BRASIL = _CHARS_PORTUGUES + "ÜÄÖËÏÝüäöëïý"

# Default (resto de LATAM): solo portugués base
_CHARS_DEFAULT = _CHARS_PORTUGUES

def _patron_texto(chars):
    return re.compile(rf"^[A-Za-z{chars}' ]+$")

def _patron_texto_numeros(chars):
    return re.compile(rf"^[A-Za-z0-9{chars}' ]+$")

# Patrones para Brasil
PATRON_TEXTO_BRASIL          = _patron_texto(_CHARS_BRASIL)
PATRON_TEXTO_NUMEROS_BRASIL  = _patron_texto_numeros(_CHARS_BRASIL)

# Patrones default (resto de países)
PATRON_TEXTO_VALIDO          = _patron_texto(_CHARS_DEFAULT)
PATRON_TEXTO_CON_NUMEROS     = _patron_texto_numeros(_CHARS_DEFAULT)

# ── Numerales alfabéticos por idioma ──────────────────────────────────────────

# Solo portugués — para Brasil
_NUMERALES_PORTUGUES = {
    "ZERO": "0", "UM": "1", "DOIS": "2", "TRES": "3", "QUATRO": "4",
    "CINCO": "5", "SEIS": "6", "SETE": "7", "OITO": "8", "NOVE": "9",
    "DEZ": "10", "ONZE": "11", "DOZE": "12", "TREZE": "13",
    "QUATORZE": "14", "QUINZE": "15",
}

# Solo español — para el resto de LATAM
_NUMERALES_ESPANOL = {
    "CERO": "0", "UNO": "1", "DOS": "2", "TRES": "3", "CUATRO": "4",
    "CINCO": "5", "SEIS": "6", "SIETE": "7", "OCHO": "8", "NUEVE": "9",
    "DIEZ": "10", "ONCE": "11", "DOCE": "12", "TRECE": "13",
    "CATORCE": "14", "QUINCE": "15",
}

_SET_NUMERALES_PORTUGUES = set(_NUMERALES_PORTUGUES.keys())
_SET_NUMERALES_ESPANOL   = set(_NUMERALES_ESPANOL.keys())

# ── Ordinales ─────────────────────────────────────────────────────────────────

_ORDINALES_ESPANOL = {
    "PRIMERA": "1", "PRIMERO": "1", "PRIMER": "1",
    "SEGUNDA": "2", "SEGUNDO": "2",
    "TERCERA": "3", "TERCERO": "3",
    "CUARTA": "4",  "CUARTO": "4",
    "QUINTA": "5",  "QUINTO": "5",
    "SEXTA": "6",   "SEXTO": "6",
    "SEPTIMA": "7", "SEPTIMO": "7",
    "OCTAVA": "8",  "OCTAVO": "8",
    "NOVENA": "9",  "NOVENO": "9",
    "DECIMA": "10", "DECIMO": "10",
}

_ORDINALES_PORTUGUES = {
    "PRIMEIRA": "1", "PRIMEIRO": "1",
    "SEGUNDA": "2",  "SEGUNDO": "2",
    "TERCEIRA": "3", "TERCEIRO": "3",
    "QUARTA": "4",   "QUARTO": "4",
    "QUINTA": "5",   "QUINTO": "5",
}

_SET_ORDINALES_ESPANOL   = set(_ORDINALES_ESPANOL.keys())
_SET_ORDINALES_PORTUGUES = set(_ORDINALES_PORTUGUES.keys())

# ── Títulos profesionales ─────────────────────────────────────────────────────

_TITULOS = {
    "DR":    "DOCTOR",      "DRA":   "DOCTORA",
    "DOC":   "DOCTOR",      "DOCA":  "DOCTORA",
    "ING":   "INGENIERO",   "INGA":  "INGENIERA",
    "LIC":   "LICENCIADO",  "LICA":  "LICENCIADA",
    "PROF":  "PROFESOR",    "PROFA": "PROFESORA",
    "GEN":   "GENERAL",     "COR":   "CORONEL",
    "PRES":  "PRESIDENTE",  "GRAL":  "GENERAL",
}
_SET_TITULOS = set(_TITULOS.keys())

# Regex: número pegado a letra(s)  ej: 2B  →  2 B
_RE_NUM_LETRA = re.compile(r"(\d)([A-Za-z])")
# Regex: letra(s) pegada a número  ej: A3  →  A 3
_RE_LETRA_NUM = re.compile(r"([A-Za-z])(\d)")


def no_vacio(valor, nombre_campo="campo"):
    """Valida que el valor no esté vacío ni sea None."""
    if valor is None:
        return False, f"El {nombre_campo} no puede ser nulo"
    if isinstance(valor, str) and valor.strip() == "":
        return False, f"El {nombre_campo} no puede estar vacío"
    return True, ""


def sin_espacios_extremos(valor, nombre_campo="campo"):
    """Valida que no tenga espacios al inicio ni al final."""
    if not isinstance(valor, str):
        return True, ""
    if valor != valor.strip():
        return False, f"El {nombre_campo} no debe tener espacios al inicio ni al final"
    return True, ""


def sin_doble_espacio(valor, nombre_campo="campo"):
    """Valida que no haya dobles espacios (o más) entre palabras."""
    if not isinstance(valor, str) or valor == "":
        return True, ""
    if "  " in valor:
        return False, f"El {nombre_campo} no debe contener dobles espacios"
    return True, ""


def en_mayusculas(valor, nombre_campo="campo"):
    """Valida que el texto esté completamente en mayúsculas."""
    if not isinstance(valor, str) or valor == "":
        return True, ""
    if valor != valor.upper():
        return False, f"El {nombre_campo} debe estar en mayúsculas"
    return True, ""


def sin_caracteres_especiales(valor, nombre_campo="campo", pais="default"):
    """
    Valida que solo contenga letras, espacios y comilla simple (').
    Brasil admite además: Ü Ä Ö Ë Ï Ý (lenguas de inmigración).
    """
    if not isinstance(valor, str) or valor == "":
        return True, ""
    patron = PATRON_TEXTO_BRASIL if pais == "Brasil" else PATRON_TEXTO_VALIDO
    if not patron.match(valor):
        chars_extra = " (Ü, Ä, Ö, Ë, Ï, Ý)" if pais == "Brasil" else ""
        return (
            False,
            f"El {nombre_campo} contiene caracteres especiales no permitidos. "
            f"Solo se admiten letras (incluye Ñ), comilla simple (') y "
            f"caracteres acentuados (Á, À, Â, Ã, É, Ê, Í, Ó, Ô, Õ, Ú, Ç, Ñ){chars_extra}",
        )
    return True, ""


def sin_caracteres_especiales_con_numeros(valor, nombre_campo="campo", pais="default"):
    """
    Valida que solo contenga letras, números, espacios y comilla simple (').
    Brasil admite además: Ü Ä Ö Ë Ï Ý.
    """
    if not isinstance(valor, str) or valor == "":
        return True, ""
    patron = PATRON_TEXTO_NUMEROS_BRASIL if pais == "Brasil" else PATRON_TEXTO_CON_NUMEROS
    if not patron.match(valor):
        chars_extra = " (Ü, Ä, Ö, Ë, Ï, Ý)" if pais == "Brasil" else ""
        return (
            False,
            f"El {nombre_campo} contiene caracteres especiales no permitidos. "
            f"Solo se admiten letras (incluye Ñ), números, comilla simple (') y "
            f"caracteres acentuados (Á, À, Â, Ã, É, Ê, Í, Ó, Ô, Õ, Ú, Ç, Ñ){chars_extra}",
        )
    return True, ""


def solo_numeros(valor, nombre_campo="campo"):
    """Valida que el valor contenga únicamente dígitos numéricos."""
    if valor is None:
        return False, f"El {nombre_campo} no puede ser nulo"
    valor_str = str(valor).strip()
    if not valor_str.isdigit():
        return False, f"El {nombre_campo} debe contener solo números"
    return True, ""


def cantidad_digitos(valor, cantidad, nombre_campo="campo"):
    """Valida que el valor tenga exactamente N dígitos."""
    valor_str = str(valor).strip()
    if len(valor_str) != cantidad:
        return False, f"El {nombre_campo} debe tener exactamente {cantidad} dígitos"
    return True, ""


def validar_texto_estandar(valor, nombre_campo="campo", pais="default"):
    """
    Aplica las validaciones generales de texto (solo letras):
    - sin espacios al inicio/final
    - sin doble espacio
    - sin caracteres especiales (según país) — solo letras
    - en mayúsculas
    """
    errores = []
    valido, msg = sin_espacios_extremos(valor, nombre_campo)
    if not valido: errores.append(msg)
    valido, msg = sin_doble_espacio(valor, nombre_campo)
    if not valido: errores.append(msg)
    valido, msg = sin_caracteres_especiales(valor, nombre_campo, pais=pais)
    if not valido: errores.append(msg)
    valido, msg = en_mayusculas(valor, nombre_campo)
    if not valido: errores.append(msg)
    return errores


def validar_texto_estandar_con_numeros(valor, nombre_campo="campo", pais="default"):
    """
    Igual que validar_texto_estandar pero permitiendo dígitos numéricos.
    Se usa para campos nom_* que pueden contener números (ej: 'SECTOR 12', 'ZONA 3').
    - sin espacios al inicio/final
    - sin doble espacio
    - letras, números, espacios y comilla simple permitidos (según país)
    - en mayúsculas
    """
    errores = []
    valido, msg = sin_espacios_extremos(valor, nombre_campo)
    if not valido: errores.append(msg)
    valido, msg = sin_doble_espacio(valor, nombre_campo)
    if not valido: errores.append(msg)
    valido, msg = sin_caracteres_especiales_con_numeros(valor, nombre_campo, pais=pais)
    if not valido: errores.append(msg)
    valido, msg = en_mayusculas(valor, nombre_campo)
    if not valido: errores.append(msg)
    return errores


# ── Validaciones de formato de nombre de vía ──────────────────────────────────

def sin_numerales_alfabeticos(valor, nombre_campo="campo", pais="default"):
    """
    Detecta números escritos en letras según el idioma del país.
    Brasil: usa lista en portugués (DOIS, TRES, SETE...).
    Resto:  usa lista en español (DOS, TRES, SIETE...).
    """
    if not isinstance(valor, str) or valor == "":
        return True, ""
    set_numerales = _SET_NUMERALES_PORTUGUES if pais == "Brasil" else _SET_NUMERALES_ESPANOL
    palabras = valor.upper().split()
    encontrados = [p for p in palabras if p in set_numerales]
    if encontrados:
        return (
            False,
            f"El {nombre_campo} contiene números escritos en letras "
            f"({', '.join(encontrados)}). Deben usarse dígitos.",
        )
    return True, ""


def sin_ordinales_alfabeticos(valor, nombre_campo="campo", pais="default"):
    """
    Detecta ordinales escritos en letras según el idioma del país.
    Brasil: usa lista en portugués (PRIMEIRA, SEGUNDO...).
    Resto:  usa lista en español (PRIMERA, SEGUNDO...).
    """
    if not isinstance(valor, str) or valor == "":
        return True, ""
    set_ordinales = _SET_ORDINALES_PORTUGUES if pais == "Brasil" else _SET_ORDINALES_ESPANOL
    palabras = valor.upper().split()
    encontrados = [p for p in palabras if p in set_ordinales]
    if encontrados:
        return (
            False,
            f"El {nombre_campo} contiene ordinales en letras "
            f"({', '.join(encontrados)}). Deben usarse dígitos.",
        )
    return True, ""


def sin_numero_pegado_a_letra(valor, nombre_campo="campo"):
    """
    Detecta dígitos pegados a letras sin espacio (ej: 2B, 3A).
    Deben ir separados: 2 B, 3 A.
    """
    if not isinstance(valor, str) or valor == "":
        return True, ""
    if _RE_NUM_LETRA.search(valor):
        return (
            False,
            f"El {nombre_campo} tiene un número pegado a una letra (ej: '2B'). "
            "Deben ir separados por espacio (ej: '2 B').",
        )
    return True, ""


def sin_letra_pegada_a_numero(valor, nombre_campo="campo"):
    """
    Detecta letras pegadas a dígitos sin espacio (ej: A3, B12).
    Deben ir separados: A 3, B 12.
    """
    if not isinstance(valor, str) or valor == "":
        return True, ""
    if _RE_LETRA_NUM.search(valor):
        return (
            False,
            f"El {nombre_campo} tiene una letra pegada a un número (ej: 'A3'). "
            "Deben ir separados por espacio (ej: 'A 3').",
        )
    return True, ""


def sin_titulos_abreviados(valor, nombre_campo="campo"):
    """
    Detecta títulos profesionales abreviados (DR, ING, LIC, PROF...).
    Deben escribirse completos (DOCTOR, INGENIERO, LICENCIADO, PROFESOR...).
    """
    if not isinstance(valor, str) or valor == "":
        return True, ""
    palabras = valor.upper().split()
    encontrados = [p for p in palabras if p in _SET_TITULOS]
    if encontrados:
        sugerencias = ", ".join(f"{p} → {_TITULOS[p]}" for p in encontrados)
        return (
            False,
            f"El {nombre_campo} contiene títulos abreviados ({sugerencias}). "
            "Deben escribirse completos.",
        )
    return True, ""
