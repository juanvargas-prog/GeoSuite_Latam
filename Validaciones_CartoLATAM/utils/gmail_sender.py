"""
gmail_sender.py
---------------
Envío de correos con detección automática del método disponible:

  MÉTODO 1 — SMTP con App Password (prioritario, sin necesitar admin):
    Requiere GMAIL_APP_PASSWORD en config_local.py.
    Genera la contraseña en: cuenta Google → Seguridad
    → Verificación en 2 pasos → Contraseñas de aplicaciones.

  MÉTODO 2 — Gmail API con cuenta de servicio (cuando no hay App Password):
    Usa el mismo JSON de Google Sheets (RUTA_CREDENCIAL_SHEETS).
    Requiere Domain-wide delegation habilitada por el admin de Workspace.

Dos tipos de envío:
  - enviar_reporte_completo : cuerpo técnico + ZIP adjunto (HTML + CSVs)
  - enviar_reporte_resumido : solo KPIs ejecutivos, sin adjunto
"""

import base64
import html as _html_lib   # para escape seguro en templates de correo
import io
import os
import smtplib
import uuid
import zipfile
from collections import Counter
from datetime import datetime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .reporte_html import GEOM_LABEL as _GEOM_LABEL

# ── Credenciales: se leen en cada llamada para recoger cambios en config_local ─

_PLUGIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _credenciales():
    """Retorna (ruta_credencial, remitente, app_password) desde .env.

    Lee el .env directamente desde _PLUGIN_DIR para evitar conflictos
    con otros plugins que también registren un paquete 'utils' en sys.modules.
    """
    vals: dict = {}
    try:
        _env_path = os.path.join(_PLUGIN_DIR, ".env")
        if os.path.isfile(_env_path):
            with open(_env_path, encoding="utf-8") as _f:
                for _line in _f:
                    _line = _line.strip()
                    if not _line or _line.startswith("#") or "=" not in _line:
                        continue
                    _k, _, _v = _line.partition("=")
                    _v = _v.strip()
                    if len(_v) >= 2 and _v[0] == _v[-1] and _v[0] in ('"', "'"):
                        _v = _v[1:-1]
                    vals[_k.strip()] = _v
    except Exception:
        pass
    return (
        vals.get("RUTA_CREDENCIAL_SHEETS", ""),
        vals.get("GMAIL_REMITENTE",        "validacion@tudominio.com"),
        vals.get("GMAIL_APP_PASSWORD",     ""),
    )

# Variables de módulo para compatibilidad con código que las lee directamente
_RUTA_CREDENCIAL, GMAIL_REMITENTE, GMAIL_APP_PASSWORD = _credenciales()

SCOPE_GMAIL = [
    "https://www.googleapis.com/auth/gmail.send",
    # gmail.readonly eliminado — principio de mínimo privilegio
]


# ── Envío: SMTP si hay App Password, si no Gmail API ─────────────────────────

def _enviar_mensaje(msg):
    _, _, app_pwd = _credenciales()
    if app_pwd:
        _enviar_smtp(msg)
    else:
        _enviar_api(msg)


def _enviar_smtp(msg):
    _, remitente, app_pwd = _credenciales()
    pwd = app_pwd.replace(" ", "")
    with smtplib.SMTP("smtp.gmail.com", 587, timeout=15) as srv:
        srv.ehlo()
        srv.starttls()
        srv.login(remitente, pwd)
        srv.send_message(msg)


# ── Gmail API ─────────────────────────────────────────────────────────────────

def _get_service():
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    ruta, remitente, _ = _credenciales()
    creds = Credentials.from_service_account_file(
        ruta, scopes=SCOPE_GMAIL,
    ).with_subject(remitente)
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


def _enviar_api(msg):
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    _get_service().users().messages().send(
        userId="me", body={"raw": raw}
    ).execute()


def _leer_client_id():
    try:
        import json
        with open(_RUTA_CREDENCIAL, encoding="utf-8") as f:
            return json.load(f).get("client_id", "—")
    except Exception:
        return "—"


def probar_conexion(remitente=None, app_pwd=None):
    """
    Verifica el método de envío disponible.
    Si hay GMAIL_APP_PASSWORD → prueba SMTP.
    Si no → prueba Gmail API con cuenta de servicio.

    Si se pasan remitente y app_pwd se usan directamente (útil para probar
    credenciales recién escritas antes de guardarlas en .env).

    Retorna (ok: bool, detalle: str)
    """
    if remitente is None or app_pwd is None:
        _, _rem, _pwd = _credenciales()
        remitente = remitente or _rem
        app_pwd   = app_pwd   or _pwd
    if app_pwd:
        try:
            pwd = app_pwd.replace(" ", "")
            with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as srv:
                srv.ehlo()
                srv.starttls()
                srv.login(remitente, pwd)
            return True, f"✓ SMTP OK — autenticado como {remitente}"
        except smtplib.SMTPAuthenticationError:
            return False, (
                "✗ SMTP: contraseña de aplicación incorrecta.\n"
                "Genera una nueva en: cuenta Google → Seguridad\n"
                "→ Verificación en 2 pasos → Contraseñas de aplicaciones."
            )
        except Exception as e:
            msg = str(e).lower()
            if "timed out" in msg or "connection" in msg:
                return False, (
                    "✗ No se pudo conectar al servidor de correo.\n"
                    "Verifica tu conexión a internet e intenta de nuevo."
                )
            return False, (
                "✗ Error al conectar con el servidor de correo.\n"
                "Verifica que el remitente y la contraseña de aplicación sean correctos."
            )

    # Sin App Password → probar Gmail API
    try:
        svc    = _get_service()
        perfil = svc.users().getProfile(userId="me").execute()
        correo = perfil.get("emailAddress", GMAIL_REMITENTE)
        return True, f"✓ Gmail API OK — cuenta de servicio autorizada para {correo}"
    except Exception as e:
        msg_e = str(e)
        if "unauthorized_client" in msg_e.lower() or "domain-wide" in msg_e.lower():
            client_id = _leer_client_id()
            return False, (
                "✗ Gmail API: cuenta de servicio sin delegación de dominio.\n\n"
                "El admin debe configurarlo en:\n"
                "  Admin Console → Seguridad → Control de API\n"
                "  → Delegación en todo el dominio → Agregar nuevo\n\n"
                f"  Client ID : {client_id}\n"
                f"  Scope     : https://www.googleapis.com/auth/gmail.send"
            )
        if "no such file" in msg_e.lower() or "credentials" in msg_e.lower():
            return False, (
                f"✗ No se encuentra el archivo de credenciales.\n"
                f"Ruta: {_RUTA_CREDENCIAL}\n"
                "Verifica RUTA_CREDENCIAL_SHEETS en config_local.py."
            )
        return False, (
            "✗ Error al conectar con Gmail API.\n"
            "Verifica que el archivo de credenciales sea válido y que la cuenta "
            "de servicio tenga permisos para enviar correos."
        )


