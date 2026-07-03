"""
validar_capa.py
---------------
Punto de entrada para ejecución desde la consola de QGIS via exec().
Limpia el caché de módulos y abre el DialogoPrincipal.

Uso:
    exec(compile(Path('ruta/validar_capa.py').read_text(), 'ruta/validar_capa.py', 'exec'))
"""

import sys
import os
import importlib


# ── Detectar ruta del plugin ──────────────────────────────────────────────────
def _detectar_ruta():
    # 1. Si exec() define __file__ correctamente (ruta real del plugin)
    try:
        ruta = os.path.dirname(os.path.abspath(__file__))
        if os.path.isfile(os.path.join(ruta, "dialogo_principal.py")):
            return ruta
    except NameError:
        pass

    # 2. Buscar en sys.path una ruta que contenga dialogo_principal.py
    for p in sys.path:
        if os.path.isfile(os.path.join(p, "dialogo_principal.py")):
            return p

    # 3. Rutas conocidas del equipo de desarrollo
    _candidatos = [
        r"C:\Users\bmora\Documents\Herramientas\validaciones_cartolatam_plugin\validaciones_cartolatam",
        r"C:\Users\bmora\Documents\Herramientas\validaciones_cartolatam\validaciones_cartolatam",
        r"C:\Users\bmora\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\Validaciones_CartoLATAM",
        r"C:\Users\bmora\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\validaciones_cartolatam",
    ]
    for c in _candidatos:
        if os.path.isfile(os.path.join(c, "dialogo_principal.py")):
            return c

    raise RuntimeError(
        "No se encontró el directorio del plugin.\n"
        "Agrega la ruta manualmente en validar_capa.py → _candidatos."
    )


RUTA_UTILS = _detectar_ruta()
if RUTA_UTILS not in sys.path:
    sys.path.insert(0, RUTA_UTILS)


# ── Limpiar caché completamente ───────────────────────────────────────────────
_PREFIJOS = ("utils", "dialogo_principal", "config_local", "validaciones_cartolatam")
for _k in list(sys.modules.keys()):
    if any(_k == p or _k.startswith(p + ".") for p in _PREFIJOS):
        del sys.modules[_k]


# ── Reimportar módulos frescos ────────────────────────────────────────────────
_MODULOS = [
    "utils", "utils.config",
    # Validadores de vías
    "utils._generales", "utils.id_capa", "utils.tipo_dir", "utils.tipovia", "utils.tipo_urb",
    "utils.nomvia", "utils.nomvtotal", "utils.nomcomun", "utils.generadora",
    "utils.costado", "utils.rango_par", "utils.rango_imp", "utils.oneway",
    "utils.velocidad", "utils.marca_vial", "utils.id_mavvial", "utils.placa",
    # Geocódigos
    "utils.cod_estado", "utils.nom_estado", "utils.cod_mun", "utils.nom_mun",
    "utils.cod_distri", "utils.nom_distri", "utils.cod_bar", "utils.nom_bar",
    # Actualización
    "utils.marca", "utils.fecha", "utils.version", "utils.cep",
    # Sitios / POI
    "utils.categoria", "utils.nom_subcat", "utils.direccion",
    "utils.manzana", "utils.casa_lote", "utils.nom_urb",
    # Infraestructura
    "utils.geo_codigos", "utils.sheets_loader", "utils._worker",
    "utils.cruce_capas", "utils.reporte_html", "utils.gmail_sender",
    "utils.topologia", "utils.estructura_capa", "utils.validar_documentacion",
    # UI principal
    "dialogo_principal",
]
for _m in _MODULOS:
    try:
        importlib.import_module(_m)
    except ImportError:
        pass


# ── Abrir el diálogo ──────────────────────────────────────────────────────────
def ejecutar_validacion():
    from dialogo_principal import DialogoPrincipal
    _iface = globals().get("iface")
    dlg = DialogoPrincipal(_iface)
    dlg.exec_()


# Se ejecuta solo cuando se llama via exec() desde la consola de QGIS.
# __spec__ está definido cuando Python importa el archivo como módulo de plugin.
if not globals().get("__spec__"):
    ejecutar_validacion()
