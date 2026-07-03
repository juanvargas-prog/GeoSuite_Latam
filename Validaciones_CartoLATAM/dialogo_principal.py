"""
dialogo_principal.py
--------------------
Diálogo principal — diseño dashboard oscuro, 3 páginas via QStackedWidget:
  0 — Selección : país + capas
  1 — Progreso  : barras + estadísticas en vivo
  2 — Resultados: KPIs animados + tarjetas por capa + correo
"""

import concurrent.futures
import os
import sys
import time

from collections import Counter
from datetime import datetime

from qgis.core import (
    QgsProject, QgsVectorLayer, QgsField, QgsFeature,
    QgsWkbTypes, QgsFeatureRequest,
)
from qgis.PyQt.QtCore import Qt, QSize, QVariant, QTimer, QPropertyAnimation, QEasingCurve
from qgis.PyQt.QtGui import QColor, QPixmap
from qgis.PyQt.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QDialog, QFileDialog,
    QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QMessageBox, QProgressBar,
    QPushButton, QScrollArea, QSizePolicy, QStackedWidget,
    QTextEdit, QVBoxLayout, QWidget,
)

PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
_EXTENSIONES_VECTOR = {".shp", ".gpkg", ".geojson", ".json", ".kml", ".gml", ".sqlite"}

# ══════════════════════════════════════════════════════════════════════════════
# DESIGN SYSTEM — CartoLatam Enterprise
# Navy oscuro frío · Acento teal · Sin glows · Dashboard profesional
# ══════════════════════════════════════════════════════════════════════════════

# Fondos — navy oscuro frío
C_ROOT      = "#0B0F1A"
C_SURFACE   = "#0F172A"
C_SURFACE_2 = "#1A2438"
C_SURFACE_3 = "#1E2A40"

# Bordes
C_BORDER    = "#1E2D45"
C_BORDER_2  = "#2D3F5C"

# Texto
C_TEXT      = "#E2E8F0"
C_SUBTEXT   = "#94A3B8"
C_MUTED     = "#475569"
C_DISABLED  = "#2D3748"
C_WHITE     = "#FFFFFF"

# Acento — teal
C_ACCENT     = "#2DD4BF"
C_ACCENT_HV  = "#5EEAD4"
C_ACCENT_DIM = "#042F2E"

# Estados
C_OK        = "#22C55E"
C_OK_DIM    = "#052E16"
C_WARN      = "#F59E0B"
C_WARN_DIM  = "#1C1003"
C_ERR       = "#EF4444"
C_ERR_DIM   = "#2D0707"

# Geometría
C_GEOM_LINE      = "#38BDF8"
C_GEOM_POINT     = "#A78BFA"
C_GEOM_POLY      = "#34D399"
C_GEOM_LINE_DIM  = "#0C2233"
C_GEOM_POINT_DIM = "#170D33"
C_GEOM_POLY_DIM  = "#052E1C"

# Modo de proceso
C_INTERNO      = "#A78BFA"
C_INTERNO_DIM  = "#170D33"
C_ENTREGA      = "#38BDF8"
C_ENTREGA_DIM  = "#0C2233"

# Producto
C_PROD      = "#22C55E"
C_PROD_DIM  = "#052E16"
C_GEO       = "#818CF8"
C_GEO_DIM   = "#1E1B4B"
C_GEOMKT    = "#F59E0B"
C_GEOMKT_DIM= "#1C1003"

# ── Botones ───────────────────────────────────────────────────────────────────
STYLE_BTN_PRIMARY = (
    f"QPushButton{{background:{C_ACCENT};color:#0A1E1C;"
    f"padding:10px 22px;border-radius:8px;font-size:13px;font-weight:700;"
    f"border:none;}}"
    f"QPushButton:hover{{background:{C_ACCENT_HV};}}"
    f"QPushButton:pressed{{background:#0D9488;}}"
    f"QPushButton:disabled{{background:{C_SURFACE_2};color:{C_DISABLED};border:none;}}"
)
STYLE_BTN_GHOST = (
    f"QPushButton{{background:transparent;color:{C_SUBTEXT};"
    f"padding:10px 20px;border-radius:8px;font-size:13px;font-weight:500;"
    f"border:1px solid {C_BORDER};}}"
    f"QPushButton:hover{{color:{C_TEXT};background:{C_SURFACE_2};"
    f"border-color:{C_BORDER_2};}}"
    f"QPushButton:disabled{{color:{C_DISABLED};}}"
)
STYLE_BTN_DANGER = (
    f"QPushButton{{background:transparent;color:{C_ERR};"
    f"padding:10px 20px;border-radius:8px;font-size:13px;font-weight:500;"
    f"border:1px solid {C_ERR};}}"
    f"QPushButton:hover{{background:{C_ERR_DIM};color:{C_ERR};}}"
    f"QPushButton:disabled{{color:{C_DISABLED};border-color:{C_DISABLED};}}"
)
STYLE_BTN_NEUTRAL = (
    f"QPushButton{{background:{C_SURFACE_2};color:{C_SUBTEXT};"
    f"padding:10px 20px;border-radius:8px;font-size:13px;font-weight:500;"
    f"border:1px solid {C_BORDER};}}"
    f"QPushButton:hover{{background:{C_SURFACE_3};color:{C_TEXT};"
    f"border-color:{C_BORDER_2};}}"
)


# ── Helpers ───────────────────────────────────────────────────────────────────

_STYLE_MSGBOX = (
    f"QMessageBox{{background:{C_SURFACE};border:1px solid {C_BORDER};}}"
    f"QMessageBox QLabel{{color:{C_TEXT};font-size:13px;background:transparent;"
    f"line-height:1.5;}}"
    f"QMessageBox QPushButton{{background:{C_ACCENT};color:{C_WHITE};"
    f"padding:7px 22px;border-radius:8px;border:none;font-size:12px;font-weight:600;}}"
    f"QMessageBox QPushButton:hover{{background:{C_ACCENT_HV};}}"
)

def _msgbox(parent, icono, titulo, texto, botones=QMessageBox.Ok):
    b = QMessageBox(parent)
    b.setIcon(icono)
    b.setWindowTitle(titulo)
    b.setText(texto)
    b.setStandardButtons(botones)
    b.setStyleSheet(_STYLE_MSGBOX)
    return b.exec_()

def _info(parent, titulo, texto):
    _msgbox(parent, QMessageBox.Information, titulo, texto)

def _warn(parent, titulo, texto):
    _msgbox(parent, QMessageBox.Warning, titulo, texto)

def _crit(parent, titulo, texto):
    _msgbox(parent, QMessageBox.Critical, titulo, texto)

def _ask(parent, titulo, texto):
    return _msgbox(parent, QMessageBox.Question, titulo, texto,
                   QMessageBox.Yes | QMessageBox.No)


def _sep(dark=False):
    f = QFrame()
    f.setFrameShape(QFrame.HLine)
    f.setFrameShadow(QFrame.Plain)
    col = C_BORDER if not dark else C_SURFACE_2
    f.setStyleSheet(
        f"color:{col};background:{col};max-height:1px;"
        f"margin:4px 0px;border:none;"
    )
    return f


def _tipo_geom(capa):
    t = QgsWkbTypes.geometryType(capa.wkbType())
    if t == QgsWkbTypes.LineGeometry:  return "linea"
    if t == QgsWkbTypes.PointGeometry: return "punto"
    return "poligono"


def _color_calidad(pct):
    return C_OK if pct >= 90 else C_WARN if pct >= 70 else C_ERR


_CORREO_LIDER_DEFAULT = "jhoinner.manrique@servinformacion.com"


def _config_local_get(attr, default=""):
    """Lee un valor de configuración desde .env (o config_local.py como fallback)."""
    try:
        if PLUGIN_DIR not in sys.path:
            sys.path.insert(0, PLUGIN_DIR)
        from .utils.env_loader import get
        return get(attr, default)
    except Exception:
        return default


def _make_header(titulo, subtitulo="", paso=None, total_pasos=3):
    """Cabecera de página — light theme profesional."""
    w = QWidget()
    w.setStyleSheet(
        f"background:{C_SURFACE};"
        f"border-bottom:1px solid {C_BORDER};"
    )
    lay = QVBoxLayout(w)
    lay.setContentsMargins(32, 20, 32, 16)
    lay.setSpacing(2)

    lbl_t = QLabel(titulo)
    lbl_t.setStyleSheet(
        f"color:{C_TEXT};font-size:18px;font-weight:700;"
        f"background:transparent;letter-spacing:-0.3px;"
    )
    lay.addWidget(lbl_t)

    if subtitulo:
        lbl_s = QLabel(subtitulo)
        lbl_s.setStyleSheet(
            f"color:{C_SUBTEXT};font-size:12px;background:transparent;"
        )
        lay.addWidget(lbl_s)

    return w


# .............................................................................
# DIÁLOGO — Configuración de correo
# .............................................................................

