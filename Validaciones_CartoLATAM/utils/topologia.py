"""
topologia.py
------------
Validaciones topológicas para capas QGIS.
Corre en el hilo principal: llama a callback(avance, total) frecuentemente
para que el llamador pueda invocar QApplication.processEvents() y mantener
la UI responsiva.

Funciones públicas:
    validar_poligonos(capa, callback, parar_fn)
    validar_lineas(capa, capa_manzana, callback, parar_fn)
    validar_puntos_placa(capa, capa_manzana, callback, parar_fn)

Parámetros comunes:
    callback(avance: int, total: int)   — llamado cada ~50 operaciones
    parar_fn() -> bool                  — retorna True si el usuario canceló
"""

from collections import defaultdict

from qgis.core import QgsGeometry, QgsSpatialIndex, QgsWkbTypes

# Capas con más features que este umbral omiten la detección de huecos
# (QgsGeometry.unaryUnion sobre miles de polígonos puede congelar QGIS).
_MAX_FEATURES_UNION = 300

# Máximo de pares a comparar en detección de superposiciones / duplicados.
# Evita que capas con muchas coincidencias espaciales bloqueen la UI.
_MAX_PARES = 50_000


# Proveedores que producen geometrías siempre válidas — isGeosValid() es innecesario
_PROVEEDORES_CONFIABLES = frozenset({"ogr", "memory", "spatialite", "gpkg"})


# ── Helpers internos ──────────────────────────────────────────────────────────

def _cargar_geometrias(capa, callback=None, parar_fn=None):
    """
    Lee todas las geometrías de la capa.
    Retorna (geoms, QgsSpatialIndex, errores_invalidos).
    Para proveedores OGR/memory se omite isGeosValid() (siempre producen geoms válidas).
    """
    verificar_geos = capa.providerType().lower() not in _PROVEEDORES_CONFIABLES
    geoms    = {}
    indice   = QgsSpatialIndex()
    invalidos = []
    total    = capa.featureCount()
    for i, feat in enumerate(capa.getFeatures()):
        if parar_fn and parar_fn():
            break
        if callback and i % 50 == 0:
            callback(i, total)
        fid = feat.id()
        g   = feat.geometry()
        if g.isNull():
            invalidos.append({"fid": fid, "regla": "geometria_invalida",
                              "descripcion": "Geometría nula"})
        elif verificar_geos and not g.isGeosValid():
            msg = g.lastError() or "—"
            invalidos.append({"fid": fid, "regla": "geometria_invalida",
                              "descripcion": f"Geometría inválida (GEOS): {msg}"})
        else:
            geoms[fid] = g
            indice.addFeature(feat)
    return geoms, indice, invalidos


def _detectar_duplicados(geoms, clave_fn, nombre_capa, callback=None, parar_fn=None):
    """Detecta geometrías idénticas agrupando por área o longitud."""
    errores = []
    grupos = defaultdict(list)
    for fid, g in geoms.items():
        grupos[round(clave_fn(g), 4)].append(fid)

    reportados = set()
    n = 0
    for fids in grupos.values():
        if len(fids) < 2:
            continue
        for i, fa in enumerate(fids):
            for fb in fids[i + 1:]:
                if parar_fn and parar_fn():
                    return errores
                n += 1
                if n > _MAX_PARES:
                    return errores
                if callback and n % 50 == 0:
                    callback(n, _MAX_PARES)
                if (fa, fb) in reportados:
                    continue
                if geoms[fa].equals(geoms[fb]):
                    errores.append({"fid": fa, "regla": "duplicado",
                                   "descripcion": f"Geometría idéntica a FID {fb} (misma capa: {nombre_capa})"})
                    reportados.add((fa, fb))
    return errores


