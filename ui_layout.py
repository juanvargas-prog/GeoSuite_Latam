# -*- coding: utf-8 -*-
"""
ui_layout.py
Capa de presentacion — Dark GIS Pro v2
Contiene todo el codigo de UI del plugin Validaciones LATAM.
"""
from PyQt5.QtWidgets import (
    QWidget, QFrame, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout, QStackedWidget,
)
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve
from qgis.PyQt import QtWidgets  # para QLineEdit.Password en Nexa

# =========================================================================
# TEMA VISUAL - DARK GIS PRO v2 (con sidebar)
# =========================================================================
def _apply_dark_theme(dlg):
    """Aplica el tema oscuro 'Dark GIS Pro' al plugin via QSS."""
    qss = """
    /* =====================================================================
       DARK GIS PRO - Validaciones LATAM
       ===================================================================== */

    /* === DIALOG BASE === */
    QDialog {
        background-color: #0d1117;
        color: #e6edf3;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 9pt;
    }

    /* === FRAMES / PANELES === */
    QFrame {
        background-color: #161b22;
        border: 1px solid #21262d;
        border-radius: 6px;
    }
    QFrame[frameShape="0"] {
        border: none;
        background-color: transparent;
    }

    /* === LABELS === */
    QLabel {
        color: #8b949e;
        background-color: transparent;
        border: none;
        font-size: 8.5pt;
        font-weight: 500;
    }

    /* === COLLAPSIBLE GROUP BOX === */
    QgsCollapsibleGroupBox, QgsCollapsibleGroupBoxBasic, QGroupBox {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        margin-top: 14px;
        padding-top: 8px;
        color: #e6edf3;
        font-weight: 600;
        font-size: 8.5pt;
    }
    QgsCollapsibleGroupBox::title, QgsCollapsibleGroupBoxBasic::title, QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        color: #58a6ff;
        padding: 0 6px;
        left: 10px;
        top: 2px;
    }

    /* === TAB WIDGET === */
    QTabWidget::pane {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 0px 6px 6px 6px;
        top: -1px;
    }
    QTabBar {
        background-color: transparent;
    }
    QTabBar::tab {
        background-color: #0d1117;
        color: #8b949e;
        border: 1px solid #30363d;
        border-bottom: none;
        padding: 7px 14px;
        margin-right: 2px;
        border-radius: 6px 6px 0px 0px;
        font-weight: 500;
        font-size: 8.5pt;
        min-width: 80px;
    }
    QTabBar::tab:selected {
        background-color: #161b22;
        color: #58a6ff;
        border-bottom: 2px solid #3b82f6;
        font-weight: 700;
    }
    QTabBar::tab:hover:!selected {
        background-color: #1f2937;
        color: #c9d1d9;
    }

    /* === COMBO BOX (nativos Qt) === */
    QComboBox {
        background-color: #1f2937;
        color: #e6edf3;
        border: 1px solid #30363d;
        border-radius: 5px;
        padding: 4px 8px;
        selection-background-color: #3b82f6;
        font-size: 8.5pt;
    }
    QComboBox:hover {
        border: 1px solid #58a6ff;
    }
    QComboBox:focus {
        border: 1px solid #3b82f6;
    }
    QComboBox::drop-down {
        border: none;
        width: 22px;
    }
    QComboBox::down-arrow {
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 6px solid #8b949e;
        width: 0;
        height: 0;
        margin-right: 6px;
    }
    QComboBox QAbstractItemView {
        background-color: #1f2937;
        color: #e6edf3;
        border: 1px solid #30363d;
        selection-background-color: #3b82f6;
        selection-color: #ffffff;
        outline: none;
    }

    /* === LINE EDIT === */
    QLineEdit {
        background-color: #1f2937;
        color: #e6edf3;
        border: 1px solid #30363d;
        border-radius: 5px;
        padding: 5px 8px;
        selection-background-color: #3b82f6;
        font-size: 8.5pt;
    }
    QLineEdit:hover {
        border: 1px solid #58a6ff;
    }
    QLineEdit:focus {
        border: 1px solid #3b82f6;
        background-color: #1c2333;
    }

    /* === CHECKBOXES === */
    QCheckBox {
        color: #c9d1d9;
        background-color: transparent;
        spacing: 8px;
        font-size: 8.5pt;
        border: none;
    }
    QCheckBox::indicator {
        width: 16px;
        height: 16px;
        border: 2px solid #30363d;
        border-radius: 4px;
        background-color: #1f2937;
    }
    QCheckBox::indicator:hover {
        border: 2px solid #58a6ff;
    }
    QCheckBox::indicator:checked {
        background-color: #3b82f6;
        border: 2px solid #3b82f6;
        image: none;
    }
    QCheckBox::indicator:checked:hover {
        background-color: #2563eb;
        border: 2px solid #2563eb;
    }
    QCheckBox:hover {
        color: #58a6ff;
    }

    /* === BOTONES BASE === */
    QPushButton {
        background-color: #21262d;
        color: #c9d1d9;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 6px 14px;
        font-weight: 600;
        font-size: 8.5pt;
        min-height: 26px;
    }
    QPushButton:hover {
        background-color: #30363d;
        color: #e6edf3;
        border: 1px solid #58a6ff;
    }
    QPushButton:pressed {
        background-color: #1c2128;
    }
    QPushButton:disabled {
        color: #484f58;
        border-color: #21262d;
        background-color: #161b22;
    }

    /* === BOTON VALIDAR (azul) === */
    QPushButton#PBvalidar_mv,
    QPushButton#PBval_pl,
    QPushButton#PBval_Campos {
        background-color: #1d4ed8;
        color: #ffffff;
        border: 1px solid #3b82f6;
    }
    QPushButton#PBvalidar_mv:hover,
    QPushButton#PBval_pl:hover,
    QPushButton#PBval_Campos:hover {
        background-color: #2563eb;
        border: 1px solid #60a5fa;
    }
    QPushButton#PBvalidar_mv:pressed,
    QPushButton#PBval_pl:pressed,
    QPushButton#PBval_Campos:pressed {
        background-color: #1e40af;
    }

    /* === BOTON ESTANDARIZAR (ámbar) === */
    QPushButton#PB_estandarizar,
    QPushButton#PBEstand_pl {
        background-color: #92400e;
        color: #fde68a;
        border: 1px solid #f59e0b;
    }
    QPushButton#PB_estandarizar:hover,
    QPushButton#PBEstand_pl:hover {
        background-color: #b45309;
        border: 1px solid #fbbf24;
        color: #ffffff;
    }
    QPushButton#PB_estandarizar:pressed,
    QPushButton#PBEstand_pl:pressed {
        background-color: #78350f;
    }

    /* === BOTON EXPORTAR (verde) === */
    QPushButton#PBexportarcapa,
    QPushButton#PBexportargdb {
        background-color: #064e3b;
        color: #6ee7b7;
        border: 1px solid #10b981;
    }
    QPushButton#PBexportarcapa:hover,
    QPushButton#PBexportargdb:hover {
        background-color: #065f46;
        border: 1px solid #34d399;
        color: #ffffff;
    }
    QPushButton#PBexportarcapa:pressed,
    QPushButton#PBexportargdb:pressed {
        background-color: #022c22;
    }

    /* === BOTON IA NEXA (purpura gradiente) === */
    QPushButton#PB_Estandarizar_IA {
        background-color: #4c1d95;
        color: #ddd6fe;
        border: 1px solid #7c3aed;
        font-weight: 700;
    }
    QPushButton#PB_Estandarizar_IA:hover {
        background-color: #5b21b6;
        border: 1px solid #a78bfa;
        color: #ffffff;
    }
    QPushButton#PB_Estandarizar_IA:pressed {
        background-color: #3b0764;
    }

    /* === BOTON CONTINUIDAD (indigo) === */
    QPushButton#valContinuidad {
        background-color: #312e81;
        color: #c7d2fe;
        border: 1px solid #6366f1;
    }
    QPushButton#valContinuidad:hover {
        background-color: #3730a3;
        border: 1px solid #818cf8;
        color: #ffffff;
    }

    /* === BOTON TOPOLOGIA === */
    QPushButton#PBval_Campos_2 {
        background-color: #1e293b;
        color: #94a3b8;
        border: 1px solid #334155;
    }
    QPushButton#PBval_Campos_2:hover {
        background-color: #334155;
        border: 1px solid #64748b;
        color: #e2e8f0;
    }

    /* === BOTON GENERAR ACTA (cian/teal) === */
    QPushButton#PBgenerar_acta {
        background-color: #164e63;
        color: #67e8f9;
        border: 1px solid #0e7490;
        border-radius: 6px;
        font-size: 9pt;
        font-weight: 700;
        padding: 6px 16px;
    }
    QPushButton#PBgenerar_acta:hover {
        background-color: #155e75;
        border-color: #22d3ee;
        color: #a5f3fc;
    }
    QPushButton#PBgenerar_acta:pressed {
        background-color: #0c4a6e;
        border-color: #0e7490;
    }

    /* === BOTON INICIAR VALIDACIONES LATAM (verde esmeralda) === */
    QPushButton#PBiniciar_val_latam {
        background-color: #064e3b;
        color: #6ee7b7;
        border: 1px solid #10b981;
        border-radius: 8px;
        font-size: 11pt;
        font-weight: 700;
        padding: 10px 24px;
        min-height: 44px;
    }
    QPushButton#PBiniciar_val_latam:hover {
        background-color: #065f46;
        border-color: #34d399;
        color: #a7f3d0;
    }
    QPushButton#PBiniciar_val_latam:pressed {
        background-color: #022c22;
        border-color: #10b981;
    }

    /* === BOTON AYUDA (secundario) === */
    QPushButton#PBayuda {
        background-color: #1c2128;
        color: #7d8590;
        border: 1px solid #30363d;
        padding: 4px 10px;
        min-height: 22px;
    }
    QPushButton#PBayuda:hover {
        background-color: #30363d;
        color: #c9d1d9;
    }

    /* === TEXT EDIT - MOSTRAR PROCESO === */
    QTextEdit#mostrarProceso {
        background-color: #0d1117;
        color: #3fb950;
        border: 1px solid #238636;
        border-left: 3px solid #238636;
        border-radius: 5px;
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 8pt;
        padding: 4px;
    }

    /* === TEXT EDIT - RESULTADOS === */
    QTextEdit#textEdit {
        background-color: #0d1117;
        color: #c9d1d9;
        border: 1px solid #30363d;
        border-radius: 5px;
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 8pt;
        padding: 4px;
    }

    /* === PROGRESS BAR === */
    QProgressBar {
        background-color: #21262d;
        border: 1px solid #30363d;
        border-radius: 8px;
        height: 10px;
        text-align: center;
        color: transparent;
    }
    QProgressBar::chunk {
        background-color: qlineargradient(
            x1:0, y1:0, x2:1, y2:0,
            stop:0 #1d4ed8,
            stop:0.5 #3b82f6,
            stop:1 #10b981
        );
        border-radius: 8px;
    }

    /* === SCROLL BARS === */
    QScrollBar:vertical {
        background-color: #0d1117;
        width: 8px;
        border-radius: 4px;
    }
    QScrollBar::handle:vertical {
        background-color: #30363d;
        border-radius: 4px;
        min-height: 20px;
    }
    QScrollBar::handle:vertical:hover {
        background-color: #58a6ff;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    QScrollBar:horizontal {
        background-color: #0d1117;
        height: 8px;
        border-radius: 4px;
    }
    QScrollBar::handle:horizontal {
        background-color: #30363d;
        border-radius: 4px;
        min-width: 20px;
    }
    QScrollBar::handle:horizontal:hover {
        background-color: #58a6ff;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0px;
    }

    /* === TOOLTIP === */
    QToolTip {
        background-color: #1f2937;
        color: #e6edf3;
        border: 1px solid #3b82f6;
        border-radius: 4px;
        padding: 4px 8px;
        font-size: 8pt;
    }

    /* === MENU / DROPDOWN === */
    QMenu {
        background-color: #1f2937;
        color: #e6edf3;
        border: 1px solid #30363d;
        border-radius: 4px;
    }
    QMenu::item:selected {
        background-color: #3b82f6;
        color: #ffffff;
    }

    /* === HEADER BAR === */
    QFrame#headerBar {
        background-color: #0d1117;
        border: none;
        border-bottom: 1px solid #21262d;
        border-radius: 0px;
    }
    QLabel#headerTitle {
        color: #e6edf3;
        font-size: 13pt;
        font-weight: 700;
        background: transparent;
        border: none;
    }
    QLabel#headerVersion {
        color: #3b82f6;
        font-size: 8.5pt;
        font-weight: 600;
        background: transparent;
        border: none;
    }

    /* === SIDEBAR === */
    QFrame#sidebar {
        background-color: #090d13;
        border: none;
        border-right: 1px solid #21262d;
        border-radius: 0px;
    }
    QLabel#sidebarLabel {
        color: #484f58;
        font-size: 7.5pt;
        font-weight: 700;
        letter-spacing: 1px;
        background: transparent;
        border: none;
        padding: 4px 0px 2px 0px;
    }
    QLabel#sidebarFooter {
        color: #30363d;
        font-size: 7pt;
        background: transparent;
        border: none;
    }
    QPushButton#sidebarToggle {
        background-color: #161b22;
        color: #58a6ff;
        border: 1px solid #21262d;
        border-radius: 4px;
        font-size: 9pt;
        font-weight: 700;
        padding: 0px;
    }
    QPushButton#sidebarToggle:hover {
        background-color: #1f2937;
        border-color: #3b82f6;
    }

    /* === CONNECTION PANEL === */
    QFrame#connectionPanel {
        background-color: #0d1117;
        border: none;
        border-bottom: 1px solid #21262d;
        border-radius: 0px;
    }
    QLabel#connLabel {
        color: #58a6ff;
        font-size: 8pt;
        font-weight: 600;
        background: transparent;
        border: none;
    }

    /* === MODULE HEADER === */
    QFrame#moduleHeader {
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
            stop:0 #161b22, stop:1 #0d1117);
        border: none;
        border-bottom: 1px solid #30363d;
        border-radius: 0px;
    }
    QLabel#moduleTitle {
        color: #e6edf3;
        font-size: 11pt;
        font-weight: 700;
        background: transparent;
        border: none;
    }

    /* === MODULE BODY === */
    QFrame#moduleBody {
        background-color: transparent;
        border: none;
    }
    QFrame#sectionFrame {
        background-color: #161b22;
        border: 1px solid #21262d;
        border-radius: 8px;
    }
    QLabel#sectionTitle {
        color: #58a6ff;
        font-size: 8.5pt;
        font-weight: 700;
        background: transparent;
        border: none;
        padding-bottom: 4px;
        border-bottom: 1px solid #21262d;
    }
    QLabel#layerLabel {
        color: #8b949e;
        font-size: 8pt;
        background: transparent;
        border: none;
    }
    QLabel#descLabel {
        color: #8b949e;
        font-size: 8.5pt;
        background: transparent;
        border: none;
        line-height: 1.4;
    }
    QLabel#infoLabel {
        color: #3b82f6;
        font-size: 8pt;
        background: transparent;
        border: none;
    }
    QFrame#actionBar {
        background-color: transparent;
        border: none;
        border-top: 1px solid #21262d;
    }

    /* === NEXA HEADER === */
    QFrame#nexaHeader {
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
            stop:0 #1a0533, stop:0.5 #2d1458, stop:1 #1a0533);
        border: none;
        border-bottom: 1px solid #7c3aed;
        border-radius: 0px;
    }
    QLabel#nexaTitle {
        color: #ddd6fe;
        font-size: 11pt;
        font-weight: 700;
        background: transparent;
        border: none;
    }
    QLabel#nexaSubtitle {
        color: #7c3aed;
        font-size: 8pt;
        font-weight: 600;
        background: transparent;
        border: none;
    }
    QPushButton#togglePwd {
        background-color: #21262d;
        color: #8b949e;
        border: 1px solid #30363d;
        border-radius: 4px;
        font-size: 11pt;
        padding: 0px;
    }
    QPushButton#togglePwd:checked {
        background-color: #1d4ed8;
        color: #ffffff;
        border-color: #3b82f6;
    }

    /* === STACKED / RIGHT PANEL === */
    QStackedWidget#mainStack {
        background-color: #0d1117;
        border: none;
    }
    QWidget#rightPanel {
        background-color: #0d1117;
    }
    QWidget#body {
        background-color: #0d1117;
    }

    /* === EXPORT NG — LISTA DE CAPAS === */
    QListWidget#QLW_export_capas {
        background-color: #0d1117;
        color: #e6edf3;
        border: 1px solid #30363d;
        border-radius: 6px;
        font-size: 8.5pt;
        padding: 4px;
        outline: none;
    }
    QListWidget#QLW_export_capas::item {
        padding: 3px 6px;
        border-radius: 4px;
    }
    QListWidget#QLW_export_capas::item:hover {
        background-color: #1f2937;
    }
    QListWidget#QLW_export_capas::item:selected {
        background-color: transparent;
        color: #e6edf3;
    }

    /* === EXPORT NG — CHECKBOX MAESTRO === */
    QCheckBox#CB_seleccionar_todo {
        color: #58a6ff;
        font-size: 8.5pt;
        font-weight: 600;
        background: transparent;
        border: none;
        spacing: 6px;
    }
    QCheckBox#CB_seleccionar_todo::indicator {
        width: 14px;
        height: 14px;
        border: 1px solid #3b82f6;
        border-radius: 3px;
        background-color: #0d1117;
    }
    QCheckBox#CB_seleccionar_todo::indicator:checked {
        background-color: #1d4ed8;
        border-color: #3b82f6;
    }

    /* === EXPORT NG — BOTÓN ACCIÓN === */
    QPushButton#PBexportar_capas_NG {
        background-color: #064e3b;
        color: #6ee7b7;
        border: 1px solid #10b981;
        border-radius: 6px;
        font-size: 9pt;
        font-weight: 700;
        padding: 6px 16px;
    }
    QPushButton#PBexportar_capas_NG:hover {
        background-color: #065f46;
        border-color: #34d399;
        color: #a7f3d0;
    }
    QPushButton#PBexportar_capas_NG:pressed {
        background-color: #022c22;
        border-color: #10b981;
    }

    /* === SCROLLBAR GLOBAL (incluye dropdowns de QComboBox) === */
    QScrollBar:vertical {
        background: #0d1117;
        width: 8px;
        border: none;
        border-radius: 4px;
        margin: 0px;
    }
    QScrollBar::handle:vertical {
        background: #30363d;
        border-radius: 4px;
        min-height: 20px;
    }
    QScrollBar::handle:vertical:hover {
        background: #58a6ff;
    }
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {
        background: #161b22;
        height: 14px;
        border: none;
        border-radius: 2px;
        subcontrol-origin: margin;
    }
    QScrollBar::sub-line:vertical {
        subcontrol-position: top;
    }
    QScrollBar::add-line:vertical {
        subcontrol-position: bottom;
    }
    QScrollBar::up-arrow:vertical {
        image: none;
        border-left: 3px solid transparent;
        border-right: 3px solid transparent;
        border-bottom: 5px solid #8b949e;
        width: 0px;
        height: 0px;
    }
    QScrollBar::down-arrow:vertical {
        image: none;
        border-left: 3px solid transparent;
        border-right: 3px solid transparent;
        border-top: 5px solid #8b949e;
        width: 0px;
        height: 0px;
    }
    QScrollBar::add-page:vertical,
    QScrollBar::sub-page:vertical {
        background: none;
    }
    QScrollBar:horizontal {
        background: #0d1117;
        height: 8px;
        border: none;
        border-radius: 4px;
        margin: 0px;
    }
    QScrollBar::handle:horizontal {
        background: #30363d;
        border-radius: 4px;
        min-width: 20px;
    }
    QScrollBar::handle:horizontal:hover {
        background: #58a6ff;
    }
    QScrollBar::add-line:horizontal,
    QScrollBar::sub-line:horizontal {
        background: none;
        width: 0px;
        border: none;
    }
    QScrollBar::add-page:horizontal,
    QScrollBar::sub-page:horizontal {
        background: none;
    }
    """
    dlg.setStyleSheet(qss)

