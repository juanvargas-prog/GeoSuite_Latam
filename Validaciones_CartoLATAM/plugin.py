import os
import importlib
import sys
import threading

from qgis.PyQt.QtWidgets import QAction, QMessageBox
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QTimer

PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))


def _leer_config():
    """Lee credenciales desde .env (o config_local.py como fallback)."""
    if PLUGIN_DIR not in sys.path:
        sys.path.insert(0, PLUGIN_DIR)
    try:
        from utils.env_loader import get, reload
        reload()   # fuerza relectura para capturar cambios en sesión
        token = get("GITHUB_TOKEN")
        repo  = get("GITHUB_REPO")
        return token or None, repo or None
    except Exception:
        return None, None


class ValidacionesCartolatamPlugin:

    def __init__(self, iface):
        self.iface   = iface
        self._actions = []

    def initGui(self):
        icon_path = os.path.join(PLUGIN_DIR, "icon.png")
        icon = QIcon(icon_path) if os.path.exists(icon_path) else QIcon()

        accion_validar    = QAction(icon, "Validar capas…", self.iface.mainWindow())
        accion_actualizar = QAction("Buscar actualización",  self.iface.mainWindow())

        accion_validar.triggered.connect(self.run)
        accion_actualizar.triggered.connect(self.check_update)

        self.iface.addPluginToMenu("&Validaciones CartoLatam", accion_validar)
        self.iface.addPluginToMenu("&Validaciones CartoLatam", accion_actualizar)
        self.iface.addToolBarIcon(accion_validar)
        self._actions = [accion_validar, accion_actualizar]

        # Verificar actualizaciones automáticamente 6 segundos después de cargar QGIS
        QTimer.singleShot(6000, self._auto_check_update)

    def unload(self):
        for action in self._actions:
            self.iface.removePluginMenu("&Validaciones CartoLatam", action)
        self.iface.removeToolBarIcon(self._actions[0])
        self._actions.clear()

    def run(self):
        if PLUGIN_DIR not in sys.path:
            sys.path.insert(0, PLUGIN_DIR)

        for nombre in list(sys.modules):
            if nombre.startswith("utils") or nombre == "dialogo_principal":
                try:
                    importlib.reload(sys.modules[nombre])
                except Exception:
                    pass

        from .dialogo_principal import DialogoPrincipal
        dlg = DialogoPrincipal(self.iface, parent=self.iface.mainWindow())
        dlg.exec_()

    # ── Verificación automática al iniciar ────────────────────────────────────

    def _auto_check_update(self):
        """Chequea actualizaciones en un hilo para no bloquear la UI."""
        def _worker():
            try:
                token, repo = _leer_config()
            except Exception:
                return

            if not token or not repo:
                return

            try:
                from . import updater
                hay_update, tag, notas, ver_local = updater.verificar_actualizacion(token, repo)
            except Exception:
                return  # Sin conexión o error de red — se ignora silenciosamente

            if hay_update:
                # Volver al hilo principal para mostrar el diálogo
                QTimer.singleShot(0, lambda: self._mostrar_aviso_update(tag, notas, ver_local, token, repo))

        threading.Thread(target=_worker, daemon=True).start()

    def _mostrar_aviso_update(self, tag, notas, ver_local, token, repo):
        extracto = (notas[:500] + "…") if len(notas) > 500 else notas
        resp = QMessageBox.question(
            self.iface.mainWindow(),
            "Actualización disponible — Validaciones CartoLatam",
            f"<b>Nueva versión: {tag}</b>  (instalada: {ver_local})<br><br>"
            f"{extracto}<br><br>"
            f"¿Descargar e instalar ahora? QGIS debe reiniciarse al terminar.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if resp != QMessageBox.Yes:
            return
        try:
            from . import updater
            updater.descargar_e_instalar(token, repo, tag)
            QMessageBox.information(
                self.iface.mainWindow(),
                "Actualización completada",
                f"Plugin actualizado a {tag}.\nReinicia QGIS para aplicar los cambios.",
            )
        except Exception as e:
            QMessageBox.critical(self.iface.mainWindow(),
                                 "Error al instalar actualización", str(e))

    # ── Verificación manual desde el menú ────────────────────────────────────

    def check_update(self):
        try:
            token, repo = _leer_config()
        except Exception:
            token, repo = None, None

        if not token or not repo:
            QMessageBox.warning(
                self.iface.mainWindow(), "Actualización",
                "No se encontró GITHUB_TOKEN o GITHUB_REPO en el archivo .env.\n\n"
                "Verifica que el archivo .env esté en la carpeta del plugin\n"
                "o configura tu correo desde ⚙ Configurar correo en la herramienta.",
            )
            return

        from . import updater
        try:
            hay_update, tag, notas, ver_local = updater.verificar_actualizacion(token, repo)
        except Exception as e:
            QMessageBox.critical(self.iface.mainWindow(),
                                 "Error al verificar actualización", str(e))
            return

        if not hay_update:
            QMessageBox.information(self.iface.mainWindow(), "Sin actualizaciones",
                                    f"Ya tienes la versión más reciente ({ver_local}).")
            return

        extracto = (notas[:600] + "…") if len(notas) > 600 else notas
        resp = QMessageBox.question(
            self.iface.mainWindow(), "Actualización disponible",
            f"<b>Nueva versión: {tag}</b>  (instalada: {ver_local})<br><br>"
            f"{extracto}<br><br>¿Descargar e instalar ahora?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if resp != QMessageBox.Yes:
            return

        try:
            updater.descargar_e_instalar(token, repo, tag)
            QMessageBox.information(
                self.iface.mainWindow(), "Actualización completada",
                f"Plugin actualizado a {tag}.\nReinicia QGIS para aplicar los cambios.",
            )
        except Exception as e:
            QMessageBox.critical(self.iface.mainWindow(),
                                 "Error al instalar actualización", str(e))
