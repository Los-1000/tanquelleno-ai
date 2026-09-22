"""
===============================================================================
PROYECTO: TanqueLleno AI — Fase M (Modelado)
ARCHIVO:  src/tanquelleno/features.py
DESCRIPCIÓN:
    Construcción del dataset maestro mensual departamental y de la variable
    objetivo del componente analítico A2.

    REGLA CENTRAL (protocolo anti-leakage, plantilla 2):
    para predecir la tendencia del mes t+1 solo se usa información disponible
    hasta el cierre del mes t-1. El precio contemporáneo P(t) jamás entra como
    feature. Esa regla está codificada en `COLUMNAS_FEATURE` y verificada por
    `auditar_antileakage()`.
===============================================================================
"""

from __future__ import annotations

import os

import numpy as np
import pandas as pd

from . import config
from .datos import cargar_serie_mensual

# Features permitidas. Todas derivan de información de t-1 o anterior, o del
# calendario (conocido ex-ante). Añadir aquí una columna contemporánea rompería
# el contrato: `auditar_antileakage()` lo detecta y aborta el entrenamiento.
COLUMNAS_FEATURE = [
    "precio_lag1",          # P(t-1)
    "precio_lag2",          # P(t-2)
    "precio_lag3",          # P(t-3)
    "delta_lag1",           # P(t-1) - P(t-2)
    "delta_lag2",           # P(t-2) - P(t-3)
    "media_movil_3",        # media de P(t-1..t-3)
    "volatilidad_3",        # desviación estándar de P(t-1..t-3)
    "desvio_vs_media3",     # P(t-1) - media_movil_3
    "delta_nacional_lag1",  # variación media del país en t-1 (proxy macro)
    "mes_sin",              # estacionalidad cíclica (calendario, ex-ante)
    "mes_cos",
]

# Columnas que nunca deben aparecer como feature porque contienen o derivan del
# valor del mes t o posterior.
COLUMNAS_PROHIBIDAS = ["precio", "precio_futuro", "delta_futuro", "y", "ym", "split"]


def construir_dataset_maestro(
    familia: str = "REGULAR", solo_etiquetadas: bool = True
) -> pd.DataFrame:
    """Genera el panel departamento x mes con features rezagadas y target.

    El target `y` codifica la tendencia del mes **siguiente**:
        1 (SUBE)     si P(t+1) - P(t) >  +UMBRAL_CLASE
        2 (BAJA)     si P(t+1) - P(t) <  -UMBRAL_CLASE
        0 (MANTIENE) en otro caso

    Nota sobre el desfase: `delta_futuro` se mide contra P(t), pero P(t) no se
    expone como feature. El modelo solo observa hasta t-1, lo que reproduce el
    rezago de publicación real de Osinergmin (el reporte del mes t aparece
    cuando t ya cerró).

    Args:
        familia: familia de combustible a modelar.
        solo_etiquetadas: si es True (entrenamiento) descarta las filas sin `y`.
            Debe ponerse en False para inferencia: el último mes observado no
            tiene etiqueta futura por definición, pero sí tiene todas sus
            features y es precisamente la fila sobre la que se quiere predecir.

    Returns:
        DataFrame con las columnas de `COLUMNAS_FEATURE`, más
        [departamento, ym, precio, y, split].
    """
    panel = cargar_serie_mensual(familia)
    panel = panel.sort_values(["departamento", "ym"]).reset_index(drop=True)

    g = panel.groupby("departamento")["precio"]

    # --- Variable objetivo: tendencia de t+1 respecto de t --------------------
    panel["precio_futuro"] = g.shift(-1)
    panel["delta_futuro"] = panel["precio_futuro"] - panel["precio"]
    panel["y"] = np.select(
        [
            panel["delta_futuro"] > config.UMBRAL_CLASE,
            panel["delta_futuro"] < -config.UMBRAL_CLASE,
        ],
        [config.CLASE_SUBE, config.CLASE_BAJA],
        default=config.CLASE_MANTIENE,
    ).astype(float)
    panel.loc[panel["delta_futuro"].isna(), "y"] = np.nan

    # --- Features rezagadas (solo información hasta t-1) ---------------------
    for k in (1, 2, 3):
        panel[f"precio_lag{k}"] = g.shift(k)

    panel["delta_lag1"] = panel["precio_lag1"] - panel["precio_lag2"]
    panel["delta_lag2"] = panel["precio_lag2"] - panel["precio_lag3"]

    ventana = g.shift(1).rolling(3, min_periods=3)
    panel["media_movil_3"] = ventana.mean().reset_index(level=0, drop=True)
    panel["volatilidad_3"] = ventana.std().reset_index(level=0, drop=True)
    panel["desvio_vs_media3"] = panel["precio_lag1"] - panel["media_movil_3"]

    # Contexto nacional en t-1: proxy de los shocks comunes a todo el país
    # mientras las series de WTI/Brent/TC siguen en semáforo rojo.
    panel["delta_nacional_lag1"] = panel.groupby("ym")["delta_lag1"].transform("mean")

    # --- Estacionalidad cíclica (calendario: disponible ex-ante) -------------
    mes = panel["ym"].dt.month
    panel["mes_sin"] = np.sin(2 * np.pi * mes / 12)
    panel["mes_cos"] = np.cos(2 * np.pi * mes / 12)

    # --- Fusión con macro externas, si ya fueron ingestadas ------------------
    panel, macro_incorporadas = _adjuntar_macro(panel)

    panel["split"] = panel["ym"].apply(asignar_split)

    columnas_requeridas = COLUMNAS_FEATURE + macro_incorporadas
    if solo_etiquetadas:
        columnas_requeridas = columnas_requeridas + ["y"]

    antes = len(panel)
    panel = panel.dropna(subset=columnas_requeridas).reset_index(drop=True)
    if solo_etiquetadas:
        panel["y"] = panel["y"].astype(int)

    panel.attrs["filas_descartadas_por_warmup"] = antes - len(panel)
    panel.attrs["familia"] = familia
    panel.attrs["macro_incorporadas"] = macro_incorporadas
    return panel


