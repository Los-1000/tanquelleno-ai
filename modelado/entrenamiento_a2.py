"""
===============================================================================
PROYECTO: TanqueLleno AI — Fase M (Modelado)
ARCHIVO:  modelado/entrenamiento_a2.py
DESCRIPCIÓN:
    Entrenamiento del componente analítico A2: clasificador de la tendencia del
    precio promedio departamental en t+1 (SUBE / MANTIENE / BAJA).

    Ejecuta la secuencia completa comprometida en el Model Design Canvas:
      1. Construye el dataset maestro y audita el protocolo anti-leakage.
      2. Mide los baselines declarados (persistencia e inercia del signo).
      3. Entrena los candidatos (logística regularizada y boosting de árboles).
      4. Selecciona por Macro-F1 en validación (2025), nunca en test.
      5. Calibra el umbral asimétrico sobre validación, partiendo de P* = 0.25.
      6. Evalúa una sola vez sobre el test ciego (2026) y reporta los OKR.

USO:
    python modelado/entrenamiento_a2.py [--familia REGULAR]
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
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, f1_score, recall_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from tanquelleno import config, features


# -----------------------------------------------------------------------------
# 1. BASELINES DECLARADOS
# -----------------------------------------------------------------------------
def baseline_persistencia(y_true: np.ndarray) -> np.ndarray:
    """"El próximo mes mantendrá el precio del mes actual": predice siempre MANTIENE."""
    return np.full_like(y_true, config.CLASE_MANTIENE)


def baseline_inercia_signo(sub: pd.DataFrame) -> np.ndarray:
    """Repite la dirección del último cambio observado, ΔP(t-1).

    Baseline más exigente que la persistencia: cualquier valor añadido del
    modelo debe superar también a esta regla trivial.
    """
    delta = sub["delta_lag1"].to_numpy()
    return np.select(
        [delta > config.UMBRAL_CLASE, delta < -config.UMBRAL_CLASE],
        [config.CLASE_SUBE, config.CLASE_BAJA],
        default=config.CLASE_MANTIENE,
    )


# -----------------------------------------------------------------------------
# 2. MÉTRICAS DEL CONTRATO
# -----------------------------------------------------------------------------
def evaluar(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """Métricas del Model Design Canvas más el costo económico esperado.

    La exactitud se omite deliberadamente: con el desbalance documentado en H2
    premia al modelo que nunca se moja.
    """
    return {
        "macro_f1": round(float(f1_score(y_true, y_pred, average="macro")), 4),
        "recall_sube": round(
            float(recall_score(y_true, y_pred, labels=[config.CLASE_SUBE],
                               average="macro", zero_division=0)), 4
        ),
        "recall_baja": round(
            float(recall_score(y_true, y_pred, labels=[config.CLASE_BAJA],
                               average="macro", zero_division=0)), 4
        ),
        "costo_esperado_soles": round(costo_economico(y_true, y_pred), 4),
        "matriz_confusion": confusion_matrix(y_true, y_pred, labels=[0, 1, 2]).tolist(),
        "n": int(len(y_true)),
    }


def costo_economico(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Costo medio por decisión, en soles, según la matriz asimétrica.

    Solo la clase SUBE dispara una acción del conductor (tanquear ya), así que
    únicamente los errores sobre esa clase tienen precio:
      - No advertir un alza que sí ocurrió: C(FN) = S/ 4.00
      - Alertar un alza que no ocurrió:      C(FP) = S/ 0.80
    """
    es_alza = y_true == config.CLASE_SUBE
    alerta = y_pred == config.CLASE_SUBE
    fn = int(np.sum(es_alza & ~alerta))
    fp = int(np.sum(~es_alza & alerta))
    return (fn * config.COSTO_FN + fp * config.COSTO_FP) / max(len(y_true), 1)


