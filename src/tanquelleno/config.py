"""
===============================================================================
PROYECTO: Lunetra IA — Fase M (Modelado)
ARCHIVO:  src/tanquelleno/config.py
DESCRIPCIÓN:
    Constantes congeladas del contrato de modelado declarado en la PC1.
    Ningún script de la Fase M debe redefinir estos valores localmente: todos
    los importan desde aquí para que el Model Design Canvas (plantilla 3) y el
    código ejecutable no puedan divergir.
===============================================================================
"""

from __future__ import annotations

import os

# -----------------------------------------------------------------------------
# 1. RUTAS DEL PROYECTO
# -----------------------------------------------------------------------------
PAQUETE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(PAQUETE_DIR, "..", ".."))

DATOS_DIR = os.path.join(PROJECT_ROOT, "datos")
MODELOS_DIR = os.path.join(PROJECT_ROOT, "modelos")
REPORTES_DIR = os.path.join(PROJECT_ROOT, "reportes")
FIGURAS_DIR = os.path.join(PROJECT_ROOT, "analisis", "figuras")

# Fuentes de datos
F_SERIE_MENSUAL = os.path.join(DATOS_DIR, "precios_combustibles_datos_crudos.csv")
F_GRIFOS_DIARIOS = os.path.join(DATOS_DIR, "precios_combustibles_anonimizados_20260301_part1.csv")

# Artefactos generados
F_DATASET_MAESTRO = os.path.join(DATOS_DIR, "dataset_maestro_mensual.parquet")
F_MACRO = os.path.join(DATOS_DIR, "macro_mensual.csv")
F_MODELO_TENDENCIA = os.path.join(MODELOS_DIR, "modelo_tendencia_a2.joblib")

SEMILLA = 42

# -----------------------------------------------------------------------------
# 2. CONTRATO DEL COMPONENTE ANALÍTICO A2 (Model Design Canvas, plantilla 3)
# -----------------------------------------------------------------------------
# Variable objetivo: tendencia del precio promedio departamental en t+1.
UMBRAL_CLASE = 0.15  # S/ por galón: |ΔP| <= 0.15 => "Se Mantiene"

CLASES = {0: "MANTIENE", 1: "SUBE", 2: "BAJA"}
CLASE_MANTIENE, CLASE_SUBE, CLASE_BAJA = 0, 1, 2

# Partición cronológica pura. Prohibido shuffle (ver plantilla 2, anti-leakage).
SPLIT_TRAIN_FIN = "2024-12-01"   # Train: ene 2020 – dic 2024
SPLIT_VAL_FIN = "2025-12-01"     # Val:   ene 2025 – dic 2025
                                 # Test:  ene 2026 – ago 2026 (ciego)

# Matriz de costos asimétricos del conductor (8 galones por tanqueada).
COSTO_FN = 4.00   # No advertir un alza: 8 gal x S/ 0.50 de salto medio (H3)
COSTO_FP = 0.80   # Falsa alarma: adelantar la carga 3-4 días
P_ESTRELLA = 0.25  # Umbral de decisión para "SUBE" = C_FP / (C_FN + C_FP)

# Metas comprometidas en los OKR (congeladas en PC1, semana 6).
META_MACRO_F1 = 0.55
META_RECALL_SUBE = 0.70
# Baseline de persistencia medido en el test ciego (ver reportes/metricas_a2.json
# y analisis/fase_m_resultados.md); no es una meta, se actualiza con lo medido.
BASELINE_MACRO_F1_DECLARADO = 0.0833

GALONES_POR_TANQUEADA = 8

# -----------------------------------------------------------------------------
# 3. CALIDAD DE DATOS
# -----------------------------------------------------------------------------
# Rango físicamente plausible para gasolinas y diésel en S/ por galón.
PRECIO_MIN_VALIDO = 5.0
PRECIO_MAX_VALIDO = 30.0

# Normalización de la nomenclatura de Osinergmin a familias continuas.
# Resuelve la transición regulatoria de 2023 (H6): "Gasohol 90 Plus" -> "Gasohol Regular".
FAMILIAS_COMBUSTIBLE = {
    "G90": "REGULAR",
    "GASOHOL 90 PLUS": "REGULAR",
    "GASOHOL REGULAR": "REGULAR",
    "GASOLINA REGULAR": "REGULAR",
    "G95": "PREMIUM",
    "GASOHOL 95 PLUS": "PREMIUM",
    "GASOHOL PREMIUM": "PREMIUM",
    "GASOLINA PREMIUM": "PREMIUM",
    "DIESEL B5 UV": "DIESEL",
    "DIESEL B5 S-50 UV": "DIESEL",
}

# -----------------------------------------------------------------------------
# 4. CONTRATO DEL COMPONENTE GENERATIVO G1
# -----------------------------------------------------------------------------
# Campos obligatorios del payload Modelo -> Lenguaje (Patrón de Conexión 1).
CAMPOS_PAYLOAD = [
    "departamento",
    "combustible",
    "periodo",
    "tendencia_predicha",
    "probabilidad_alza",
    "confianza",
    "p10_mercado",
    "p50_mediana",
    "p90_mercado",
    "brecha_dispersion",
]

# Banda de probabilidad en la que el System Prompt obliga a declarar incertidumbre.
ZONA_INCERTIDUMBRE = (0.40, 0.55)
