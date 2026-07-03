"""
updater.py
----------
Descarga e instala actualizaciones del plugin desde un repositorio privado de GitHub.

Flujo:
  1. Llama a la API de GitHub para obtener el último release.
  2. Compara el tag del release con la versión local en metadata.txt.
  3. Si hay versión nueva, descarga el zipball y extrae los archivos sobre el plugin.

El usuario debe tener configurado un GitHub Personal Access Token (PAT) con
permiso de lectura al repositorio en config_local.py.
"""

import json
import os
import shutil
import tempfile
import urllib.error
import urllib.request
import zipfile

PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))


def _leer_version_local():
    meta = os.path.join(PLUGIN_DIR, "metadata.txt")
    if not os.path.exists(meta):
        return "0.0.0"
    with open(meta, encoding="utf-8") as f:
        for linea in f:
            if linea.startswith("version="):
                return linea.split("=", 1)[1].strip()
    return "0.0.0"


def _version_tuple(v):
    v = v.lstrip("v")
    try:
        return tuple(int(x) for x in v.split("."))
    except ValueError:
        return (0,)


def _request_github(url, token):
    req = urllib.request.Request(url, headers={
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "utils-qgis-v2-updater",
    })
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode("utf-8"))


def bootstrap(token, repo):
    """
    Descarga e instala el último release sin comparar versiones.
    Se usa en la primera instalación cuando solo existen los archivos mínimos.
    """
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    try:
        data = _request_github(url, token)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"GitHub API respondió {e.code}: {e.reason}.")

    tag = data.get("tag_name")
    if not tag:
        raise RuntimeError("No hay ningún release publicado en el repositorio.")

    descargar_e_instalar(token, repo, tag)
    return tag


def verificar_actualizacion(token, repo):
    """
    Consulta el último release en GitHub y lo compara con la versión local.

    Retorna (hay_update: bool, tag_remoto: str, notas: str, version_local: str)
    """
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    try:
        data = _request_github(url, token)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"GitHub API respondió {e.code}: {e.reason}. Verifica el token y el nombre del repo.")

    tag_remoto    = data.get("tag_name", "0.0.0")
    notas         = data.get("body", "")
    version_local = _leer_version_local()
    hay_update    = _version_tuple(tag_remoto) > _version_tuple(version_local)

    return hay_update, tag_remoto, notas, version_local


def descargar_e_instalar(token, repo, tag):
    """
    Descarga el zipball del tag indicado y reemplaza los archivos del plugin.
    No toca config_local.py si existe.
    """
    url = f"https://api.github.com/repos/{repo}/zipball/{tag}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "utils-qgis-v2-updater",
    })

    # mkstemp evita la condición de carrera (TOCTOU) de mktemp
    _fd, tmp_zip = tempfile.mkstemp(suffix=".zip")
    os.close(_fd)
    tmp_dir = tempfile.mkdtemp()

    try:
        print(f"[Updater] Descargando {tag}…")
        _MAX_ZIP_MB = 50
        with urllib.request.urlopen(req, timeout=60) as r:
            datos = r.read(_MAX_ZIP_MB * 1024 * 1024 + 1)
        if len(datos) > _MAX_ZIP_MB * 1024 * 1024:
            raise RuntimeError(f"ZIP excede el tamaño máximo permitido ({_MAX_ZIP_MB} MB).")
        with open(tmp_zip, "wb") as f:
            f.write(datos)

        with zipfile.ZipFile(tmp_zip) as zf:
            # Validar rutas antes de extraer — previene Path Traversal
            for entry in zf.namelist():
                if ".." in entry or entry.startswith("/") or entry.startswith("\\"):
                    raise RuntimeError(f"Ruta insegura detectada en ZIP: {entry!r}")
            zf.extractall(tmp_dir)

        # El zip de GitHub genera una carpeta con formato owner-repo-sha/
        contenido = os.listdir(tmp_dir)
        if len(contenido) != 1 or not os.path.isdir(os.path.join(tmp_dir, contenido[0])):
            raise RuntimeError(f"Estructura inesperada en el ZIP: {contenido}")

        carpeta_zip = os.path.join(tmp_dir, contenido[0])

        # config_local.py se preserva siempre — las credenciales vienen del
        # ZIP bootstrap y no deben ser sobreescritas por ninguna actualización.
        # Preservar credenciales locales del profesional — nunca sobreescribir
        preservar = {".env", "credentials.enc"}

        print(f"[Updater] Instalando en {PLUGIN_DIR}…")
        for item in os.listdir(carpeta_zip):
            if item in preservar:
                continue
            src = os.path.join(carpeta_zip, item)
            dst = os.path.join(PLUGIN_DIR, item)
            if os.path.isdir(src):
                if os.path.exists(dst):
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)

        print(f"[Updater] Plugin actualizado a {tag}.")

    finally:
        if os.path.exists(tmp_zip):
            os.remove(tmp_zip)
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir, ignore_errors=True)