# =========================================================================
# NUEVO LAYOUT - SIDEBAR + STACKED WIDGET
# =========================================================================
def _rebuild_layout(dlg):
    """Reconstruye el layout con sidebar colapsable + contenido dinamico."""
    from PyQt5.QtWidgets import (QSplitter, QStackedWidget, QGridLayout,
                                 QScrollArea, QSizePolicy, QListWidget,
                                 QListWidgetItem, QHBoxLayout as QHBox)
    from PyQt5.QtCore import Qt, QSize
    from PyQt5.QtGui import QFont

    # --- PASO 1: Proteger todos los widgets reparentandolos a dlg ANTES
    #             de tocar el layout. Solo setParent(dlg) — NO hide(),
    #             porque hide() activa el flag "explicitamente oculto" en Qt
    #             y eso hace que addWidget() los deje invisibles.
    _attrs_to_protect = [
        'PBayuda', 'CBselectDatabase', 'CBselectScheme',
        'QCB_Filtro', 'QLE_DigFiltro', 'combo_Paises',
        'textEdit', 'mostrarProceso', 'progressBar',
        'PBval_Campos', 'PBval_Campos_2',
        'QMLCBmv_mv', 'QMLCBmv_placas',
        'PB_estandarizar', 'PBvalidar_mv', 'valContinuidad',
        'QMLCBplacas_pl', 'QMLCBmavvial_pl',
        'QMLCBpredios_pl', 'QMLCBmanzanas_pl',
        'PBEstand_pl', 'PBval_pl',
        'QMLCB_CapaIA', 'QERCW_rutaIA', 'QCB_columnaIA',
        'QLE_EstHib_ApiKey', 'PB_Estandarizar_IA',
    ]
    for attr in _attrs_to_protect:
        try:
            getattr(dlg, attr).setParent(dlg)
        except Exception:
            pass
    # Proteger val1-val12 (combos de capas)
    for i in range(1, 13):
        try:
            getattr(dlg, f'val{i}').setParent(dlg)
        except Exception:
            pass
    # Proteger checkboxes Mavvial y Placas
    for i in range(1, 11):
        for pfx in ('CB_Mv_', 'CB_Pl_'):
            try:
                getattr(dlg, f'{pfx}{i}').setParent(dlg)
            except Exception:
                pass

    # --- PASO 2: Ahora es SEGURO reemplazar el layout porque nuestros
    #             widgets ya no son hijos del frame del .ui
    old = dlg.layout()
    if old:
        QWidget().setLayout(old)   # El frame viejo del .ui se destruye solo

    # --- Layout principal del dialog ---
    root = QVBoxLayout(dlg)
    root.setContentsMargins(0, 0, 0, 0)
    root.setSpacing(0)

    # HEADER BAR
    hdr = QFrame()
    hdr.setObjectName("headerBar")
    hdr.setFixedHeight(50)
    hl = QHBoxLayout(hdr)
    hl.setContentsMargins(18, 0, 14, 0)
    ttl = QLabel("🌎  GEOSUITE LATAM")
    ttl.setObjectName("headerTitle")
    ver = QLabel("Version 7.4.7")
    ver.setObjectName("headerVersion")
    dlg.PBayuda.setParent(hdr)
    dlg.PBayuda.setText("❓ Ayuda")
    hl.addWidget(ttl)
    hl.addStretch()
    hl.addWidget(ver)
    hl.addWidget(dlg.PBayuda)
    dlg.PBayuda.show()
    root.addWidget(hdr)

    # BODY
    body = QWidget()
    body.setObjectName("body")
    bl = QHBoxLayout(body)
    bl.setContentsMargins(0, 0, 0, 0)
    bl.setSpacing(0)
    root.addWidget(body, 1)

    # --- SIDEBAR ---
    dlg._sidebar = QFrame()
    dlg._sidebar.setObjectName("sidebar")
    dlg._sidebar_w = 240
    dlg._sidebar.setFixedWidth(dlg._sidebar_w)
    dlg._sidebar_expanded = True
    sl = QVBoxLayout(dlg._sidebar)
    sl.setContentsMargins(8, 10, 8, 10)
    sl.setSpacing(3)

    # Toggle
    dlg._btn_toggle = QPushButton("◀")
    dlg._btn_toggle.setObjectName("sidebarToggle")
    dlg._btn_toggle.setFixedHeight(26)
    dlg._btn_toggle.setToolTip("Colapsar / Expandir sidebar")
    dlg._btn_toggle.clicked.connect(lambda: _toggle_sidebar(dlg))
    sl.addWidget(dlg._btn_toggle)

    sep_lbl = QLabel("  MÓDULOS")
    sep_lbl.setObjectName("sidebarLabel")
    sl.addWidget(sep_lbl)
    sl.addSpacing(4)

    modules_def = [
        ("🗺️  Comprobar Campos", 0, "#1d4ed8"),
        ("🛣️  Mavvial",           1, "#92400e"),
        ("📍  Placas",            2, "#5b21b6"),
        ("🌎  Validaciones Cartograficas", 3, "#065f46"),
        ("📤  Export",            4, "#064e3b"),
        ("🚀  Nexa AI",           5, "#4c1d95"),
        ("📄  Actas",             6, "#0e7490"),
    ]
    dlg._mod_btns = []
    for label, idx, color in modules_def:
        btn = QPushButton(label)
        btn.setObjectName("sidebarBtn")
        btn.setCheckable(True)
        btn.setFixedHeight(40)
        btn.setToolTip(label.strip())
        btn.clicked.connect(lambda chk, i=idx: _switch_module(dlg, i))
        sl.addWidget(btn)
        dlg._mod_btns.append((btn, color))

    sl.addStretch()
    foot = QLabel("  Data GIS · Automatizaciones")
    foot.setObjectName("sidebarFooter")
    sl.addWidget(foot)
    bl.addWidget(dlg._sidebar)

    # --- PANEL DERECHO ---
    rp = QWidget()
    rp.setObjectName("rightPanel")
    rl = QVBoxLayout(rp)
    rl.setContentsMargins(10, 10, 10, 8)
    rl.setSpacing(8)
    bl.addWidget(rp, 1)

    # PANEL CONEXION (siempre visible)
    cp = QFrame()
    cp.setObjectName("connectionPanel")
    cpL = QHBoxLayout(cp)
    cpL.setContentsMargins(12, 6, 12, 6)
    cpL.setSpacing(10)

    for lbl_txt, widget in [
        ("🗄️ Base de Datos:", dlg.CBselectDatabase),
        ("📂 Schema:",         dlg.CBselectScheme),
    ]:
        l = QLabel(lbl_txt); l.setObjectName("connLabel")
        widget.setParent(cp)
        cpL.addWidget(l)
        cpL.addWidget(widget, 2 if "Datos" in lbl_txt else 1)
        widget.show()

    l_filt = QLabel("🔍 Filtro:"); l_filt.setObjectName("connLabel")
    dlg.QCB_Filtro.setParent(cp)
    dlg.QLE_DigFiltro.setParent(cp)
    dlg.QLE_DigFiltro.setPlaceholderText("Ej: 0701")
    cpL.addWidget(l_filt)
    cpL.addWidget(dlg.QCB_Filtro, 1)
    cpL.addWidget(dlg.QLE_DigFiltro, 1)
    dlg.QCB_Filtro.show()
    dlg.QLE_DigFiltro.show()
    rl.addWidget(cp)

    # STACKED WIDGET
    dlg._stack = QStackedWidget()
    dlg._stack.setObjectName("mainStack")
    rl.addWidget(dlg._stack, 1)
    dlg._stack.addWidget(_build_page_campos(dlg))        # 0
    dlg._stack.addWidget(_build_page_mavvial(dlg))       # 1
    dlg._stack.addWidget(_build_page_placas(dlg))        # 2
    dlg._stack.addWidget(_build_page_val_latam(dlg))     # 3
    dlg._stack.addWidget(_build_page_export(dlg))        # 4
    dlg._stack.addWidget(_build_page_nexa(dlg))          # 5
    dlg._stack.addWidget(_build_page_actas(dlg))         # 6

    # STATUS BAR
    dlg.mostrarProceso.setParent(rp)
    dlg.mostrarProceso.setEnabled(True)
    dlg.mostrarProceso.setMinimumHeight(46)
    dlg.mostrarProceso.setMaximumHeight(200)
    dlg.mostrarProceso.setSizePolicy(
        QSizePolicy.Expanding, QSizePolicy.Preferred)
    rl.addWidget(dlg.mostrarProceso)
    dlg.mostrarProceso.show()

    # PROGRESS BAR
    dlg.progressBar.setParent(rp)
    dlg.progressBar.setFixedHeight(12)
    rl.addWidget(dlg.progressBar)
    dlg.progressBar.show()

    # Seleccionar primer modulo
    _switch_module(dlg, 0)
    _force_combo_dark(dlg)

