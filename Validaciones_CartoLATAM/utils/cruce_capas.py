"""
cruce_capas.py
--------------
Validación cruzada de geo-códigos entre capas de distinto tipo geométrico.

Lógica:
  - Capas de POLÍGONOS = referencia (contienen los códigos válidos del territorio)
  - Capas de PUNTOS y LÍNEAS = se validan contra los polígonos

  Para cada campo geo-código presente en una capa de puntos o líneas,
  se verifica que cada valor único exista en al menos una capa de polígonos
  que también tenga ese campo.

  Si no hay ninguna capa de polígonos con ese campo → aviso (sin_capa_referencia).
  Si el valor no aparece en ningún polígono → error (valor_huerfano).

Jerarquía por país:
  Solo se validan los campos definidos en JERARQUIA_PAIS para el país activo.
  No se validan nom_* (solo cod_*).
"""

from .geo_codigos import REGLAS_PAIS

# Campos cod_* relevantes por país (de mayor a menor nivel)
JERARQUIA_PAIS = {
    "Brasil":               ["cod_estado", "cod_mun",    "cod_distri", "cod_bar"],
    "Chile":                ["cod_reg",    "cod_prov",   "cod_com"],
    "Perú":                 ["cod_dep",    "cod_prov",   "cod_distri"],
    "Argentina":            ["cod_prov",   "cod_dep",    "cod_mun"],
    "Guatemala":            ["cod_dep",    "cod_mun",    "cod_zona"],
    "Mexico":               ["cod_estado", "cod_mun",    "cod_alc",    "cod_loc",  "cod_col"],
    "El Salvador":          ["cod_dep",    "cod_mun",    "cod_distri", "cod_canton","cod_col"],
    "Ecuador":              ["cod_prov",   "cod_can",    "cod_parroq"],
    "Panamá":               ["cod_prov",   "cod_distri", "cod_correg"],
    "Honduras":             ["cod_dep",    "cod_mun",    "cod_col"],
    "Republica Dominicana": ["cod_reg",    "cod_prov",   "cod_mun"],
    "Puerto Rico":          ["cod_mun"],
    "Costa Rica":           ["cod_prov",   "cod_canton", "cod_distri"],
}


def construir_indice(datos_capa, campos_capa, pais):
    """
    Construye {campo: set(valores_únicos)} para los campos geo-código del país.

    :param datos_capa : list of (fid, dict_valores)
    :param campos_capa: set de nombres de campo presentes en la capa
    :param pais       : str
    :returns          : dict {campo: {valor_str: [fids]}}
    """
    jerarquia   = JERARQUIA_PAIS.get(pais, [])
    campos_geo  = [c for c in jerarquia if c in campos_capa]
    indice      = {c: {} for c in campos_geo}

    for fid, d in datos_capa:
        for campo in campos_geo:
            val = d.get(campo)
            if val is None:
                continue
            # Conversión consciente del tipo: evitar str() para valores ya string
            val_str = val.strip() if isinstance(val, str) else str(val).strip()
            if val_str in ("", "NULL", "None"):
                continue
            if val_str not in indice[campo]:
                indice[campo][val_str] = []
            indice[campo][val_str].append(fid)

    return indice


