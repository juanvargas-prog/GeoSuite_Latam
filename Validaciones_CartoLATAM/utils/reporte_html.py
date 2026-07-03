"""
reporte_html.py
---------------
Genera un reporte HTML interactivo liviano + archivos CSV separados.

Estructura de salida:
  reporte_validacion_PAIS/
    reporte.html          — estadísticas, KPIs, gráficas, tablas de muestra
    NOMBRECAPA_errores.csv — todos los errores de la capa
    ...

El HTML no incrusta los datos CSV — solo los referencia con links relativos.
Esto evita que el HTML se vuelva pesado con bases grandes.
"""

import concurrent.futures
import html as _html_mod
import os
import json
import csv
from datetime import datetime
from collections import defaultdict

# Etiquetas de tipo geométrico compartidas con gmail_sender.py
GEOM_LABEL = {"linea": "líneas", "punto": "puntos", "poligono": "polígonos"}

def _e(valor) -> str:
    """Escapa caracteres HTML de cualquier valor de usuario. Previene XSS."""
    return _html_mod.escape(str(valor) if valor is not None else "")


# ─────────────────────────────────────────────────────────────────────────────
# Estadísticas
# ─────────────────────────────────────────────────────────────────────────────

def construir_stats(nombre_capa, resultados_capa):
    total      = len(resultados_capa)
    con_error  = sum(1 for _, _, e in resultados_capa if e)
    sin_error  = total - con_error
    pct_calidad = round(sin_error * 100 / total, 1) if total else 0

    errores_por_campo = defaultdict(list)
    for fid, d, errs in resultados_capa:
        for campo, msgs in errs.items():
            for msg in msgs:
                errores_por_campo[campo].append({
                    "fid":   fid,
                    "valor": str(d.get(campo, "")),
                    "msg":   msg,
                })

    campos_ordenados = sorted(errores_por_campo.keys(),
                              key=lambda c: len(errores_por_campo[c]),
                              reverse=True)
    return {
        "nombre":           nombre_capa,
        "total":            total,
        "con_error":        con_error,
        "sin_error":        sin_error,
        "pct_calidad":      pct_calidad,
        "n_campos_error":   len(errores_por_campo),
        "campos_ordenados": campos_ordenados,
        "errores_por_campo": dict(errores_por_campo),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Generación de CSVs separados
# ─────────────────────────────────────────────────────────────────────────────

def _generar_csvs(stats_capas, carpeta_salida):
    """
    Genera un CSV por capa con todos sus errores de atributos.
    Retorna dict {nombre_capa: nombre_archivo_csv}
    """
    archivos_csv = {}
    for s in stats_capas:
        if not s["campos_ordenados"]:
            continue
        nombre_csv = f"{s['nombre'].replace(' ', '_')}_errores.csv"
        ruta_csv   = os.path.join(carpeta_salida, nombre_csv)
        with open(ruta_csv, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["fid", "estado", "campo", "valor", "error"])
            for campo in s["campos_ordenados"]:
                for item in s["errores_por_campo"][campo]:
                    writer.writerow([item["fid"], "ERROR", campo, item["valor"], item["msg"]])
        archivos_csv[s["nombre"]] = nombre_csv
    return archivos_csv


def _generar_csvs_topologia(topo_resultados, carpeta_salida):
    """
    Genera un CSV por capa con sus errores topológicos.
    Retorna dict {nombre_capa: nombre_archivo_csv}
    """
    archivos = {}
    for tr in (topo_resultados or []):
        if not tr["errores"]:
            continue
        nombre_csv = f"{tr['nombre_capa'].replace(' ', '_')}_topologia.csv"
        ruta_csv   = os.path.join(carpeta_salida, nombre_csv)
        with open(ruta_csv, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["fid", "regla", "descripcion"])
            for err in tr["errores"]:
                writer.writerow([err["fid"], err["regla"], err["descripcion"]])
        archivos[tr["nombre_capa"]] = nombre_csv
    return archivos


def _generar_csvs_cruce_espacial(inconsistencias, carpeta_salida):
    """
    Genera un CSV por capa origen con todos sus errores de cruce (espacial + placa-mavvial).
    Columnas: capa_origen, tipo_geom, campo, ref, tipo, fid, val_actual, val_esperado
    Retorna {nombre_capa: nombre_archivo_csv}
    """
    _TIPOS_ITEMS = {"inconsistencia_espacial", "sin_poligono_contenedor",
                    "cruce_placa_mavvial", "id_mavvial_huerfano"}
    from collections import defaultdict
    por_capa = defaultdict(list)
    for i in inconsistencias:
        if i["tipo"] not in _TIPOS_ITEMS:
            continue
        pol_ref = ", ".join(i.get("capas_referencia") or [])
        for fid, val_a, val_e in i.get("items", []):
            por_capa[i["capa_origen"]].append(
                (i["capa_origen"], i.get("tipo_geom", ""), i["campo"],
                 pol_ref, i["tipo"], fid, val_a, val_e)
            )

    archivos = {}
    for nom_capa, filas in por_capa.items():
        nombre_csv = f"{nom_capa.replace(' ', '_')}_cruce_espacial.csv"
        ruta_csv   = os.path.join(carpeta_salida, nombre_csv)
        with open(ruta_csv, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["capa_origen", "tipo_geom", "campo", "pol_referencia",
                             "tipo", "fid", "val_actual", "val_esperado"])
            writer.writerows(filas)
        archivos[nom_capa] = nombre_csv
    return archivos


def _generar_csv_resumen(stats_capas, carpeta_salida):
    """
    CSV global de resumen para profesionals: capa, campo, n_errores.
    Una fila por campo con errores, ordenadas por capa y luego por n_errores desc.
    """
    nombre_csv = "resumen_errores.csv"
    ruta_csv   = os.path.join(carpeta_salida, nombre_csv)
    with open(ruta_csv, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["capa", "campo", "n_errores"])
        for s in stats_capas:
            for campo in s["campos_ordenados"]:
                writer.writerow([s["nombre"], campo,
                                 len(s["errores_por_campo"][campo])])
    return nombre_csv


# ─────────────────────────────────────────────────────────────────────────────
# Helpers de color
# ─────────────────────────────────────────────────────────────────────────────

def _color(pct):
    return "#27ae60" if pct >= 90 else "#f39c12" if pct >= 70 else "#e74c3c"

def _badge(pct):
    if pct >= 90: return "BUENA",   "#27ae60"
    if pct >= 70: return "REGULAR", "#f39c12"
    return              "CRÍTICA",  "#e74c3c"


# ─────────────────────────────────────────────────────────────────────────────
# Generación HTML
# ─────────────────────────────────────────────────────────────────────────────

def _sev_badge(msg):
    """Badge HTML de severidad para el reporte de entrega."""
    try:
        from .clasificador_errores import clasificar, severidad, color_severidad
        sev      = severidad(clasificar(msg))
        bg, fg   = color_severidad(sev)
        return (f'<span style="background:{bg};color:{fg};padding:1px 6px;'
                f'border-radius:8px;font-size:10px;font-weight:700;'
                f'white-space:nowrap">{sev}</span>')
    except Exception:
        return ""


def _html_bloque_entrega(bloque):
    """
    Genera el HTML del bloque de resumen de entrega que va al inicio del reporte.

    bloque = {
        "pais":           str,
        "ot":             str,
        "drive_url":      str,
        "drive_archivos": [{"name": str, "mimeType": str, "modifiedTime": str}],
        "doc_resultado":  dict | None,   # resultado de validar_documentacion()
        "capas":          [{"nombre": str, "tipo_geom": str, "n_registros": int}]
    }
    """
    _MIME_ICON = {
        "application/vnd.google-apps.folder":       "📁",
        "application/vnd.google-apps.spreadsheet":  "📊",
        "application/vnd.google-apps.document":     "📄",
        "application/pdf":                          "📕",
        "application/zip":                          "🗜",
        "application/x-zip-compressed":             "🗜",
        "image/png":                                "🖼",
        "image/jpeg":                               "🖼",
    }

    pais             = _e(bloque.get("pais", ""))
    ot               = _e(bloque.get("ot", ""))
    drive_url        = bloque.get("drive_url", "").strip()
    drive_archivos   = bloque.get("drive_archivos") or []
    doc_resultado    = bloque.get("doc_resultado")
    capas            = bloque.get("capas", [])
    fecha            = datetime.now().strftime("%m-%Y")
    version          = f"V1-{datetime.now().strftime('%y')}"
    total_reg        = sum(c.get("n_registros", 0) for c in capas)

    # ── Tabla de capas ────────────────────────────────────────────────────────
    filas_capas = ""
    for c in capas:
        geom_label = GEOM_LABEL.get(c.get("tipo_geom", ""), c.get("tipo_geom", "—"))
        n_reg      = c.get("n_registros", 0)
        filas_capas += (
            f"<tr>"
            f"<td style='padding:7px 14px;border-bottom:1px solid #dee2e6;'>{_e(c.get('nombre',''))}</td>"
            f"<td style='padding:7px 14px;border-bottom:1px solid #dee2e6;text-align:center;'>{_e(geom_label)}</td>"
            f"<td style='padding:7px 14px;border-bottom:1px solid #dee2e6;text-align:right;'>{n_reg:,}</td>"
            f"</tr>"
        )

    ruta_html = (
        f"<a href='{_e(drive_url)}' style='color:#1a73e8;'>{ot}</a>"
        if drive_url else ot
    )

    # ── Sección documentación ─────────────────────────────────────────────────
    _SEC_STYLE  = "margin:24px 0 0 0;padding-top:18px;border-top:1px solid #dee2e6;"
    _HDR_STYLE  = "font-size:13px;font-weight:700;color:#1565c0;margin:0 0 10px 0;letter-spacing:.3px;"
    _OK_BADGE   = "<span style='color:#fff;background:#2e7d32;border-radius:4px;padding:2px 8px;font-size:11px;font-weight:700;'>OK</span>"
    _WARN_BADGE = "<span style='color:#fff;background:#c62828;border-radius:4px;padding:2px 8px;font-size:11px;font-weight:700;'>Observaciones</span>"

    seccion_doc = ""
    if doc_resultado:
        errores_doc = doc_resultado.get("errores", {})
        _SHEETS = [
            ("cronograma",       "Cronograma"),
            ("control_ordenes",  "Control de Órdenes"),
            ("control_entregas", "Control de Entregas"),
            ("actas",            "Consecutivo de Actas de Entrega"),
            ("cruce",            "Cruce entre documentos"),
        ]
        filas_doc = ""
        for clave, etiqueta in _SHEETS:
            errs = errores_doc.get(clave, [])
            badge = _OK_BADGE if not errs else _WARN_BADGE
            detalle = ""
            if errs:
                items = "".join(
                    f"<li style='margin:2px 0;color:#c62828;'>{_e(er)}</li>"
                    for er in errs
                )
                detalle = f"<ul style='margin:4px 0 0 16px;padding:0;font-size:12px;'>{items}</ul>"
            filas_doc += (
                f"<tr>"
                f"<td style='padding:7px 14px;border-bottom:1px solid #f0f0f0;font-size:13px;'>"
                f"  {_e(etiqueta)}"
                f"  {detalle}"
                f"</td>"
                f"<td style='padding:7px 14px;border-bottom:1px solid #f0f0f0;text-align:center;'>{badge}</td>"
                f"</tr>"
            )
        seccion_doc = (
            f"<div style='{_SEC_STYLE}'>"
            f"<p style='{_HDR_STYLE}'>&#9989; VALIDACIÓN DE DOCUMENTACIÓN</p>"
            f"<table style='width:100%;border-collapse:collapse;font-size:13px;'>"
            f"<thead><tr style='background:#e3f2fd;'>"
            f"<th style='padding:8px 14px;text-align:left;font-weight:600;color:#1565c0;'>Documento</th>"
            f"<th style='padding:8px 14px;text-align:center;font-weight:600;color:#1565c0;'>Estado</th>"
            f"</tr></thead>"
            f"<tbody>{filas_doc}</tbody>"
            f"</table></div>"
        )

    # ── Sección carpeta Drive ─────────────────────────────────────────────────
    seccion_drive = ""
    if not drive_url:
        seccion_drive = (
            f"<div style='{_SEC_STYLE}'>"
            f"<p style='{_HDR_STYLE}'>&#128193; CARPETA DE ENTREGA DRIVE</p>"
            f"<p style='color:#856404;background:#fff3cd;padding:10px 14px;"
            f"border-radius:6px;font-size:13px;margin:0;'>"
            f"&#9888; Link de carpeta Drive no proporcionado — archivos no verificados</p>"
            f"</div>"
        )
    elif drive_url and not drive_archivos:
        seccion_drive = (
            f"<div style='{_SEC_STYLE}'>"
            f"<p style='{_HDR_STYLE}'>&#128193; CARPETA DE ENTREGA DRIVE</p>"
            f"<p style='margin:0 0 6px 0;font-size:12px;color:#6c757d;'>"
            f"  <a href='{_e(drive_url)}' style='color:#1a73e8;'>Ver carpeta</a></p>"
            f"<p style='color:#856404;background:#fff3cd;padding:10px 14px;"
            f"border-radius:6px;font-size:13px;margin:0;'>"
            f"&#9888; Carpeta registrada pero los archivos no fueron verificados — "
            f"usa 'Verificar ahora' antes de validar para revisar el contenido.</p>"
            f"</div>"
        )
    elif drive_archivos:
        filas_drive = ""
        for f in drive_archivos:
            icon  = _MIME_ICON.get(f.get("mimeType", ""), "📎")
            nombre = _e(f.get("name", ""))
            fecha_mod = f.get("modifiedTime", "")[:10]
            filas_drive += (
                f"<tr>"
                f"<td style='padding:6px 14px;border-bottom:1px solid #f0f0f0;'>"
                f"  {icon}&nbsp; {nombre}"
                f"</td>"
                f"<td style='padding:6px 14px;border-bottom:1px solid #f0f0f0;text-align:right;"
                f"  font-size:12px;color:#6c757d;'>{_e(fecha_mod)}</td>"
                f"</tr>"
            )
        n_arch = len(drive_archivos)
        seccion_drive = (
            f"<div style='{_SEC_STYLE}'>"
            f"<p style='{_HDR_STYLE}'>&#128193; CARPETA DE ENTREGA DRIVE"
            f"  <span style='font-weight:400;color:#6c757d;font-size:12px;'>"
            f"    ({n_arch} archivo{'s' if n_arch != 1 else ''})</span></p>"
            f"<table style='width:100%;border-collapse:collapse;font-size:13px;'>"
            f"<tbody>{filas_drive}</tbody>"
            f"</table></div>"
        )

    return f"""
<div style="font-family:Arial,sans-serif;font-size:14px;color:#212529;
            max-width:720px;margin:0 auto 32px auto;padding:24px;
            background:#fff;border-radius:8px;border:1px solid #dee2e6;">

  <p style="margin:0 0 18px 0;">
    A continuación, se realiza entrega capas cartografía <strong>{pais}</strong>,
    enfoque principal nuevos registros placa.
  </p>

  <p style="margin:4px 0;"><strong>Ver Carpeta:</strong> {ruta_html}</p>
  <p style="margin:4px 0;"><strong>Fecha:</strong> {_e(fecha)}</p>
  <p style="margin:4px 0;"><strong>Versión:</strong> {_e(version)}</p>
  <p style="margin:4px 0 18px 0;"><strong>Ruta de acceso:</strong> {ruta_html}</p>

  <table style="width:100%;border-collapse:collapse;font-size:13px;">
    <thead>
      <tr style="background:#1565c0;color:#fff;">
        <th style="padding:9px 14px;text-align:left;">NOMBRE CAPA</th>
        <th style="padding:9px 14px;text-align:center;">TIPO DE GEOMETRÍA</th>
        <th style="padding:9px 14px;text-align:right;">REGISTROS</th>
      </tr>
    </thead>
    <tbody>
      {filas_capas}
      <tr style="background:#1565c0;color:#fff;font-weight:700;">
        <td style="padding:9px 14px;">Total</td>
        <td></td>
        <td style="padding:9px 14px;text-align:right;">{total_reg:,}</td>
      </tr>
    </tbody>
  </table>

  {seccion_doc}
  {seccion_drive}

  <p style="margin:24px 0 4px 0;padding-top:18px;border-top:1px solid #dee2e6;">
    Agradezco de antemano su confirmación una vez que la información haya sido
    cargada en la plataforma o se completen las fases de carga establecidas.
  </p>
  <p style="margin:0;">Atentamente,</p>
</div>
"""


def _comentario_sec(bloque_entrega) -> str:
    comentario = (bloque_entrega or {}).get("comentario", "").strip()
    if not comentario:
        return ""
    return (
        '  <section class="section">\n'
        '    <h2 class="sec-title">Comentarios del validador</h2>\n'
        '    <div style="background:#fefce8;border-left:4px solid #f59e0b;'
        'padding:14px 18px;border-radius:6px;font-size:13px;color:#374151;'
        f'white-space:pre-wrap;line-height:1.6">{_e(comentario)}</div>\n'
        '  </section>\n'
    )


def generar(stats_capas, inconsistencias_cruce, pais, tiempo_total_s, ruta_salida,
            topo_resultados=None, tarea="", bloque_entrega=None):
    """
    Genera el reporte HTML y los CSVs en una carpeta junto a ruta_salida.

    ruta_salida:     ruta completa del archivo .html (ej: /ruta/reporte.html)
    Los CSVs se guardan en la misma carpeta que el HTML.
    topo_resultados: lista de {"nombre_capa", "tipo", "errores"} (opcional).
    bloque_entrega:  dict con datos de la entrega — si se pasa, se inyecta al
                     inicio del HTML como resumen de capas entregadas.
    """
    carpeta_salida = os.path.dirname(ruta_salida)
    os.makedirs(carpeta_salida, exist_ok=True)

    # Generar los 4 CSVs en paralelo — todos son I/O-bound sobre archivos distintos
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as _csv_ex:
        _f_attr = _csv_ex.submit(_generar_csvs,               stats_capas,                   carpeta_salida)
        _f_topo = _csv_ex.submit(_generar_csvs_topologia,     topo_resultados,                carpeta_salida)
        _f_res  = _csv_ex.submit(_generar_csv_resumen,         stats_capas,                   carpeta_salida)
        _f_esp  = _csv_ex.submit(_generar_csvs_cruce_espacial, inconsistencias_cruce or [],   carpeta_salida)
        archivos_csv           = _f_attr.result()
        archivos_csv_topo      = _f_topo.result()
        csv_resumen            = _f_res.result()
        archivos_csv_cruce_esp = _f_esp.result()

    fecha_hora = datetime.now().strftime("%d/%m/%Y %H:%M")
    total_feat = sum(s["total"]     for s in stats_capas)
    total_err  = sum(s["con_error"] for s in stats_capas)
    pct_global = round((total_feat - total_err) * 100 / total_feat, 1) if total_feat else 0
    col_global = _color(pct_global)

    # Datos para Chart.js (solo labels y conteos, sin valores individuales)
    graficas = []
    for idx, s in enumerate(stats_capas):
        top = s["campos_ordenados"][:8]
        graficas.append({
            "id":     f"chart-{idx}",
            "labels": top,
            "data":   [len(s["errores_por_campo"][c]) for c in top],
        })
    graficas_json = json.dumps(graficas, ensure_ascii=False)

    # ── Tarjetas ──────────────────────────────────────────────────────────
    _tarjetas_parts = []
    for s in stats_capas:
        etiq, cbadge = _badge(s["pct_calidad"])
        col = _color(s["pct_calidad"])
        _tarjetas_parts.append(
            '<div class="card">'
              '<div class="card-header">'
                f'<span class="card-title">{_e(s["nombre"])}</span>'
                f'<span class="badge" style="background:{cbadge}">{etiq}</span>'
              '</div>'
              '<div class="qbar-bg">'
                f'<div class="qbar-fill" style="width:{s["pct_calidad"]}%;background:{col}"></div>'
              '</div>'
              '<div class="card-stats">'
                f'<div class="stat"><span class="stat-n">{s["total"]:,}</span>'
                  '<span class="stat-l">Features</span></div>'
                f'<div class="stat ok"><span class="stat-n">{s["sin_error"]:,}</span>'
                  '<span class="stat-l">&#10003; Sin error</span></div>'
                f'<div class="stat err"><span class="stat-n">{s["con_error"]:,}</span>'
                  '<span class="stat-l">&#10007; Con error</span></div>'
                f'<div class="stat"><span class="stat-n" style="color:{col}">{s["pct_calidad"]}%</span>'
                  '<span class="stat-l">Calidad</span></div>'
              '</div>'
            '</div>'
        )
    tarjetas = "".join(_tarjetas_parts)

    # ── Detalle por capa (muestra máx 100 errores por campo en HTML) ──────
    _detalle_parts = []
    for idx, s in enumerate(stats_capas):
        nombre_esc = s["nombre"].replace("'", "\\'")
        csv_file   = archivos_csv.get(s["nombre"], "")

        _campos_parts = []
        for campo in s["campos_ordenados"]:
            items  = s["errores_por_campo"][campo]
            n_err  = len(items)
            muestra = items[:100]
            filas_t = "".join(
                f'<tr><td class="fid">{i["fid"]}</td>'
                f'<td class="val">{_e(i["valor"][:60])}</td>'
                f'<td class="msg">{_e(i["msg"])}</td>'
                f'<td style="white-space:nowrap">{_sev_badge(i["msg"])}</td></tr>'
                for i in muestra
            )
            aviso = (
                f'<p class="truncado">Mostrando 100 de {n_err:,} errores. '
                f'Descarga el CSV para ver todos.</p>'
                if n_err > 100 else ""
            )
            s_err = "es" if n_err != 1 else ""
            _campos_parts.append(
                '<div class="campo-bloque">'
                  f'<button class="campo-toggle" onclick="toggleCampo(this)">'
                    f'<span class="campo-n">{campo}</span>'
                    f'<span class="campo-c">{n_err:,} error{s_err}</span>'
                    '<span class="chev">&#9660;</span>'
                  '</button>'
                  '<div class="campo-det" style="display:none">'
                    f'{aviso}'
                    '<table class="etable">'
                      '<thead><tr><th>FID</th><th>Valor</th><th>Error</th><th>Severidad</th></tr></thead>'
                      f'<tbody>{filas_t}</tbody>'
                    '</table>'
                  '</div>'
                '</div>'
            )
        campos_html = "".join(_campos_parts)

        if not campos_html:
            campos_html = '<p class="sin-err">&#10003; Sin errores en esta capa.</p>'

        btn_csv = (
            f'<a class="btn-csv btn-err" href="{csv_file}" download>'
              '&#11015; Descargar errores CSV'
            '</a>'
            if csv_file else ""
        )

        _detalle_parts.append(
            '<div class="capa-bloque">'
              '<div class="capa-header">'
                f'<div class="capa-toggle" onclick="toggleCapa(this)">'
                  f'<span class="capa-n">{_e(s["nombre"])}</span>'
                  f'<span class="capa-m">{s["n_campos_error"]} campo(s) con errores'
                  f' &middot; {s["con_error"]:,} features</span>'
                  '<span class="chev">&#9660;</span>'
                '</div>'
                f'<div class="capa-acc">{btn_csv}</div>'
              '</div>'
              f'<div class="capa-det" id="capa-{idx}" style="display:none">'
                f'<div class="graf-box"><canvas id="chart-{idx}" height="160"></canvas></div>'
                f'{campos_html}'
              '</div>'
            '</div>'
        )
    detalle = "".join(_detalle_parts)

    # ── Estructura de capas ───────────────────────────────────────────────
    _stats_est = [s for s in stats_capas if s.get("estructura_validada")]
    if _stats_est:
        _COL_PREF_EST = {
            "FALTANTE":    ("#fdecea", "#c0392b"),
            "SOBRANTE":    ("#fff8e1", "#e65100"),
            "TIPO":        ("#fff3e0", "#b45309"),
            "LONGITUD":    ("#fff3e0", "#b45309"),
            "SIN ESQUEMA": ("#fdecea", "#c0392b"),
        }
        _capas_ok_est  = sum(1 for s in _stats_est if not s.get("estructura_errores"))
        _capas_err_est = len(_stats_est) - _capas_ok_est
        _tot_err_est   = sum(len(s.get("estructura_errores") or []) for s in _stats_est)
        _badge_est = (
            '<span class="badge" style="background:#27ae60;margin-left:8px">Sin errores</span>'
            if _capas_err_est == 0 else
            f'<span class="badge" style="background:#e74c3c;margin-left:8px">'
            f'{_capas_err_est} capa(s) &middot; {_tot_err_est} problema(s)</span>'
        )
        _bloques_est = ""
        for s in _stats_est:
            errs = s.get("estructura_errores") or []
            if not errs:
                _bloques_est += (
                    '<div class="capa-bloque">'
                      '<div class="capa-header" style="background:#f0fdf4;">'
                        '<div style="flex:1;padding:14px 18px;display:flex;'
                             'align-items:center;gap:14px;">'
                          f'<span class="capa-n">{_e(s["nombre"])}</span>'
                          '<span style="color:#27ae60;font-weight:600;font-size:13px;">'
                            '&#10003;&nbsp;Estructura correcta'
                          '</span>'
                        '</div>'
                      '</div>'
                    '</div>'
                )
            else:
                _grupos_est = {}
                for msg in errs:
                    _pref = msg[1:msg.index("]")] if msg.startswith("[") and "]" in msg else "OTRO"
                    _grupos_est.setdefault(_pref, []).append(msg)

                _campos_est = ""
                for pref, msgs in _grupos_est.items():
                    bg, fg = _COL_PREF_EST.get(pref, ("#f5f5f5", "#555"))
                    _filas_pref = ""
                    for msg in msgs:
                        txt = msg[msg.index("]") + 2:] if "]" in msg else msg
                        _filas_pref += (
                            f'<tr><td class="msg">{_e(txt)}</td></tr>'
                        )
                    _campos_est += (
                        '<div class="campo-bloque">'
                          f'<button class="campo-toggle" onclick="toggleCampo(this)" '
                          f'style="background:{bg}">'
                            f'<span class="campo-n" style="color:{fg}">{_e(pref)}</span>'
                            f'<span class="campo-c" style="color:{fg}">'
                              f'{len(msgs)} problema{"s" if len(msgs) != 1 else ""}'
                            '</span>'
                            '<span class="chev">&#9660;</span>'
                          '</button>'
                          '<div class="campo-det" style="display:none">'
                            '<table class="etable">'
                              '<thead><tr><th>Detalle</th></tr></thead>'
                              f'<tbody>{_filas_pref}</tbody>'
                            '</table>'
                          '</div>'
                        '</div>'
                    )

                _bloques_est += (
                    '<div class="capa-bloque">'
                      '<div class="capa-header">'
                        f'<div class="capa-toggle" onclick="toggleCapa(this)">'
                          f'<span class="capa-n">{_e(s["nombre"])}</span>'
                          f'<span class="capa-m" style="color:#e74c3c;">'
                            f'{len(errs)} problema{"s" if len(errs) != 1 else ""} de estructura'
                          '</span>'
                          '<span class="chev">&#9660;</span>'
                        '</div>'
                      '</div>'
                      f'<div class="capa-det" style="display:none">'
                        f'{_campos_est}'
                      '</div>'
                    '</div>'
                )
        estructura_sec = (
            '<section class="section">'
              f'<h2 class="sec-title">Validaci&#243;n de Estructura {_badge_est}</h2>'
              f'{_bloques_est}'
            '</section>'
        )
    else:
        estructura_sec = ""

    # ── Topología ─────────────────────────────────────────────────────────
    if topo_resultados:
        n_total_topo = sum(len(tr["errores"]) for tr in topo_resultados)
        badge_topo = (
            f'<span class="badge" style="background:#e74c3c;margin-left:8px">'
            f'{n_total_topo:,} error(es)</span>'
            if n_total_topo else
            '<span class="badge" style="background:#27ae60;margin-left:8px">Sin errores</span>'
        )

        bloques_topo = ""
        for tr in topo_resultados:
            n_err = len(tr["errores"])
            csv_t = archivos_csv_topo.get(tr["nombre_capa"], "")

            if n_err == 0:
                # Capa sin errores → fila verde siempre visible, sin colapsar
                bloques_topo += (
                    '<div class="capa-bloque">'
                      '<div class="capa-header" style="background:#f0fdf4;">'
                        '<div style="flex:1;padding:12px 18px;display:flex;'
                             'align-items:center;gap:14px;">'
                          f'<span class="capa-n">{_e(tr["nombre_capa"])}</span>'
                          '<span style="color:#27ae60;font-weight:600;font-size:13px;">'
                            '&#10003;&nbsp;Sin errores topol&#243;gicos'
                          '</span>'
                        '</div>'
                      '</div>'
                    '</div>'
                )
            else:
                # Capa con errores → bloque colapsable con tabla
                btn_t = (
                    f'<a class="btn-csv btn-err" href="{csv_t}" download>'
                    '&#11015; CSV topolog&#237;a</a>'
                    if csv_t else ""
                )
                reglas_cnt = defaultdict(int)
                for e in tr["errores"]:
                    reglas_cnt[e["regla"]] += 1
                badges_regla = "".join(
                    f'<span class="regla-badge">{r}: {c:,}</span>'
                    for r, c in sorted(reglas_cnt.items(), key=lambda x: -x[1])
                )
                muestra_topo = tr["errores"][:200]
                filas_topo = "".join(
                    f'<tr><td class="fid">{e["fid"]}</td>'
                    f'<td><span class="regla-badge">{e["regla"]}</span></td>'
                    f'<td class="msg">{e["descripcion"]}</td></tr>'
                    for e in muestra_topo
                )
                aviso_topo = (
                    f'<p class="truncado">Mostrando 200 de {n_err:,} errores. '
                    'Descarga el CSV para ver todos.</p>'
                    if n_err > 200 else ""
                )
                id_bloque = f"topo-{tr['nombre_capa'].replace(' ', '-')}"
                bloques_topo += (
                    '<div class="capa-bloque">'
                      '<div class="capa-header">'
                        f'<div class="capa-toggle" onclick="toggleCapa(this)">'
                          f'<span class="capa-n">{_e(tr["nombre_capa"])}</span>'
                          f'<span class="capa-m" style="color:#e74c3c;">'
                            f'{n_err:,} error(es) topol&#243;gico(s)'
                          '</span>'
                          '<span class="chev">&#9660;</span>'
                        '</div>'
                        f'<div class="capa-acc">{badges_regla} {btn_t}</div>'
                      '</div>'
                      f'<div class="capa-det" id="{id_bloque}" style="display:none">'
                        f'{aviso_topo}'
                        '<table class="etable"><thead><tr>'
                        '<th>FID</th><th>Regla</th><th>Descripci&#243;n</th>'
                        f'</tr></thead><tbody>{filas_topo}</tbody></table>'
                      '</div>'
                    '</div>'
                )

        topo_sec = (
            '<section class="section">'
              f'<h2 class="sec-title">Validaci&#243;n Topol&#243;gica {badge_topo}</h2>'
              f'{bloques_topo}'
            '</section>'
        )
    else:
        topo_sec = ""

    # ── Cruce de capas ────────────────────────────────────────────────────
    if inconsistencias_cruce:
        n_inc = len(inconsistencias_cruce)

        huerfanos  = [i for i in inconsistencias_cruce if i["tipo"] == "valor_huerfano"]
        sin_ref    = [i for i in inconsistencias_cruce if i["tipo"] == "sin_capa_referencia"]
        espaciales = [i for i in inconsistencias_cruce if i["tipo"] == "inconsistencia_espacial"]
        sin_pol    = [i for i in inconsistencias_cruce if i["tipo"] == "sin_poligono_contenedor"]
        placa_mav  = [i for i in inconsistencias_cruce
                      if i["tipo"] in ("cruce_placa_mavvial", "id_mavvial_huerfano")]

        # Tabla de valores huérfanos (atributos)
        avisos_sr = "".join(
            f'<div class="aviso-card">&#9888; {_e(i["mensaje"])}</div>'
            for i in sin_ref
        )
        filas_h = "".join(
            f'<tr><td>{_e(i["capa_origen"])}</td><td>{_e(i.get("tipo_geom","&#8212;"))}</td>'
            f'<td>{_e(i["campo"])}</td><td class="val">{_e(i["valor"])}</td>'
            f'<td>{i.get("n_features",0):,}</td>'
            f'<td>{_e(", ".join(i.get("capas_referencia") or []) or "&#8212;")}</td>'
            f'<td class="msg">{_e(i["mensaje"])}</td></tr>'
            for i in huerfanos[:300]
        )
        aviso_trunc_h = (
            f'<p class="truncado">Mostrando 300 de {len(huerfanos):,}.</p>'
            if len(huerfanos) > 300 else ""
        )
        bloque_huerfanos = ""
        if huerfanos or sin_ref:
            tabla_h = (
                '<table class="etable"><thead><tr>'
                '<th>Capa</th><th>Tipo</th><th>Campo</th><th>Valor</th>'
                '<th>Features</th><th>Ref. pol&#237;gonos</th><th>Detalle</th>'
                '</tr></thead>'
                f'<tbody>{filas_h}</tbody></table>'
            ) if huerfanos else ""
            bloque_huerfanos = (
                '<h3 style="font-size:14px;font-weight:700;margin:16px 0 8px;color:#2c3e50">'
                  'C&#243;digos sin referencia en pol&#237;gonos</h3>'
                f'{avisos_sr}{aviso_trunc_h}{tabla_h}'
            )

        def _filas_espacial(inc_list, con_esperado, csvs):
            """Una fila resumen + fila de detalle expandible + botón CSV por grupo."""
            filas = ""
            for i in inc_list:
                items     = i.get("items", [])
                n         = i.get("n_features", 0)
                pol       = ", ".join(i.get("capas_referencia") or []) or "&#8212;"
                fids_prev = ", ".join(str(it[0]) for it in items[:10])
                if n > 10:
                    fids_prev += f" &#8230; (+{n - 10} m&#225;s)"

                # Botón CSV
                csv_file = csvs.get(i["capa_origen"], "")
                btn_csv  = (
                    f'<a class="btn-csv btn-err" href="{csv_file}" download '
                    f'onclick="event.stopPropagation()">&#11015; CSV</a>'
                    if csv_file else ""
                )

                aviso_det = (
                    f'<p class="truncado">Mostrando todos los {n:,} features en el CSV.</p>'
                    if n > 0 else ""
                )
                if con_esperado:
                    det_filas = "".join(
                        f'<tr><td class="fid">{it[0]}</td>'
                        f'<td class="val">{it[1]}</td>'
                        f'<td class="val" style="color:#27ae60">{it[2]}</td></tr>'
                        for it in items[:200]
                    )
                    trunc_det = (
                        f'<p class="truncado">Mostrando 200 de {n:,}. Descarga el CSV para todos.</p>'
                        if n > 200 else ""
                    )
                    det_tabla = (
                        f'{trunc_det}'
                        '<table class="etable" style="margin:8px 0 4px">'
                        '<thead><tr><th>FID</th><th>Valor actual</th>'
                        '<th style="color:#27ae60">Valor esperado</th></tr></thead>'
                        f'<tbody>{det_filas}</tbody></table>'
                    )
                else:
                    det_filas = "".join(
                        f'<tr><td class="fid">{it[0]}</td>'
                        f'<td class="val">{it[1]}</td></tr>'
                        for it in items[:200]
                    )
                    trunc_det = (
                        f'<p class="truncado">Mostrando 200 de {n:,}. Descarga el CSV para todos.</p>'
                        if n > 200 else ""
                    )
                    det_tabla = (
                        f'{trunc_det}'
                        '<table class="etable" style="margin:8px 0 4px">'
                        '<thead><tr><th>FID</th><th>Valor</th></tr></thead>'
                        f'<tbody>{det_filas}</tbody></table>'
                    )

                filas += (
                    f'<tr style="cursor:pointer" onclick="toggleEsp(this)">'
                    f'<td style="font-weight:600">{_e(i["capa_origen"])}</td>'
                    f'<td>{i.get("tipo_geom","&#8212;")}</td>'
                    f'<td style="font-family:monospace;color:#2980b9">{_e(i["campo"])}</td>'
                    f'<td>{pol}</td>'
                    f'<td style="font-weight:700;color:#e74c3c;text-align:center">{n:,}</td>'
                    f'<td style="font-size:11px;color:#888;font-family:monospace">{fids_prev}</td>'
                    f'<td style="text-align:center">{btn_csv}</td>'
                    f'<td style="font-size:11px;color:#aaa;text-align:center">&#9660; detalle</td>'
                    f'</tr>'
                    f'<tr class="esp-det-row" style="display:none">'
                    f'<td colspan="8" style="padding:10px 24px;background:#f8f9fa">'
                      f'{det_tabla}</td></tr>'
                )
            return filas

        bloque_espacial = ""
        if espaciales:
            bloque_espacial += (
                '<h3 style="font-size:14px;font-weight:700;margin:16px 0 6px;color:#2c3e50">'
                  'C&#243;digos no coinciden con el pol&#237;gono contenedor</h3>'
                '<p style="font-size:12px;color:#7f8c8d;margin-bottom:10px">'
                  'Haz clic en una fila para ver los FIDs. '
                  '<em>Valor actual</em> = lo que dice el feature; '
                  '<em style="color:#27ae60">Valor esperado</em> = lo que dice el pol&#237;gono. '
                  'Descarga el CSV para la lista completa.</p>'
                '<table class="etable"><thead><tr>'
                '<th>Capa</th><th>Tipo</th><th>Campo</th><th>Pol&#237;gono ref.</th>'
                '<th style="text-align:center">Features</th>'
                '<th>Muestra de FIDs</th><th>CSV</th><th></th>'
                '</tr></thead>'
                f'<tbody>{_filas_espacial(espaciales, True, archivos_csv_cruce_esp)}</tbody></table>'
            )
        if sin_pol:
            bloque_espacial += (
                '<h3 style="font-size:14px;font-weight:700;margin:16px 0 6px;color:#2c3e50">'
                  'Features fuera de todos los pol&#237;gonos</h3>'
                '<table class="etable"><thead><tr>'
                '<th>Capa</th><th>Tipo</th><th>Campo</th><th>Pol&#237;gono ref.</th>'
                '<th style="text-align:center">Features</th>'
                '<th>Muestra de FIDs</th><th>CSV</th><th></th>'
                '</tr></thead>'
                f'<tbody>{_filas_espacial(sin_pol, False, archivos_csv_cruce_esp)}</tbody></table>'
            )

        bloque_placa_mav = ""
        if placa_mav:
            bloque_placa_mav = (
                '<h3 style="font-size:14px;font-weight:700;margin:16px 0 6px;color:#2c3e50">'
                  'Cruce placa &#8596; mavvial</h3>'
                '<p style="font-size:12px;color:#7f8c8d;margin-bottom:10px">'
                  'Haz clic en una fila para ver los FIDs. '
                  '<em>Valor actual</em> = campo en placa; '
                  '<em style="color:#27ae60">Valor esperado</em> = campo en mavvial. '
                  'Descarga el CSV para la lista completa.</p>'
                '<table class="etable"><thead><tr>'
                '<th>Capa</th><th>Tipo</th><th>Campo</th><th>Ref. mavvial</th>'
                '<th style="text-align:center">Features</th>'
                '<th>Muestra de FIDs</th><th>CSV</th><th></th>'
                '</tr></thead>'
                f'<tbody>{_filas_espacial(placa_mav, True, archivos_csv_cruce_esp)}</tbody></table>'
            )

        cruce_sec = (
            '<section class="section">'
              '<h2 class="sec-title">Validaci&#243;n cruzada y espacial '
                f'<span class="badge" style="background:#e74c3c;margin-left:8px">'
                  f'{n_inc} inconsistencia(s)</span></h2>'
              f'{bloque_huerfanos}{bloque_espacial}{bloque_placa_mav}'
            '</section>'
        )
    else:
        cruce_sec = (
            '<section class="section">'
              '<h2 class="sec-title">Validaci&#243;n cruzada y espacial</h2>'
              '<p class="sin-err">&#10003; Todos los geo-c&#243;digos son consistentes '
              'y los features est&#225;n dentro de los pol&#237;gonos correctos.</p>'
            '</section>'
        )

    # ── JS (raw string, sin f-string) ─────────────────────────────────────
    js_code = r"""
function toggleCapa(el) {
  var bloque = el.parentElement.parentElement;
  var det    = bloque.querySelector('.capa-det');
  var chev   = el.querySelector('.chev');
  var open   = det.style.display !== 'none';
  det.style.display = open ? 'none' : 'block';
  chev.classList.toggle('open', !open);
  if (!open) initCharts();
}
function toggleCampo(btn) {
  var det  = btn.nextElementSibling;
  var chev = btn.querySelector('.chev');
  var open = det.style.display !== 'none';
  det.style.display = open ? 'none' : 'block';
  chev.classList.toggle('open', !open);
}
function toggleEsp(row) {
  var det = row.nextElementSibling;
  if (!det || !det.classList.contains('esp-det-row')) return;
  var open = det.style.display !== 'none';
  det.style.display = open ? 'none' : 'table-row';
  var last = row.cells[row.cells.length - 1];
  if (last) last.innerHTML = open ? '&#9660; ver detalle' : '&#9650; ocultar';
}
var chartsInit = false;
function initCharts() {
  if (chartsInit) return;
  chartsInit = true;
  GRAFICAS_DATA.forEach(function(g) {
    var el = document.getElementById(g.id);
    if (!el || !g.labels.length) return;
    new Chart(el, {
      type: 'bar',
      data: {
        labels: g.labels,
        datasets: [{
          label: 'Errores',
          data: g.data,
          backgroundColor: 'rgba(231,76,60,0.6)',
          borderColor: '#e74c3c',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true, ticks: { precision: 0 } } }
      }
    });
  });
}
"""

    # ── HTML final ────────────────────────────────────────────────────────
    html = (
        '<!DOCTYPE html>\n<html lang="es">\n<head>\n'
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        f'<title>Reporte de Validaci&#243;n &#8212; {_e(pais)}</title>\n'
        '<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>\n'
        '<style>\n'
        '* { box-sizing: border-box; margin: 0; padding: 0; }\n'
        'body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;\n'
        '       background: #f0f2f5; color: #2c3e50; font-size: 14px; }\n'
        '.header { background: linear-gradient(135deg, #1a252f 0%, #2c3e50 100%);\n'
        '          color: white; padding: 28px 40px; }\n'
        '.header h1 { font-size: 24px; font-weight: 700; margin-bottom: 6px; }\n'
        '.header-meta { opacity: .75; font-size: 13px; display: flex; gap: 20px; flex-wrap: wrap; }\n'
        '.global-kpi { background: white; border-bottom: 1px solid #e0e0e0;\n'
        '              padding: 16px 40px; display: flex; gap: 36px; flex-wrap: wrap; }\n'
        '.kpi { text-align: center; }\n'
        '.kpi-num { font-size: 26px; font-weight: 700; display: block; }\n'
        '.kpi-label { font-size: 11px; text-transform: uppercase; letter-spacing: .5px; color: #7f8c8d; }\n'
        '.kpi.ok .kpi-num { color: #27ae60; }\n'
        '.kpi.err .kpi-num { color: #e74c3c; }\n'
        '.main { max-width: 1100px; margin: 0 auto; padding: 28px 20px; }\n'
        '.section { margin-bottom: 32px; }\n'
        '.sec-title { font-size: 17px; font-weight: 700; margin-bottom: 14px;\n'
        '             padding-bottom: 8px; border-bottom: 2px solid #e0e0e0;\n'
        '             display: flex; align-items: center; flex-wrap: wrap; gap: 8px; }\n'
        '.cards-grid { display: grid; grid-template-columns: repeat(auto-fill,minmax(260px,1fr)); gap: 14px; }\n'
        '.card { background: white; border-radius: 10px; padding: 18px;\n'
        '        box-shadow: 0 2px 8px rgba(0,0,0,.07); }\n'
        '.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }\n'
        '.card-title { font-weight: 700; font-size: 14px; flex: 1; margin-right: 8px;\n'
        '              white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }\n'
        '.badge { display: inline-block; color: white; font-size: 11px; font-weight: 700;\n'
        '         padding: 2px 8px; border-radius: 20px; white-space: nowrap; }\n'
        '.qbar-bg { background: #ecf0f1; border-radius: 4px; height: 7px; margin-bottom: 12px; overflow: hidden; }\n'
        '.qbar-fill { height: 100%; border-radius: 4px; }\n'
        '.card-stats { display: flex; justify-content: space-between; }\n'
        '.stat { text-align: center; flex: 1; }\n'
        '.stat-n { display: block; font-size: 18px; font-weight: 700; }\n'
        '.stat-l { font-size: 11px; color: #7f8c8d; }\n'
        '.stat.ok .stat-n { color: #27ae60; }\n'
        '.stat.err .stat-n { color: #e74c3c; }\n'
        '.capa-bloque { background: white; border-radius: 10px; margin-bottom: 10px;\n'
        '               box-shadow: 0 2px 8px rgba(0,0,0,.07); overflow: hidden; }\n'
        '.capa-header { display: flex; align-items: stretch; border-bottom: 1px solid #f5f5f5; }\n'
        '.capa-toggle { flex: 1; cursor: pointer; padding: 14px 18px;\n'
        '               display: flex; align-items: center; gap: 10px; font-size: 14px; user-select: none; }\n'
        '.capa-toggle:hover { background: #f8f9fa; }\n'
        '.capa-n { font-weight: 700; font-size: 14px; flex: 1; }\n'
        '.capa-m { color: #7f8c8d; font-size: 13px; }\n'
        '.capa-acc { display: flex; align-items: center; padding: 0 14px; gap: 6px; }\n'
        '.btn-csv { padding: 5px 11px; border-radius: 5px; font-size: 12px;\n'
        '           font-weight: 600; cursor: pointer; white-space: nowrap;\n'
        '           text-decoration: none; display: inline-block; }\n'
        '.btn-err { background: #fdecea; color: #c0392b; border: 1px solid #f5c6cb; }\n'
        '.btn-err:hover { opacity: .82; }\n'
        '.capa-det { padding: 0 18px 18px; }\n'
        '.graf-box { margin-bottom: 16px; max-height: 200px; }\n'
        '.campo-bloque { margin-bottom: 6px; border: 1px solid #e8e8e8; border-radius: 6px; overflow: hidden; }\n'
        '.campo-toggle { width: 100%; background: #fafafa; border: none; cursor: pointer;\n'
        '                padding: 9px 12px; display: flex; align-items: center;\n'
        '                gap: 8px; font-size: 13px; font-family: inherit; }\n'
        '.campo-toggle:hover { background: #f0f0f0; }\n'
        '.campo-n { font-weight: 600; flex: 1; text-align: left; }\n'
        '.campo-c { color: #e74c3c; font-weight: 600; font-size: 12px; }\n'
        '.campo-det { padding: 0 12px 12px; }\n'
        '.chev { font-size: 10px; color: #aaa; transition: transform .2s; }\n'
        '.chev.open { transform: rotate(180deg); }\n'
        '.etable { width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 6px; }\n'
        '.etable th { background: #2c3e50; color: white; padding: 7px 10px; text-align: left; font-weight: 600; }\n'
        '.etable td { padding: 5px 10px; border-bottom: 1px solid #f0f0f0; vertical-align: top; }\n'
        '.etable tr:hover td { background: #fef9f0; }\n'
        '.etable td.fid { color: #999; font-size: 12px; white-space: nowrap; }\n'
        '.etable td.val { font-family: monospace; color: #2980b9; max-width: 160px;\n'
        '                  overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }\n'
        '.etable td.msg { color: #c0392b; }\n'
        '.sin-err { color: #27ae60; font-weight: 600; padding: 14px 0; }\n'
        '.truncado { color: #e67e22; font-size: 12px; margin-bottom: 6px;\n'
        '            padding: 6px 10px; background: #fff3cd; border-radius: 4px; }\n'
        '.aviso-card { background: #fff3cd; border-left: 4px solid #f39c12;\n'
        '              padding: 10px 14px; border-radius: 4px; margin-bottom: 8px; font-size: 13px; }\n'
        '.topo-ok { color: #27ae60; font-weight: 600; padding: 10px 0; }\n'
        '.regla-badge { display: inline-block; color: white; font-size: 11px; font-weight: 700;\n'
        '               padding: 2px 8px; border-radius: 20px; margin-right: 4px;\n'
        '               white-space: nowrap; background: #e74c3c; }\n'
        '.footer { text-align: center; color: #aaa; font-size: 12px;\n'
        '          padding: 28px; border-top: 1px solid #e0e0e0; margin-top: 12px; }\n'
        '</style>\n</head>\n<body>\n'

        + (_html_bloque_entrega(bloque_entrega) if bloque_entrega else '')

        + '<div class="header">\n'
        '  <h1>Reporte de Validaci&#243;n de Capas</h1>\n'
        + (f'  <div style="color:#94a3b8;font-size:13px;margin-bottom:4px">&#128204; {_e(tarea)}</div>\n' if tarea else '') +
        '  <div class="header-meta">\n'
        f'    <span>&#127758; Pa&#237;s: <strong>{_e(pais)}</strong></span>\n'
        f'    <span>&#128197; {fecha_hora}</span>\n'
        f'    <span>&#9201; {tiempo_total_s:.1f}s</span>\n'
        f'    <span>&#128194; {len(stats_capas)} capa(s)</span>\n'
        '  </div>\n'
        '</div>\n'

        '<div class="global-kpi">\n'
        f'  <div class="kpi"><span class="kpi-num">{total_feat:,}</span>'
            '<span class="kpi-label">Features totales</span></div>\n'
        f'  <div class="kpi ok"><span class="kpi-num">{total_feat - total_err:,}</span>'
            '<span class="kpi-label">Sin errores</span></div>\n'
        f'  <div class="kpi err"><span class="kpi-num">{total_err:,}</span>'
            '<span class="kpi-label">Con errores</span></div>\n'
        f'  <div class="kpi"><span class="kpi-num" style="color:{col_global}">{pct_global}%</span>'
            '<span class="kpi-label">Calidad global</span></div>\n'
        f'  <div class="kpi"><span class="kpi-num">{len(inconsistencias_cruce)}</span>'
            '<span class="kpi-label">Inconsist. cruce</span></div>\n'
        '</div>\n'

        '<div class="main">\n'
        '  <section class="section">\n'
        '    <h2 class="sec-title">Resumen por capa</h2>\n'
        f'    <div class="cards-grid">{tarjetas}</div>\n'
        '  </section>\n'
        '  <section class="section">\n'
        '    <h2 class="sec-title">Detalle de errores por capa</h2>\n'
        f'    {detalle}\n'
        '  </section>\n'
        f'  {estructura_sec}\n'
        f'  {topo_sec}\n'
        f'  {cruce_sec}\n'
        + _comentario_sec(bloque_entrega) +
        '</div>\n'
        f'<div class="footer">Generado por utils_qgis &middot; {fecha_hora}</div>\n'

        '<script>\n'
        f'var GRAFICAS_DATA = {graficas_json};\n'
        '</script>\n'
        '<script>\n'
        + js_code +
        '</script>\n'
        '</body>\n</html>\n'
    )

    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write(html)

    # Combinar CSVs de atributos y topología en un solo dict
    todos_csv = {
        **archivos_csv,
        **{f"{k}_topologia":     v for k, v in archivos_csv_topo.items()},
        **{f"{k}_cruce_espacial": v for k, v in archivos_csv_cruce_esp.items()},
    }
    return ruta_salida, todos_csv, csv_resumen

