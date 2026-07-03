"""
config.py
---------
Constantes y helpers puros compartidos por toda la herramienta.

No importa nada de QGIS — puede ser usado tanto por el hilo
principal como por los workers de multiprocessing.
"""

import os
import sys
from math import ceil


# ── Módulos que NO son campos (infraestructura, no validadores) ───────────────
_NO_SON_CAMPOS = {
    "config", "geo_codigos", "sheets_loader",
    "cruce_capas", "reporte_html", "gmail_sender", "topologia",
}

# ── CAMPOS_CONOCIDOS: se construye automáticamente ────────────────────────────
# Lee todos los archivos .py de esta carpeta que no empiecen con _ y
# no estén en _NO_SON_CAMPOS. Cada archivo = un campo que se sabe validar.
# Para agregar un campo nuevo basta con crear utils/nuevo_campo.py.
_dir_utils = os.path.dirname(os.path.abspath(__file__))

CAMPOS_CONOCIDOS = {
    f[:-3]                          # quitar .py
    for f in os.listdir(_dir_utils)
    if f.endswith(".py")
    and not f.startswith("_")
    and f[:-3] not in _NO_SON_CAMPOS
}

# Campos geo-código que valida geo_codigos.py pero no tienen módulo propio
# (son demasiados para un archivo por cada uno — se agrupan por jerarquía)
_CAMPOS_GEO_CODIGOS = {
    "cod_reg",    "nom_reg",
    "cod_prov",   "nom_prov",
    "cod_com",    "nom_com",
    "cod_dep",    "nom_dep",
    "cod_zona",   "nom_zona",
    "cod_alc",    "nom_alc",
    "cod_loc",    "nom_loc",
    "cod_col",    "nom_col",
    "cod_can",    "nom_can",
    "cod_parroq", "nom_parroq",
    "cod_correg", "nom_correg",
    "cod_canton", "nom_canton",
    "cod_parr",   "nom_parr",
    "cod_postal", "cod_post",
}

CAMPOS_CONOCIDOS |= _CAMPOS_GEO_CODIGOS


# ── Campos opcionales en líneas ───────────────────────────────────────────────
# En capas de LÍNEAS estos campos pueden estar vacíos sin ser error.
CAMPOS_OPCIONALES_LINEAS = {
    "cep", "costado", "generadora", "rango_par", "rango_imp",
    # Campos de dirección extendida (opcionales en todos los tipos)
    "manzana", "casa_lote", "nom_urb",
}


# ── Rendimiento ───────────────────────────────────────────────────────────────
BATCH_SIZE = 5000   # features por batch al insertar en la capa resultado
UI_CADA    = 500    # cada cuántos features se llama processEvents()


# ── Helpers puros ─────────────────────────────────────────────────────────────

def normalizar(val):
    """Convierte NULL de QGIS a None; deja el resto igual."""
    if val is None:
        return None
    s = str(val)
    return None if s in ("NULL", "None") else val


def es_vacio(val):
    """Retorna True si el valor es None o string vacío."""
    return val is None or str(val).strip() == ""


def chunk_list(lst, n):
    """Divide una lista en n partes aproximadamente iguales."""
    if not lst:
        return []
    if n <= 0:
        return [lst]
    size = max(1, ceil(len(lst) / n))
    return [lst[i:i + size] for i in range(0, len(lst), size)]


# ── Ocultar ventanas CMD en Windows ──────────────────────────────────────────

def ocultar_ventanas_cmd():
    """
    En Windows, evita que los workers de multiprocessing abran
    ventanas de CMD visibles al usuario.

    Multiprocessing usa _winapi.CreateProcess directamente (no subprocess),
    por eso hay que parchear a ese nivel.
    El flag CREATE_NO_WINDOW (0x08000000) oculta la ventana del proceso hijo.

    Debe llamarse una vez antes de crear el Pool.
    """
    if sys.platform != "win32":
        return
    try:
        import _winapi
        import multiprocessing.popen_spawn_win32 as _psw  # noqa: F401 — side-effect: pre-carga el módulo de spawn

        CREATE_NO_WINDOW = 0x08000000
        _orig_create = _winapi.CreateProcess

        def _create_sin_ventana(app, cmd, proc_sec, thr_sec,
                                inherit, flags, env, cwd, startup):
            return _orig_create(
                app, cmd, proc_sec, thr_sec,
                inherit,
                flags | CREATE_NO_WINDOW,   # <- aquí estaba el 0
                env, cwd, startup,
            )

        _winapi.CreateProcess = _create_sin_ventana
    except Exception as e:
        print(f"  Nota: no se pudo suprimir ventanas CMD ({e})")
