"""
===============================================================================
PROYECTO: TanqueLleno AI — Fase M (Modelado)
ARCHIVO:  pipeline_inferencia.py
DESCRIPCIÓN:
    Pipeline end-to-end del Patrón de Conexión 1 (Modelo -> Lenguaje):

        features rezagadas -> modelo A2 -> umbral asimétrico
        -> payload JSON -> System Prompt G1 -> recomendación en texto
        -> auditoría anti-alucinación (KR2)

    Los percentiles del payload se calculan sobre el padrón real de grifos de
    Lima y Callao cuando el departamento consultado es Lima; en el resto del
    país se recurre a la dispersión de la serie departamental, y el payload lo
    declara en `fuente_percentiles` para no presentar como local un dato que
    no lo es.

USO:
    python pipeline_inferencia.py --departamento LIMA --nivel-tanque bajo
    python pipeline_inferencia.py --auditoria-kr2 50
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

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

import joblib

from tanquelleno import config, features, geo, prompts
from tanquelleno.datos import cargar_grifos_lima_callao

MESES_ES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Setiembre", "Octubre", "Noviembre", "Diciembre",
]

# Correspondencia entre la familia que modela A2 y la columna de precio del
# padrón de Lima/Callao. Sin este mapeo el payload podría anunciar "Gasolina
# Regular" mientras muestra los percentiles del premium: una incoherencia que
# el conductor leería como un precio equivocado.
COLUMNA_PRECIO_PADRON = {
    "REGULAR": ("regular_lista", "Gasolina Regular"),
    "PREMIUM": ("premium_final", "Gasolina Premium (precio con descuento de aplicativo)"),
    "DIESEL": ("diesel_lista", "Diésel B5"),
}


def cargar_artefactos() -> tuple[dict, pd.DataFrame]:
    """Carga el modelo A2 entrenado y el panel de inferencia.

    El panel se reconstruye con `solo_etiquetadas=False`, no se lee del parquet
    de entrenamiento: ese archivo descarta el último mes observado por no tener
    etiqueta futura, que es justamente la fila sobre la que hay que predecir.
    """
    if not os.path.exists(config.F_MODELO_TENDENCIA):
        raise FileNotFoundError(
            f"Falta {os.path.relpath(config.F_MODELO_TENDENCIA, config.PROJECT_ROOT)}. "
            "Ejecuta primero:\n    python modelado/entrenamiento_a2.py"
        )
    artefacto = joblib.load(config.F_MODELO_TENDENCIA)
    panel = features.construir_dataset_maestro(
        artefacto.get("familia", "REGULAR"), solo_etiquetadas=False
    )
    return artefacto, panel


def clasificar_confianza(probabilidades: np.ndarray) -> str:
    """Traduce la distribución de probabilidad a la etiqueta del contrato G1.

    Se mide sobre la probabilidad de la clase más probable: cuanto más cerca
    del azar (1/3), menos confianza merece la recomendación.
    """
    p_max = float(np.max(probabilidades))
    if p_max >= 0.60:
        return "ALTA"
    if p_max >= 0.45:
        return "MEDIA"
    return "BAJA"


def percentiles_para(
    departamento: str, panel: pd.DataFrame, familia: str = "REGULAR"
) -> dict:
    """Percentiles de mercado del departamento consultado.

    Para Lima y Callao usa el padrón georreferenciado de grifos, que refleja la
    dispersión real entre estaciones. Para el resto del país solo existe la
    serie departamental promedio, así que la banda se construye sobre la
    variación histórica reciente y el payload lo declara explícitamente.
    """
    columna, _ = COLUMNA_PRECIO_PADRON[familia]
    if departamento.upper() in ("LIMA", "CALLAO") and os.path.exists(config.F_PREMIUM_LIMA):
        grifos = cargar_grifos_lima_callao()
        if departamento.upper() == "CALLAO":
            grifos = grifos[grifos["zona"].str.upper() == "CALLAO"]

        # Si la columna del padrón viene mayoritariamente vacía, una banda
        # calculada sobre un puñado de grifos no representa al mercado.
        if grifos[columna].notna().sum() >= 20:
            percentiles = geo.percentiles_mercado(grifos, columna_precio=columna)
            percentiles["fuente_percentiles"] = (
                f"padron_grifos_lima_callao/{columna} "
                f"({percentiles['n_estaciones']} estaciones)"
            )
            return percentiles

    serie = panel[panel["departamento"] == departamento.upper()]["precio"].dropna()
    if serie.empty:
        raise ValueError(f"No hay serie de precios para el departamento '{departamento}'.")
    ultimos = serie.tail(12)
    p10, p50, p90 = (float(ultimos.quantile(q)) for q in (0.10, 0.50, 0.90))
    return {
        "p10_mercado": round(p10, 2),
        "p50_mediana": round(p50, 2),
        "p90_mercado": round(p90, 2),
        "brecha_dispersion": round(p90 - p10, 2),
        "n_estaciones": 0,
        "ahorro_por_tanqueada": round((p90 - p10) * config.GALONES_POR_TANQUEADA, 2),
        "fuente_percentiles": "serie_departamental_mensual_ultimos_12_meses",
    }


def generar_payload(departamento: str = "LIMA") -> dict:
    """Ejecuta el modelo A2 sobre el último mes disponible y arma el payload.

    Returns:
        dict con los 10 campos obligatorios del contrato, más `_trazabilidad`,
        que la app puede mostrar pero el generador no debe citar.
    """
    artefacto, panel = cargar_artefactos()
    modelo, columnas, clases = artefacto["modelo"], artefacto["columnas"], artefacto["clases"]
    umbral = artefacto["umbral"]

    depto = departamento.upper()
    filas = panel[panel["departamento"] == depto].sort_values("ym")
    if filas.empty:
        disponibles = sorted(panel["departamento"].unique())
        raise ValueError(f"Departamento '{depto}' no encontrado. Disponibles: {disponibles}")

    ultima = filas.iloc[[-1]]
    proba = modelo.predict_proba(ultima[columnas].to_numpy())[0]
    idx_sube = int(np.where(clases == config.CLASE_SUBE)[0][0])
    p_sube = float(proba[idx_sube])

    if p_sube > umbral:
        clase = config.CLASE_SUBE
    else:
        clase = int(np.delete(clases, idx_sube)[np.argmax(np.delete(proba, idx_sube))])

    # El modelo predice t+1 a partir de la última fila observada (mes t).
    mes_objetivo = pd.Timestamp(ultima["ym"].iloc[0]) + pd.DateOffset(months=1)
    periodo = f"{MESES_ES[mes_objetivo.month - 1]} {mes_objetivo.year} (t+1)"

    familia = artefacto.get("familia", "REGULAR")
    mercado = percentiles_para(depto, panel, familia)
    payload = {
        "departamento": depto,
        "combustible": COLUMNA_PRECIO_PADRON[familia][1],
        "periodo": periodo,
        "tendencia_predicha": config.CLASES[clase],
        "probabilidad_alza": round(p_sube, 2),
        "confianza": clasificar_confianza(proba),
        "p10_mercado": mercado["p10_mercado"],
        "p50_mediana": mercado["p50_mediana"],
        "p90_mercado": mercado["p90_mercado"],
        "brecha_dispersion": mercado["brecha_dispersion"],
    }

    payload["_trazabilidad"] = {
        "mes_base_observado": str(pd.Timestamp(ultima["ym"].iloc[0]).date()),
        "umbral_aplicado": umbral,
        "probabilidades": {
            config.CLASES[int(c)]: round(float(p), 4) for c, p in zip(clases, proba)
        },
        "fuente_percentiles": mercado["fuente_percentiles"],
        "ahorro_por_tanqueada": mercado["ahorro_por_tanqueada"],
    }
    return payload


def recomendar(departamento: str = "LIMA", nivel_tanque: str = "medio") -> dict:
    """Payload + texto generado + auditoría, en una sola llamada."""
    payload = generar_payload(departamento)
    contrato = {k: v for k, v in payload.items() if not k.startswith("_")}

    texto = prompts.redactar_sin_llm(contrato, nivel_tanque)
    auditoria = prompts.auditar_alucinacion_numerica(texto, contrato)

    return {
        "payload": payload,
        "mensaje_usuario_para_llm": prompts.construir_mensaje_usuario(contrato, nivel_tanque),
        "recomendacion": texto,
        "auditoria": auditoria,
    }


def auditoria_kr2(n_casos: int = 50) -> dict:
    """Mide el KR2 recorriendo departamentos y niveles de tanque.

    El KR2 exige 100% de recomendaciones sin alucinación numérica sobre al
    menos 50 evaluaciones. Esta función produce esa evidencia de forma
    reproducible en lugar de declararla.
    """
    _, panel = cargar_artefactos()
    departamentos = sorted(panel["departamento"].unique())
    niveles = ["bajo", "medio", "lleno"]

    casos, fallos = [], []
    for depto in departamentos:
        for nivel in niveles:
            if len(casos) >= n_casos:
                break
            try:
                resultado = recomendar(depto, nivel)
            except ValueError:
                continue
            auditoria = resultado["auditoria"]
            casos.append(
                {
                    "departamento": depto,
                    "nivel_tanque": nivel,
                    "tendencia": resultado["payload"]["tendencia_predicha"],
                    "cumple_contrato": auditoria["cumple_contrato"],
                    "cifras_inventadas": auditoria["cifras_inventadas"],
                }
            )
            if not auditoria["cumple_contrato"]:
                fallos.append(casos[-1])

    n = len(casos)
    return {
        "generado_en": datetime.now(timezone.utc).isoformat(),
        "n_evaluaciones": n,
        "meta_minima": 50,
        "sin_alucinacion_pct": round(100 * (n - len(fallos)) / max(n, 1), 2),
        "kr2_cumple": bool(n >= 50 and not fallos),
        "fallos": fallos,
        "casos": casos,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Pipeline de inferencia end-to-end.")
    parser.add_argument("--departamento", default="LIMA")
    parser.add_argument("--nivel-tanque", default="medio", choices=["bajo", "medio", "lleno"])
    parser.add_argument("--auditoria-kr2", type=int, metavar="N", default=None,
                        help="Ejecuta la auditoría del KR2 sobre N casos y sale.")
    args = parser.parse_args()

    if args.auditoria_kr2 is not None:
        os.makedirs(config.REPORTES_DIR, exist_ok=True)
        reporte = auditoria_kr2(args.auditoria_kr2)
        ruta = os.path.join(config.REPORTES_DIR, "auditoria_kr2.json")
        with open(ruta, "w", encoding="utf-8") as fh:
            json.dump(reporte, fh, ensure_ascii=False, indent=2)
        estado = "CUMPLE" if reporte["kr2_cumple"] else "NO CUMPLE"
        print(f"Auditoría KR2: {reporte['n_evaluaciones']} evaluaciones, "
              f"{reporte['sin_alucinacion_pct']:.2f}% sin alucinación -> {estado}")
        if reporte["fallos"]:
            print(f"Fallos: {reporte['fallos']}")
        print(f"Reporte: {os.path.relpath(ruta, config.PROJECT_ROOT)}")
        return

    resultado = recomendar(args.departamento, args.nivel_tanque)
    contrato = {k: v for k, v in resultado["payload"].items() if not k.startswith("_")}

    print("=" * 78)
    print("PAYLOAD (contrato Modelo -> Lenguaje)")
    print("=" * 78)
    print(json.dumps(contrato, ensure_ascii=False, indent=2))
    print("\nTrazabilidad:")
    print(json.dumps(resultado["payload"]["_trazabilidad"], ensure_ascii=False, indent=2))
    print("\n" + "=" * 78)
    print("RECOMENDACIÓN GENERADA")
    print("=" * 78)
    print(resultado["recomendacion"])
    print("\n" + "=" * 78)
    print("AUDITORÍA ANTI-ALUCINACIÓN (KR2)")
    print("=" * 78)
    print(json.dumps(resultado["auditoria"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
