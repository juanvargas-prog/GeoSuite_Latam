"""
sheets_loader.py
----------------
Acceso a todos los Google Sheets del plugin (autenticación con cuenta de servicio).

Datos que carga:
- Abreviaturas tipovía  (TIPOVIA_BRASIL / TIPOVIA_LATAM, columnas TIPO/ABREVIATURA/NOMVTOTAL)
- Abreviaturas tipo URB (mismo Sheet, filas con TIPO == "URB")
- Categorías/subcategorías por país (SHEET_ID_CAT)
- Esquema de estructura de capas por país (SHEET_ID_ESTRUCTURA)
  Columnas: NOMBRE CAPA, NOMBRE CAMPO, TIPO DE CAMPO, LONGITUD, PRODUCCION, ENTREGA, GEOMARKETING
- Tareas/órdenes internas (SHEET_ID_TAREAS)

Caché en disco (%TEMP%/cartolatam_cache/) con TTL de 24 h.
Las claves de caché de estructura usan prefijo "estructura_v2_" para forzar re-lectura
cuando cambia el esquema de claves del dict parseado.
"""

import json
import os
import re
import sys
import time

# ── Configuración ─────────────────────────────────────────────────────────────
SHEET_ID            = "1DwHXQtOtBsAGnrAnDeZRSfxpI7cdRUOR0Ay563X888E"  # Sheets de tipovia
SHEET_ID_CAT        = "1wrVpN02ZGQ35mknGsjBj-xkEeOWrJ7z-khIHKsPEUkA"  # Sheets de categorías y subcategorías
SHEET_ID_TAREAS     = "1iK1MT1tc9OMyAdysm7FIeR2GprKm5JU7ZFtmhRwBxeY"  # Sheets de tareas/órdenes internas
SHEET_ID_ESTRUCTURA = "1mExc_Gz1h3eWDya4kZgNRXiKDDwPq01b4VTeXDaK0wo"  # Sheets de esquema de estructura de capas
# Documentos de control para validación de documentación de entrega
SHEET_ID_CRONOGRAMA       = "1wQ2B9drXjqu_PZmsq_gRYXOfIGj5PiaLgbP6MlgstVM"
SHEET_ID_CONTROL_ORDENES  = "1iK1MT1tc9OMyAdysm7FIeR2GprKm5JU7ZFtmhRwBxeY"
SHEET_ID_CONTROL_ENTREGAS = "12IJRkkTVeVD2r92qRHDx-kiFZiyjZ6KIIdN-yJreC64"
SHEET_ID_ACTAS            = "1v8YbIl-Fav8OjqzAAIwcvKZ_eqlfBu7CDgbbgMtTmmI"

# Nombres de pestañas y fila de encabezado para cada sheet de control
TAB_CRONOGRAMA   = "LATAM Cronograma"
TAB_ACTAS        = "Actas de Entrega 2026"
TAB_ENTREGAS     = "Matriz de Entregas 2026"
TAB_CONTROL_OT   = "CONTROL DE ORDENES DE TRABAJO"
HEAD_CRONOGRAMA  = 7   # fila real del encabezado (1-based)
HEAD_ACTAS       = 6
HEAD_ENTREGAS    = 1
HEAD_CONTROL_OT  = 6

# Ruta al JSON de cuenta de servicio — viene del .env (RUTA_CREDENCIAL_SHEETS)
# Si no está configurada se usa cadena vacía; el sistema de credenciales cifradas
# (credentials.enc) tiene prioridad sobre este fallback.
try:
    _plugin_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if _plugin_dir not in sys.path:
        sys.path.insert(0, _plugin_dir)
    from utils.env_loader import get as _env_get
    RUTA_CREDENCIAL = _env_get("RUTA_CREDENCIAL_SHEETS", "")
except Exception:
    RUTA_CREDENCIAL = ""   # vacío — usar credentials.enc en su lugar
SCOPE           = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

# Mapeo: nombre del país (como aparecerá en el diálogo) → código de columna en LATAM
# Brasil usa su propia hoja, el resto usa TIPOVIA_LATAM
PAISES = {
    "Brasil":    "BRASIL",
    "Perú":      "PER",
    "Panamá":    "PAN",
    "Guatemala": "GTM",
    "Chile":     "CHI",
    "Argentina": "ARG",
    "Ecuador": "ECU",
    "Mexico": "MEX",
    "Honduras": "HND",
    "El Salvador": "SALV",
    "Republica Dominicana": "RD",
    "Puerto Rico": "PR",
    "Costa Rica": "CR",
    "Venezuela":  "VEN",

    # Agrega más países aquí cuando los tengas
}

