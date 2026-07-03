import os
import sys

PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
_BOOTSTRAP_ERROR = [""]


def _leer_env() -> dict:
    """
    Lee el archivo .env directamente — sin importar utils/ que aún no existe
    durante el bootstrap. Parser mínimo: clave=valor, ignora comentarios.
    """
    env_path = os.path.join(PLUGIN_DIR, ".env")
    resultado = {}
    if not os.path.exists(env_path):
        return resultado
    try:
        with open(env_path, encoding="utf-8-sig") as f:
            for linea in f:
                linea = linea.rstrip("\n\r").strip()
                if not linea or linea.startswith("#"):
                    continue
                if "=" in linea:
                    clave, _, valor = linea.partition("=")
                    clave = clave.strip()
                    valor = valor.strip().strip('"').strip("'")
                    if clave:
                        resultado[clave] = valor
    except Exception:
        pass
    return resultado


def _bootstrap():
    """Descarga el plugin completo desde GitHub si aún no está instalado."""
    if os.path.exists(os.path.join(PLUGIN_DIR, "plugin.py")):
        return True

    # Leer .env directamente — utils/ no existe aún
    env = _leer_env()
    token = env.get("GITHUB_TOKEN", "").strip()
    repo  = env.get("GITHUB_REPO",  "").strip()

    if not token or not repo:
        _BOOTSTRAP_ERROR[0] = (
            "No se encontró GITHUB_TOKEN o GITHUB_REPO en el archivo .env.\n"
            f"El archivo .env debe estar en:\n{PLUGIN_DIR}"
        )
        return False

    if "xxxx" in token.lower():
        _BOOTSTRAP_ERROR[0] = "GITHUB_TOKEN no configurado en el archivo .env"
        return False

    if "/" not in repo:
        _BOOTSTRAP_ERROR[0] = "GITHUB_REPO debe tener formato usuario/repositorio"
        return False

    try:
        from . import updater
        tag = updater.bootstrap(token, repo)
        print(f"[Validaciones CartoLatam] Plugin instalado desde GitHub: {tag}")
        return True
    except Exception as e:
        _BOOTSTRAP_ERROR[0] = str(e)
        print(f"[Validaciones CartoLatam] Error en bootstrap: {e}")
        return False


def classFactory(iface):
    ok = _bootstrap()

    if not ok:
        class _PluginError:
            def __init__(self, iface):
                self._iface = iface
                self._action = None
            def initGui(self):
                from qgis.PyQt.QtWidgets import QAction, QMessageBox
                self._action = QAction(
                    "Validaciones CartoLatam — Error de instalación",
                    self._iface.mainWindow(),
                )
                msg = _BOOTSTRAP_ERROR[0] or "Error desconocido"
                self._action.triggered.connect(lambda: QMessageBox.critical(
                    self._iface.mainWindow(),
                    "Validaciones CartoLatam",
                    f"No se pudo descargar el plugin desde GitHub.\n\n"
                    f"Detalle: {msg}",
                ))
                self._iface.addPluginToMenu("&Validaciones CartoLatam", self._action)
            def unload(self):
                if self._action:
                    self._iface.removePluginMenu("&Validaciones CartoLatam", self._action)
        return _PluginError(iface)

    from .plugin import ValidacionesCartolatamPlugin
    return ValidacionesCartolatamPlugin(iface)
