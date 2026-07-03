"""
Paquete de validaciones (utils) para campos de capas QGIS.

Cada módulo de campo expone una función `validar(valor, ...)` que retorna
una lista de mensajes de error. Lista vacía = campo válido.

Módulos de infraestructura (no son campos):
    config       — constantes y helpers compartidos
    _generales   — validaciones reutilizables
    _worker      — procesamiento paralelo (multiprocessing)
    geo_codigos  — validación de jerarquías geográficas por país
    sheets_loader — carga de catálogos desde Google Sheets
    gmail_sender  — envío de correos (SMTP / Gmail API)
    cruce_capas  — validación cruzada entre capas
    reporte_html — generación de reporte HTML + CSVs

Uso:
    from utils import id_capa, tipovia, nomvia
    errores = tipovia.validar("AV", pais="Brasil", abreviaturas={"AV", "RUA"})
"""

from . import (
    # ── Infraestructura ───────────────────────────────────────────────────────
    _generales,
    geo_codigos,
    sheets_loader,
    gmail_sender,
    cruce_capas,
    reporte_html,
    # NOTA: topologia NO se importa aquí porque usa qgis.core, que no está
    # disponible en los workers de multiprocessing. Se importa directamente
    # desde dialogo_principal cuando hace falta.

    # ── Campos de vías ────────────────────────────────────────────────────────
    id_capa,
    tipovia,
    tipo_urb,
    nomvia,
    nomvtotal,
    nomcomun,
    generadora,
    costado,
    rango_par,
    rango_imp,
    oneway,
    velocidad,
    marca_vial,
    id_mavvial,
    placa,
    cep,

    # ── Códigos geográficos ───────────────────────────────────────────────────
    cod_estado,
    nom_estado,
    cod_mun,
    nom_mun,
    cod_distri,
    nom_distri,
    cod_bar,
    nom_bar,

    # ── Campos de actualización ───────────────────────────────────────────────
    marca,
    fecha,
    version,

    # ── Campos de sitios / POI ────────────────────────────────────────────────
    categoria,
    nom_subcat,
    direccion,
    manzana,
    casa_lote,
    nom_urb,
)

__all__ = [
    # Infraestructura
    "_generales", "geo_codigos", "sheets_loader", "gmail_sender",
    "cruce_capas", "reporte_html",
    # Vías
    "id_capa", "tipovia", "tipo_urb", "nomvia", "nomvtotal", "nomcomun",
    "generadora", "costado", "rango_par", "rango_imp",
    "oneway", "velocidad", "marca_vial", "id_mavvial", "placa", "cep",
    # Geocódigos
    "cod_estado", "nom_estado", "cod_mun", "nom_mun",
    "cod_distri", "nom_distri", "cod_bar", "nom_bar",
    # Actualización
    "marca", "fecha", "version",
    # Sitios / POI
    "categoria", "nom_subcat", "direccion", "manzana", "casa_lote", "nom_urb",
]