# -------------------------------------------------------------------------
def _force_combo_dark(dlg):
    """Fuerza estilos oscuros en combos que ignoran el QSS global."""
    # Combos Qt estandar — incluye dropdown list
    dark = (
        "QComboBox{"
        "background:#1f2937;color:#e6edf3;border:1px solid #30363d;"
        "border-radius:5px;padding:3px 8px;}"
        "QComboBox:hover{border-color:#58a6ff;}"
        "QComboBox::drop-down{border:none;width:20px;}"
        "QComboBox::down-arrow{image:none;border-left:4px solid transparent;"
        "border-right:4px solid transparent;border-top:5px solid #8b949e;"
        "margin-right:6px;}"
        "QComboBox QAbstractItemView{background:#1f2937;color:#e6edf3;"
        "border:1px solid #30363d;border-radius:4px;"
        "selection-background-color:#1d4ed8;selection-color:#fff;"
        "outline:none;}"
    )
    for w in [dlg.CBselectDatabase, dlg.CBselectScheme,
              dlg.QCB_Filtro, dlg.combo_Paises,
              dlg.QCB_columna_exp, dlg.QCB_formato_exp, dlg.QCB_columnaIA]:
        try: w.setStyleSheet(dark)
        except Exception: pass
    # QgsMapLayerComboBox — necesitan estilo directo
    qgs = ("QgsMapLayerComboBox{background:#1f2937;color:#e6edf3;"
           "border:1px solid #30363d;border-radius:5px;padding:2px 8px;}"
           "QgsMapLayerComboBox QAbstractItemView{background:#1f2937;"
           "color:#e6edf3;border:1px solid #30363d;"
           "selection-background-color:#3b82f6;selection-color:#fff;}")
    layer_combos = [
        dlg.QMLCBmv_mv, dlg.QMLCBmv_placas,
        dlg.QMLCBplacas_pl, dlg.QMLCBmavvial_pl,
        dlg.QMLCBpredios_pl, dlg.QMLCBmanzanas_pl,
        dlg.QMLCB_CapaIA,
    ]
    for w in layer_combos:
        try: w.setStyleSheet(qgs)
        except Exception: pass
    # val1-val12 (capas en Comprobar Campos)
    for i in range(1, 13):
        try: getattr(dlg, f'val{i}').setStyleSheet(qgs)
        except Exception: pass

