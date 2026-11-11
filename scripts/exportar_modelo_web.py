"""
===============================================================================
PROYECTO: Lunetra IA — Fase M -> MVP
ARCHIVO:  scripts/exportar_modelo_web.py
DESCRIPCIÓN:
    Exporta el modelo A2 entrenado (StandardScaler + Regresión Logística
    multinomial) a JSON para que el MVP en Next.js (mvp/web) ejecute la MISMA
    inferencia en el servidor de Vercel, sin depender de Python en producción.

    Genera en mvp/web/data/:
      - modelo_a2.json        parámetros del modelo (medias, escalas, coeficientes,
                              interceptos, clases, umbral P*) + métricas de test.
      - departamentos.json    última fila de features por departamento (mes t),
                              percentiles de mercado y, como fixture de paridad,
                              las probabilidades que calcula scikit-learn.

    El test `mvp/web/lib/__tests__/paridad.test.ts` exige que la inferencia en
    TypeScript reproduzca las probabilidades de scikit-learn (tolerancia 1e-6).

USO:
    python modelado/entrenamiento_a2.py     # si aún no existe el .joblib
    python scripts/exportar_modelo_web.py
===============================================================================
"""

from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "src"))
sys.path.insert(0, RAIZ)

from tanquelleno import config  # noqa: E402
import pipeline_inferencia as pipe  # noqa: E402

SALIDA = os.path.join(RAIZ, "mvp", "web", "data")


def _extraer_pipeline(modelo):
    """Devuelve (scaler, logistic) del Pipeline elegido por el entrenamiento."""
    if not hasattr(modelo, "named_steps"):
        raise TypeError(
            "El modelo elegido no es un Pipeline StandardScaler + LogisticRegression. "
            "La exportación web solo soporta ese candidato (el elegido en validación)."
        )
    return modelo.named_steps["escalado"], modelo.named_steps["clf"]


def main() -> None:
    artefacto, panel = pipe.cargar_artefactos()
    modelo, columnas, clases = artefacto["modelo"], artefacto["columnas"], artefacto["clases"]
    escalado, clf = _extraer_pipeline(modelo)

    with open(os.path.join(config.REPORTES_DIR, "metricas_a2.json"), encoding="utf-8") as fh:
        metricas = json.load(fh)

    modelo_json = {
        "version": artefacto.get("entrenado_en"),
        "familia": artefacto.get("familia", "REGULAR"),
        "tipo": "StandardScaler + LogisticRegression multinomial (L2, C=0.5, class_weight=balanced)",
        "columnas": list(columnas),
        "clases": [config.CLASES[int(c)] for c in clases],
        "media": escalado.mean_.tolist(),
        "escala": escalado.scale_.tolist(),
        "coeficientes": clf.coef_.tolist(),
        "interceptos": clf.intercept_.tolist(),
        "umbral_sube": float(artefacto["umbral"]),
        "galones_por_tanqueada": config.GALONES_POR_TANQUEADA,
        "zona_incertidumbre": list(config.ZONA_INCERTIDUMBRE),
        "metricas_test": {
            "baseline_persistencia_macro_f1": metricas["baselines_test"]["persistencia_mantiene"]["macro_f1"],
            "macro_f1_umbral": metricas["test_con_umbral"]["macro_f1"],
            "macro_f1_argmax": metricas["test_argmax"]["macro_f1"],
            "recall_sube_umbral": metricas["test_con_umbral"]["recall_sube"],
            "costo_modelo": metricas["test_con_umbral"]["costo_esperado_soles"],
            "costo_baseline": metricas["baselines_test"]["persistencia_mantiene"]["costo_esperado_soles"],
        },
    }

    departamentos = []
    for depto in sorted(panel["departamento"].unique()):
        filas = panel[panel["departamento"] == depto].sort_values("ym")
        ultima = filas.iloc[[-1]]
        x = ultima[columnas].to_numpy(dtype=float)
        if not np.all(np.isfinite(x)):
            # Sin features completas no se puede predecir con honestidad: se omite.
            print(f"  [omitido] {depto}: features incompletas en el último mes")
            continue
        proba = modelo.predict_proba(x)[0]
        payload = pipe.generar_payload(depto)
        mes_base = pd.Timestamp(ultima["ym"].iloc[0])
        mercado = pipe.percentiles_para(depto, panel, modelo_json["familia"])
        departamentos.append(
            {
                "departamento": depto,
                "mes_base": str(mes_base.date()),
                "features": [float(v) for v in x[0]],
                "mercado": mercado,
                "esperado_python": {
                    "probabilidades": {
                        config.CLASES[int(c)]: float(p) for c, p in zip(clases, proba)
                    },
                    "tendencia_predicha": payload["tendencia_predicha"],
                    "confianza": payload["confianza"],
                    "periodo": payload["periodo"],
                },
            }
        )

    os.makedirs(SALIDA, exist_ok=True)
    with open(os.path.join(SALIDA, "modelo_a2.json"), "w", encoding="utf-8") as fh:
        json.dump(modelo_json, fh, ensure_ascii=False, indent=2)
    with open(os.path.join(SALIDA, "departamentos.json"), "w", encoding="utf-8") as fh:
        json.dump(departamentos, fh, ensure_ascii=False, indent=2)

    print(f"Exportados: modelo ({len(columnas)} features, clases {modelo_json['clases']}) "
          f"y {len(departamentos)} departamentos -> {os.path.relpath(SALIDA, RAIZ)}")


if __name__ == "__main__":
    main()