def columnas_modelo(panel: pd.DataFrame) -> list[str]:
    """Features efectivamente disponibles en el panel construido."""
    return COLUMNAS_FEATURE + list(panel.attrs.get("macro_incorporadas", []))


def asignar_split(ym: pd.Timestamp) -> str:
    """Partición cronológica pura declarada en el Model Design Canvas."""
    if ym <= pd.Timestamp(config.SPLIT_TRAIN_FIN):
        return "train"
    if ym <= pd.Timestamp(config.SPLIT_VAL_FIN):
        return "val"
    return "test"


def _adjuntar_macro(panel: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Incorpora las variables macro rezagadas a t-1 si el archivo existe.

    Mientras `datos/macro_mensual.csv` no haya sido generado por
    `scripts/obtener_macro.py`, el modelo entrena sin estas variables y el
    reporte lo declara explícitamente en lugar de rellenarlas con ceros.

    Returns:
        (panel, nombres de las columnas macro incorporadas)
    """
    if not os.path.exists(config.F_MACRO):
        return panel, []

    macro = pd.read_csv(config.F_MACRO, parse_dates=["ym"]).sort_values("ym")
    base = [c for c in macro.columns if c != "ym"]
    if not base:
        return panel, []

    # Rezago explícito: el valor del mes t-1 se adjunta a la fila del mes t.
    for col in base:
        macro[f"{col}_lag1"] = macro[col].shift(1)

    lags = [f"{c}_lag1" for c in base]
    panel = panel.merge(macro[["ym"] + lags], on="ym", how="left")

    utiles = [c for c in lags if panel[c].notna().any()]
    return panel, utiles


def auditar_antileakage(panel: pd.DataFrame, columnas_usadas: list[str]) -> None:
    """Aborta si el conjunto de features viola el protocolo anti-leakage.

    Verifica tres cosas:
      1. Ninguna feature está en la lista de columnas prohibidas.
      2. Ninguna feature correlaciona ~1.0 con el precio contemporáneo P(t),
         señal de que se coló una transformación del presente.
      3. Los splits no se solapan en el tiempo.

    Raises:
        ValueError: si alguna verificación falla.
    """
    prohibidas_usadas = sorted(set(columnas_usadas) & set(COLUMNAS_PROHIBIDAS))
    if prohibidas_usadas:
        raise ValueError(
            f"Leakage: estas columnas contienen información de t o t+1 y no "
            f"pueden ser features: {prohibidas_usadas}"
        )

    for col in columnas_usadas:
        corr = panel[col].corr(panel["precio"])
        if pd.notna(corr) and abs(corr) > 0.999:
            raise ValueError(
                f"Leakage: la feature '{col}' correlaciona {corr:.4f} con el "
                f"precio contemporáneo P(t); es una copia del presente."
            )

    limites = panel.groupby("split")["ym"].agg(["min", "max"])
    if {"train", "val"} <= set(limites.index):
        if limites.loc["train", "max"] >= limites.loc["val", "min"]:
            raise ValueError("Leakage: los splits train y val se solapan en el tiempo.")
    if {"val", "test"} <= set(limites.index):
        if limites.loc["val", "max"] >= limites.loc["test", "min"]:
            raise ValueError("Leakage: los splits val y test se solapan en el tiempo.")


def separar_splits(panel: pd.DataFrame, columnas: list[str]) -> dict:
    """Devuelve {split: (X, y, sub_dataframe)} respetando el orden cronológico."""
    salida = {}
    for nombre in ("train", "val", "test"):
        sub = panel[panel["split"] == nombre].sort_values(["ym", "departamento"])
        salida[nombre] = (sub[columnas].to_numpy(), sub["y"].to_numpy(), sub)
    return salida