# -------------------------------------------------------------------------
def _switch_module(dlg, idx):
    """Cambia el modulo activo en el stacked widget y actualiza sidebar."""
    dlg._stack.setCurrentIndex(idx)
    colors = ["#1d4ed8", "#92400e", "#5b21b6", "#065f46", "#064e3b", "#4c1d95", "#0e7490"]
    # En modo colapsado los botones muestran solo el emoji → centrar
    collapsed = not getattr(dlg, '_sidebar_expanded', True)
    align = "center" if collapsed else "left"
    pad   = "0px"    if collapsed else "10px"
    for i, (btn, col) in enumerate(dlg._mod_btns):
        if i == idx:
            btn.setChecked(True)
            btn.setStyleSheet(
                f"QPushButton{{background-color:{col};color:#fff;"
                f"border:none;border-left:4px solid #fff;border-radius:4px;"
                f"font-weight:700;text-align:{align};padding-left:{pad};}}"
            )
        else:
            btn.setChecked(False)
            btn.setStyleSheet(
                f"QPushButton{{background-color:transparent;color:#8b949e;"
                f"border:none;border-left:4px solid transparent;border-radius:4px;"
                f"font-weight:500;text-align:{align};padding-left:{pad};}}"
                f"QPushButton:hover{{background-color:#21262d;color:#c9d1d9;"
                f"border-left:4px solid #30363d;}}"
            )

# -------------------------------------------------------------------------
def _toggle_sidebar(dlg):
    """Colapsa/expande el sidebar con animacion de ancho."""
    from PyQt5.QtCore import QPropertyAnimation, QEasingCurve
    anim = QPropertyAnimation(dlg._sidebar, b"minimumWidth")
    anim.setDuration(200)
    anim.setEasingCurve(QEasingCurve.InOutCubic)
    anim2 = QPropertyAnimation(dlg._sidebar, b"maximumWidth")
    anim2.setDuration(200)
    anim2.setEasingCurve(QEasingCurve.InOutCubic)

    icons   = ["🗺️", "🛣️", "📍", "🌎", "📤", "🚀", "📄"]
    full    = ["🗺️  Comprobar Campos", "🛣️  Mavvial",
               "📍  Placas", "🌎  Validaciones Cartograficas", "📤  Export", "🚀  Nexa AI", "📄  Actas"]

    if dlg._sidebar_expanded:
        anim.setStartValue(dlg._sidebar_w); anim.setEndValue(56)
        anim2.setStartValue(dlg._sidebar_w); anim2.setEndValue(56)
        dlg._btn_toggle.setText("▶")
        for (btn, _), icon in zip(dlg._mod_btns, icons):
            btn.setText(icon)
    else:
        anim.setStartValue(56); anim.setEndValue(dlg._sidebar_w)
        anim2.setStartValue(56); anim2.setEndValue(dlg._sidebar_w)
        dlg._btn_toggle.setText("◀")
        for (btn, _), txt in zip(dlg._mod_btns, full):
            btn.setText(txt)
    dlg._sidebar_expanded = not dlg._sidebar_expanded
    anim.start(); anim2.start()
    dlg._anim = anim; dlg._anim2 = anim2
    # Reaplicar estilos de botones con el alineado correcto para el nuevo estado
    _switch_module(dlg, dlg._stack.currentIndex())

# =========================================================================
# PAGE BUILDERS
# =========================================================================
def _module_header(icon, title, parent=None):
    """Crea un frame header de modulo reutilizable."""
    h = QFrame(parent); h.setObjectName("moduleHeader")
    hl = QHBoxLayout(h); hl.setContentsMargins(14, 8, 14, 8)
    lbl = QLabel(f"{icon}  {title}"); lbl.setObjectName("moduleTitle")
    hl.addWidget(lbl); hl.addStretch()
    return h, hl

def _section(title, parent=None):
    """Crea un QFrame seccion con titulo."""
    f = QFrame(parent); f.setObjectName("sectionFrame")
    vl = QVBoxLayout(f); vl.setContentsMargins(10, 8, 10, 8); vl.setSpacing(6)
    if title:
        lbl = QLabel(title); lbl.setObjectName("sectionTitle")
        vl.addWidget(lbl)
    return f, vl

