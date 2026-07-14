# -*- coding: utf-8 -*-
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QDockWidget

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .Validaciones_LATAM_dialog import Validaciones_LATAMDialog, GeoSuitePanelWidget
import os.path
import shutil

class Validaciones_LATAM:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)

        # AUTORECUPERACIÓN  DE CREDENCIALES
        self.restaurar_credenciales()

        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Validaciones_LATAM_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.menu = self.tr(u'&GeoSuite LATAM')
        self.first_start = None
        # Referencia al DockWidget (None si no está creado)
        self._dock = None

    def restaurar_credenciales(self):
        """
        Verifica si existen las credenciales en la carpeta segura del usuario y las copia de vuelta a la carpeta del plugin si es necesario.
        """
        # Definir la ruta segura fuera de QGIS (ej: C:/Users/NombreUsuario/.geosuite_latam)
        user_home = os.path.expanduser("~")
        safe_config_dir = os.path.join(user_home, ".geosuite_latam")
        
        # Si la carpeta segura no existe en la PC del usuario, la creamos
        if not os.path.exists(safe_config_dir):
            try:
                os.makedirs(safe_config_dir)
            except Exception:
                pass

        # Lista de archivos confidenciales  que queremos blindar
        credenciales = [".env", "client_secret.json"]

        for archivo in credenciales:
            ruta_segura = os.path.join(safe_config_dir, archivo)
            ruta_plugin = os.path.join(self.plugin_dir, archivo)

            # Si el archivo vive seguro afuera, pero no está dentro del plugin (por una actualización)
            if os.path.exists(ruta_segura) and not os.path.exists(ruta_plugin):
                try:
                    shutil.copy(ruta_segura, ruta_plugin)
                except Exception:
                    # Falla silenciosa si hay problemas de permisos al copiar
                    print("Error al copiar el archivo ")
                    pass

    def tr(self, message):
        return QCoreApplication.translate('GeoSuite LATAM', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)
        if whats_this is not None:
            action.setWhatsThis(whats_this)
        if add_to_toolbar:
            self.iface.addToolBarIcon(action)
        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)

        self.actions.append(action)
        return action

    def initGui(self):
        """Registra las dos acciones en el menú y la barra de herramientas."""
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")

        # ── Acción 1: ventana flotante (comportamiento original) ──────────
        self.add_action(
            icon_path,
            text=self.tr(u'GeoSuite LATAM  (Ventana)'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # ── Acción 2: panel acoplable ─────────────────────────────────────
        self.add_action(
            icon_path,
            text=self.tr(u'GeoSuite LATAM  (Panel acoplable)'),
            callback=self.run_dock,
            add_to_toolbar=False,          # solo en menú para no saturar barra
            parent=self.iface.mainWindow())

        self.first_start = True

    def unload(self):
        """Limpia menú, barra de herramientas y cierra el dock si estaba abierto."""
        for action in self.actions:
            self.iface.removePluginMenu(self.tr(u'&GeoSuite LATAM'), action)
            self.iface.removeToolBarIcon(action)

        if self._dock is not None:
            self.iface.mainWindow().removeDockWidget(self._dock)
            self._dock.deleteLater()
            self._dock = None

    # ── Modo 1: Ventana flotante (QDialog) ────────────────────────────────
    def run(self):
        """Abre GeoSuite LATAM como ventana flotante tradicional."""
        if self.first_start is True or not hasattr(self, 'dlg'):
            self.first_start = False
            self.dlg = Validaciones_LATAMDialog()

        self.dlg.show()
        result = self.dlg.exec_()
        if result:
            pass

    # ── Modo 2: Panel acoplable (QDockWidget) ─────────────────────────────
    def run_dock(self):
        """
        Abre / muestra u oculta GeoSuite LATAM como panel acoplable lateral.
        Si ya existe y está visible, lo oculta (toggle). Si no existe, lo crea.
        """
        if self._dock is None:
            # Crear el widget de contenido
            panel_widget = GeoSuitePanelWidget(parent=self.iface.mainWindow())

            # Envolver en QDockWidget
            self._dock = QDockWidget("  🌎  GeoSuite LATAM", self.iface.mainWindow())
            self._dock.setObjectName("GeoSuiteLatamDock")
            self._dock.setWidget(panel_widget)
            self._dock.setMinimumWidth(280)
            self._dock.setAllowedAreas(
                Qt.LeftDockWidgetArea  |
                Qt.RightDockWidgetArea |
                Qt.BottomDockWidgetArea
            )
            # Limpiar referencia cuando el usuario cierre el dock manualmente
            self._dock.destroyed.connect(self._on_dock_destroyed)

            self.iface.mainWindow().addDockWidget(Qt.RightDockWidgetArea, self._dock)
            self._dock.show()

        else:
            # Toggle: si está visible lo oculta, si está oculto lo muestra
            if self._dock.isVisible():
                self._dock.hide()
            else:
                self._dock.show()
                self._dock.raise_()

    def _on_dock_destroyed(self):
        """Limpia la referencia interna cuando el dock es destruido."""
        self._dock = None