# ── ZIP con HTML + CSVs ───────────────────────────────────────────────────────

def _crear_zip_bytes(ruta_html, archivos_csv, carpeta_rep):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        if os.path.exists(ruta_html):
            zf.write(ruta_html, os.path.basename(ruta_html))
        for nombre_csv in archivos_csv.values():
            ruta_csv = os.path.join(carpeta_rep, nombre_csv)
            if os.path.exists(ruta_csv):
                zf.write(ruta_csv, nombre_csv)
    return buffer.getvalue()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _formato_tiempo(seg: float) -> str:
    """Convierte segundos a formato legible: '1m 23s' o '45s'."""
    seg = int(seg)
    if seg >= 60:
        m, s = divmod(seg, 60)
        return f"{m}m {s}s"
    return f"{seg}s"


def _nombre_desde_correo(correo: str) -> str:
    """Extrae nombre desde email: 'bryan.mora@empresa.com' → 'Bryan Mora'."""
    try:
        local = correo.strip().split("@")[0]
        return " ".join(p.capitalize() for p in local.replace(".", " ").replace("_", " ").split())
    except Exception:
        return correo


def _generar_message_id(remitente: str) -> str:
    domain = remitente.split("@")[-1] if "@" in remitente else "mail.local"
    return f"<{uuid.uuid4().hex}@{domain}>"


def _fmt_num(n: int) -> str:
    """Formatea entero con separador de miles en estilo español: 158.507"""
    return f"{n:,}".replace(",", ".")


# ── HTML cuerpo correo interno ────────────────────────────────────────────────

def _html_cuerpo_interno(stats_capas, inconsistencias, pais, tiempo_s, tarea=""):
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")

    total_feat = sum(s["total"]     for s in stats_capas)
    total_err  = sum(s["con_error"] for s in stats_capas)
    pct_global = round((total_feat - total_err) * 100 / total_feat, 1) if total_feat else 0

    def color(p):
        return "#27ae60" if p >= 90 else "#f39c12" if p >= 70 else "#e74c3c"

    filas_capas = ""
    for s in stats_capas:
        col = color(s["pct_calidad"])
        top = ""
        for campo in s["campos_ordenados"][:5]:
            n = len(s["errores_por_campo"][campo])
            top += (f"<tr><td style='padding:3px 10px;font-size:12px;color:#555'>{campo}</td>"
                    f"<td style='padding:3px 10px;font-size:12px;color:#e74c3c;font-weight:600'>"
                    f"{n:,}</td></tr>")
        if s["n_campos_error"] > 5:
            top += (f"<tr><td colspan='2' style='padding:3px 10px;font-size:11px;color:#aaa'>"
                    f"…y {s['n_campos_error']-5} campo(s) más</td></tr>")

        filas_capas += f"""
        <tr>
          <td style="padding:10px;border-bottom:1px solid #f0f0f0;font-weight:600">{s['nombre']}</td>
          <td style="padding:10px;border-bottom:1px solid #f0f0f0;text-align:center">{s['total']:,}</td>
          <td style="padding:10px;border-bottom:1px solid #f0f0f0;text-align:center;color:#27ae60;font-weight:600">{s['sin_error']:,}</td>
          <td style="padding:10px;border-bottom:1px solid #f0f0f0;text-align:center;color:#e74c3c;font-weight:600">{s['con_error']:,}</td>
          <td style="padding:10px;border-bottom:1px solid #f0f0f0;text-align:center">
            <span style="color:{col};font-weight:700">{s['pct_calidad']}%</span>
          </td>
          <td style="padding:10px;border-bottom:1px solid #f0f0f0">
            <table style="border:none;border-collapse:collapse">
              <tbody>{top or "<tr><td style='color:#27ae60;font-size:12px'>Sin errores</td></tr>"}</tbody>
            </table>
          </td>
        </tr>"""

    if inconsistencias:
        _tipos_cruce = {"valor_huerfano", "cruce_placa_mavvial", "id_mavvial_huerfano"}
        conteo = Counter(i["campo"] for i in inconsistencias if i["tipo"] in _tipos_cruce)
        filas_cruce = "".join(
            f"<tr><td style='padding:5px 10px;font-size:12px'>{c}</td>"
            f"<td style='padding:5px 10px;font-size:12px;color:#e74c3c;font-weight:600'>{n:,}</td></tr>"
            for c, n in conteo.most_common()
        )
        cruce_html = f"""
        <h3 style="color:#2c3e50;margin:24px 0 10px">Validación cruzada entre capas</h3>
        <p style="color:#e74c3c;font-weight:600;margin-bottom:8px">
          ⚠ {len(inconsistencias)} inconsistencia(s) encontrada(s)
        </p>
        <table style="border-collapse:collapse">
          <thead><tr style="background:#f8f9fa">
            <th style="padding:6px 10px;text-align:left;font-size:12px;color:#555">Campo</th>
            <th style="padding:6px 10px;text-align:left;font-size:12px;color:#555">Valores huérfanos</th>
          </tr></thead>
          <tbody>{filas_cruce}</tbody>
        </table>"""
    else:
        cruce_html = "<p style='color:#27ae60;font-weight:600;margin-top:16px'>✓ Validación cruzada: sin inconsistencias.</p>"

    tarea_html = (f'<p style="margin:6px 0 0;color:#94a3b8;font-size:12px">📌 {tarea}</p>'
                  if tarea else "")

    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"></head>