# Mapeo: nombre del país → nombre de la hoja de categorías en Sheets
PAISES_HOJAS_CAT = {
    "Brasil":               "BRA",
    "Perú":                 "PER",
    "Panamá":               "PAN",
    "Guatemala":            "GTM",
    "Chile":                "CHI",
    "Argentina":            "ARG",
    "Ecuador":              "ECU",
    "Mexico":               "MEX",
    "Honduras":             "HND",
    "El Salvador":          "SALV",
    "Republica Dominicana": "RD",
    "Puerto Rico":          "PR",
    "Costa Rica":           "CR",
    "Colombia":             "COL",
    "Venezuela":            "VEN",
}

# Mapeo: nombre del país → nombre de la hoja de esquema de estructura en Sheets
PAISES_HOJAS_ESTRUCTURA = {
    "Brasil":               "BRA",
    "Perú":                 "PER",
    "Panamá":               "PAN",
    "Guatemala":            "GTM",
    "Chile":                "CHI",
    "Argentina":            "ARG",
    "Ecuador":              "ECU II",
    "Mexico":               "MEX",
    "Honduras":             "HOND",
    "El Salvador":          "SALV",
    "Republica Dominicana": "RD",
    "Puerto Rico":          "PR",
    "Costa Rica":           "CR",
    "Colombia":             "COL",
    "Venezuela":            "VEN",
    "Paraguay":             "PRY",
    "Uruguay":              "URY",
    "Jamaica":              "JM",
    "Trinidad y Tobago":    "TT",
}

# Cache en memoria para no reconectar en cada ejecución dentro de la misma sesión.
_cache           = {}
_cache_cat       = {}
_cache_estructura= {}
_client_cache = None   # cliente gspread autenticado — reutilizado entre llamadas
_CACHE_TTL_S  = 24 * 3600  # 24 horas — los datos de Sheets cambian raramente


def _ruta_cache_disco(clave):
    # Caché en %TEMP% del usuario — no en el directorio del plugin (que puede ser legible por otros)
    import tempfile, stat
    cache_dir = os.path.join(tempfile.gettempdir(), "cartolatam_cache")
    os.makedirs(cache_dir, exist_ok=True)
    try:
        os.chmod(cache_dir, stat.S_IRWXU)   # solo lectura/escritura del usuario actual
    except Exception:
        pass   # Windows puede no soportar chmod — no es bloqueante
    return os.path.join(cache_dir, f"cache_{clave.replace(' ', '_')}.json")


def _leer_cache_disco(clave, es_sets=False):
    """Lee caché de disco; retorna None si expirado, inexistente, corrupto o vacío."""
    try:
        with open(_ruta_cache_disco(clave), encoding="utf-8") as _f:
            _d = json.load(_f)
        if time.time() - _d.get("ts", 0) > _CACHE_TTL_S:
            return None
        _p = _d["payload"]
        # No servir resultados vacíos desde caché — obliga a recargar desde Sheets
        if not _p:
            return None
        return {k: set(v) for k, v in _p.items()} if es_sets else _p
    except Exception:
        return None


def _guardar_cache_disco(clave, payload, es_sets=False):
    """Guarda payload en disco; silencia errores (no es crítico)."""
    try:
        _serial = {k: list(v) for k, v in payload.items()} if es_sets else payload
        with open(_ruta_cache_disco(clave), "w", encoding="utf-8") as _f:
            json.dump({"ts": time.time(), "payload": _serial}, _f, ensure_ascii=False)
    except Exception:
        pass


def _obtener_credenciales():
    """Retorna el objeto Credentials de la cuenta de servicio (para Sheets y Drive)."""
    from google.oauth2.service_account import Credentials

    try:
        from .credenciales import obtener_credencial_sheets, credencial_disponible
        if credencial_disponible():
            info = obtener_credencial_sheets()
            return Credentials.from_service_account_info(info, scopes=SCOPE)
    except Exception:
        pass

    if not RUTA_CREDENCIAL or not os.path.exists(RUTA_CREDENCIAL):
        raise RuntimeError(
            "No se encontró credencial de Google. Configura CREDENTIALS_KEY o RUTA_CREDENCIAL_SHEETS."
        )
    return Credentials.from_service_account_file(RUTA_CREDENCIAL, scopes=SCOPE)


def _conectar():
    """Retorna el cliente autenticado de gspread, reutilizando la conexión si ya existe."""
    global _client_cache
    if _client_cache is not None:
        return _client_cache
    import gspread
    creds = _obtener_credenciales()
    _client_cache = gspread.authorize(creds)
    return _client_cache


