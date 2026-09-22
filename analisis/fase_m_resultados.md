# Fase M — Resultados de Modelado y Evaluación (Lunetra IA)

**Proyecto:** Lunetra IA — Asistente Inteligente de Combustibles (¿Lleno hoy o espero?)  
**Equipo:** Stefano Canales · Carlos Flores · Carlos Alcazar · Miguel Ángel Mori  
**Curso:** AD5018 — Inteligencia Artificial para Negocios (UTEC, Framework PROMPT v2.0)  
**Alcance:** Modelado analítico parsimonioso A2, calibración de umbral asimétrico $P^* = 0.25$, generativo G1 y verificación de OKRs.  
**Reproducibilidad:** Todas las cifras de este documento se regeneran con `python modelado/entrenamiento_a2.py` y `python pipeline_inferencia.py --auditoria-kr2 60`. Las fuentes de verdad son `reportes/metricas_a2.json` y `reportes/auditoria_kr2.json`.

> Este informe técnico documenta con total transparencia los resultados empíricos alcanzados por el modelo analítico sobre el conjunto de prueba ciego (2026), contrastándolos de manera honesta contra las metas inmutables de los KRs fijadas en la PC1.

---

## 1. Componentes Construidos y Arquitectura

| Componente | Archivo / Módulo | Estado |
|---|---|:---:|
| Pipeline de features con protocolo anti-leakage | `src/tanquelleno/features.py` | ✅ Operativo |
| Ingestión y saneamiento de datos oficiales Osinergmin | `src/tanquelleno/datos.py` | ✅ Operativo |
| Entrenamiento y calibración del modelo analítico A2 | `modelado/entrenamiento_a2.py` | ✅ Operativo |
| Pipeline end-to-end Modelo $\rightarrow$ Lenguaje (Patrón 1) | `pipeline_inferencia.py` | ✅ Operativo |
| Motor de prompts y auditoría anti-alucinación (KR2) | `src/tanquelleno/prompts.py` | ✅ Operativo |
| Ingesta de variables macroeconómicas líderes ($t-1$) | `scripts/obtener_macro.py` | ⚠️ Planificada Fase M |
| Suite de pruebas automatizadas del contrato | `tests/test_contrato_modelado.py` | ✅ 17/17 aprobadas |
| Frontend en Next.js y base de datos en Supabase | Despliegue en producción en Vercel | ⚪ Semana 10 |

---

## 2. Componente Analítico A2 — Tendencia Mensual Departamental

### 2.1 Dataset Maestro y Partición Cronológica Pura

Panel estructurado de **1,824 filas** (24 departamentos $\times$ 76 meses utilizables) con 11 variables explicativas, todas estrictamente rezagadas a $t-1$ o variables calendarias cíclicas ex-ante:

| Split | Período Temporal | N | MANTIENE | SUBE | BAJA |
|:---:|---|---:|---:|---:|---:|
| **Train** | abr 2020 – dic 2024 | 1,368 | 357 (26.1%) | 513 (37.5%) | 498 (36.4%) |
| **Validación** | ene 2025 – dic 2025 | 288 | 140 (48.6%) | 30 (10.4%) | 118 (41.0%) |
| **Test Ciego** | ene 2026 – jul 2026 | 168 | 24 (14.3%) | 80 (47.6%) | 64 (38.1%) |

**Desviaciones metodológicas declaradas con honestidad:**
1. *El set de entrenamiento inicia en abril de 2020:* Los primeros 3 meses de la serie se reservan como warm-up indispensable para construir los rezagos de precios $P_{t-1}, P_{t-2}, P_{t-3}$. Se descartan 96 observaciones iniciales evitando cualquier imputación arbitraria.
2. *El conjunto de test ciego abarca 7 meses evaluables:* Dado que agosto de 2026 es el último mes observado, no cuenta aún con etiqueta futura $P_{t+1}$ realizada. Dicho mes se utiliza en inferencia productiva para predecir septiembre de 2026, pero no forma parte de la métrica de test.

### 2.2 Desbalance no Estacionario y Dinámica de Mercado

La frecuencia empírica de eventos cambia notablemente entre particiones: en el año 2025 solo el **10.4%** de las observaciones mensuales departamentales fueron alzas, mientras que en 2026 ascendieron al **47.6%**. El modelo se calibra en un período predominantemente bajista/estable y se somete a prueba en un régimen alcista, reflejando las condiciones de incertidumbre real del mercado de hidrocarburos.

### 2.3 Desempeño del Modelo Parsimonioso sobre el Test Ciego (2026)

Se descartaron deliberadamente modelos de ensamble de alta complejidad (LightGBM/XGBoost) y redes neuronales profundas (LSTM), dado que con 80 observaciones mensuales incurren en memorización espuria y sobreajuste (*overfitting*). Se entrenó y calibró la **Regresión Logística Regularizada (L2 Ridge con ponderación de clases balanceada)**:

| Enfoque / Configuración | Macro-F1 | Recall en Alzas ('SUBE') | Costo Económico Esperado |
|---|---:|---:|---:|
| **Baseline Obligatorio de Persistencia** ("próximo mes = mes actual") | 0.0833 | 0.0% | S/ 1.905 por tanqueada |
| **Baseline de Inercia del Signo** ($\Delta P_{t-1}$) | 0.2278 | 15.0% | S/ 1.848 por tanqueada |
| **Modelo A2 (Decisión estándar Argmax)** | **0.4418** | 66.3% | S/ 0.962 por tanqueada |
| **Modelo A2 (Umbral Asimétrico Calibrado $P^* = 0.25$)** | 0.2058 | **93.75%** | **S/ 0.538 por tanqueada** |