class _DialogoConfigCorreo(QDialog):
    """Diálogo para que cada profesional configure sus credenciales de correo."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurar correo")
        self.setMinimumWidth(500)
        self.setStyleSheet(f"background:{C_ROOT};color:{C_TEXT};")
        self.setWindowFlags(
            Qt.Dialog | Qt.WindowCloseButtonHint
        )

        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 24, 28, 20)
        lay.setSpacing(0)

        # Título
        lbl_titulo = QLabel("Configuración de correo")
        lbl_titulo.setStyleSheet(
            f"font-size:17px;font-weight:700;color:{C_TEXT};margin-bottom:6px;"
        )
        lay.addWidget(lbl_titulo)

        lbl_desc = QLabel(
            "Configura tu cuenta Gmail para enviar reportes de validación. "
            "Los datos se guardan solo en tu máquina."
        )
        lbl_desc.setStyleSheet(f"font-size:12px;color:{C_SUBTEXT};margin-bottom:18px;")
        lbl_desc.setWordWrap(True)
        lay.addWidget(lbl_desc)

        # Campos
        _INPUT_STYLE = (
            f"QLineEdit{{background:{C_SURFACE_2};border:none;"
            f"border-radius:9px;padding:10px 14px;font-size:13px;color:{C_TEXT};}}"
            f"QLineEdit:focus{{background:{C_SURFACE_3};}}"
        )
        _LABEL_STYLE = (
            f"font-size:11px;font-weight:600;color:{C_MUTED};"
            f"letter-spacing:0.5px;margin-top:12px;margin-bottom:4px;"
        )

        def _lbl(texto):
            l = QLabel(texto.upper())
            l.setStyleSheet(_LABEL_STYLE)
            return l

        # Correo
        lay.addWidget(_lbl("Tu correo Gmail"))
        self.txt_remitente = QLineEdit()
        self.txt_remitente.setPlaceholderText("tucorreo@gmail.com  o  tucorreo@empresa.com")
        self.txt_remitente.setStyleSheet(_INPUT_STYLE)
        lay.addWidget(self.txt_remitente)

        # Contraseña de app
        lay.addWidget(_lbl("Contraseña de aplicación Google"))
        self.txt_password = QLineEdit()
        self.txt_password.setPlaceholderText("xxxx xxxx xxxx xxxx  (16 caracteres con espacios)")
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_password.setStyleSheet(_INPUT_STYLE)
        lay.addWidget(self.txt_password)

        # Link de ayuda
        lbl_ayuda = QLabel(
            "Obtén tu contraseña en: "
            "<b>Cuenta Google > Seguridad > Verificación en 2 pasos "
            "> Contraseñas de aplicaciones</b>"
        )
        lbl_ayuda.setStyleSheet(
            f"font-size:11px;color:{C_MUTED};margin-top:6px;margin-bottom:4px;"
        )
        lbl_ayuda.setWordWrap(True)
        lay.addWidget(lbl_ayuda)

        # Separador visual
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(
            f"color:{C_BORDER};background:{C_BORDER};max-height:1px;margin:16px 0 4px 0;"
        )
        lay.addWidget(sep)

        # Destinatarios
        lay.addWidget(_lbl("Para: Reporte al líder"))
        self.txt_lider = QLineEdit()
        self.txt_lider.setPlaceholderText("lider@empresa.com")
        self.txt_lider.setStyleSheet(_INPUT_STYLE)
        lay.addWidget(self.txt_lider)

        lay.addWidget(_lbl("Para: Reporte a profesionals"))
        self.txt_profesionals = QLineEdit()
        self.txt_profesionals.setPlaceholderText("equipo@empresa.com  (varios separados por coma)")
        self.txt_profesionals.setStyleSheet(_INPUT_STYLE)
        lay.addWidget(self.txt_profesionals)

        lay.addSpacing(16)

        # Estado / feedback
        self._lbl_estado = QLabel("")
        self._lbl_estado.setWordWrap(True)
        self._lbl_estado.setStyleSheet(f"font-size:12px;color:{C_SUBTEXT};min-height:18px;")
        lay.addWidget(self._lbl_estado)

        lay.addSpacing(8)

        # Botones
        btn_row = QHBoxLayout()
        btn_probar = QPushButton("Probar conexion")
        btn_probar.setStyleSheet(STYLE_BTN_NEUTRAL)
        btn_probar.setToolTip("Verifica que el correo y la contraseña son correctos antes de guardar")
        btn_probar.clicked.connect(self._probar_conexion)
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setStyleSheet(STYLE_BTN_GHOST)
        btn_cancelar.clicked.connect(self.reject)
        btn_guardar = QPushButton("Guardar configuración")
        btn_guardar.setStyleSheet(STYLE_BTN_PRIMARY)
        btn_guardar.clicked.connect(self._guardar)
        btn_row.addWidget(btn_probar)
        btn_row.addStretch()
        btn_row.addWidget(btn_cancelar)
        btn_row.addSpacing(8)
        btn_row.addWidget(btn_guardar)
        lay.addLayout(btn_row)

        self._cargar_valores_actuales()

    def _cargar_valores_actuales(self):
        """Pre-rellena los campos con los valores del .env si ya existen."""
        self.txt_remitente.setText(_config_local_get("GMAIL_REMITENTE"))
        self.txt_password.setText(_config_local_get("GMAIL_APP_PASSWORD"))
        self.txt_lider.setText(_config_local_get("CORREO_REPORTE_COMPLETO", _CORREO_LIDER_DEFAULT))
        self.txt_profesionals.setText(_config_local_get("CORREO_REPORTE_RESUMIDO"))

    def _set_estado(self, texto, ok=None):
        if ok is True:
            color = C_OK
        elif ok is False:
            color = C_ERR
        else:
            color = C_SUBTEXT
        self._lbl_estado.setStyleSheet(
            f"font-size:12px;color:{color};"
            f"background:{C_OK_DIM if ok is True else (C_ERR_DIM if ok is False else 'transparent')};"
            f"padding:{('8px 10px;border-radius:6px;' if ok is not None else '0')};"
        )
        self._lbl_estado.setText(texto)

    def _probar_conexion(self):
        from .utils import gmail_sender
        remitente = self.txt_remitente.text().strip()
        password  = self.txt_password.text().strip()
        self._set_estado("Probando conexión...")
        QApplication.processEvents()
        try:
            ok, detalle = gmail_sender.probar_conexion(remitente=remitente, app_pwd=password)
            self._set_estado(detalle, ok=ok)
        except Exception:
            self._set_estado(
                "No se pudo probar la conexión. Verifica tu internet y las credenciales.",
                ok=False)

    def _guardar(self):
        remitente  = self.txt_remitente.text().strip()
        password   = self.txt_password.text().strip()
        lider      = self.txt_lider.text().strip()
        profesionals  = self.txt_profesionals.text().strip()

        if not remitente:
            self._set_estado("El correo no puede estar vacío.", ok=False)
            return
        if "@" not in remitente:
            self._set_estado("El correo no parece válido.", ok=False)
            return

        try:
            if PLUGIN_DIR not in sys.path:
                sys.path.insert(0, PLUGIN_DIR)
            from .utils.env_loader import save
            datos = {
                "GMAIL_REMITENTE":         remitente,
                "CORREO_REPORTE_COMPLETO": lider,
                "CORREO_REPORTE_RESUMIDO": profesionals,
            }
            if password:
                datos["GMAIL_APP_PASSWORD"] = password
            save(datos)
            self._set_estado("Configuracion guardada correctamente.", ok=True)
            QTimer.singleShot(1200, self.accept)
        except Exception as e:
            self._set_estado(f"Error al guardar: {e}", ok=False)


# .............................................................................
# PÁGINA 0 — Selección
# .............................................................................

class _PaginaSeleccion(QWidget):

    def __init__(self, iface, paises, parent=None):
        super().__init__(parent)
        self._iface = iface
        self.setStyleSheet(f"background:{C_ROOT};")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        lay.addWidget(_make_header(
            "Configuración del sistema",
            "País, tipo de validación y capas geoespaciales",
            paso=1,
        ))

        _scroll_body = QScrollArea()
        _scroll_body.setWidgetResizable(True)
        _scroll_body.setFrameShape(QFrame.NoFrame)
        _scroll_body.setStyleSheet(f"background:{C_ROOT};border:none;")

        body = QWidget()
        body.setStyleSheet(f"background:{C_ROOT};")
        bl = QVBoxLayout(body)
        bl.setContentsMargins(24, 20, 24, 24)
        bl.setSpacing(16)

        _STYLE_INPUT = (
            f"QLineEdit{{background:{C_SURFACE_2};border:none;"
            f"border-radius:10px;padding:11px 14px;font-size:13px;color:{C_TEXT};}}"
            f"QLineEdit:focus{{background:{C_SURFACE_3};"
            f"border:1px solid {C_ACCENT};outline:none;}}"
            f"QLineEdit:disabled{{background:{C_SURFACE_2};color:{C_MUTED};}}"
        )
        _STYLE_COMBO = (
            f"QComboBox{{background:{C_SURFACE_2};border:none;"
            f"border-radius:10px;padding:11px 14px;font-size:13px;color:{C_TEXT};}}"
            f"QComboBox:focus{{background:{C_SURFACE_3};border:1px solid {C_ACCENT};}}"
            f"QComboBox::drop-down{{border:none;width:28px;}}"
            f"QComboBox QAbstractItemView{{background:{C_SURFACE};border:1px solid {C_BORDER};"
            f"border-radius:8px;color:{C_TEXT};"
            f"selection-background-color:{C_ACCENT_DIM};outline:none;}}"
        )
        self._modo_proceso = "interno"

        # ──────────────────────────────────────────────────────────────────────
        # SECCIÓN 1 — ORDEN & COLABORADORES
        # ──────────────────────────────────────────────────────────────────────
        sec1_hdr = QHBoxLayout()
        sec1_hdr.setSpacing(10)
        lbl_sec1 = QLabel("Información de la orden")
        lbl_sec1.setStyleSheet(
            f"font-size:11px;font-weight:600;color:{C_MUTED};"
            f"letter-spacing:0.4px;background:transparent;border:none;"
        )
        _rem = _config_local_get("GMAIL_REMITENTE", "")
        self._lbl_correo_cfg = QLabel(_rem if _rem else "Sin correo configurado")
        self._lbl_correo_cfg.setStyleSheet(
            f"font-size:11px;color:{C_SUBTEXT if _rem else C_MUTED};background:transparent;border:none;"
        )
        btn_cfg_correo_top = QPushButton("Configurar correo")
        btn_cfg_correo_top.setCursor(Qt.PointingHandCursor)
        btn_cfg_correo_top.setStyleSheet(
            f"QPushButton{{background:{C_ACCENT_DIM};color:{C_ACCENT};"
            f"padding:5px 12px;border-radius:6px;font-size:11px;font-weight:600;"
            f"border:none;}}"
            f"QPushButton:hover{{background:{C_ACCENT};color:#0A1E1C;}}"
        )
        btn_cfg_correo_top.clicked.connect(self._abrir_config_correo)
        sec1_hdr.addWidget(lbl_sec1)
        sec1_hdr.addStretch()
        sec1_hdr.addWidget(self._lbl_correo_cfg)
        sec1_hdr.addWidget(btn_cfg_correo_top)
        bl.addLayout(sec1_hdr)

        # Orden interna
        lbl_tarea_cap = QLabel("ORDEN INTERNA")
        lbl_tarea_cap.setStyleSheet(
            f"font-size:10px;font-weight:700;color:{C_MUTED};letter-spacing:0.8px;"
            f"background:transparent;border:none;"
        )
        bl.addWidget(lbl_tarea_cap)
        tarea_row = QHBoxLayout()
        tarea_row.setSpacing(8)
        self.combo_tarea = QComboBox()
        self.combo_tarea.setEditable(False)
        self.combo_tarea.addItem("— Selecciona una orden —", None)
        self.combo_tarea.setStyleSheet(_STYLE_COMBO)
        btn_reload = QPushButton("↻")
        btn_reload.setFixedSize(40, 40)
        btn_reload.setToolTip("Recargar órdenes desde Google Sheets")
        btn_reload.setStyleSheet(
            f"QPushButton{{background:{C_SURFACE_2};color:{C_SUBTEXT};"
            f"border:none;border-radius:8px;font-size:16px;}}"
            f"QPushButton:hover{{background:{C_SURFACE_3};color:{C_ACCENT};}}"
        )
        btn_reload.clicked.connect(self._cargar_tareas_sheets)
        tarea_row.addWidget(self.combo_tarea, 1)
        tarea_row.addWidget(btn_reload)
        bl.addLayout(tarea_row)
        self.lbl_tarea_estado = QLabel("")
        self.lbl_tarea_estado.setStyleSheet(f"font-size:11px;color:{C_MUTED};background:transparent;border:none;")
        bl.addWidget(self.lbl_tarea_estado)
        self.combo_tarea.currentIndexChanged.connect(self._actualizar_btn_ver_entrega)

        # Colaboradores
        lbl_colab = QLabel("COLABORADORES")
        lbl_colab.setStyleSheet(
            f"font-size:10px;font-weight:700;color:{C_MUTED};letter-spacing:0.8px;"
            f"background:transparent;border:none;"
        )
        bl.addWidget(lbl_colab)
        self.txt_colaboradores = QLineEdit()
        self.txt_colaboradores.setPlaceholderText("colega1@empresa.com, colega2@empresa.com")
        self.txt_colaboradores.setToolTip("Correos adicionales que recibirán el reporte")
        self.txt_colaboradores.setStyleSheet(_STYLE_INPUT)
        bl.addWidget(self.txt_colaboradores)

        # ──────────────────────────────────────────────────────────────────────
        # SECCIÓN 2 — PAÍS + TIPO DE VALIDACIÓN (lado a lado)
        # ──────────────────────────────────────────────────────────────────────
        row_pais_tipo = QHBoxLayout()
        row_pais_tipo.setSpacing(24)

        # columna izquierda — PAÍS (sin caja exterior)
        col_pais = QWidget()
        col_pais.setStyleSheet("background:transparent;")
        cp_lay = QVBoxLayout(col_pais)
        cp_lay.setContentsMargins(0, 0, 0, 0)
        cp_lay.setSpacing(8)
        lbl_pais_hdr = QLabel("PAÍS")
        lbl_pais_hdr.setStyleSheet(
            f"font-size:10px;font-weight:700;color:{C_MUTED};"
            f"letter-spacing:0.8px;background:transparent;border:none;"
        )
        self.combo_pais = QComboBox()
        self.combo_pais.addItem("— Selecciona un país —", None)
        self.combo_pais.addItems(paises)
        self.combo_pais.setToolTip("Selecciona el país para aplicar las reglas de validación")
        self.combo_pais.setStyleSheet(_STYLE_COMBO)
        cp_lay.addWidget(lbl_pais_hdr)
        cp_lay.addWidget(self.combo_pais)
        cp_lay.addStretch()
        row_pais_tipo.addWidget(col_pais, 5)

        # columna derecha — TIPO DE VALIDACIÓN (sin caja exterior, radio-cards)
        col_tipo = QWidget()
        col_tipo.setStyleSheet("background:transparent;")
        ct_lay = QVBoxLayout(col_tipo)
        ct_lay.setContentsMargins(0, 0, 0, 0)
        ct_lay.setSpacing(8)
        lbl_tipo_hdr = QLabel("TIPO DE VALIDACIÓN")
        lbl_tipo_hdr.setStyleSheet(
            f"font-size:10px;font-weight:700;color:{C_MUTED};"
            f"letter-spacing:0.8px;background:transparent;border:none;"
        )
        ct_lay.addWidget(lbl_tipo_hdr)
        proceso_row = QHBoxLayout()
        proceso_row.setSpacing(10)
        self._proceso_labels = {}
        for clave, titulo, desc_corta in [
            ("interno", "Validación Interna",  "Revisión y corrección interna"),
            ("entrega", "Validación Entrega",  "Entrega oficial al líder"),
        ]:
            card = QFrame()
            card.setObjectName(f"card_proceso_{clave}")
            card.setMinimumHeight(72)
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            card.setCursor(Qt.PointingHandCursor)
            cl = QVBoxLayout(card)
            cl.setContentsMargins(14, 12, 14, 12)
            cl.setSpacing(4)
            lbl_tit = QLabel(titulo)
            lbl_tit.setStyleSheet(
                f"font-size:12px;font-weight:700;border:none;background:transparent;"
            )
            lbl_dc = QLabel(desc_corta)
            lbl_dc.setStyleSheet(
                f"font-size:11px;border:none;background:transparent;"
            )
            cl.addWidget(lbl_tit)
            cl.addWidget(lbl_dc)
            self._proceso_labels[clave] = (lbl_tit, lbl_dc)
            card.mousePressEvent = (lambda e, k=clave: self._set_proceso(k))
            if clave == "interno": self._btn_interno = card
            else: self._btn_entrega = card
            proceso_row.addWidget(card, 1)
        ct_lay.addLayout(proceso_row)
        row_pais_tipo.addWidget(col_tipo, 7)
        bl.addLayout(row_pais_tipo)
        self._actualizar_estilo_proceso()

        # ──────────────────────────────────────────────────────────────────────
        # SECCIÓN 2.5 — PRODUCTO
        # ──────────────────────────────────────────────────────────────────────
        self._modo_producto = "produccion"
        lbl_prod_hdr = QLabel("PRODUCTO")
        lbl_prod_hdr.setStyleSheet(
            f"font-size:10px;font-weight:700;color:{C_MUTED};"
            f"letter-spacing:0.8px;background:transparent;border:none;"
        )
        bl.addWidget(lbl_prod_hdr)
        prod_row = QHBoxLayout()
        prod_row.setSpacing(10)
        self._producto_labels = {}
        _prod_cards = {}
        for clave, titulo, desc_corta in [
            ("produccion",      "Producción",      "Capas de producción cartográfica"),
            ("entrega", "Entrega", "Capas de entrega"),
            ("geomarketing",    "Geomarketing",    "Capas de análisis de mercado"),
        ]:
            card = QFrame()
            card.setObjectName(f"card_prod_{clave}")
            card.setMinimumHeight(72)
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            card.setCursor(Qt.PointingHandCursor)
            cl = QVBoxLayout(card)
            cl.setContentsMargins(14, 12, 14, 12)
            cl.setSpacing(4)
            lbl_tit = QLabel(titulo)
            lbl_tit.setStyleSheet(
                f"font-size:12px;font-weight:700;border:none;background:transparent;"
            )
            lbl_dc = QLabel(desc_corta)
            lbl_dc.setStyleSheet(
                f"font-size:11px;border:none;background:transparent;"
            )
            cl.addWidget(lbl_tit)
            cl.addWidget(lbl_dc)
            self._producto_labels[clave] = (lbl_tit, lbl_dc)
            card.mousePressEvent = (lambda e, k=clave: self._set_producto(k))
            _prod_cards[clave] = card
            prod_row.addWidget(card, 1)
        self._btn_prod_produccion      = _prod_cards["produccion"]
        self._btn_prod_entrega = _prod_cards["entrega"]
        self._btn_prod_geomarketing    = _prod_cards["geomarketing"]
        bl.addLayout(prod_row)
        self._actualizar_estilo_producto()

        # ──────────────────────────────────────────────────────────────────────
        # SECCIÓN 3 — VALIDACIONES INDIVIDUALES (chips full-width)
        # ──────────────────────────────────────────────────────────────────────
        lbl_chips_hdr = QLabel("VALIDACIONES INDIVIDUALES")
        lbl_chips_hdr.setStyleSheet(
            f"font-size:10px;font-weight:700;color:{C_MUTED};letter-spacing:0.8px;"
            f"background:transparent;border:none;"
        )
        bl.addWidget(lbl_chips_hdr)
        chips_row = QHBoxLayout()
        chips_row.setSpacing(8)
        self._chips = {}
        for clave, etiq, tip in [
            ("estructura", "Estructura", "Verifica que los campos, tipos y longitudes coincidan con el esquema del país y producto."),
            ("atributos",  "Atributos",  "Valida campos, formatos, rangos y obligatoriedad."),
            ("topologia",  "Topología",  "Valida geometría: duplicados, superposiciones, huecos."),
            ("geocodigos", "Geocódigos", "Verifica que los geo-códigos existan y sean espacialmente correctos."),
        ]:
            btn = QPushButton(etiq)
            btn.setToolTip(tip)
            btn.setCheckable(True)
            btn.setChecked(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            self._chips[clave] = btn
            chips_row.addWidget(btn)
        self._actualizar_estilo_chips()
        for btn in self._chips.values():
            btn.clicked.connect(self._on_chip_toggle)

        # Chip Verificar Entrega — toggle con color propio (ámbar)
        self._btn_ver_entrega = QPushButton("Documentación")
        self._btn_ver_entrega.setToolTip(
            "Activa para incluir verificación de la carpeta Drive al validar"
        )
        self._btn_ver_entrega.setEnabled(False)
        self._btn_ver_entrega.setCheckable(True)
        self._btn_ver_entrega.setChecked(False)
        self._btn_ver_entrega.setCursor(Qt.PointingHandCursor)
        self._btn_ver_entrega.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._btn_ver_entrega.clicked.connect(self._on_ver_entrega_toggle)
        self._actualizar_estilo_ver_entrega()
        chips_row.addWidget(self._btn_ver_entrega)
        bl.addLayout(chips_row)

        # Panel desplegable — aparece cuando se activa "Verificar Entrega"
        self._panel_entrega = QWidget()
        self._panel_entrega.setVisible(False)
        self._panel_entrega.setStyleSheet(
            f"background:{C_SURFACE_2};border-radius:10px;border:1px solid {C_BORDER};"
        )
        _pe_lay = QVBoxLayout(self._panel_entrega)
        _pe_lay.setContentsMargins(16, 14, 16, 14)
        _pe_lay.setSpacing(10)

        lbl_pe_t = QLabel("Documentación de entrega")
        lbl_pe_t.setStyleSheet(
            f"font-size:12px;font-weight:700;color:{C_TEXT};"
            f"background:transparent;border:none;"
        )
        lbl_pe_sub = QLabel(
            "Ingresa el link de la carpeta Drive. "
            "Se verificará que contenga los documentos requeridos."
        )
        lbl_pe_sub.setWordWrap(True)
        lbl_pe_sub.setStyleSheet(
            f"font-size:11px;color:{C_MUTED};background:transparent;border:none;"
        )
        _pe_lay.addWidget(lbl_pe_t)
        _pe_lay.addWidget(lbl_pe_sub)

        self._txt_drive_url = QLineEdit()
        self._txt_drive_url.setPlaceholderText("Link de la carpeta Drive")
        self._txt_drive_url.setStyleSheet(
            f"QLineEdit{{background:{C_SURFACE};border:1px solid {C_BORDER};"
            f"border-radius:8px;padding:9px 12px;font-size:12px;color:{C_TEXT};}}"
            f"QLineEdit:focus{{border-color:{C_ACCENT};}}"
        )
        _pe_lay.addWidget(self._txt_drive_url)

        bl.addWidget(self._panel_entrega)

        # ──────────────────────────────────────────────────────────────────────
        # SECCIÓN 4 — CAPAS VECTORIALES
        # ──────────────────────────────────────────────────────────────────────
        hdr_capas = QHBoxLayout()
        lbl_capas_sec = QLabel("CAPAS VECTORIALES")
        lbl_capas_sec.setStyleSheet(
            f"font-size:10px;font-weight:700;color:{C_SUBTEXT};letter-spacing:0.8px;"
            f"background:transparent;border:none;"
        )
        self._lbl_count = QLabel("0 seleccionadas")
        self._lbl_count.setStyleSheet(
            f"font-size:11px;color:{C_MUTED};"
            f"background:{C_SURFACE_2};padding:2px 8px;border-radius:10px;border:none;"
        )
        self._btn_todas   = QPushButton("Todas")
        self._btn_ninguna = QPushButton("Ninguna")
        self._btn_carpeta = QPushButton("+ Carpeta")
        self._btn_todas.setToolTip("Seleccionar todas las capas")
        self._btn_ninguna.setToolTip("Deseleccionar todas las capas")
        self._btn_carpeta.setToolTip("Agregar archivos vectoriales desde una carpeta")
        _SM = (
            f"QPushButton{{background:transparent;color:{C_SUBTEXT};"
            f"padding:4px 10px;border-radius:6px;font-size:11px;"
            f"font-weight:500;border:1px solid {C_BORDER};}}"
            f"QPushButton:hover{{color:{C_TEXT};background:{C_SURFACE_2};"
            f"border-color:{C_BORDER_2};}}"
        )
        _SMP = (
            f"QPushButton{{background:{C_ACCENT};color:{C_WHITE};"
            f"padding:4px 12px;border-radius:6px;font-size:11px;"
            f"font-weight:600;border:none;}}"
            f"QPushButton:hover{{background:{C_ACCENT_HV};}}"
        )
        for b in (self._btn_todas, self._btn_ninguna): b.setStyleSheet(_SM)
        self._btn_carpeta.setStyleSheet(_SMP)
        self._btn_todas.clicked.connect(lambda: self._check_all(True))
        self._btn_ninguna.clicked.connect(lambda: self._check_all(False))
        self._btn_carpeta.clicked.connect(self._agregar_carpeta)
        hdr_capas.addWidget(lbl_capas_sec)
        hdr_capas.addSpacing(8)
        hdr_capas.addWidget(self._lbl_count)
        hdr_capas.addStretch()
        hdr_capas.addWidget(self._btn_todas)
        hdr_capas.addWidget(self._btn_ninguna)
        hdr_capas.addWidget(self._btn_carpeta)
        bl.addLayout(hdr_capas)

        # Panel manzana (referencia topología)
        self._panel_manzana = QFrame()
        self._panel_manzana.setObjectName("panel_manzana")
        self._panel_manzana.setStyleSheet(
            f"QFrame#panel_manzana{{background:{C_SURFACE_2};border:none;border-radius:10px;}}"
        )
        pm_lay = QHBoxLayout(self._panel_manzana)
        pm_lay.setContentsMargins(14, 10, 14, 10)
        pm_lay.setSpacing(10)
        lbl_manz = QLabel("Capa manzana:")
        lbl_manz.setStyleSheet(
            f"font-size:12px;color:{C_SUBTEXT};min-width:120px;"
            f"background:transparent;border:none;"
        )
        self.combo_manzana = QComboBox()
        self.combo_manzana.setStyleSheet(_STYLE_COMBO)
        self.combo_manzana.setToolTip("Capa de polígonos para validar que las líneas no crucen manzanas")
        pm_lay.addWidget(lbl_manz)
        pm_lay.addWidget(self.combo_manzana, 1)
        self._panel_manzana.setVisible(True)
        bl.addWidget(self._panel_manzana)

        # Panel georef (capas de referencia geocódigos)
        self._panel_georef = QFrame()
        self._panel_georef.setObjectName("panel_georef")
        self._panel_georef.setStyleSheet(
            f"QFrame#panel_georef{{background:{C_SURFACE_2};border:none;border-radius:10px;}}"
        )
        pgr_lay = QVBoxLayout(self._panel_georef)
        pgr_lay.setContentsMargins(14, 10, 14, 10)
        pgr_lay.setSpacing(6)
        lbl_gr = QLabel("Capas de referencia geocódigos")
        lbl_gr.setStyleSheet(
            f"font-size:12px;font-weight:600;color:{C_SUBTEXT};"
            f"background:transparent;border:none;"
        )
        lbl_gr_info = QLabel("Solo como referencia — no aparecen en el reporte")
        lbl_gr_info.setStyleSheet(
            f"font-size:11px;color:{C_MUTED};"
            f"background:transparent;border:none;"
        )
        pgr_lay.addWidget(lbl_gr)
        pgr_lay.addWidget(lbl_gr_info)
        self.lista_georef = QListWidget()
        self.lista_georef.setSelectionMode(QListWidget.NoSelection)
        self.lista_georef.setMaximumHeight(100)
        self.lista_georef.setStyleSheet(
            f"QListWidget{{background:{C_SURFACE_2};border:none;"
            f"border-radius:6px;font-size:12px;padding:4px;color:{C_TEXT};}}"
            f"QListWidget::item{{padding:5px 8px;border-radius:4px;margin:1px;}}"
            f"QListWidget::item:hover{{background:{C_BORDER};}}"
        )
        pgr_lay.addWidget(self.lista_georef)
        self._panel_georef.setVisible(True)
        bl.addWidget(self._panel_georef)

        self.txt_buscar_capa = QLineEdit()
        self.txt_buscar_capa.setPlaceholderText("Buscar capa...")
        self.txt_buscar_capa.setStyleSheet(_STYLE_INPUT)
        self.txt_buscar_capa.setClearButtonEnabled(True)
        self.txt_buscar_capa.textChanged.connect(self._filtrar_capas)
        bl.addWidget(self.txt_buscar_capa)

        self.lista = QListWidget()
        self.lista.setSelectionMode(QListWidget.NoSelection)
        self.lista.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.lista.setMinimumHeight(180)
        self.lista.setStyleSheet(
            f"QListWidget{{background:{C_SURFACE_2};border:none;"
            f"border-radius:10px;outline:none;padding:4px;color:{C_TEXT};}}"
            f"QListWidget::item{{border-radius:6px;padding:4px 6px;"
            f"margin:1px 2px;color:{C_TEXT};font-size:13px;}}"
            f"QListWidget::item:hover{{background:{C_SURFACE_3};}}"
        )
        self.lista.itemChanged.connect(self._actualizar_count)
        bl.addWidget(self.lista)

        self.lbl_estado = QLabel("")
        self.lbl_estado.setStyleSheet(
            f"font-size:11px;color:{C_MUTED};margin-top:4px;"
            f"background:transparent;border:none;"
        )
        bl.addWidget(self.lbl_estado)

        # ── Comentarios del validador ─────────────────────────────────────────────
        lbl_com_t = QLabel("Comentarios")
        lbl_com_t.setStyleSheet(
            f"font-size:12px;font-weight:700;color:{C_TEXT};"
            f"background:transparent;border:none;margin-top:10px;"
        )
        lbl_com_sub = QLabel(
            "Observaciones o notas para el reporte de trazabilidad (opcional)."
        )
        lbl_com_sub.setWordWrap(True)
        lbl_com_sub.setStyleSheet(
            f"font-size:11px;color:{C_MUTED};background:transparent;border:none;"
        )
        self.txt_comentario = QTextEdit()
        self.txt_comentario.setPlaceholderText(
            "Ej: Se encontraron errores en el campo tipo_via de la capa calles. "
            "Pendiente corrección en próxima entrega..."
        )
        self.txt_comentario.setFixedHeight(80)
        self.txt_comentario.setStyleSheet(
            f"QTextEdit{{background:{C_SURFACE_2};border:1px solid {C_BORDER};"
            f"border-radius:8px;padding:8px 10px;font-size:12px;color:{C_TEXT};}}"
            f"QTextEdit:focus{{border-color:{C_ACCENT};}}"
        )
        bl.addWidget(lbl_com_t)
        bl.addWidget(lbl_com_sub)
        bl.addWidget(self.txt_comentario)

        body.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        _scroll_body.setWidget(body)
        lay.addWidget(_scroll_body, 1)
        self._cargar_capas_proyecto()
        self._poblar_combo_manzana()
        self._poblar_lista_georef()
        self._actualizar_count()

    def _cargar_capas_proyecto(self):
        todas = sorted(
            [c for c in QgsProject.instance().mapLayers().values()
             if isinstance(c, QgsVectorLayer)],
            key=lambda c: c.name(),
        )
        activa = self._iface.activeLayer() \
            if isinstance(self._iface.activeLayer(), QgsVectorLayer) else None
        for capa in todas:
            self._agregar_item(capa, checked=(capa == activa))

    _GEOM_CFG = {
        "linea":    ("~", "LÍNEAS",    C_GEOM_LINE,  C_GEOM_LINE_DIM),
        "punto":    ("-", "PUNTOS",    C_GEOM_POINT, C_GEOM_POINT_DIM),
        "poligono": ("■", "POLÍGONOS", C_GEOM_POLY,  C_GEOM_POLY_DIM),
    }

    def _agregar_item(self, capa, checked=False):
        tg = _tipo_geom(capa)
        icono, etiq, col, col_dim = self._GEOM_CFG.get(
            tg, ("-<", "CAPA", C_MUTED, C_SURFACE_2))
        n = capa.featureCount()

        item = QListWidgetItem()
        item.setData(Qt.UserRole, capa)
        item.setSizeHint(QSize(0, 52))
        self.lista.addItem(item)

        # Widget personalizado — mejor visual que texto plano
        w = QWidget()
        w.setAttribute(Qt.WA_TranslucentBackground)
        wl = QHBoxLayout(w)
        wl.setContentsMargins(10, 6, 14, 6)
        wl.setSpacing(10)

        # Checkbox estilizado
        chk = QCheckBox()
        chk.setChecked(checked)
        chk.setStyleSheet(
            f"QCheckBox::indicator{{width:18px;height:18px;border-radius:5px;"
            f"border:1.5px solid {C_BORDER_2};background:{C_SURFACE_2};}}"
            f"QCheckBox::indicator:checked{{background:{C_ACCENT};"
            f"border-color:{C_ACCENT};}}"
            f"QCheckBox::indicator:hover{{border-color:{C_ACCENT};}}"
        )
        chk.stateChanged.connect(self._actualizar_count)

        # Icono de geometría
        lbl_icono = QLabel(icono)
        lbl_icono.setStyleSheet(
            f"font-size:16px;color:{col};background:transparent;"
            f"min-width:20px;"
        )

        # Nombre de la capa
        lbl_nombre = QLabel(capa.name())
        lbl_nombre.setStyleSheet(
            f"font-size:13px;font-weight:500;color:{C_TEXT};"
            f"background:transparent;"
        )

        # Badge de tipo de geometría
        lbl_badge = QLabel(etiq)
        lbl_badge.setStyleSheet(
            f"background:{col_dim};color:{col};"
            f"padding:2px 8px;border-radius:4px;"
            f"font-size:10px;font-weight:700;letter-spacing:0.4px;"
        )

        # Conteo de features
        lbl_count = QLabel(f"{n:,}")
        lbl_count.setStyleSheet(
            f"font-size:11px;color:{C_MUTED};background:transparent;"
            f"min-width:60px;text-align:right;"
        )
        lbl_count.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        wl.addWidget(chk)
        wl.addWidget(lbl_icono)
        wl.addWidget(lbl_nombre, 1)
        wl.addWidget(lbl_badge)
        wl.addWidget(lbl_count)

        # Guardar referencia al checkbox en el item
        item.setData(Qt.UserRole + 1, chk)
        self.lista.setItemWidget(item, w)

    def capas_seleccionadas(self):
        resultado = []
        for i in range(self.lista.count()):
            item = self.lista.item(i)
            chk = item.data(Qt.UserRole + 1)
            if chk and chk.isChecked():
                resultado.append(item.data(Qt.UserRole))
            elif chk is None and item.checkState() == Qt.Checked:
                resultado.append(item.data(Qt.UserRole))
        return resultado

    def _rutas_ya_cargadas(self):
        rutas = set()
        for i in range(self.lista.count()):
            capa = self.lista.item(i).data(Qt.UserRole)
            if capa:
                src = capa.source().split("|")[0]
                rutas.add(os.path.normcase(os.path.abspath(src)))
        return rutas

    def _agregar_carpeta(self):
        carpeta = QFileDialog.getExistingDirectory(
            self, "Seleccionar carpeta con archivos vectoriales",
            os.path.expanduser("~"), QFileDialog.ShowDirsOnly,
        )
        if not carpeta:
            return

        # Feedback inmediato — evita que parezca que QGIS colgó
        self.lbl_estado.setStyleSheet(f"font-size:12px;color:{C_SUBTEXT};")
        self.lbl_estado.setText("Escaneando carpeta...")
        QApplication.processEvents()

        ya = self._rutas_ya_cargadas()
        agr = omit = err = 0

        # Recolectar rutas primero (sin cargar capas) — rápido
        rutas_candidatas = []
        for raiz, _, archivos in os.walk(carpeta):
            for archivo in sorted(archivos):
                if os.path.splitext(archivo)[1].lower() not in _EXTENSIONES_VECTOR:
                    continue
                ruta_abs = os.path.normcase(os.path.abspath(os.path.join(raiz, archivo)))
                if ruta_abs in ya:
                    omit += 1
                else:
                    rutas_candidatas.append((ruta_abs, os.path.join(raiz, archivo),
                                             os.path.splitext(archivo)[0]))

        # Cargar capas de a una actualizando la UI cada 5 archivos
        for idx, (ruta_abs, ruta_real, nombre) in enumerate(rutas_candidatas):
            capa = QgsVectorLayer(ruta_real, nombre, "ogr")
            if not capa.isValid():
                err += 1
            else:
                self._agregar_item(capa, checked=True)
                ya.add(ruta_abs)
                agr += 1
            # Actualizar UI cada 5 archivos para que QGIS no se congele
            if idx % 5 == 0:
                self.lbl_estado.setText(f"Cargando... {idx + 1}/{len(rutas_candidatas)}")
                QApplication.processEvents()

        partes = []
        if agr:  partes.append(f"✓ {agr} archivo(s) agregado(s)")
        if omit: partes.append(f"{omit} ya en la lista")
        if err:  partes.append(f"{err} no válidos")
        if not partes: partes.append("No se encontraron archivos vectoriales")
        color = C_OK if agr else C_WARN
        self.lbl_estado.setStyleSheet(f"font-size:12px;color:{color};")
        self.lbl_estado.setText("  ".join(partes))
        self._actualizar_count()

    def _check_all(self, estado):
        for i in range(self.lista.count()):
            item = self.lista.item(i)
            chk = item.data(Qt.UserRole + 1)
            if chk:
                chk.setChecked(estado)
            else:
                item.setCheckState(Qt.Checked if estado else Qt.Unchecked)

    def _actualizar_count(self):
        n = len(self.capas_seleccionadas())
        self._lbl_count.setText(f"{n} seleccionada{'s' if n != 1 else ''}")

    def pais(self):
        return "" if self.combo_pais.currentIndex() == 0 else self.combo_pais.currentText()

    def pais_seleccionado(self):
        return self.combo_pais.currentIndex() > 0

    def _poblar_combo_manzana(self):
        self.combo_manzana.clear()
        self.combo_manzana.addItem("— Sin capa de manzana —", None)
        auto_idx = 0
        for capa in sorted(QgsProject.instance().mapLayers().values(),
                           key=lambda c: c.name()):
            if isinstance(capa, QgsVectorLayer) and _tipo_geom(capa) == "poligono":
                self.combo_manzana.addItem(capa.name(), capa)
                if "manzana" in capa.name().lower() and auto_idx == 0:
                    auto_idx = self.combo_manzana.count() - 1
        if auto_idx:
            self.combo_manzana.setCurrentIndex(auto_idx)

    def _poblar_lista_georef(self):
        self.lista_georef.clear()
        for capa in sorted(QgsProject.instance().mapLayers().values(),
                           key=lambda c: c.name()):
            if isinstance(capa, QgsVectorLayer) and _tipo_geom(capa) == "poligono":
                item = QListWidgetItem(f"  {capa.name()}")
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Unchecked)
                item.setData(Qt.UserRole, capa)
                item.setSizeHint(QSize(0, 30))
                self.lista_georef.addItem(item)

    def capas_referencia_geocodigos(self):
        return [
            self.lista_georef.item(i).data(Qt.UserRole)
            for i in range(self.lista_georef.count())
            if self.lista_georef.item(i).checkState() == Qt.Checked
        ]

    def capa_manzana_ref(self):
        return self.combo_manzana.currentData()

    def _set_proceso(self, modo):
        self._modo_proceso = modo
        if modo == "entrega":
            # Validación Final requiere los 3 tipos — forzar y bloquear chips
            for btn in self._chips.values():
                btn.setChecked(True)
                btn.setEnabled(False)
            self._panel_manzana.setVisible(True)
            self._panel_georef.setVisible(True)
        else:
            for btn in self._chips.values():
                btn.setEnabled(True)
            self._panel_manzana.setVisible(self._chips["topologia"].isChecked())
            self._panel_georef.setVisible(self._chips["geocodigos"].isChecked())
        self._actualizar_estilo_proceso()
        self._actualizar_estilo_chips()
        # Actualizar texto del botón validar en el diálogo padre
        parent = self.parent()
        if parent and hasattr(parent, "_btn_validar"):
            modo_v = self.modo_validacion()
            partes = []
            if "estructura" in modo_v: partes.append("Estructura")
            if "atributos"  in modo_v: partes.append("Atributos")
            if "topologia"  in modo_v: partes.append("Topología")
            if "geocodigos" in modo_v: partes.append("Geocódigos")
            parent._btn_validar.setText(
                f"Validar  {' + '.join(partes)}" if partes else "Validar"
            )

    def _actualizar_estilo_proceso(self):
        _COLOR_MAP = {
            "interno": (C_INTERNO, C_INTERNO_DIM),
            "entrega": (C_ENTREGA, C_ENTREGA_DIM),
        }
        for card, clave in [(self._btn_interno, "interno"),
                            (self._btn_entrega, "entrega")]:
            activo = self._modo_proceso == clave
            col, dim = _COLOR_MAP[clave]
            lbl_tit, lbl_dc = self._proceso_labels[clave]
            if activo:
                card.setStyleSheet(
                    f"QFrame#{card.objectName()}{{background:qlineargradient("
                    f"x1:0,y1:0,x2:0,y2:1,"
                    f"stop:0 {dim},stop:1 {C_SURFACE_2});"
                    f"border-radius:10px;border:1.5px solid {col};}}"
                )
                lbl_tit.setStyleSheet(
                    f"font-size:12px;font-weight:700;color:{C_TEXT};"
                    f"border:none;background:transparent;"
                )
                lbl_dc.setStyleSheet(
                    f"font-size:11px;color:{C_SUBTEXT};"
                    f"border:none;background:transparent;"
                )
            else:
                card.setStyleSheet(
                    f"QFrame#{card.objectName()}{{background:{C_SURFACE_2};"
                    f"border-radius:10px;border:none;}}"
                    f"QFrame#{card.objectName()}:hover{{background:{C_SURFACE_3};"
                    f"border:1px solid {C_BORDER_2};}}"
                )
                lbl_tit.setStyleSheet(
                    f"font-size:12px;font-weight:700;color:{C_MUTED};"
                    f"border:none;background:transparent;"
                )
                lbl_dc.setStyleSheet(
                    f"font-size:11px;color:{C_MUTED};"
                    f"border:none;background:transparent;"
                )

    def producto(self):
        """Retorna 'produccion', 'entrega' o 'geomarketing'."""
        return self._modo_producto

    def _set_producto(self, clave):
        self._modo_producto = clave
        self._actualizar_estilo_producto()

    def _actualizar_estilo_producto(self):
        _COLOR_MAP = {
            "produccion":      (C_PROD,   C_PROD_DIM),
            "entrega":         (C_GEO,    C_GEO_DIM),
            "geomarketing":    (C_GEOMKT, C_GEOMKT_DIM),
        }
        _CARDS = {
            "produccion":      self._btn_prod_produccion,
            "entrega":         self._btn_prod_entrega,
            "geomarketing":    self._btn_prod_geomarketing,
        }
        for clave, card in _CARDS.items():
            activo = (self._modo_producto == clave)
            col, dim = _COLOR_MAP[clave]
            lbl_tit, lbl_dc = self._producto_labels[clave]
            if activo:
                card.setStyleSheet(
                    f"QFrame#{card.objectName()}{{background:qlineargradient("
                    f"x1:0,y1:0,x2:0,y2:1,"
                    f"stop:0 {dim},stop:1 {C_SURFACE_2});"
                    f"border-radius:10px;border:1.5px solid {col};}}"
                )
                lbl_tit.setStyleSheet(
                    f"font-size:12px;font-weight:700;color:{C_TEXT};"
                    f"border:none;background:transparent;"
                )
                lbl_dc.setStyleSheet(
                    f"font-size:11px;color:{C_SUBTEXT};"
                    f"border:none;background:transparent;"
                )
            else:
                card.setStyleSheet(
                    f"QFrame#{card.objectName()}{{background:{C_SURFACE_2};"
                    f"border-radius:10px;border:none;}}"
                    f"QFrame#{card.objectName()}:hover{{background:{C_SURFACE_3};"
                    f"border:1px solid {C_BORDER_2};}}"
                )
                lbl_tit.setStyleSheet(
                    f"font-size:12px;font-weight:700;color:{C_MUTED};"
                    f"border:none;background:transparent;"
                )
                lbl_dc.setStyleSheet(
                    f"font-size:11px;color:{C_MUTED};"
                    f"border:none;background:transparent;"
                )

    def _filtrar_capas(self, texto: str):
        """Filtra la lista de capas según el texto de búsqueda."""
        texto = texto.strip().lower()
        for i in range(self.lista.count()):
            item = self.lista.item(i)
            capa = item.data(Qt.UserRole)
            nombre = capa.name().lower() if capa else ""
            item.setHidden(bool(texto) and texto not in nombre)

    def _cargar_tareas_sheets(self):
        """Carga las órdenes desde Google Sheets y llena el combo."""
        try:
            from .utils.sheets_loader import cargar_tareas, limpiar_cache_tareas
            limpiar_cache_tareas()
            tareas = cargar_tareas()
            seleccion_actual = self.combo_tarea.currentText()
            self.combo_tarea.clear()
            self.combo_tarea.addItem("— Selecciona una orden —", None)
            for t in tareas:
                self.combo_tarea.addItem(t["orden"], t)
            # Restaurar selección previa si sigue en la lista
            idx = self.combo_tarea.findText(seleccion_actual)
            if idx >= 0:
                self.combo_tarea.setCurrentIndex(idx)
            n = len(tareas)
            color = C_OK if tareas else C_WARN
            texto = (
                f"✓ {n} orden{'es' if n != 1 else ''} cargada{'s' if n != 1 else ''} desde Sheets"
                if tareas else "Sin órdenes en el Sheets"
            )
            self.lbl_tarea_estado.setStyleSheet(f"font-size:11px;color:{color};")
            self.lbl_tarea_estado.setText(texto)
        except Exception as e:
            self.lbl_tarea_estado.setStyleSheet(f"font-size:11px;color:{C_ERR};")
            self.lbl_tarea_estado.setText("Error al cargar ordenes")
            _crit(self, "Error al cargar órdenes desde Sheets",
                  f"Detalle del error:\n\n{e}\n\n"
                  f"Verifica que:\n"
                  f"1. La cuenta de servicios tiene acceso al Sheets\n"
                  f"2. Las credenciales en .env son correctas\n"
                  f"3. Hay conexión a internet")

    def orden_seleccionada(self) -> str:
        """Retorna el nombre de la orden seleccionada (vacío si no se seleccionó ninguna)."""
        data = self.combo_tarea.currentData()
        if data is None:
            return ""
        return self.combo_tarea.currentText().strip()

    def orden_num_seleccionada(self) -> str:
        """Retorna el número de tarea (ej. 'INT 035-26') de la orden seleccionada."""
        data = self.combo_tarea.currentData()
        if not data or not isinstance(data, dict):
            return ""
        num = data.get("num_tarea", "").strip()
        if num:
            return num
        # Fallback: extraer el código del inicio del nombre completo
        import re
        m = re.match(r'^((?:INT|OT)\s*\d{3}-\d{2})', data.get("orden", ""), re.IGNORECASE)
        return m.group(1).upper() if m else ""

    def responsable_seleccionado(self) -> str:
        """Retorna el nombre del responsable de la orden desde Sheets."""
        idx = self.combo_tarea.currentIndex()
        if idx >= 0:
            data = self.combo_tarea.itemData(idx)
            if data and isinstance(data, dict):
                return data.get("responsable", "")
        return ""

    def colaboradores(self) -> str:
        """Retorna los colaboradores adicionales (correos separados por coma)."""
        return self.txt_colaboradores.text().strip()

    def _abrir_config_correo(self):
        dlg = _DialogoConfigCorreo(self)
        if dlg.exec_() == _DialogoConfigCorreo.Accepted:
            remitente = _config_local_get("GMAIL_REMITENTE")
            self._lbl_correo_cfg.setText(remitente if remitente else "Sin correo configurado")
            self._lbl_correo_cfg.setStyleSheet(
                f"font-size:11px;color:{C_SUBTEXT if remitente else C_MUTED};"
                f"background:transparent;"
            )

    def modo_proceso(self):
        return self._modo_proceso

    def _on_chip_toggle(self):
        # Garantiza que al menos un chip quede activo
        if not any(b.isChecked() for b in self._chips.values()):
            self.sender().setChecked(True)
        self._actualizar_estilo_chips()
        self._panel_manzana.setVisible(self._chips["topologia"].isChecked())
        self._panel_georef.setVisible(self._chips["geocodigos"].isChecked())

    _CHIP_COLOR = {
        "estructura": (C_PROD,     "#86EFAC",    C_PROD_DIM,    "#052E16"),
        "atributos":  (C_ACCENT,   C_ACCENT_HV,  C_ACCENT_DIM,  "#0A1E1C"),
        "topologia":  ("#A78BFA",  "#C4B5FD",    "#170D33",     "#0F0820"),
        "geocodigos": ("#38BDF8",  "#7DD3FC",    "#0C2233",     "#061422"),
    }

    def _actualizar_estilo_chips(self):
        STYLE_OFF = (
            f"QPushButton{{background:{C_SURFACE_2};color:{C_MUTED};"
            f"padding:11px 20px;border-radius:10px;font-size:13px;"
            f"font-weight:500;border:none;min-height:42px;}}"
            f"QPushButton:hover{{color:{C_TEXT};background:{C_SURFACE_3};}}"
            f"QPushButton:disabled{{color:{C_SURFACE_3};background:{C_SURFACE_2};}}"
        )
        for clave, btn in self._chips.items():
            if btn.isChecked():
                col, hv, dim, txt = self._CHIP_COLOR.get(clave, (C_ACCENT, C_ACCENT_HV, C_ACCENT_DIM, "#0A1E1C"))
                btn.setStyleSheet(
                    f"QPushButton{{background:{col};color:{txt};"
                    f"padding:11px 20px;border-radius:10px;font-size:13px;"
                    f"font-weight:700;border:none;min-height:42px;}}"
                    f"QPushButton:hover{{background:{hv};}}"
                    f"QPushButton:disabled{{background:{dim};color:{col};}}"
                )
            else:
                btn.setStyleSheet(STYLE_OFF)

    def _on_ver_entrega_toggle(self):
        activo = self._btn_ver_entrega.isChecked()
        self._panel_entrega.setVisible(activo)
        self._actualizar_estilo_ver_entrega()

    def _actualizar_estilo_ver_entrega(self):
        if self._btn_ver_entrega.isChecked():
            self._btn_ver_entrega.setStyleSheet(
                "QPushButton{background:#92400E;color:#FCD34D;"
                "padding:11px 20px;border-radius:10px;font-size:13px;"
                "font-weight:700;border:none;min-height:42px;}"
                "QPushButton:hover{background:#B45309;color:#FEF3C7;}"
                "QPushButton:disabled{background:#1C1004;color:#92400E;}"
            )
        else:
            self._btn_ver_entrega.setStyleSheet(
                f"QPushButton{{background:{C_SURFACE_2};color:{C_MUTED};"
                f"padding:11px 20px;border-radius:10px;font-size:13px;"
                f"font-weight:500;border:none;min-height:42px;}}"
                f"QPushButton:enabled{{color:{C_TEXT};}}"
                f"QPushButton:hover{{color:{C_TEXT};background:{C_SURFACE_3};}}"
                f"QPushButton:disabled{{color:{C_SURFACE_3};background:{C_SURFACE_2};}}"
            )

    def _actualizar_btn_ver_entrega(self):
        ot = self.orden_seleccionada()
        habilitado = bool(ot and ot.strip())
        self._btn_ver_entrega.setEnabled(habilitado)
        if not habilitado:
            self._btn_ver_entrega.setChecked(False)
            self._panel_entrega.setVisible(False)
            self._actualizar_estilo_ver_entrega()

    def modo_validacion(self):
        modos = set()
        if self._chips["estructura"].isChecked():  modos.add("estructura")
        if self._chips["atributos"].isChecked():   modos.add("atributos")
        if self._chips["topologia"].isChecked():   modos.add("topologia")
        if self._chips["geocodigos"].isChecked():  modos.add("geocodigos")
        return modos if modos else {"atributos"}

    def topologia_activa(self):
        return self._chips["topologia"].isChecked()

    def email_config(self):
        _fecha = datetime.now().strftime("%d/%m/%Y")
        return {
            "modo_proceso":  self._modo_proceso,
            "tarea":         self.orden_num_seleccionada() or self.orden_seleccionada(),
            "responsable":   self.responsable_seleccionado(),
            "colaboradores": self.colaboradores(),
            "enviar_c": self._modo_proceso == "entrega",
            "para_c":   _config_local_get("CORREO_REPORTE_COMPLETO", _CORREO_LIDER_DEFAULT),
            "asunto_c": f"[Entrega Oficial] {_fecha}",
            "enviar_r": True,
            "para_r":   _config_local_get("CORREO_REPORTE_RESUMIDO", ""),
            "asunto_r": f"Validación Interna — {_fecha}",
        }


# .............................................................................
# PÁGINA 1 — Progreso
# .............................................................................

class _PaginaProgreso(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._cancelado      = False
        self._t_inicio_ms    = 0
        self._chips_activos  = set()
        self._etapa_actual   = None
        self.setStyleSheet(f"background:{C_ROOT};")

        self._timer_tiempo = QTimer(self)
        self._timer_tiempo.timeout.connect(self._actualizar_tiempo)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self._header = _make_header("Validando capas...", paso=2)
        lay.addWidget(self._header)

        body = QWidget()
        body.setStyleSheet(f"background:{C_ROOT};")
        bl = QVBoxLayout(body)
        bl.setContentsMargins(28, 24, 28, 16)
        bl.setSpacing(16)

        # ── PROGRESO GENERAL (borderless) ─────────────────────────────────────
        row_gen = QHBoxLayout()
        lbl_gen_cap = QLabel("PROGRESO GENERAL")
        lbl_gen_cap.setStyleSheet(
            f"font-weight:700;font-size:10px;color:{C_MUTED};letter-spacing:0.8px;"
        )
        self.lbl_gen_pct = QLabel("0%")
        self.lbl_gen_pct.setStyleSheet(
            f"font-size:34px;font-weight:800;color:{C_ACCENT};letter-spacing:-1px;"
        )
        row_gen.addWidget(lbl_gen_cap, 1)
        row_gen.addWidget(self.lbl_gen_pct)
        bl.addLayout(row_gen)

        self.bar_general = self._make_bar(C_ACCENT, 10)
        bl.addWidget(self.bar_general)

        row_meta = QHBoxLayout()
        self.lbl_gen_sub = QLabel("Iniciando...")
        self.lbl_gen_sub.setStyleSheet(f"font-size:12px;color:{C_SUBTEXT};")
        self.lbl_tiempo = QLabel("")
        self.lbl_tiempo.setStyleSheet(f"font-size:12px;color:{C_MUTED};")
        self.lbl_eta = QLabel("")
        self.lbl_eta.setStyleSheet(f"font-size:12px;color:{C_MUTED};font-style:italic;")
        row_meta.addWidget(self.lbl_gen_sub)
        row_meta.addStretch()
        row_meta.addWidget(self.lbl_tiempo)
        row_meta.addSpacing(16)
        row_meta.addWidget(self.lbl_eta)
        bl.addLayout(row_meta)

        # ── CAPA ACTUAL + ETAPAS (lado a lado) ────────────────────────────────
        mid_row = QHBoxLayout()
        mid_row.setSpacing(16)

        card_capa = self._make_card()
        cc = QVBoxLayout(card_capa)
        cc.setContentsMargins(20, 16, 20, 16)
        cc.setSpacing(8)

        lbl_capa_cap = QLabel("CAPA ACTUAL")
        lbl_capa_cap.setStyleSheet(
            f"font-size:10px;font-weight:700;color:{C_MUTED};"
            f"letter-spacing:0.8px;background:transparent;border:none;"
        )
        self.lbl_capa = QLabel("Preparando...")
        self.lbl_capa.setStyleSheet(
            f"font-weight:700;font-size:15px;color:{C_TEXT};"
            f"background:transparent;border:none;"
        )
        cc.addWidget(lbl_capa_cap)
        cc.addWidget(self.lbl_capa)

        row_fase = QHBoxLayout()
        self.lbl_fase = QLabel("-")
        self.lbl_fase.setStyleSheet(
            f"font-size:12px;color:{C_SUBTEXT};background:transparent;border:none;"
        )
        self.lbl_fase_pct = QLabel("")
        self.lbl_fase_pct.setStyleSheet(
            f"font-size:13px;font-weight:700;color:{C_OK};"
            f"background:transparent;border:none;"
        )
        row_fase.addWidget(self.lbl_fase)
        row_fase.addStretch()
        row_fase.addWidget(self.lbl_fase_pct)
        cc.addLayout(row_fase)

        self.bar_fase = self._make_bar(C_OK, 4)
        cc.addWidget(self.bar_fase)

        self.lbl_stats = QLabel("")
        self.lbl_stats.setStyleSheet(
            f"font-size:12px;color:{C_MUTED};font-family:monospace;"
            f"background:transparent;border:none;"
        )
        cc.addWidget(self.lbl_stats)
        mid_row.addWidget(card_capa, 6)

        # ETAPAS — columna derecha, sin borde
        col_etapas = QWidget()
        col_etapas.setStyleSheet("background:transparent;")
        et_lay = QVBoxLayout(col_etapas)
        et_lay.setContentsMargins(4, 0, 0, 0)
        et_lay.setSpacing(6)

        lbl_etapas_cap = QLabel("ETAPAS")
        lbl_etapas_cap.setStyleSheet(
            f"font-size:10px;font-weight:700;color:{C_MUTED};letter-spacing:0.8px;"
        )
        et_lay.addWidget(lbl_etapas_cap)

        self._etapas = {}
        for idx, (clave, nombre) in enumerate([
            ("preparando", "Preparando"),
            ("estructura", "Estructura"),
            ("atributos",  "Atributos"),
            ("topologia",  "Topología"),
            ("geocodigos", "Geocódigos"),
        ], start=1):
            row_et = QHBoxLayout()
            row_et.setSpacing(10)
            lbl_num = QLabel(str(idx))
            lbl_num.setFixedSize(24, 24)
            lbl_num.setAlignment(Qt.AlignCenter)
            lbl_num.setStyleSheet(
                f"font-size:11px;font-weight:700;color:{C_MUTED};"
                f"background:{C_SURFACE_2};border-radius:12px;"
            )
            lbl_nom = QLabel(nombre)
            lbl_nom.setStyleSheet(f"font-size:13px;color:{C_MUTED};")
            lbl_st = QLabel("·")
            lbl_st.setStyleSheet(f"font-size:14px;color:{C_MUTED};")
            row_et.addWidget(lbl_num)
            row_et.addWidget(lbl_nom, 1)
            row_et.addWidget(lbl_st)
            self._etapas[clave] = {
                "lbl_num": lbl_num, "lbl_nom": lbl_nom, "lbl_st": lbl_st,
            }
            et_lay.addLayout(row_et)

        et_lay.addStretch()
        mid_row.addWidget(col_etapas, 4)
        bl.addLayout(mid_row)

        # ── REGISTRO DE ACTIVIDAD ─────────────────────────────────────────────
        lbl_reg_cap = QLabel("REGISTRO DE ACTIVIDAD")
        lbl_reg_cap.setStyleSheet(
            f"font-size:10px;font-weight:700;color:{C_MUTED};letter-spacing:0.8px;"
        )
        bl.addWidget(lbl_reg_cap)

        self._registro = QListWidget()
        self._registro.setMaximumHeight(148)
        self._registro.setSelectionMode(QListWidget.NoSelection)
        self._registro.setStyleSheet(
            f"QListWidget{{background:{C_SURFACE};border:none;"
            f"border-radius:10px;font-size:12px;padding:4px;color:{C_TEXT};}}"
            f"QListWidget::item{{padding:6px 12px;border-radius:4px;margin:1px;}}"
            f"QListWidget::item:hover{{background:{C_SURFACE_2};}}"
        )
        bl.addWidget(self._registro)
        bl.addStretch()

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.btn_cancelar = QPushButton("Cancelar validación")
        self.btn_cancelar.setStyleSheet(STYLE_BTN_DANGER)
        self.btn_cancelar.clicked.connect(self._on_cancelar)
        self.btn_cancelar.setToolTip("Detiene el proceso. Los resultados parciales se mostrarán igualmente.")
        btn_row.addWidget(self.btn_cancelar)
        bl.addLayout(btn_row)

        lay.addWidget(body, 1)

    def _make_card(self):
        f = QFrame()
        f.setObjectName("pro_card")
        f.setStyleSheet(
            f"QFrame#pro_card{{background:{C_SURFACE};border-radius:12px;"
            f"border:1px solid {C_BORDER};}}"
        )
        return f

    def _make_bar(self, color, height):
        bar = QProgressBar()
        bar.setFixedHeight(height)
        bar.setTextVisible(False)
        r = height // 2
        bar.setStyleSheet(
            f"QProgressBar{{background:{C_SURFACE_3};border-radius:{r}px;border:none;}}"
            f"QProgressBar::chunk{{background:qlineargradient("
            f"x1:0,y1:0,x2:1,y2:0,stop:0 {color},stop:1 {C_ACCENT_HV});"
            f"border-radius:{r}px;}}"
        )
        return bar

    def _animar_barra(self, bar, valor_final, duracion=280, lbl_pct=None):
        anim = QPropertyAnimation(bar, b"value", self)
        anim.setDuration(duracion)
        anim.setStartValue(bar.value())
        end = min(int(valor_final), bar.maximum())
        anim.setEndValue(end)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        if lbl_pct is not None:
            mx = bar.maximum()
            anim.valueChanged.connect(
                lambda v: lbl_pct.setText(
                    f"{min(round(int(v) * 100 // max(mx, 1)), 100)}%"
                )
            )
        anim.start()
        self._anim_activa = anim

    def _actualizar_tiempo(self):
        import time
        if self._t_inicio_ms <= 0:
            return
        seg = time.time() - self._t_inicio_ms
        mm, ss = divmod(int(seg), 60)
        self.lbl_tiempo.setText(f"{mm:02d}:{ss:02d}")
        mx  = self.bar_general.maximum()
        val = self.bar_general.value()
        pct = val / mx if mx > 0 else 0
        if pct > 0.05:
            total_est = seg / pct
            rest = max(0, total_est - seg)
            mr, sr = divmod(int(rest), 60)
            self.lbl_eta.setText(f"~{mr:02d}:{sr:02d} restante")
        else:
            self.lbl_eta.setText("")

    def _set_etapa_estado(self, clave, estado):
        if clave not in self._etapas:
            return
        e = self._etapas[clave]
        if estado == "activa":
            e["lbl_num"].setStyleSheet(
                f"font-size:11px;font-weight:700;color:{C_ROOT};"
                f"background:{C_ACCENT};border-radius:12px;"
            )
            e["lbl_nom"].setStyleSheet(
                f"font-size:13px;color:{C_TEXT};font-weight:600;"
            )
            e["lbl_st"].setText("→")
            e["lbl_st"].setStyleSheet(
                f"font-size:13px;color:{C_ACCENT};font-weight:700;"
            )
        elif estado == "hecha":
            e["lbl_num"].setStyleSheet(
                f"font-size:11px;font-weight:700;color:{C_ROOT};"
                f"background:{C_OK};border-radius:12px;"
            )
            e["lbl_nom"].setStyleSheet(f"font-size:13px;color:{C_SUBTEXT};")
            e["lbl_st"].setText("✓")
            e["lbl_st"].setStyleSheet(
                f"font-size:13px;color:{C_OK};font-weight:700;"
            )
        elif estado == "omitida":
            e["lbl_num"].setStyleSheet(
                f"font-size:11px;font-weight:700;color:{C_SURFACE_3};"
                f"background:{C_SURFACE_2};border-radius:12px;"
            )
            e["lbl_nom"].setStyleSheet(f"font-size:13px;color:{C_SURFACE_3};")
            e["lbl_st"].setText("—")
            e["lbl_st"].setStyleSheet(f"font-size:13px;color:{C_SURFACE_3};")
        else:  # pendiente
            e["lbl_num"].setStyleSheet(
                f"font-size:11px;font-weight:700;color:{C_MUTED};"
                f"background:{C_SURFACE_2};border-radius:12px;"
            )
            e["lbl_nom"].setStyleSheet(f"font-size:13px;color:{C_MUTED};")
            e["lbl_st"].setText("·")
            e["lbl_st"].setStyleSheet(f"font-size:14px;color:{C_MUTED};")

    def _log_append(self, texto, tipo="info"):
        import time
        if self._t_inicio_ms > 0:
            seg = time.time() - self._t_inicio_ms
            mm, ss = divmod(int(seg), 60)
            ts = f"{mm:02d}:{ss:02d}"
        else:
            ts = "--:--"
        col = {
            "ok":   C_OK,
            "err":  C_ERR,
            "warn": C_WARN,
            "info": C_SUBTEXT,
        }.get(tipo, C_SUBTEXT)
        item = QListWidgetItem(f"{ts}  {texto}")
        item.setForeground(QColor(col))
        self._registro.addItem(item)
        self._registro.scrollToBottom()

    def reiniciar(self, pais, total_capas, chips=None):
        import time
        self._cancelado      = False
        self._t_inicio_ms    = time.time()
        self._chips_activos  = chips or set()
        self._etapa_actual   = None
        self.btn_cancelar.setEnabled(True)
        self._header.findChild(QLabel).setText(f"Validando {total_capas} capa(s) — {pais}")
        self.bar_general.setMaximum(total_capas)
        self.bar_general.setValue(0)
        self.lbl_gen_pct.setText("0%")
        self.lbl_gen_sub.setText(f"0 de {total_capas} capas")
        self.lbl_tiempo.setText("")
        self.lbl_eta.setText("")
        self.bar_fase.setValue(0)
        self.lbl_capa.setText("Preparando...")
        self.lbl_fase.setText("")
        self.lbl_fase_pct.setText("")
        self.lbl_stats.setText("")
        self._registro.clear()
        self._timer_tiempo.start(500)
        self._set_etapa_estado("preparando", "activa")
        for clave in ("estructura", "atributos", "topologia", "geocodigos"):
            estado = "pendiente" if (chips and clave in chips) else "omitida"
            self._set_etapa_estado(clave, estado)

    def set_capa(self, n, total, nombre):
        val = min(n - 1, self.bar_general.maximum())
        self._animar_barra(self.bar_general, val, duracion=400, lbl_pct=self.lbl_gen_pct)
        self.lbl_gen_sub.setText(f"Capa {n} de {total}")
        self.lbl_capa.setText(nombre)
        self.bar_fase.setValue(0)
        self.lbl_fase_pct.setText("")
        self.lbl_stats.setText("")
        if n == 1:
            self._set_etapa_estado("preparando", "hecha")
        self._log_append(f"→  {nombre}", "info")

    def set_fase(self, num, texto, maximo):
        self.lbl_fase.setText(f"Fase {num} — {texto}")
        self.bar_fase.setMaximum(max(1, maximo))
        self.bar_fase.setValue(0)
        self.lbl_fase_pct.setText("0%")
        tl = texto.lower()
        if "atributo" in tl and self._etapa_actual != "atributos":
            self._etapa_actual = "atributos"
            self._set_etapa_estado("atributos", "activa")
        elif ("geometr" in tl or "topolog" in tl) and self._etapa_actual != "topologia":
            self._etapa_actual = "topologia"
            if "atributos" in self._chips_activos:
                self._set_etapa_estado("atributos", "hecha")
            self._set_etapa_estado("topologia", "activa")
        elif "geocódig" in tl and self._etapa_actual != "geocodigos":
            self._etapa_actual = "geocodigos"
            if "topologia" in self._chips_activos:
                self._set_etapa_estado("topologia", "hecha")
            elif "atributos" in self._chips_activos:
                self._set_etapa_estado("atributos", "hecha")
            self._set_etapa_estado("geocodigos", "activa")

    def set_valor(self, valor, stats=""):
        mx = self.bar_fase.maximum()
        self._animar_barra(self.bar_fase, min(int(valor), mx), duracion=180, lbl_pct=self.lbl_fase_pct)
        if stats:
            self.lbl_stats.setText(stats)

    def capa_completada(self, nombre, total, errores, seg):
        pct = round((total - errores) * 100 / total, 1) if total else 0
        ico = "✓" if pct >= 90 else "⚠" if pct >= 70 else "✗"
        tipo = "ok" if pct >= 90 else "warn" if pct >= 70 else "err"
        self._log_append(
            f"{ico}  {nombre}  ·  {total:,} feat  ·  {errores:,} err  ·  {pct}%  ·  {seg:.1f}s",
            tipo,
        )

    def finalizar(self, total_capas):
        self._timer_tiempo.stop()
        self.bar_general.setValue(total_capas)
        self.lbl_gen_pct.setText("100%")
        self.lbl_gen_sub.setText("✓ Completado")
        self.lbl_eta.setText("")
        self.btn_cancelar.setEnabled(False)
        for clave, e in self._etapas.items():
            if e["lbl_st"].text() in ("→", "·"):
                self._set_etapa_estado(clave, "hecha")
        self._log_append("✓  Validación completada", "ok")

    def fue_cancelado(self):
        return self._cancelado

    def _on_cancelar(self):
        respuesta = _ask(self, "Confirmar cancelación",
                         "¿Deseas detener la validación en curso?\n"
                         "Los resultados parciales se mostrarán igualmente.")
        if respuesta != QMessageBox.Yes:
            return
        self._cancelado = True
        self.lbl_fase.setText("Cancelando — espera un momento")
        self.btn_cancelar.setEnabled(False)


# .............................................................................
# PÁGINA 2 — Resultados
# .............................................................................

class _KpiLabel(QLabel):
    """QLabel que anima un número desde 0 hasta el valor final."""

    def __init__(self, valor_final, sufijo="", prefijo="", decimales=0, parent=None):
        super().__init__(parent)
        self._final     = valor_final
        self._sufijo    = sufijo
        self._prefijo   = prefijo
        self._decimales = decimales
        self._actual    = 0.0
        self.setText(self._fmt(0))

    def _fmt(self, v):
        if self._decimales:
            return f"{self._prefijo}{v:,.{self._decimales}f}{self._sufijo}"
        return f"{self._prefijo}{int(v):,}{self._sufijo}"

    def animar(self, duracion_ms=900):
        pasos = 40
        delta = self._final / pasos if self._final else 0
        interval = duracion_ms // pasos
        self._actual = 0.0
        t = QTimer(self)
        def _step():
            self._actual = min(self._actual + delta, self._final)
            self.setText(self._fmt(self._actual))
            if self._actual >= self._final:
                t.stop()
        t.timeout.connect(_step)
        t.start(max(1, interval))


class _DialogoGuiaErrores(QDialog):
    """Guía de referencia rápida: qué significa cada tipo de error y cómo corregirlo."""

    _GUIA = [
        ("CRÍTICO", "Campo vacío",
         "El campo es obligatorio y no tiene ningún valor.",
         "Abre la tabla de atributos en QGIS, filtra por campo vacío y completa los valores faltantes."),
        ("CRÍTICO", "ID duplicado",
         "El identificador único de la feature ya existe en otra feature de la misma capa.",
         "Filtra por el campo id_capa duplicado y asigna un nuevo ID único al feature duplicado."),
        ("ALTO",    "Abreviatura de vía no válida",
         "El valor del campo tipovía no corresponde a ninguna abreviatura del catálogo del país.",
         "Revisa el catálogo de tipovías en el Sheets y corrige la abreviatura (ej: CLL, CR, AV)."),
        ("ALTO",    "Abreviatura urbana no válida",
         "El valor del campo tipo_urb no existe en el catálogo de tipos urbanos del país.",
         "Consulta el catálogo de abreviaturas URB y actualiza el valor del campo."),
        ("ALTO",    "Código no existe en catálogo",
         "El valor del campo geocódigo (cod_mun, cod_estado, etc.) no existe en las capas de referencia.",
         "Verifica el código con la capa de polígonos de referencia. El código debe coincidir exactamente."),
        ("ALTO",    "Nombre no corresponde al código",
         "El nombre (nom_mun, nom_estado) no coincide con el código que tiene asignado el feature.",
         "Cruza el código con el catálogo y actualiza el nombre para que coincida."),
        ("ALTO",    "Valor no permitido",
         "El valor del campo no está en la lista de valores permitidos (ej: oneway debe ser B, F o N).",
         "Revisa los valores permitidos en el catálogo del campo y corrige el valor."),
        ("ALTO",    "Forma estandarizada incorrecta",
         "El campo nomvtotal no contiene la forma estandarizada del tipovía (ej: CALLE en lugar de CLL).",
         "El nomvtotal debe ser la unión del tipovía estandarizado + nomvia (ej: CALLE 15)."),
        ("ALTO",    "Campo vacío si otro campo tiene datos",
         "Un campo dependiente está vacío cuando el campo relacionado sí tiene valor.",
         "Si tipovía tiene valor, nomvia y nomvtotal también deben tenerlo. Completa los campos dependientes."),
        ("MEDIO",   "Debe estar en mayúsculas",
         "El texto del campo contiene letras minúsculas cuando debe estar completamente en MAYÚSCULAS.",
         "Usa la calculadora de campos de QGIS: upper(\"campo\") para convertir a mayúsculas."),
        ("MEDIO",   "Formato incorrecto",
         "El valor no cumple el formato esperado (ej: fecha debe ser MM-AAAA, versión debe ser V#-AA).",
         "Revisa el formato requerido para el campo y ajusta el valor. Ej: 01-2025 para fecha."),
        ("MEDIO",   "Longitud incorrecta (dígitos)",
         "El campo tiene más o menos dígitos de los requeridos (ej: cod_mun debe tener exactamente 5 dígitos).",
         "Verifica la cantidad de dígitos requerida y ajusta el valor con ceros a la izquierda si es necesario."),
        ("MEDIO",   "Valor fuera de rango",
         "El valor numérico está fuera del rango permitido (ej: velocidad > 200, valor negativo).",
         "Corrige el valor para que esté dentro del rango permitido para ese campo."),
        ("MEDIO",   "Caracteres especiales no permitidos",
         "El campo contiene caracteres que no están permitidos (ej: !, @, #, $).",
         "Elimina los caracteres especiales. Solo se permiten letras, números y los caracteres indicados."),
        ("MEDIO",   "Solo se admiten números",
         "El campo debe contener únicamente dígitos numéricos pero tiene letras u otros caracteres.",
         "Elimina todo lo que no sean dígitos del valor del campo."),
        ("BAJO",    "Espacio al inicio o al final",
         "El texto tiene espacios en blanco al inicio o al final que no son visibles pero generan errores.",
         "Usa trim(\"campo\") en la calculadora de campos para eliminar espacios extremos."),
        ("BAJO",    "Doble espacio",
         "El texto contiene dos o más espacios consecutivos entre palabras.",
         "Usa regexp_replace(\"campo\", '\\\\s+', ' ') en la calculadora de campos."),
        ("BAJO",    "Número pegado a letra (falta espacio)",
         "Hay un número directamente pegado a una letra sin espacio (ej: 2B debe ser 2 B).",
         "Agrega un espacio entre el número y la letra: 2B → 2 B, 15A → 15 A."),
        ("BAJO",    "Número escrito en letras",
         "El campo contiene números escritos en letras cuando deben ser dígitos (ej: DOS → 2).",
         "Reemplaza los números en letras por sus equivalentes numéricos."),
        ("BAJO",    "Título debe escribirse completo",
         "Se usó una abreviatura de título (DR, ING, LIC) cuando debe escribirse completo (DOCTOR, INGENIERO).",
         "Expande la abreviatura al nombre completo del título."),
    ]

    _COLOR_SEV = {
        "CRÍTICO": ("#450A0A", "#FCA5A5"),
        "ALTO":    ("#451A03", "#FDE68A"),
        "MEDIO":   ("#1E3A5F", "#93C5FD"),
        "BAJO":    ("#1F2937", "#9CA3AF"),
    }

    def __init__(self, parent=None, tipos_encontrados=None):
        super().__init__(parent)
        # Filtrar: si se pasan tipos, mostrar solo esos; si no, mostrar todos
        guia_filtrada = (
            [e for e in self._GUIA if e[1] in tipos_encontrados]
            if tipos_encontrados else self._GUIA
        )
        n = len(guia_filtrada)
        titulo_ventana = (
            f"Errores de esta validación ({n} tipo{'s' if n != 1 else ''})"
            if tipos_encontrados else "Guía completa de errores"
        )
        self.setWindowTitle(titulo_ventana)
        self.setMinimumSize(720, 580)
        self.setStyleSheet(f"background:{C_ROOT};color:{C_TEXT};")
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # Cabecera
        hdr = QWidget()
        hdr.setStyleSheet(f"background:{C_SURFACE};border-bottom:1px solid {C_BORDER};")
        hdr_lay = QVBoxLayout(hdr)
        hdr_lay.setContentsMargins(28, 18, 28, 16)
        lbl_t = QLabel(titulo_ventana)
        lbl_t.setStyleSheet(f"font-size:18px;font-weight:700;color:{C_TEXT};")
        lbl_s = QLabel(
            "Estos son los tipos de error que aparecieron en la validación — descripción y cómo corregirlos en QGIS"
            if tipos_encontrados else
            "Referencia completa: qué significa cada error y cómo corregirlo en QGIS"
        )
        lbl_s.setStyleSheet(f"font-size:12px;color:{C_SUBTEXT};")
        hdr_lay.addWidget(lbl_t)
        hdr_lay.addWidget(lbl_s)
        lay.addWidget(hdr)

        # Scroll con tarjetas
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(f"background:{C_ROOT};border:none;")
        contenido = QWidget()
        contenido.setStyleSheet(f"background:{C_ROOT};")
        cl = QVBoxLayout(contenido)
        cl.setContentsMargins(24, 20, 24, 20)
        cl.setSpacing(10)

        if not guia_filtrada:
            lbl_vacio = QLabel("No se encontraron errores de atributos en esta validación.")
            lbl_vacio.setStyleSheet(f"font-size:13px;color:{C_SUBTEXT};padding:20px;")
            cl.addWidget(lbl_vacio)

        sev_actual = None
        for sev, tipo, desc, fix in guia_filtrada:
            # Separador de severidad
            if sev != sev_actual:
                sev_actual = sev
                bg, fg = self._COLOR_SEV[sev]
                lbl_sev = QLabel(sev)
                lbl_sev.setStyleSheet(
                    f"background:{bg};color:{fg};padding:3px 12px;"
                    f"border-radius:6px;font-size:11px;font-weight:700;"
                    f"letter-spacing:0.5px;margin-top:8px;"
                )
                lbl_sev.setFixedWidth(80)
                cl.addWidget(lbl_sev)

            card = QFrame()
            card.setObjectName("guide_card")
            card.setStyleSheet(
                f"QFrame#guide_card{{background:{C_SURFACE};border-radius:10px;border:none;}}"
            )
            card_lay = QVBoxLayout(card)
            card_lay.setContentsMargins(16, 12, 16, 12)
            card_lay.setSpacing(6)

            # Tipo de error
            lbl_tipo = QLabel(tipo)
            lbl_tipo.setStyleSheet(f"font-size:13px;font-weight:700;color:{C_TEXT};")
            card_lay.addWidget(lbl_tipo)

            # Descripción
            lbl_desc = QLabel(f"¿Qué es?  {desc}")
            lbl_desc.setStyleSheet(f"font-size:12px;color:{C_SUBTEXT};")
            lbl_desc.setWordWrap(True)
            card_lay.addWidget(lbl_desc)

            # Cómo corregir
            lbl_fix = QLabel(f"¿Cómo corregir?  {fix}")
            lbl_fix.setStyleSheet(
                f"font-size:12px;color:{C_OK};"
            )
            lbl_fix.setWordWrap(True)
            card_lay.addWidget(lbl_fix)

            cl.addWidget(card)

        cl.addStretch()
        scroll.setWidget(contenido)
        lay.addWidget(scroll, 1)

        # Botón cerrar
        fondo = QWidget()
        fondo.setStyleSheet(f"background:{C_SURFACE};border-top:1px solid {C_BORDER};")
        frow = QHBoxLayout(fondo)
        frow.setContentsMargins(24, 10, 24, 12)
        frow.addStretch()
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setStyleSheet(STYLE_BTN_PRIMARY)
        btn_cerrar.clicked.connect(self.close)
        frow.addWidget(btn_cerrar)
        lay.addWidget(fondo)


class _PaginaResultados(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._datos    = {}
        self._email_cfg = {}
        self.setStyleSheet(f"background:{C_ROOT};")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        lay.addWidget(_make_header("Resultados de la validación", paso=3))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(f"background:{C_ROOT};border:none;")
        self._contenido = QWidget()
        self._contenido.setStyleSheet(f"background:{C_ROOT};")
        self._lay_c = QVBoxLayout(self._contenido)
        self._lay_c.setSpacing(16)
        self._lay_c.setContentsMargins(24, 20, 24, 8)
        scroll.setWidget(self._contenido)
        lay.addWidget(scroll, 1)

        # Label de estado del correo — siempre visible, fuera del scroll
        self._lbl_estado_correo = QLabel("")
        self._lbl_estado_correo.setWordWrap(True)
        self._lbl_estado_correo.setContentsMargins(20, 8, 20, 8)
        self._lbl_estado_correo.setVisible(False)
        lay.addWidget(self._lbl_estado_correo)

        fondo = QWidget()
        fondo.setStyleSheet(
            f"background:{C_SURFACE};border-top:1px solid {C_BORDER};"
        )
        frow = QHBoxLayout(fondo)
        frow.setContentsMargins(20, 10, 20, 12)
        self.btn_nueva  = QPushButton("Nueva validación")
        self.btn_nueva.setStyleSheet(STYLE_BTN_GHOST)
        self.btn_cerrar = QPushButton("Cerrar")
        self.btn_cerrar.setStyleSheet(STYLE_BTN_PRIMARY)
        frow.addWidget(self.btn_nueva)
        frow.addStretch()
        frow.addWidget(self.btn_cerrar)
        lay.addWidget(fondo)

    def mostrar(self, stats, inconsistencias, pais, tiempo_s,
                ruta_html, archivos_csv, carpeta_rep, topo_resultados=None,
                capas_res=None, csv_resumen=None, capas_res_cruce_esp=None,
                email_config=None, modo_proceso="interno",
                datos_cruce_lazy=None,
                verificar_entrega=False, doc_resultado=None,
                drive_url="", drive_archivos=None, comentario=""):
        self._email_cfg        = email_config or {}
        self._modo_proceso     = modo_proceso
        self._datos_cruce_lazy = datos_cruce_lazy or {}
        self._datos = dict(
            stats=stats, inconsistencias=inconsistencias, pais=pais,
            tiempo_s=tiempo_s, ruta_html=ruta_html,
            archivos_csv=archivos_csv, carpeta_rep=carpeta_rep,
            csv_resumen=csv_resumen,
            modo=(email_config or {}).get("modo", set()),
            verificar_entrega=verificar_entrega,
            doc_resultado=doc_resultado,
            drive_url=drive_url,
            drive_archivos=drive_archivos or [],
            comentario=comentario,
        )
        while self._lay_c.count():
            item = self._lay_c.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._kpis_animados = []
        self._construir(stats, inconsistencias, pais, tiempo_s,
                        ruta_html, archivos_csv, carpeta_rep, topo_resultados or [],
                        capas_res or {}, capas_res_cruce_esp or {},
                        verificar_entrega=self._datos.get("verificar_entrega", False),
                        drive_url=self._datos.get("drive_url", ""),
                        drive_archivos=self._datos.get("drive_archivos", []))
        QTimer.singleShot(80, self._iniciar_animaciones)

    def _iniciar_animaciones(self):
        for k in self._kpis_animados:
            k.animar()

    def _card(self):
        f = QFrame()
        f.setObjectName("result_card")
        f.setStyleSheet(
            f"QFrame#result_card{{background:{C_SURFACE};border-radius:12px;"
            f"border:1px solid {C_BORDER};}}"
        )
        return f

    def _collapsible_section(self, titulo, contenido, abierto=True):
        wrapper = QWidget()
        wl = QVBoxLayout(wrapper)
        wl.setContentsMargins(0, 0, 0, 4)
        wl.setSpacing(8)
        btn = QPushButton(f"{'▾' if abierto else '▸'}  {titulo}")
        btn.setStyleSheet(
            f"QPushButton{{background:transparent;color:{C_TEXT};"
            f"font-size:14px;font-weight:700;text-align:left;"
            f"border:none;padding:2px 0px;letter-spacing:-0.2px;}}"
            f"QPushButton:hover{{color:{C_ACCENT_HV};}}"
        )
        btn.setCursor(Qt.PointingHandCursor)
        contenido.setVisible(abierto)
        def _toggle():
            vis = not contenido.isVisible()
            contenido.setVisible(vis)
            btn.setText(f"{'▾' if vis else '▸'}  {titulo}")
        btn.clicked.connect(_toggle)
        wl.addWidget(btn)
        wl.addWidget(contenido)
        return wrapper

    def _construir(self, stats, inconsistencias, pais, tiempo_s,
                   ruta_html, archivos_csv, carpeta_rep, topo_resultados=None,
                   capas_res=None, capas_res_cruce_esp=None,
                   verificar_entrega=False,
                   drive_url="", drive_archivos=None):
        lay = self._lay_c

        total_feat = sum(s["total"]     for s in stats)
        total_err  = sum(s["con_error"] for s in stats)
        total_ok   = total_feat - total_err
        pct_g      = round(total_ok * 100 / total_feat, 1) if total_feat else 0
        col_g      = _color_calidad(pct_g)
        hay_atribs = total_feat > 0

        # ── Banner de calidad global ─────────────────────────────────────────────
        _estado_txt = ("EXCELENTE" if pct_g >= 90 else
                       "ACEPTABLE" if pct_g >= 70 else "CRÍTICO")
        _estado_col = col_g
        banner = QFrame()
        banner.setObjectName("result_banner")
        banner.setStyleSheet(
            f"QFrame#result_banner{{background:{C_SURFACE};"
            f"border-radius:14px;border:none;}}"
        )
        bl = QHBoxLayout(banner)
        bl.setContentsMargins(28, 22, 28, 22)
        bl.setSpacing(0)

        # Izquierda — info
        left = QVBoxLayout()
        left.setSpacing(4)
        lbl_done = QLabel(f"Validación completada")
        lbl_done.setStyleSheet(
            f"color:{C_SUBTEXT};font-size:11px;font-weight:600;"
            f"letter-spacing:0.5px;background:transparent;border:none;"
        )
        lbl_pais_b = QLabel(pais)
        lbl_pais_b.setStyleSheet(
            f"color:{C_TEXT};font-size:18px;font-weight:700;"
            f"background:transparent;border:none;letter-spacing:-0.3px;"
        )
        fecha_txt = QLabel(datetime.now().strftime("%d/%m/%Y  %H:%M"))
        fecha_txt.setStyleSheet(f"color:{C_MUTED};font-size:11px;background:transparent;border:none;")
        left.addWidget(lbl_done)
        left.addWidget(lbl_pais_b)
        left.addWidget(fecha_txt)
        bl.addLayout(left, 1)

        # Derecha — porcentaje grande
        right = QVBoxLayout()
        right.setSpacing(2)
        right.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        if hay_atribs:
            kpi_pct = QLabel(f"{pct_g}%")
            kpi_pct.setStyleSheet(
                f"color:{_estado_col};font-size:44px;font-weight:800;"
                f"background:transparent;border:none;letter-spacing:-2px;"
            )
            kpi_pct.setAlignment(Qt.AlignRight)
            lbl_estado_b = QLabel(_estado_txt)
            lbl_estado_b.setStyleSheet(
                f"color:{_estado_col};font-size:11px;font-weight:700;"
                f"letter-spacing:1px;background:transparent;border:none;"
            )
            lbl_estado_b.setAlignment(Qt.AlignRight)
            right.addWidget(kpi_pct)
            right.addWidget(lbl_estado_b)
        else:
            lbl_modo_res = QLabel("Sin validación de atributos")
            lbl_modo_res.setStyleSheet(
                f"color:{C_SUBTEXT};font-size:13px;background:transparent;border:none;"
            )
            lbl_modo_res.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            right.addWidget(lbl_modo_res)
        bl.addLayout(right)
        lay.addWidget(banner)

        # Botón guía de errores — solo en modo VALIDAR, solo con los errores que salieron
        _es_interno_banner = getattr(self, "_modo_proceso", "interno") == "interno"
        if _es_interno_banner and hay_atribs:
            # Recopilar tipos de error — solo el primer mensaje por campo (rápido)
            try:
                from .utils.clasificador_errores import clasificar
                _tipos_encontrados = set()
                for s in (stats or []):
                    for campo, items in s.get("errores_por_campo", {}).items():
                        if items:
                            _tipos_encontrados.add(clasificar(items[0].get("msg", "")))
            except Exception:
                _tipos_encontrados = set()

            n_tipos = len(_tipos_encontrados)
            btn_guia = QPushButton(
                f"¿Qué significa cada error?  ({n_tipos} tipo{'s' if n_tipos != 1 else ''} encontrado{'s' if n_tipos != 1 else ''})"
                if n_tipos else "¿Qué significa cada error?"
            )
            btn_guia.setCursor(Qt.PointingHandCursor)
            btn_guia.setStyleSheet(
                f"QPushButton{{background:transparent;color:{C_ACCENT};"
                f"border:1px solid {C_ACCENT_DIM};border-radius:8px;"
                f"padding:8px 16px;font-size:12px;font-weight:600;}}"
                f"QPushButton:hover{{background:{C_ACCENT_DIM};}}"
            )
            btn_guia.setToolTip(
                "Muestra solo los tipos de error que aparecieron en esta validación, "
                "con descripción y cómo corregirlos en QGIS"
            )
            btn_guia.clicked.connect(
                lambda: _DialogoGuiaErrores(self, _tipos_encontrados).show()
            )
            lay.addWidget(btn_guia)

        # (estructura se añade después de los KPIs — ver abajo)

        # ── KPIs — 4 tiles con icono + número + etiqueta ─────────────────────────
        _kpi_data = [
            (total_feat, "#", "ANALIZADAS",  C_TEXT,    0, C_SURFACE_2),
            (total_ok,   "✓", "CORRECTAS",   C_OK,      0, C_OK_DIM),
            (total_err,  "✗", "CON ERRORES", C_ERR,     0, C_ERR_DIM),
            (tiempo_s,   "s", "SEGUNDOS",    C_SUBTEXT, 1, C_SURFACE_2),
        ]
        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(10)
        for val, icono, etiq, col, dec, bg in _kpi_data:
            tile = QFrame()
            tile.setObjectName("kpi_tile")
            tile.setStyleSheet(
                f"QFrame#kpi_tile{{background:{bg};border-radius:12px;border:none;}}"
            )
            tl = QVBoxLayout(tile)
            tl.setContentsMargins(18, 16, 18, 14)
            tl.setSpacing(2)

            # Icono pequeño
            lbl_ico = QLabel(icono)
            lbl_ico.setStyleSheet(
                f"font-size:13px;color:{col};background:transparent;border:none;"
            )
            kv = _KpiLabel(val, decimales=dec)
            kv.setStyleSheet(
                f"font-size:30px;font-weight:800;color:{col};"
                f"background:transparent;border:none;letter-spacing:-1px;"
            )
            kv.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            ke = QLabel(etiq)
            ke.setStyleSheet(
                f"font-size:9px;font-weight:700;color:{C_MUTED};"
                f"letter-spacing:0.8px;background:transparent;border:none;"
            )
            tl.addWidget(lbl_ico)
            tl.addWidget(kv)
            tl.addWidget(ke)
            kpi_row.addWidget(tile, 1)
            self._kpis_animados.append(kv)

        lay.addLayout(kpi_row)

        # ── Estructura de capas (colapsable, mismo estilo que el resto del panel) ──
        _stats_con_estructura = [s for s in stats if s.get("estructura_validada")]
        if _stats_con_estructura:
            _errs_est_total = sum(len(s.get("estructura_errores") or [])
                                  for s in _stats_con_estructura)
            _capas_ok  = sum(1 for s in _stats_con_estructura
                             if not s.get("estructura_errores"))
            _capas_err = len(_stats_con_estructura) - _capas_ok

            _tit_est = (
                f"Estructura  ✓  ({_capas_ok}/{len(_stats_con_estructura)} capas correctas)"
                if _capas_err == 0 else
                f"Estructura  —  {_capas_err} capa{'s' if _capas_err != 1 else ''} "
                f"con errores · {_errs_est_total} problema{'s' if _errs_est_total != 1 else ''}"
            )

            # (color_borde_izq, color_badge, color_msg)
            _PREF_STYLE = {
                "FALTANTE":    (C_ERR,     C_ERR,     C_ERR),
                "SOBRANTE":    ("#FB923C", "#FB923C", "#FB923C"),
                "TIPO":        (C_WARN,    C_WARN,    C_WARN),
                "LONGITUD":    (C_WARN,    C_WARN,    C_WARN),
                "SIN ESQUEMA": (C_ERR,     C_ERR,     C_ERR),
                "OTRO":        (C_BORDER,  C_SUBTEXT, C_SUBTEXT),
            }

            _est_contenido = QWidget()
            _est_inner = QVBoxLayout(_est_contenido)
            _est_inner.setContentsMargins(0, 0, 0, 0)
            _est_inner.setSpacing(8)

            for s in _stats_con_estructura:
                errs_capa = s.get("estructura_errores") or []
                icono     = "✓" if not errs_capa else "✗"
                col_ico   = C_OK if not errs_capa else C_ERR
                _n_e      = len(errs_capa)

                capa_card = self._card()
                capa_lay  = QVBoxLayout(capa_card)
                capa_lay.setContentsMargins(14, 12, 14, 12)
                capa_lay.setSpacing(6)

                # Cabecera de la capa
                hdr = QHBoxLayout()
                hdr.setSpacing(8)
                lbl_ico = QLabel(icono)
                lbl_ico.setStyleSheet(
                    f"font-size:13px;font-weight:800;color:{col_ico};"
                    f"background:transparent;border:none;"
                )
                lbl_nom = QLabel(s["nombre"])
                lbl_nom.setStyleSheet(
                    f"font-size:13px;font-weight:700;color:{C_TEXT};"
                    f"background:transparent;border:none;"
                )
                hdr.addWidget(lbl_ico)
                hdr.addWidget(lbl_nom, 1)
                if errs_capa:
                    lbl_cnt = QLabel(
                        f"{_n_e} error{'es' if _n_e != 1 else ''}"
                    )
                    lbl_cnt.setStyleSheet(
                        f"font-size:11px;font-weight:600;color:{C_ERR};"
                        f"background:{C_ERR_DIM};border-radius:6px;"
                        f"padding:2px 8px;border:none;"
                    )
                    hdr.addWidget(lbl_cnt)
                capa_lay.addLayout(hdr)

                if errs_capa:
                    # Agrupa por prefijo y muestra con borde izquierdo de color
                    _grupos = {}
                    for msg in errs_capa:
                        _pref = (msg[1:msg.index("]")]
                                 if msg.startswith("[") and "]" in msg else "OTRO")
                        _grupos.setdefault(_pref, []).append(msg)

                    for pref, msgs in _grupos.items():
                        col_borde, col_badge, col_msg = _PREF_STYLE.get(
                            pref, _PREF_STYLE["OTRO"])

                        grp = QFrame()
                        grp.setStyleSheet(
                            f"QFrame{{background:{C_SURFACE_2};border-radius:6px;"
                            f"border-left:3px solid {col_borde};"
                            f"border-top:1px solid {C_BORDER};"
                            f"border-right:1px solid {C_BORDER};"
                            f"border-bottom:1px solid {C_BORDER};}}"
                        )
                        grp_lay = QVBoxLayout(grp)
                        grp_lay.setContentsMargins(10, 6, 10, 6)
                        grp_lay.setSpacing(3)

                        pref_row = QHBoxLayout()
                        pref_row.setSpacing(6)
                        lbl_badge = QLabel(pref)
                        lbl_badge.setStyleSheet(
                            f"font-size:10px;font-weight:800;color:{col_badge};"
                            f"background:transparent;border:none;letter-spacing:0.5px;"
                        )
                        lbl_n = QLabel(
                            f"{len(msgs)} problema{'s' if len(msgs) != 1 else ''}"
                        )
                        lbl_n.setStyleSheet(
                            f"font-size:10px;color:{C_SUBTEXT};"
                            f"background:transparent;border:none;"
                        )
                        pref_row.addWidget(lbl_badge)
                        pref_row.addWidget(lbl_n, 1)
                        grp_lay.addLayout(pref_row)

                        for msg in msgs:
                            txt = msg[msg.index("]") + 2:] if "]" in msg else msg
                            lbl = QLabel(f"• {txt}")
                            lbl.setWordWrap(True)
                            lbl.setStyleSheet(
                                f"font-size:11px;color:{col_msg};"
                                f"background:transparent;border:none;"
                            )
                            grp_lay.addWidget(lbl)

                        capa_lay.addWidget(grp)

                _est_inner.addWidget(capa_card)

            lay.addWidget(self._collapsible_section(_tit_est, _est_contenido, abierto=True))

        # ── Tarjetas por capa (colapsable, contenido según modo) ─────────────────
        capas_res     = capas_res or {}
        es_interno    = getattr(self, "_modo_proceso", "interno") == "interno"
        _grid_contenido = QWidget()
        _grid_inner   = QVBoxLayout(_grid_contenido)
        _grid_inner.setContentsMargins(0, 0, 0, 0)
        _grid_inner.setSpacing(0)
        # Modo interno: full-width (lectura rápida) | Modo entrega: grid 2 col (denso/técnico)
        if es_interno:
            _cards_lay = QVBoxLayout()
            _cards_lay.setSpacing(10)
        else:
            grid = QGridLayout()
            grid.setSpacing(12)

        for idx, s in enumerate(stats):
            col  = _color_calidad(s["pct_calidad"])
            card = self._card()
            cl   = QVBoxLayout(card)
            cl.setContentsMargins(16, 14, 16, 14)
            cl.setSpacing(8)

            # Cabecera — igual para ambos modos
            row_top = QHBoxLayout()
            hn = QLabel(s["nombre"])
            hn.setStyleSheet(f"font-size:13px;font-weight:700;color:{C_TEXT};background:transparent;border:none;")
            hp = QLabel(f"{s['pct_calidad']}%")
            hp.setStyleSheet(f"font-size:18px;font-weight:800;color:{col};background:transparent;border:none;")
            row_top.addWidget(hn, 1)
            row_top.addWidget(hp)
            cl.addLayout(row_top)

            # Barra de calidad — igual para ambos modos
            bar = QProgressBar()
            bar.setMaximum(100)
            bar.setValue(int(s["pct_calidad"]))
            bar.setTextVisible(False)
            bar.setFixedHeight(6)
            bar.setStyleSheet(
                f"QProgressBar{{background:{C_SURFACE_2};border-radius:3px;border:none;}}"
                f"QProgressBar::chunk{{background:{col};border-radius:3px;}}"
            )
            cl.addWidget(bar)

            # Estadísticas resumen — igual para ambos modos
            row_stats = QHBoxLayout()
            for v, e, c in [
                (f"{s['total']:,}", "features", C_SUBTEXT),
                (f"{s['sin_error']:,}", "correctos", C_OK),
                (f"{s['con_error']:,}", "errores", C_ERR),
            ]:
                bx = QVBoxLayout()
                lv = QLabel(v)
                lv.setStyleSheet(f"font-size:14px;font-weight:700;color:{c};background:transparent;border:none;")
                lv.setAlignment(Qt.AlignCenter)
                le = QLabel(e)
                le.setStyleSheet(f"font-size:10px;color:{C_SUBTEXT};background:transparent;border:none;")
                le.setAlignment(Qt.AlignCenter)
                bx.addWidget(lv); bx.addWidget(le)
                row_stats.addLayout(bx)
            cl.addLayout(row_stats)

            if es_interno:
                # ── Modo interno: errores agrupados por campo → tipo → cantidad ───
                if s["campos_ordenados"]:
                    try:
                        from .utils.clasificador_errores import (
                            agrupar_por_tipo, extraer_hints_por_tipo,
                            severidad, color_severidad)
                        errores_campo = s.get("errores_por_campo", {})
                        agrupado = agrupar_por_tipo(errores_campo)
                        hints_d  = extraer_hints_por_tipo(errores_campo)
                    except Exception:
                        agrupado = {}
                        hints_d  = {}

                    for campo in s["campos_ordenados"][:5]:
                        tipos   = agrupado.get(campo, {})
                        hints_c = hints_d.get(campo, {})
                        if not tipos:
                            continue
                        sep_c = QFrame()
                        sep_c.setFrameShape(QFrame.HLine)
                        sep_c.setFrameShadow(QFrame.Plain)
                        sep_c.setStyleSheet(f"background:{C_BORDER};border:none;")
                        sep_c.setFixedHeight(1)
                        cl.addWidget(sep_c)
                        lbl_c = QLabel(campo)
                        lbl_c.setStyleSheet(
                            f"font-size:11px;font-weight:700;color:{C_ACCENT_HV};"
                            f"background:transparent;border:none;letter-spacing:0.3px;"
                        )
                        cl.addWidget(lbl_c)
                        for tipo, n in list(tipos.items())[:3]:
                            sev      = severidad(tipo)
                            bg, fg   = color_severidad(sev)
                            hint     = hints_c.get(tipo, "")
                            tipo_row = QHBoxLayout()
                            lbl_tipo = QLabel(tipo)
                            lbl_tipo.setStyleSheet(
                                f"font-size:11px;color:{C_SUBTEXT};"
                                f"background:transparent;border:none;"
                            )
                            lbl_sev  = QLabel(sev)
                            lbl_sev.setStyleSheet(
                                f"background:{bg};color:{fg};padding:2px 7px;"
                                f"border-radius:8px;font-size:9px;font-weight:700;border:none;"
                            )
                            lbl_n = QLabel(f"{n:,}")
                            lbl_n.setStyleSheet(
                                f"font-size:12px;font-weight:700;color:{C_ERR};"
                                f"background:transparent;border:none;"
                            )
                            tipo_row.addWidget(lbl_tipo, 1)
                            tipo_row.addWidget(lbl_sev)
                            tipo_row.addWidget(lbl_n)
                            cl.addLayout(tipo_row)
                            if hint:
                                lbl_hint = QLabel(hint)
                                lbl_hint.setStyleSheet(
                                    f"font-size:10px;color:{C_MUTED};font-style:italic;"
                                    f"background:transparent;border:none;"
                                )
                                lbl_hint.setWordWrap(True)
                                cl.addWidget(lbl_hint)

                    if s["n_campos_error"] > 5:
                        lbl_mas = QLabel(f"+{s['n_campos_error']-5} campos más")
                        lbl_mas.setStyleSheet(f"font-size:11px;color:{C_MUTED};background:transparent;border:none;")
                        cl.addWidget(lbl_mas)
            else:
                # ── Modo entrega: vista detallada con badges de FIDs ─────────────
                capa_r = capas_res.get(s["nombre"])
                if capa_r is not None:
                    btn_qgis = QPushButton("Visualizar en QGIS")
                    btn_qgis.setStyleSheet(
                        f"QPushButton{{background:#1E40AF;color:white;padding:4px 10px;"
                        f"border-radius:5px;font-size:11px;border:none;}}"
                        f"QPushButton:hover{{background:#2563EB;}}"
                        f"QPushButton:disabled{{background:#334155;color:#64748B;}}"
                    )
                    def _send(_, layer=capa_r, b=btn_qgis):
                        QgsProject.instance().addMapLayer(layer)
                        b.setText("✓ En QGIS"); b.setEnabled(False)
                    btn_qgis.clicked.connect(_send)
                    cl.addWidget(btn_qgis)

                if s["campos_ordenados"]:
                    badges_row = QHBoxLayout()
                    badges_row.setSpacing(6)
                    for campo in s["campos_ordenados"][:4]:
                        n_err = len(s["errores_por_campo"][campo])
                        badge = QLabel(f"{campo}  {n_err:,}")
                        badge.setStyleSheet(
                            f"background:{C_ERR_DIM};color:{C_ERR};"
                            f"border-radius:6px;padding:3px 10px;"
                            f"font-size:11px;font-weight:600;border:none;"
                        )
                        badges_row.addWidget(badge)
                    if s["n_campos_error"] > 4:
                        mas = QLabel(f"+{s['n_campos_error']-4} más")
                        mas.setStyleSheet(f"color:{C_SUBTEXT};font-size:11px;")
                        badges_row.addWidget(mas)
                    badges_row.addStretch()
                    cl.addLayout(badges_row)

            if es_interno:
                _cards_lay.addWidget(card)
            else:
                grid.addWidget(card, idx // 2, idx % 2)

        if es_interno:
            _grid_inner.addLayout(_cards_lay)
        else:
            _grid_inner.addLayout(grid)
        titulo_seccion = ("Resumen por capa" if es_interno else "Detalle por capa")
        lay.addWidget(self._collapsible_section(titulo_seccion, _grid_contenido))

        # ── Sección topología (colapsable) ───────────────────────────────────────
        if topo_resultados:
            _topo_contenido = QWidget()
            _topo_inner = QVBoxLayout(_topo_contenido)
            _topo_inner.setContentsMargins(0, 0, 0, 0)
            _topo_inner.setSpacing(10)

            for tr in topo_resultados:
                tc = self._card()
                tl = QVBoxLayout(tc)
                tl.setContentsMargins(16, 12, 16, 12)
                tl.setSpacing(6)

                row_th = QHBoxLayout()
                lbl_tn = QLabel(tr["nombre_capa"])
                lbl_tn.setStyleSheet(f"font-size:13px;font-weight:700;color:{C_TEXT};background:transparent;border:none;")
                n_terr = len(tr["errores"])
                col_te = C_OK if n_terr == 0 else C_ERR
                lbl_te = QLabel(f"{n_terr} error{'es' if n_terr != 1 else ''}")
                lbl_te.setStyleSheet(
                    f"font-size:14px;font-weight:700;color:{col_te};background:transparent;border:none;"
                )
                row_th.addWidget(lbl_tn, 1)
                row_th.addWidget(lbl_te)
                tl.addLayout(row_th)

                if n_terr > 0:
                    reglas = Counter(e["regla"] for e in tr["errores"])
                    badges_topo = QHBoxLayout()
                    badges_topo.setSpacing(6)
                    for regla, cnt in reglas.most_common():
                        badge = QLabel(f"{regla}  {cnt}")
                        badge.setStyleSheet(
                            f"background:{C_ERR_DIM};color:{C_ERR};"
                            f"border-radius:6px;border:none;"
                            f"padding:3px 10px;font-size:11px;font-weight:600;"
                        )
                        badges_topo.addWidget(badge)
                    badges_topo.addStretch()
                    tl.addLayout(badges_topo)
                    for err in tr["errores"][:5]:
                        lbl_ei = QLabel(f"  FID {err['fid']}: {err['descripcion']}")
                        lbl_ei.setStyleSheet(f"font-size:11px;color:{C_SUBTEXT};background:transparent;border:none;")
                        tl.addWidget(lbl_ei)
                    if n_terr > 5:
                        lbl_mas_t = QLabel(f"  + {n_terr - 5} más")
                        lbl_mas_t.setStyleSheet(f"font-size:11px;color:{C_SUBTEXT};background:transparent;border:none;")
                        tl.addWidget(lbl_mas_t)
                else:
                    lbl_tok = QLabel("  ✓ Sin problemas topológicos")
                    lbl_tok.setStyleSheet(f"font-size:12px;color:{C_OK};background:transparent;border:none;")
                    tl.addWidget(lbl_tok)

                _topo_inner.addWidget(tc)

            lay.addWidget(self._collapsible_section("Topología", _topo_contenido))

        # ── Sección geocódigos — orden: puntos → líneas → polígonos ─────────────
        capas_res_cruce_esp = capas_res_cruce_esp or {}
        todas_incons = inconsistencias or []
        if todas_incons or capas_res_cruce_esp:
            from collections import defaultdict as _dd
            _ORDEN_TGEOM = {"puntos": 0, "líneas": 1, "poligono": 2}
            _ETIQ_TIPO = {
                "valor_huerfano":          "Valor sin referencia",
                "sin_capa_referencia":     "Sin capa referencia",
                "inconsistencia_espacial": "Código incorrecto",
                "sin_poligono_contenedor": "Fuera de polígono",
                "cruce_placa_mavvial":     "Cruce placa-mavvial",
                "id_mavvial_huerfano":     "ID mavvial huérfano",
            }
            # Agrupar por (capa_origen, tipo_geom)
            por_capa = _dd(list)
            for i in todas_incons:
                por_capa[(i["capa_origen"], i.get("tipo_geom", ""))].append(i)

            _geo_contenido = QWidget()
            _geo_inner = QVBoxLayout(_geo_contenido)
            _geo_inner.setContentsMargins(0, 0, 0, 0)
            _geo_inner.setSpacing(10)

            for (nom_c, tgeom), errores_capa in sorted(
                por_capa.items(),
                key=lambda x: (_ORDEN_TGEOM.get(x[0][1], 3), x[0][0])
            ):
                total_err_c = sum(i.get("n_features", 0) for i in errores_capa)
                tc_g = self._card()
                tl_g = QVBoxLayout(tc_g)
                tl_g.setContentsMargins(16, 14, 16, 14)
                tl_g.setSpacing(8)

                # Cabecera: capa + geometría + total
                row_h = QHBoxLayout()
                lbl_nom_g = QLabel(nom_c)
                lbl_nom_g.setStyleSheet(f"font-size:13px;font-weight:700;color:{C_TEXT};background:transparent;border:none;")
                lbl_tgeom = QLabel(tgeom.upper() if tgeom else "")
                lbl_tgeom.setStyleSheet(
                    f"background:{C_SURFACE_3};color:{C_SUBTEXT};padding:2px 8px;"
                    f"border-radius:8px;font-size:11px;font-weight:600;border:none;"
                )
                lbl_cnt_g = QLabel(f"{total_err_c:,} features")
                lbl_cnt_g.setStyleSheet(f"font-size:13px;font-weight:700;color:{C_ERR};background:transparent;border:none;")
                row_h.addWidget(lbl_nom_g, 1)
                row_h.addWidget(lbl_tgeom)
                row_h.addSpacing(8)
                row_h.addWidget(lbl_cnt_g)
                tl_g.addLayout(row_h)

                # Detalle por inconsistencia
                for inc in errores_capa:
                    sep_d = QFrame()
                    sep_d.setFrameShape(QFrame.HLine)
                    sep_d.setFrameShadow(QFrame.Plain)
                    sep_d.setStyleSheet(f"background:{C_BORDER};border:none;")
                    sep_d.setFixedHeight(1)
                    tl_g.addWidget(sep_d)
                    row_f = QHBoxLayout()
                    lbl_campo_g = QLabel(inc['campo'])
                    lbl_campo_g.setStyleSheet(
                        f"font-size:12px;font-weight:600;color:{C_ACCENT_HV};"
                        f"background:transparent;border:none;"
                    )
                    tipo_etiq = _ETIQ_TIPO.get(inc.get("tipo", ""), inc.get("tipo", ""))
                    lbl_tipo_g = QLabel(tipo_etiq)
                    lbl_tipo_g.setStyleSheet(
                        f"background:{C_ERR_DIM};color:{C_ERR};padding:2px 8px;"
                        f"border-radius:8px;font-size:11px;font-weight:600;border:none;"
                    )
                    lbl_nf_g = QLabel(f"{inc.get('n_features', 0):,} feat.")
                    lbl_nf_g.setStyleSheet(
                        f"font-size:12px;color:{C_SUBTEXT};"
                        f"background:transparent;border:none;"
                    )
                    row_f.addWidget(lbl_campo_g)
                    row_f.addWidget(lbl_tipo_g)
                    row_f.addStretch()
                    row_f.addWidget(lbl_nf_g)
                    tl_g.addLayout(row_f)
                    refs = ", ".join(inc.get("capas_referencia") or []) or "—"
                    lbl_ref_g = QLabel(f"Capas en conflicto:  {refs}")
                    lbl_ref_g.setStyleSheet(
                        f"font-size:11px;color:{C_SUBTEXT};"
                        f"background:transparent;border:none;"
                    )
                    tl_g.addWidget(lbl_ref_g)
                    items = inc.get("items", [])
                    if items:
                        fids_s = ", ".join(str(it[0]) for it in items[:10])
                        sufijo = f" (+{len(items)-10} más)" if len(items) > 10 else ""
                        lbl_fids_g = QLabel(f"FIDs:  {fids_s}{sufijo}")
                        lbl_fids_g.setStyleSheet(
                            f"font-size:11px;color:{C_MUTED};font-family:monospace;"
                            f"background:transparent;border:none;"
                        )
                        tl_g.addWidget(lbl_fids_g)

                # Botón QGIS — crea la capa lazy solo al hacer clic
                if nom_c in (capas_res_cruce_esp or {}) or nom_c in getattr(self, "_datos_cruce_lazy", {}):
                    btn_qgis_g = QPushButton("Visualizar errores en QGIS")
                    btn_qgis_g.setStyleSheet(
                        f"QPushButton{{background:#1E40AF;color:white;padding:4px 10px;"
                        f"border-radius:5px;font-size:11px;border:none;}}"
                        f"QPushButton:hover{{background:#2563EB;}}"
                        f"QPushButton:disabled{{background:#334155;color:#64748B;}}"
                    )
                    def _send_g(_, n=nom_c, b=btn_qgis_g):
                        capa_lazy = capas_res_cruce_esp.get(n) or self._crear_capa_cruce_lazy(n)
                        if capa_lazy:
                            QgsProject.instance().addMapLayer(capa_lazy)
                            b.setText("✓ En QGIS"); b.setEnabled(False)
                    btn_qgis_g.clicked.connect(_send_g)
                    tl_g.addWidget(btn_qgis_g)

                _geo_inner.addWidget(tc_g)

            n_geo = sum(i.get("n_features", 0) for i in todas_incons)
            titulo_geo = f"Geocódigos  —  {n_geo:,} inconsistencias" if n_geo else "Geocódigos"
            lay.addWidget(self._collapsible_section(titulo_geo, _geo_contenido))

        # ── Sección Verificación de Entrega ──────────────────────────────────────
        _ent_contenido = QWidget()
        _ent_inner = QVBoxLayout(_ent_contenido)
        _ent_inner.setContentsMargins(0, 0, 0, 0)
        _ent_inner.setSpacing(10)

        if not verificar_entrega:
            card_noop = self._card()
            cl_noop = QHBoxLayout(card_noop)
            cl_noop.setContentsMargins(16, 14, 16, 14)
            lbl_noop = QLabel("No solicitada en esta validación")
            lbl_noop.setStyleSheet(
                f"font-size:13px;color:{C_MUTED};background:transparent;border:none;"
            )
            cl_noop.addWidget(lbl_noop)
            _ent_inner.addWidget(card_noop)
        else:
            # ── Resultados Drive ──────────────────────────────────────────────
            card_drive = self._card()
            cl_d = QVBoxLayout(card_drive)
            cl_d.setContentsMargins(16, 14, 16, 14)
            cl_d.setSpacing(8)
            lbl_drive_t = QLabel("Carpeta Drive")
            lbl_drive_t.setStyleSheet(
                f"font-size:13px;font-weight:700;color:{C_TEXT};background:transparent;border:none;"
            )
            cl_d.addWidget(lbl_drive_t)

            if not drive_url:
                lbl_no_url = QLabel("⚠  Link de carpeta Drive no proporcionado — sin verificación de archivos")
                lbl_no_url.setStyleSheet(
                    f"font-size:12px;color:#F59E0B;background:transparent;border:none;"
                )
                lbl_no_url.setWordWrap(True)
                cl_d.addWidget(lbl_no_url)
            elif drive_url and not drive_archivos:
                lbl_url_ok = QLabel(f"🔗  {drive_url}")
                lbl_url_ok.setStyleSheet(
                    f"font-size:11px;color:{C_ACCENT};background:transparent;border:none;"
                )
                lbl_url_ok.setWordWrap(True)
                lbl_pendiente = QLabel(
                    "⚠  No se pudo listar el contenido de la carpeta Drive."
                )
                lbl_pendiente.setStyleSheet(
                    f"font-size:12px;color:#F59E0B;background:transparent;border:none;"
                )
                lbl_pendiente.setWordWrap(True)
                cl_d.addWidget(lbl_url_ok)
                cl_d.addWidget(lbl_pendiente)
            else:
                try:
                    from .utils.validar_documentacion import validar_archivos_carpeta
                    val = validar_archivos_carpeta(drive_archivos or [])
                except Exception:
                    val = {}
                encontrados = val.get("encontrados", {})
                _REQ = [
                    ("acta",    "Acta de Entrega (Word)"),
                    ("plan",    "Plan de Trabajo Global (Excel)"),
                    ("informe", "Informe de Actualización (PDF)"),
                ]
                for clave, etiq in _REQ:
                    nombre_arch = encontrados.get(clave)
                    row_d = QHBoxLayout()
                    lbl_req = QLabel(etiq)
                    lbl_req.setStyleSheet(
                        f"font-size:12px;color:{C_SUBTEXT};background:transparent;border:none;"
                    )
                    if nombre_arch:
                        badge_d = QLabel(f"✓  {nombre_arch}")
                        badge_d.setStyleSheet(
                            f"font-size:11px;font-weight:600;color:{C_OK};"
                            f"background:#052E16;border-radius:6px;padding:2px 8px;border:none;"
                        )
                    else:
                        badge_d = QLabel("✗  No encontrado")
                        badge_d.setStyleSheet(
                            f"font-size:11px;font-weight:600;color:{C_ERR};"
                            f"background:{C_ERR_DIM};border-radius:6px;padding:2px 8px;border:none;"
                        )
                    row_d.addWidget(lbl_req, 1)
                    row_d.addWidget(badge_d)
                    cl_d.addLayout(row_d)

                n_arch = len(drive_archivos or [])
                lbl_total = QLabel(f"{n_arch} archivo{'s' if n_arch!=1 else ''} en la carpeta")
                lbl_total.setStyleSheet(
                    f"font-size:11px;color:{C_MUTED};background:transparent;border:none;margin-top:4px;"
                )
                cl_d.addWidget(lbl_total)
            _ent_inner.addWidget(card_drive)

        titulo_ent = "Verificación de Entrega"
        lay.addWidget(self._collapsible_section(titulo_ent, _ent_contenido))

        lay.addWidget(_sep())

        # ── Botones de reporte ────────────────────────────────────────────────────
        es_interno   = getattr(self, "_modo_proceso", "interno") == "interno"
        # Fila de botones de reporte
        _rep_row = QHBoxLayout()
        _rep_row.setSpacing(10)

        btn_lbl_html = ("Abrir reporte" if es_interno else "Abrir reporte completo")
        btn_html = QPushButton("Generando reporte...")
        btn_html.setStyleSheet(STYLE_BTN_PRIMARY)
        btn_html.setEnabled(False)   # se activa cuando el reporte esté listo
        btn_html.setToolTip("El reporte se está generando, espera un momento...")
        self._btn_html_ref = btn_html   # referencia para activarlo desde actualizar_reporte

        def _abrir_html():
            ruta = self._datos.get("ruta_html", "")
            if ruta and os.path.exists(ruta):
                __import__("webbrowser").open(f"file:///{ruta.replace(chr(92), '/')}")
        btn_html.clicked.connect(_abrir_html)

        btn_guardar = QPushButton("Guardar reportes...")
        btn_guardar.setStyleSheet(STYLE_BTN_NEUTRAL)
        btn_guardar.setToolTip("Copia los reportes a una carpeta permanente de tu elección")
        btn_guardar.clicked.connect(
            lambda: self._guardar_reportes(self._datos.get("carpeta_rep", ""))
        )

        _rep_row.addWidget(btn_html)
        _rep_row.addWidget(btn_guardar)
        _rep_row.addStretch()
        lay.addLayout(_rep_row)

        # Activar el botón cuando el reporte esté listo
        def _activar_btn_html():
            try:
                ruta = self._datos.get("ruta_html", "")
                if ruta and os.path.exists(ruta):
                    btn_html.setText(btn_lbl_html)
                    btn_html.setEnabled(True)
                    btn_html.setToolTip("Abre el reporte en el navegador")
                elif btn_html.text() != "Error al generar reporte":
                    QTimer.singleShot(500, _activar_btn_html)
            except RuntimeError:
                pass  # btn_html fue eliminado al reconstruir la página — cancelar polling
        QTimer.singleShot(300, _activar_btn_html)

        # Referencia requerida internamente
        self._lbl_prueba = QLabel("")
        self._lbl_prueba.setVisible(False)
        lay.addStretch()

    def _guardar_reportes(self, carpeta_origen: str):
        """Copia los reportes de la carpeta temporal a una carpeta elegida por el usuario."""
        import shutil
        destino = QFileDialog.getExistingDirectory(
            self, "Seleccionar carpeta donde guardar los reportes",
            os.path.expanduser("~"),
            QFileDialog.ShowDirsOnly,
        )
        if not destino:
            return
        nombre = os.path.basename(carpeta_origen.rstrip("\\/"))
        destino_final = os.path.join(destino, nombre)
        try:
            shutil.copytree(carpeta_origen, destino_final)
            _info(self, "Reportes guardados",
                  f"Los reportes se copiaron a:\n{destino_final}")
        except FileExistsError:
            resp = _ask(self, "Carpeta ya existe",
                        f"Ya existe '{nombre}' en ese destino. ¿Reemplazar?")
            if resp == QMessageBox.Yes:
                shutil.rmtree(destino_final)
                shutil.copytree(carpeta_origen, destino_final)
                _info(self, "Reportes guardados",
                      f"Reportes guardados en:\n{destino_final}")
        except Exception:
            _crit(self, "No se pudo guardar la carpeta",
                  "Ocurrió un error al copiar los reportes.\n"
                  "Verifica que tengas permisos de escritura en la carpeta de destino "
                  "y que no haya archivos abiertos.")

    def _mostrar_estado_correo(self, texto: str, ok: bool = True):
        """Muestra el estado del envío de correo al final de la pantalla de resultados."""
        if not hasattr(self, "_lbl_estado_correo"):
            return
        color = C_OK if ok else C_ERR
        bg    = C_OK_DIM if ok else C_ERR_DIM
        self._lbl_estado_correo.setText(texto)
        self._lbl_estado_correo.setStyleSheet(
            f"font-size:12px;font-weight:600;color:{color};"
            f"background:{bg};padding:10px 16px;border-radius:8px;"
        )
        self._lbl_estado_correo.setVisible(True)

    def actualizar_reporte(self, ruta_html, archivos_csv, carpeta_rep, csv_resumen):
        """Llamado en segundo plano cuando el reporte ya fue generado."""
        self._datos["ruta_html"]    = ruta_html
        self._datos["archivos_csv"] = archivos_csv
        self._datos["carpeta_rep"]  = carpeta_rep
        self._datos["csv_resumen"]  = csv_resumen
        # Actualizar botón HTML ahora que el archivo existe
        try:
            if hasattr(self, "_btn_html_ref") and ruta_html and os.path.exists(ruta_html):
                self._btn_html_ref.setEnabled(True)
                self._btn_html_ref.setToolTip("Abre el reporte en el navegador")
        except RuntimeError:
            pass  # _btn_html_ref fue eliminado — ignorar

    def actualizar_ot_sheets(self, result: dict, modo_proceso: str):
        """Agrega la tarjeta de concordancia OT/Sheets al panel de resultados."""
        if not result:
            return

        es_final = (modo_proceso == "entrega")
        ot_num   = result.get("ot", "—")
        errores  = result.get("errores", [])
        cron     = result.get("cronograma")
        actas    = result.get("actas", [])
        entregas = result.get("entregas", [])
        ctrl     = result.get("control_ot")

        rows = []  # (nombre_hoja, encontrado, detalle)

        if cron:
            estado = cron.get("estado") or "—"
            fi     = cron.get("fecha_inicio") or "—"
            ff     = cron.get("fecha_fin")    or "—"
            rows.append(("Cronograma", True,
                         f"Estado: {estado}   Inicio: {fi}   Fin: {ff}"))
        else:
            rows.append(("Cronograma", False, "OT no encontrada — revisar Cronograma"))

        if actas:
            ult = actas[-1].get("fecha_acta") or "—"
            rows.append(("Actas de Entrega", True, f"{len(actas)} acta(s)   Última: {ult}"))
        else:
            rows.append(("Actas de Entrega", False, "OT no encontrada — revisar Actas de Entrega"))

        if entregas:
            ult = entregas[-1].get("fecha_entrega") or "—"
            rows.append(("Control Entregas", True, f"{len(entregas)} registro(s)   Última: {ult}"))
        else:
            rows.append(("Control Entregas", False, "OT no encontrada — revisar Control de Entregas"))

        if ctrl:
            estado = ctrl.get("estado") or "—"
            fi     = ctrl.get("fecha_inicio") or "—"
            ff     = ctrl.get("fecha_final")  or "—"
            rows.append(("Control de OT", True,
                         f"Estado: {estado}   Inicio: {fi}   Fin: {ff}"))
        else:
            rows.append(("Control de OT", False, "OT no encontrada — revisar Control de OT"))

        todo_ok   = all(ok for _, ok, _ in rows)
        faltantes = [s for s, ok, _ in rows if not ok]

        cuerpo = QWidget()
        cuerpo.setStyleSheet("background:transparent;")
        cl = QVBoxLayout(cuerpo)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(5)

        for err in errores:
            lbl_e = QLabel(f"⚠  {err}")
            lbl_e.setWordWrap(True)
            lbl_e.setStyleSheet(
                f"color:{C_WARN};font-size:11px;"
                f"background:{C_WARN_DIM};padding:6px 10px;border-radius:6px;"
            )
            cl.addWidget(lbl_e)

        for sheet_name, found, detail in rows:
            if found:
                ic, ic_col, bg, det_col = "✓", C_OK,  C_OK_DIM,   C_SUBTEXT
            elif es_final:
                ic, ic_col, bg, det_col = "✗", C_ERR, C_ERR_DIM,  C_ERR
            else:
                ic, ic_col, bg, det_col = "!", C_WARN, C_WARN_DIM, C_WARN

            row_w = QWidget()
            row_w.setStyleSheet(f"background:{bg};border-radius:7px;")
            rl = QHBoxLayout(row_w)
            rl.setContentsMargins(10, 7, 10, 7)
            rl.setSpacing(10)

            lbl_ic = QLabel(ic)
            lbl_ic.setFixedWidth(18)
            lbl_ic.setAlignment(Qt.AlignCenter)
            lbl_ic.setStyleSheet(
                f"color:{ic_col};font-size:13px;font-weight:700;"
                f"background:transparent;border:none;"
            )
            lbl_sn = QLabel(sheet_name)
            lbl_sn.setFixedWidth(155)
            lbl_sn.setStyleSheet(
                f"color:{C_TEXT};font-size:12px;font-weight:600;"
                f"background:transparent;border:none;"
            )
            lbl_dt = QLabel(detail)
            lbl_dt.setWordWrap(True)
            lbl_dt.setStyleSheet(
                f"color:{det_col};font-size:11px;background:transparent;border:none;"
            )
            rl.addWidget(lbl_ic)
            rl.addWidget(lbl_sn)
            rl.addWidget(lbl_dt, 1)
            cl.addWidget(row_w)

        if es_final:
            if todo_ok:
                res_txt = "Todo concordando — OT registrada en todos los documentos de control."
                res_col, res_bg = C_OK, C_OK_DIM
            else:
                res_txt = f"Hay discrepancias — OT ausente en: {', '.join(faltantes)}."
                res_col, res_bg = C_ERR, C_ERR_DIM
        else:
            if faltantes:
                res_txt = f"Revisar: falta registrar la OT en {', '.join(faltantes)}."
                res_col, res_bg = C_WARN, C_WARN_DIM
            else:
                res_txt = "OT registrada en todos los documentos de control."
                res_col, res_bg = C_OK, C_OK_DIM

        lbl_res = QLabel(res_txt)
        lbl_res.setWordWrap(True)
        lbl_res.setStyleSheet(
            f"font-size:12px;font-weight:600;color:{res_col};"
            f"background:{res_bg};padding:8px 12px;border-radius:7px;margin-top:4px;"
        )
        cl.addWidget(lbl_res)

        card = self._card()
        card_l = QVBoxLayout(card)
        card_l.setContentsMargins(20, 16, 20, 16)
        card_l.setSpacing(12)
        card_l.addWidget(
            self._collapsible_section(
                f"Control de Cronograma y OT  —  {ot_num}",
                cuerpo,
                abierto=True,
            )
        )
        self._lay_c.insertWidget(max(0, self._lay_c.count() - 1), card)

    def _crear_capa_cruce_lazy(self, nom_c):
        """Crea la capa de errores espaciales para 'nom_c' bajo demanda."""
        datos = self._datos_cruce_lazy.get(nom_c)
        if not datos:
            return None
        capa_orig, fid_items, tg = datos
        gtipo = ("LineString" if tg == "linea" else "Point" if tg == "punto" else "Polygon")
        crs   = capa_orig.crs().authid()
        capa_err = QgsVectorLayer(f"{gtipo}?crs={crs}", f"cruce_esp_{nom_c}", "memory")
        pr_e = capa_err.dataProvider()
        pr_e.addAttributes([
            QgsField("fid_orig",       QVariant.Int),
            QgsField("campo",          QVariant.String),
            QgsField("val_actual",     QVariant.String),
            QgsField("val_esperado",   QVariant.String),
            QgsField("pol_referencia", QVariant.String),
            QgsField("tipo_error",     QVariant.String),
        ])
        capa_err.updateFields()
        fid_to_info = {it[0]: it[1:] for it in fid_items}
        feats_err = []
        for feat in capa_orig.getFeatures(
            QgsFeatureRequest().setFilterFids(list(fid_to_info.keys()))
        ):
            info = fid_to_info.get(feat.id())
            if info is None:
                continue
            campo, val_a, val_e, pol_ref, tipo_e = info
            f_e = QgsFeature()
            f_e.setGeometry(feat.geometry())
            f_e.setAttributes([feat.id(), campo, val_a, val_e, pol_ref, tipo_e])
            feats_err.append(f_e)
        pr_e.addFeatures(feats_err)
        capa_err.updateExtents()
        return capa_err

    def _probar_conexion(self):
        from .utils import gmail_sender
        self._lbl_prueba.setText("Probando conexión...")
        self._lbl_prueba.setStyleSheet(f"font-size:12px;color:{C_SUBTEXT};")
        QApplication.processEvents()
        try:
            ok, detalle = gmail_sender.probar_conexion()
        except Exception as e:
            ok, detalle = False, f"Error inesperado: {e}"
        col = C_OK if ok else C_ERR
        self._lbl_prueba.setStyleSheet(
            f"font-size:12px;color:{col};background:{C_OK_DIM if ok else C_ERR_DIM};"
            f"padding:10px;border-radius:8px;border:1px solid {C_OK if ok else C_ERR};"
        )
        self._lbl_prueba.setText(detalle)

    @staticmethod
    def _msg_error_correo(exc):
        """Convierte una excepción SMTP en un mensaje legible para el usuario."""
        texto = str(exc)
        if "535" in texto or "BadCredentials" in texto or "Username and Password not accepted" in texto:
            return (
                "Credenciales no válidas.\n\n"
                "Si usas Gmail, debes usar una Contraseña de Aplicación en lugar "
                "de tu contraseña normal.\n\n"
                "Cómo generarla:\n"
                "  1. Ve a myaccount.google.com/apppasswords\n"
                "  2. Crea una nueva contraseña para 'CartoLATAM'\n"
                "  3. Usa esa clave (16 caracteres, sin espacios) en la configuración del correo."
            )
        return texto

    def _enviar(self):
        """Envía el correo en un hilo de fondo — no bloquea la UI."""
        import threading as _threading
        from .utils import gmail_sender
        from .utils.contador_intentos import obtener
        try:
            from qgis.core import QgsMessageLog, Qgis
            def _log(msg): QgsMessageLog.logMessage(msg, "CartoLATAM", Qgis.Info)
        except Exception:
            def _log(msg): pass

        _log(f"[_enviar] llamado — modo={getattr(self,'_modo_proceso','?')}")
        self._mostrar_estado_correo("Enviando correo...", ok=True)

        _, remitente, _ = gmail_sender._credenciales()
        if not remitente or remitente == "validacion@tudominio.com":
            _log("[_enviar] ABORTADO — remitente no configurado")
            _crit(self, "Remitente no configurado",
                  "Configura GMAIL_REMITENTE en tu archivo .env\n"
                  "o usa el botón Configurar correo.")
            return

        # Capturar todos los valores en el hilo principal ANTES de lanzar el hilo
        ecfg          = self._email_cfg or {}
        es_interno    = getattr(self, "_modo_proceso", "interno") == "interno"
        d             = self._datos
        orden         = ecfg.get("tarea", "")
        pais          = d.get("pais", "")
        responsable   = ecfg.get("responsable", "")
        colaboradores = ecfg.get("colaboradores", "")

        modo_set = d.get("modo", set())
        partes_alcance = []
        if "estructura" in modo_set: partes_alcance.append("Estructura")
        if "atributos"  in modo_set: partes_alcance.append("Atributos")
        if "topologia"  in modo_set: partes_alcance.append("Topología")
        if "geocodigos" in modo_set: partes_alcance.append("Geocódigos")
        tipo_alcance = ", ".join(partes_alcance) if partes_alcance else "Completa"

        para_lider = ""
        if not es_interno:
            para_lider = ecfg.get("para_c", "")
            if not para_lider:
                _crit(self, "Falta el correo del líder",
                      "Configura el correo del líder en la sección de correo.")
                return

        _log(f"[_enviar] iniciando hilo — interno={es_interno}, pais={pais}, orden={orden}")

        _res_correo = {}
        _correo_listo = _threading.Event()

        def _enviar_bg():
            import traceback as _tb
            try:
                if es_interno:
                    intento_actual = obtener(orden)
                    _log(f"[_enviar_bg] llamando enviar_reporte_interno — intento={intento_actual}")
                    _, destinatarios, _mid = gmail_sender.enviar_reporte_interno(
                        destinatarios=None,
                        stats_capas=d["stats"],
                        inconsistencias=d["inconsistencias"],
                        pais=pais,
                        tiempo_s=d["tiempo_s"],
                        orden=orden,
                        responsable=responsable,
                        colaboradores=colaboradores,
                        tipo_validacion=tipo_alcance,
                        numero_intento=intento_actual,
                        ruta_html=d["ruta_html"],
                        archivos_csv=d["archivos_csv"],
                        carpeta_rep=d["carpeta_rep"],
                        comentario=d.get("comentario", ""),
                        modo=modo_set,
                    )
                    _log(f"[_enviar_bg] reporte_interno OK → {destinatarios}")
                    if d.get("stats"):
                        _log("[_enviar_bg] llamando enviar_resumen_capas")
                        gmail_sender.enviar_resumen_capas(
                            destinatarios=destinatarios,
                            stats_capas=d["stats"],
                            pais=pais,
                            orden=orden,
                            drive_url=d.get("drive_url", ""),
                            in_reply_to=_mid,
                        )
                        _log("[_enviar_bg] resumen_capas OK")
                    _res_correo['ok']  = True
                    _res_correo['msg'] = f"✓  Correos enviados a: {', '.join(destinatarios)}"
                else:
                    intentos_prev = obtener(orden)
                    _log(f"[_enviar_bg] llamando enviar_reporte_entrega — intentos_prev={intentos_prev}")
                    _, destinatarios = gmail_sender.enviar_reporte_entrega(
                        destinatario_lider=para_lider,
                        stats_capas=d["stats"],
                        inconsistencias=d["inconsistencias"],
                        pais=pais,
                        tiempo_s=d["tiempo_s"],
                        orden=orden,
                        responsable=responsable,
                        tipo_validacion=tipo_alcance,
                        intentos_internos=intentos_prev,
                        ruta_html=d["ruta_html"],
                        archivos_csv=d["archivos_csv"],
                        carpeta_rep=d["carpeta_rep"],
                        comentario=d.get("comentario", ""),
                    )
                    _log(f"[_enviar_bg] entrega OK → {destinatarios}")
                    _res_correo['ok']  = True
                    _res_correo['msg'] = f"✓  Entrega enviada a: {', '.join(destinatarios)}"
            except Exception as e:
                _log(f"[_enviar_bg] ERROR: {_tb.format_exc()}")
                _res_correo['ok']   = False
                _res_correo['err']  = self._msg_error_correo(e)
                _res_correo['full'] = _tb.format_exc()
            finally:
                _correo_listo.set()

        def _poll_correo():
            """Polling en hilo principal — igual que _poll_resultado para _post_proceso."""
            if not _correo_listo.is_set():
                QTimer.singleShot(200, _poll_correo)
                return
            if _res_correo.get('ok'):
                self._mostrar_estado_correo(_res_correo['msg'], ok=True)
            else:
                err  = _res_correo.get('err', 'Error desconocido')
                full = _res_correo.get('full', '')
                self._mostrar_estado_correo(f"✗  Error: {err}", ok=False)
                try:
                    from qgis.utils import iface as _iface
                    _iface.messageBar().pushCritical("CartoLATAM — Error de correo", err)
                except Exception:
                    pass
                _crit(self, "Error al enviar correo",
                      f"{err}\n\nDetalle técnico:\n{full[:400]}")

        _threading.Thread(target=_enviar_bg, daemon=True).start()
        QTimer.singleShot(200, _poll_correo)


# .............................................................................
# DIÁLOGO PRINCIPAL
# .............................................................................

class DialogoPrincipal(QDialog):

    def __init__(self, iface, parent=None):
        super().__init__(parent)
        self._iface = iface
        self._drive_folder_url      = ""   # URL de carpeta Drive validada
        self._drive_archivos        = []   # Lista de archivos encontrados en la carpeta Drive
        self._doc_validation_result = None  # Resultado de validar_documentacion() (futuro)
        self.setWindowTitle("Validaciones CartoLatam — Servinformación")
        self.setMinimumSize(920, 760)
        self.resize(1020, 860)
        self.setStyleSheet(f"background:{C_ROOT};")
        # Ventana independiente: minimizable, maximizable y sin bloquear QGIS
        self.setWindowFlags(
            Qt.Window |
            Qt.WindowMinimizeButtonHint |
            Qt.WindowMaximizeButtonHint |
            Qt.WindowCloseButtonHint
        )

        from .utils.sheets_loader import paises_disponibles
        paises = paises_disponibles()

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # ── Barra de navegación — branding + stepper en dos filas ────────────────
        self._nav_bar = QWidget()
        self._nav_bar.setStyleSheet(
            f"background:{C_SURFACE};border-bottom:1px solid {C_BORDER};"
        )
        nav_main = QVBoxLayout(self._nav_bar)
        nav_main.setContentsMargins(0, 0, 0, 0)
        nav_main.setSpacing(0)

        # Fila 1 — Branding
        _branding = QWidget()
        _branding.setStyleSheet(f"background:{C_SURFACE};")
        _bl = QHBoxLayout(_branding)
        _bl.setContentsMargins(20, 10, 20, 8)
        _bl.setSpacing(12)

        _icon_path = os.path.join(PLUGIN_DIR, "icon.png")
        if os.path.exists(_icon_path):
            _logo_lbl = QLabel()
            _logo_lbl.setStyleSheet("background:transparent;")
            _logo_pix = QPixmap(_icon_path).scaled(
                32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            _logo_lbl.setPixmap(_logo_pix)
            _logo_lbl.setFixedSize(32, 32)
            _bl.addWidget(_logo_lbl)

        _lbl_brand = QWidget()
        _lbl_brand.setStyleSheet("background:transparent;")
        _bb = QVBoxLayout(_lbl_brand)
        _bb.setContentsMargins(0, 0, 0, 0)
        _bb.setSpacing(1)
        _lbl_name = QLabel("CartoLatam Validador")
        _lbl_name.setStyleSheet(
            f"font-size:14px;font-weight:700;color:{C_TEXT};"
            f"background:transparent;letter-spacing:-0.2px;"
        )
        _lbl_sub = QLabel("Validación cartográfica y control de calidad")
        _lbl_sub.setStyleSheet(
            f"font-size:10px;color:{C_MUTED};background:transparent;"
        )
        _bb.addWidget(_lbl_name)
        _bb.addWidget(_lbl_sub)
        _bl.addWidget(_lbl_brand)
        _bl.addStretch()
        nav_main.addWidget(_branding)

        # Fila 2 — Stepper
        _stepper = QWidget()
        _stepper.setStyleSheet(
            f"background:{C_ROOT};border-top:1px solid {C_BORDER};"
        )
        _sl = QHBoxLayout(_stepper)
        _sl.setContentsMargins(20, 0, 20, 0)
        _sl.setSpacing(0)

        self._nav_btns    = []
        self._paso_actual  = 0
        self._pasos_vistos = {0}

        _PASOS_NAV = [
            ("Selección",  "Elegir capas, país y tipo de validación"),
            ("Progreso",   "Estado y avance del proceso en ejecución"),
            ("Resultados", "Resultados, reportes y envío por correo"),
        ]
        for idx, (etiq, tip) in enumerate(_PASOS_NAV):
            if idx > 0:
                linea = QFrame()
                linea.setFrameShape(QFrame.HLine)
                linea.setFixedWidth(32)
                linea.setStyleSheet(
                    f"color:{C_BORDER_2};background:{C_BORDER_2};max-height:1px;"
                )
                _sl.addWidget(linea)

            btn = QPushButton(etiq)
            btn.setToolTip(tip)
            btn.setEnabled(idx == 0)
            btn.setFixedHeight(36)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, i=idx: self._ir_a(i))
            self._nav_btns.append(btn)
            _sl.addWidget(btn)

        _sl.addStretch()
        nav_main.addWidget(_stepper)

        lay.addWidget(self._nav_bar)

        self.stack = QStackedWidget()
        self.pag_sel = _PaginaSeleccion(iface, paises)
        self.pag_pro = _PaginaProgreso()
        self.pag_res = _PaginaResultados()
        self.stack.addWidget(self.pag_sel)
        self.stack.addWidget(self.pag_pro)
        self.stack.addWidget(self.pag_res)
        lay.addWidget(self.stack, 1)

        # Barra de botones página 0
        self._barra_btn = QWidget()
        self._barra_btn.setStyleSheet(
            f"background:{C_SURFACE};border-top:1px solid {C_BORDER};"
        )
        frow = QHBoxLayout(self._barra_btn)
        frow.setContentsMargins(20, 10, 20, 12)
        self._btn_cancel_sel = QPushButton("Cancelar")
        self._btn_cancel_sel.setStyleSheet(STYLE_BTN_DANGER)
        self._btn_cancel_sel.setToolTip("Cerrar sin validar")
        self._btn_validar = QPushButton("Validar")
        self._btn_validar.setStyleSheet(STYLE_BTN_PRIMARY)
        self._btn_validar.setToolTip("Iniciar el proceso de validación según el modo seleccionado")
        self._btn_cancel_sel.clicked.connect(self.reject)
        self._btn_validar.clicked.connect(self._iniciar)
        frow.addStretch()
        frow.addWidget(self._btn_cancel_sel)
        frow.addWidget(self._btn_validar)
        lay.addWidget(self._barra_btn)

        self.pag_res.btn_nueva.clicked.connect(self._nueva_validacion)
        self.pag_res.btn_cerrar.clicked.connect(self.accept)

        # Actualizar texto del botón Validar cuando cambie algún chip
        def _actualizar_btn_texto():
            modo = self.pag_sel.modo_validacion()
            partes = []
            if "estructura" in modo: partes.append("Estructura")
            if "atributos"  in modo: partes.append("Atributos")
            if "topologia"  in modo: partes.append("Topología")
            if "geocodigos" in modo: partes.append("Geocódigos")
            self._btn_validar.setText(
                f"Validar  {' + '.join(partes)}" if partes else "Validar"
            )
        for btn in self.pag_sel._chips.values():
            btn.clicked.connect(_actualizar_btn_texto)
        _actualizar_btn_texto()

        # Aplicar estilos iniciales a la barra de navegación
        self._actualizar_nav(0)

    # ── Estilos de la barra de navegación ────────────────────────────────────────
    # Wizard nav — 3 estados: activo · completado · bloqueado
    _STYLE_NAV_ACTIVO = (
        f"QPushButton{{background:transparent;color:{C_ACCENT};"
        f"padding:0 16px;font-size:12px;font-weight:700;border:none;border-radius:0;"
        f"border-bottom:2px solid {C_ACCENT};}}"
    )
    _STYLE_NAV_VISTO = (
        f"QPushButton{{background:transparent;color:{C_OK};"
        f"padding:0 16px;font-size:12px;font-weight:600;border:none;border-radius:0;"
        f"border-bottom:2px solid {C_OK};}}"
        f"QPushButton:hover{{background:{C_OK_DIM};}}"
    )
    _STYLE_NAV_BLOQUEADO = (
        f"QPushButton{{background:transparent;color:{C_MUTED};"
        f"padding:0 16px;font-size:12px;font-weight:400;border:none;border-radius:0;}}"
    )

    def _actualizar_nav(self, idx_activo):
        self._paso_actual = idx_activo
        for i, btn in enumerate(self._nav_btns):
            if i == idx_activo:
                btn.setStyleSheet(self._STYLE_NAV_ACTIVO)
                btn.setEnabled(True)
            elif i in self._pasos_vistos:
                btn.setStyleSheet(self._STYLE_NAV_VISTO)
                btn.setEnabled(True)
            else:
                btn.setStyleSheet(self._STYLE_NAV_BLOQUEADO)
                btn.setEnabled(False)

    def _ir_a(self, idx):
        self._pasos_vistos.add(idx)
        self.stack.setCurrentIndex(idx)
        self._barra_btn.setVisible(idx == 0)
        self._actualizar_nav(idx)

    def _nueva_validacion(self):
        self._pasos_vistos = {0}   # reiniciar navegación
        self._ir_a(0)
        self.pag_sel.lbl_estado.setStyleSheet(f"font-size:12px;color:{C_SUBTEXT};")
        self.pag_sel.lbl_estado.setText("")

    def _iniciar(self):
        capas      = self.pag_sel.capas_seleccionadas()
        email_cfg  = self.pag_sel.email_config()
        if not self.pag_sel.pais_seleccionado():
            self.pag_sel.lbl_estado.setStyleSheet(f"font-size:12px;color:{C_ERR};")
            self.pag_sel.lbl_estado.setText("Selecciona un país antes de validar.")
            return
        if not capas:
            self.pag_sel.lista.setStyleSheet(
                f"QListWidget{{background:{C_WHITE};border:2px solid {C_ERR};"
                f"border-radius:8px;outline:none;padding:4px;}}"
            )
            self.pag_sel.lbl_estado.setStyleSheet(f"font-size:12px;color:{C_ERR};")
            self.pag_sel.lbl_estado.setText("Selecciona al menos una capa para validar.")
            return
        self.pag_sel.lista.setStyleSheet("")

        if "geocodigos" in self.pag_sel.modo_validacion():
            capas_admin = self.pag_sel.capas_referencia_geocodigos()
            if not capas_admin:
                self.pag_sel.lista_georef.setStyleSheet(
                    f"QListWidget{{background:{C_WHITE};border:2px solid {C_ERR};"
                    f"border-radius:8px;outline:none;padding:4px;}}"
                )
                self.pag_sel.lbl_estado.setStyleSheet(f"font-size:12px;color:{C_ERR};")
                self.pag_sel.lbl_estado.setText(
                    "Geocódigos está activo — selecciona al menos una capa administrativa de referencia."
                )
                return
            self.pag_sel.lista_georef.setStyleSheet("")
        self.pag_sel.lbl_estado.setStyleSheet(f"font-size:12px;color:{C_SUBTEXT};")
        self.pag_sel.lbl_estado.setText("")

        # Capturar URL del Drive siempre que haya texto (independiente del toggle)
        self._drive_folder_url = self.pag_sel._txt_drive_url.text().strip()

        # Lanzar verificación de OT en sheets en paralelo (no bloquea la UI)
        import threading as _threading
        _ot_num = self.pag_sel.orden_num_seleccionada()
        self._ot_result_box  = [None]
        self._hilo_ot_sheets = None
        if _ot_num:
            from .utils.sheets_loader import verificar_ot_en_sheets as _ver_ot
            def _ot_bg():
                try:
                    self._ot_result_box[0] = _ver_ot(_ot_num)
                except Exception as _e:
                    self._ot_result_box[0] = {
                        "ot": _ot_num, "cronograma": None,
                        "actas": [], "entregas": [], "control_ot": None,
                        "errores": [str(_e)],
                    }
            self._hilo_ot_sheets = _threading.Thread(target=_ot_bg, daemon=True)
            self._hilo_ot_sheets.start()

        # Lanzar listado de carpeta Drive en background (si hay URL)
        self._drive_archivos_box = [None]
        self._hilo_drive = None
        _drive_url_listed = self._drive_folder_url
        if _drive_url_listed and self.pag_sel._btn_ver_entrega.isChecked():
            from .utils.validar_documentacion import (
                extraer_id_drive as _ext_id, listar_carpeta_drive as _listar)
            def _drive_bg():
                try:
                    fid = _ext_id(_drive_url_listed)
                    self._drive_archivos_box[0] = _listar(fid) if fid else []
                except Exception:
                    self._drive_archivos_box[0] = []
            self._hilo_drive = _threading.Thread(target=_drive_bg, daemon=True)
            self._hilo_drive.start()

        pais          = self.pag_sel.pais()
        modo          = self.pag_sel.modo_validacion()
        modo_proceso  = self.pag_sel.modo_proceso()
        producto      = self.pag_sel.producto()
        self._ir_a(1)
        self.pag_pro.reiniciar(pais, len(capas), chips=modo)
        QApplication.processEvents()

        from .utils.sheets_loader import (cargar_todo as _cargar_todo,
                                          cargar_esquema_estructura as _cargar_estructura)

        abreviaturas_tv    = set()
        estandarizacion_tv = {}
        abreviaturas_urb   = set()
        categorias_validas = None
        esquema_estructura  = {}
        error_est_msg       = ""   # descripción del error si el esquema no cargó
        incluir_topo   = self.pag_sel.topologia_activa()
        capa_manzana_r = self.pag_sel.capa_manzana_ref() if incluir_topo else None
        capas_ref_geo  = self.pag_sel.capas_referencia_geocodigos()

        hacer_atrib_ini      = "atributos"  in modo
        hacer_estructura_ini = "estructura" in modo

        # Si no se necesita ningún catálogo de Sheets → ir directo
        if not hacer_atrib_ini and not hacer_estructura_ini:
            self.pag_pro.lbl_capa.setText("Iniciando validación...")
            self.pag_pro.lbl_fase.setText("")
            QApplication.processEvents()
            self._ejecutar(pais, capas, set(), {}, set(), None,
                           incluir_topo=incluir_topo, capa_manzana_ref=capa_manzana_r,
                           modo=modo, capas_ref_geo=capas_ref_geo,
                           email_cfg=email_cfg, modo_proceso=modo_proceso,
                           esquema_estructura={}, producto=producto,
                           error_est_msg="")
            return

        self.pag_pro.lbl_capa.setText("Cargando datos desde Google Sheets...")
        self.pag_pro.lbl_fase.setText("Cargando catálogos en paralelo...")
        QApplication.processEvents()

        avisos  = []
        n_partes = []

        if hacer_atrib_ini:
            try:
                dict_tv, dict_urb, categorias_validas, cat_err = _cargar_todo(pais)
                abreviaturas_tv    = set(dict_tv.keys())
                estandarizacion_tv = dict_tv
                abreviaturas_urb   = set(dict_urb.keys()) if dict_urb else set()
                if cat_err:
                    avisos.append(f"Categorías: {cat_err}")
                    n_partes.append(f"{len(abreviaturas_tv)} abreviaturas VIA"
                                    f" · {len(abreviaturas_urb)} URB · Sin categorías")
                else:
                    n_c = len(categorias_validas)
                    n_s = sum(len(v) for v in categorias_validas.values())
                    n_partes.append(f"✓ {len(abreviaturas_tv)} VIA"
                                    f" · {len(abreviaturas_urb)} URB"
                                    f" · {n_c} cat · {n_s} subcat")
            except Exception as e:
                avisos.append(f"Abreviaturas: {e}")
                n_partes.append(f"⚠ Sin abreviaturas")
            QApplication.processEvents()

        if hacer_estructura_ini:
            from .utils.sheets_loader import PAISES_HOJAS_ESTRUCTURA as _PH_EST
            try:
                esquema_estructura = _cargar_estructura(pais)
                n_esq = len(esquema_estructura)
                if n_esq:
                    n_partes.append(f"✓ {n_esq} esquemas de estructura")
                else:
                    _hoja = _PH_EST.get(pais, "?")
                    error_est_msg = (f"La hoja '{_hoja}' existe pero no contiene filas. "
                                     f"Verifica que las columnas tengan los nombres correctos.")
                    avisos.append(f"Esquema de estructura: {error_est_msg}")
                    n_partes.append("⚠ Esquema vacío")
            except Exception as e_est:
                _hoja = _PH_EST.get(pais, "?")
                error_est_msg = f"Pestaña '{_hoja}': {e_est}"
                avisos.append(f"Esquema de estructura: {error_est_msg}")
                n_partes.append("⚠ Sin esquema de estructura")
            QApplication.processEvents()

        self.pag_pro.lbl_fase.setText("  ·  ".join(n_partes))
        QApplication.processEvents()

        if avisos:
            _warn(self, "Advertencia — Google Sheets",
                  "No se pudieron cargar algunos datos de Google Sheets.\n"
                  "La validación continuará sin ellos.\n\n" + "\n".join(avisos))

        self.pag_pro.lbl_capa.setText("Iniciando validación...")
        self.pag_pro.lbl_fase.setText("")
        QApplication.processEvents()

        self._ejecutar(pais, capas, abreviaturas_tv, estandarizacion_tv,
                       abreviaturas_urb, categorias_validas,
                       incluir_topo=incluir_topo, capa_manzana_ref=capa_manzana_r,
                       modo=modo, capas_ref_geo=capas_ref_geo,
                       email_cfg=email_cfg, modo_proceso=modo_proceso,
                       esquema_estructura=esquema_estructura, producto=producto,
                       error_est_msg=error_est_msg)

    def _ejecutar(self, pais, capas, abreviaturas_tv, estandarizacion_tv,
                  abreviaturas_urb, categorias_validas,
                  incluir_topo=False, capa_manzana_ref=None, modo=None,
                  capas_ref_geo=None, email_cfg=None, modo_proceso="interno",
                  esquema_estructura=None, producto="produccion",
                  error_est_msg=""):
        from .utils.config       import (CAMPOS_CONOCIDOS, BATCH_SIZE, UI_CADA,
                                        normalizar, chunk_list)
        from .utils._worker      import validar_chunk

        modo = modo or set()
        hacer_estructura = "estructura" in modo
        hacer_atrib      = "atributos"  in modo
        hacer_topo       = "topologia"  in modo and incluir_topo
        hacer_geo        = "geocodigos" in modo

        pro = self.pag_pro
        t_global    = time.time()
        total_capas = len(capas)
        capas_stats = []

        # Pre-cargar manzana una sola vez en hilo principal antes del bucle
        manz_dict   = {}
        idx_manz    = None
        nom_manzana = ""
        if incluir_topo and capa_manzana_ref is not None:
            from .utils import topologia as _topo
            pro.lbl_capa.setText("Pre-cargando capa manzana...")
            QApplication.processEvents()
            manz_dict, idx_manz = _topo.precargar_manzana(capa_manzana_ref)
            nom_manzana = capa_manzana_ref.name()

        # QgsSpatialIndex usa libspatialindex que no es seguro para instancias concurrentes
        # en Windows — se limita a 1 hilo para evitar access violations.
        _topo_executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

        from .utils.cruce_capas  import construir_indice as _construir_indice
        from .utils.reporte_html import construir_stats   as _construir_stats

        # ThreadPoolExecutor para validación de atributos (multiprocessing no es compatible
        # con plugins QGIS por conflicto de rutas de importación en el pickle de funciones).
        _cpus      = os.cpu_count() or 1
        _n_workers = max(1, _cpus - 1)
        _pool_atrib = concurrent.futures.ThreadPoolExecutor(max_workers=_n_workers) if hacer_atrib else None

        for n_capa, capa in enumerate(capas, start=1):
            if pro.fue_cancelado():
                break

            pro.set_capa(n_capa, total_capas, capa.name())
            QApplication.processEvents()

            tg       = _tipo_geom(capa)
            es_linea = tg == "linea"
            es_punto = tg == "punto"

            total_feat = capa.featureCount()
            if total_feat == 0:
                pro.capa_completada(capa.name(), 0, 0, 0.0)
                QApplication.processEvents()
                continue
            campos_capa = {f.name() for f in capa.fields()}
            campos_v    = campos_capa & CAMPOS_CONOCIDOS
            campos_ext  = campos_capa - CAMPOS_CONOCIDOS
            _noms_lista = list(capa.fields().names())
            _noms_idx   = {n: i for i, n in enumerate(_noms_lista)}
            idx_campos  = {c: _noms_idx[c] for c in campos_v if c in _noms_idx}

            # PASO 0 — Validación de estructura (siempre primero, no lee features)
            errs_estructura = None   # None = no validado; [] = OK; [...] = errores
            if hacer_estructura:
                pro._set_etapa_estado("estructura", "activa")
                pro.lbl_fase.setText("Verificando estructura de campos...")
                QApplication.processEvents()
                if esquema_estructura:
                    from .utils.estructura_capa import validar_estructura as _validar_estructura
                    _campos_info = {
                        f.name(): {"tipo_int": f.type(), "longitud": f.length()}
                        for f in capa.fields()
                    }
                    errs_estructura = _validar_estructura(
                        capa.name(), _campos_info, esquema_estructura, producto
                    )
                else:
                    _msg_est = error_est_msg if error_est_msg else (
                        "No se pudo cargar el esquema del país desde Google Sheets. "
                        "Verifica la conexión y que la hoja del país esté disponible."
                    )
                    errs_estructura = [f"[SIN ESQUEMA] {_msg_est}"]
                pro._set_etapa_estado("estructura", "hecha")
                pro.lbl_fase.setText("")
                QApplication.processEvents()

            t_capa = time.time()

            datos          = []
            geoms_topo     = {}
            invalidos_geom = []
            _topo_future   = None
            _topo_prog     = [0, max(1, total_feat)]

            if hacer_atrib or hacer_geo:
                # Fase 1a — lectura de atributos (sin geometría, más rápido)
                pro.set_fase(1, f"Leyendo {total_feat:,} atributos...", total_feat)
                QApplication.processEvents()
                req = (QgsFeatureRequest()
                       .setSubsetOfAttributes(list(idx_campos.values()))
                       .setFlags(QgsFeatureRequest.NoGeometry))
                for i, feat in enumerate(capa.getFeatures(req)):
                    datos.append((feat.id(), {
                        c: normalizar(feat.attributes()[idx_campos[c]])
                        for c in campos_v if c in idx_campos
                    }))
                    if i % UI_CADA == 0:
                        pro.set_valor(i, f"{i:,} / {total_feat:,} atributos")
                        QApplication.processEvents()
                        if pro.fue_cancelado(): break
                if pro.fue_cancelado(): break
                pro.set_valor(total_feat)

            # Fase 1b — lectura solo de geometrías (topología)
            if hacer_topo:
                pro.set_fase(1, f"Leyendo {total_feat:,} geometrías para topología...", total_feat)
                QApplication.processEvents()
                req_geo = QgsFeatureRequest().setSubsetOfAttributes([])
                for i, feat in enumerate(capa.getFeatures(req_geo)):
                    fid = feat.id()
                    g   = feat.geometry()
                    if g.isNull():
                        invalidos_geom.append({"fid": fid, "regla": "geometria_invalida",
                                               "descripcion": "Geometría nula"})
                    elif not g.isGeosValid():
                        invalidos_geom.append({"fid": fid, "regla": "geometria_invalida",
                                               "descripcion": f"Geometría inválida (GEOS): {g.lastError() or '—'}"})
                    else:
                        geoms_topo[fid] = g
                    if i % UI_CADA == 0:
                        pro.set_valor(i, f"{i:,} / {total_feat:,} geometrías")
                        QApplication.processEvents()
                        if pro.fue_cancelado(): break
                if pro.fue_cancelado(): break
                pro.set_valor(total_feat)

            contador_ids = None
            if hacer_atrib and "id_capa" in campos_v:
                contador_ids = Counter(d.get("id_capa") for _, d in datos)

            # Lanzar topología en hilo (en paralelo con atributos cuando modo=todo)
            if hacer_topo and geoms_topo:
                from .utils import topologia as _topo

                def _topo_cb(done, total, _p=_topo_prog):
                    _p[0] = done   # escritura atómica — GIL garantiza seguridad
                    _p[1] = total

                if tg == "poligono":
                    _topo_future = _topo_executor.submit(
                        _topo.validar_poligonos_desde_geoms,
                        geoms_topo, invalidos_geom, capa.name(),
                        pro.fue_cancelado, _topo_cb,
                    )
                elif tg == "linea":
                    _topo_future = _topo_executor.submit(
                        _topo.validar_lineas_desde_geoms,
                        geoms_topo, invalidos_geom, capa.name(),
                        manz_dict, idx_manz, nom_manzana,
                        pro.fue_cancelado, _topo_cb,
                    )
                elif tg == "punto":
                    _topo_future = _topo_executor.submit(
                        _topo.validar_puntos_desde_geoms,
                        geoms_topo, invalidos_geom, capa.name(),
                        manz_dict, idx_manz, nom_manzana,
                        pro.fue_cancelado, _topo_cb,
                    )
                del geoms_topo, invalidos_geom  # liberar referencias en hilo principal

            resultados = []
            if hacer_atrib:
                # Fase 2 — validación de atributos con ThreadPoolExecutor (pool compartido)
                n_workers = _n_workers
                n_chunks  = n_workers * 4
                chunks    = chunk_list(datos, n_chunks)
                pool_args = [
                    (chunk, campos_v, (es_linea, es_punto, tg == "poligono"),
                     contador_ids, abreviaturas_tv, estandarizacion_tv,
                     abreviaturas_urb, categorias_validas, pais, PLUGIN_DIR)
                    for chunk in chunks
                ]
                pro.set_fase(2, f"Validando con {n_workers} hilos...", len(chunks))
                QApplication.processEvents()

                t_val = time.time()
                for chunk_res in _pool_atrib.map(validar_chunk, pool_args):
                    resultados.extend(chunk_res)
                    elapsed   = time.time() - t_val
                    feat_proc = len(resultados)
                    rate      = feat_proc / elapsed if elapsed > 0 else 0
                    t_pct     = min(int(_topo_prog[0] * 100 / _topo_prog[1]), 100)
                    topo_txt  = f"  |  Topo: {t_pct}%" if _topo_future else ""
                    pro.set_valor(
                        len(resultados) // (len(datos) // len(chunks) + 1),
                        f"{feat_proc:,} features  ·  {rate:,.0f} feat/s{topo_txt}",
                    )
                    QApplication.processEvents()
                    if pro.fue_cancelado():
                        break
                if pro.fue_cancelado(): break

            capa_res = None
            if hacer_atrib:
                # Fase 3 — escribir resultados en capa QGIS
                pro.set_fase(3, f"Escribiendo {len(resultados):,} resultados en QGIS...", len(resultados))
                QApplication.processEvents()
                nombre_res = f"validacion_{capa.name()}"
                capa_res   = QgsVectorLayer("NoGeometry", nombre_res, "memory")
                pr_prov    = capa_res.dataProvider()
                pr_prov.addAttributes([
                    QgsField("fila_id", QVariant.Int),
                    QgsField("estado",  QVariant.String),
                    QgsField("campo",   QVariant.String),
                    QgsField("valor",   QVariant.String),
                    QgsField("error",   QVariant.String),
                ])
                capa_res.updateFields()

                batch = []; total_ok_c = total_error = 0
                for i, (fid, d, errs) in enumerate(resultados):
                    if errs:
                        total_error += 1
                        for campo_e, msgs in errs.items():
                            for msg in msgs:
                                f = QgsFeature()
                                f.setAttributes([fid, "ERROR", campo_e, str(d.get(campo_e, "")), msg])
                                batch.append(f)
                    else:
                        total_ok_c += 1
                        f = QgsFeature()
                        f.setAttributes([fid, "OK", "", "", ""])
                        batch.append(f)
                    if len(batch) >= BATCH_SIZE:
                        pr_prov.addFeatures(batch); batch.clear()
                    if i % UI_CADA == 0:
                        pro.set_valor(i); QApplication.processEvents()
                if batch:
                    pr_prov.addFeatures(batch)

            if not hacer_atrib:
                total_error = 0

            seg_capa = time.time() - t_capa
            pro.capa_completada(capa.name(), total_feat, total_error, seg_capa)
            QApplication.processEvents()

            # Recoger topología: inmediato en modo mixto, diferido en modo topología pura
            errores_topo  = []
            _fut_diferido = None
            if _topo_future is not None:
                if modo == "topologia":
                    # Se recoge después del bucle junto con todos los demás (paralelismo real)
                    _fut_diferido = _topo_future
                else:
                    while True:
                        try:
                            errores_topo = _topo_future.result(timeout=0.1)
                            break
                        except concurrent.futures.TimeoutError:
                            if pro.fue_cancelado():
                                break
                            t_pct = min(int(_topo_prog[0] * 100 / _topo_prog[1]), 100)
                            pro.lbl_fase.setText(f"Finalizando topología? {t_pct}%")
                            pro.set_valor(_topo_prog[0],
                                          f"Topología: {_topo_prog[0]:,} / {_topo_prog[1]:,}")
                            QApplication.processEvents()
                        except Exception as exc_t:
                            errores_topo = [{"fid": -1, "regla": "error_interno",
                                             "descripcion": str(exc_t)}]
                            break

            # Calcular índice de cruce y stats inmediatamente para liberar datos/resultados
            if hacer_atrib or hacer_geo:
                _campos_c  = set(datos[0][1].keys()) if datos else set()
                _cruce_idx = _construir_indice(datos, _campos_c, pais)
            else:
                _cruce_idx = {}
            del datos

            _stats_c = _construir_stats(capa.name(), resultados) if hacer_atrib else None
            del resultados

            capas_stats.append({
                "nombre":             capa.name(),
                "tipo_geom":          tg,
                "n_registros":        total_feat,
                "capa":               capa,
                "capa_res":           capa_res,
                "cruce_idx":          _cruce_idx,
                "stats_c":            _stats_c,
                "campos_ext":         sorted(campos_ext) if hacer_atrib else [],
                "errores_topo":       errores_topo,
                "estructura_errores": errs_estructura,   # None=no validado, []=OK, [...]=errores
                "_topo_fut":          _fut_diferido,
            })

        if _pool_atrib is not None:
            _pool_atrib.shutdown(wait=False)

        # Recoger resultados de topología diferidos (modo topología con múltiples capas)
        pendientes = [(cs, cs.pop("_topo_fut")) for cs in capas_stats
                      if cs.get("_topo_fut") is not None]
        if pendientes:
            pro.lbl_capa.setText(f"Finalizando topología de {len(pendientes)} capa(s)...")
            QApplication.processEvents()
            for cs, fut in pendientes:
                try:
                    cs["errores_topo"] = fut.result(timeout=600)
                except Exception as exc_t:
                    cs["errores_topo"] = [{"fid": -1, "regla": "error_interno",
                                           "descripcion": str(exc_t)}]
        # Limpiar clave interna de futures (si no fue movida arriba)
        for cs in capas_stats:
            cs.pop("_topo_fut", None)

        pro.finalizar(total_capas)
        t_total = time.time() - t_global

        if not capas_stats:
            return

        from .utils.cruce_capas  import validar_cruce, validar_cruce_espacial
        from .utils.reporte_html import generar as generar_html

        indices   = []
        stats_rep = []
        if hacer_atrib or hacer_geo:
            for cs in capas_stats:
                indices.append((cs["nombre"], cs["tipo_geom"], cs["cruce_idx"]))
        if hacer_atrib:
            for cs in capas_stats:
                if cs["stats_c"] is not None:
                    _est = cs.get("estructura_errores")   # None, [] o [errores...]
                    cs["stats_c"]["estructura_errores"] = _est if _est is not None else []
                    cs["stats_c"]["estructura_validada"] = _est is not None
                    cs["stats_c"]["tipo_geom"] = cs["tipo_geom"]
                    stats_rep.append(cs["stats_c"])
        elif hacer_estructura:
            # Solo estructura (sin atributos): armar stats mínimos por capa
            for cs in capas_stats:
                _est = cs.get("estructura_errores")
                if _est is not None:
                    stats_rep.append({
                        "nombre":               cs["nombre"],
                        "tipo_geom":            cs["tipo_geom"],
                        "total":                cs["n_registros"],
                        "sin_error":            0,
                        "con_error":            0,
                        "pct_calidad":          100,
                        "campos_ordenados":     [],
                        "errores_por_campo":    {},
                        "estructura_errores":   _est,
                        "estructura_validada":  True,
                    })

        # Construir índices y lista de QgsVectorLayer para capas de referencia externas
        indices_ref     = []
        capas_ref_lista = []
        if hacer_geo and capas_ref_geo:
            pro.lbl_capa.setText("Indexando capas de referencia geocódigos...")
            QApplication.processEvents()
            for capa_r in capas_ref_geo:
                _campos_r = {f.name() for f in capa_r.fields()} & CAMPOS_CONOCIDOS
                _datos_r  = [
                    (feat.id(), {c: normalizar(feat[c]) for c in _campos_r
                                 if feat[c] is not None})
                    for feat in capa_r.getFeatures(
                        QgsFeatureRequest().setFlags(QgsFeatureRequest.NoGeometry)
                    )
                ]
                _idx_r = _construir_indice(_datos_r, _campos_r, pais)
                indices_ref.append((capa_r.name(), _idx_r))
                capas_ref_lista.append((capa_r.name(), "poligono", capa_r))

        inconsistencias = validar_cruce(
            indices, pais,
            capas_ref=indices_ref if indices_ref else None,
        ) if (indices or indices_ref) else []

        # Cruce placa ↔ mavvial (id_mavvial = id_capa, campos tipovia/nomvia/nomvtotal/generadora)
        if hacer_atrib:
            from .utils.cruce_capas import validar_cruce_placa_mavvial as _cruce_placa_mav
            inconsistencias = inconsistencias + _cruce_placa_mav(capas_stats)

        # Validación espacial: ¿están los features dentro del polígono correcto?
        _hay_pols_disp = (
            any(cs["tipo_geom"] == "poligono" for cs in capas_stats)
            or bool(capas_ref_lista)
        )
        _hay_no_pols = any(cs["tipo_geom"] != "poligono" for cs in capas_stats)
        if hacer_geo and _hay_pols_disp and _hay_no_pols and not pro.fue_cancelado():
            pro.lbl_capa.setText("Validando concordancia espacial y de códigos...")
            pro.lbl_fase.setText("")
            QApplication.processEvents()
            capas_con_tipo = [(cs["nombre"], cs["tipo_geom"], cs["capa"])
                              for cs in capas_stats]

            def _cb_espacial(n, total):
                pro.set_valor(n, f"Cruce espacial: {n:,} / {total:,}")
                QApplication.processEvents()

            try:
                incons_esp = validar_cruce_espacial(
                    capas_con_tipo, pais,
                    callback=_cb_espacial,
                    parar_fn=pro.fue_cancelado,
                    capas_ref=capas_ref_lista if capas_ref_lista else None,
                )
                inconsistencias = inconsistencias + incons_esp
            except Exception:
                incons_esp = []

        # capas_res_cruce_esp se crea de forma diferida (lazy) al hacer clic en
        # "Visualizar en QGIS" — evita leer miles de geometrías antes de mostrar resultados.
        # Guardamos los datos fuente para construirlas bajo demanda.
        capas_res_cruce_esp = {}
        _datos_cruce_esp_lazy = {}   # {nom_c: (capa_orig, fid_items, tg)}
        if hacer_geo:
            esp_tipos = {"inconsistencia_espacial", "sin_poligono_contenedor",
                         "cruce_placa_mavvial", "id_mavvial_huerfano"}
            incons_solo_esp = [i for i in inconsistencias if i["tipo"] in esp_tipos]
            if incons_solo_esp:
                capa_map  = {cs["nombre"]: cs["capa"]     for cs in capas_stats}
                tgeom_map = {cs["nombre"]: cs["tipo_geom"] for cs in capas_stats}
                from collections import defaultdict as _dd
                fid_info_por_capa = _dd(list)
                for i in incons_solo_esp:
                    for fid, val_a, val_e in i.get("items", []):
                        fid_info_por_capa[i["capa_origen"]].append(
                            (fid, i["campo"], val_a, val_e,
                             ", ".join(i.get("capas_referencia") or []), i["tipo"])
                        )
                for nom_c, fid_items in fid_info_por_capa.items():
                    capa_orig = capa_map.get(nom_c)
                    if capa_orig:
                        _datos_cruce_esp_lazy[nom_c] = (
                            capa_orig, fid_items, tgeom_map.get(nom_c, "")
                        )

        _topo_executor.shutdown(wait=False)

        # Topología ya corrió en paralelo por capa — solo ensamblar resultados
        topo_resultados = []
        if hacer_topo:
            for cs in capas_stats:
                topo_resultados.append({
                    "nombre_capa": cs["nombre"],
                    "tipo":        cs["tipo_geom"],
                    "errores":     cs.get("errores_topo", []),
                })

        tarea          = (email_cfg or {}).get("tarea", "")
        sufijo_carpeta = "interno" if modo_proceso == "interno" else "entrega"

        capas_res = {cs["nombre"]: cs["capa_res"] for cs in capas_stats
                     if cs.get("capa_res") is not None}

        # Incrementar contador de intentos
        if modo_proceso == "interno" and tarea:
            from .utils.contador_intentos import incrementar as _inc
            _inc(tarea)

        if email_cfg is None:
            email_cfg = {}
        email_cfg["modo"]     = modo
        email_cfg["producto"] = producto

        # Esperar listado Drive (best-effort 5 s — para el panel de resultados en UI)
        if self._hilo_drive is not None and self._hilo_drive.is_alive():
            self._hilo_drive.join(timeout=5)
        if self._drive_archivos_box[0] is not None:
            self._drive_archivos = self._drive_archivos_box[0]

        # Capturar valores de widgets ANTES de lanzar el hilo de fondo
        _ver_entrega_snap = self.pag_sel._btn_ver_entrega.isChecked()
        _comentario_snap  = self.pag_sel.txt_comentario.toPlainText().strip()

        # Mostrar resultados INMEDIATAMENTE — sin esperar a generar reportes
        self.pag_res.mostrar(stats_rep, inconsistencias, pais, t_total,
                             None, {}, None, topo_resultados,
                             capas_res=capas_res, csv_resumen=None,
                             capas_res_cruce_esp={},
                             email_config=email_cfg, modo_proceso=modo_proceso,
                             datos_cruce_lazy=_datos_cruce_esp_lazy,
                             verificar_entrega=_ver_entrega_snap,
                             doc_resultado=self._doc_validation_result,
                             drive_url=self._drive_folder_url,
                             drive_archivos=list(self._drive_archivos),
                             comentario=_comentario_snap)
        self._pasos_vistos.add(2)
        self._ir_a(2)
        QApplication.processEvents()

        # Generar reportes en hilo de fondo.
        # El resultado se comunica via un dict compartido + threading.Event.
        # Un QTimer en el hilo principal (event loop de Qt) hace polling hasta
        # que el hilo de fondo termina y entonces actualiza la UI y envía correo.
        # Esto evita por completo el problema de QTimer.singleShot cross-thread.
        import threading as _threading
        _res = {}              # contenedor compartido para el resultado
        _listo = _threading.Event()

        def _post_proceso():
            # ── 1. OT/Sheets join (no crítico) ───────────────────────────────────
            _ot_result_local = None
            try:
                if self._hilo_ot_sheets is not None and self._hilo_ot_sheets.is_alive():
                    self._hilo_ot_sheets.join(timeout=30)
                _ot_result_local = self._ot_result_box[0]
            except Exception:
                pass

            # ── 2. Drive join (no crítico) ────────────────────────────────────────
            try:
                if self._hilo_drive is not None and self._hilo_drive.is_alive():
                    self._hilo_drive.join(timeout=15)
                if self._drive_archivos_box[0] is not None:
                    self._drive_archivos = self._drive_archivos_box[0]
            except Exception:
                pass

            # ── 3. Generación del reporte ─────────────────────────────────────────
            ruta_html = archivos_csv = csv_resumen = carpeta_rep = None
            _error_reporte = None
            try:
                import tempfile
                _prefijo = f"cartolatam_{sufijo_carpeta}_{pais.replace(' ', '_')}_"
                carpeta_rep = tempfile.mkdtemp(prefix=_prefijo)
                os.makedirs(carpeta_rep, exist_ok=True)

                if modo_proceso == "interno":
                    from .utils.reporte_resumido import generar as _gen_resumido
                    ruta_html = os.path.join(carpeta_rep, "resumen_interno.html")
                    ruta_html, archivos_csv, csv_resumen = _gen_resumido(
                        stats_rep, topo_resultados, inconsistencias,
                        pais, t_total, tarea, ruta_html)
                else:
                    ruta_html = os.path.join(carpeta_rep, "reporte_completo.html")
                    _bloque_entrega = {
                        "pais":              pais,
                        "ot":                tarea,
                        "drive_url":         self._drive_folder_url,
                        "drive_archivos":    list(self._drive_archivos),
                        "doc_resultado":     self._doc_validation_result,
                        "verificar_entrega": _ver_entrega_snap,
                        "comentario":        _comentario_snap,
                        "capas": [
                            {
                                "nombre":      cs["nombre"],
                                "tipo_geom":   cs["tipo_geom"],
                                "n_registros": cs["n_registros"],
                            }
                            for cs in capas_stats
                        ],
                    }
                    ruta_html, archivos_csv, csv_resumen = generar_html(
                        stats_rep, inconsistencias, pais, t_total,
                        ruta_html, topo_resultados, tarea=tarea,
                        bloque_entrega=_bloque_entrega)
            except Exception:
                import traceback
                _error_reporte = traceback.format_exc()

            # ── 4. Guardar resultado y señalizar al hilo principal ────────────────
            _res['rh']   = ruta_html   or ""
            _res['ac']   = archivos_csv or {}
            _res['cr']   = csv_resumen  or ""
            _res['crep'] = carpeta_rep  or ""
            _res['err']  = _error_reporte
            _res['ot']   = _ot_result_local
            _listo.set()   # señal al hilo principal: ya terminamos

        def _poll_resultado():
            """Corre en el hilo principal (event loop Qt). Polling hasta que el hilo termine."""
            if not _listo.is_set():
                QTimer.singleShot(150, _poll_resultado)
                return
            # El hilo de fondo terminó — ahora actualizamos UI desde el hilo principal
            _r = _res
            if _r.get('ot'):
                self.pag_res.actualizar_ot_sheets(_r['ot'], modo_proceso)
            self.pag_res.actualizar_reporte(_r['rh'], _r['ac'], _r['crep'], _r['cr'])
            try:
                if _r.get('err') and hasattr(self.pag_res, "_btn_html_ref"):
                    self.pag_res._btn_html_ref.setText("Error al generar reporte")
                    self.pag_res._btn_html_ref.setEnabled(False)
                    self.pag_res._btn_html_ref.setToolTip(_r['err'][:300])
            except RuntimeError:
                pass
            QTimer.singleShot(300, self.pag_res._enviar)

        _threading.Thread(target=_post_proceso, daemon=True).start()
        QTimer.singleShot(150, _poll_resultado)   # empieza el polling en el hilo principal