def validar_cruce(nombre_capas_tgeom_indices, pais, capas_ref=None):
    """
    Valida que los geo-códigos de puntos/líneas existan en los polígonos.

    :param nombre_capas_tgeom_indices: list of (nombre, tipo_geom, indice)
          tipo_geom: "poligono" | "linea" | "punto"
          indice   : {campo: {valor: [fids]}}
    :param pais: str
    :param capas_ref: list of (nombre, indice) — polígonos de referencia externos
                      que no aparecen en el reporte pero sí en la comparación

    :returns: list of {
        "capa_origen"    : nombre de la capa con el valor problemático,
        "tipo_geom"      : tipo geométrico de la capa origen,
        "campo"          : campo geo-código con el problema,
        "valor"          : valor que no tiene correspondencia,
        "n_features"     : cantidad de features afectadas,
        "fids"           : lista de fids (máx 50 para no inflar memoria),
        "capas_referencia": lista de nombres de capas polígono que tienen ese campo,
        "tipo"           : "sin_capa_referencia" | "valor_huerfano",
        "mensaje"        : descripción legible,
    }
    """
    jerarquia = JERARQUIA_PAIS.get(pais, [])
    if not jerarquia:
        return []

    # Separar polígonos (referencia) de puntos/líneas (a validar)
    poligonos   = [(n, idx) for n, tg, idx in nombre_capas_tgeom_indices if tg == "poligono"]
    a_validar   = [(n, tg, idx) for n, tg, idx in nombre_capas_tgeom_indices if tg != "poligono"]

    # Agregar capas de referencia externas (no aparecen en reporte)
    if capas_ref:
        poligonos = list(poligonos) + list(capas_ref)

    if not a_validar:
        return []  # Solo hay polígonos, nada que validar

    # Construir referencia global por campo: {campo: set(valores en cualquier polígono)}
    ref_global  = {}  # campo → set de valores
    ref_nombres = {}  # campo → [nombres de capas polígono que lo tienen]
    for nombre_pol, idx_pol in poligonos:
        for campo, valores in idx_pol.items():
            if campo not in ref_global:
                ref_global[campo]  = set()
                ref_nombres[campo] = []
            ref_global[campo].update(valores.keys())
            ref_nombres[campo].append(nombre_pol)

    inconsistencias = []

    for nombre_capa, tipo_geom, indice in a_validar:
        tipo_label = "líneas" if tipo_geom == "linea" else "puntos"

        for campo in jerarquia:
            if campo not in indice:
                continue  # esta capa no tiene este campo

            valores_capa = indice[campo]

            # ── Caso 1: ningún polígono tiene este campo ───────────────────
            if campo not in ref_global:
                inconsistencias.append({
                    "capa_origen":     nombre_capa,
                    "tipo_geom":       tipo_label,
                    "campo":           campo,
                    "valor":           f"{len(valores_capa)} valores únicos",
                    "n_features":      sum(len(v) for v in valores_capa.values()),
                    "fids":            [],
                    "capas_referencia":[],
                    "tipo":            "sin_capa_referencia",
                    "mensaje":         (
                        f"La capa de {tipo_label} '{nombre_capa}' tiene '{campo}' "
                        f"pero ninguna capa de polígonos cargada tiene ese campo "
                        f"para usarla como referencia."
                    ),
                })
                continue

            # ── Caso 2: verificar que cada valor exista en los polígonos ───
            refs = ref_nombres[campo]
            refs_label = ", ".join(f"'{r}'" for r in refs)

            for val, fids in valores_capa.items():
                if val not in ref_global[campo]:
                    inconsistencias.append({
                        "capa_origen":     nombre_capa,
                        "tipo_geom":       tipo_label,
                        "campo":           campo,
                        "valor":           val,
                        "n_features":      len(fids),
                        "fids":            fids[:50],
                        "capas_referencia": refs,
                        "tipo":            "valor_huerfano",
                        "mensaje":         (
                            f"'{campo}' = '{val}' en capa de {tipo_label} '{nombre_capa}' "
                            f"no existe en {'la capa' if len(refs)==1 else 'las capas'} "
                            f"de polígonos {refs_label}."
                        ),
                    })

    return inconsistencias


