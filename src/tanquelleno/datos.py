"""
===============================================================================
PROYECTO: TanqueLleno AI — Fase M (Modelado)
ARCHIVO:  src/tanquelleno/datos.py
DESCRIPCIÓN:
    Capa única de carga y saneamiento de datos. Todo script del proyecto lee
    a través de estas funciones para que los filtros de calidad declarados en
    la Fase R (rango S/ 5 – S/ 30, normalización de familias, resolución de la
    transición regulatoria de 2023) se apliquen siempre de la misma manera.
===============================================================================
"""

from __future__ import annotations

import io
import os
import re

import numpy as np
import pandas as pd

from . import config

# El scraper de Lima/Callao hace append de cada snapshot sin escribir el salto
# de línea final, por lo que la última fila de un snapshot queda concatenada con
# la primera del siguiente: ..."26.99""2026-09-16T22:06:15-0500","158833",...
# Este patrón detecta la frontera: comilla de cierre seguida de un timestamp ISO.
_PATRON_FILAS_PEGADAS = re.compile(r'"(?="20\d\d-\d\d-\d\dT)')


# -----------------------------------------------------------------------------
# 1. SERIE MENSUAL DEPARTAMENTAL (fuente del modelo A2)
# -----------------------------------------------------------------------------
def cargar_serie_mensual(familia: str = "REGULAR") -> pd.DataFrame:
    """Devuelve el panel departamento x mes de una familia de combustible.

    Normaliza la nomenclatura de Osinergmin a familias continuas, lo que resuelve
    la transición regulatoria de 2023 (H6) sin dejar huecos en la serie: los
    nombres "G90", "Gasohol 90 Plus" y "Gasohol Regular" colapsan en "REGULAR".

    Returns:
        DataFrame con columnas [departamento, ym, precio], ordenado
        cronológicamente. `ym` es el primer día del mes (datetime64).
    """
    df = pd.read_csv(config.F_SERIE_MENSUAL)
    df["familia"] = df["combustible_norm"].map(config.FAMILIAS_COMBUSTIBLE)

    df = df[df["familia"] == familia].copy()
    if df.empty:
        raise ValueError(
            f"No hay registros para la familia '{familia}'. "
            f"Familias disponibles: {sorted(set(config.FAMILIAS_COMBUSTIBLE.values()))}"
        )

    df["ym"] = pd.to_datetime(
        dict(year=df["anio"], month=df["mes_num"], day=1)
    )
    df = sanear_precios(df, ["precio_soles_galon"])

    # Varias denominaciones pueden coexistir en un mismo mes durante la
    # transición normativa; el promedio simple las reconcilia en una serie única.
    panel = (
        df.groupby(["departamento", "ym"], as_index=False)["precio_soles_galon"]
        .mean()
        .rename(columns={"precio_soles_galon": "precio"})
        .sort_values(["departamento", "ym"])
        .reset_index(drop=True)
    )
    return panel


# -----------------------------------------------------------------------------
# 2. MUESTRA NACIONAL DE GRIFOS OSINERGMIN (Archivo A oficial)
# -----------------------------------------------------------------------------
def cargar_grifos_diarios_nacional() -> pd.DataFrame:
    """Carga la muestra nacional anonimizada de grifos de Osinergmin.
    
    Aplica el saneamiento de precios oficial de la Fase R (anulación de 16 valores
    extremos < S/ 5 o > S/ 30 sin eliminar filas).
    """
    df = pd.read_csv(config.F_GRIFOS_DIARIOS)
    cols_precio = [c for c in df.columns if "g_" in c or "precio" in c or "diesel" in c]
    df = sanear_precios(df, cols_precio)
    return df


# -----------------------------------------------------------------------------
# 3. SANEAMIENTO COMPARTIDO
# -----------------------------------------------------------------------------
def sanear_precios(df: pd.DataFrame, columnas: list[str]) -> pd.DataFrame:
    """Anula los precios fuera del rango físicamente plausible (S/ 5 – S/ 30).

    No elimina filas: convierte el valor imposible en NaN para que la fila siga
    aportando sus demás columnas. Es el mismo criterio de la Fase R que saneó
    los 16 valores extremos del archivo nacional.
    """
    df = df.copy()
    for col in columnas:
        if col not in df.columns:
            continue
        fuera_de_rango = (df[col] < config.PRECIO_MIN_VALIDO) | (
            df[col] > config.PRECIO_MAX_VALIDO
        )
        df.loc[fuera_de_rango, col] = np.nan
    return df


def resumen_fuentes() -> pd.DataFrame:
    """Inventario ejecutable de las fuentes disponibles y su estado en disco."""
    filas = []
    for nombre, ruta in [
        ("serie_mensual_departamental", config.F_SERIE_MENSUAL),
        ("grifos_diarios_nacional", config.F_GRIFOS_DIARIOS),
        ("macro_mensual", config.F_MACRO),
    ]:
        existe = os.path.exists(ruta)
        filas.append(
            {
                "fuente": nombre,
                "disponible": existe,
                "mb": round(os.path.getsize(ruta) / 1e6, 2) if existe else 0.0,
                "ruta": os.path.relpath(ruta, config.PROJECT_ROOT),
            }
        )
    return pd.DataFrame(filas)