def _action_bar(*buttons):
    """Crea un frame de botones de accion alineados a la derecha."""
    f = QFrame(); f.setObjectName("actionBar")
    hl = QHBoxLayout(f); hl.setContentsMargins(8, 6, 8, 6)
    hl.addStretch()
    for b in buttons:
        hl.addWidget(b)
    return f

# -------------------------------------------------------------------------
def _build_page_campos(dlg):
    page = QWidget(); page.setObjectName("pageCampos")
    pl = QVBoxLayout(page); pl.setContentsMargins(6, 6, 6, 6); pl.setSpacing(10)

    # Header con selector de pais
    hdr, hl = _module_header("🗺️", "Comprobar Campos")
    l_pais = QLabel("País:"); l_pais.setObjectName("connLabel")
    dlg.combo_Paises.setParent(hdr)
    hl.addWidget(l_pais); hl.addWidget(dlg.combo_Paises)
    dlg.combo_Paises.show()
    pl.addWidget(hdr)

    # Card: asignacion de capas en grid 2 columnas
    c1, vl1 = _section("📋  Asignación de Capas al Proyecto")
    grid = QGridLayout(); grid.setSpacing(8)
    grid.setColumnStretch(1, 1); grid.setColumnStretch(3, 1)
    names = ["Mavvial", "Placa", "Manzana", "Conc. Urbana",
             "Distrito", "Estado", "Centro Poblado", "Parque / ZV",
             "Hidrografía", "Predio", "CEP", "Adicional"]
    for i in range(12):
        cb = getattr(dlg, f'val{i+1}')
        lbl = QLabel(f"{names[i]}:"); lbl.setObjectName("layerLabel")
        row, col = i // 2, (i % 2) * 2
        grid.addWidget(lbl, row, col)
        grid.addWidget(cb,  row, col + 1)
        cb.show()
    vl1.addLayout(grid)
    pl.addWidget(c1)

    # Card: resultados
    c2, vl2 = _section("📊  Resultados de Validación")
    dlg.textEdit.setParent(c2)
    vl2.addWidget(dlg.textEdit, 1)
    dlg.textEdit.show()
    pl.addWidget(c2, 1)

    dlg.PBval_Campos.setText("🗺️  Validar Campos")
    dlg.PBval_Campos_2.setText("🔗  Validar Topología")
    dlg.PBval_Campos.show()
    dlg.PBval_Campos_2.show()
    pl.addWidget(_action_bar(dlg.PBval_Campos, dlg.PBval_Campos_2))
    return page

