"""
credenciales.py
---------------
Sistema seguro de gestión de credenciales para el equipo.

Flujo:
  1. Bryan cifra el archivo JSON de cuenta de servicio con una clave Fernet.
  2. El archivo cifrado (credentials.enc) se sube al repositorio de GitHub — es seguro
     porque sin la clave de descifrado es ilegible.
  3. Cada profesional recibe SOLO la clave de descifrado (por canal seguro: WhatsApp,
     Signal, Teams privado) y la pone en su config_local.py.
  4. El plugin descifra en memoria al momento de necesitar la credencial.
  5. El JSON descifrado NUNCA se escribe en disco — solo vive en RAM durante la sesión.

Para cifrar por primera vez (Bryan ejecuta esto UNA SOLA VEZ):
    python -c "from utils.credenciales import cifrar_credencial; cifrar_credencial()"
"""

import base64
import json
import os
import sys

_PLUGIN_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ENC_FILE    = os.path.join(_PLUGIN_DIR, "credentials.enc")
_KEY_ATTR    = "CREDENTIALS_KEY"
_CACHE: dict = {}   # caché en memoria para no descifrar en cada llamada


# ── Dependencia: cryptography (ya disponible en QGIS vía google-auth) ─────────

def _fernet(key: str):
    try:
        from cryptography.fernet import Fernet
        return Fernet(key.encode() if isinstance(key, str) else key)
    except ImportError:
        raise RuntimeError(
            "La librería 'cryptography' no está disponible en este entorno.\n"
            "Instálala con: pip install cryptography"
        )


# ── API pública ────────────────────────────────────────────────────────────────

def obtener_credencial_sheets() -> dict:
    """
    Retorna el dict de la cuenta de servicio de Google, descifrado en memoria.
    Lanza CredencialError si no hay clave configurada o el archivo no existe.
    """
    if "sheets" in _CACHE:
        return _CACHE["sheets"]

    key = _leer_key()
    datos_json = _descifrar(key)
    _CACHE["sheets"] = datos_json
    return datos_json


def credencial_disponible() -> bool:
    """Retorna True si el archivo cifrado existe y la clave está configurada."""
    try:
        key = _leer_key()
        return bool(key) and os.path.exists(_ENC_FILE)
    except Exception:
        return False


def limpiar_cache():
    """Limpia la credencial de memoria (llamar al cerrar QGIS o al desconectar)."""
    _CACHE.clear()


# ── Herramienta de cifrado (uso exclusivo del administrador) ──────────────────

def cifrar_credencial(ruta_json: str = None, ruta_salida: str = None) -> str:
    """
    Cifra un archivo JSON de cuenta de servicio y guarda credentials.enc.
    Retorna la clave de cifrado que debe distribuirse al equipo.

    Solo el administrador ejecuta esto. La clave resultante se comparte
    por canal seguro (NO por correo, NO por GitHub).

    Uso desde consola Python:
        from utils.credenciales import cifrar_credencial
        clave = cifrar_credencial("/ruta/a/cuenta_servicio.json")
        print("Clave para el equipo:", clave)
    """
    from cryptography.fernet import Fernet

    if ruta_json is None:
        ruta_json = input("Ruta al archivo JSON de cuenta de servicio: ").strip()

    if not os.path.exists(ruta_json):
        raise FileNotFoundError(f"No se encontró: {ruta_json}")

    with open(ruta_json, "rb") as f:
        contenido = f.read()

    # Validar que es un JSON válido de cuenta de servicio
    try:
        parsed = json.loads(contenido)
        if "type" not in parsed or parsed.get("type") != "service_account":
            raise ValueError("El archivo no parece ser una cuenta de servicio de Google.")
    except json.JSONDecodeError as e:
        raise ValueError(f"El archivo no es JSON válido: {e}")

    key    = Fernet.generate_key()
    f_obj  = Fernet(key)
    cifrado = f_obj.encrypt(contenido)

    destino = ruta_salida or _ENC_FILE
    with open(destino, "wb") as f:
        f.write(cifrado)

    clave_str = key.decode()
    print(f"\n✓ credentials.enc generado en: {destino}")
    print(f"\n🔑 CLAVE PARA EL EQUIPO (comparte solo por canal seguro):")
    print(f"   {clave_str}")
    print(f"\n⚠  Esta clave NO se guarda en ningún archivo.")
    print(f"   Cada profesional debe ponerla en su config_local.py:")
    print(f"   CREDENTIALS_KEY = \"{clave_str}\"\n")

    return clave_str


# ── Helpers internos ──────────────────────────────────────────────────────────

def _leer_key() -> str:
    if _PLUGIN_DIR not in sys.path:
        sys.path.insert(0, _PLUGIN_DIR)
    try:
        from utils.env_loader import get
        key = get(_KEY_ATTR, "")
    except Exception:
        key = ""

    if not key:
        raise CredencialError(
            f"No se encontró '{_KEY_ATTR}' en el archivo .env.\n"
            "Solicita la clave al administrador y agrégala en tu .env:\n"
            f"  {_KEY_ATTR}=tu_clave_aqui"
        )
    return key


def _descifrar(key: str) -> dict:
    if not os.path.exists(_ENC_FILE):
        raise CredencialError(
            f"No se encontró el archivo de credenciales cifradas ({_ENC_FILE}).\n"
            "Asegúrate de haber actualizado el plugin desde GitHub."
        )
    with open(_ENC_FILE, "rb") as f:
        cifrado = f.read()
    try:
        f_obj   = _fernet(key)
        descifrado = f_obj.decrypt(cifrado)
        return json.loads(descifrado)
    except Exception:
        raise CredencialError(
            "La clave de descifrado es incorrecta o el archivo está corrupto.\n"
            "Verifica que CREDENTIALS_KEY en config_local.py sea la correcta."
        )


class CredencialError(Exception):
    pass

