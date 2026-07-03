"""
Validaciones para el campo tipo_dir.
Reglas:
- Debe ser CARDINAL o MZCASA
- No puede estar vacío si el campo existe en la capa
"""

_VALORES_VALIDOS = {"CARDINAL", "MZCASA"}


def validar(valor, pais="default"):
    """Valida el campo tipo_dir: debe ser CARDINAL o MZCASA, no vacío."""
    errores = []
    nombre = "tipo_dir"

    if valor is None or str(valor).strip() == "":
        errores.append(f"El {nombre} no puede estar vacío")
        return errores

    val_str = str(valor).strip().upper()

    if val_str not in _VALORES_VALIDOS:
        errores.append(
            f"El {nombre} debe ser CARDINAL o MZCASA, recibido '{val_str}'"
        )

    return errores
