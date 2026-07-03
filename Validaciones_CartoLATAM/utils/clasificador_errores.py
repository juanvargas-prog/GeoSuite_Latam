"""
clasificador_errores.py
-----------------------
Clasifica mensajes de error de los validadores en tipos descriptivos y accionables.
Cada tipo le dice al profesional EXACTAMENTE qué debe corregir, sin mostrar el dato.
Usado por reporte_resumido.py para agrupar errores del informe interno.
"""

from collections import Counter

# ── Formato esperado de 'direccion' por país ──────────────────────────────────
# Se muestra cuando el error es "mal estructurado para <pais>".
# [CAMPO] indica que el campo es opcional en la concatenación.
_FORMATOS_DIRECCION: dict[str, str] = {
    "Brasil":               "NOMVTOTAL PLACA, NOM_BAR, NOM_DISTRI, NOM_MUN, CEP, NOM_ESTADO",
    "Chile":                "NOMVTOTAL PLACA, NOM_COM, NOM_REG  (ó con COD_POSTAL antes de NOM_REG en Santiago)",
    "Perú":                 "NOMVTOTAL PLACA, NOM_DISTRI  |  NOM_URB, MANZANA, CASA_LOTE, NOM_DISTRI",
    "Argentina":            "NOMVTOTAL PLACA, NOM_MUN, NOM_DEP, NOM_PROV",
    "Guatemala":            "NOMVTOTAL GENERADORA-PLACA, NOM_ZONA, NOM_MUN, NOM_DEP",
    "Mexico":               "NOMVTOTAL PLACA, NOM_COL, NOM_MUN, COD_POSTAL, NOM_ESTADO",
    "El Salvador":          "NOMVTOTAL PLACA, NOM_COL, NOM_DISTRI, NOM_MUN",
    "Ecuador":              "NOMVTOTAL PLACA",
    "Panamá":               "NOMVTOTAL PLACA",
    "Honduras":             "NOMVTOTAL PLACA",
    "Republica Dominicana": "NOMVTOTAL PLACA",
    "Puerto Rico":          "NOMVTOTAL PLACA",
    "Costa Rica":           "NOMVTOTAL PLACA",
    "Venezuela":            "NOMVTOTAL [PLACA], COD_POSTAL, NOM_PARR",
}