<body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;color:#2c3e50;max-width:760px;margin:0 auto">
  <div style="background:linear-gradient(135deg,#1e293b,#0f172a);color:white;padding:22px 30px;border-radius:8px 8px 0 0">
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:5px">
      <span style="background:#1d4ed8;color:#bfdbfe;padding:2px 10px;border-radius:20px;font-size:11px;font-weight:700">VALIDACIÓN INTERNA</span>
      <h2 style="margin:0;font-size:18px">Reporte — {pais}</h2>
    </div>
    {tarea_html}
    <p style="margin:6px 0 0;opacity:.6;font-size:12px">📅 {fecha} &nbsp;·&nbsp; ⏱ {tiempo_s:.1f}s &nbsp;·&nbsp; 🗂 {len(stats_capas)} capa(s)</p>
  </div>
  <div style="background:#f8fafc;padding:16px 30px;border:1px solid #e2e8f0;display:flex;gap:24px;flex-wrap:wrap">
    <div><span style="font-size:22px;font-weight:700">{total_feat:,}</span><br><span style="font-size:10px;color:#64748b;text-transform:uppercase">Features totales</span></div>
    <div><span style="font-size:22px;font-weight:700;color:#16a34a">{total_feat-total_err:,}</span><br><span style="font-size:10px;color:#64748b;text-transform:uppercase">Sin errores</span></div>
    <div><span style="font-size:22px;font-weight:700;color:#dc2626">{total_err:,}</span><br><span style="font-size:10px;color:#64748b;text-transform:uppercase">Con errores</span></div>
    <div><span style="font-size:22px;font-weight:700;color:{color(pct_global)}">{pct_global}%</span><br><span style="font-size:10px;color:#64748b;text-transform:uppercase">Calidad global</span></div>
  </div>
  <div style="padding:18px 30px;background:white;border:1px solid #e2e8f0;border-top:none">
    <h3 style="font-size:14px;color:#1e293b;margin:0 0 10px">Resumen por capa</h3>
    <table style="border-collapse:collapse;width:100%;font-size:12px">
      <thead><tr style="background:#1e293b;color:white">
        <th style="padding:7px 10px;text-align:left">Capa</th>
        <th style="padding:7px 10px;text-align:center">Features</th>
        <th style="padding:7px 10px;text-align:center">Con error</th>
        <th style="padding:7px 10px;text-align:center">Calidad</th>
        <th style="padding:7px 10px;text-align:left">Campos con más errores</th>
      </tr></thead>
      <tbody>{filas_capas}</tbody>
    </table>
    {cruce_html}
    <p style="margin-top:16px;font-size:11px;color:#94a3b8">
      📎 Se adjuntan los CSVs agrupados por tipo de error. Ábrelos en Excel para localizar los FIDs.
    </p>
  </div>
  <div style="background:#f8fafc;border-top:1px solid #e2e8f0;padding:10px 30px;text-align:center;color:#94a3b8;font-size:11px;border-radius:0 0 8px 8px">
    Reporte interno — Validaciones CartoLatam · {fecha}
  </div>
</body></html>"""


# ── HTML cuerpo correo entrega (líder) ────────────────────────────────────────

def _html_cuerpo_entrega(stats_capas, pais, tiempo_s, tarea=""):
    """Cuerpo del correo oficial de entrega para el líder."""
    fecha      = datetime.now().strftime("%d/%m/%Y %H:%M")
    total_feat = sum(s["total"]     for s in stats_capas)
    total_err  = sum(s["con_error"] for s in stats_capas)
    pct_global = round((total_feat - total_err) * 100 / total_feat, 1) if total_feat else 0

    def color(p):
        return "#16a34a" if p >= 90 else "#d97706" if p >= 70 else "#dc2626"

    col_g      = color(pct_global)
    tarea_html = (f'<p style="margin:5px 0 0;color:#94a3b8;font-size:12px">📌 {tarea}</p>'
                  if tarea else "")

    filas = ""
    for s in stats_capas:
        col   = color(s["pct_calidad"])
        badge = ("✓ BUENA" if s["pct_calidad"] >= 90
                 else "⚠ REGULAR" if s["pct_calidad"] >= 70 else "✗ CRÍTICA")
        bg_b  = ("#dcfce7" if s["pct_calidad"] >= 90
                 else "#fef9c3" if s["pct_calidad"] >= 70 else "#fee2e2")
        filas += (f"<tr>"
                  f"<td style='padding:9px 12px;border-bottom:1px solid #f0f0f0;font-weight:600'>{s['nombre']}</td>"
                  f"<td style='padding:9px 12px;border-bottom:1px solid #f0f0f0;text-align:center'>{s['total']:,}</td>"
                  f"<td style='padding:9px 12px;border-bottom:1px solid #f0f0f0;text-align:center;color:#dc2626;font-weight:600'>{s['con_error']:,}</td>"
                  f"<td style='padding:9px 12px;border-bottom:1px solid #f0f0f0;text-align:center;font-weight:700;color:{col}'>{s['pct_calidad']}%</td>"
                  f"<td style='padding:9px 12px;border-bottom:1px solid #f0f0f0;text-align:center'>"
                  f"<span style='background:{bg_b};color:{col};padding:2px 8px;border-radius:10px;font-size:11px;font-weight:700'>{badge}</span></td>"
                  f"</tr>")

    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"></head>
<body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;color:#1e293b;max-width:680px;margin:0 auto">
  <div style="background:linear-gradient(135deg,#1e293b,#0f172a);color:white;padding:24px 32px;border-radius:8px 8px 0 0">
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:5px">
      <span style="background:#059669;color:#d1fae5;padding:2px 10px;border-radius:20px;font-size:11px;font-weight:700">ENTREGA OFICIAL</span>
      <h2 style="margin:0;font-size:19px">Reporte de Validación — {pais}</h2>
    </div>
    {tarea_html}
    <p style="margin:6px 0 0;opacity:.65;font-size:12px">📅 {fecha} &nbsp;·&nbsp; ⏱ {tiempo_s:.1f}s &nbsp;·&nbsp; 🗂 {len(stats_capas)} capa(s)</p>
  </div>
  <div style="padding:20px 32px;background:white;border:1px solid #e2e8f0;border-top:none">
    <div style="text-align:center;padding:20px;background:#f8fafc;border-radius:10px;margin-bottom:20px;border:1px solid #e2e8f0">
      <div style="font-size:48px;font-weight:800;color:{col_g}">{pct_global}%</div>
      <div style="font-size:13px;color:#64748b;margin-top:4px">Calidad global de datos</div>
      <div style="font-size:12px;color:#94a3b8;margin-top:2px">{total_feat-total_err:,} de {total_feat:,} features sin errores</div>
    </div>
    <table style="border-collapse:collapse;width:100%;font-size:13px">
      <thead><tr style="background:#1e293b;color:white">
        <th style="padding:9px 12px;text-align:left">Capa</th>
        <th style="padding:9px 12px;text-align:center">Features</th>
        <th style="padding:9px 12px;text-align:center">Con error</th>
        <th style="padding:9px 12px;text-align:center">Calidad</th>
        <th style="padding:9px 12px;text-align:center">Estado</th>
      </tr></thead>
      <tbody>{filas}</tbody>
    </table>
    <p style="margin-top:18px;font-size:12px;color:#64748b;border-top:1px solid #f0f0f0;padding-top:12px">
      📎 Se adjunta el reporte técnico completo (HTML interactivo + CSVs de errores por FID, campo y capa).
    </p>
  </div>
  <div style="background:#f8fafc;border-top:1px solid #e2e8f0;padding:10px 32px;text-align:center;color:#94a3b8;font-size:11px;border-radius:0 0 8px 8px">
    Validaciones CartoLatam · {fecha}
  </div>
</body></html>"""