def validar_cruce_espacial(capas_con_tipo, pais, callback=None, parar_fn=None, capas_ref=None):
    """
    Valida que los geo-códigos de puntos/líneas coincidan con los polígonos
    que los contienen espacialmente.

    capas_con_tipo : list of (nombre, tipo_geom, QgsVectorLayer)
                     tipo_geom: "poligono" | "linea" | "punto"
    callback(n, total) : progreso (llamado cada ~200 features)
    parar_fn()         : retorna True si el usuario canceló

    Para cada feature de punto/línea:
      - Localiza el polígono contenedor vía índice espacial
      - Verifica que cada campo geo-código coincida con el valor del polígono

    Retorna lista de inconsistencias con tipo:
      "inconsistencia_espacial"    — el código no coincide con el polígono contenedor
      "sin_poligono_contenedor"    — el feature no está dentro de ningún polígono
    """
    from qgis.core import QgsSpatialIndex, QgsWkbTypes, QgsFeatureRequest

    jerarquia = JERARQUIA_PAIS.get(pais, [])
    if not jerarquia:
        return []

    pols = [(n, c) for n, tg, c in capas_con_tipo if tg == "poligono"]
    vals = [(n, tg, c) for n, tg, c in capas_con_tipo if tg != "poligono"]

    # Agregar capas de referencia externas (solo para consulta espacial, no en reporte)
    if capas_ref:
        pols = list(pols) + [(n, c) for n, _tg, c in capas_ref]

    if not pols or not vals:
        return []

    # ── Pre-cargar polígonos (geometrías + atributos geo-código) ─────────────
    pol_data = {}
    for nom_pol, capa_pol in pols:
        campos_pol = {f.name() for f in capa_pol.fields()}
        campos_geo = [c for c in jerarquia if c in campos_pol]
        if not campos_geo:
            continue

        idx_pol    = QgsSpatialIndex()
        geoms_pol  = {}
        attrs_pol  = {}

        _pol_noms_idx = {n: i for i, n in enumerate(capa_pol.fields().names())}
        idx_campos    = [_pol_noms_idx[c] for c in campos_geo if c in _pol_noms_idx]
        req = QgsFeatureRequest().setSubsetOfAttributes(idx_campos)

        for feat in capa_pol.getFeatures(req):
            g = feat.geometry()
            if g.isNull() or not g.isGeosValid():
                continue
            idx_pol.addFeature(feat)
            geoms_pol[feat.id()] = g
            attrs_pol[feat.id()] = {
                c: str(feat[c]).strip()
                for c in campos_geo
                if feat[c] is not None
                and str(feat[c]).strip() not in ("", "NULL", "None")
            }

        pol_data[nom_pol] = (idx_pol, geoms_pol, attrs_pol, campos_geo)

    if not pol_data:
        return []

    # ── Validar capas de puntos y líneas ─────────────────────────────────────
    inconsistencias = []
    total_global    = sum(c.featureCount() for _, _, c in vals)
    n_global        = 0

    for nom_val, tg_val, capa_val in vals:
        if parar_fn and parar_fn():
            break

        campos_val = {f.name() for f in capa_val.fields()}
        campos_geo = [c for c in jerarquia if c in campos_val]
        if not campos_geo:
            continue

        es_linea   = (tg_val == "linea")
        tipo_label = "líneas" if es_linea else "puntos"

        # Solo leer los campos geo-código (+ geometría)
        _val_noms_idx  = {n: i for i, n in enumerate(capa_val.fields().names())}
        idx_campos_val = [_val_noms_idx[c] for c in campos_geo if c in _val_noms_idx]

        # Acumular errores: key → {n, fids}
        acum = {}

        for feat in capa_val.getFeatures(QgsFeatureRequest().setSubsetOfAttributes(idx_campos_val)):
            if parar_fn and parar_fn():
                break
            n_global += 1
            if callback and n_global % 200 == 0:
                callback(n_global, max(1, total_global))

            g   = feat.geometry()
            fid = feat.id()
            if g.isNull():
                continue

            # Punto de referencia: centroide para líneas, geometría directa para puntos
            ref = g.centroid() if es_linea else g
            if ref.isNull():
                continue

            # Valores geo-código del feature
            vals_feat = {}
            for c in campos_geo:
                v = feat[c]
                if v is None:
                    continue
                vs = str(v).strip()
                if vs and vs not in ("NULL", "None"):
                    vals_feat[c] = vs

            if not vals_feat:
                continue

            for nom_pol, (idx_pol, geoms_pol, attrs_pol_d, campos_pol_geo) in pol_data.items():
                campos_comunes = [c for c in campos_geo
                                  if c in campos_pol_geo and c in vals_feat]
                if not campos_comunes:
                    continue

                # Buscar TODOS los polígonos que contengan el centroide
                cfids        = idx_pol.intersects(ref.boundingBox())
                contenedores = [cfid for cfid in cfids
                                if geoms_pol[cfid].contains(ref)]

                if not contenedores:
                    continue  # sin polígono contenedor → no es error

                # Para cada campo, verificar si el código coincide con
                # AL MENOS UNO de los polígonos contenedores.
                # Solo es error si ninguno coincide.
                for campo in campos_comunes:
                    val_f     = vals_feat[campo]
                    vals_pols = [attrs_pol_d.get(cfid, {}).get(campo, "")
                                 for cfid in contenedores]
                    vals_validos = [v for v in vals_pols if v]
                    if not vals_validos:
                        continue  # ningún polígono tiene este campo — no validar
                    if val_f not in vals_validos:
                        val_esperado = ", ".join(sorted(set(vals_validos)))
                        key = (nom_val, tipo_label, campo, nom_pol,
                               "inconsistencia_espacial")
                        _acum_add(acum, key, fid, val_f, val_esperado)

        # Convertir acumulado → lista de inconsistencias
        # Clave: (capa, tipo_geom, campo, pol_ref, tipo) → una fila por grupo
        for (n_val, tg_label, campo, nom_pol, tipo), dat in acum.items():
            n = dat["n"]
            if tipo == "inconsistencia_espacial":
                msg = (
                    f"{n:,} feature(s) de '{n_val}' tienen '{campo}' que no coincide "
                    f"con el polígono contenedor en '{nom_pol}'."
                )
            else:
                msg = (
                    f"{n:,} feature(s) de '{n_val}' no están dentro de ningún "
                    f"polígono en '{nom_pol}'."
                )
            inconsistencias.append({
                "capa_origen":     n_val,
                "tipo_geom":       tg_label,
                "campo":           campo,
                "n_features":      n,
                "items":           dat["items"],   # [(fid, val_actual, val_esperado)]
                "capas_referencia": [nom_pol],
                "tipo":            tipo,
                "mensaje":         msg,
                # Campos legacy para compatibilidad con tablas de atributos
                "valor":           f"{n:,} features",
                "valor_esperado":  "",
            })

    if callback:
        callback(total_global, total_global)
    return inconsistencias