# ── Hints estáticos por campo ─────────────────────────────────────────────────
# Mostrados como fallback cuando el mensaje de error no contiene ejemplos
# ni formatos parseables. Dan orientación accionable al profesional.
_HINTS_POR_CAMPO: dict[str, str] = {
    # ── Vías ──────────────────────────────────────────────────────────────────
    "tipovia":    "Abreviatura de tipo de vía del catálogo. Ej: AV, CL, CR, TV, PSJ, AUTOP",
    "tipo_urb":   "Abreviatura urbana del catálogo. Ej: URB, RES, CONJ, SECT, VLL",
    "nomvtotal":  "Composición: TIPOVÍA_ESTÁNDAR + espacio + NOMVIA. Ej: AVENIDA BOLÍVAR, CALLE 5",
    "nomvia":     "Nombre de la vía sin abreviatura. Ej: BOLÍVAR, 5 DE JULIO, LIBERTADORES",
    "nomcomun":   "Nombre popular o alterno de la vía. Campo opcional",
    "placa":      "Número de puerta o dirección. Ej: 12, 45B, S/N",
    "costado":    "I (izquierdo), D (derecho), A (ambos), N (no aplica)",
    "generadora": "S (genera numeración de casas) o N (no genera)",
    "rango_par":  "Rango de numeración par separado por guión. Ej: 100-200, 0-98",
    "rango_imp":  "Rango de numeración impar separado por guión. Ej: 101-201, 1-99",
    "oneway":     "B (ambos sentidos), F (un sentido fwd), N (no aplica)",
    "velocidad":  "Velocidad en km/h, múltiplos de 10. Ej: 30, 50, 80, 120",
    "marca_vial": "Tipo de señalización. Ej: CONTINUA, DISCONTINUA, DOBLE",
    # ── Metadatos ─────────────────────────────────────────────────────────────
    "marca":      "Fuente del dato. Ej: GOOGLEMAPS, FIELDWORK, OFFICIAL",
    "fecha":      "Mes y año de la última modificación. Formato: MM-AAAA. Ej: 06-2025",
    "version":    "Versión del dato. Formato: V#-AA. Ej: V1-25, V2-26",
    "id_capa":    "Identificador único en la capa. No se permite repetir en ninguna feature",
    "id_mavvial": "ID de vía en la base MAVVIAL. Valor alfanumérico del proveedor",
    # ── Dirección / POI ───────────────────────────────────────────────────────
    "direccion":  "Verificar formato: campos separados por coma, nomvtotal+placa sin coma",
    "manzana":    "Identificador de manzana. Ej: MZ A, MZ 12, M-1",
    "casa_lote":  "Número de casa o lote. Ej: LT 5, CASA 3, L-7",
    "nom_urb":    "Nombre de urbanización en mayúsculas. Ej: LOS PINOS, LA CASTELLANA",
    "categoria":  "Categoría válida del catálogo del país (ver Sheets de categorías)",
    "nom_subcat": "Subcategoría válida para la categoría indicada (ver Sheets)",
    # ── Código postal ─────────────────────────────────────────────────────────
    "cep":        "CEP (código postal Brasil): 8 dígitos numéricos. Ej: 01310100",
    "cod_postal": "Código postal numérico. Ej: 1010 (VEN, 4 dig), 50000 (MEX/GTM, 5 dig), 7 dig (CHL)",
    "cod_post":   "Código postal de Ecuador: 6 dígitos. Ej: 170101",
    # ── Geocódigos — jerarquía estado/departamento ─────────────────────────────
    "cod_estado": "Exactamente 2 dígitos numéricos. Ej: 01, 11, 23",
    "nom_estado": "Nombre oficial del estado en mayúsculas. Ej: MIRANDA, CARABOBO",
    "cod_dep":    "Código numérico del departamento (revisar dígitos del país). Ej: 01, 07",
    "nom_dep":    "Nombre oficial del departamento en mayúsculas",
    "cod_prov":   "Código numérico de la provincia (revisar dígitos del país). Ej: 01, 13",
    "nom_prov":   "Nombre oficial de la provincia en mayúsculas",
    "cod_reg":    "Código numérico de la región (revisar dígitos del país). Ej: 01, 13",
    "nom_reg":    "Nombre oficial de la región en mayúsculas",
    # ── Geocódigos — municipio ────────────────────────────────────────────────
    "cod_mun":    "Código numérico que debe iniciar con el código del padre. Revisar jerarquía",
    "nom_mun":    "Nombre oficial del municipio en mayúsculas",
    "cod_alc":    "Código de la alcaldía (México): 3 dígitos. Ej: 001, 016",
    "nom_alc":    "Nombre de la alcaldía en mayúsculas",
    "cod_com":    "Código de la comuna (Chile): debe iniciar con cod_prov. Ej: 13101",
    "nom_com":    "Nombre oficial de la comuna en mayúsculas",
    "cod_can":    "Código del cantón (Ecuador): debe iniciar con cod_prov. Ej: 0101",
    "nom_can":    "Nombre oficial del cantón en mayúsculas",
    # ── Geocódigos — nivel inferior ──────────────────────────────────────────
    "cod_parr":   "Código de 6 dígitos que debe iniciar con cod_mun. Ej: 010101",
    "nom_parr":   "Nombre oficial de la parroquia en mayúsculas",
    "cod_parroq": "Código de 6 dígitos que debe iniciar con cod_can (Ecuador). Ej: 010150",
    "nom_parroq": "Nombre oficial de la parroquia ecuatoriana en mayúsculas",
    "cod_distri": "Código numérico que debe iniciar con el código padre. Revisar jerarquía",
    "nom_distri": "Nombre oficial del distrito en mayúsculas",
    "cod_correg": "Código del corregimiento (Panamá). Ej: 01, 02",
    "nom_correg": "Nombre oficial del corregimiento en mayúsculas",
    "cod_canton": "Código del cantón (Costa Rica): debe iniciar con cod_prov. Ej: 101",
    "nom_canton": "Nombre oficial del cantón en mayúsculas",
    "cod_zona":   "Código numérico de la zona. Ej: 01, 12 (Guatemala)",
    "nom_zona":   "Nombre oficial de la zona en mayúsculas. Ej: ZONA 1, ZONA 12",
    "cod_col":    "Código de la colonia o corregimiento (revisar país). Ej: 010101",
    "nom_col":    "Nombre oficial de la colonia en mayúsculas",
    "cod_loc":    "Código de la localidad (México). Ej: 001, 0001",
    "nom_loc":    "Nombre de la localidad en mayúsculas",
    "cod_bar":    "Código del barrio. Revisar si es numérico y cantidad de dígitos del país",
    "nom_bar":    "Nombre oficial del barrio en mayúsculas",
}