# ── Funciones públicas ────────────────────────────────────────────────────────

def _resumen_tabla(stats_capas) -> str:
    """Genera una tabla HTML con el resumen de capas para los correos."""
    def col(p): return "#16a34a" if p >= 90 else "#d97706" if p >= 70 else "#dc2626"
    filas = ""
    for s in (stats_capas or []):
        c = col(s["pct_calidad"])
        filas += (
            f"<tr>"
            f"<td style='padding:8px 12px;border-bottom:1px solid #e5e7eb'>{s['nombre']}</td>"
            f"<td style='padding:8px 12px;border-bottom:1px solid #e5e7eb;text-align:center'>{s['total']:,}</td>"
            f"<td style='padding:8px 12px;border-bottom:1px solid #e5e7eb;text-align:center;"
            f"color:#16a34a;font-weight:600'>{s['sin_error']:,}</td>"
            f"<td style='padding:8px 12px;border-bottom:1px solid #e5e7eb;text-align:center;"
            f"color:#dc2626;font-weight:600'>{s['con_error']:,}</td>"
            f"<td style='padding:8px 12px;border-bottom:1px solid #e5e7eb;text-align:center;"
            f"color:{c};font-weight:700'>{s['pct_calidad']}%</td>"
            f"</tr>"
        )
    if not filas:
        return ""
    return (
        "<table style='border-collapse:collapse;width:100%;font-size:13px;margin-top:12px'>"
        "<thead><tr style='background:#f9fafb'>"
        "<th style='padding:8px 12px;text-align:left;color:#374151'>Capa</th>"
        "<th style='padding:8px 12px;text-align:center;color:#374151'>Features</th>"
        "<th style='padding:8px 12px;text-align:center;color:#374151'>Sin error</th>"
        "<th style='padding:8px 12px;text-align:center;color:#374151'>Con error</th>"
        "<th style='padding:8px 12px;text-align:center;color:#374151'>Calidad</th>"
        "</tr></thead>"
        f"<tbody>{filas}</tbody></table>"
    )


def _html_interno_template(colaborador, orden, pais, tipo_general, tipo_alcance,
                            tiempo, numero_intento, encargado, stats_capas,
                            modo=None, comentario="") -> str:
    from datetime import datetime
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    tabla = _resumen_tabla(stats_capas)
    # Escapar todas las variables de usuario para prevenir XSS / inyección HTML
    _e = _html_lib.escape
    colaborador  = _e(str(colaborador))
    orden        = _e(str(orden))
    pais         = _e(str(pais))
    tipo_general = _e(str(tipo_general))
    tipo_alcance = _e(str(tipo_alcance))
    tiempo       = _e(str(tiempo))
    encargado    = _e(str(encargado))
    _modo = modo or set()
    _TIPOS = [
        ("estructura",  "Estructura"),
        ("atributos",   "Atributos"),
        ("topologia",   "Topología"),
        ("geocodigos",  "Geocódigos"),
    ]
    _filas_tipos = ""
    for clave, etiq in _TIPOS:
        if clave in _modo:
            badge = ("<span style='color:#16a34a;font-weight:700'>✓ Realizada</span>")
        else:
            badge = ("<span style='color:#9ca3af'>— No se realizó</span>")
        _filas_tipos += (
            f"<tr><td style='padding:5px 0;color:#6b7280;width:160px'>{etiq}</td>"
            f"<td style='padding:5px 0'>{badge}</td></tr>"
        )

    comentario_html = (
        f'<div style="background:#fefce8;border-left:4px solid #f59e0b;'
        f'border-radius:6px;padding:14px 18px;margin:20px 0 0;font-size:13px;color:#374151">'
        f'<p style="margin:0 0 6px;font-size:11px;font-weight:700;letter-spacing:0.5px;color:#92400e">'
        f'COMENTARIOS DEL VALIDADOR</p>'
        f'<p style="margin:0;white-space:pre-wrap;line-height:1.6">{_e(str(comentario))}</p>'
        f'</div>'
    ) if comentario and str(comentario).strip() else ""
    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"></head>