_MAX_ITEMS_POR_GRUPO = 10_000  # protege RAM en datasets grandes; el contador total es exacto


def validar_cruce_placa_mavvial(capas_stats):
    """
    Valida la relación placa (puntos) ↔ mavvial (líneas):
      - placa.id_mavvial debe existir como id_capa en mavvial
      - Cuando existe match, tipovia / nomvia / nomvtotal / generadora deben coincidir

    capas_stats : list of {"nombre", "tipo_geom", "capa" (QgsVectorLayer), ...}

    Retorna inconsistencias en el mismo formato que validar_cruce_espacial.
    """
    CAMPOS_CRUCE = ["tipovia", "nomvia", "nomvtotal", "generadora"]

    placa_cs   = next((cs for cs in capas_stats
                       if "placa"   in cs["nombre"].lower() and cs["tipo_geom"] == "punto"),  None)
    mavvial_cs = next((cs for cs in capas_stats
                       if "mavvial" in cs["nombre"].lower() and cs["tipo_geom"] == "linea"), None)

    if not placa_cs or not mavvial_cs:
        return []

    placa_capa   = placa_cs["capa"]
    mavvial_capa = mavvial_cs["capa"]

    placa_campos   = {f.name() for f in placa_capa.fields()}
    mavvial_campos = {f.name() for f in mavvial_capa.fields()}

    if "id_mavvial" not in placa_campos or "id_capa" not in mavvial_campos:
        return []

    # Solo comparar los campos que existen en ambas capas
    campos_activos = [c for c in CAMPOS_CRUCE
                      if c in placa_campos and c in mavvial_campos]

    def _val(feat, campo):
        """Retorna valor normalizado o None si vacío/NULL."""
        v = feat[campo]
        if v is None:
            return None
        s = str(v).strip()
        return None if s in ("", "NULL", "None") else s

    # ── Índice mavvial: id_capa → {campo: valor_str|None} ──────────────────────
    from qgis.core import QgsFeatureRequest
    _req_no_geom = QgsFeatureRequest().setFlags(QgsFeatureRequest.NoGeometry)

    mavvial_idx = {}
    for feat in mavvial_capa.getFeatures(_req_no_geom):
        raw = _val(feat, "id_capa")
        if raw is None:
            continue
        mavvial_idx[raw] = {c: _val(feat, c) for c in campos_activos}

    # ── Recorrer placa y acumular errores ───────────────────────────────────────
    acum = {}

    for feat in placa_capa.getFeatures(_req_no_geom):
        id_mav = _val(feat, "id_mavvial")
        if id_mav is None:
            continue
        fid = feat.id()

        if id_mav not in mavvial_idx:
            key = (placa_cs["nombre"], "puntos", "id_mavvial",
                   mavvial_cs["nombre"], "id_mavvial_huerfano")
            _acum_add(acum, key, fid, id_mav, "—")
            continue

        mav_vals = mavvial_idx[id_mav]
        for campo in campos_activos:
            vp = _val(feat, campo)
            vm = mav_vals.get(campo)
            # Comparar en mayúsculas; None vs valor también es diferencia
            vp_norm = vp.upper() if vp else None
            vm_norm = vm.upper() if vm else None
            if vp_norm != vm_norm:
                key = (placa_cs["nombre"], "puntos", campo,
                       mavvial_cs["nombre"], "cruce_placa_mavvial")
                _acum_add(acum, key, fid, vp or "(vacío)", vm or "(vacío)")

    # ── Convertir acumulado → lista de inconsistencias ─────────────────────────
    inconsistencias = []
    for (nom_orig, tg_label, campo, nom_ref, tipo), dat in acum.items():
        n = dat["n"]
        if tipo == "id_mavvial_huerfano":
            msg = (f"{n:,} feature(s) de '{nom_orig}' tienen id_mavvial "
                   f"que no existe en '{nom_ref}' (id_capa).")
        else:
            msg = (f"{n:,} feature(s) de '{nom_orig}' tienen '{campo}' "
                   f"que no coincide con '{nom_ref}' para el mismo id_mavvial.")
        inconsistencias.append({
            "capa_origen":      nom_orig,
            "tipo_geom":        tg_label,
            "campo":            campo,
            "n_features":       n,
            "items":            dat["items"],
            "capas_referencia": [nom_ref],
            "tipo":             tipo,
            "mensaje":          msg,
            "valor":            f"{n:,} features",
            "valor_esperado":   "",
        })

    return inconsistencias


def _acum_add(acum, key, fid, val_actual="", val_esperado=""):
    """
    Acumula errores por clave (capa, campo, polígono_ref, tipo).
    Guarda hasta _MAX_ITEMS_POR_GRUPO items para CSV/QGIS; el contador total es exacto.
    """
    if key not in acum:
        acum[key] = {"n": 0, "items": []}
    acum[key]["n"] += 1
    if len(acum[key]["items"]) < _MAX_ITEMS_POR_GRUPO:
        acum[key]["items"].append((fid, val_actual, val_esperado))