# ── Tipos específicos → patrones reales de los mensajes ──────────────────────
# Orden: más específico primero. Comparación case-insensitive.

_TIPOS: list[tuple[str, list[str]]] = [

    # ── VACÍOS ────────────────────────────────────────────────────────────────
    ("Campo vacío si otro campo tiene datos", [
        "también debe tenerla",
        "también debe tenerlo",
        "no debe estar vacía si",
        "no debe estar vacío si",
    ]),
    ("Campo vacío", [
        "no puede estar vacío",
        "no puede ser nulo",
        "no debe estar vacía",
        "no debe estar vacío",
    ]),

    # ── DUPLICADOS ────────────────────────────────────────────────────────────
    ("ID duplicado", [
        "duplicado",
        "debe ser único",
    ]),

    # ── CÓDIGO / CATÁLOGO ─────────────────────────────────────────────────────
    ("Abreviatura de vía no válida", [
        "no es una abreviatura válida",
    ]),
    ("Abreviatura urbana no válida", [
        "no es una abreviatura urbana válida",
    ]),
    ("Categoría no válida para el país", [
        "no es válida para",       # "La categoria 'X' no es válida para Colombia"
        "subcategoría",            # "La subcategoría 'X' no es válida para..."
    ]),
    ("Código no existe en catálogo", [
        "no se encuentra en el catálogo",
    ]),
    ("Nombre no corresponde al código", [
        "no corresponde al",
    ]),
    ("Valor no permitido", [
        "valores permitidos",      # oneway: "Valores permitidos: B (ambos), F, N"
        "no es válido",            # oneway, costado: "El X no es válido"
    ]),

    # ── SOLO NÚMEROS (va ANTES de cualquier patrón con "debe contener") ──────
    ("Solo se admiten números", [
        "debe contener solo números",
    ]),

    # ── INCONSISTENCIA ENTRE CAMPOS ───────────────────────────────────────────
    ("Prefijo jerárquico incorrecto", [
        "primeros",                # "Los primeros N dígitos de X deben coincidir"
    ]),
    ("Forma estandarizada incorrecta", [
        "forma estandarizada",     # "El nomvtotal debe contener la forma estandarizada"
        "tipovía estandarizado",
    ]),
    ("Valor no coincide con el formato esperado", [
        "debería ser",
    ]),
    ("Valor repetido entre campos", [
        "no debe contener el valor",
    ]),

    # ── MAYÚSCULAS ────────────────────────────────────────────────────────────
    ("Debe estar en mayúsculas", [
        "debe estar en mayúsculas",
        "completamente en mayúsculas",
        "en mayúsculas",
        "debe estar completamente",
    ]),

    # ── ESPACIOS ──────────────────────────────────────────────────────────────
    ("Espacio al inicio o al final", [
        "espacios al inicio",
        "no debe tener espacios al inicio",
    ]),
    ("Doble espacio", [
        "dobles espacios",
        "contener dobles espacios",
    ]),

    # ── CARACTERES ────────────────────────────────────────────────────────────
    ("Caracteres especiales no permitidos", [
        "caracteres especiales no permitidos",
        "caracteres no permitidos",
        "solo se admiten",
        "solo puede contener",
    ]),
    # ── SEPARACIÓN ────────────────────────────────────────────────────────────
    ("Número pegado a letra (falta espacio)", [
        "número pegado a una letra",
        "pegado a una letra",
    ]),
    ("Letra pegada a número (falta espacio)", [
        "letra pegada a un número",
        "pegada a un número",
        "deben ir separados",
    ]),

    # ── NUMERALES Y ORDINALES ─────────────────────────────────────────────────
    ("Número escrito en letras", [
        "números escritos en letras",
        "deben usarse dígitos",
    ]),
    ("Ordinal escrito en letras", [
        "ordinales en letras",
    ]),

    # ── TÍTULO ABREVIADO ──────────────────────────────────────────────────────
    ("Título debe escribirse completo", [
        "títulos abreviados",
        "deben escribirse completos",
    ]),

    # ── FORMATO / ESTRUCTURA ──────────────────────────────────────────────────
    ("Longitud incorrecta (dígitos)", [
        "debe tener exactamente",
        "dígitos",
    ]),
    ("Falta cero inicial", [
        "0 a la izquierda",
    ]),
    ("Debe ser una sigla", [
        "debe ser una sigla",
    ]),
    ("Formato de fecha incorrecto", [
        "debe estar en formato",   # "debe estar en formato mm-aaaa"
        "formato mm-aaaa",
    ]),
    ("Formato de versión incorrecto", [
        "formato v#-aa",
        "formato v",
    ]),
    ("Formato incorrecto", [
        "debe tener formato",
        "debe tener el formato",
        "no se pudo interpretar",
        "mal estructurado",
        "formato",
    ]),

    # ── RANGO NUMÉRICO ────────────────────────────────────────────────────────
    ("Valor no es múltiplo de 10", [
        "debe ir de",
    ]),
    ("Valor excede el máximo permitido", [
        "no puede superar",
    ]),
    ("Valor no puede ser negativo", [
        "no puede ser negativa",
    ]),
    ("Número debe ser par", [
        "deben ser pares",
        "valor impar",
    ]),
    ("Número debe ser impar", [
        "deben ser impares",
        "valor par",
    ]),
    ("Primer número mayor que segundo", [
        "debe ser ≤",
    ]),
]