<body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
             color:#111827;max-width:620px;margin:0 auto;background:#f9fafb">
  <div style="background:#1e1e20;color:white;padding:28px 32px;border-radius:12px 12px 0 0">
    <div style="font-size:11px;letter-spacing:1px;color:#9ca3af;margin-bottom:6px">
      VALIDACIÓN INTERNA DE CALIDAD
    </div>
    <h2 style="margin:0;font-size:20px;font-weight:700">{pais} — {orden}</h2>
    <p style="margin:6px 0 0;font-size:12px;color:#9ca3af">{fecha}</p>
  </div>
  <div style="background:white;padding:28px 32px;border:1px solid #e5e7eb;border-top:none">
    <p style="margin:0 0 20px;font-size:14px;line-height:1.6;color:#374151">
      Saludos <strong>{colaborador}</strong>,<br><br>
      Se han finalizado las validaciones para la OT INTERNA <strong>{orden}</strong>,
      correspondiente al país <strong>{pais}</strong>.<br>
      Por favor, revisa detalladamente los resultados y comunícate con
      <strong>{encargado}</strong> en caso de algún inconveniente o discrepancia.
    </p>
    <div style="background:#f9fafb;border-radius:8px;padding:18px 20px;margin-bottom:20px">
      <p style="margin:0 0 10px;font-size:11px;font-weight:700;letter-spacing:0.5px;color:#6b7280">
        RESUMEN DE VALIDACIONES EJECUTADAS
      </p>
      <table style="border-collapse:collapse;width:100%;font-size:13px">
        <tr><td style="padding:5px 0;color:#6b7280;width:160px">Tipo</td>
            <td style="padding:5px 0;font-weight:600">{tipo_general}</td></tr>
        <tr><td style="padding:5px 0;color:#6b7280">País</td>
            <td style="padding:5px 0;font-weight:600">{pais}</td></tr>
        <tr><td style="padding:5px 0;color:#6b7280">Orden</td>
            <td style="padding:5px 0;font-weight:600">{orden}</td></tr>
        <tr><td style="padding:5px 0;color:#6b7280">Tiempo de ejecución</td>
            <td style="padding:5px 0;font-weight:600">{tiempo}</td></tr>
        <tr><td style="padding:5px 0;color:#6b7280">Número de intento</td>
            <td style="padding:5px 0;font-weight:700;color:#4b7bf5">#{numero_intento}</td></tr>
      </table>
    </div>
    <div style="background:#f9fafb;border-radius:8px;padding:18px 20px;margin-bottom:20px">
      <p style="margin:0 0 10px;font-size:11px;font-weight:700;letter-spacing:0.5px;color:#6b7280">
        VALIDACIONES INDIVIDUALES
      </p>
      <table style="border-collapse:collapse;width:100%;font-size:13px">
        {_filas_tipos}
      </table>
    </div>
    <p style="margin:0 0 8px;font-size:13px;font-weight:600;color:#374151">
      Resumen por capa:
    </p>
    {tabla}
    {comentario_html}
    <p style="margin:20px 0 0;font-size:12px;color:#9ca3af">
      📎 Los archivos CSV con el detalle de errores se adjuntan a este correo.
    </p>
  </div>
  <div style="background:#f9fafb;border:1px solid #e5e7eb;border-top:none;
              padding:12px 32px;border-radius:0 0 12px 12px;text-align:center;
              font-size:11px;color:#9ca3af">
    Validaciones CartoLatam · Servinformación · {fecha}
  </div>
