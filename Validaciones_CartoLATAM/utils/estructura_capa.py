"""
estructura_capa.py
------------------
Valida que la estructura (campos, tipos, longitudes) de una capa vectorial
coincida con el esquema definido en Google Sheets para el país y producto.

Flujo:
1. Buscar qué nombre de esquema corresponde a la capa por prefijo
   ('mavvial_chile' → esquema 'mavvial')
2. Filtrar campos requeridos para el producto seleccionado
3. Verificar que los campos requeridos estén presentes con tipo y longitud correctos
4. Verificar que los campos del esquema NO requeridos para ese producto estén ausentes
5. Reportar campos completamente desconocidos (fuera del esquema)
"""

# Mapeo tipo_dato (Sheets) → set de valores válidos de QVariant.Type
_TIPO_QGIS_VALIDOS = {
    "string":   {10},       # QVariant.String
    "entero":   {2, 4},     # QVariant.Int / QVariant.LongLong
    "decimal":  {6},        # QVariant.Double
    "fecha":    {14},       # QVariant.Date
    "booleano": {1},        # QVariant.Bool
}

_TIPO_QGIS_NOMBRE = {
    10: "string",
    2:  "entero",
    4:  "entero (long)",
    6:  "decimal",
    14: "fecha",
    1:  "booleano",
}


def _norm(s):
    return str(s).strip().upper() if s is not None else ""


def buscar_schema_para_capa(nombre_capa, esquemas):
    """
    Encuentra el nombre de esquema que corresponde a esta capa.

    'mavvial_chile' → 'mavvial'  (empieza con el nombre del esquema + '_', o es igual)

    Retorna el key en `esquemas` que coincide, o None si no hay coincidencia.
    """
    nombre_lower = nombre_capa.lower()
    for schema_name in esquemas:
        sn = schema_name.lower()
        if nombre_lower == sn or nombre_lower.startswith(sn + "_"):
            return schema_name
    return None


def validar_estructura(nombre_capa, campos_qgis, esquemas, producto):
    """
    Valida la estructura de una capa vectorial contra el esquema del país.

    :param nombre_capa:  nombre de la capa en QGIS
    :param campos_qgis:  dict {campo_name: {"tipo_int": int, "longitud": int}}
                         donde tipo_int es el valor entero de QVariant.Type y
                         longitud es field.length() de la capa
    :param esquemas:     dict {schema_name: [{"campo": str, "tipo": str,
                                              "longitud": int | None,
                                              "produccion": bool,
                                              "entrega": bool,
                                              "geomarketing": bool}]}
                         (retornado por sheets_loader.cargar_esquema_estructura)
    :param producto:     "produccion" | "entrega" | "geomarketing"
    :returns:            list of error strings (lista vacía = sin errores)
    """
    if not esquemas:
        return []

    errores = []

    # 1. Buscar esquema correspondiente
    schema_name = buscar_schema_para_capa(nombre_capa, esquemas)
    if schema_name is None:
        errores.append(
            f"[SIN ESQUEMA] '{nombre_capa}' — no hay esquema definido para esta capa. "
            f"Esquemas disponibles: {', '.join(sorted(esquemas.keys()))}"
        )
        return errores

    campos_schema = esquemas[schema_name]

    # índice rápido (nombre lower → definición del campo en el esquema)
    qgis_idx          = {c.lower(): c for c in campos_qgis}
    todos_schema_lower = {_norm(f["campo"]).lower() for f in campos_schema}

    campos_requeridos = [f for f in campos_schema if f.get(producto, False)]
    campos_no_aplica  = [f for f in campos_schema if not f.get(producto, False)]

    # 2. Campos requeridos: deben estar presentes con tipo y longitud correctos
    for campo_def in campos_requeridos:
        nombre_campo = _norm(campo_def["campo"])
        nombre_lower = nombre_campo.lower()

        if nombre_lower not in qgis_idx:
            errores.append(f"[FALTANTE] '{nombre_campo}' — campo obligatorio para {producto} ausente en la capa")
            continue

        nombre_real = qgis_idx[nombre_lower]
        info        = campos_qgis[nombre_real]
        tipo_esp    = _norm(campo_def.get("tipo", "")).lower()

        # Verificar tipo
        if tipo_esp and tipo_esp in _TIPO_QGIS_VALIDOS:
            tipo_int = info["tipo_int"]
            if tipo_int not in _TIPO_QGIS_VALIDOS[tipo_esp]:
                tipo_real = _TIPO_QGIS_NOMBRE.get(tipo_int, str(tipo_int))
                errores.append(
                    f"[TIPO] '{nombre_campo}' — esperado: {tipo_esp}, la capa tiene: {tipo_real}"
                )

        # Verificar longitud (solo aplica para campos string)
        long_esp = campo_def.get("longitud")
        if long_esp and tipo_esp == "string":
            try:
                long_esp_int = int(long_esp)
                long_real    = info.get("longitud", 0)
                if long_real != long_esp_int:
                    errores.append(
                        f"[LONGITUD] '{nombre_campo}' — esperado: {long_esp_int}, la capa tiene: {long_real}"
                    )
            except (ValueError, TypeError):
                pass

    # 3. Campos del esquema que NO aplican al producto seleccionado → sobrantes de producto
    for campo_def in campos_no_aplica:
        nombre_campo = _norm(campo_def["campo"])
        if nombre_campo.lower() in qgis_idx:
            # Detectar a qué producto(s) sí aplica este campo
            _aplica_en = [p for p in ("produccion", "entrega", "geomarketing")
                          if campo_def.get(p, False)]
            _aplica_txt = " / ".join(_aplica_en) if _aplica_en else "ningún producto"
            errores.append(
                f"[SOBRANTE] '{nombre_campo}' — no aplica para {producto} "
                f"(aplica en: {_aplica_txt})"
            )

    # 4. Campos en la capa completamente ausentes del esquema → sobrantes desconocidos
    _CAMPOS_INTERNOS_QGIS = {"fid", "id", "geom", "geometry", "shape", "objectid"}
    for nombre_qgis in campos_qgis:
        if nombre_qgis.lower() in _CAMPOS_INTERNOS_QGIS:
            continue
        if nombre_qgis.lower() not in todos_schema_lower:
            errores.append(
                f"[SOBRANTE] '{nombre_qgis}' — campo no definido en el esquema del país"
            )

    return errores