def predecir_con_umbral(proba: np.ndarray, clases: np.ndarray, umbral: float) -> np.ndarray:
    """Aplica el umbral asimétrico en lugar del argmax ciego.

    Si la probabilidad de alza supera `umbral`, se emite SUBE aunque no sea la
    clase más probable. En caso contrario se decide por argmax entre las
    restantes. Esta es la traducción operativa de C(FN) = 5 x C(FP).
    """
    idx_sube = int(np.where(clases == config.CLASE_SUBE)[0][0])
    p_sube = proba[:, idx_sube]

    otras = np.delete(proba, idx_sube, axis=1)
    clases_otras = np.delete(clases, idx_sube)
    pred = clases_otras[np.argmax(otras, axis=1)]
    return np.where(p_sube > umbral, config.CLASE_SUBE, pred)


def calibrar_umbral(proba_val: np.ndarray, clases: np.ndarray, y_val: np.ndarray) -> dict:
    """Barre umbrales sobre validación y elige el de menor costo económico.

    Se calibra en validación (2025), nunca en test: mover el umbral mirando el
    test ciego equivaldría a entrenar sobre él.
    """
    rejilla = np.round(np.arange(0.05, 0.96, 0.01), 2)
    barrido = []
    for u in rejilla:
        pred = predecir_con_umbral(proba_val, clases, u)
        barrido.append(
            {
                "umbral": float(u),
                "costo": round(costo_economico(y_val, pred), 4),
                "macro_f1": round(float(f1_score(y_val, pred, average="macro")), 4),
                "recall_sube": round(
                    float(recall_score(y_val, pred, labels=[config.CLASE_SUBE],
                                       average="macro", zero_division=0)), 4
                ),
            }
        )

    mejor = min(barrido, key=lambda r: (r["costo"], -r["macro_f1"]))
    en_declarado = min(barrido, key=lambda r: abs(r["umbral"] - config.P_ESTRELLA))
    return {
        "umbral_declarado_pc1": config.P_ESTRELLA,
        "metricas_en_umbral_declarado": en_declarado,
        "umbral_optimo_validacion": mejor["umbral"],
        "metricas_en_umbral_optimo": mejor,
        "barrido": barrido,
    }


# -----------------------------------------------------------------------------
# 3. CANDIDATOS
# -----------------------------------------------------------------------------
def construir_candidatos() -> dict:
    """Modelos a comparar.

    `class_weight="balanced"` es obligatorio aquí: sin él, el desbalance
    documentado en H2 empuja a ambos modelos a predecir siempre MANTIENE, que
    es exactamente el baseline que deben superar.
    """
    return {
        "logistica_regularizada": Pipeline(
            [
                ("escalado", StandardScaler()),
                (
                    "clf",
                    LogisticRegression(
                        max_iter=2000,
                        C=0.5,
                        class_weight="balanced",
                        random_state=config.SEMILLA,
                    ),
                ),
            ]
        ),
        "boosting_arboles": HistGradientBoostingClassifier(
            max_depth=4,
            max_iter=300,
            learning_rate=0.06,
            l2_regularization=1.0,
            min_samples_leaf=25,
            class_weight="balanced",
            early_stopping=False,
            random_state=config.SEMILLA,
        ),
    }


