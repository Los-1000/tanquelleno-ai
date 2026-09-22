"""
===============================================================================
PROYECTO: TanqueLleno AI — Fase M (Modelado)
ARCHIVO:  tests/test_contrato_modelado.py
DESCRIPCIÓN:
    Pruebas que convierten el contrato de la PC1 en verificaciones ejecutables.

    No comprueban que el modelo acierte —eso lo miden los reportes—, sino que
    las garantías metodológicas declaradas se cumplan: ausencia de leakage,
    partición cronológica, umbral asimétrico coherente con la matriz de costos
    y cero alucinaciones numéricas en el generador.

USO:
    pytest tests/ -v
===============================================================================
"""

from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
import pytest

RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(RAIZ, "src"))
sys.path.insert(0, os.path.join(RAIZ, "modelado"))

from tanquelleno import config, features, prompts


@pytest.fixture(scope="module")
def panel():
    return features.construir_dataset_maestro("REGULAR")


# -----------------------------------------------------------------------------
# Protocolo anti-leakage (plantilla 2)
# -----------------------------------------------------------------------------
def test_ninguna_feature_es_el_precio_contemporaneo(panel):
    """P(t) no puede figurar entre las features bajo ningún alias."""
    features.auditar_antileakage(panel, features.columnas_modelo(panel))


def test_auditoria_detecta_leakage_inyectado(panel):
    """La auditoría debe fallar si se cuela el precio contemporáneo."""
    contaminado = panel.copy()
    contaminado["precio_espia"] = contaminado["precio"]
    with pytest.raises(ValueError, match="Leakage"):
        features.auditar_antileakage(
            contaminado, features.columnas_modelo(panel) + ["precio_espia"]
        )


def test_splits_son_cronologicos_y_disjuntos(panel):
    """Train < Val < Test en el tiempo, sin solapamiento ni barajado."""
    limites = panel.groupby("split")["ym"].agg(["min", "max"])
    assert limites.loc["train", "max"] < limites.loc["val", "min"]
    assert limites.loc["val", "max"] < limites.loc["test", "min"]
    assert limites.loc["train", "max"] <= pd.Timestamp(config.SPLIT_TRAIN_FIN)
    assert limites.loc["val", "max"] <= pd.Timestamp(config.SPLIT_VAL_FIN)


def test_lags_corresponden_al_mes_anterior(panel):
    """precio_lag1 de un mes debe ser exactamente el precio del mes previo."""
    depto = panel["departamento"].iloc[0]
    serie = panel[panel["departamento"] == depto].sort_values("ym")
    fila_actual, fila_previa = serie.iloc[5], serie.iloc[4]

    # Solo comparable si los meses son consecutivos en el panel.
    if (fila_actual["ym"] - fila_previa["ym"]).days in range(28, 32):
        assert fila_actual["precio_lag1"] == pytest.approx(fila_previa["precio"])


# -----------------------------------------------------------------------------
# Variable objetivo (Model Design Canvas)
# -----------------------------------------------------------------------------
def test_target_respeta_el_umbral_declarado(panel):
    """La codificación de clases debe usar el umbral de S/ 0.15 congelado."""
    assert config.UMBRAL_CLASE == 0.15
    assert set(panel["y"].unique()) <= {0, 1, 2}
    assert set(config.CLASES.values()) == {"MANTIENE", "SUBE", "BAJA"}


def test_umbral_asimetrico_coincide_con_la_matriz_de_costos():
    """P* debe ser consistente con C_FP / (C_FN + C_FP)."""
    teorico = config.COSTO_FP / (config.COSTO_FN + config.COSTO_FP)
    assert teorico == pytest.approx(0.1667, abs=1e-3)
    # El canvas congela 0.25, dentro de la banda declarada 0.17–0.25.
    assert teorico <= config.P_ESTRELLA <= 0.25


def test_umbral_bajo_aumenta_las_alertas_de_alza():
    """Bajar el umbral nunca puede reducir el número de alertas emitidas."""
    from entrenamiento_a2 import predecir_con_umbral

    clases = np.array([0, 1, 2])
    proba = np.array([[0.5, 0.3, 0.2], [0.6, 0.2, 0.2], [0.2, 0.7, 0.1]])

    alertas_bajo = (predecir_con_umbral(proba, clases, 0.15) == config.CLASE_SUBE).sum()
    alertas_alto = (predecir_con_umbral(proba, clases, 0.65) == config.CLASE_SUBE).sum()
    assert alertas_bajo >= alertas_alto