# ── Severidad por tipo ────────────────────────────────────────────────────────
_SEVERIDAD: dict[str, str] = {
    # CRÍTICO — bloquean la entrega
    "Campo vacío":                                 "CRÍTICO",
    "Campo vacío si otro campo tiene datos":       "CRÍTICO",
    "ID duplicado":                                "CRÍTICO",

    # ALTO — errores de referencia y consistencia
    "Abreviatura de vía no válida":                "ALTO",
    "Abreviatura urbana no válida":                "ALTO",
    "Categoría no válida para el país":            "ALTO",
    "Subcategoría no válida":                      "ALTO",
    "Código no existe en catálogo":                "ALTO",
    "Nombre no corresponde al código":             "ALTO",
    "Valor no permitido":                          "ALTO",
    "Prefijo jerárquico incorrecto":               "ALTO",
    "Forma estandarizada incorrecta":              "ALTO",
    "Solo se admiten números":                     "MEDIO",
    "Valor no coincide con el formato esperado":   "ALTO",

    # MEDIO — errores de formato y estructura
    "Debe estar en mayúsculas":                    "MEDIO",
    "Formato incorrecto":                          "MEDIO",
    "Formato de fecha incorrecto":                 "MEDIO",
    "Formato de versión incorrecto":               "MEDIO",
    "Longitud incorrecta (dígitos)":               "MEDIO",
    "Falta cero inicial":                          "MEDIO",
    "Debe ser una sigla":                          "MEDIO",
    "Caracteres especiales no permitidos":         "MEDIO",
    "Solo se admiten números":                     "MEDIO",
    "Valor no es múltiplo de 10":                  "MEDIO",
    "Valor excede el máximo permitido":            "MEDIO",
    "Valor no puede ser negativo":                 "MEDIO",
    "Número debe ser par":                         "MEDIO",
    "Número debe ser impar":                       "MEDIO",
    "Primer número mayor que segundo":             "MEDIO",
    "Valor repetido entre campos":                 "MEDIO",

    # BAJO — errores de estilo / escritura
    "Espacio al inicio o al final":                "BAJO",
    "Doble espacio":                               "BAJO",
    "Número pegado a letra (falta espacio)":       "BAJO",
    "Letra pegada a número (falta espacio)":       "BAJO",
    "Número escrito en letras":                    "BAJO",
    "Ordinal escrito en letras":                   "BAJO",
    "Título debe escribirse completo":             "BAJO",
    "Otro error":                                  "BAJO",
}

