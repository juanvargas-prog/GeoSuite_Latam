"""
validar_documentacion.py
------------------------
Valida la documentación de entrega de una OT contra los 3 documentos
de control de Cartografía LATAM.

Documentos validados (Google Sheets):
  - Cronograma          SHEET_ID_CRONOGRAMA,      hoja "LATAM Cronograma"
  - Control de Ordenes  SHEET_ID_CONTROL_ORDENES, hoja "CONTROL DE ORDENES DE TRABAJO"
  - Control de Entregas SHEET_ID_CONTROL_ENTREGAS, hoja "Matriz de Entregas 2026"

Retorna:
    {
        "ot":    str,
        "ok":    bool,
        "errores": {
            "cronograma":      [str, ...],
            "control_ordenes": [str, ...],
            "control_entregas":[str, ...],
            "cruce":           [str, ...],
        },
        "datos": {
            "cronograma":      {nombre, f_inicio, f_fin, responsable},
            "control_ordenes": {nombre, f_inicio, f_fin},
            "control_entregas":{fecha, fecha_s},
        },
    }
"""

import re
from datetime import date, datetime, timedelta


# ── Helpers ───────────────────────────────────────────────────────────────────

def _norm(s):
    return str(s).strip().upper() if s is not None else ""


def _get(fila, idx):
    if idx is None or idx < 0 or idx >= len(fila):
        return ""
    v = fila[idx]
    return "" if v is None else str(v).strip()


def _col(headers, nombre):
    """Índice de la primera columna cuyo encabezado coincide (case-insensitive)."""
    n = nombre.strip().upper()
    for i, h in enumerate(headers):
        if str(h).strip().upper() == n:
            return i
    return None


def _encontrar_headers(filas, campo_clave):
    """
    Localiza la fila de encabezados buscando `campo_clave`.
    Retorna (headers_list, data_start_index) o (None, 0) si no se encuentra.
    """
    clave = campo_clave.strip().upper()
    for i, fila in enumerate(filas):
        if any(str(c).strip().upper() == clave for c in fila):
            return fila, i + 1
    return None, 0


def _parsear_fecha(s):
    """Convierte un string de fecha a ``date``, o ``None`` si no es parseable."""
    if not s or str(s).strip() in ("", "d/mm/yyyy", "None", "NULL", "0"):
        return None
    s = str(s).strip()
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    # Serial numérico de Sheets (por si llega con UNFORMATTED_VALUE)
    try:
        return date(1899, 12, 30) + timedelta(days=int(float(s)))
    except (ValueError, TypeError):
        pass
    return None


# ── Validación principal ──────────────────────────────────────────────────────