def _filtrar_tipovia(sheet, pais_nombre, codigo, tipo):
    """Carga y filtra abreviaturas de la hoja TIPOVIA según país y tipo (VIA/URB)."""
    nombre_hoja = "TIPOVIA_BRASIL" if pais_nombre == "Brasil" else "TIPOVIA_LATAM"
    filas = [{k.strip(): v for k, v in f.items()}
             for f in sheet.worksheet(nombre_hoja).get_all_records()]
    return {
        str(f["ABREVIATURA"]).strip().upper(): str(f["NOMVTOTAL"]).strip().upper()
        for f in filas
        if str(f.get("TIPO", "")).strip().upper() == tipo
        and str(f.get("ABREVIATURA", "")).strip() != ""
        and (pais_nombre == "Brasil" or str(f.get(codigo, "")).strip().upper() == "TRUE")
    }


def cargar_abreviaturas(pais_nombre):
    """
    Carga y retorna las abreviaturas válidas para el país indicado.

    :param pais_nombre: nombre del país tal como aparece en PAISES (ej: "Brasil")
    :returns: dict {ABREVIATURA: NOMVTOTAL}  — solo filas con TIPO == "VIA"
    :raises ValueError: si el país no está en el mapeo
    :raises Exception: si falla la conexión o la hoja no existe
    """
    if pais_nombre in _cache:
        return _cache[pais_nombre]

    _disco = _leer_cache_disco(f"abrev_{pais_nombre}")
    if _disco is not None:
        _cache[pais_nombre] = _disco
        return _disco

    codigo = PAISES.get(pais_nombre)
    if codigo is None:
        raise ValueError(
            f"País '{pais_nombre}' no reconocido. "
            f"Disponibles: {', '.join(PAISES.keys())}"
        )

    client = _conectar()
    result = _filtrar_tipovia(client.open_by_key(SHEET_ID), pais_nombre, codigo, "VIA")
    _cache[pais_nombre] = result
    _guardar_cache_disco(f"abrev_{pais_nombre}", result)
    return result


def cargar_categorias(pais_nombre):
    """
    Carga las categorías y subcategorías válidas para el país indicado.

    Retorna:
        dict {CATEGORIA: set(SUBCATEGORIAS)}
        Ejemplo: {"COMERCIO": {"FARMACIAS", "TIENDAS", ...}, "SALUD": {...}}

    :raises ValueError: si el país no tiene hoja de categorías definida
    :raises Exception:  si falla la conexión o la hoja no existe
    """
    if pais_nombre in _cache_cat:
        return _cache_cat[pais_nombre]

    _disco_cat = _leer_cache_disco(f"cat_{pais_nombre}", es_sets=True)
    if _disco_cat is not None:
        _cache_cat[pais_nombre] = _disco_cat
        return _disco_cat

    nombre_hoja = PAISES_HOJAS_CAT.get(pais_nombre)
    if nombre_hoja is None:
        raise ValueError(
            f"País '{pais_nombre}' no tiene hoja de categorías definida. "
            f"Disponibles: {', '.join(PAISES_HOJAS_CAT.keys())}"
        )

    client = _conectar()
    sheet  = client.open_by_key(SHEET_ID_CAT)
    hoja   = sheet.worksheet(nombre_hoja)
    filas  = hoja.get_all_records()
    filas  = [{k.strip(): v for k, v in f.items()} for f in filas]

    resultado = {}
    for f in filas:
        cat    = str(f.get("CATEGORIA",    "")).strip().upper()
        subcat = str(f.get("SUBCATEGORIA", "")).strip().upper()
        if not cat:
            continue
        if cat not in resultado:
            resultado[cat] = set()
        if subcat:
            resultado[cat].add(subcat)

    _cache_cat[pais_nombre] = resultado
    _guardar_cache_disco(f"cat_{pais_nombre}", resultado, es_sets=True)
    return resultado


def cargar_abreviaturas_urb(pais_nombre):
    """
    Carga las abreviaturas de tipo urbano (TIPO == "URB") para el país indicado.
    Usa el mismo Sheet que tipovia pero filtra por TIPO == "URB".

    :param pais_nombre: nombre del país (igual que en PAISES)
    :returns: dict {ABREVIATURA: NOMVTOTAL} — puede ser vacío si el país no tiene URB definidos
    """
    _clave = f"urb_{pais_nombre}"

    if _clave in _cache:
        return _cache[_clave]

    _disco = _leer_cache_disco(_clave)
    if _disco is not None:
        _cache[_clave] = _disco
        return _disco

    codigo = PAISES.get(pais_nombre)
    if codigo is None:
        return {}   # país sin mapeo → no se valida tipo_urb

    client = _conectar()
    result = _filtrar_tipovia(client.open_by_key(SHEET_ID), pais_nombre, codigo, "URB")
    _cache[_clave] = result
    _guardar_cache_disco(_clave, result)
    return result


