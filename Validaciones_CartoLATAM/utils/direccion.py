"""
direccion.py
------------
Validaciones para el campo direccion.

Reglas generales:
- Campo alfanumérico, todo en MAYÚSCULAS.
- Sin caracteres especiales (se permiten letras, números, espacios y comas).
- La estructura varía por país (ver ESTRUCTURAS_PAIS).
- Formato de concatenación:
    · Si el patrón contiene 'nomvtotal' + 'placa': se unen con espacio
      y el resto de componentes se separan con ", ".
      Ejemplo: "AVENIDA LAS FLORES 123, BARRIO NORTE, DISTRITO 1, SAO PAULO"
    · Si el patrón NO contiene 'placa': todos los componentes
      se separan con ", ".
      Ejemplo: "URB LOS PINOS, MZ A, LT 5, MIRAFLORES"
- Los campos vacíos o nulos se omiten de la concatenación.
- Los valores de cada componente deben coincidir exactamente con
  los valores de los campos correspondientes en la misma fila.

Nota sobre campos opcionales en patrones:
  manzana y casa_lote pueden estar vacíos; si lo están se omiten
  de la dirección esperada sin generar error.
"""

import re

from ._generales import (
    PATRON_TEXTO_NUMEROS_BRASIL,
    PATRON_TEXTO_CON_NUMEROS,
)

# ── Estructuras válidas por país ──────────────────────────────────────────────
# Cada entrada es una lista de patrones posibles.
# Cada patrón es una tupla de nombres de campo (en minúsculas) en orden.
# El validador acepta la dirección si coincide con CUALQUIERA de los patrones.

ESTRUCTURAS_PAIS = {
    "Brasil": [
        ("nomvtotal", "placa", "nom_bar", "nom_distri", "nom_mun", "cep", "nom_estado"),
    ],
    "Chile": [
        ("nomvtotal", "placa", "nom_com", "nom_prov"),                    # resto del país
        ("nomvtotal", "placa", "nom_urb", "nom_com", "nom_prov"),         # RM (cod_reg=13)
    ],
    "Perú": [
        ("nomvtotal", "placa", "nom_distri"),
        ("nomvtotal", "manzana", "casa_lote", "nom_distri"),
        ("nom_urb", "manzana", "casa_lote", "nom_distri"),
    ],
    "Argentina": [
        ("nomvtotal", "placa", "nom_mun", "nom_dep", "nom_prov"),
    ],
    "Guatemala": [
        ("nomvtotal", "generadora", "placa", "nom_zona", "nom_mun", "nom_dep"),
    ],
    "Mexico": [
        ("nomvtotal", "placa", "nom_col", "nom_mun", "cod_postal", "nom_estado"),
    ],
    "El Salvador": [
        ("nomvtotal", "placa", "nom_col", "nom_distri", "nom_mun"),
        ("nom_col", "manzana", "casa_lote"),
    ],
    "Ecuador":              [("nomvtotal", "placa")],
    "Panamá":               [("nomvtotal", "placa")],
    "Honduras":             [("nomvtotal", "placa")],
    "Republica Dominicana": [("nomvtotal", "placa")],
    "Puerto Rico":          [("nomvtotal", "placa")],
    "Costa Rica":           [("nomvtotal", "placa")],
    "Venezuela": [
        ("nomvtotal", "placa", "cod_postal", "nom_parr"),  # con placa
        ("nomvtotal", "cod_postal", "nom_parr"),            # sin placa
    ],
}

# Campos que pueden estar vacíos dentro de un patrón sin invalidarlo
_CAMPOS_OPCIONALES_EN_PATRON = {"manzana", "casa_lote"}

# Pares de campos adyacentes que se unen con guion en la dirección construida
# Ejemplo: Guatemala → generadora=14, placa=65 → "14-65"
_PARES_CON_GUION = {("generadora", "placa")}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _val(d, campo):
    """Retorna el valor del campo normalizado a string en mayúsculas, o None si vacío."""
    v = d.get(campo)
    if v is None or str(v).strip() in ("", "NULL", "None"):
        return None
    return str(v).strip().upper()