# -------------------------------------------------------------------------
def _build_page_mavvial(dlg):
    page = QWidget(); page.setObjectName("pageMavvial")
    pl = QVBoxLayout(page); pl.setContentsMargins(6, 6, 6, 6); pl.setSpacing(10)
    hdr, _ = _module_header("🛣️", "Validación Mavvial")
    pl.addWidget(hdr)

    # Card: capas de entrada
    c1, vl1 = _section("🗺️  Capas de Entrada")
    for lbl_txt, widget in [
        ("🛣️  Capa Mavvial:", dlg.QMLCBmv_mv),
        ("📍  Capa Placas:",  dlg.QMLCBmv_placas),
    ]:
        row = QHBoxLayout()
        l = QLabel(lbl_txt); l.setObjectName("connLabel"); l.setFixedWidth(140)
        widget.setParent(c1)
        row.addWidget(l); row.addWidget(widget, 1)
        widget.show()
        vl1.addLayout(row)
    pl.addWidget(c1)

    # Card: validaciones con checkboxes en 2 columnas
    c2, vl2 = _section("⚙️  Seleccione las Validaciones a Ejecutar")
    chk_grid = QGridLayout(); chk_grid.setSpacing(10)
    chk_grid.setColumnStretch(0, 1); chk_grid.setColumnStretch(1, 1)
    for i, num in enumerate([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]):
        cb = getattr(dlg, f'CB_Mv_{num}')
        chk_grid.addWidget(cb, i // 2, i % 2)
        cb.show()
    vl2.addLayout(chk_grid)
    pl.addWidget(c2, 1)

    # Botones de accion
    dlg.PB_estandarizar.setText("⚡  Estandarizar")
    dlg.PBvalidar_mv.setText("🔍  Validar Mavvial")
    dlg.valContinuidad.setText("🔗  Continuidad")
    for b in [dlg.PB_estandarizar, dlg.PBvalidar_mv, dlg.valContinuidad]:
        b.setFixedHeight(34)
        b.show()
    pl.addWidget(_action_bar(
        dlg.PB_estandarizar, dlg.PBvalidar_mv, dlg.valContinuidad))
    return page

# -------------------------------------------------------------------------
def _build_page_placas(dlg):
    page = QWidget(); page.setObjectName("pagePlacas")
    pl = QVBoxLayout(page); pl.setContentsMargins(6, 6, 6, 6); pl.setSpacing(10)
    hdr, _ = _module_header("📍", "Validación Placas")
    pl.addWidget(hdr)

    # Card: capas de entrada en grid 2x2
    c1, vl1 = _section("🗺️  Capas de Entrada")
    cap_grid = QGridLayout(); cap_grid.setSpacing(8)
    cap_grid.setColumnStretch(1, 1); cap_grid.setColumnStretch(3, 1)
    caps = [
        ("📍 Placa:",    dlg.QMLCBplacas_pl,   0, 0),
        ("🛣️ Mavvial:",  dlg.QMLCBmavvial_pl,  0, 2),
        ("🏘️ Predios:",  dlg.QMLCBpredios_pl,  1, 0),
        ("🏙️ Manzanas:", dlg.QMLCBmanzanas_pl, 1, 2),
    ]
    for lbl_txt, widget, r, c in caps:
        l = QLabel(lbl_txt); l.setObjectName("connLabel")
        widget.setParent(c1)
        cap_grid.addWidget(l,      r, c)
        cap_grid.addWidget(widget, r, c + 1)
        widget.show()
    vl1.addLayout(cap_grid)
    pl.addWidget(c1)

    # Card: validaciones en 2 columnas
    c2, vl2 = _section("⚙️  Seleccione las Validaciones a Ejecutar")
    chk_grid = QGridLayout(); chk_grid.setSpacing(10)
    chk_grid.setColumnStretch(0, 1); chk_grid.setColumnStretch(1, 1)
    for i, num in enumerate([1, 2, 3, 4, 5, 6, 7, 8, 10]):
        cb = getattr(dlg, f'CB_Pl_{num}')
        chk_grid.addWidget(cb, i // 2, i % 2)
        cb.show()
    vl2.addLayout(chk_grid)
    pl.addWidget(c2, 1)

    dlg.PBEstand_pl.setText("⚡  Estandarizar Placas")
    dlg.PBval_pl.setText("🔍  Validar Placas")
    for b in [dlg.PBEstand_pl, dlg.PBval_pl]:
        b.setFixedHeight(34)
        b.show()
    pl.addWidget(_action_bar(dlg.PBEstand_pl, dlg.PBval_pl))
    return page

# -------------------------------------------------------------------------
def _build_page_export(dlg):
    from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QCheckBox, QComboBox, QSizePolicy
    from PyQt5.QtCore import Qt

    page = QWidget(); page.setObjectName("pageExport")
    pl = QVBoxLayout(page); pl.setContentsMargins(6,6,6,6); pl.setSpacing(10)
    hdr, _ = _module_header("📤", "Exportar Capas NG")
    pl.addWidget(hdr)

    # ── Card única: selección múltiple ────────────────────────────────────
    c1, vl1 = _section("🚀  Selección y Exportación de Capas")

    desc = QLabel(
        "Selecciona las capas del esquema activo que deseas exportar. "
        "Elige la columna de referencia y el formato de salida."
    )
    desc.setWordWrap(True); desc.setObjectName("descLabel")
    vl1.addWidget(desc)

    # ── Tabla: Capa | Estructura | Filtrar | Columna / Valor ─────────────
    from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
    dlg.QTW_export_capas = QTableWidget(0, 4)
    dlg.QTW_export_capas.setObjectName("QTW_export_capas")
    dlg.QTW_export_capas.setHorizontalHeaderLabels([
        "Capa (servidor)", "Estructura (Sheet)", "Filtrar", "Columna  /  Valor"
    ])
    hh = dlg.QTW_export_capas.horizontalHeader()
    hh.setSectionResizeMode(0, QHeaderView.Stretch)
    hh.setSectionResizeMode(1, QHeaderView.Stretch)
    hh.setSectionResizeMode(2, QHeaderView.ResizeToContents)
    hh.setSectionResizeMode(3, QHeaderView.Stretch)
    dlg.QTW_export_capas.verticalHeader().setVisible(False)
    dlg.QTW_export_capas.setSelectionMode(QTableWidget.NoSelection)
    dlg.QTW_export_capas.setEditTriggers(QTableWidget.NoEditTriggers)
    dlg.QTW_export_capas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    dlg.QTW_export_capas.setMinimumHeight(200)
    dlg.QTW_export_capas.setStyleSheet(
        "QTableWidget{background:#0d1117;color:#e6edf3;border:1px solid #30363d;"
        "border-radius:6px;gridline-color:#21262d;font-size:8.5pt;}"
        "QTableWidget::item{padding:3px 6px;}"
        "QTableWidget::item:selected{background:transparent;}"
        "QHeaderView::section{background:#161b22;color:#58a6ff;border:none;"
        "border-bottom:1px solid #30363d;padding:4px 8px;font-weight:700;font-size:8pt;}"
    )
    vl1.addWidget(dlg.QTW_export_capas, 1)

    # ── Parámetros: columna y formato ─────────────────────────────────────
    _combo_dark = (
        "QComboBox{background:#1f2937;color:#e6edf3;border:1px solid #30363d;"
        "border-radius:5px;padding:3px 8px;}"
        "QComboBox:hover{border-color:#58a6ff;}"
        "QComboBox::drop-down{border:none;width:20px;}"
        "QComboBox::down-arrow{image:none;border-left:4px solid transparent;"
        "border-right:4px solid transparent;border-top:5px solid #8b949e;"
        "margin-right:6px;}"
        "QComboBox QAbstractItemView{background:#1f2937;color:#e6edf3;"
        "border:1px solid #30363d;border-radius:4px;"
        "selection-background-color:#1d4ed8;selection-color:#fff;outline:none;}"
    )

    params_row = QHBoxLayout(); params_row.setSpacing(12)

    l_col = QLabel("Servicio:"); l_col.setObjectName("connLabel")
    dlg.QCB_columna_exp = QComboBox()
    dlg.QCB_columna_exp.setObjectName("QCB_columna_exp")
    dlg.QCB_columna_exp.addItems(['produccion', 'Geolocalizacion', 'Geomarketing'])
    dlg.QCB_columna_exp.setFixedHeight(28)
    dlg.QCB_columna_exp.setStyleSheet(_combo_dark)

    l_fmt = QLabel("Formato:"); l_fmt.setObjectName("connLabel")
    dlg.QCB_formato_exp = QComboBox()
    dlg.QCB_formato_exp.setObjectName("QCB_formato_exp")
    dlg.QCB_formato_exp.addItems(['shp', 'csv', 'gpkg'])
    dlg.QCB_formato_exp.setFixedHeight(28)
    dlg.QCB_formato_exp.setStyleSheet(_combo_dark)

    params_row.addWidget(l_col)
    params_row.addWidget(dlg.QCB_columna_exp, 1)
    params_row.addSpacing(16)
    params_row.addWidget(l_fmt)
    params_row.addWidget(dlg.QCB_formato_exp, 1)
    vl1.addLayout(params_row)

    # ── Fila de acción: botón + checkbox Drive ────────────────────────────
    from PyQt5.QtWidgets import QCheckBox, QLineEdit

    # ── Fila superior: Servicio Drive (checkbox + folder ID) ──────────────
    dlg.CB_drive_upload = QCheckBox("☁️  Drive")
    dlg.CB_drive_upload.setObjectName("CB_drive_upload")
    dlg.CB_drive_upload.setToolTip(
        "Si está activo, sube la carpeta exportada a Google Drive al finalizar"
    )
    dlg.CB_drive_upload.setStyleSheet(
        "QCheckBox{color:#c9d1d9;background:transparent;border:none;"
        "font-size:8.5pt;font-weight:600;spacing:6px;}"
        "QCheckBox::indicator{width:16px;height:16px;border:2px solid #30363d;"
        "border-radius:4px;background:#1f2937;}"
        "QCheckBox::indicator:hover{border-color:#58a6ff;}"
        "QCheckBox::indicator:checked{background:#1d4ed8;border-color:#3b82f6;}"
        "QCheckBox:hover{color:#58a6ff;}"
    )

    dlg.QLE_drive_folder_id = QLineEdit()
    dlg.QLE_drive_folder_id.setObjectName("QLE_drive_folder_id")
    dlg.QLE_drive_folder_id.setPlaceholderText("ID de la carpeta destino en Google Drive...")
    dlg.QLE_drive_folder_id.setEnabled(False)
    dlg.QLE_drive_folder_id.setFixedHeight(30)
    dlg.QLE_drive_folder_id.setStyleSheet(
        "QLineEdit{background:#161b22;color:#484f58;border:1px solid #21262d;"
        "border-radius:5px;padding:4px 8px;font-size:8.5pt;}"
        "QLineEdit:enabled{background:#1f2937;color:#e6edf3;border:1px solid #30363d;}"
        "QLineEdit:enabled:hover{border-color:#58a6ff;}"
        "QLineEdit:enabled:focus{border-color:#3b82f6;background:#1c2333;}"
    )

    l_folder = QLabel("📁  Folder ID:"); l_folder.setObjectName("connLabel")
    l_folder.setFixedWidth(90)
    service_row = QHBoxLayout(); service_row.setSpacing(8)
    service_row.addWidget(dlg.CB_drive_upload)
    service_row.addWidget(l_folder)
    service_row.addWidget(dlg.QLE_drive_folder_id, 1)
    vl1.addLayout(service_row)

    # Conectar checkbox → habilitar/deshabilitar el campo de ID
    dlg.CB_drive_upload.toggled.connect(dlg.QLE_drive_folder_id.setEnabled)

    # ── Fila inferior: botón de exportar ──────────────────────────────────
    dlg.PBexportar_capas_NG = QPushButton("🚀  Exportar Capas NG")
    dlg.PBexportar_capas_NG.setObjectName("PBexportar_capas_NG")
    dlg.PBexportar_capas_NG.setFixedHeight(40)
    vl1.addWidget(dlg.PBexportar_capas_NG)

    pl.addWidget(c1, 1)

    return page

# -------------------------------------------------------------------------
def _build_page_nexa(dlg):
    page = QWidget(); page.setObjectName("pageNexa")
    pl = QVBoxLayout(page); pl.setContentsMargins(4,4,4,4); pl.setSpacing(10)

    # Header especial AI
    hdr = QFrame(); hdr.setObjectName("nexaHeader")
    hl = QHBoxLayout(hdr); hl.setContentsMargins(16,10,16,10)
    lbl_n = QLabel("🚀  NEXA  ·  Estandarizador con IA")
    lbl_n.setObjectName("nexaTitle")
    sub = QLabel("Powered by Gemini AI")
    sub.setObjectName("nexaSubtitle")
    hl.addWidget(lbl_n); hl.addStretch(); hl.addWidget(sub)
    pl.addWidget(hdr)

    # Card API Key
    c1, vl1 = _section("🔑  Configuración de API")
    row_api = QHBoxLayout()
    l_api = QLabel("API Key Gemini:"); l_api.setObjectName("connLabel")
    dlg.QLE_EstHib_ApiKey.setParent(c1)
    dlg.QLE_EstHib_ApiKey.setPlaceholderText("Ingresa tu API Key de Google Gemini...")
    dlg.QLE_EstHib_ApiKey.setEchoMode(QtWidgets.QLineEdit.Password)
    btn_show = QPushButton("👁")
    btn_show.setObjectName("togglePwd")
    btn_show.setFixedWidth(36); btn_show.setFixedHeight(30)
    btn_show.setCheckable(True)
    btn_show.toggled.connect(
        lambda on: dlg.QLE_EstHib_ApiKey.setEchoMode(
            QtWidgets.QLineEdit.Normal if on else QtWidgets.QLineEdit.Password))
    row_api.addWidget(l_api); row_api.addWidget(dlg.QLE_EstHib_ApiKey, 1)
    row_api.addWidget(btn_show)
    dlg.QLE_EstHib_ApiKey.show()
    vl1.addLayout(row_api)
    pl.addWidget(c1)

    # Card capa + columna + CSV
    c2, vl2 = _section("🗺️  Selección de Datos")
    grid2 = QGridLayout(); grid2.setSpacing(8)
    l_cap = QLabel("Capa:"); l_cap.setObjectName("connLabel")
    dlg.QMLCB_CapaIA.setParent(c2)
    l_col = QLabel("Columna:"); l_col.setObjectName("connLabel")
    dlg.QCB_columnaIA.setParent(c2)
    l_csv = QLabel("Archivo CSV:"); l_csv.setObjectName("connLabel")
    dlg.QERCW_rutaIA.setParent(c2)
    # Forzar estilo oscuro penetrando los sub-widgets internos del QgsFileWidget.
    # Se usa QTimer para garantizar que Qt haya terminado de construir el árbol
    # de hijos antes de aplicar los estilos.
    def _style_rutaIA():
        from PyQt5.QtWidgets import QLineEdit as _QLE, QToolButton as _QTB
        dlg.QERCW_rutaIA.setStyleSheet(
            "QgsFileWidget, QWidget { background: transparent; border: none; }"
        )
        _le = dlg.QERCW_rutaIA.findChild(_QLE)
        if _le:
            _le.setStyleSheet(
                "background-color: #1f2937; color: #e6edf3; "
                "border: 1px solid #30363d; border-radius: 5px; "
                "padding: 4px 8px; font-size: 8.5pt;"
            )
        for _tb in dlg.QERCW_rutaIA.findChildren(_QTB):
            _tb.setStyleSheet(
                "background-color: #21262d; color: #c9d1d9; "
                "border: 1px solid #30363d; border-radius: 4px; "
                "padding: 3px 8px; font-size: 8pt; min-height: 22px;"
            )
    from PyQt5.QtCore import QTimer
    QTimer.singleShot(0, _style_rutaIA)
    grid2.addWidget(l_cap, 0, 0); grid2.addWidget(dlg.QMLCB_CapaIA, 0, 1)
    grid2.addWidget(l_col, 1, 0); grid2.addWidget(dlg.QCB_columnaIA, 1, 1)
    grid2.addWidget(l_csv, 2, 0); grid2.addWidget(dlg.QERCW_rutaIA, 2, 1)
    dlg.QMLCB_CapaIA.show()
    dlg.QCB_columnaIA.show()
    dlg.QERCW_rutaIA.show()
    vl2.addLayout(grid2)
    pl.addWidget(c2)

    # Boton ejecutar
    dlg.PB_Estandarizar_IA.setText("🚀  Ejecutar Estandarización con IA")
    dlg.PB_Estandarizar_IA.setParent(page)
    dlg.PB_Estandarizar_IA.setFixedHeight(44)
    pl.addWidget(dlg.PB_Estandarizar_IA)
    dlg.PB_Estandarizar_IA.show()
    pl.addStretch()
    return page

# -------------------------------------------------------------------------
def _build_page_actas(dlg):
    """Construye la pagina 'Generacion de Actas' con los widgets requeridos."""
    from PyQt5.QtWidgets import QLineEdit, QSizePolicy
    from qgis.gui import QgsFileWidget

    page = QWidget(); page.setObjectName("pageActas")
    pl = QVBoxLayout(page); pl.setContentsMargins(6, 6, 6, 6); pl.setSpacing(10)

    # Header del modulo
    hdr, _ = _module_header("📄", "Generación de Actas de Entrega")
    pl.addWidget(hdr)

    # ── Card 1: Configuración de API ──────────────────────────────────────
    c1, vl1 = _section("🔑  Configuración de API Gemini")

    desc_api = QLabel(
        "Ingresa tu API Key de Google Gemini para generar la descripción "
        "cartográfica con inteligencia artificial."
    )
    desc_api.setWordWrap(True); desc_api.setObjectName("descLabel")
    vl1.addWidget(desc_api)

    row_api = QHBoxLayout(); row_api.setSpacing(8)
    l_api = QLabel("API Key Gemini:"); l_api.setObjectName("connLabel"); l_api.setFixedWidth(120)

    dlg.QLE_GeminiKey = QLineEdit()
    dlg.QLE_GeminiKey.setObjectName("QLE_GeminiKey")
    dlg.QLE_GeminiKey.setPlaceholderText("Ingresa tu API Key de Google Gemini...")
    dlg.QLE_GeminiKey.setEchoMode(QLineEdit.Password)
    dlg.QLE_GeminiKey.setFixedHeight(30)

    from PyQt5.QtWidgets import QPushButton as _QPB
    btn_show_acta = _QPB("👁")
    btn_show_acta.setObjectName("togglePwd")
    btn_show_acta.setFixedWidth(36); btn_show_acta.setFixedHeight(30)
    btn_show_acta.setCheckable(True)
    btn_show_acta.toggled.connect(
        lambda on: dlg.QLE_GeminiKey.setEchoMode(
            QLineEdit.Normal if on else QLineEdit.Password))

    row_api.addWidget(l_api)
    row_api.addWidget(dlg.QLE_GeminiKey, 1)
    row_api.addWidget(btn_show_acta)
    vl1.addLayout(row_api)
    pl.addWidget(c1)

    # ── Card 2: Datos del Acta ────────────────────────────────────────────
    c2, vl2 = _section("📋  Datos del Acta de Entrega")

    grid = QGridLayout(); grid.setSpacing(8)
    grid.setColumnStretch(1, 1)

    # Carpeta de salida (QgsFileWidget en modo directorio)
    l_carpeta = QLabel("Carpeta de Salida:"); l_carpeta.setObjectName("connLabel")
    dlg.QERCW_CarpetaActa = QgsFileWidget()
    dlg.QERCW_CarpetaActa.setObjectName("QERCW_CarpetaActa")
    dlg.QERCW_CarpetaActa.setStorageMode(QgsFileWidget.GetDirectory)
    dlg.QERCW_CarpetaActa.setDialogTitle("Seleccionar carpeta con shapefiles")
    dlg.QERCW_CarpetaActa.lineEdit().setPlaceholderText("Selecciona la carpeta con los shapefiles...")
    grid.addWidget(l_carpeta,              0, 0)
    grid.addWidget(dlg.QERCW_CarpetaActa, 0, 1)

    # Número de acta
    l_num = QLabel("N° de Acta:"); l_num.setObjectName("connLabel")
    dlg.QLE_num_acta = QLineEdit()
    dlg.QLE_num_acta.setObjectName("QLE_num_acta")
    dlg.QLE_num_acta.setPlaceholderText("Ej: 001-2025 o ACT-042...")
    dlg.QLE_num_acta.setFixedHeight(30)
    grid.addWidget(l_num,            1, 0)
    grid.addWidget(dlg.QLE_num_acta, 1, 1)

    # Nombre del usuario
    l_user = QLabel("Nombre Usuario:"); l_user.setObjectName("connLabel")
    dlg.QLE_user_name = QLineEdit()
    dlg.QLE_user_name.setObjectName("QLE_user_name")
    dlg.QLE_user_name.setPlaceholderText("Nombre completo del responsable...")
    dlg.QLE_user_name.setFixedHeight(30)
    grid.addWidget(l_user,            2, 0)
    grid.addWidget(dlg.QLE_user_name, 2, 1)

    # Correo del usuario
    l_mail = QLabel("Correo Usuario:"); l_mail.setObjectName("connLabel")
    dlg.QLE_user_mail = QLineEdit()
    dlg.QLE_user_mail.setObjectName("QLE_user_mail")
    dlg.QLE_user_mail.setPlaceholderText("correo@ejemplo.com")
    dlg.QLE_user_mail.setFixedHeight(30)
    grid.addWidget(l_mail,            3, 0)
    grid.addWidget(dlg.QLE_user_mail, 3, 1)

    vl2.addLayout(grid)
    pl.addWidget(c2)

    # ── Botón de acción ───────────────────────────────────────────────────
    dlg.PBgenerar_acta = QPushButton("📄  Generar Acta de Entrega")
    dlg.PBgenerar_acta.setObjectName("PBgenerar_acta")
    dlg.PBgenerar_acta.setFixedHeight(44)
    pl.addWidget(dlg.PBgenerar_acta)

    pl.addStretch()
    return page

# -------------------------------------------------------------------------
def _build_page_val_latam(dlg):
    """
    Página del módulo Validaciones Cartográficas LATAM.
    Muestra título, descripción, carrusel de imágenes de países y botón de inicio.

    Imágenes esperadas en la carpeta images/ (PNG o JPG, 400×250 px recomendado):
        mexico.png  |  brasil.png  |  guatemala.png
        peru.png    |  argentina.png  |  chile.png
    """
    import os as _os
    from PyQt5.QtWidgets import QScrollArea, QSizePolicy as QSP
    from PyQt5.QtGui     import QPixmap, QFont, QColor
    from PyQt5.QtCore    import Qt, QTimer, QPropertyAnimation, QEasingCurve

    IMAGES_DIR = _os.path.join(_os.path.dirname(__file__), "images")
    PAISES = ["mexico", "brasil", "guatemala", "peru", "argentina", "chile"]

    page = QWidget(); page.setObjectName("pageValLatam")
    root_lay = QVBoxLayout(page)
    root_lay.setContentsMargins(0, 0, 0, 0)
    root_lay.setSpacing(0)

    # ── Scroll para que el contenido no se corte ──────────────────────────
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)
    scroll.setStyleSheet(
        "QScrollArea{background:#0d1117;border:none;}"
        "QScrollBar:vertical{background:#0d1117;width:6px;}"
        "QScrollBar::handle:vertical{background:#30363d;border-radius:3px;}"
    )

    inner = QWidget(); inner.setObjectName("valLatamInner")
    inner.setStyleSheet("background:#0d1117;")
    lay = QVBoxLayout(inner)
    lay.setContentsMargins(20, 16, 20, 20)
    lay.setSpacing(16)

    # ── Header degradado ──────────────────────────────────────────────────
    hdr_frame = QFrame()
    hdr_frame.setStyleSheet(
        "QFrame{background:qlineargradient(x1:0,y1:0,x2:1,y2:1,"
        "stop:0 #052e16,stop:0.5 #064e3b,stop:1 #0d1117);"
        "border-radius:12px;border:1px solid #10b981;}"
    )
    hdr_frame.setMinimumHeight(100)
    hdr_lay = QVBoxLayout(hdr_frame)
    hdr_lay.setContentsMargins(24, 16, 24, 16)
    hdr_lay.setSpacing(4)

    lbl_titulo = QLabel("🌎  Validaciones Cartográficas LATAM")
    lbl_titulo.setAlignment(Qt.AlignCenter)
    lbl_titulo.setStyleSheet(
        "color:#6ee7b7;font-size:18pt;font-weight:800;"
        "background:transparent;border:none;"
        "letter-spacing:1px;"
    )

    lbl_sub = QLabel("Herramienta de validación geoespacial para Latinoamérica")
    lbl_sub.setAlignment(Qt.AlignCenter)
    lbl_sub.setStyleSheet(
        "color:#10b981;font-size:9pt;font-weight:500;"
        "background:transparent;border:none;"
    )

    hdr_lay.addWidget(lbl_titulo)
    hdr_lay.addWidget(lbl_sub)
    lay.addWidget(hdr_frame)

    # ── Descripción ───────────────────────────────────────────────────────
    desc_frame = QFrame()
    desc_frame.setObjectName("sectionFrame")
    desc_lay = QVBoxLayout(desc_frame)
    desc_lay.setContentsMargins(16, 12, 16, 12)
    desc_lay.setSpacing(8)

    lbl_desc_titulo = QLabel("📋  ¿Qué hace este módulo?")
    lbl_desc_titulo.setObjectName("sectionTitle")

    desc_texto = (
        "• Valida la estructura de capas cartográficas contra el estándar LATAM.\n"
        "• Verifica tipos de datos, longitudes y campos requeridos por país.\n"
        "• Detecta inconsistencias en geometrías y atributos espaciales.\n"
        "• Compatible con Ecuador, Perú, Brasil, México, Guatemala, Chile,\n"
        "  Argentina, Colombia, Panamá, Honduras, El Salvador y más.\n"
        "• Genera reportes detallados por capa con errores y advertencias.\n"
        "• Integración directa con el visor de capas de QGIS.\n"
        "• Soporte para shapefiles y conexiones PostgreSQL/PostGIS.\n"
        "• Permite exportar los resultados de validación a CSV.\n"
        "• Actualización automática desde el repositorio oficial del equipo."
    )

    lbl_desc = QLabel(desc_texto)
    lbl_desc.setObjectName("descLabel")
    lbl_desc.setWordWrap(True)
    lbl_desc.setStyleSheet(
        "color:#c9d1d9;font-size:8.5pt;line-height:1.6;"
        "background:transparent;border:none;"
    )

    desc_lay.addWidget(lbl_desc_titulo)
    desc_lay.addWidget(lbl_desc)
    lay.addWidget(desc_frame)

    # ── Carrusel de imágenes ──────────────────────────────────────────────
    carousel_frame = QFrame()
    carousel_frame.setObjectName("sectionFrame")
    carousel_frame.setMinimumHeight(220)
    carousel_frame.setMaximumHeight(260)
    carousel_lay = QVBoxLayout(carousel_frame)
    carousel_lay.setContentsMargins(12, 10, 12, 10)
    carousel_lay.setSpacing(6)

    lbl_carousel_titulo = QLabel("🏙️  Países que abarca")
    lbl_carousel_titulo.setObjectName("sectionTitle")
    carousel_lay.addWidget(lbl_carousel_titulo)

    # Label que muestra la imagen actual
    dlg._carousel_lbl = QLabel()
    dlg._carousel_lbl.setAlignment(Qt.AlignCenter)
    dlg._carousel_lbl.setMinimumHeight(160)
    dlg._carousel_lbl.setStyleSheet(
        "background:#0d1117;border-radius:8px;border:1px solid #21262d;"
    )
    carousel_lay.addWidget(dlg._carousel_lbl, 1)

    # Indicadores de punto (dots)
    dots_row = QHBoxLayout()
    dots_row.setAlignment(Qt.AlignCenter)
    dots_row.setSpacing(6)
    dlg._carousel_dots = []
    for _ in PAISES:
        dot = QLabel("●")
        dot.setStyleSheet("color:#30363d;font-size:8pt;background:transparent;border:none;")
        dots_row.addWidget(dot)
        dlg._carousel_dots.append(dot)
    carousel_lay.addLayout(dots_row)

    # Nombre del país actual
    dlg._carousel_pais_lbl = QLabel("")
    dlg._carousel_pais_lbl.setAlignment(Qt.AlignCenter)
    dlg._carousel_pais_lbl.setStyleSheet(
        "color:#10b981;font-size:8pt;font-weight:600;"
        "background:transparent;border:none;"
    )
    carousel_lay.addWidget(dlg._carousel_pais_lbl)

    lay.addWidget(carousel_frame)

    # ── Botón iniciar ─────────────────────────────────────────────────────
    dlg.PBiniciar_val_latam = QPushButton("🌎  Iniciar Validaciones Cartográficas")
    dlg.PBiniciar_val_latam.setObjectName("PBiniciar_val_latam")
    lay.addWidget(dlg.PBiniciar_val_latam)

    # ── Botón buscar actualización ────────────────────────────────────────
    dlg.PBcheck_update_val_latam = QPushButton("🔄  Buscar Actualización del Sub-complemento")
    dlg.PBcheck_update_val_latam.setObjectName("PBcheck_update_val_latam")
    dlg.PBcheck_update_val_latam.setFixedHeight(34)
    dlg.PBcheck_update_val_latam.setStyleSheet(
        "QPushButton{background-color:#1c2128;color:#7d8590;border:1px solid #30363d;"
        "border-radius:6px;font-size:8.5pt;font-weight:500;padding:4px 14px;}"
        "QPushButton:hover{background-color:#21262d;color:#c9d1d9;border-color:#58a6ff;}"
        "QPushButton:pressed{background-color:#161b22;}"
    )
    lay.addWidget(dlg.PBcheck_update_val_latam)
    lay.addStretch()

    scroll.setWidget(inner)
    root_lay.addWidget(scroll)

    # ── Lógica del carrusel ───────────────────────────────────────────────
    nombres_display = {
        "mexico": "México 🇲🇽", "brasil": "Brasil 🇧🇷",
        "guatemala": "Guatemala 🇬🇹", "peru": "Perú 🇵🇪",
        "argentina": "Argentina 🇦🇷", "chile": "Chile 🇨🇱"
    }
    dlg._carousel_idx = 0

    def _carousel_load(idx):
        """Carga la imagen del país en el índice dado."""
        pais = PAISES[idx]
        # Intentar png y jpg
        img_path = None
        for ext in (".png", ".jpg", ".jpeg", ".PNG", ".JPG"):
            candidate = _os.path.join(IMAGES_DIR, pais + ext)
            if _os.path.exists(candidate):
                img_path = candidate
                break

        if img_path:
            pix = QPixmap(img_path)
            if not pix.isNull():
                # Escalar manteniendo aspecto
                pix = pix.scaled(
                    dlg._carousel_lbl.width() or 400,
                    dlg._carousel_lbl.height() or 180,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                dlg._carousel_lbl.setPixmap(pix)
            else:
                dlg._carousel_lbl.setText(f"🖼️  {pais}.png")
        else:
            # Placeholder si no existe la imagen
            dlg._carousel_lbl.setPixmap(QPixmap())
            dlg._carousel_lbl.setText(
                f"📁  Coloca {pais}.png en la carpeta images/"
            )
            dlg._carousel_lbl.setStyleSheet(
                "color:#484f58;font-size:9pt;background:#0d1117;"
                "border-radius:8px;border:1px dashed #30363d;"
            )

        # Actualizar dots
        for i, dot in enumerate(dlg._carousel_dots):
            dot.setStyleSheet(
                "color:#10b981;font-size:10pt;background:transparent;border:none;"
                if i == idx else
                "color:#30363d;font-size:8pt;background:transparent;border:none;"
            )

        dlg._carousel_pais_lbl.setText(nombres_display.get(pais, pais.title()))

    def _carousel_next():
        # Verificar que el objeto C++ no haya sido destruido
        try:
            import sip
            if sip.isdeleted(dlg._carousel_lbl):
                dlg._carousel_timer.stop()
                return
        except Exception:
            dlg._carousel_timer.stop()
            return
        dlg._carousel_idx = (dlg._carousel_idx + 1) % len(PAISES)
        _carousel_load(dlg._carousel_idx)

    # Cargar primera imagen
    _carousel_load(0)

    # Timer cada 3 segundos — se asigna como hijo de 'page' para que Qt
    # lo destruya automáticamente cuando la página sea eliminada
    dlg._carousel_timer = QTimer(page)
    dlg._carousel_timer.setInterval(3000)
    dlg._carousel_timer.timeout.connect(_carousel_next)
    dlg._carousel_timer.start()

    # Detener el timer al destruir la página
    page.destroyed.connect(dlg._carousel_timer.stop)

    return page