</body></html>"""


def _html_entrega_template(profesional, orden, pais, tipo_general, tipo_alcance,
                            tiempo, intentos_internos, stats_capas,
                            inconsistencias=None, comentario="") -> str:
    from datetime import datetime
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    _e = _html_lib.escape

    profesional  = _e(str(profesional))
    orden        = _e(str(orden))
    pais         = _e(str(pais))
    tipo_general = _e(str(tipo_general))
    tipo_alcance = _e(str(tipo_alcance))
    tiempo       = _e(str(tiempo))
    comentario_html = (
        f'<div style="background:#fefce8;border-left:4px solid #f59e0b;'
        f'border-radius:6px;padding:14px 18px;margin:20px 0 0;font-size:13px;color:#374151">'
        f'<p style="margin:0 0 6px;font-size:11px;font-weight:700;letter-spacing:0.5px;color:#92400e">'
        f'COMENTARIOS DEL VALIDADOR</p>'
        f'<p style="margin:0;white-space:pre-wrap;line-height:1.6">{_e(str(comentario))}</p>'
        f'</div>'
    ) if comentario and str(comentario).strip() else ""
    intentos_txt = (
        f"{intentos_internos} validación{'es' if intentos_internos != 1 else ''} interna{'s' if intentos_internos != 1 else ''} previa{'s' if intentos_internos != 1 else ''}"
        if intentos_internos > 0 else "Primera validación"
    )
    def col_pct(p):
        return "#16a34a" if p >= 90 else "#d97706" if p >= 70 else "#dc2626"

    # ── Detalle completo por capa ─────────────────────────────────────────────
    MAX_ERRORES_CAMPO = 100   # máx filas por campo para no inflar el correo

    detalle_capas = ""
    for s in (stats_capas or []):
        if not s.get("campos_ordenados"):
            detalle_capas += (
                f'<details style="margin-bottom:10px">'
                f'<summary style="cursor:pointer;padding:10px 14px;'
                f'background:#f0fdf4;border-radius:8px;font-weight:600;'
                f'font-size:13px;color:#15803d;list-style:none">'
                f'✓ {_e(s["nombre"])} — Sin errores</summary></details>'
            )
            continue

        col = col_pct(s["pct_calidad"])
        campos_html = ""
        for campo in s.get("campos_ordenados", []):
            items = s["errores_por_campo"].get(campo, [])
            n_total = len(items)
            muestra = items[:MAX_ERRORES_CAMPO]
            filas = "".join(
                f'<tr style="border-bottom:1px solid #f3f4f6">'
                f'<td style="padding:5px 8px;font-family:monospace;font-size:11px;'
                f'color:#6b7280;white-space:nowrap">{_e(str(it["fid"]))}</td>'
                f'<td style="padding:5px 8px;font-size:11px;color:#1d4ed8;'
                f'max-width:140px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">'
                f'{_e(str(it.get("valor",""))[:50])}</td>'
                f'<td style="padding:5px 8px;font-size:11px;color:#374151">'
                f'{_e(str(it.get("msg","")))}</td>'
                f'</tr>'
                for it in muestra
            )
            aviso = (
                f'<p style="margin:6px 0 0;font-size:11px;color:#f59e0b">'
                f'Mostrando {MAX_ERRORES_CAMPO:,} de {n_total:,} errores. '
                f'Descarga el CSV para ver todos.</p>'
            ) if n_total > MAX_ERRORES_CAMPO else ""

            campos_html += (
                f'<details style="margin:6px 0">'
                f'<summary style="cursor:pointer;padding:8px 12px;'
                f'background:#fef9f0;border-radius:6px;font-size:12px;'
                f'font-weight:600;color:#92400e;list-style:none">'
                f'{_e(campo)}  '
                f'<span style="color:#dc2626;font-weight:700">{n_total:,} errores</span>'
                f'</summary>'
                f'<div style="overflow-x:auto;margin-top:6px">'
                f'<table style="border-collapse:collapse;width:100%;font-size:12px">'
                f'<thead><tr style="background:#f9fafb">'
                f'<th style="padding:6px 8px;text-align:left;color:#6b7280;font-weight:600">FID</th>'
                f'<th style="padding:6px 8px;text-align:left;color:#6b7280;font-weight:600">Valor</th>'
                f'<th style="padding:6px 8px;text-align:left;color:#6b7280;font-weight:600">Error</th>'
                f'</tr></thead>'
                f'<tbody>{filas}</tbody>'
                f'</table>{aviso}</div>'
                f'</details>'
            )

        detalle_capas += (
            f'<details style="margin-bottom:12px">'
            f'<summary style="cursor:pointer;padding:12px 16px;'
            f'background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;'
            f'font-weight:700;font-size:13px;list-style:none;display:flex;'
            f'align-items:center;gap:12px">'
            f'{_e(s["nombre"])}'
            f'<span style="color:{col};font-weight:700">{s["pct_calidad"]}%</span>'
            f'<span style="color:#dc2626;font-size:12px">{s["con_error"]:,} features con errores</span>'
            f'</summary>'
            f'<div style="padding:10px 0 0 0">{campos_html}</div>'
            f'</details>'
        )

    # ── Geocódigos ────────────────────────────────────────────────────────────
    geocodigos_html = ""
    if inconsistencias:
        _ETIQ = {
            "valor_huerfano":          "Valor sin referencia",
            "inconsistencia_espacial": "Código incorrecto",
            "sin_capa_referencia":     "Sin capa referencia",
            "cruce_placa_mavvial":     "Cruce placa-mavvial",
            "id_mavvial_huerfano":     "ID mavvial huérfano",
        }
        filas_geo = ""
        for inc in inconsistencias[:200]:
            refs = ", ".join(inc.get("capas_referencia") or []) or "—"
            etiq = _ETIQ.get(inc.get("tipo", ""), inc.get("tipo", ""))
            sample_fids = ", ".join(
                str(it[0]) for it in (inc.get("items") or [])[:8]
            )
            suf = f" …(+{len(inc.get('items',[]))-8} más)" if len(inc.get("items",[])) > 8 else ""
            filas_geo += (
                f'<tr style="border-bottom:1px solid #fef3c7">'
                f'<td style="padding:6px 8px;font-size:12px;font-weight:600">'
                f'{_e(inc["capa_origen"])}</td>'
                f'<td style="padding:6px 8px;font-size:12px;font-family:monospace;color:#1d4ed8">'
                f'{_e(inc["campo"])}</td>'
                f'<td style="padding:6px 8px;font-size:12px;color:#92400e">{_e(etiq)}</td>'
                f'<td style="padding:6px 8px;font-size:11px;text-align:center;font-weight:700;color:#dc2626">'
                f'{inc.get("n_features",0):,}</td>'
                f'<td style="padding:6px 8px;font-size:10px;color:#6b7280;font-family:monospace">'
                f'{_e(sample_fids)}{_e(suf)}</td>'
                f'</tr>'
            )
        n_geo = sum(i.get("n_features",0) for i in inconsistencias)
        geocodigos_html = (
            f'<h3 style="font-size:14px;font-weight:700;color:#1e293b;margin:24px 0 10px">'
            f'Geocódigos — {len(inconsistencias)} inconsistencias · {n_geo:,} features</h3>'
            f'<div style="overflow-x:auto">'
            f'<table style="border-collapse:collapse;width:100%;font-size:12px">'
            f'<thead><tr style="background:#fef9c3">'
            f'<th style="padding:7px 8px;text-align:left;color:#6b7280">Capa</th>'
            f'<th style="padding:7px 8px;text-align:left;color:#6b7280">Campo</th>'
            f'<th style="padding:7px 8px;text-align:left;color:#6b7280">Tipo</th>'
            f'<th style="padding:7px 8px;text-align:center;color:#6b7280">Features</th>'
            f'<th style="padding:7px 8px;text-align:left;color:#6b7280">FIDs muestra</th>'
            f'</tr></thead>'
            f'<tbody>{filas_geo}</tbody>'
            f'</table></div>'
        )

    tabla_resumen = _resumen_tabla(stats_capas)

    return f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8">
<style>
  details > summary {{ user-select:none; }}
  details > summary::-webkit-details-marker {{ display:none; }}
  details > summary::before {{ content:"▶ "; font-size:10px; }}
  details[open] > summary::before {{ content:"▼ "; }}
</style>
</head>
<body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
             color:#111827;max-width:740px;margin:0 auto;background:#f9fafb">

  <div style="background:#1c2b50;color:white;padding:28px 32px;border-radius:12px 12px 0 0">
    <div style="font-size:11px;letter-spacing:1px;color:#93c5fd;margin-bottom:6px">
      VALIDACIÓN ENTREGA FINAL
    </div>
    <h2 style="margin:0;font-size:20px;font-weight:700">{pais} — {orden}</h2>
    <p style="margin:6px 0 0;font-size:12px;color:#93c5fd">{fecha}</p>
  </div>

  <div style="background:white;padding:28px 32px;border:1px solid #e5e7eb;border-top:none">

    <p style="margin:0 0 20px;font-size:14px;line-height:1.6;color:#374151">
      Saludos estimado líder,<br><br>
      Se han finalizado las validaciones de la OT <strong>{orden}</strong>,
      país <strong>{pais}</strong>, ejecutadas por <strong>{profesional}</strong>.
    </p>

    <div style="background:#f8fafc;border-radius:8px;padding:16px 20px;margin-bottom:24px">
      <p style="margin:0 0 10px;font-size:11px;font-weight:700;letter-spacing:0.5px;color:#6b7280">
        INFORMACIÓN DE LA VALIDACIÓN
      </p>
      <table style="border-collapse:collapse;width:100%;font-size:13px">
        <tr><td style="padding:4px 0;color:#6b7280;width:160px">Tipo</td>
            <td style="padding:4px 0;font-weight:600">{tipo_general}</td></tr>
        <tr><td style="padding:4px 0;color:#6b7280">Alcance</td>
            <td style="padding:4px 0;font-weight:600">{tipo_alcance}</td></tr>
        <tr><td style="padding:4px 0;color:#6b7280">Tiempo de ejecución</td>
            <td style="padding:4px 0;font-weight:600">{tiempo}</td></tr>
        <tr><td style="padding:4px 0;color:#6b7280">Historial</td>
            <td style="padding:4px 0;font-weight:600;color:#4b7bf5">{intentos_txt}</td></tr>
      </table>
    </div>

    <h3 style="font-size:14px;font-weight:700;color:#1e293b;margin:0 0 12px">
      Resumen por capa
    </h3>
    {tabla_resumen}

    <h3 style="font-size:14px;font-weight:700;color:#1e293b;margin:24px 0 12px">
      Detalle de errores por capa
      <span style="font-size:11px;font-weight:400;color:#6b7280">
        (haz clic en cada capa para expandir)
      </span>
    </h3>
    {detalle_capas}

    {geocodigos_html}
    {comentario_html}

    <p style="margin:24px 0 0;font-size:12px;color:#9ca3af;border-top:1px solid #f3f4f6;padding-top:14px">
      📎 El reporte HTML interactivo completo y los CSVs de errores se adjuntan como ZIP.
    </p>
  </div>

  <div style="background:#f9fafb;border:1px solid #e5e7eb;border-top:none;
              padding:12px 32px;border-radius:0 0 12px 12px;text-align:center;
              font-size:11px;color:#9ca3af">
    Validaciones CartoLatam · Servinformación · {fecha}
  </div>
</body></html>"""