# -----------------------------------------------------------------------------
# 4. ORQUESTACIÓN
# -----------------------------------------------------------------------------
def main(familia: str = "REGULAR") -> dict:
    print("=" * 78)
    print("ENTRENAMIENTO DEL COMPONENTE ANALÍTICO A2 — TanqueLleno AI")
    print("=" * 78)

    os.makedirs(config.MODELOS_DIR, exist_ok=True)
    os.makedirs(config.REPORTES_DIR, exist_ok=True)

    # --- Dataset y auditoría -------------------------------------------------
    panel = features.construir_dataset_maestro(familia)
    columnas = features.columnas_modelo(panel)
    features.auditar_antileakage(panel, columnas)
    print(f"\n[1/5] Dataset maestro: {len(panel):,} filas x {len(columnas)} features")
    print(f"      Familia: {familia} | Descartadas por warm-up de lags: "
          f"{panel.attrs['filas_descartadas_por_warmup']}")
    macro = panel.attrs.get("macro_incorporadas", [])
    print(f"      Variables macro externas: "
          f"{macro if macro else 'NO DISPONIBLES (semáforo rojo; ver scripts/obtener_macro.py)'}")
    print("      Auditoría anti-leakage: OK (sin features contemporáneas, splits disjuntos)")

    panel.to_parquet(config.F_DATASET_MAESTRO, index=False)
    print(f"      Guardado: {os.path.relpath(config.F_DATASET_MAESTRO, config.PROJECT_ROOT)}")

    splits = features.separar_splits(panel, columnas)
    X_tr, y_tr, _ = splits["train"]
    X_va, y_va, _ = splits["val"]
    X_te, y_te, sub_te = splits["test"]

    resumen_splits = {}
    for nombre, (_, y_s, sub_s) in splits.items():
        reparto = {config.CLASES[c]: int((y_s == c).sum()) for c in (0, 1, 2)}
        resumen_splits[nombre] = {
            "n": int(len(y_s)),
            "desde": str(sub_s["ym"].min().date()) if len(sub_s) else None,
            "hasta": str(sub_s["ym"].max().date()) if len(sub_s) else None,
            "distribucion": reparto,
        }
        print(f"      {nombre:5s}: n={len(y_s):5,}  {resumen_splits[nombre]['desde']} "
              f"-> {resumen_splits[nombre]['hasta']}  {reparto}")

    # --- Baselines -----------------------------------------------------------
    print("\n[2/5] Baselines sobre el test ciego")
    baselines = {
        "persistencia_mantiene": evaluar(y_te, baseline_persistencia(y_te)),
        "inercia_del_signo": evaluar(y_te, baseline_inercia_signo(sub_te)),
    }
    for nombre, m in baselines.items():
        print(f"      {nombre:24s} Macro-F1={m['macro_f1']:.4f}  "
              f"Recall(SUBE)={m['recall_sube']:.4f}  Costo=S/ {m['costo_esperado_soles']:.3f}")

    # --- Candidatos, seleccionados en validación -----------------------------
    print("\n[3/5] Candidatos (selección por Macro-F1 en validación 2025)")
    candidatos, entrenados = {}, {}
    for nombre, modelo in construir_candidatos().items():
        modelo.fit(X_tr, y_tr)
        m_va = evaluar(y_va, modelo.predict(X_va))
        candidatos[nombre] = {"validacion_argmax": m_va}
        entrenados[nombre] = modelo
        print(f"      {nombre:24s} Macro-F1(val)={m_va['macro_f1']:.4f}  "
              f"Recall(SUBE)={m_va['recall_sube']:.4f}")

    elegido = max(candidatos, key=lambda n: candidatos[n]["validacion_argmax"]["macro_f1"])
    modelo = entrenados[elegido]
    print(f"      -> Modelo elegido: {elegido}")

    # --- Calibración del umbral asimétrico -----------------------------------
    print(f"\n[4/5] Calibración del umbral asimétrico "
          f"(C_FN=S/ {config.COSTO_FN:.2f}, C_FP=S/ {config.COSTO_FP:.2f})")
    clases = modelo.classes_
    umbral = calibrar_umbral(modelo.predict_proba(X_va), clases, y_va)
    u_decl = umbral["metricas_en_umbral_declarado"]
    u_opt = umbral["metricas_en_umbral_optimo"]
    print(f"      P* declarado en PC1 = {config.P_ESTRELLA:.2f} -> "
          f"costo S/ {u_decl['costo']:.3f}, Macro-F1 {u_decl['macro_f1']:.4f}, "
          f"Recall(SUBE) {u_decl['recall_sube']:.4f}")
    print(f"      P* óptimo en val    = {umbral['umbral_optimo_validacion']:.2f} -> "
          f"costo S/ {u_opt['costo']:.3f}, Macro-F1 {u_opt['macro_f1']:.4f}, "
          f"Recall(SUBE) {u_opt['recall_sube']:.4f}")

    # El umbral que se despliega es el declarado en la PC1; el óptimo se reporta
    # como evidencia de que la elección congelada no fue arbitraria.
    umbral_produccion = config.P_ESTRELLA

    # --- Evaluación final sobre el test ciego --------------------------------
    print("\n[5/5] Evaluación sobre el test ciego (ene–ago 2026)")
    proba_te = modelo.predict_proba(X_te)
    test_argmax = evaluar(y_te, modelo.predict(X_te))
    test_umbral = evaluar(y_te, predecir_con_umbral(proba_te, clases, umbral_produccion))

    print(f"      Argmax  : Macro-F1={test_argmax['macro_f1']:.4f}  "
          f"Recall(SUBE)={test_argmax['recall_sube']:.4f}  "
          f"Costo=S/ {test_argmax['costo_esperado_soles']:.3f}")
    print(f"      P*={umbral_produccion:.2f}: Macro-F1={test_umbral['macro_f1']:.4f}  "
          f"Recall(SUBE)={test_umbral['recall_sube']:.4f}  "
          f"Costo=S/ {test_umbral['costo_esperado_soles']:.3f}")

    okr = {
        "kr1_macro_f1": {
            "meta": config.META_MACRO_F1,
            "obtenido": test_umbral["macro_f1"],
            "cumple": bool(test_umbral["macro_f1"] >= config.META_MACRO_F1),
        },
        "kr1_recall_sube": {
            "meta": config.META_RECALL_SUBE,
            "obtenido": test_umbral["recall_sube"],
            "cumple": bool(test_umbral["recall_sube"] >= config.META_RECALL_SUBE),
        },
        "supera_baseline_persistencia": bool(
            test_umbral["macro_f1"] > baselines["persistencia_mantiene"]["macro_f1"]
        ),
        "supera_baseline_inercia": bool(
            test_umbral["macro_f1"] > baselines["inercia_del_signo"]["macro_f1"]
        ),
        "ahorro_vs_baseline_soles_por_decision": round(
            baselines["persistencia_mantiene"]["costo_esperado_soles"]
            - test_umbral["costo_esperado_soles"],
            4,
        ),
    }
    print("\n      OKR KR1:")
    for clave in ("kr1_macro_f1", "kr1_recall_sube"):
        estado = "CUMPLE" if okr[clave]["cumple"] else "NO CUMPLE"
        print(f"        {clave:18s} meta={okr[clave]['meta']:.2f} "
              f"obtenido={okr[clave]['obtenido']:.4f} -> {estado}")
    print(f"        Ahorro vs. baseline: S/ "
          f"{okr['ahorro_vs_baseline_soles_por_decision']:.3f} por decisión de tanqueo")

    # --- Persistencia de artefactos ------------------------------------------
    joblib.dump(
        {
            "modelo": modelo,
            "columnas": columnas,
            "clases": clases,
            "umbral": umbral_produccion,
            "familia": familia,
            "entrenado_en": datetime.now(timezone.utc).isoformat(),
        },
        config.F_MODELO_TENDENCIA,
    )

    reporte = {
        "generado_en": datetime.now(timezone.utc).isoformat(),
        "familia": familia,
        "features": columnas,
        "macro_externas_disponibles": macro,
        "splits": resumen_splits,
        "baselines_test": baselines,
        "candidatos": candidatos,
        "modelo_elegido": elegido,
        "calibracion_umbral": umbral,
        "umbral_produccion": umbral_produccion,
        "test_argmax": test_argmax,
        "test_con_umbral": test_umbral,
        "okr": okr,
    }
    ruta_reporte = os.path.join(config.REPORTES_DIR, "metricas_a2.json")
    with open(ruta_reporte, "w", encoding="utf-8") as fh:
        json.dump(reporte, fh, ensure_ascii=False, indent=2)

    print(f"\n      Modelo:  {os.path.relpath(config.F_MODELO_TENDENCIA, config.PROJECT_ROOT)}")
    print(f"      Reporte: {os.path.relpath(ruta_reporte, config.PROJECT_ROOT)}")
    print("=" * 78)
    return reporte


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Entrena el componente analítico A2.")
    parser.add_argument(
        "--familia", default="REGULAR",
        choices=sorted(set(config.FAMILIAS_COMBUSTIBLE.values())),
        help="Familia de combustible a modelar (por defecto REGULAR).",
    )
    args = parser.parse_args()
    main(args.familia)