def cargar_esquema_estructura(pais_nombre):
    """
    Carga el esquema de estructura de capas para el país indicado.

    Columnas esperadas en la hoja del país:
      - NOMBRE CAPA   : nombre base del esquema (ej: "mavvial")  — puede quedar vacío
                        en filas que continúan la misma capa; se propaga hacia abajo
      - CAPA          : nombre del campo en la capa
      - TIPO          : tipo de dato esperado ("string" o "entero")
      - LONGITUD      : longitud máxima (solo strings)
      - PRODUCCION    : checkbox/TRUE si el campo aplica para Producción
      - ENTREGA        : checkbox/TRUE si el campo aplica para Entrega
      - GEOMARKETING  : checkbox/TRUE si el campo aplica para Geomarketing

    Retorna:
        dict {nombre_capa_lower: [{"campo": str, "tipo": str, "longitud": int|None,
                                    "produccion": bool, "entrega": bool,
                                    "geomarketing": bool}]}

    :raises ValueError: si el país no tiene hoja de estructura definida
    :raises Exception:  si falla la conexión o la hoja no existe
    """
    if pais_nombre in _cache_estructura:
        return _cache_estructura[pais_nombre]

    _disco = _leer_cache_disco(f"estructura_v2_{pais_nombre}")
    if _disco is not None:
        _cache_estructura[pais_nombre] = _disco
        return _disco

    nombre_hoja = PAISES_HOJAS_ESTRUCTURA.get(pais_nombre)
    if nombre_hoja is None:
        raise ValueError(
            f"País '{pais_nombre}' no tiene hoja de estructura definida. "
            f"Disponibles: {', '.join(PAISES_HOJAS_ESTRUCTURA.keys())}"
        )

    client = _conectar()
    sheet  = client.open_by_key(SHEET_ID_ESTRUCTURA)
    hoja   = sheet.worksheet(nombre_hoja)
    try:
        todos = hoja.get_all_values(value_render_option="UNFORMATTED_VALUE")
    except TypeError:
        todos = hoja.get_all_values()

    if not todos:
        raise ValueError("la hoja existe pero está completamente vacía")

    # Cabeceras posibles para cada columna (se acepta cualquier variante)
    # IMPORTANTE: "CAPA" va en _VAR_NOMBRE (col A = nombre de la capa),
    # NO en _VAR_CAMPO (col C = nombre del campo dentro de la capa).
    _VAR_NOMBRE = {"CAPA", "NOMBRE CAPA", "NOMBRE_CAPA", "NOMBRECAPA",
                   "LAYER", "LAYER NAME", "NOMBRE DE CAPA"}
    _VAR_CAMPO  = {"CAMPO", "FIELD", "NOMBRE CAMPO", "NOMBRE_CAMPO", "FIELD NAME"}
    _VAR_TIPO   = {"TIPO", "TIPO DATO", "TIPO_DATO", "TYPE",
                   "TIPO DE DATO", "TIPO DE CAMPO", "TIPO_CAMPO"}
    _VAR_LONG   = {"LONGITUD", "LENGTH", "LARGO"}
    _VAR_PROD   = {"PRODUCCION", "PRODUCCIÓN", "PRODUCTION", "PROD"}
    _VAR_GEO    = {"ENTREGA", "GEOLOCALIZACION", "GEOLOCALIZACIÓN", "GEOLOCALIZATION",
                   "GEO", "GEOLOC"}
    _VAR_GEOMKT = {"GEOMARKETING", "GEO MARKETING", "GEOMKT"}

    # Buscar fila de cabecera — la que contenga la columna de campo
    idx_cab = None
    for i, fila in enumerate(todos):
        celdas = [str(c).strip().upper() for c in fila]
        if any(c in _VAR_CAMPO for c in celdas):
            idx_cab = i
            break

    if idx_cab is None:
        _primera = [str(c).strip() for c in todos[0]][:12]
        raise ValueError(
            f"no se encontró columna de campo en ninguna fila. "
            f"Primera fila de la hoja: {_primera}"
        )

    cabeceras = [str(c).strip().upper() for c in todos[idx_cab]]

    def _col(variantes):
        return next((i for i, c in enumerate(cabeceras) if c in variantes), None)

    col_nombre = _col(_VAR_NOMBRE)
    col_campo  = _col(_VAR_CAMPO)
    col_tipo   = _col(_VAR_TIPO)
    col_long   = _col(_VAR_LONG)
    col_prod   = _col(_VAR_PROD)
    col_geo    = _col(_VAR_GEO)
    col_geomkt = _col(_VAR_GEOMKT)

    if col_campo is None:
        raise ValueError(
            f"cabecera encontrada en fila {idx_cab + 1} pero sin columna de campo. "
            f"Cabeceras detectadas: {cabeceras[:12]}"
        )

    def _get(fila, col):
        if col is None or col >= len(fila):
            return ""
        v = fila[col]
        if v is None:
            return ""
        return str(v).strip()

    def _bool_val(raw):
        s = raw.strip().upper()
        return s not in ("", "FALSE", "FALSO", "NO", "0", "N", "F")

    resultado     = {}
    nombre_actual = ""

    for fila in todos[idx_cab + 1:]:
        if not fila or not any(str(c).strip() for c in fila):
            continue

        # Nombre de capa: propagación hacia abajo si la celda está vacía
        nombre_nuevo = _get(fila, col_nombre).lower()
        if nombre_nuevo:
            nombre_actual = nombre_nuevo

        campo = _get(fila, col_campo).upper()
        if not campo or not nombre_actual:
            continue

        long_s = _get(fila, col_long)
        try:
            longitud = int(long_s) if long_s else None
        except (ValueError, TypeError):
            longitud = None

        entrada = {
            "campo":           campo,
            "tipo":            _get(fila, col_tipo).lower(),
            "longitud":        longitud,
            "produccion":      _bool_val(_get(fila, col_prod))    if col_prod   is not None else False,
            "entrega":         _bool_val(_get(fila, col_geo))     if col_geo    is not None else False,
            "geomarketing":    _bool_val(_get(fila, col_geomkt))  if col_geomkt is not None else False,
        }

        resultado.setdefault(nombre_actual, []).append(entrada)

    if not resultado:
        raise ValueError(
            f"cabeceras detectadas {cabeceras[:12]} pero ninguna fila produjo entradas válidas. "
            "Verifica que la columna A (nombre de capa) y la columna de campo tengan datos."
        )

    _cache_estructura[pais_nombre] = resultado
    _guardar_cache_disco(f"estructura_v2_{pais_nombre}", resultado)
    return resultado


