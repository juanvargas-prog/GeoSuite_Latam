"""
contador_intentos.py
--------------------
Rastrea cuántas veces se ha corrido la validación interna
de calidad para una orden específica.

Almacenamiento: JSON en %TEMP%/cartolatam_intentos.json
  - Persiste entre sesiones de QGIS
  - Se limpia automáticamente al reiniciar el sistema
  - Clave: nombre de la orden (NOMBRE TAREA)
"""

import json
import os
import tempfile

_ARCHIVO = os.path.join(tempfile.gettempdir(), "cartolatam_intentos.json")


def _leer() -> dict:
    try:
        with open(_ARCHIVO, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _guardar(data: dict):
    try:
        with open(_ARCHIVO, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def obtener(orden: str) -> int:
    """Retorna el número de intentos actuales para la orden."""
    return _leer().get(orden.strip(), 0)


def incrementar(orden: str) -> int:
    """Incrementa el contador de la orden y retorna el nuevo valor."""
    data = _leer()
    clave = orden.strip()
    data[clave] = data.get(clave, 0) + 1
    _guardar(data)
    return data[clave]


def resetear(orden: str):
    """Reinicia el contador de una orden (útil para pruebas)."""
    data = _leer()
    data.pop(orden.strip(), None)
    _guardar(data)


def nombre_desde_correo(correo: str) -> str:
    """
    Extrae el nombre desde un correo corporativo.
    Ej: 'bryan.mora@servinformacion.com' → 'Bryan Mora'
    """
    try:
        local = correo.strip().split("@")[0]
        partes = local.replace(".", " ").replace("_", " ").split()
        return " ".join(p.capitalize() for p in partes if p)
    except Exception:
        return correo
