"""
_worker.py
----------
Función de trabajo para procesamiento paralelo de validaciones.

NO importa nada de QGIS — se ejecuta en procesos hijos
que arrancan sin QGIS (multiprocessing spawn en Windows).

Recibe chunks de datos Python puros y retorna listas de errores.
"""


def validar_chunk(args):
    """
    Valida un chunk de features y retorna los resultados.

    Parámetros (tupla para compatibilidad con Pool.imap):
        chunk                : list of (fid, dict_valores)
        campos               : set de nombres de campo presentes en la capa
        flags                : (es_linea, es_punto, es_poligono)
        contador_ids         : collections.Counter {id_capa: frecuencia}
        abreviaturas_tipovia : set de abreviaturas VIA válidas
        estandarizacion      : dict {ABREVIATURA: NOMVTOTAL}
        abreviaturas_urb     : set de abreviaturas URB válidas
        categorias_validas   : dict {CATEGORIA: set(SUBCATEGORIAS)}
        pais                 : str nombre del país
        ruta_utils           : str ruta absoluta a la carpeta que contiene utils/

    Retorna:
        list of (fid, dict_valores, dict_errores)
    """
    (chunk, campos, flags, contador_ids,
     abreviaturas_tipovia, estandarizacion_tipovia,
     abreviaturas_urb, categorias_validas, pais, ruta_utils) = args

    import sys, os

    # Normalizar ruta_utils para que la comparación funcione en Windows
    # independientemente del estilo de separadores (\ vs /).
    _ruta_norm = os.path.normcase(os.path.normpath(ruta_utils))

    # Eliminar cualquier 'utils' incorrecto que el spawner haya importado
    # antes de que pudiéramos fijar sys.path (pasa cuando otro plugin ocupa
    # la posición 0 con su propio paquete 'utils').
    for _k in list(sys.modules.keys()):
        if _k == "utils" or _k.startswith("utils."):
            _mod_file = getattr(sys.modules[_k], "__file__", None) or ""
            if _ruta_norm not in os.path.normcase(os.path.normpath(_mod_file)):
                del sys.modules[_k]

    # Asegurar que ruta_utils quede en la primera posición del path
    # (comparación normalizada para manejar \ vs / en Windows).
    sys.path = [p for p in sys.path
                if os.path.normcase(os.path.normpath(p)) != _ruta_norm]
    sys.path.insert(0, ruta_utils)

    # Constantes y helpers desde config (fuente única de verdad)
    from utils.config import CAMPOS_OPCIONALES_LINEAS, es_vacio

    from utils import (
        id_capa     as mod_id_capa,
        tipo_dir    as mod_tipo_dir,
        tipovia     as mod_tipovia,
        tipo_urb    as mod_tipo_urb,
        nomvia      as mod_nomvia,
        nomvtotal   as mod_nomvtotal,
        nomcomun    as mod_nomcomun,
        generadora  as mod_generadora,
        costado     as mod_costado,
        rango_par   as mod_rango_par,
        rango_imp   as mod_rango_imp,
        oneway      as mod_oneway,
        velocidad   as mod_velocidad,
        marca_vial  as mod_marca_vial,
        marca       as mod_marca,
        fecha       as mod_fecha,
        version     as mod_version,
        placa       as mod_placa,
        cep         as mod_cep,
        id_mavvial  as mod_id_mavvial,
        geo_codigos as mod_geo_codigos,
        manzana     as mod_manzana,
        casa_lote   as mod_casa_lote,
        nom_urb     as mod_nom_urb,
        direccion   as mod_direccion,
        categoria   as mod_categoria,
        nom_subcat  as mod_nom_subcat,
    )

    es_linea, es_punto, _ = flags   # es_poligono no se usa en validaciones de atributos

    # Pre-computar reglas geográficas y filtrarlas a los campos de esta capa (1 vez por chunk)
    from utils.geo_codigos import obtener_reglas as _obtener_reglas
    _reglas_geo = _obtener_reglas(pais)
    # Solo las reglas cuyos campos están presentes en la capa — elimina el filtro por feature
    _reglas_geo = {c: r for c, r in _reglas_geo.items() if c in campos}

    def _validar_fila(d):
        err = {}

        def reg(campo, lista):
            if lista:
                err.setdefault(campo, []).extend(lista)

        def v(c):    return d.get(c)
        def ok(c):   return c in campos
        def skip(c): return es_linea and c in CAMPOS_OPCIONALES_LINEAS and es_vacio(v(c))

        if ok("id_capa"):
            reg("id_capa", mod_id_capa.validar(v("id_capa"), contador_ids=contador_ids))

        if ok("tipo_dir"):
            reg("tipo_dir", mod_tipo_dir.validar(v("tipo_dir"), pais=pais))

        if ok("tipovia"):
            reg("tipovia", mod_tipovia.validar(
                v("tipovia"), nomvia=v("nomvia"), nomvtotal=v("nomvtotal"),
                pais=pais, abreviaturas=abreviaturas_tipovia,
                tipo_dir=v("tipo_dir"),
            ))
        if ok("tipo_urb"):
            reg("tipo_urb", mod_tipo_urb.validar(
                v("tipo_urb"), pais=pais, abreviaturas_urb=abreviaturas_urb,
            ))
        if ok("nomvia"):
            reg("nomvia", mod_nomvia.validar(
                v("nomvia"), tipovia=v("tipovia"), nomvtotal=v("nomvtotal"),
                pais=pais, tipo_dir=v("tipo_dir"),
            ))
        if ok("nomvtotal"):
            nvt_errs = mod_nomvtotal.validar(
                v("nomvtotal"), tipovia=v("tipovia"), nomvia=v("nomvia"),
                estandarizacion=estandarizacion_tipovia, pais=pais,
                tipo_dir=v("tipo_dir"),
            )
            reg("nomvtotal", [e for e in nvt_errs
                              if "tipovia también debe" not in e
                              and "nomvia también debe"  not in e
                              and "nomvtotal debe tener" not in e])
        if ok("nomcomun"):
            reg("nomcomun", mod_nomcomun.validar(v("nomcomun")))

        if ok("generadora") and not skip("generadora"):
            reg("generadora", mod_generadora.validar(
                v("generadora"), tipo_dir=v("tipo_dir"), pais=pais,
            ))
        if ok("costado") and not skip("costado"):
            reg("costado", mod_costado.validar(v("costado"), es_punto=es_punto))
        if ok("rango_par") and not skip("rango_par"):
            reg("rango_par", mod_rango_par.validar(v("rango_par")))
        if ok("rango_imp") and not skip("rango_imp"):
            reg("rango_imp", mod_rango_imp.validar(v("rango_imp")))
        if ok("placa"):
            reg("placa", mod_placa.validar(v("placa")))

        if ok("oneway"):     reg("oneway",     mod_oneway.validar(v("oneway")))
        if ok("velocidad"):  reg("velocidad",  mod_velocidad.validar(v("velocidad")))
        if ok("marca_vial"): reg("marca_vial", mod_marca_vial.validar(v("marca_vial")))

        for campo_geo, msgs_geo in mod_geo_codigos.validar_geo_codigos(
                d, campos, pais, reglas=_reglas_geo).items():
            reg(campo_geo, msgs_geo)

        if ok("cep") and not skip("cep"):
            reg("cep", mod_cep.validar(v("cep")))
        if ok("id_mavvial"):
            reg("id_mavvial", mod_id_mavvial.validar(v("id_mavvial")))

        if ok("marca"):   reg("marca",   mod_marca.validar(v("marca"),   fecha=v("fecha"),  version=v("version")))
        if ok("fecha"):   reg("fecha",   mod_fecha.validar(v("fecha"),   marca=v("marca"),  version=v("version")))
        if ok("version"): reg("version", mod_version.validar(v("version"), fecha=v("fecha"), marca=v("marca")))

        # Campos opcionales nuevos
        if ok("manzana"):   reg("manzana",   mod_manzana.validar(v("manzana")))
        if ok("casa_lote"): reg("casa_lote", mod_casa_lote.validar(v("casa_lote")))
        if ok("nom_urb"):   reg("nom_urb",   mod_nom_urb.validar(v("nom_urb"), pais=pais))

        # Categoría y subcategoría (POI) — validadas contra catálogo de Sheets
        if ok("categoria"):  reg("categoria",  mod_categoria.validar(
            v("categoria"), categorias_validas=categorias_validas, pais=pais))
        if ok("nom_subcat"): reg("nom_subcat", mod_nom_subcat.validar(
            v("nom_subcat"), categoria=v("categoria"),
            categorias_validas=categorias_validas, pais=pais))

        # Dirección: validación cruzada con todos los valores de la fila
        if ok("direccion"): reg("direccion", mod_direccion.validar(v("direccion"), d=d, pais=pais))

        return err

    resultados = []
    for fid, d in chunk:
        try:
            resultados.append((fid, d, _validar_fila(d)))
        except Exception as exc:
            resultados.append((fid, d, {"_worker": [f"Error interno: {exc}"]}))
    return resultados