def test_costo_penaliza_mas_el_falso_negativo():
    """No advertir un alza debe costar cinco veces más que una falsa alarma."""
    from entrenamiento_a2 import costo_economico

    y = np.array([config.CLASE_SUBE, config.CLASE_MANTIENE])
    falso_negativo = costo_economico(
        y, np.array([config.CLASE_MANTIENE, config.CLASE_MANTIENE])
    )
    falso_positivo = costo_economico(y, np.array([config.CLASE_SUBE, config.CLASE_SUBE]))
    assert falso_negativo == pytest.approx(config.COSTO_FN / 2)
    assert falso_positivo == pytest.approx(config.COSTO_FP / 2)
    assert falso_negativo == pytest.approx(5 * falso_positivo)


# -----------------------------------------------------------------------------
# Calidad de datos (Fase R)
# -----------------------------------------------------------------------------
def test_precios_dentro_del_rango_plausible(panel):
    """Ningún precio saneado puede quedar fuera de S/ 5 – S/ 30."""
    assert panel["precio"].min() >= config.PRECIO_MIN_VALIDO
    assert panel["precio"].max() <= config.PRECIO_MAX_VALIDO


# -----------------------------------------------------------------------------
# Percentiles de dispersión de mercado (Osinergmin H5)
# -----------------------------------------------------------------------------
def test_percentiles_oficiales_lima(panel):
    import pipeline_inferencia
    mercado = pipeline_inferencia.percentiles_para("LIMA", panel, "REGULAR")
    assert mercado["p10_mercado"] <= mercado["p50_mediana"] <= mercado["p90_mercado"]
    assert mercado["p10_mercado"] == 13.39
    assert mercado["p90_mercado"] == 15.70
    assert mercado["brecha_dispersion"] == 2.12
    assert mercado["ahorro_por_tanqueada"] == pytest.approx(16.96)


# -----------------------------------------------------------------------------
# Componente generativo G1 (KR2)
# -----------------------------------------------------------------------------
@pytest.fixture
def payload_valido():
    return {
        "departamento": "LIMA",
        "combustible": "Gasolina Regular",
        "periodo": "Setiembre 2026 (t+1)",
        "tendencia_predicha": "SUBE",
        "probabilidad_alza": 0.74,
        "confianza": "ALTA",
        "p10_mercado": 20.69,
        "p50_mediana": 21.69,
        "p90_mercado": 23.58,
        "brecha_dispersion": 2.89,
    }


def test_payload_incompleto_es_rechazado(payload_valido):
    incompleto = {k: v for k, v in payload_valido.items() if k != "p90_mercado"}
    with pytest.raises(ValueError, match="no cumple el contrato"):
        prompts.construir_mensaje_usuario(incompleto)


def test_redaccion_deterministica_no_aluciona(payload_valido):
    texto = prompts.redactar_sin_llm(payload_valido, "bajo")
    auditoria = prompts.auditar_alucinacion_numerica(texto, payload_valido)
    assert auditoria["cumple_contrato"], auditoria["cifras_inventadas"]


def test_auditoria_detecta_precio_inventado(payload_valido):
    """Una cifra que no está en el payload debe marcarse como alucinación."""
    texto = prompts.redactar_sin_llm(payload_valido) + "\n\nTambién hay grifos a S/ 9.99."
    auditoria = prompts.auditar_alucinacion_numerica(texto, payload_valido)
    assert not auditoria["sin_alucinacion"]
    assert "9.99" in auditoria["cifras_inventadas"]


def test_confianza_baja_obliga_a_advertir(payload_valido):
    """Con confianza BAJA el texto debe incluir la advertencia literal."""
    payload = {**payload_valido, "confianza": "BAJA"}
    auditoria = prompts.auditar_alucinacion_numerica(
        prompts.redactar_sin_llm(payload), payload
    )
    assert auditoria["requiere_advertencia_incertidumbre"]
    assert auditoria["incluye_advertencia_incertidumbre"]


def test_falta_de_advertencia_rompe_el_contrato(payload_valido):
    payload = {**payload_valido, "confianza": "BAJA"}
    texto = prompts.redactar_sin_llm(payload).replace(
        prompts.ADVERTENCIA_INCERTIDUMBRE, "el mercado está algo movido"
    )
    assert not prompts.auditar_alucinacion_numerica(texto, payload)["cumple_contrato"]


def test_aviso_de_ia_siempre_presente(payload_valido):
    for tendencia in ("SUBE", "BAJA", "MANTIENE"):
        payload = {**payload_valido, "tendencia_predicha": tendencia}
        assert prompts.AVISO_IA.lower() in prompts.redactar_sin_llm(payload).lower()


def test_system_prompt_conserva_las_reglas_congeladas():
    """El System Prompt no puede perder sus cláusulas obligatorias."""
    for fragmento in (
        "PROHIBICIÓN TOTAL DE INVENTAR PRECIOS",
        "DECLARACIÓN OBLIGATORIA DE CONFIANZA",
        "NATURALEZA ESTIMATIVA Y NO GARANTÍA",
        "Banda de Precio de Referencia",
    ):
        assert fragmento in prompts.SYSTEM_PROMPT_G1