def limpiar_cache():
    """Limpia memoria, conexión y archivos de caché en disco."""
    import tempfile
    global _client_cache
    _cache.clear()
    _cache_cat.clear()
    _cache_estructura.clear()
    _client_cache = None
    # Los archivos de caché se guardan en %TEMP%/cartolatam_cache/ con nombre cache_*.json
    _cache_dir = os.path.join(tempfile.gettempdir(), "cartolatam_cache")
    if os.path.isdir(_cache_dir):
        for _fn in os.listdir(_cache_dir):
            if _fn.startswith("cache_") and _fn.endswith(".json"):
                try:
                    os.remove(os.path.join(_cache_dir, _fn))
                except Exception:
                    pass


def paises_disponibles():
    """Retorna la lista de nombres de países disponibles."""
    return list(PAISES.keys())


# ── Tareas / órdenes internas ─────────────────────────────────────────────────

_cache_tareas = []   # caché en memoria de las tareas del Sheets

def cargar_tareas() -> list[dict]:
    """
    Carga las tareas/órdenes internas desde el Sheets de gestión.

    Columnas esperadas en el Sheets:
      - NOMBRE TAREA  : nombre/código de la orden interna (ej: "OT-2025-COL-001")
      - RESPONSABLES  : nombre del responsable asignado (ej: "Bryan Mora")

    Retorna lista de dicts:
      [{"orden": "...", "responsable": "..."}, ...]
    """
    global _cache_tareas

    if _cache_tareas:
        return _cache_tareas

    try:
        client = _conectar()
        sheet  = client.open_by_key(SHEET_ID_TAREAS)
        hoja   = sheet.get_worksheet(0)

        # Leer todos los valores en crudo para encontrar la fila de cabecera
        # independientemente de cuántas filas de título haya arriba
        todos = hoja.get_all_values()
        if not todos:
            raise ValueError("El Sheets de órdenes está vacío.")

        # Buscar la fila que contiene "NOMBRE TAREA"
        _VARIANTES_TAREA    = {"NOMBRE TAREA", "NOMBRETAREA", "NOMBRE_TAREA",
                               "TAREA", "NOMBRE DE TAREA"}
        _VARIANTES_NUM_TAREA = {"NUMERO TAREA", "NÚMERO TAREA", "NUM TAREA",
                                "NUMEROTAREA", "NUMERO_TAREA"}
        _VARIANTES_RESP     = {"RESPONSABLES", "RESPONSABLE", "ENCARGADO",
                               "PROFESIONAL", "ASIGNADO"}

        idx_cabecera = None
        for i, fila in enumerate(todos):
            celdas_upper = [str(c).strip().upper() for c in fila]
            if any(c in _VARIANTES_TAREA for c in celdas_upper):
                idx_cabecera = i
                break

        if idx_cabecera is None:
            cabs_encontradas = [str(c).strip() for c in todos[0]] if todos else []
            raise ValueError(
                f"No se encontró la columna 'NOMBRE TAREA' en ninguna fila del Sheets.\n"
                f"Primera fila encontrada: {', '.join(cabs_encontradas)}\n\n"
                f"Asegúrate de que exista una columna llamada exactamente: NOMBRE TAREA"
            )

        cabeceras = [str(c).strip().upper() for c in todos[idx_cabecera]]

        # Índices de las columnas que nos interesan
        col_tarea    = next((i for i, c in enumerate(cabeceras) if c in _VARIANTES_TAREA),     None)
        col_num_tarea= next((i for i, c in enumerate(cabeceras) if c in _VARIANTES_NUM_TAREA), None)
        col_resp     = next((i for i, c in enumerate(cabeceras) if c in _VARIANTES_RESP),      None)
        col_estado   = next((i for i, c in enumerate(cabeceras) if c in {"ESTADO", "STATUS", "ESTATUS"}), None)

        # Solo órdenes con estado ABIERTO
        _ESTADOS_ABIERTOS = {"ABIERTO", "ABIERTA", "OPEN", "ACTIVO", "ACTIVA", "A"}

        resultado = []
        for fila in todos[idx_cabecera + 1:]:
            if not fila or not any(fila):
                continue
            nombre    = str(fila[col_tarea]).strip()     if col_tarea     is not None and col_tarea     < len(fila) else ""
            num_tarea = str(fila[col_num_tarea]).strip() if col_num_tarea is not None and col_num_tarea < len(fila) else ""
            resp      = str(fila[col_resp]).strip()      if col_resp      is not None and col_resp      < len(fila) else ""
            estado    = str(fila[col_estado]).strip().upper() if col_estado is not None and col_estado  < len(fila) else ""

            if not nombre or nombre.upper() in ("NOMBRE TAREA", ""):
                continue

            # Filtrar solo órdenes abiertas (si existe la columna ESTADO)
            if col_estado is not None and estado and estado not in _ESTADOS_ABIERTOS:
                continue

            resultado.append({"orden": nombre, "num_tarea": num_tarea, "responsable": resp})

        _cache_tareas = resultado
        return resultado

    except Exception as e:
        raise   # propagar para que _cargar_tareas_sheets muestre el error real