def _construir_direccion(patron, d):
    """
    Construye el valor esperado de la dirección dado un patrón y los valores de la fila.
    Retorna None si los campos obligatorios del patrón están vacíos.

    Regla de formato:
      - Si el patrón contiene 'nomvtotal' seguido de 'placa' (o bloque generadora-placa):
          "{nomvtotal} {placa}, {comp3}, {comp4}, ..."
          "{nomvtotal} {generadora}-{placa}, {comp3}, ..."  ← Guatemala
      - En cualquier otro caso:
          "{comp1}, {comp2}, {comp3}, ..."
    """
    # Recopilar valores no vacíos en orden
    campos_con_valor = []
    for campo in patron:
        v = _val(d, campo)
        if v is not None:
            campos_con_valor.append((campo, v))
        elif campo not in _CAMPOS_OPCIONALES_EN_PATRON:
            # Campo obligatorio vacío — este patrón no aplica
            return None

    if not campos_con_valor:
        return None

    # Fusionar pares adyacentes con guion (ej: generadora + placa → "14-65")
    fusionados = []
    i = 0
    while i < len(campos_con_valor):
        if i + 1 < len(campos_con_valor):
            par = (campos_con_valor[i][0], campos_con_valor[i + 1][0])
            if par in _PARES_CON_GUION:
                fusionados.append(
                    ("_bloque_guion_", campos_con_valor[i][1] + "-" + campos_con_valor[i + 1][1])
                )
                i += 2
                continue
        fusionados.append(campos_con_valor[i])
        i += 1

    nombres = [c for c, _ in fusionados]
    valores = [v for _, v in fusionados]

    # Detectar si hay bloque nomvtotal seguido de placa o de bloque generadora-placa
    idx_nvt = nombres.index("nomvtotal") if "nomvtotal" in nombres else -1
    tiene_bloque_nvt_placa = (
        idx_nvt >= 0
        and idx_nvt + 1 < len(nombres)
        and nombres[idx_nvt + 1] in ("placa", "_bloque_guion_")
    )

    if tiene_bloque_nvt_placa:
        bloque_inicio = valores[idx_nvt] + " " + valores[idx_nvt + 1]
        resto = valores[idx_nvt + 2:]
        if resto:
            return bloque_inicio + ", " + ", ".join(resto)
        return bloque_inicio
    else:
        # Todos los componentes separados por comas
        return ", ".join(valores)


# ── Patrones condicionales por país ──────────────────────────────────────────

def _patrones_chile(d):
    """
    Retorna el patrón de dirección para Chile según la región.

    RM (cod_reg=13): nomvtotal placa nom_urb nom_com nom_prov
    Resto:           nomvtotal placa         nom_com nom_prov
    """
    cod_reg = str(d.get("cod_reg", "")).strip()
    if cod_reg == "13":
        return [
            ("nomvtotal", "placa", "nom_urb", "nom_com", "nom_prov"),  # con nom_urb
            ("nomvtotal", "placa", "nom_com", "nom_prov"),              # fallback si nom_urb vacío
        ]
    return [("nomvtotal", "placa", "nom_com", "nom_prov")]


# ── Validación principal ──────────────────────────────────────────────────────

def validar(valor, d=None, pais="default"):
    """
    Valida el campo direccion.

    :param valor: valor del campo direccion
    :param d    : dict con todos los valores de la fila (para validación cruzada)
    :param pais : nombre del país
    """
    errores = []
    nombre = "direccion"

    # ── Vacío ──────────────────────────────────────────────────────────────
    if valor is None or str(valor).strip() == "":
        errores.append(f"El {nombre} no puede estar vacío")
        return errores

    valor = str(valor).strip()

    # ── Mayúsculas ─────────────────────────────────────────────────────────
    if valor != valor.upper():
        errores.append(f"El {nombre} debe estar completamente en MAYÚSCULAS")

    # ── Caracteres permitidos (varía por país) ────────────────────────────
    # Para Brasil: letras del portugués + lenguas de inmigración.
    # Para el resto: letras estándar + acentuadas.
    # En todos los casos se admiten: números, espacios, comas y guion (-).
    patron_chars = PATRON_TEXTO_NUMEROS_BRASIL if pais == "Brasil" else PATRON_TEXTO_CON_NUMEROS
    # Normalizar comas y guiones a espacio antes de aplicar el patrón
    valor_norm_chars = valor.replace(",", " ").replace("-", " ")
    if not patron_chars.match(valor_norm_chars.strip()):
        if pais == "Brasil":
            errores.append(
                f"El {nombre} contiene caracteres no permitidos. "
                f"Para Brasil se admiten letras (incluye Ã, Ç, É, Ê, Â, Ó, Ô, Ü, Ä, Ö…), "
                f"números, espacios, comas y guion (-)."
            )
        else:
            errores.append(
                f"El {nombre} contiene caracteres no permitidos. "
                f"Solo se admiten letras, números, espacios, comas y guion (-)."
            )

    # Si ya hay errores de formato no seguimos con validación cruzada
    if errores:
        return errores

    # ── Validación cruzada contra valores de la fila ───────────────────────
    if d is None:
        return errores  # sin datos de fila, no podemos validar estructura

    if pais == "Chile":
        patrones = _patrones_chile(d)
    else:
        patrones = ESTRUCTURAS_PAIS.get(pais)
    if not patrones:
        return errores  # país sin estructura definida, no validamos estructura

    # Construir la dirección esperada para cada patrón del país
    esperados = []
    for patron in patrones:
        esperado = _construir_direccion(patron, d)
        if esperado is not None:
            esperados.append((patron, esperado))

    if not esperados:
        # No se pudo construir ningún esperado (campos vacíos, etc.)
        return errores

    # Verificar si el valor coincide con alguno de los esperados
    valor_norm = " ".join(valor.upper().split())  # normalizar espacios múltiples
    for patron, esperado in esperados:
        esperado_norm = " ".join(esperado.split())
        if valor_norm == esperado_norm:
            return errores  # coincide — sin error

    # No coincidió con ningún patrón
    errores.append(f"El {nombre} está mal estructurado para {pais}")

    return errores