def validar_documentacion(ot):
    """
    Valida la documentación de entrega de una OT.

    :param ot:  código de la orden (ej: "INT 017-26")
    :returns:   dict con "ok", "errores" y "datos"
    """
    from .sheets_loader import (
        _conectar,
        SHEET_ID_CRONOGRAMA,
        SHEET_ID_CONTROL_ORDENES,
        SHEET_ID_CONTROL_ENTREGAS,
        SHEET_ID_ACTAS,
    )

    errores = {
        "cronograma":       [],
        "control_ordenes":  [],
        "control_entregas": [],
        "actas":            [],
        "cruce":            [],
    }
    datos = {}

    if not ot or not ot.strip():
        errores["cruce"].append("No hay OT seleccionada — selecciona una orden primero")
        return {"ot": ot, "errores": errores, "datos": datos, "ok": False}

    ot_norm = ot.strip().upper()
    hoy     = date.today()

    try:
        gc = _conectar()
    except Exception as e:
        errores["cruce"].append(
            "No se pudo conectar con Google Sheets. "
            "Verifica tu conexión a internet y que las credenciales estén configuradas correctamente."
        )
        return {"ot": ot, "errores": errores, "datos": datos, "ok": False}

    # ── 1. CRONOGRAMA ──────────────────────────────────────────────────────────
    crono = {}
    try:
        ws    = gc.open_by_key(SHEET_ID_CRONOGRAMA).worksheet("LATAM Cronograma")
        filas = ws.get_all_values()
        hdrs, data_ini = _encontrar_headers(filas, "Numero de OT")
        if hdrs is None:
            errores["cronograma"].append(
                "No se encontró la fila de encabezados en Cronograma"
            )
        else:
            c_ot     = _col(hdrs, "Numero de OT")
            c_nombre = _col(hdrs, "Nombre Orden de Trabajo")
            c_estado = _col(hdrs, "Estado")
            c_f_ini  = _col(hdrs, "Fecha Inicio")
            c_f_est  = _col(hdrs, "Fecha Estimado")
            c_f_fin  = _col(hdrs, "Fecha Finalizado")
            c_resp   = _col(hdrs, "Responsable")

            fila = next(
                (r for r in filas[data_ini:] if _norm(_get(r, c_ot)) == ot_norm),
                None,
            )
            if fila is None:
                errores["cronograma"].append(
                    f"La OT '{ot}' no se encontró en el Cronograma"
                )
            else:
                estado  = _norm(_get(fila, c_estado))
                f_est_s = _get(fila, c_f_est)
                f_fin_s = _get(fila, c_f_fin)
                f_fin   = _parsear_fecha(f_fin_s)
                f_ini   = _parsear_fecha(_get(fila, c_f_ini))
                resp    = _get(fila, c_resp)

                if estado != "COMPLETADO":
                    errores["cronograma"].append(
                        f"Estado es '{_get(fila, c_estado)}' — debe ser 'Completado'"
                    )
                if not f_est_s:
                    errores["cronograma"].append(
                        "Fecha Estimado no está diligenciada"
                    )
                if f_fin is None:
                    errores["cronograma"].append(
                        "Fecha Finalizado no está diligenciada"
                    )
                elif f_fin != hoy:
                    errores["cronograma"].append(
                        f"Fecha Finalizado es '{f_fin_s}' — debe ser hoy "
                        f"({hoy.strftime('%d/%m/%Y')})"
                    )
                if not resp:
                    errores["cronograma"].append(
                        "Responsable no está diligenciado"
                    )

                crono = {
                    "nombre":      _get(fila, c_nombre),
                    "f_inicio":    f_ini,
                    "f_fin":       f_fin,
                    "responsable": resp,
                }
                datos["cronograma"] = crono

    except Exception as e:
        errores["cronograma"].append(
            "No se pudo leer el Cronograma. Verifica que el documento esté accesible y tenga el formato esperado."
        )

    # ── 2. CONTROL DE ORDENES ──────────────────────────────────────────────────
    ordenes = {}
    try:
        ws    = gc.open_by_key(SHEET_ID_CONTROL_ORDENES).worksheet(
            "CONTROL DE ORDENES DE TRABAJO"
        )
        filas = ws.get_all_values()
        hdrs, data_ini = _encontrar_headers(filas, "NUMERO TAREA")
        if hdrs is None:
            errores["control_ordenes"].append(
                "No se encontró la fila de encabezados en Control de Ordenes"
            )
        else:
            c_tarea  = _col(hdrs, "NUMERO TAREA")
            c_nombre = _col(hdrs, "NOMBRE ORDEN DE TRABAJO")
            c_resp   = _col(hdrs, "RESPONSABLE")
            c_digit  = _col(hdrs, "DIGITALIZADOR")
            c_f_ini  = _col(hdrs, "FECHA INICIO")
            c_f_fin  = _col(hdrs, "FECHA FINAL")
            c_estado = _col(hdrs, "ESTADO")

            fila = next(
                (r for r in filas[data_ini:] if _norm(_get(r, c_tarea)) == ot_norm),
                None,
            )
            if fila is None:
                errores["control_ordenes"].append(
                    f"La OT '{ot}' no se encontró en Control de Ordenes"
                )
            else:
                estado  = _norm(_get(fila, c_estado))
                f_ini_s = _get(fila, c_f_ini)
                f_fin_s = _get(fila, c_f_fin)
                f_ini   = _parsear_fecha(f_ini_s)
                f_fin   = _parsear_fecha(f_fin_s)

                if estado != "CERRADO":
                    errores["control_ordenes"].append(
                        f"Estado es '{_get(fila, c_estado)}' — debe ser 'cerrado'"
                    )
                for campo, val in [
                    ("RESPONSABLE",   _get(fila, c_resp)),
                    ("DIGITALIZADOR", _get(fila, c_digit)),
                    ("FECHA INICIO",  f_ini_s),
                    ("FECHA FINAL",   f_fin_s),
                ]:
                    if not val:
                        errores["control_ordenes"].append(
                            f"{campo} no está diligenciado"
                        )

                ordenes = {
                    "nombre":   _get(fila, c_nombre),
                    "f_inicio": f_ini,
                    "f_fin":    f_fin,
                }
                datos["control_ordenes"] = ordenes

    except Exception as e:
        errores["control_ordenes"].append(
            "No se pudo leer el Control de Órdenes. Verifica que el documento esté accesible y tenga el formato esperado."
        )

    # ── 3. CONTROL DE ENTREGAS ──────────────────────────────────────────────────
    entregas = {}
    try:
        ws    = gc.open_by_key(SHEET_ID_CONTROL_ENTREGAS).worksheet(
            "Matriz de Entregas 2026"
        )
        filas = ws.get_all_values()
        hdrs, data_ini = _encontrar_headers(filas, "OT INTERNA")
        if hdrs is None:
            errores["control_entregas"].append(
                "No se encontró la fila de encabezados en Control de Entregas"
            )
        else:
            c_ot    = _col(hdrs, "OT INTERNA")
            c_fecha = _col(hdrs, "fecha")

            fila = next(
                (r for r in filas[data_ini:] if _norm(_get(r, c_ot)) == ot_norm),
                None,
            )
            if fila is None:
                errores["control_entregas"].append(
                    f"La OT '{ot}' no se encontró en Control de Entregas"
                )
            else:
                # Columnas A–H deben tener datos
                for i, letra in enumerate("ABCDEFGH"):
                    if not _get(fila, i):
                        errores["control_entregas"].append(
                            f"Columna {letra} sin datos"
                        )
                fecha_s = _get(fila, c_fecha)
                entregas = {"fecha": _parsear_fecha(fecha_s), "fecha_s": fecha_s}
                datos["control_entregas"] = entregas

    except Exception as e:
        errores["control_entregas"].append(
            "No se pudo leer el Control de Entregas. Verifica que el documento esté accesible y tenga el formato esperado."
        )

    # ── 4. CONSECUTIVO ACTAS DE ENTREGA ───────────────────────────────────────
    actas = {}
    try:
        ws    = gc.open_by_key(SHEET_ID_ACTAS).worksheet("Actas de Entrega 2026")
        filas = ws.get_all_values()
        hdrs, data_ini = _encontrar_headers(filas, "OT INTERNA")
        if hdrs is None:
            errores["actas"].append(
                "No se encontró la fila de encabezados en el Consecutivo de Actas"
            )
        else:
            c_ot_int  = _col(hdrs, "OT INTERNA")
            c_ot_gen  = _col(hdrs, "OT GENERAL")
            c_n_acta  = _col(hdrs, "Nº Acta")
            c_f_acta  = _col(hdrs, "Fecha ACTA")
            c_f_ini   = _col(hdrs, "FECHA INICIO OT")
            c_f_fin   = _col(hdrs, "FECHA FIN OT")
            c_cliente = _col(hdrs, "Cliente")

            fila = next(
                (r for r in filas[data_ini:] if _norm(_get(r, c_ot_int)) == ot_norm),
                None,
            )
            if fila is None:
                errores["actas"].append(
                    f"La OT '{ot}' no se encontró en el Consecutivo de Actas de Entrega"
                )
            else:
                n_acta  = _get(fila, c_n_acta)
                f_acta_s = _get(fila, c_f_acta)
                f_acta   = _parsear_fecha(f_acta_s)

                if not n_acta:
                    errores["actas"].append("El Nº de Acta no está diligenciado")
                if not f_acta_s:
                    errores["actas"].append("La Fecha del Acta no está diligenciada")

                actas = {
                    "n_acta":  n_acta,
                    "f_acta":  f_acta,
                    "ot_gen":  _get(fila, c_ot_gen),
                    "cliente": _get(fila, c_cliente),
                }
                datos["actas"] = actas

    except Exception:
        errores["actas"].append(
            "No se pudo leer el Consecutivo de Actas. Verifica que el documento esté accesible."
        )

    # ── 5. CRUCES ──────────────────────────────────────────────────────────────
    if crono and ordenes:
        fi_c = crono.get("f_inicio")
        fi_o = ordenes.get("f_inicio")
        if fi_c and fi_o and fi_c != fi_o:
            errores["cruce"].append(
                f"Fecha Inicio no coincide:\n"
                f"  Cronograma:         {fi_c.strftime('%d/%m/%Y')}\n"
                f"  Control de Ordenes: {fi_o.strftime('%d/%m/%Y')}"
            )

        ff_c = crono.get("f_fin")
        ff_o = ordenes.get("f_fin")
        if ff_c and ff_o and ff_c != ff_o:
            errores["cruce"].append(
                f"Fecha Final no coincide:\n"
                f"  Cronograma (Fecha Finalizado):    {ff_c.strftime('%d/%m/%Y')}\n"
                f"  Control de Ordenes (FECHA FINAL): {ff_o.strftime('%d/%m/%Y')}"
            )

    if crono and entregas:
        ff_c = crono.get("f_fin")
        f_e  = entregas.get("fecha")
        if ff_c and f_e and ff_c != f_e:
            errores["cruce"].append(
                f"Fecha de entrega no coincide:\n"
                f"  Cronograma (Fecha Finalizado): {ff_c.strftime('%d/%m/%Y')}\n"
                f"  Control de Entregas (fecha):   {entregas.get('fecha_s', '?')}"
            )

    ok = not any(errores.values())
    return {"ot": ot, "errores": errores, "datos": datos, "ok": ok}