# ── Colores para badges (fondo, texto) ───────────────────────────────────────
COLORES_SEVERIDAD: dict[str, tuple[str, str]] = {
    "CRÍTICO": ("#450A0A", "#FCA5A5"),
    "ALTO":    ("#451A03", "#FDE68A"),
    "MEDIO":   ("#1E3A5F", "#93C5FD"),
    "BAJO":    ("#1F2937", "#9CA3AF"),
}

ORDEN_SEVERIDAD: dict[str, int] = {
    "CRÍTICO": 0, "ALTO": 1, "MEDIO": 2, "BAJO": 3,
}


# ── API pública ───────────────────────────────────────────────────────────────

def clasificar(mensaje: str) -> str:
    """Clasifica un mensaje de error en un tipo descriptivo y accionable."""
    m = mensaje.lower()
    for tipo, patrones in _TIPOS:
        if any(p.lower() in m for p in patrones):
            return tipo
    return "Otro error"


def severidad(tipo_o_mensaje: str) -> str:
    """Retorna la severidad de un tipo de error o de un mensaje."""
    tipo = (tipo_o_mensaje
            if tipo_o_mensaje in _SEVERIDAD
            else clasificar(tipo_o_mensaje))
    return _SEVERIDAD.get(tipo, "BAJO")


def color_severidad(sev: str) -> tuple[str, str]:
    """Retorna (color_fondo, color_texto) para el badge de severidad."""
    return COLORES_SEVERIDAD.get(sev, COLORES_SEVERIDAD["BAJO"])


