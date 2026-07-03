"""
reporte_resumido.py
-------------------
Genera el reporte HTML agrupado + CSVs resumidos para validación INTERNA.

Diferencia clave vs reporte_html.py:
  - Atributos: agrupados por campo → tipo_error → cantidad (sin listar features)
  - Topología: sí muestra FID + tipo + descripción (necesario para localizar)
  - Geocódigos: mismo comportamiento que el reporte detallado
  - HTML diseño oscuro, limpio, orientado a corrección rápida
"""

import csv
import os
from collections import defaultdict
from datetime import datetime

from .clasificador_errores import (
    agrupar_por_tipo, extraer_hints_por_tipo,
    severidad, color_severidad,
    ORDEN_SEVERIDAD,
)


# ── Punto de entrada principal ────────────────────────────────────────────────

def generar(stats_capas, topo_resultados, inconsistencias,
            pais, tiempo_s, tarea, ruta_salida):
    """
    Genera HTML resumido + CSVs agrupados para validación interna.

    Returns:
        (ruta_html, archivos_csv_dict, csv_resumen_nombre)
        archivos_csv_dict: {clave: nombre_archivo}
    """
    carpeta = os.path.dirname(ruta_salida)
    os.makedirs(carpeta, exist_ok=True)

    archivos = {}

    csv_attr = _csv_atributos_agrupados(stats_capas, carpeta)
    if csv_attr:
        archivos["atributos_agrupados"] = csv_attr

    csv_topo = _csv_topologia(topo_resultados, carpeta)
    if csv_topo:
        archivos["topologia"] = csv_topo

    csv_geo = _csv_geocodigos(inconsistencias, carpeta)
    if csv_geo:
        archivos["geocodigos"] = csv_geo

    html = _html(stats_capas, topo_resultados, inconsistencias,
                 pais, tiempo_s, tarea, archivos)
    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write(html)

    return ruta_salida, archivos, csv_attr or ""


# ── Generadores de CSV ─────────────────────────────────────────────────────────

def _csv_atributos_agrupados(stats_capas, carpeta):
    nombre = "atributos_agrupados.csv"
    ruta   = os.path.join(carpeta, nombre)
    filas  = 0
    with open(ruta, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["capa", "campo", "tipo_error", "cantidad", "severidad"])
        for s in stats_capas:
            agrupado = agrupar_por_tipo(s.get("errores_por_campo", {}))
            for campo, tipos in agrupado.items():
                for tipo, n in tipos.items():
                    w.writerow([s["nombre"], campo, tipo, n, severidad(tipo)])
                    filas += 1
    return nombre if filas else None


def _csv_topologia(topo_resultados, carpeta):
    if not topo_resultados:
        return None
    nombre = "topologia_detalle.csv"
    ruta   = os.path.join(carpeta, nombre)
    filas  = 0
    with open(ruta, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["capa", "fid", "tipo_error", "descripcion"])
        for tr in topo_resultados:
            for err in tr["errores"]:
                w.writerow([tr["nombre_capa"], err["fid"],
                             err["regla"], err.get("descripcion", "")])
                filas += 1
    return nombre if filas else None


def _csv_geocodigos(inconsistencias, carpeta):
    if not inconsistencias:
        return None
    nombre = "geocodigos_resumen.csv"
    ruta   = os.path.join(carpeta, nombre)
    with open(ruta, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["capa", "tipo_geom", "campo",
                    "tipo_inconsistencia", "n_features", "capas_referencia"])
        for i in inconsistencias:
            w.writerow([
                i["capa_origen"], i.get("tipo_geom", ""), i["campo"],
                i.get("tipo", ""), i.get("n_features", 0),
                ", ".join(i.get("capas_referencia") or []),
            ])
    return nombre


# ── Generador HTML ─────────────────────────────────────────────────────────────

_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
       background: #0f172a; color: #e2e8f0; font-size: 14px; line-height: 1.5; }