def enviar_reporte_interno(destinatarios, stats_capas, inconsistencias,
                           pais, tiempo_s, orden="", responsable="",
                           colaboradores="", tipo_validacion="",
                           numero_intento=1,
                           ruta_html=None, archivos_csv=None, carpeta_rep=None,
                           comentario="", modo=None):
    """
    Correo de Validación Interna de Calidad.
    Destinatarios: quien corrió + colaboradores + Bryan (fijo).
    Correo SIEMPRE obligatorio — lanza excepción si falla.
    """
    _, remitente, _ = _credenciales()
    encargado_email = "bryan.mora@servinformacion.com"
    encargado_nombre = "Bryan Mora"

    # Nombre del que corrió la validación
    nombre_responsable = responsable or _nombre_desde_correo(remitente)

    # Asunto unificado (ambos correos del hilo comparten este asunto)
    asunto = f"LATAM | {pais} - {orden}"

    # Destinatarios: remitente + colaboradores + Bryan
    lista_dest = [remitente]
    if colaboradores:
        lista_dest += [c.strip() for c in colaboradores.split(",") if c.strip()]
    if encargado_email not in lista_dest:
        lista_dest.append(encargado_email)

    # Tiempo formateado
    tiempo_fmt = _formato_tiempo(tiempo_s)

    # Cuerpo del correo
    cuerpo = _html_interno_template(
        colaborador=nombre_responsable,
        orden=orden,
        pais=pais,
        tipo_general="Validación interna de calidad",
        tipo_alcance=tipo_validacion,
        tiempo=tiempo_fmt,
        numero_intento=numero_intento,
        encargado=encargado_nombre,
        stats_capas=stats_capas,
        modo=modo,
        comentario=comentario,
    )

    mid = _generar_message_id(remitente)
    msg = MIMEMultipart("mixed")
    msg["From"]       = remitente
    msg["To"]         = ", ".join(lista_dest)
    msg["Subject"]    = asunto
    msg["Message-ID"] = mid
    msg.attach(MIMEText(cuerpo, "html", "utf-8"))

    # Adjuntar CSVs agrupados
    if archivos_csv and carpeta_rep:
        for clave in ("atributos_agrupados", "topologia", "geocodigos"):
            nombre_csv = archivos_csv.get(clave)
            if not nombre_csv:
                continue
            ruta_csv = os.path.join(carpeta_rep, nombre_csv)
            if os.path.exists(ruta_csv):
                with open(ruta_csv, "rb") as f:
                    parte = MIMEApplication(f.read(), Name=nombre_csv)
                parte["Content-Disposition"] = f'attachment; filename="{nombre_csv}"'
                msg.attach(parte)

    _enviar_mensaje(msg)
    return asunto, lista_dest, mid


# ── HTML resumen de capas entregadas ─────────────────────────────────────────