# ── Validación de archivos en carpeta Drive ───────────────────────────────────

def validar_archivos_carpeta(archivos):
    """
    Verifica que los archivos requeridos estén presentes en la carpeta Drive.

    Requeridos:
      - Google Doc  con "acta de entrega" en el nombre   (Acta de Entrega)
      - Google Sheets con "plan de trabajo" en el nombre (Plan de Trabajo Global)
      - PDF          con "informe" en el nombre          (Informe de Actualización)

    :param archivos: lista de dicts {name, mimeType, ...} de Drive
    :returns: {"ok": bool, "errores": [str], "encontrados": {clave: nombre}}
    """
    _MIME_DOC   = "application/vnd.google-apps.document"
    _MIME_SHEET = "application/vnd.google-apps.spreadsheet"
    _MIME_PDF   = "application/pdf"

    errores     = []
    encontrados = {}

    def _nom(f):
        return f.get("name", "").lower()

    def _mime(f):
        return f.get("mimeType", "")

    def _buscar(cond):
        return next((f for f in archivos if cond(f)), None)

    acta_f = _buscar(lambda f: "acta" in _nom(f) and _mime(f) == _MIME_DOC)
    plan_f = _buscar(lambda f: ("plan" in _nom(f) or "trabajo" in _nom(f))
                               and _mime(f) == _MIME_SHEET)
    inf_f  = _buscar(lambda f: "informe" in _nom(f) and _mime(f) == _MIME_PDF)

    if not acta_f:
        errores.append("Falta el Acta de Entrega (Google Doc con 'acta' en el nombre)")
    else:
        encontrados["acta"] = acta_f["name"]

    if not plan_f:
        errores.append(
            "Falta el Plan de Trabajo Global (Google Sheets con 'plan' o 'trabajo' en el nombre)"
        )
    else:
        encontrados["plan"] = plan_f["name"]

    if not inf_f:
        errores.append("Falta el Informe de Actualización (PDF con 'informe' en el nombre)")
    else:
        encontrados["informe"] = inf_f["name"]

    return {"ok": not errores, "errores": errores, "encontrados": encontrados}


