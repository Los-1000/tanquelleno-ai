"""
===============================================================================
PROYECTO: TanqueLleno AI — Fase M (Modelado)
ARCHIVO:  src/tanquelleno/geo.py
DESCRIPCIÓN:
    Utilidades geoespaciales sobre el padrón de grifos de Lima y Callao.

    Este módulo existe gracias a que la nueva fuente de datos incorpora `lat`,
    `lon` y `distrito` por estación. La Fase R había declarado la geolocalización
    en semáforo ROJO y, en consecuencia, el alcance del MVP excluía mapas y la
    función de "grifo más cercano". Con esta fuente esa restricción deja de
    aplicar para Lima Metropolitana y el Callao.
===============================================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

RADIO_TIERRA_KM = 6371.0088

# Etiquetas de posición relativa de un grifo dentro de su mercado local.
ETIQUETA_BARATO = "BARATO"
ETIQUETA_JUSTO = "JUSTO"
ETIQUETA_CARO = "CARO"


def distancia_haversine_km(
    lat1: float | np.ndarray,
    lon1: float | np.ndarray,
    lat2: float | np.ndarray,
    lon2: float | np.ndarray,
) -> np.ndarray:
    """Distancia sobre la superficie terrestre en kilómetros.

    Vectorizada: acepta escalares o arrays de NumPy y difunde entre ellos.
    """
    lat1, lon1, lat2, lon2 = map(np.radians, (lat1, lon1, lat2, lon2))
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 2 * RADIO_TIERRA_KM * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def matriz_distancias(grifos: pd.DataFrame) -> np.ndarray:
    """Matriz simétrica N x N de distancias en km entre todos los grifos."""
    lat = grifos["lat"].to_numpy()
    lon = grifos["lon"].to_numpy()
    return distancia_haversine_km(
        lat[:, None], lon[:, None], lat[None, :], lon[None, :]
    )


def grifos_cercanos(
    grifos: pd.DataFrame,
    lat: float,
    lon: float,
    radio_km: float = 3.0,
    columna_precio: str = "premium_final",
) -> pd.DataFrame:
    """Grifos dentro de un radio, ordenados del más barato al más caro.

    Args:
        grifos: padrón cargado con `datos.cargar_grifos_lima_callao()`.
        lat, lon: posición del conductor.
        radio_km: radio de búsqueda en kilómetros.
        columna_precio: precio a usar para el ordenamiento.

    Returns:
        Subconjunto del padrón con la columna adicional `distancia_km`.
        Vacío si no hay ninguna estación dentro del radio.
    """
    validos = grifos.dropna(subset=["lat", "lon", columna_precio]).copy()
    validos["distancia_km"] = distancia_haversine_km(
        lat, lon, validos["lat"].to_numpy(), validos["lon"].to_numpy()
    )
    dentro = validos[validos["distancia_km"] <= radio_km]
    return dentro.sort_values([columna_precio, "distancia_km"]).reset_index(drop=True)


def features_vecindad(
    grifos: pd.DataFrame,
    columna_precio: str = "premium_final",
    radio_km: float = 2.0,
    min_vecinos: int = 3,
) -> pd.DataFrame:
    """Calcula el precio de referencia del entorno de cada grifo.

    Para cada estación resume los precios de sus vecinos **excluyéndose a sí
    misma**. Esa exclusión es lo que convierte la variable en una feature
    legítima: si el grifo entrara en su propio promedio, el target se filtraría
    dentro del predictor.

    Returns:
        DataFrame con [codigo_osinergmin, precio_vecinos_mediana,
        precio_vecinos_min, precio_vecinos_p90, dispersion_vecinos, n_vecinos].
        Las estaciones con menos de `min_vecinos` quedan en NaN.
    """
    columnas = [
        "codigo_osinergmin", "precio_vecinos_mediana", "precio_vecinos_min",
        "precio_vecinos_p90", "dispersion_vecinos", "n_vecinos",
    ]
    validos = grifos.dropna(subset=["lat", "lon", columna_precio]).reset_index(drop=True)
    if validos.empty:
        return pd.DataFrame(columns=columnas)

    dist = matriz_distancias(validos)
    precios = validos[columna_precio].to_numpy()
    np.fill_diagonal(dist, np.inf)  # un grifo nunca es vecino de sí mismo

    filas = []
    for i in range(len(validos)):
        vecinos = precios[dist[i] <= radio_km]
        if len(vecinos) < min_vecinos:
            filas.append((np.nan, np.nan, np.nan, np.nan, len(vecinos)))
            continue
        p10, p90 = np.percentile(vecinos, [10, 90])
        filas.append(
            (
                float(np.median(vecinos)),
                float(np.min(vecinos)),
                float(p90),
                float(p90 - p10),
                len(vecinos),
            )
        )

    resumen = pd.DataFrame(filas, columns=columnas[1:])
    resumen.insert(0, "codigo_osinergmin", validos["codigo_osinergmin"].to_numpy())
    return resumen


def percentiles_mercado(
    grifos: pd.DataFrame, columna_precio: str = "premium_final"
) -> dict:
    """Percentiles del mercado, en el formato que consume el payload G1.

    Returns:
        dict con p10_mercado, p50_mediana, p90_mercado, brecha_dispersion,
        n_estaciones y ahorro_por_tanqueada.
    """
    from . import config

    serie = grifos[columna_precio].dropna()
    if serie.empty:
        raise ValueError(f"No hay precios válidos en la columna '{columna_precio}'.")

    p10 = float(serie.quantile(0.10))
    p50 = float(serie.quantile(0.50))
    p90 = float(serie.quantile(0.90))
    return {
        "p10_mercado": round(p10, 2),
        "p50_mediana": round(p50, 2),
        "p90_mercado": round(p90, 2),
        "brecha_dispersion": round(p90 - p10, 2),
        "n_estaciones": int(serie.size),
        "ahorro_por_tanqueada": round((p90 - p10) * config.GALONES_POR_TANQUEADA, 2),
    }


def etiquetar_posicion(
    grifos: pd.DataFrame,
    columna_precio: str = "premium_final",
    por: str = "distrito",
) -> pd.Series:
    """Clasifica cada grifo como BARATO / JUSTO / CARO dentro de su mercado local.

    El corte usa los percentiles 33 y 67 del grupo `por`. Los grupos con menos
    de cinco estaciones caen al mercado completo, porque un tercil calculado
    sobre dos o tres grifos no distingue nada.

    Returns:
        Serie de etiquetas alineada con el índice de `grifos`.
    """
    etiquetas = pd.Series(index=grifos.index, dtype="object")
    precios = grifos[columna_precio]

    grandes = grifos.groupby(por)[columna_precio].transform("count") >= 5
    for mascara, agrupador in (
        (grandes, grifos[por]),
        (~grandes, pd.Series("__global__", index=grifos.index)),
    ):
        if not mascara.any():
            continue
        sub = precios[mascara]
        claves = agrupador[mascara]
        q33 = sub.groupby(claves).transform(lambda s: s.quantile(0.33))
        q67 = sub.groupby(claves).transform(lambda s: s.quantile(0.67))
        etiquetas.loc[mascara] = np.select(
            [sub <= q33, sub >= q67],
            [ETIQUETA_BARATO, ETIQUETA_CARO],
            default=ETIQUETA_JUSTO,
        )

    etiquetas[precios.isna()] = np.nan
    return etiquetas
