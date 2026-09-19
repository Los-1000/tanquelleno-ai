"""
===============================================================================
PROYECTO: TanqueLleno AI — Fase M (Modelado)
ARCHIVO:  modelado/entrenamiento_posicion.py
DESCRIPCIÓN:
    Entrenamiento del modelo de posición de precio por grifo para Lima y Callao.

    Responde una pregunta distinta a la del modelo A2. A2 contesta *cuándo*
    tanquear (tendencia temporal); este modelo contesta *dónde*: dado un grifo
    con su marca, distrito y coordenadas, cuál es el precio esperado y si la
    estación está barata, justa o cara frente a su mercado local.

    Es un problema transversal, no una serie temporal: aquí la validación
    cruzada con barajado sí es correcta, y no contradice el protocolo
    anti-leakage de la plantilla 2, que rige sobre datos con eje temporal.
    Lo que sí se controla es el leakage espacial: el precio de referencia del
    entorno de cada grifo se calcula excluyéndolo a él mismo.

USO:
    python modelado/entrenamiento_posicion.py [--objetivo premium_final]
===============================================================================
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

import joblib
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import RidgeCV
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import KFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from tanquelleno import config, geo
from tanquelleno.datos import cargar_grifos_lima_callao

CATEGORICAS = ["marca", "distrito"]
NUMERICAS = ["lat", "lon", "precio_vecinos_mediana", "precio_vecinos_min",
             "dispersion_vecinos", "n_vecinos"]


def construir_tabla_modelado(objetivo: str = "premium_final") -> pd.DataFrame:
    """Une el padrón de grifos con las features de vecindad espacial."""
    grifos = cargar_grifos_lima_callao()
    vecindad = geo.features_vecindad(grifos, columna_precio=objetivo)

    tabla = grifos.merge(vecindad, on="codigo_osinergmin", how="left")
    tabla["etiqueta_posicion"] = geo.etiquetar_posicion(tabla, columna_precio=objetivo)

    # Las estaciones aisladas (sin vecinos suficientes) no pueden compararse con
    # su entorno; conservarlas con NaN imputado inventaría un mercado local.
    tabla = tabla.dropna(subset=[objetivo] + NUMERICAS).reset_index(drop=True)
    return tabla


def construir_modelos() -> dict:
    """Candidatos para estimar el precio esperado de una estación."""
    preproceso = ColumnTransformer(
        [
            ("cat", OneHotEncoder(handle_unknown="ignore", min_frequency=3), CATEGORICAS),
            ("num", StandardScaler(), NUMERICAS),
        ]
    )
    return {
        "ridge": Pipeline(
            [("prep", preproceso), ("reg", RidgeCV(alphas=np.logspace(-3, 3, 25)))]
        ),
        "bosque_aleatorio": Pipeline(
            [
                ("prep", preproceso),
                (
                    "reg",
                    RandomForestRegressor(
                        n_estimators=400,
                        min_samples_leaf=3,
                        max_features=0.6,
                        random_state=config.SEMILLA,
                        n_jobs=-1,
                    ),
                ),
            ]
        ),
    }


def evaluar_regresion(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    return {
        "mae_soles": round(float(mean_absolute_error(y_true, y_pred)), 4),
        "rmse_soles": round(float(np.sqrt(np.mean((y_true - y_pred) ** 2))), 4),
        "r2": round(float(r2_score(y_true, y_pred)), 4),
    }


def main(objetivo: str = "premium_final") -> dict:
    print("=" * 78)
    print("ENTRENAMIENTO DEL MODELO DE POSICIÓN DE PRECIO — Lima y Callao")
    print("=" * 78)

    os.makedirs(config.MODELOS_DIR, exist_ok=True)
    os.makedirs(config.REPORTES_DIR, exist_ok=True)

    tabla = construir_tabla_modelado(objetivo)
    X = tabla[CATEGORICAS + NUMERICAS]
    y = tabla[objetivo].to_numpy()

    print(f"\n[1/4] Corte transversal: {len(tabla)} estaciones utilizables")
    print(f"      Objetivo: {objetivo} | Marcas: {tabla['marca'].nunique()} | "
          f"Distritos: {tabla['distrito'].nunique()}")
    mercado = geo.percentiles_mercado(tabla, columna_precio=objetivo)
    print(f"      Mercado: P10=S/ {mercado['p10_mercado']:.2f}  "
          f"P50=S/ {mercado['p50_mediana']:.2f}  P90=S/ {mercado['p90_mercado']:.2f}  "
          f"Brecha=S/ {mercado['brecha_dispersion']:.2f}")
    print(f"      Ahorro máximo por tanqueada ({config.GALONES_POR_TANQUEADA} gal): "
          f"S/ {mercado['ahorro_por_tanqueada']:.2f}")

    # --- Baselines: lo que se consigue sin modelo ---------------------------
    print("\n[2/4] Baselines")
    baselines = {
        "media_global": evaluar_regresion(y, np.full_like(y, y.mean())),
        "mediana_por_distrito": evaluar_regresion(
            y, tabla.groupby("distrito")[objetivo].transform("median").to_numpy()
        ),
        "mediana_por_marca": evaluar_regresion(
            y, tabla.groupby("marca")[objetivo].transform("median").to_numpy()
        ),
    }
    for nombre, m in baselines.items():
        print(f"      {nombre:22s} MAE=S/ {m['mae_soles']:.3f}  R2={m['r2']:.4f}")

    # --- Candidatos con validación cruzada ----------------------------------
    # Con N del orden de 190 estaciones, una sola partición hold-out daría una
    # métrica dominada por el ruido del muestreo; se usa CV de 5 pliegues.
    print("\n[3/4] Candidatos (validación cruzada de 5 pliegues)")
    cv = KFold(n_splits=5, shuffle=True, random_state=config.SEMILLA)
    candidatos = {}
    for nombre, modelo in construir_modelos().items():
        pred = cross_val_predict(modelo, X, y, cv=cv)
        candidatos[nombre] = evaluar_regresion(y, pred)
        print(f"      {nombre:22s} MAE=S/ {candidatos[nombre]['mae_soles']:.3f}  "
              f"R2={candidatos[nombre]['r2']:.4f}")

    elegido = min(candidatos, key=lambda n: candidatos[n]["mae_soles"])
    modelo = construir_modelos()[elegido]
    modelo.fit(X, y)
    print(f"      -> Modelo elegido: {elegido}")

    # --- Posición relativa y ahorro accionable ------------------------------
    print("\n[4/4] Posición de mercado y ahorro accionable")
    reparto = tabla["etiqueta_posicion"].value_counts().to_dict()
    print(f"      Etiquetas por distrito: {reparto}")

    ahorro = _ahorro_por_radio(tabla, objetivo)
    for radio, datos in ahorro.items():
        print(f"      Radio {radio}: moverse al grifo más barato del entorno ahorra en "
              f"mediana S/ {datos['ahorro_mediano_por_tanqueada']:.2f} por tanqueada "
              f"(cobertura {datos['cobertura_pct']:.0f}% de estaciones)")

    descuentos = _resumen_descuentos(tabla)
    for marca, d in descuentos.items():
        print(f"      Descuento de app en {marca}: S/ {d['descuento_medio_por_galon']:.2f}/gal "
              f"= S/ {d['ahorro_por_tanqueada']:.2f} por tanqueada ({d['n_estaciones']} grifos)")

    joblib.dump(
        {
            "modelo": modelo,
            "categoricas": CATEGORICAS,
            "numericas": NUMERICAS,
            "objetivo": objetivo,
            "entrenado_en": datetime.now(timezone.utc).isoformat(),
        },
        config.F_MODELO_POSICION,
    )

    reporte = {
        "generado_en": datetime.now(timezone.utc).isoformat(),
        "objetivo": objetivo,
        "n_estaciones": int(len(tabla)),
        "cobertura": {
            "distritos": int(tabla["distrito"].nunique()),
            "marcas": sorted(tabla["marca"].unique().tolist()),
            "zonas": sorted(tabla["zona"].unique().tolist()),
        },
        "mercado": mercado,
        "baselines": baselines,
        "candidatos_cv5": candidatos,
        "modelo_elegido": elegido,
        "reparto_etiquetas": {str(k): int(v) for k, v in reparto.items()},
        "ahorro_por_radio": ahorro,
        "descuento_por_marca": descuentos,
    }
    ruta = os.path.join(config.REPORTES_DIR, "metricas_posicion.json")
    with open(ruta, "w", encoding="utf-8") as fh:
        json.dump(reporte, fh, ensure_ascii=False, indent=2)

    print(f"\n      Modelo:  {os.path.relpath(config.F_MODELO_POSICION, config.PROJECT_ROOT)}")
    print(f"      Reporte: {os.path.relpath(ruta, config.PROJECT_ROOT)}")
    print("=" * 78)
    return reporte


def _ahorro_por_radio(tabla: pd.DataFrame, objetivo: str) -> dict:
    """Cuantifica el ahorro de moverse al grifo más barato dentro de un radio.

    Es la traducción a soles del KR4: cuánto captura realmente el conductor si
    la app le indica la estación más barata a la que puede llegar.
    """
    resultado = {}
    for radio_km in (1.0, 2.0, 3.0, 5.0):
        vecindad = geo.features_vecindad(
            tabla, columna_precio=objetivo, radio_km=radio_km, min_vecinos=1
        )
        unido = tabla[["codigo_osinergmin", objetivo]].merge(
            vecindad[["codigo_osinergmin", "precio_vecinos_min"]],
            on="codigo_osinergmin", how="left",
        )
        delta = (unido[objetivo] - unido["precio_vecinos_min"]).clip(lower=0).dropna()
        resultado[f"{radio_km:g}km"] = {
            "ahorro_mediano_por_galon": round(float(delta.median()), 4),
            "ahorro_mediano_por_tanqueada": round(
                float(delta.median()) * config.GALONES_POR_TANQUEADA, 2
            ),
            "ahorro_p90_por_tanqueada": round(
                float(delta.quantile(0.90)) * config.GALONES_POR_TANQUEADA, 2
            ),
            "cobertura_pct": round(100 * len(delta) / len(tabla), 1),
        }
    return resultado


def _resumen_descuentos(tabla: pd.DataFrame) -> dict:
    """Descuento medio de aplicación por marca, en soles por galón.

    Esta variable no existía en la fuente nacional anonimizada. Es relevante
    porque un descuento fijo de marca puede superar al ahorro obtenido por
    acertar la tendencia mensual.
    """
    if "descuento" not in tabla.columns:
        return {}
    resumen = tabla.groupby("marca")["descuento"].agg(["mean", "max", "size"])
    return {
        str(marca): {
            "descuento_medio_por_galon": round(float(fila["mean"]), 2),
            "descuento_max_por_galon": round(float(fila["max"]), 2),
            "ahorro_por_tanqueada": round(
                float(fila["mean"]) * config.GALONES_POR_TANQUEADA, 2
            ),
            "n_estaciones": int(fila["size"]),
        }
        for marca, fila in resumen.iterrows()
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Entrena el modelo de posición de precio por grifo."
    )
    parser.add_argument(
        "--objetivo", default="premium_final",
        choices=["premium_final", "premium_lista", "regular_lista", "diesel_lista"],
        help="Columna de precio a modelar (por defecto el premium con descuento).",
    )
    args = parser.parse_args()
    main(args.objetivo)
