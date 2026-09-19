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
# 2. GRIFOS DE LIMA Y CALLAO CON GEOLOCALIZACIÓN (fuente del modelo de posición)
# -----------------------------------------------------------------------------
def cargar_grifos_lima_callao(ruta: str | None = None) -> pd.DataFrame:
    """Carga el corte transversal de grifos de Lima y Callao con coordenadas.

    Este archivo es el que levanta el semáforo rojo de geolocalización de la
    Fase R: a diferencia del archivo anonimizado nacional, aquí cada grifo trae
    `lat`, `lon`, `distrito` y `marca` identificables.

    Returns:
        DataFrame con los precios en columnas numéricas y sin filas duplicadas
        por `codigo_osinergmin`.
    """
    ruta = ruta or config.F_PREMIUM_LIMA
    df = pd.read_csv(ruta, encoding="utf-8-sig", dtype={"codigo_osinergmin": str})

    columnas_precio = [
        "premium_lista", "descuento", "premium_final",
        "regular_lista", "diesel_lista",
    ]
    for col in columnas_precio:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in ("lat", "lon"):
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = sanear_precios(df, [c for c in columnas_precio if c != "descuento"])
    df = _sanear_coordenadas(df)

    # Un mismo grifo no puede aparecer dos veces en un corte transversal.
    df = df.drop_duplicates(subset="codigo_osinergmin", keep="last").reset_index(drop=True)
    return df


def cargar_historico_lima_callao(ruta: str | None = None) -> pd.DataFrame:
    """Carga el histórico de snapshots del scraper, reparando filas concatenadas.

    El archivo crudo tiene filas frontera pegadas entre snapshots (falta el salto
    de línea final en cada append). Leerlo sin reparar hace que el parser aborte
    o descarte silenciosamente una fila por snapshot.

    Returns:
        DataFrame con columna adicional `scraped_dt` (datetime con zona horaria).
    """
    ruta = ruta or config.F_HISTORICO_LIMA
    with open(ruta, encoding="utf-8-sig") as fh:
        crudo = fh.read()

    reparado = _PATRON_FILAS_PEGADAS.sub('"\n', crudo)
    df = pd.read_csv(
        io.StringIO(reparado), dtype={"codigo_osinergmin": str}
    )

    for col in ("premium_lista", "descuento", "premium_final",
                "regular_lista", "diesel_lista", "lat", "lon"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["scraped_dt"] = pd.to_datetime(df["scraped_at"], format="ISO8601")
    df = sanear_precios(
        df, ["premium_lista", "premium_final", "regular_lista", "diesel_lista"]
    )
    return df.sort_values(["codigo_osinergmin", "scraped_dt"]).reset_index(drop=True)


def reparar_historico_en_disco(ruta: str | None = None) -> int:
    """Reescribe el histórico del scraper con las filas frontera separadas.

    Returns:
        Número de uniones reparadas.
    """
    ruta = ruta or config.F_HISTORICO_LIMA
    with open(ruta, encoding="utf-8-sig") as fh:
        crudo = fh.read()

    n_uniones = len(_PATRON_FILAS_PEGADAS.findall(crudo))
    if n_uniones == 0 and crudo.endswith("\n"):
        return 0

    reparado = _PATRON_FILAS_PEGADAS.sub('"\n', crudo)
    if not reparado.endswith("\n"):
        reparado += "\n"
    with open(ruta, "w", encoding="utf-8") as fh:
        fh.write(reparado)
    return n_uniones


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


def _sanear_coordenadas(df: pd.DataFrame) -> pd.DataFrame:
    """Anula coordenadas fuera del rectángulo que contiene Lima y Callao."""
    df = df.copy()
    dentro = (
        df["lat"].between(-12.6, -11.4) & df["lon"].between(-77.3, -76.5)
    )
    df.loc[~dentro, ["lat", "lon"]] = np.nan
    return df


def resumen_fuentes() -> pd.DataFrame:
    """Inventario ejecutable de las fuentes disponibles y su estado en disco."""
    filas = []
    for nombre, ruta in [
        ("serie_mensual_departamental", config.F_SERIE_MENSUAL),
        ("grifos_diarios_nacional", config.F_GRIFOS_DIARIOS),
        ("grifos_lima_callao_corte", config.F_PREMIUM_LIMA),
        ("grifos_lima_callao_historico", config.F_HISTORICO_LIMA),
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