def _detectar_superposicion_pares(geoms, indice, tipo_esperado, nombre_capa,
                                   callback=None, parar_fn=None):
    """
    Compara pares candidatos vía índice espacial.
    tipo_esperado: None (polígonos — usa área) o QgsWkbTypes.LineGeometry (líneas).
    nombre_capa: nombre de la capa, se incluye en el mensaje de error.
    """
    errores = []
    pares = set()
    n = 0
    for fid, g in geoms.items():
        if parar_fn and parar_fn():
            break
        for cfid in indice.intersects(g.boundingBox()):
            if cfid == fid:
                continue
            par = (min(fid, cfid), max(fid, cfid))
            if par in pares:
                continue
            pares.add(par)
            n += 1
            if n > _MAX_PARES:
                return errores
            if callback and n % 50 == 0:
                callback(n, _MAX_PARES)
            if parar_fn and parar_fn():
                return errores

            inter = g.intersection(geoms[cfid])
            if inter.isNull():
                continue
            if tipo_esperado is None:
                if inter.area() > 1e-6:
                    errores.append({
                        "fid": fid, "regla": "superposicion",
                        "descripcion": f"Se superpone con FID {cfid} (misma capa: {nombre_capa})",
                    })
            else:
                t = QgsWkbTypes.geometryType(inter.wkbType())
                if t == tipo_esperado:
                    errores.append({
                        "fid": fid, "regla": "superposicion",
                        "descripcion": f"Segmento superpuesto con FID {cfid} (misma capa: {nombre_capa})",
                    })
    return errores


# ── API para ejecución en hilos (geometrías pre-cargadas) ─────────────────────

def _construir_indice(geoms):
    """Construye QgsSpatialIndex a partir de un dict {fid: QgsGeometry}."""
    from qgis.core import QgsFeature as _QF
    idx = QgsSpatialIndex()
    for fid, g in geoms.items():
        f = _QF()
        f.setId(fid)
        f.setGeometry(g)
        idx.addFeature(f)
    return idx


def precargar_manzana(capa_manzana):
    """Lee geometrías de la capa manzana de una vez en el hilo principal."""
    if capa_manzana is None:
        return {}, None
    manz_dict, idx_manz, _ = _cargar_geometrias(capa_manzana)
    return manz_dict, idx_manz


def validar_poligonos_desde_geoms(geoms, invalidos, nombre_capa,
                                   parar_fn=None, callback=None):
    """
    Valida topología de polígonos sobre un dict de geometrías ya cargadas.
    Apto para ejecutarse en un hilo (GEOS libera el GIL).
    invalidos : errores de geometría detectados durante la lectura de geometrías.
    callback(done, total) : llamado periódicamente para actualizar barra de progreso.
    """
    total   = len(geoms)
    errores = list(invalidos)
    if callback: callback(0, total)
    if parar_fn and parar_fn():
        return errores

    indice = _construir_indice(geoms)
    errores.extend(_detectar_duplicados(geoms, lambda g: g.area(), nombre_capa,
                                        callback=callback, parar_fn=parar_fn))
    if parar_fn and parar_fn():
        return errores

    errores.extend(_detectar_superposicion_pares(geoms, indice, None, nombre_capa,
                                                  callback=callback, parar_fn=parar_fn))

    if not (parar_fn and parar_fn()) and 1 < len(geoms) <= _MAX_FEATURES_UNION:
        try:
            union = QgsGeometry.unaryUnion(list(geoms.values()))
            if not union.isNull():
                polys = (union.asMultiPolygon()
                         if union.isMultipart() else [union.asPolygon()])
                n_huecos = sum(len(anillos) - 1 for anillos in polys if anillos)
                if n_huecos > 0:
                    errores.append({"fid": -1, "regla": "hueco",
                                   "descripcion": f"{n_huecos} hueco(s) en la unión de la capa"})
        except Exception:
            pass

    if callback: callback(total, total)
    return errores