# ── Carpeta de Drive ──────────────────────────────────────────────────────────

def extraer_id_drive(url_o_id):
    """
    Extrae el folder ID de un link de Google Drive o lo retorna directamente
    si ya es un ID.

    Formatos soportados:
      https://drive.google.com/drive/folders/1ABC...xyz
      https://drive.google.com/drive/u/0/folders/1ABC...xyz
      1ABC...xyz  (ID directo)
    """
    if not url_o_id:
        return None
    url_o_id = url_o_id.strip()
    m = re.search(r"/folders/([a-zA-Z0-9_-]{10,})", url_o_id)
    if m:
        return m.group(1)
    # Si parece un ID directo (solo alfanumérico y guiones, > 10 chars)
    if re.match(r"^[a-zA-Z0-9_-]{10,}$", url_o_id):
        return url_o_id
    return None


def listar_carpeta_drive(folder_id):
    """
    Lista los archivos de una carpeta de Google Drive.

    :param folder_id: ID de la carpeta Drive
    :returns: list of dict {name, mimeType, modifiedTime, id}
    :raises:  Exception si no se puede conectar o acceder
    """
    from .sheets_loader import _obtener_credenciales

    try:
        from googleapiclient.discovery import build as _build
    except ImportError:
        raise RuntimeError(
            "La librería 'google-api-python-client' no está instalada. "
            "Instálala con: pip install google-api-python-client"
        )

    creds   = _obtener_credenciales()
    service = _build("drive", "v3", credentials=creds)

    query   = f"'{folder_id}' in parents and trashed=false"
    results = service.files().list(
        q=query,
        fields="files(id, name, mimeType, modifiedTime)",
        orderBy="name",
        pageSize=100,
        corpora="allDrives",
        includeItemsFromAllDrives=True,
        supportsAllDrives=True,
    ).execute()

    return results.get("files", [])