def extraer_hint(mensaje: str, campo: str = None) -> str:
    """
    Extrae del mensaje de error el ejemplo o formato esperado.
    Retorna un string corto tipo "Formato: mm-aaaa" o "Permitidos: B, F, N"
    que sirve de guía al profesional sin revelar el dato incorrecto.

    :param mensaje: mensaje de error del validador
    :param campo:   nombre del campo al que pertenece el error (mejora la especificidad)
    """
    import re
    m = mensaje

    # ── Caso especial: direccion → mostrar formato exacto del país ────────────
    if campo == "direccion":
        match = re.search(r"mal estructurado para (.+?)\.?\s*$", m, re.IGNORECASE)
        if match:
            pais = match.group(1).strip()
            fmt = _FORMATOS_DIRECCION.get(pais)
            if fmt:
                return f"Formato para {pais}: {fmt}"

    # ── Patrones extraídos del texto del mensaje ──────────────────────────────

    # "Valores permitidos: B (ambos sentidos), F (un sentido), N (no aplica)"
    match = re.search(r"[Vv]alores permitidos[:\s]+(.{5,80}?)(?:\.|$)", m)
    if match:
        return f"Permitidos: {match.group(1).strip()}"

    # "formato 'numero' o 'numero-numero'"  /  "formato mm-aaaa"  /  "formato V#-AA"
    match = re.search(r"[Ff]ormato ['\"]?([^,'\"\n]{3,50})", m)
    if match:
        return f"Formato: {match.group(1).strip().rstrip('.,)')}"

    # "(ej: V1-26, V2-25)"  /  "(ej: MZ A, MZ 12)"
    match = re.search(r"[Ee]j[.:]?\s*([^\)\.]{3,50})", m)
    if match:
        return f"Ej: {match.group(1).strip().rstrip(',.')}"

    # "debe ir de 10 en 10 (0, 10, 20, ...)"  → extrae la serie entre paréntesis
    match = re.search(r"\(([0-9,\s\.]+)\.\.\.\)", m)
    if match:
        return f"Ej: {match.group(1).strip()}..."

    # "debe ser 1 o 2"  /  "debe ser PAR o IMPAR"
    match = re.search(r"[Dd]ebe ser (.{3,40}?)(?:,|\.|$)", m)
    if match:
        return f"Debe ser: {match.group(1).strip()}"

    # "exactamente N dígitos"
    match = re.search(r"exactamente (\d+) dígitos", m, re.IGNORECASE)
    if match:
        return f"Debe tener exactamente {match.group(1)} dígitos"

    # "Los primeros N dígitos de campo ('XX') deben coincidir con padre ('YY')"
    match = re.search(r"coincidir con \w+ \('([^']+)'\)", m)
    if match:
        return f"Debe iniciar con: {match.group(1)}"

    # "esperado: 'VALOR'"  /  "esperado: VALOR"
    match = re.search(r"esperado[:\s]+['\"]?([^'\"]{2,30})['\"]?", m, re.IGNORECASE)
    if match:
        return f"Esperado: {match.group(1).strip()}"

    # ── Fallback: hint estático por campo ────────────────────────────────────
    if campo:
        return _HINTS_POR_CAMPO.get(campo, "")

    return ""


def extraer_hints_por_tipo(errores_por_campo: dict) -> dict:
    """
    Por cada campo y tipo de error, extrae el primer hint disponible.

    Input:  {campo: [{fid, valor, msg}, ...]}
    Output: {campo: {tipo_error: hint_string}}
    """
    resultado: dict[str, dict[str, str]] = {}
    for campo, items in errores_por_campo.items():
        hints: dict[str, str] = {}
        for item in items:
            tipo = clasificar(item["msg"])
            if tipo not in hints or not hints[tipo]:
                h = extraer_hint(item["msg"], campo=campo)
                if h:
                    hints[tipo] = h
        resultado[campo] = hints
    return resultado


def agrupar_por_tipo(errores_por_campo: dict) -> dict:
    """
    Agrupa errores por campo → tipo específico → cantidad.

    Input:  {campo: [{fid, valor, msg}, ...]}
    Output: {campo: {tipo_error: count}} ordenado por severidad desc, luego frecuencia desc
    """
    resultado = {}
    for campo, items in errores_por_campo.items():
        contador = Counter(clasificar(item["msg"]) for item in items)
        resultado[campo] = dict(
            sorted(
                contador.items(),
                key=lambda kv: (ORDEN_SEVERIDAD.get(severidad(kv[0]), 3), -kv[1])
            )
        )
    return resultado


def severidad_global(errores_por_campo: dict) -> str:
    """Retorna la severidad más alta encontrada en una capa."""
    for nivel in ("CRÍTICO", "ALTO", "MEDIO"):
        for campo, items in errores_por_campo.items():
            for item in items:
                if severidad(clasificar(item["msg"])) == nivel:
                    return nivel
    return "BAJO"