def _html_resumen_capas(pais, orden, drive_url, stats_capas):
    fecha_str   = datetime.now().strftime("%m-%Y")
    version_str = "V1-" + datetime.now().strftime("%y")

    filas = ""
    total_reg = 0
    for i, s in enumerate(stats_capas):
        bg    = "#ffffff" if i % 2 == 0 else "#f8fafc"
        tg    = _GEOM_LABEL.get(s.get("tipo_geom", ""), s.get("tipo_geom", "—"))
        _t = s.get("total")
        n_reg = _t if _t is not None else (s.get("n_registros") or 0)
        total_reg += n_reg
        filas += f"""
        <tr style="background:{bg}">
          <td style="padding:8px 12px;border-bottom:1px solid #e2e8f0">{_html_lib.escape(s['nombre'])}</td>
          <td style="padding:8px 12px;border-bottom:1px solid #e2e8f0;text-align:center">{tg}</td>
          <td style="padding:8px 12px;border-bottom:1px solid #e2e8f0;text-align:right">{_fmt_num(n_reg)}</td>
        </tr>"""

    intro = (f"A continuación, se realiza entrega de capas cartografía "
             f"{_html_lib.escape(pais)}.")

    link_html = (f'<a href="{_html_lib.escape(drive_url)}" '
                 f'style="color:#1d4ed8;text-decoration:none">'
                 f'{_html_lib.escape(orden)}</a>'
                 if drive_url else _html_lib.escape(orden))

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"></head>
<body style="font-family:Arial,sans-serif;font-size:14px;color:#1e293b;margin:0;padding:20px">
  <p style="margin:0 0 16px">{intro}</p>

  <table style="border-collapse:collapse;margin-bottom:20px">
    <tbody>
      <tr>
        <td style="padding:4px 12px 4px 0;font-weight:600;white-space:nowrap">Ver Carpeta:</td>
        <td style="padding:4px 0">{_html_lib.escape(orden)}</td>
      </tr>
      <tr>
        <td style="padding:4px 12px 4px 0;font-weight:600">Fecha:</td>
        <td style="padding:4px 0">{fecha_str}</td>
      </tr>
      <tr>
        <td style="padding:4px 12px 4px 0;font-weight:600">Versión:</td>
        <td style="padding:4px 0">{version_str}</td>
      </tr>
      <tr>
        <td style="padding:4px 12px 4px 0;font-weight:600">Ruta de acceso:</td>
        <td style="padding:4px 0">{link_html}</td>
      </tr>
    </tbody>
  </table>

  <table style="border-collapse:collapse;width:100%;max-width:560px">
    <thead>
      <tr style="background:#1d4ed8;color:#ffffff">
        <th style="padding:10px 12px;text-align:left;font-size:13px">NOMBRE CAPA</th>
        <th style="padding:10px 12px;text-align:center;font-size:13px">TIPO DE GEOMETRÍA</th>
        <th style="padding:10px 12px;text-align:right;font-size:13px">REGISTROS</th>
      </tr>
    </thead>
    <tbody>{filas}</tbody>
    <tfoot>
      <tr style="background:#1d4ed8;color:#ffffff;font-weight:700">
        <td colspan="2" style="padding:10px 12px;font-size:13px">Total</td>
        <td style="padding:10px 12px;text-align:right;font-size:13px">{_fmt_num(total_reg)}</td>
      </tr>
    </tfoot>
  </table>
</body></html>"""


def enviar_resumen_capas(destinatarios, stats_capas, pais, orden,
                          drive_url="", in_reply_to=""):
    """
    Segundo correo del hilo: resumen de capas entregadas (tabla nombre/geom/registros).
    Se hila con el correo de validaciones usando In-Reply-To.
    """
    _, remitente, _ = _credenciales()
    asunto = f"LATAM | {pais} - {orden}"

    cuerpo = _html_resumen_capas(
        pais=pais,
        orden=orden,
        drive_url=drive_url,
        stats_capas=stats_capas,
    )

    mid = _generar_message_id(remitente)
    msg = MIMEMultipart("mixed")
    msg["From"]       = remitente
    msg["To"]         = ", ".join(destinatarios)
    msg["Subject"]    = asunto
    msg["Message-ID"] = mid
    if in_reply_to:
        msg["In-Reply-To"] = in_reply_to
        msg["References"]  = in_reply_to
    msg.attach(MIMEText(cuerpo, "html", "utf-8"))

    _enviar_mensaje(msg)


def enviar_reporte_entrega(destinatario_lider, stats_capas, inconsistencias,
                           pais, tiempo_s, orden="", responsable="",
                           tipo_validacion="", intentos_internos=0,
                           ruta_html=None, archivos_csv=None, carpeta_rep=None,
                           comentario=""):
    """
    Correo de Validación Entrega Final.
    Destinatarios: quien corrió + Bryan + líder.
    Correo SIEMPRE obligatorio — lanza excepción si falla.
    """
    _, remitente, _ = _credenciales()
    encargado_email = "bryan.mora@servinformacion.com"
    lider_fijo      = "jhoinner.manrique@servinformacion.com"   # líder siempre obligatorio

    nombre_profesional = responsable or _nombre_desde_correo(remitente)
    asunto = f"LATAM | {pais} - {orden} | Validaciones de entrega"

    # Destinatarios: remitente + Bryan + líder fijo + líder adicional si se configuró
    lista_dest = [remitente]
    for correo in (encargado_email, lider_fijo):
        if correo not in lista_dest:
            lista_dest.append(correo)
    if destinatario_lider and destinatario_lider not in lista_dest:
        lista_dest.append(destinatario_lider)

    tiempo_fmt = _formato_tiempo(tiempo_s)

    cuerpo = _html_entrega_template(
        profesional=nombre_profesional,
        orden=orden,
        pais=pais,
        tipo_general="Validación entrega final",
        tipo_alcance=tipo_validacion,
        tiempo=tiempo_fmt,
        intentos_internos=intentos_internos,
        stats_capas=stats_capas,
        inconsistencias=inconsistencias,
        comentario=comentario,
    )

    msg = MIMEMultipart("mixed")
    msg["From"]    = remitente
    msg["To"]      = ", ".join(lista_dest)
    msg["Subject"] = asunto
    msg.attach(MIMEText(cuerpo, "html", "utf-8"))

    if ruta_html and archivos_csv and carpeta_rep:
        zip_bytes  = _crear_zip_bytes(ruta_html, archivos_csv, carpeta_rep)
        nombre_zip = f"entrega_{pais.replace(' ', '_')}_{orden}.zip"
        parte_zip  = MIMEApplication(zip_bytes, Name=nombre_zip)
        parte_zip["Content-Disposition"] = f'attachment; filename="{nombre_zip}"'
        msg.attach(parte_zip)

    _enviar_mensaje(msg)
    return asunto, lista_dest