.header { background: linear-gradient(135deg, #1e293b, #0f172a);
          padding: 26px 40px; border-bottom: 1px solid #1e293b; }
.header h1 { font-size: 21px; font-weight: 700; color: #f1f5f9; margin-bottom: 5px; }
.header-meta { color: #64748b; font-size: 13px; display: flex; gap: 18px;
               flex-wrap: wrap; margin-top: 6px; }
.badge { padding: 2px 10px; border-radius: 20px; font-size: 11px;
         font-weight: 700; display: inline-block; }
.badge-interno { background: #1d4ed8; color: #bfdbfe; }
.kpis { display: flex; background: #1e293b; border-bottom: 1px solid #334155; }
.kpi { flex: 1; padding: 16px 20px; border-right: 1px solid #334155; text-align: center; }
.kpi:last-child { border-right: none; }
.kpi-n { font-size: 26px; font-weight: 800; display: block; }
.kpi-l { font-size: 11px; color: #64748b; text-transform: uppercase; letter-spacing: .5px; }
.main { max-width: 1080px; margin: 0 auto; padding: 28px 20px; }
.section { margin-bottom: 30px; }
.sec-title { font-size: 15px; font-weight: 700; color: #f1f5f9; margin-bottom: 12px;
             padding-bottom: 8px; border-bottom: 1px solid #1e293b;
             display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.capa-card { background: #1e293b; border-radius: 10px; border: 1px solid #334155;
             margin-bottom: 10px; overflow: hidden; }
.capa-head { padding: 13px 18px; display: flex; align-items: center; gap: 12px;
             cursor: pointer; user-select: none; }
.capa-head:hover { background: #253347; }
.chev { font-size: 10px; color: #64748b; transition: transform .18s; flex-shrink: 0; }
.chev.open { transform: rotate(90deg); }
.capa-name { font-weight: 700; font-size: 14px; flex: 1; color: #f1f5f9; }
.capa-body { padding: 0 18px 14px; display: none; }
.campo-bloque { background: #0f172a; border-radius: 8px; padding: 11px 14px;
                margin-bottom: 8px; border: 1px solid #1e293b; }
.campo-name { font-size: 13px; font-weight: 600; color: #93c5fd; margin-bottom: 8px;
              display: flex; align-items: center; gap: 8px; }
.error-row { display: flex; align-items: center; gap: 8px; padding: 5px 0;
             border-bottom: 1px solid #1a2537; }
.error-row:last-child { border-bottom: none; }
.error-tipo { flex: 1; font-size: 13px; color: #cbd5e1; }
.error-n { font-size: 14px; font-weight: 700; color: #f87171; min-width: 70px;
           text-align: right; }
.sev-badge { padding: 1px 8px; border-radius: 10px; font-size: 10px;
             font-weight: 700; white-space: nowrap; }
.topo-item { padding: 9px 14px; background: #0f172a; border-radius: 7px;
             margin-bottom: 6px; border-left: 3px solid #f87171; }
.topo-fid { color: #93c5fd; font-weight: 600; font-size: 13px; }
.topo-tipo { color: #fca5a5; margin-left: 8px; font-size: 13px; }
.topo-desc { color: #94a3b8; font-size: 12px; margin-top: 3px; }
.est-item { padding: 8px 14px; background: #0f172a; border-radius: 7px;
            margin-bottom: 5px; display: flex; align-items: flex-start; gap: 10px; }
.est-badge { padding: 1px 8px; border-radius: 10px; font-size: 10px;
             font-weight: 700; white-space: nowrap; flex-shrink: 0; margin-top: 2px; }
.est-msg { color: #cbd5e1; font-size: 13px; }
.geo-item { padding: 9px 14px; background: #0f172a; border-radius: 7px;
            margin-bottom: 6px; border-left: 3px solid #fbbf24; }
.ok-msg { color: #34d399; font-size: 13px; padding: 8px 0; }
.hint { color: #475569; font-size: 11px; margin-top: 8px; }
.footer { text-align: center; color: #334155; font-size: 12px;
          padding: 20px; border-top: 1px solid #1e293b; margin-top: 8px; }
"""

_JS = """
document.querySelectorAll('.capa-head').forEach(h => {
  h.addEventListener('click', () => {
    const body = h.nextElementSibling;
    const chev = h.querySelector('.chev');
    if (!body || !body.classList.contains('capa-body')) return;
    const open = body.style.display === 'block';
    body.style.display = open ? 'none' : 'block';
    if (chev) chev.classList.toggle('open', !open);
  });
});
"""


def _html(stats_capas, topo_resultados, inconsistencias,
          pais, tiempo_s, tarea, archivos):
    fecha      = datetime.now().strftime("%d/%m/%Y %H:%M")
    total_feat = sum(s["total"]     for s in stats_capas)
    total_err  = sum(s["con_error"] for s in stats_capas)
    pct_g      = round((total_feat - total_err) * 100 / total_feat, 1) if total_feat else 0

    def col(p): return "#34d399" if p >= 90 else "#fbbf24" if p >= 70 else "#f87171"

    tarea_html = (f'<span style="color:#94a3b8;font-size:13px">📌 {tarea}</span>'
                  if tarea else "")

    sec_est  = _sec_estructura(stats_capas)
    sec_attr = _sec_atributos(stats_capas, col, archivos)
    sec_topo = _sec_topologia(topo_resultados, archivos)
    sec_geo  = _sec_geocodigos(inconsistencias, archivos)

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Validación Interna — {pais}</title>
<style>{_CSS}</style>
</head>
<body>

<div class="header">
  <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">
    <span class="badge badge-interno">VALIDACIÓN INTERNA</span>
    <h1>Reporte de Validación — {pais}</h1>
  </div>
  {tarea_html}
  <div class="header-meta">
    <span>📅 {fecha}</span>
    <span>⏱ {tiempo_s:.1f}s</span>
    <span>🗂 {len(stats_capas)} capa(s)</span>
    <span style="color:{col(pct_g)};font-weight:700">{pct_g}% calidad global</span>
  </div>
</div>

<div class="kpis">
  <div class="kpi">
    <span class="kpi-n">{total_feat:,}</span>
    <span class="kpi-l">Features totales</span>
  </div>
  <div class="kpi">
    <span class="kpi-n" style="color:#34d399">{total_feat - total_err:,}</span>
    <span class="kpi-l">Sin errores</span>
  </div>
  <div class="kpi">
    <span class="kpi-n" style="color:#f87171">{total_err:,}</span>
    <span class="kpi-l">Con errores</span>
  </div>
  <div class="kpi">
    <span class="kpi-n" style="color:{col(pct_g)}">{pct_g}%</span>
    <span class="kpi-l">Calidad global</span>
  </div>
</div>

<div class="main">
  {sec_est}
  {sec_attr}
  {sec_topo}
  {sec_geo}
</div>

<div class="footer">
  Reporte interno — Validaciones CartoLatam · {fecha}<br>
  <small>Este reporte es para uso interno del país. No es el reporte oficial de entrega.</small>
</div>

<script>{_JS}</script>
</body>
</html>"""


def _sec_estructura(stats_capas):
    _stats_est = [s for s in stats_capas if s.get("estructura_validada")]
    if not _stats_est:
        return ""

    _COL = {
        "FALTANTE":    ("#7f1d1d", "#fca5a5"),
        "SOBRANTE":    ("#78350f", "#fcd34d"),
        "TIPO":        ("#7c2d12", "#fdba74"),
        "LONGITUD":    ("#7c2d12", "#fdba74"),
        "SIN ESQUEMA": ("#7f1d1d", "#fca5a5"),
    }
    _capas_err = sum(1 for s in _stats_est if s.get("estructura_errores"))
    _tot_prob  = sum(len(s.get("estructura_errores") or []) for s in _stats_est)

    bloques = ""
    for s in _stats_est:
        errs = s.get("estructura_errores") or []
        if not errs:
            bloques += (
                f'<div class="capa-card"><div class="capa-head">'
                f'<span class="capa-name">{s["nombre"]}</span>'
                f'<span class="ok-msg">✓ Estructura correcta</span>'
                f'</div></div>'
            )
            continue

        items_html = ""
        _grupos = {}
        for msg in errs:
            _pref = msg[1:msg.index("]")] if msg.startswith("[") and "]" in msg else "OTRO"
            _grupos.setdefault(_pref, []).append(msg)

        for pref, msgs in _grupos.items():
            bg, fg = _COL.get(pref, ("#1e293b", "#94a3b8"))
            for msg in msgs:
                txt = msg[msg.index("]") + 2:] if "]" in msg else msg
                items_html += (
                    f'<div class="est-item">'
                    f'<span class="est-badge" style="background:{bg};color:{fg}">{pref}</span>'
                    f'<span class="est-msg">{txt}</span>'
                    f'</div>'
                )

        bloques += (
            f'<div class="capa-card">'
            f'<div class="capa-head">'
            f'<span class="chev">▶</span>'
            f'<span class="capa-name">{s["nombre"]}</span>'
            f'<span style="color:#f87171;font-size:13px">'
            f'{len(errs)} problema{"s" if len(errs) != 1 else ""}</span>'
            f'</div>'
            f'<div class="capa-body">{items_html}</div>'
            f'</div>'
        )

    _badge_color = "#34d399" if _capas_err == 0 else "#f87171"
    _badge_txt   = ("Sin errores" if _capas_err == 0
                    else f"{_capas_err} capa(s) · {_tot_prob} problema(s)")
    return (
        f'<div class="section">'
        f'<div class="sec-title">⊞ Estructura'
        f'<span style="color:{_badge_color};font-size:13px">{_badge_txt}</span>'
        f'</div>{bloques}</div>'
    )


def _sec_atributos(stats_capas, col_fn, archivos):
    if not stats_capas:
        return ""
    total_err_all = sum(s["con_error"] for s in stats_capas)
    csv_link = ""
    if archivos.get("atributos_agrupados"):
        csv_link = (f'<a href="{archivos["atributos_agrupados"]}" download '
                    f'style="background:#1d4ed8;color:#bfdbfe;padding:2px 10px;'
                    f'border-radius:5px;font-size:11px;text-decoration:none">↓ CSV</a>')

    bloques = ""
    for s in stats_capas:
        if not s.get("campos_ordenados"):
            bloques += (f'<div class="capa-card"><div class="capa-head">'
                        f'<span class="capa-name">{s["nombre"]}</span>'
                        f'<span class="ok-msg">✓ Sin errores de atributos</span>'
                        f'</div></div>')
            continue

        errores_campo = s.get("errores_por_campo", {})
        agrupado      = agrupar_por_tipo(errores_campo)
        hints         = extraer_hints_por_tipo(errores_campo)
        col           = col_fn(s["pct_calidad"])

        campos_html = ""
        for campo in s["campos_ordenados"]:
            tipos   = agrupado.get(campo, {})
            hints_c = hints.get(campo, {})
            total_c = sum(tipos.values())
            filas   = ""
            for tipo, n in tipos.items():
                sev      = severidad(tipo)
                bg, fg   = color_severidad(sev)
                hint     = hints_c.get(tipo, "")
                hint_html = (
                    f'<div style="color:#52525b;font-size:10px;margin-top:2px;'
                    f'padding-left:2px;font-style:italic">{hint}</div>'
                    if hint else ""
                )
                filas += (f'<div class="error-row" style="flex-direction:column;'
                          f'align-items:flex-start;padding:6px 0;">'
                          f'<div style="display:flex;align-items:center;gap:8px;width:100%">'
                          f'<span class="error-tipo" style="flex:1">{tipo}</span>'
                          f'<span class="sev-badge" style="background:{bg};color:{fg}">{sev}</span>'
                          f'<span class="error-n">{n:,}</span>'
                          f'</div>'
                          f'{hint_html}'
                          f'</div>')
            campos_html += (f'<div class="campo-bloque">'
                            f'<div class="campo-name">{campo}'
                            f'<span style="color:#475569;font-size:11px">{total_c:,} errores</span>'
                            f'</div>{filas}</div>')

        bloques += (f'<div class="capa-card">'
                    f'<div class="capa-head">'
                    f'<span class="chev">▶</span>'
                    f'<span class="capa-name">{s["nombre"]}</span>'
                    f'<span style="color:{col};font-weight:700">{s["pct_calidad"]}%</span>'
                    f'<span style="color:#f87171;font-size:13px">{s["con_error"]:,} feat. con errores</span>'
                    f'</div>'
                    f'<div class="capa-body">{campos_html}'
                    f'<p class="hint">ℹ Descarga el CSV para ver los FIDs individuales.</p>'
                    f'</div></div>')

    return (f'<div class="section">'
            f'<div class="sec-title">✦ Atributos'
            f'<span style="color:#f87171;font-size:13px">{total_err_all:,} features con errores</span>'
            f'{csv_link}</div>{bloques}</div>')


def _sec_topologia(topo_resultados, archivos):
    if not topo_resultados:
        return ""
    n_total = sum(len(tr["errores"]) for tr in topo_resultados)
    csv_link = ""
    if archivos.get("topologia"):
        csv_link = (f'<a href="{archivos["topologia"]}" download '
                    f'style="background:#1d4ed8;color:#bfdbfe;padding:2px 10px;'
                    f'border-radius:5px;font-size:11px;text-decoration:none">↓ CSV</a>')

    bloques = ""
    for tr in topo_resultados:
        n_err = len(tr["errores"])
        if n_err == 0:
            bloques += (f'<div class="capa-card"><div class="capa-head">'
                        f'<span class="capa-name">{tr["nombre_capa"]}</span>'
                        f'<span class="ok-msg">✓ Sin errores topológicos</span>'
                        f'</div></div>')
            continue

        items_html = ""
        for err in tr["errores"]:
            desc = err.get("descripcion", "")
            items_html += (f'<div class="topo-item">'
                           f'<span class="topo-fid">FID {err["fid"]}</span>'
                           f'<span class="topo-tipo">{err["regla"]}</span>'
                           f'<div class="topo-desc">{desc}</div>'
                           f'</div>')

        bloques += (f'<div class="capa-card">'
                    f'<div class="capa-head">'
                    f'<span class="chev">▶</span>'
                    f'<span class="capa-name">{tr["nombre_capa"]}</span>'
                    f'<span style="color:#f87171;font-size:13px">'
                    f'{n_err:,} error{"es" if n_err != 1 else ""}</span>'
                    f'</div>'
                    f'<div class="capa-body">{items_html}</div>'
                    f'</div>')

    return (f'<div class="section">'
            f'<div class="sec-title">◈ Topología'
            f'<span style="color:#f87171;font-size:13px">{n_total:,} errores</span>'
            f'{csv_link}</div>{bloques}</div>')


def _sec_geocodigos(inconsistencias, archivos):
    csv_link = ""
    if archivos.get("geocodigos"):
        csv_link = (f'<a href="{archivos["geocodigos"]}" download '
                    f'style="background:#1d4ed8;color:#bfdbfe;padding:2px 10px;'
                    f'border-radius:5px;font-size:11px;text-decoration:none">↓ CSV</a>')

    if not inconsistencias:
        return (f'<div class="section">'
                f'<div class="sec-title">⊙ Geocódigos {csv_link}</div>'
                f'<p class="ok-msg">✓ Sin inconsistencias de geocódigos.</p></div>')

    _ORDEN_TGEOM = {"puntos": 0, "líneas": 1, "poligono": 2}
    _ETIQ = {
        "valor_huerfano":          "Valor sin referencia",
        "sin_capa_referencia":     "Sin capa referencia",
        "inconsistencia_espacial": "Código incorrecto",
        "sin_poligono_contenedor": "Fuera de polígono",
    }
    por_capa = defaultdict(list)
    for i in inconsistencias:
        por_capa[(i["capa_origen"], i.get("tipo_geom", ""))].append(i)

    bloques = ""
    for (nom, tgeom), errs in sorted(
        por_capa.items(),
        key=lambda x: (_ORDEN_TGEOM.get(x[0][1], 3), x[0][0])
    ):
        total_n = sum(i.get("n_features", 0) for i in errs)
        icon    = {"puntos": "📍", "líneas": "〰", "poligono": "⬟"}.get(tgeom, "⬡")
        items   = ""
        for inc in errs:
            refs   = ", ".join(inc.get("capas_referencia") or []) or "—"
            etiq   = _ETIQ.get(inc.get("tipo", ""), inc.get("tipo", ""))
            raw    = inc.get("items", [])
            fids_s = ", ".join(str(it[0]) for it in raw[:8])
            suf    = f" …(+{len(raw)-8} más)" if len(raw) > 8 else ""
            fids_html = (f'<div style="color:#475569;font-size:11px;font-family:monospace">'
                         f'FIDs: {fids_s}{suf}</div>' if fids_s else "")
            items += (f'<div class="geo-item">'
                      f'<span style="color:#fbbf24;font-weight:600">Campo: {inc["campo"]}</span>'
                      f'<span style="color:#f87171;margin-left:10px">{etiq}</span>'
                      f'<span style="color:#64748b;margin-left:10px">{inc.get("n_features",0):,} feat.</span>'
                      f'<div style="color:#475569;font-size:12px;margin-top:3px">Capas: {refs}</div>'
                      f'{fids_html}</div>')

        bloques += (f'<div class="capa-card">'
                    f'<div class="capa-head">'
                    f'<span class="chev">▶</span>'
                    f'<span class="capa-name">{icon} {nom}</span>'
                    f'<span style="color:#94a3b8;font-size:11px">{tgeom.upper() if tgeom else ""}</span>'
                    f'<span style="color:#f87171;font-size:13px">{total_n:,} feat.</span>'
                    f'</div>'
                    f'<div class="capa-body">{items}</div>'
                    f'</div>')

    n_total = sum(i.get("n_features", 0) for i in inconsistencias)
    return (f'<div class="section">'
            f'<div class="sec-title">⊙ Geocódigos'
            f'<span style="color:#fbbf24;font-size:13px">{n_total:,} inconsistencias</span>'
            f'{csv_link}</div>{bloques}</div>')