def validar_lineas_desde_geoms(geoms, invalidos, nombre_capa,
                               manz_dict=None, idx_manz=None, nombre_manzana="",
                               parar_fn=None, callback=None):
    """Valida topología de líneas sobre un dict de geometrías ya cargadas."""
    total   = len(geoms)
    errores = list(invalidos)
    if callback: callback(0, total)
    if parar_fn and parar_fn():
        return errores

    errores.extend(_detectar_duplicados(geoms, lambda g: g.length(), nombre_capa,
                                        callback=callback, parar_fn=parar_fn))
    if parar_fn and parar_fn():
        return errores

    if manz_dict and idx_manz:
        for n, (fid, g) in enumerate(geoms.items()):
            if parar_fn and parar_fn():
                break
            if callback and n % 50 == 0:
                callback(n, total)
            for mfid in idx_manz.intersects(g.boundingBox()):
                mg = manz_dict.get(mfid)
                if mg is None:
                    continue
                if g.crosses(mg):
                    errores.append({
                        "fid": fid, "regla": "cruza_manzana",
                        "descripcion": (
                            f"La línea atraviesa '{nombre_manzana}' — FID manzana {mfid}"
                        ),
                    })
                    break

    if callback: callback(total, total)
    return errores


def validar_puntos_desde_geoms(geoms, invalidos, nombre_capa,
                               manz_dict=None, idx_manz=None, nombre_manzana="",
                               parar_fn=None, callback=None):
    """Valida topología de puntos sobre un dict de geometrías ya cargadas."""
    total   = len(geoms)
    errores = list(invalidos)
    if callback: callback(0, total)
    if parar_fn and parar_fn():
        return errores

    if not manz_dict or not idx_manz:
        if callback: callback(total, total)
        return errores

    for n, (fid, g) in enumerate(geoms.items()):
        if parar_fn and parar_fn():
            break
        if callback and n % 50 == 0:
            callback(n, total)
        contenedora = None
        for mfid in idx_manz.intersects(g.boundingBox()):
            mg = manz_dict.get(mfid)
            if mg and mg.contains(g):
                contenedora = mg
                break

        if contenedora is None:
            errores.append({
                "fid": fid, "regla": "fuera_manzana",
                "descripcion": (
                    f"El punto no está dentro de ninguna manzana (capa: '{nombre_manzana}')"
                ),
            })
            continue

        interior = contenedora.buffer(-3.0, 5)
        if not interior.isNull() and not interior.isEmpty():
            franja = contenedora.difference(interior)
            if not franja.isNull() and not franja.contains(g):
                errores.append({
                    "fid": fid, "regla": "fuera_franja_3m",
                    "descripcion": (
                        f"El punto no está en la franja de 3 m del borde"
                        f" (capa manzana: '{nombre_manzana}')"
                    ),
                })

    if callback: callback(total, total)
    return errores


# ── Validadores públicos (leen la capa directamente) ──────────────────────────

def validar_poligonos(capa, callback=None, parar_fn=None):
    """
    Reglas:
      geometria_invalida · duplicado · superposicion · hueco
    Los huecos solo se calculan si la capa tiene ≤ 300 features.
    """
    errores = []
    total = capa.featureCount()

    geoms, indice, err_geom = _cargar_geometrias(capa, callback, parar_fn)
    errores.extend(err_geom)

    nombre_capa = capa.name()

    if parar_fn and parar_fn():
        return errores

    errores.extend(_detectar_duplicados(geoms, lambda g: g.area(),
                                        nombre_capa, callback, parar_fn))

    if parar_fn and parar_fn():
        return errores

    errores.extend(_detectar_superposicion_pares(
        geoms, indice,
        tipo_esperado=None,
        nombre_capa=nombre_capa,
        callback=callback, parar_fn=parar_fn,
    ))

    # Huecos — solo para capas pequeñas (unaryUnion es muy lento en capas grandes)
    if not (parar_fn and parar_fn()) and 1 < len(geoms) <= _MAX_FEATURES_UNION:
        try:
            union = QgsGeometry.unaryUnion(list(geoms.values()))
            if not union.isNull():
                polys = (union.asMultiPolygon()
                         if union.isMultipart() else [union.asPolygon()])
                n_huecos = sum(len(anillos) - 1 for anillos in polys if anillos)
                if n_huecos > 0:
                    errores.append({"fid": -1, "regla": "hueco",
                                   "descripcion": f"{n_huecos} hueco(s) en la unión de la capa"})
        except Exception:
            pass

    if callback:
        callback(total, total)
    return errores