def limpiar_cache_tareas():
    """Limpia la caché de tareas para forzar recarga."""
    global _cache_tareas
    _cache_tareas = []


def cargar_todo(pais_nombre):
    """
    Carga abreviaturas VIA, abreviaturas URB y categorías en paralelo (3 threads).
    Retorna (dict_abreviaturas_via, dict_abreviaturas_urb, dict_categorias_o_None, exc_cat_o_None).
    """
    import threading

    via_result = [None]; via_error = [None]
    urb_result = [None]; urb_error = [None]
    cat_result = [None]; cat_error = [None]

    def _load_via():
        try:
            via_result[0] = cargar_abreviaturas(pais_nombre)
        except Exception as e:
            via_error[0] = e

    def _load_urb():
        try:
            urb_result[0] = cargar_abreviaturas_urb(pais_nombre)
        except Exception as e:
            urb_error[0] = e

    def _load_cat():
        try:
            cat_result[0] = cargar_categorias(pais_nombre)
        except Exception as e:
            cat_error[0] = e

    t1 = threading.Thread(target=_load_via, daemon=True)
    t2 = threading.Thread(target=_load_urb, daemon=True)
    t3 = threading.Thread(target=_load_cat, daemon=True)
    t1.start(); t2.start(); t3.start()
    t1.join();  t2.join();  t3.join()

    if via_error[0]:
        raise via_error[0]

    return via_result[0], urb_result[0] or {}, cat_result[0], cat_error[0]


# ── Verificación de OT en los 4 sheets de control ────────────────────────────

_MESES_ES = {
    "ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6,
    "jul": 7, "ago": 8, "sep": 9, "oct": 10, "nov": 11, "dic": 12,
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5,
    "junio": 6, "julio": 7, "agosto": 8, "septiembre": 9,
    "octubre": 10, "noviembre": 11, "diciembre": 12,
}