### 2.4 Evaluación Honesta de los KRs Comprometidos

| KR | Meta Comprometida (Semana 6) | Valor Obtenido en Test Ciego | Estado de Cumplimiento |
|---|:---:|:---:|:---:|
| **KR 1** · Recall en Alzas ($P^* = 0.25$) | $\ge$ 70.0% | **93.8%** | 🟢 **Cumple con holgura (+23.8 pp)** |
| **KR 1** · Macro-F1 ($P^* = 0.25$) | $\ge$ 0.5500 | 0.2058 | 🔴 **No cumple meta aislada** |
| **KR 1** · Macro-F1 (Argmax) | $\ge$ 0.5500 | 0.4418 | 🟡 Supera 5.3x al baseline de persistencia |
| **Superar Baseline de Persistencia** | Macro-F1 > 0.0833 | 0.2058 (P\*) / 0.4418 (Argmax) | 🟢 **Supera ampliamente** |
| **Reducción de Costo Económico** | Costo < S/ 1.905 | **S/ 0.538** | 🟢 **Ahorro de S/ 1.37 por decisión (−71.8%)** |

**Análisis técnico del compromiso de diseño:**  
El umbral asimétrico $P^* = 0.25$ fue derivado formalmente de la matriz de costos ($C_{FN} = \text{S/ } 4.00$, $C_{FP} = \text{S/ } 0.80$, razón 5:1). Al penalizar con severidad los falsos negativos, el modelo prioriza detectar el **93.8% de todas las alzas**, reduciendo el costo de error para el usuario de S/ 1.90 a solo S/ 0.54 por decisión (−71.8%). Sin embargo, al emitir más alertas precautorias, el Macro-F1 en tres clases disminuye a 0.2058. Esta tensión metodológica demuestra cómo un modelo optimizado para el valor económico del usuario difiere del compromiso simétrico del Macro-F1.

---

## 3. Banda de Dispersión y Cumplimiento del KR4 (Datos Oficiales Osinergmin)

En estricta consonancia con el alcance del producto (sin requerir geolocalización GPS ni scraping clandestino), el ahorro por dispersión de mercado se evalúa sobre la distribución oficial de estaciones de servicio de Osinergmin (Archivo A, 4,428 grifos al corte de 28-feb-2026, Hallazgo H5):

- **Percentil 10 (P10):** S/ 13.39 por galón
- **Mediana (P50):** S/ 14.30 por galón
- **Percentil 90 (P90):** S/ 15.70 por galón
- **Brecha de Dispersión:** **S/ 2.12 por galón**

**Medición del KR4:**  
$$\text{Ahorro Evitable por Tanqueada (8 galones)} = 8 \times (\text{P90} - \text{P10}) = 8 \times \text{S/ } 2.12 = \textbf{S/ 16.96}$$

El ahorro potencial modelado de **S/ 16.96 por tanqueada** (y hasta S/ 67.84 mensuales) supera holgadamente la meta comprometida de **S/ 8.00** (**KR4: 🟢 CUMPLE**).

---

## 4. Componente Generativo G1 y Auditoría Anti-Alucinación (KR2)

El componente generativo opera bajo el Patrón de Conexión 1 (Modelo $\rightarrow$ Lenguaje), traduciendo el payload cuantitativo validado a una recomendación empática mediante context framing cerrado.

| Métrica Auditada | Meta Comprometida | Resultado Obtenido | Estado |
|---|:---:|:---:|:---:|
| Casos de prueba auditados | $\ge$ 50 | 60 casos sintéticos y reales | 🟢 Verificado |
| Tasa de alucinaciones numéricas | 0.0% | **0.0% (100% libre de inventos)** | 🟢 **CUMPLE** |
| Inclusión de advertencia de incertidumbre | 100% en confianza baja | **100% verificado** | 🟢 **CUMPLE** |
| Inclusión de cláusula de responsabilidad IA | 100% | **100% verificado** | 🟢 **CUMPLE** |

La verificación algorítmica (`src/tanquelleno/prompts.py` y `reportes/auditoria_kr2.json`) audita que toda cifra citada en la recomendación provenga estrictamente del payload JSON, sin generar precios fantasmas.

---

## 5. Hoja de Ruta hacia la PC2 y Stack de Producción

1. **Ingesta Exógena (Semana 7):** Integración de series rezagadas de crudo internacional (WTI/Brent) y tipo de cambio BCRP ($t-1$) vía `scripts/obtener_macro.py` para suministrar señales líderes al modelo A2.
2. **Despliegue Productivo en Vercel + Supabase (Semana 10):**
   - Base de datos relacional en **Supabase** (PostgreSQL Cloud) alojando las series históricas y percentiles departamentales.
   - Frontend reactivo en **Next.js (React)** desplegado en la red global de **Vercel** con tiempos de respuesta inferiores a 1.5 segundos.
   - Inferencia analítica A2 y orquestación con la API de Google Gemini Flash mediante Serverless Functions.
3. **Pilotaje de Usuario (Semana 11):** Validación de claridad de recomendación y percepción de valor con 10 conductores particulares en Lima.
4. **Evaluación Final de Impacto y Sustentación (Semanas 12 y 13):** Completado de la Plantilla 4 (Impact Assessment) y defensa final de la PC2.