def validar_lineas(capa, capa_manzana=None, callback=None, parar_fn=None):
    """
    Reglas:
      geometria_invalida · duplicado · cruza_manzana
    (La superposición entre líneas de la misma capa está descartada
    porque en redes viales los segmentos compartidos son válidos.)
    """
    errores = []
    total = capa.featureCount()

    geoms, _, err_geom = _cargar_geometrias(capa, callback, parar_fn)
    errores.extend(err_geom)

    nombre_capa = capa.name()
    nombre_manzana = capa_manzana.name() if capa_manzana else ""

    if parar_fn and parar_fn():
        return errores

    errores.extend(_detectar_duplicados(geoms, lambda g: g.length(),
                                        nombre_capa, callback, parar_fn))

    if parar_fn and parar_fn():
        return errores

    # Cruce con manzanas
    if capa_manzana and not (parar_fn and parar_fn()):
        manz_dict = {}
        idx_manz = QgsSpatialIndex()
        for mfeat in capa_manzana.getFeatures():
            mg = mfeat.geometry()
            if not mg.isNull() and mg.isGeosValid():
                manz_dict[mfeat.id()] = mg
                idx_manz.addFeature(mfeat)

        n = 0
        for fid, g in geoms.items():
            if parar_fn and parar_fn():
                break
            n += 1
            if callback and n % 50 == 0:
                callback(n, total)
            for mfid in idx_manz.intersects(g.boundingBox()):
                mg = manz_dict.get(mfid)
                if mg is None:
                    continue
                # crosses() = True solo cuando la línea entra al interior del
                # polígono; no se activa si la línea corre sobre el borde.
                if g.crosses(mg):
                    errores.append({
                        "fid": fid, "regla": "cruza_manzana",
                        "descripcion": (
                            f"La línea atraviesa '{nombre_manzana}' — FID manzana {mfid}"
                        ),
                    })
                    break

    if callback:
        callback(total, total)
    return errores


def validar_puntos_placa(capa, capa_manzana=None, callback=None, parar_fn=None):
    """
    Reglas:
      geometria_invalida · fuera_manzana · fuera_franja_3m
    La franja de 3 m asume CRS en metros.
    """
    errores = []
    total = capa.featureCount()
    nombre_manzana = capa_manzana.name() if capa_manzana else ""

    manz_dict = {}
    idx_manz = None
    if capa_manzana:
        idx_manz = QgsSpatialIndex()
        for mfeat in capa_manzana.getFeatures():
            mg = mfeat.geometry()
            if not mg.isNull() and mg.isGeosValid():
                manz_dict[mfeat.id()] = mg
                idx_manz.addFeature(mfeat)

    for i, feat in enumerate(capa.getFeatures()):
        if parar_fn and parar_fn():
            break
        if callback and i % 50 == 0:
            callback(i, total)

        fid = feat.id()
        g = feat.geometry()

        if g.isNull():
            errores.append({"fid": fid, "regla": "geometria_invalida",
                           "descripcion": "Geometría nula"})
            continue
        if not g.isGeosValid():
            errores.append({"fid": fid, "regla": "geometria_invalida",
                           "descripcion": "Geometría inválida (GEOS)"})
            continue

        if not capa_manzana or idx_manz is None:
            continue

        contenedora = None
        for mfid in idx_manz.intersects(g.boundingBox()):
            mg = manz_dict.get(mfid)
            if mg and mg.contains(g):
                contenedora = mg
                break

        if contenedora is None:
            errores.append({
                "fid": fid, "regla": "fuera_manzana",
                "descripcion": f"El punto no está dentro de ninguna manzana (capa: '{nombre_manzana}')",
            })
            continue

        interior = contenedora.buffer(-3.0, 5)
        if not interior.isNull() and not interior.isEmpty():
            franja = contenedora.difference(interior)
            if not franja.isNull() and not franja.contains(g):
                errores.append({
                    "fid": fid, "regla": "fuera_franja_3m",
                    "descripcion": (
                        f"El punto no está en la franja de 3 m del borde"
                        f" (capa manzana: '{nombre_manzana}')"
                    ),
                })

    if callback:
        callback(total, total)
    return errores
