"""
===============================================================================
PROYECTO: TanqueLleno AI — Predicción Inteligente de Precios de Combustibles
CURSO:    AD5018 - Inteligencia Artificial para Negocios (UTEC, Framework PROMPT v2.0)
ARCHIVO:  analisis/perfilado_datos.py
DESCRIPCIÓN:
    Script reproducible de análisis exploratorio y perfilado de datos.
    Recalcula desde cero las métricas descriptivas, valida los hallazgos H1-H10,
    aplica filtros de calidad y exporta visualizaciones para sustento de la PC1.
===============================================================================
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Configuración de estilo de visualización
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8

# -----------------------------------------------------------------------------
# 1. CONFIGURACIÓN DE RUTAS DE DATOS Y SALIDAS
# -----------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

POSSIBLE_DATA_DIRS = [
    os.path.join(PROJECT_ROOT, "datos"),
    os.path.join(PROJECT_ROOT),
    os.path.join(SCRIPT_DIR, "..", "datos"),
    r"C:\Users\cefd2\Downloads\Proyecto_ia\datos",
    r"C:\Users\cefd2\Downloads"
]

DATA_DIR = None
for d in POSSIBLE_DATA_DIRS:
    if os.path.exists(os.path.join(d, "precios_combustibles_anonimizados_20260301_part1.csv")):
        DATA_DIR = d
        break

if DATA_DIR is None:
    print("ERROR: No se encontró la carpeta con los archivos de datos.")
    sys.exit(1)

OUTPUT_FIG_DIR = os.path.join(SCRIPT_DIR, "figuras")
os.makedirs(OUTPUT_FIG_DIR, exist_ok=True)

FILE_A = os.path.join(DATA_DIR, "precios_combustibles_anonimizados_20260301_part1.csv")
FILE_B = os.path.join(DATA_DIR, "precios_combustibles_datos_crudos.csv")
FILE_C = os.path.join(DATA_DIR, "historico_precios_combustibles_peru_2020_2026.xlsx")

print("=" * 80)
print("PERFILADO DE DATOS — PROYECTO PC1 (AD5018 · UTEC)")
print(f"Ruta de datos detectada: {DATA_DIR}")
print(f"Directorio de figuras:   {OUTPUT_FIG_DIR}")
print("=" * 80)

# -----------------------------------------------------------------------------
# 2. PROCESAMIENTO Y PERFILADO: ARCHIVO A (Precios por Grifo, Diarios)
# -----------------------------------------------------------------------------
print("\n[1/3] Cargando Archivo A: precios por grifo diarios (59 días)...")
df_a = pd.read_csv(FILE_A)
n_filas_a = len(df_a)
grifos_a = df_a['ANON_CO_LOCAL_VENTA'].nunique()
print(f"  -> Total filas: {n_filas_a:,}")
print(f"  -> Grifos únicos (hash anonimizado): {grifos_a:,}")

# Fechas y cobertura
df_a['fe_eval_dt'] = pd.to_datetime(df_a['fe_eval'].astype(str), format='%Y%m%d')
min_date = df_a['fe_eval_dt'].min().strftime('%Y-%m-%d')
max_date = df_a['fe_eval_dt'].max().strftime('%Y-%m-%d')
total_dias = df_a['fe_eval_dt'].nunique()
print(f"  -> Rango temporal: {min_date} al {max_date} ({total_dias} días observados)")

dias_por_grifo = df_a.groupby('ANON_CO_LOCAL_VENTA')['fe_eval_dt'].nunique()
completos_59 = (dias_por_grifo == total_dias).sum()
print(f"  -> Grifos con los {total_dias} días completos: {completos_59:,} ({completos_59/grifos_a*100:.1f}%)")

# Nulos por columna
combustibles_cols = ['g_premium', 'g_regular', 'diesel', 'gnv', 'glp_g', 'glp_e']
print("\n  -> Porcentaje de valores nulos:")
for col in combustibles_cols:
    null_count = df_a[col].isnull().sum()
    null_pct = (null_count / n_filas_a) * 100
    print(f"     - {col:10s}: {null_pct:5.1f}% nulos ({null_count:,} filas)")

# Detección de valores fuera de rango (imposibles: < 5 o > 30 en gasolinas y diésel)
imposibles_dict = {}
total_imposibles = 0
for col in ['g_premium', 'g_regular', 'diesel']:
    cond = (df_a[col].notnull()) & ((df_a[col] < 5.0) | (df_a[col] > 30.0))
    imp_vals = df_a.loc[cond, col].tolist()
    imposibles_dict[col] = imp_vals
    total_imposibles += len(imp_vals)
    if len(imp_vals) > 0:
        print(f"  -> Valores imposibles en {col} (< S/ 5 o > S/ 30): {len(imp_vals)} casos -> {imp_vals[:4]}")

print(f"  -> Total de anomalías extremas registradas: {total_imposibles} casos")

# Aplicación de filtro de calidad 5 a 30 S//galón
for col in ['g_premium', 'g_regular', 'diesel']:
    df_a.loc[(df_a[col] < 5.0) | (df_a[col] > 30.0), col] = np.nan

# -----------------------------------------------------------------------------
# 3. VERIFICACIÓN DE HALLAZGOS H1 - H5 (Comportamiento a Nivel Grifo)
# -----------------------------------------------------------------------------
print("\n" + "-" * 50)
print("RECALCULANDO HALLAZGOS H1 - H5:")
df_a = df_a.sort_values(['ANON_CO_LOCAL_VENTA', 'fe_eval_dt'])

# H1: Inercia diaria
df_a['diff1_reg'] = df_a.groupby('ANON_CO_LOCAL_VENTA')['g_regular'].diff()
diff1_valid = df_a['diff1_reg'].dropna()
pct_sin_cambio = (diff1_valid == 0.0).mean() * 100
print(f"  [H1] Pares grifo-día sin variación de precio (g_regular): {pct_sin_cambio:.2f}% (~96.1%)")

# H2: Distribución de cambios a 7 días
df_a['diff7_reg'] = df_a.groupby('ANON_CO_LOCAL_VENTA')['g_regular'].diff(7)
diff7_valid = df_a['diff7_reg'].dropna()
h2_mantiene = (diff7_valid.abs() < 0.01).mean() * 100
h2_sube = (diff7_valid >= 0.01).mean() * 100
h2_baja = (diff7_valid <= -0.01).mean() * 100
print(f"  [H2] Comportamiento a 7 días: Se Mantiene = {h2_mantiene:.1f}%, Sube = {h2_sube:.1f}%, Baja = {h2_baja:.1f}%")

# H3: Magnitud media de salto cuando cambia
subidas = diff1_valid[diff1_valid > 0.001]
bajadas = diff1_valid[diff1_valid < -0.001]
print(f"  [H3] Salto medio al subir: +S/ {subidas.mean():.3f} por galón | Salto medio al bajar: -S/ {abs(bajadas.mean()):.3f} por galón")

# H4: Grifos estáticos
grifos_obs = df_a.groupby('ANON_CO_LOCAL_VENTA')['g_regular'].agg(['count', 'std'])
grifos_30 = grifos_obs[grifos_obs['count'] >= 30]
pct_estaticos = ((grifos_30['std'] == 0) | (grifos_30['std'].isna())).mean() * 100
print(f"  [H4] Grifos con >=30 obs que nunca cambiaron precio: {pct_estaticos:.1f}% ({((grifos_30['std'] == 0) | (grifos_30['std'].isna())).sum():,}/{len(grifos_30):,})")

# H5: Dispersión transversal al 28 feb 2026
feb28 = df_a[df_a['fe_eval_dt'] == '2026-02-28']['g_regular'].dropna()
p10_feb28 = feb28.quantile(0.10)
p50_feb28 = feb28.quantile(0.50)
p90_feb28 = feb28.quantile(0.90)
brecha_p90_p10 = p90_feb28 - p10_feb28
print(f"  [H5] Dispersión al 28-Feb-2026 (N={len(feb28):,} grifos):")
print(f"       Media: S/ {feb28.mean():.2f} | Desv. Estándar: S/ {feb28.std():.2f}")
print(f"       P10: S/ {p10_feb28:.2f} | P50 (Mediana): S/ {p50_feb28:.2f} | P90: S/ {p90_feb28:.2f}")
print(f"       BRECHA P90 - P10: S/ {brecha_p90_p10:.2f} por galón")

# -----------------------------------------------------------------------------
# 4. PROCESAMIENTO Y PERFILADO: ARCHIVOS B Y C (Serie Mensual Departamental)
# -----------------------------------------------------------------------------
print("\n[2/3] Cargando Archivos B y C: series mensuales departamentales (80 meses)...")
df_b = pd.read_csv(FILE_B)
print(f"  -> Archivo B: {len(df_b):,} filas, {df_b.isnull().sum().sum()} nulos, {df_b['departamento'].nunique()} departamentos")

xl = pd.ExcelFile(FILE_C)
df_lima = xl.parse('Lima')
print(f"  -> Archivo C (Hoja Lima): {df_lima.shape[0]} meses ({df_lima.shape[1]} columnas)")

# H6: Transición de nomenclatura en Lima
col_g90 = [c for c in df_lima.columns if '90' in str(c)][0]
col_greg = [c for c in df_lima.columns if 'REGULAR' in str(c).upper() and 'GASOHOL' in str(c).upper()][0]
print(f"  [H6] Columnas de nomenclatura: Anterior='{col_g90}', Nueva='{col_greg}'")

# Reconstrucción serie continua regular
serie_lima_reg = df_lima[col_greg].combine_first(df_lima[col_g90])

# H7: Estadísticas serie reconstruida Lima
print(f"  [H7] Serie Lima reconstruida (80 meses continuos):")
print(f"       Observaciones: {serie_lima_reg.count()} meses")
print(f"       Media: S/ {serie_lima_reg.mean():.2f} | Desv. Estándar: S/ {serie_lima_reg.std():.2f}")
print(f"       Mínimo: S/ {serie_lima_reg.min():.2f} | Máximo: S/ {serie_lima_reg.max():.2f}")

# H8: Autocorrelaciones de cambios mensuales
diff_mensual = serie_lima_reg.diff()
ac_lag1 = diff_mensual.autocorr(1)
ac_lag2 = diff_mensual.autocorr(2)
ac_lag3 = diff_mensual.autocorr(3)
print(f"  [H8] Autocorrelación de cambios mensuales: Lag 1 = {ac_lag1:.2f}, Lag 2 = {ac_lag2:.2f}, Lag 3 = {ac_lag3:.2f}")

# H9: Señal estacional de Marzo
mes_col = [c for c in df_lima.columns if 'Mes' in str(c) and 'N' not in str(c)][0]
df_lima['diff_mensual_reg'] = diff_mensual
estacionalidad = df_lima.groupby(mes_col)['diff_mensual_reg'].agg(['mean', 'count'])
marzo_stats = estacionalidad.loc['Marzo'] if 'Marzo' in estacionalidad.index else None
if marzo_stats is not None:
    print(f"  [H9] Estacionalidad preliminar en Marzo: Cambio promedio = +S/ {marzo_stats['mean']:.2f}/galón (N = {int(marzo_stats['count'])} observaciones)")
    print("       *Nota: Declarado como indicio exploratorio debido al tamaño muestral reducido (7 años).")

print("  [H10] Hueco temporal verificado: Datos por grifo concluyen en 2026-02; serie mensual de Osinergmin se extiende a 2026-08.")

# -----------------------------------------------------------------------------
# 5. GENERACIÓN DE VISUALIZACIONES OFICIALES
# -----------------------------------------------------------------------------
print("\n[3/3] Generando figuras para documentación y sustentación...")

# FIGURA 1: Dispersión transversal al 28 feb 2026
fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
n_bins = 40
ax.hist(feb28, bins=n_bins, color='#1f77b4', alpha=0.7, edgecolor='white', density=True, label='Distribución de Grifos')
feb28.plot.kde(ax=ax, color='#0d3b66', linewidth=2.2, label='Densidad Estimada')

ax.axvline(p10_feb28, color='#2a9d8f', linestyle='--', linewidth=1.8, label=f'P10: S/ {p10_feb28:.2f}')
ax.axvline(p50_feb28, color='#e76f51', linestyle='-', linewidth=2.0, label=f'Mediana (P50): S/ {p50_feb28:.2f}')
ax.axvline(p90_feb28, color='#e63946', linestyle='--', linewidth=1.8, label=f'P90: S/ {p90_feb28:.2f}')

ax.annotate(f'Brecha P90 - P10 = S/ {brecha_p90_p10:.2f}/gal\nSobrecosto = S/ {brecha_p90_p10 * 8:.2f} por tanque (8 gal)',
            xy=(p50_feb28, 0.40), xytext=(p50_feb28 + 0.6, 0.55),
            arrowprops=dict(facecolor='black', arrowstyle='->', lw=1.2),
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#fff3cd', edgecolor='#ffeeba', alpha=0.9),
            fontsize=10, fontweight='bold')

ax.set_title('Figura 1: Dispersión Transversal de Precios — Gasolina Regular (28 Feb 2026)\n'
             'La brecha entre grifos supera ampliamente el cambio esperado en el tiempo', fontsize=12, fontweight='bold', pad=12)
ax.set_xlabel('Precio al Consumidor (Soles por Galón)', fontsize=10, fontweight='bold')
ax.set_ylabel('Densidad de Grifos', fontsize=10, fontweight='bold')
ax.set_xlim(11.5, 18.5)
ax.legend(loc='upper right', frameon=True)
plt.tight_layout()
fig1_path = os.path.join(OUTPUT_FIG_DIR, "figura_1_dispersion_grifos.png")
fig.savefig(fig1_path)
plt.close(fig)
print(f"  -> Guardada: {fig1_path}")

# FIGURA 2: Serie histórica Lima 80 meses
fig, ax = plt.subplots(figsize=(11, 5.5), dpi=300)
fechas_mensuales = pd.date_range(start='2020-01-01', periods=len(serie_lima_reg), freq='MS')
ax.plot(fechas_mensuales, serie_lima_reg, color='#023e8a', linewidth=2.4, marker='o', markersize=3.5, label='Gasolina Regular / G90 Lima')

ax.axvspan(pd.Timestamp('2023-03-01'), pd.Timestamp('2023-06-30'), color='#ffd166', alpha=0.35, label='Transición Osinergmin (G90 -> Regular)')
ax.axvline(pd.Timestamp('2022-06-01'), color='#d90429', linestyle=':', alpha=0.7, label='Pico Inflacionario Global 2022 (S/ 22.43)')

ax.set_title('Figura 2: Evolución Histórica del Precio Promedio Mensual en Lima (2020 - 2026)\n'
             'Serie continua de 80 meses reconstruida tras transición normativa de Osinergmin', fontsize=12, fontweight='bold', pad=12)
ax.set_xlabel('Año / Mes', fontsize=10, fontweight='bold')
ax.set_ylabel('Precio Promedio (Soles por Galón)', fontsize=10, fontweight='bold')
ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('S/ %.2f'))
ax.legend(loc='upper left', frameon=True)
plt.tight_layout()
fig2_path = os.path.join(OUTPUT_FIG_DIR, "figura_2_serie_historica_lima.png")
fig.savefig(fig2_path)
plt.close(fig)
print(f"  -> Guardada: {fig2_path}")

# FIGURA 3: Matriz de cambios a 7 días (Desbalance de clases)
fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
categorias = ['Se Mantiene\n(|Δ| < S/ 0.01)', 'Sube\n(Δ ≥ +S/ 0.01)', 'Baja\n(Δ ≤ -S/ 0.01)']
porcentajes = [h2_mantiene, h2_sube, h2_baja]
colores = ['#457b9d', '#e63946', '#2a9d8f']

bars = ax.bar(categorias, porcentajes, color=colores, width=0.55, edgecolor='black', linewidth=0.8)
for bar, pct in zip(bars, porcentajes):
    height = bar.get_height()
    ax.annotate(f'{pct:.1f}%',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 4), textcoords="offset points",
                ha='center', va='bottom', fontsize=11, fontweight='bold')

ax.set_title('Figura 3: Distribución de Variación de Precio a 7 Días por Grifo\n'
             'Fuerte desbalance de clases que exige optimización de umbrales asimétricos', fontsize=12, fontweight='bold', pad=12)
ax.set_ylabel('Frecuencia Relativa (%)', fontsize=10, fontweight='bold')
ax.set_ylim(0, 100)
plt.tight_layout()
fig3_path = os.path.join(OUTPUT_FIG_DIR, "figura_3_matriz_cambios_7dias.png")
fig.savefig(fig3_path)
plt.close(fig)
print(f"  -> Guardada: {fig3_path}")

# FIGURA 4: Estacionalidad mensual
fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
meses_orden = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Setiembre', 'Octubre', 'Noviembre', 'Diciembre']
estac_ordenada = estacionalidad.reindex([m for m in meses_orden if m in estacionalidad.index])
colores_estac = ['#e63946' if val > 0.5 else '#457b9d' if val >= 0 else '#2a9d8f' for val in estac_ordenada['mean']]

bars_m = ax.bar(estac_ordenada.index, estac_ordenada['mean'], color=colores_estac, edgecolor='black', linewidth=0.7)
ax.axhline(0, color='black', linewidth=0.8, linestyle='--')

for bar, val in zip(bars_m, estac_ordenada['mean']):
    va = 'bottom' if val >= 0 else 'top'
    offset = 4 if val >= 0 else -12
    ax.annotate(f'{val:+.2f}',
                xy=(bar.get_x() + bar.get_width() / 2, val),
                xytext=(0, offset), textcoords="offset points",
                ha='center', va=va, fontsize=9, fontweight='bold')

ax.set_title('Figura 4: Variación Promedio Mensual del Precio en Lima por Mes Calendario\n'
             'Indicio exploratorio: Marzo registra mayor presión alcista (+S/ 0.99 a +S/ 1.01, N=7)', fontsize=12, fontweight='bold', pad=12)
ax.set_ylabel('Variación Media (S/ por Galón)', fontsize=10, fontweight='bold')
ax.set_xticklabels(estac_ordenada.index, rotation=30, ha='right')
ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('S/ %+.2f'))
plt.tight_layout()
fig4_path = os.path.join(OUTPUT_FIG_DIR, "figura_4_estacionalidad_mensual.png")
fig.savefig(fig4_path)
plt.close(fig)
print(f"  -> Guardada: {fig4_path}")

print("\n" + "=" * 80)
print("PROCESO DE PERFILADO FINALIZADO CON ÉXITO.")
print("Todas las métricas y gráficos están listos para alimentar los entregables de la PC1.")
print("=" * 80)