def _parsear_fecha_es(texto) -> str:
    """
    Parsea fechas en formato dd/mm/yyyy, dd-mm-yyyy o 'dd - mes_es - yyyy'.
    Retorna una cadena normalizada 'dd/mm/yyyy' o '' si no reconoce el valor.
    """
    import re
    s = str(texto).strip()
    if not s or s.lower() in ("d/mm/yyyy", "dd/mm/yyyy", ""):
        return ""

    # Numérico: separadores / - .
    m = re.fullmatch(r'(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})', s)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            from datetime import date
            date(y, mo, d)          # valida que la fecha exista
            return f"{d:02d}/{mo:02d}/{y}"
        except ValueError:
            pass

    # Texto con nombre de mes en español: "20 - ene - 2026" / "20-ene-2026"
    m = re.match(r'(\d{1,2})\s*[-/\s]\s*([a-záéíóú]+)\.?\s*[-/\s]\s*(\d{4})', s.lower())
    if m:
        d_str, mes_str, y_str = m.group(1), m.group(2).rstrip('.'), m.group(3)
        mes_num = _MESES_ES.get(mes_str) or _MESES_ES.get(mes_str[:3])
        if mes_num:
            try:
                from datetime import date
                date(int(y_str), mes_num, int(d_str))
                return f"{int(d_str):02d}/{mes_num:02d}/{y_str}"
            except ValueError:
                pass
    return ""


_RE_OT_CODE = re.compile(r'\b((?:INT|OT)\s*\d{3}-\d{2})\b', re.IGNORECASE)


def _codigo_ot(texto: str) -> str:
    """Extrae solo el código OT (ej. 'INT 012-26') de un texto cualquiera.
    Si no hay patrón reconocible devuelve el texto normalizado."""
    m = _RE_OT_CODE.search(str(texto))
    if m:
        # Normalizar espacios internos: 'INT012-26' → 'INT 012-26'
        return re.sub(r'\s+', ' ', m.group(1)).upper()
    return str(texto).strip().upper()


