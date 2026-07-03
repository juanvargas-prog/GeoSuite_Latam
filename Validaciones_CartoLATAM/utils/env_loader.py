"""
env_loader.py
-------------
Carga variables de configuración desde un archivo .env.

Por qué .env en lugar de config_local.py:
  - config_local.py es código Python ejecutable — si alguien lo modifica puede
    inyectar código que se ejecuta automáticamente al abrir QGIS (CRÍTICO-4).
  - .env solo contiene pares clave=valor (datos, no código) — nunca se ejecuta.
  - Es el estándar de la industria para configuración local de aplicaciones.

Formato del .env:
  GITHUB_TOKEN=ghp_xxxxx
  GMAIL_REMITENTE=correo@empresa.com
  GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
  # Las líneas que empiezan con # son comentarios
  # Las líneas vacías se ignoran
  # Las comillas en los valores son opcionales y se eliminan automáticamente

No requiere librerías externas — parser implementado con solo stdlib.
"""

import os

_PLUGIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ENV_FILE   = os.path.join(_PLUGIN_DIR, ".env")

# Caché en memoria para no releer el archivo en cada llamada
_cache: dict[str, str] | None = None


def get(key: str, default: str = "") -> str:
    """
    Retorna el valor de una variable de configuración.
    Busca en .env primero; si no existe, busca en config_local.py como fallback.
    """
    global _cache
    if _cache is None:
        _cache = _cargar_env()
    valor = _cache.get(key)
    if valor is not None:
        return valor
    # Fallback a config_local.py para compatibilidad con instalaciones anteriores
    return _fallback_config_local(key, default)


def reload():
    """Fuerza la recarga del archivo .env (útil si el usuario lo editó en sesión)."""
    global _cache
    _cache = None


def save(updates: dict) -> None:
    """
    Actualiza o agrega claves en el archivo .env sin borrar las existentes.
    Crea el archivo si no existe.
    """
    # Leer líneas actuales
    lineas: list[str] = []
    if os.path.exists(_ENV_FILE):
        with open(_ENV_FILE, encoding="utf-8") as f:
            lineas = f.readlines()

    actualizadas: set[str] = set()
    nuevas: list[str] = []

    for linea in lineas:
        stripped = linea.strip()
        if not stripped or stripped.startswith("#"):
            nuevas.append(linea)
            continue
        if "=" in stripped:
            clave = stripped.split("=", 1)[0].strip()
            if clave in updates:
                nuevas.append(f"{clave}={updates[clave]}\n")
                actualizadas.add(clave)
                continue
        nuevas.append(linea)

    # Claves nuevas que no existían en el archivo
    for clave, valor in updates.items():
        if clave not in actualizadas:
            nuevas.append(f"{clave}={valor}\n")

    with open(_ENV_FILE, "w", encoding="utf-8") as f:
        f.writelines(nuevas)

    reload()   # invalidar caché para que los cambios sean inmediatos


def _cargar_env() -> dict[str, str]:
    """
    Parsea el archivo .env y retorna un dict con las variables.
    Soporta: comentarios (#), líneas vacías, valores con/sin comillas,
    valores con espacios (ej: App Passwords de Google).
    """
    resultado: dict[str, str] = {}
    if not os.path.exists(_ENV_FILE):
        return resultado
    try:
        with open(_ENV_FILE, encoding="utf-8") as f:
            for linea in f:
                linea = linea.rstrip("\n\r")
                # Ignorar líneas vacías y comentarios
                stripped = linea.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                if "=" not in stripped:
                    continue
                clave, _, valor = stripped.partition("=")
                clave = clave.strip()
                valor = valor.strip()
                # Eliminar comillas encuadernadas (simples o dobles)
                if len(valor) >= 2:
                    if (valor[0] == '"'  and valor[-1] == '"') or \
                       (valor[0] == "'" and valor[-1] == "'"):
                        valor = valor[1:-1]
                if clave:
                    resultado[clave] = valor
    except Exception:
        pass  # si el archivo es ilegible no bloqueamos QGIS
    return resultado


def _fallback_config_local(key: str, default: str) -> str:
    """
    Fallback eliminado por seguridad.
    config_local.py ejecutaba código Python arbitrario (exec_module),
    lo que permitía inyección de código si el archivo era modificado.
    Toda la configuración debe venir del archivo .env.
    """
    return default