def verificar_ot_en_sheets(ot_numero: str) -> dict:
    """
    Verifica la OT en los 4 sheets de control (Cronograma, Actas, Control de
    Entregas, Control de OT) y retorna un dict estructurado con los hallazgos.

    Estructura retornada:
    {
        "ot":          str,
        "cronograma":  dict | None,   # None = no encontrada
        "actas":       list[dict],    # vacío = no encontrada
        "entregas":    list[dict],    # vacío = no encontrada
        "control_ot":  dict | None,
        "errores":     list[str],     # mensajes de error por sheet
    }
    """
    resultado = {
        "ot":         ot_numero,
        "cronograma": None,
        "actas":      [],
        "entregas":   [],
        "control_ot": None,
        "errores":    [],
    }
    if not ot_numero:
        return resultado

    ot_upper = _codigo_ot(ot_numero)  # solo "INT 012-26", descarta el resto

    try:
        client = _conectar()
    except Exception as e:
        resultado["errores"].append(f"Conexión: {e}")
        return resultado

    # ── 1. Cronograma ────────────────────────────────────────────────────────
    try:
        hoja = client.open_by_key(SHEET_ID_CRONOGRAMA).worksheet(TAB_CRONOGRAMA)
        todos = hoja.get_all_values()
        if todos and len(todos) > HEAD_CRONOGRAMA:
            cab, vistos = [], {}
            for c in todos[HEAD_CRONOGRAMA - 1]:
                k = str(c).strip().upper()
                cab.append(k if k not in vistos else f"__dup_{len(cab)}")
                vistos[k] = True
            for fila in todos[HEAD_CRONOGRAMA:]:
                f = {cab[i]: str(fila[i]).strip() for i in range(min(len(cab), len(fila)))}
                num = _codigo_ot(f.get("NUMERO DE OT", "") or f.get("NUMERO OT", "")
                                 or f.get("N° OT", "") or f.get("NOT", ""))
                if num == ot_upper:
                    resultado["cronograma"] = {
                        "nombre":         f.get("NOMBRE ORDEN DE TRABAJO", f.get("NOMBRE TAREA", "")),
                        "estado":         f.get("ESTADO", ""),
                        "fecha_inicio":   _parsear_fecha_es(f.get("FECHA INICIO", f.get("FECHA DE INICIO", ""))),
                        "fecha_estimado": _parsear_fecha_es(f.get("FECHA ESTIMADO", f.get("FECHA ESTIMADA", ""))),
                        "fecha_fin":      _parsear_fecha_es(f.get("FECHA FINALIZADO", f.get("FECHA FIN", f.get("FECHA FINALIZACION", "")))),
                        "avance":         f.get("AVANCE (%)", f.get("AVANCE", "")),
                        "responsable":    f.get("RESPONSABLE", ""),
                    }
                    break
    except Exception as e:
        resultado["errores"].append(f"Cronograma: {e}")

    # ── 2. Actas de entrega ──────────────────────────────────────────────────
    try:
        hoja = client.open_by_key(SHEET_ID_ACTAS).worksheet(TAB_ACTAS)
        todos = hoja.get_all_values()
        if todos and len(todos) > HEAD_ACTAS:
            cab, vistos = [], {}
            for c in todos[HEAD_ACTAS - 1]:
                k = str(c).strip().upper()
                cab.append(k if k not in vistos else f"__dup_{len(cab)}")
                vistos[k] = True
            for fila in todos[HEAD_ACTAS:]:
                f = {cab[i]: str(fila[i]).strip() for i in range(min(len(cab), len(fila)))}
                ot_int = _codigo_ot(f.get("OT INTERNA", ""))
                if ot_int == ot_upper:
                    resultado["actas"].append({
                        "n_acta":          f.get("N° ACTA", f.get("N ACTA", f.get("ACTA", ""))),
                        "ot_general":      f.get("OT GENERAL", ""),
                        "fecha_inicio_ot": _parsear_fecha_es(f.get("FECHA INICIO OT", "")),
                        "fecha_fin_ot":    _parsear_fecha_es(f.get("FECHA FIN OT", "")),
                        "fecha_acta":      _parsear_fecha_es(f.get("FECHA ACTA", "")),
                    })
    except Exception as e:
        resultado["errores"].append(f"Actas: {e}")

    # ── 3. Control de entregas ───────────────────────────────────────────────
    try:
        hoja = client.open_by_key(SHEET_ID_CONTROL_ENTREGAS).worksheet(TAB_ENTREGAS)
        todos = hoja.get_all_values()
        if todos and len(todos) > HEAD_ENTREGAS:
            cab, vistos = [], {}
            for c in todos[HEAD_ENTREGAS - 1]:
                k = str(c).strip().upper()
                cab.append(k if k not in vistos else f"__dup_{len(cab)}")
                vistos[k] = True
            for fila in todos[HEAD_ENTREGAS:]:
                f = {cab[i]: str(fila[i]).strip() for i in range(min(len(cab), len(fila)))}
                ot_int = _codigo_ot(f.get("OT INTERNA", ""))
                if ot_int == ot_upper:
                    resultado["entregas"].append({
                        "nombre_archivo": f.get("NOMBRE ARCHIVO ENTREGA", f.get("NOMBRE ARCHIVO", "")),
                        "ot_general":     f.get("OT GENERAL", ""),
                        "contexto":       f.get("CONTEXTO", ""),
                        "fecha_entrega":  _parsear_fecha_es(f.get("FECHA ENTREGA", f.get("FECHA_ENTREGA", ""))),
                    })
    except Exception as e:
        resultado["errores"].append(f"Control de entregas: {e}")

    # ── 4. Control de OT ────────────────────────────────────────────────────
    try:
        hoja  = client.open_by_key(SHEET_ID_CONTROL_ORDENES).worksheet(TAB_CONTROL_OT)
        # Leer en crudo para evitar error por encabezados duplicados (celdas combinadas)
        todos = hoja.get_all_values()
        if todos and len(todos) > HEAD_CONTROL_OT:
            cab_raw  = todos[HEAD_CONTROL_OT - 1]  # fila de encabezado (0-based)
            # Desduplicar: conservar solo la primera aparición de cada nombre
            cabeceras = []
            vistos    = {}
            for c in cab_raw:
                key = str(c).strip().upper()
                if key in vistos:
                    cabeceras.append(f"__dup_{len(cabeceras)}")
                else:
                    vistos[key] = True
                    cabeceras.append(key)
            for fila in todos[HEAD_CONTROL_OT:]:
                f = {cabeceras[i]: str(fila[i]).strip()
                     for i in range(min(len(cabeceras), len(fila)))}
                num_t = _codigo_ot(f.get("NUMERO TAREA", "") or f.get("NÚMERO TAREA", ""))
                if num_t == ot_upper:
                    resultado["control_ot"] = {
                        "nombre_tarea":  f.get("NOMBRE TAREA", ""),
                        "responsable":   f.get("RESPONSABLE", ""),
                        "digitalizador": f.get("DIGITALIZADOR", ""),
                        "fecha_inicio":  _parsear_fecha_es(f.get("FECHA INICIO", "")),
                        "fecha_final":   _parsear_fecha_es(f.get("FECHA FINAL",  "")),
                        "estado":        f.get("ESTADO", ""),
                    }
                    break
    except Exception as e:
        resultado["errores"].append(f"Control de OT: {e}")

    return resultado
