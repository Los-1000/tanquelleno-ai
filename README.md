# Lunetra IA — Asistente Inteligente para la Optimización del Gasto en Combustibles

Repositorio oficial del proyecto desarrollado para el curso **AD5018 — Inteligencia Artificial para Negocios** en la **Universidad de Ingeniería y Tecnología (UTEC)**, bajo el marco metodológico **PROMPT v2.0**.

> **Nota para la evaluación:** Este es el **único repositorio para todo el semestre académico**. Para la entrega final de la PC2 (Semanas 12–13) se actualizarán estos entregables y se integrarán los nuevos artefactos de modelado e impacto; no se creará un repositorio separado.

---

## 1. Carátula del Proyecto

- **Nombre del MVP:** Lunetra IA
- **Pregunta Central:** "¿Lleno hoy o espero?"
- **Curso:** AD5018 — Inteligencia Artificial para Negocios
- **Universidad:** Universidad de Ingeniería y Tecnología (UTEC)
- **Departamento:** Administración & Negocios Digitales · Malla 2024 — Ciclo 9
- **Evaluación:** Práctica Calificada 1 (PC1) — Fases P, R y O (Semana 6)
- **Integrantes del Equipo:**
  - Stefano Canales
  - Carlos Flores
  - Carlos Alcazar
  - Miguel Ángel Mori
- **Usuario GitHub / Organización:** [Los-1000](https://github.com/Los-1000)
- **Repositorio Oficial:** [tanquelleno-ai](https://github.com/Los-1000/tanquelleno-ai)
- **Fecha de Entrega / Sustentación:** 19 de septiembre de 2026 · Ciclo 2026-II

---

## 2. Descripción del Proyecto

Lunetra IA responde a una sola pregunta, respondida bien: **"¿Lleno hoy o espero?"**. 

En Lima Metropolitana, los conductores particulares que usan su auto a diario enfrentan una brecha de precios de hasta S/ 2.12 por galón el mismo día entre grifos (S/ 17 por tanqueada, S/ 814 al año). 

Lunetra IA combina un **componente analítico de Machine Learning (Nivel A2 — Eje de Ambición)** basado en **Regresión Logística Regularizada (L2 Ridge / ElasticNet) con Calibración Sigmoide (Platt Scaling)** evaluada formalmente frente al **Baseline Obligatorio de Persistencia** (descartando modelos sobreparametrizados de ensamble o redes profundas inviables para una serie corta de 80 meses), optimizando un umbral asimétrico de decisión ($P^* = 0.25$, porque no avisar una subida cuesta 5 veces más que una falsa alarma), con un **componente generativo (Nivel G1)** que responde en una frase clara y empática: **"Carga hoy"** o **"Puedes esperar"**, junto con la banda de precio justo de referencia, sin alucinaciones numéricas. Detrás hay seis años de datos; adelante, una frase.

### Stack Tecnológico de Producción
- **Frontend & Edge Functions:** Next.js (React) alojado en la red global de **Vercel** (latencia < 1.5s).
- **Base de Datos & Almacenamiento:** **Supabase** (PostgreSQL Cloud administrado con PostgREST).
- **Modelado Analítico (A2):** Python 3.12 / Scikit-Learn (Regresión Logística Regularizada con Calibración Platt).
- **Motor Generativo (G1):** Google Gemini Flash API con System Prompt blindado y contexto cerrado.

---

## 3. Estado del Proyecto (Semana 6)

| Fase Metodológica (PROMPT v2.0) | Semanas | Estado | Entregables Clave |
|---|:---:|:---:|---|
| **Fase P (Problem Statement Canvas)** | S1 – S3 | 🟢 **Cerrada** | Canvas de problema sin tecnología, cuantificación de sobrecosto (H5), filtro de IA y componentes A2 + G1. |
| **Fase R (Data Readiness Assessment)** | S4 – S5 | 🟢 **Cerrada** | Inventario oficial, semáforo transparente, protocolo anti-leakage y saneamiento de anomalías (16 valores fuera de rango). |
| **Fase M (Modelado & Despliegue)** | S7 – S11 | 🟡 **En curso** | Ingestión macro ($t-1$), entrenamiento de Regresión Logística Regularizada calibrada, pipeline de inferencia end-to-end con auditoría KR2 (0% alucinaciones) y **despliegue en Vercel + Supabase en Semana 10**. Resultados en [`analisis/fase_m_resultados.md`](analisis/fase_m_resultados.md). |
| **Fase P2 (Pilotaje e Impacto)** | S12 | ⚪ *Pendiente* | Evaluación sobre test set ciego (2026), medición de KRs y elaboración de la Plantilla 4. |
| **Fase T (Transferencia & Cierre PC2)** | S13 | ⚪ *Pendiente* | Manual de entrega técnica, video demo y sustentación final ante jurado. |

---

## 4. Estructura del Repositorio e Índice de Entregables

```
tanquelleno-ai/
├── README.md                               <- Carátula, índice general y estado del proyecto
├── resumen_ejecutivo.md                    <- Síntesis ejecutiva de P + R + O en una sola página
├── cronograma.md                           <- Plan de trabajo detallado de Semana 7 a 13
├── presentacion_pc1_guion.md               <- Guion slide por slide de las 13 láminas para la exposición
├── presentacion_pc1.pdf                    <- Deck oficial de 13 láminas en PDF compilado y listo para sustentar
├── Lunetra IA - V3 completo.pptx           <- Presentación original de diapositivas en PowerPoint
├── Lunetra IA.html                         <- Presentación interactiva animada en HTML
├── requirements.txt                        <- [Fase M] Dependencias de Python
├── Makefile                                <- [Fase M] Atajos reproducibles (make ayuda)
├── pipeline_inferencia.py                  <- [Fase M] Pipeline end-to-end: modelo -> payload -> recomendación
├── plantillas/
│   ├── plantilla_1_problem_statement.md    <- Fase P: Problem Statement Canvas y filtro de IA
│   ├── plantilla_2_data_readiness.md       <- Fase R: Inventario, Data Readiness y protocolo de calidad
│   └── plantilla_3_ai_product_canvas.md    <- Fase O: AI Product Canvas, System Prompt, Arquitectura y OKRs
├── src/tanquelleno/                        <- [Fase M] Paquete reutilizable del proyecto
│   ├── config.py                           <- Constantes congeladas del contrato (umbrales, costos, splits)
│   ├── datos.py                            <- Carga y saneamiento de todas las fuentes
│   ├── features.py                         <- Dataset maestro, target y auditoría anti-leakage
│   └── prompts.py                          <- System Prompt G1 y auditoría anti-alucinación
├── modelado/                               <- [Fase M] Scripts de entrenamiento
│   └── entrenamiento_a2.py                 <- Componente analítico A2 (tendencia mensual departamental)
├── scripts/
│   └── obtener_macro.py                    <- [Fase M] Ingesta de WTI, Brent y tipo de cambio
├── tests/
│   └── test_contrato_modelado.py           <- [Fase M] 17 pruebas del contrato metodológico
├── analisis/
│   ├── perfilado_datos.py                  <- Script reproducible que recalcula métricas y genera figuras
│   ├── hallazgos.md                        <- Documentación exhaustiva de los hallazgos empíricos H1 a H10
│   ├── fase_m_resultados.md                <- [Fase M] Resultados de modelado y estado real de los KR
│   └── figuras/                            <- Gráficos oficiales generados para el sustento
│       ├── figura_1_dispersion_grifos.png  <- Dispersión transversal P10-P90 (Brecha S/ 2.12/galón)
│       ├── figura_2_serie_historica_lima.png <- Serie histórica de 80 meses Osinergmin reconstruida
│       ├── figura_3_matriz_cambios_7dias.png <- Distribución de variación semanal y desbalance
│       └── figura_4_estacionalidad_mensual.png <- Indicio estacional exploratorio en marzo
├── datos/
│   ├── README_datos.md                     <- Catálogo de fuentes, orígenes Osinergmin y políticas
│   ├── historico_precios_combustibles_peru_2020_2026.xlsx <- Versión Excel consolidada (4 hojas)
│   ├── precios_combustibles_anonimizados_20260301_part1.csv <- Registro diario por grifo (497,156 filas)
│   └── precios_combustibles_datos_crudos.csv <- Serie histórica mensual departamental (11,227 filas)
├── modelos/                                <- [Fase M] Artefactos entrenados (.joblib, no versionados)
├── reportes/                               <- [Fase M] Métricas y auditorías en JSON
└── .gitignore                              <- Filtros estándar para Python, cachés y archivos temporales
```

### Tabla de Navegación Rápida con Enlaces Relativos

| Entregable Oficial | Fase / Componente | Descripción del Contenido |
|---|:---:|---|
| [`README.md`](README.md) | General | Portada del equipo, estado del proyecto e índice de navegación. |
| [`resumen_ejecutivo.md`](resumen_ejecutivo.md) | Síntesis | Resumen ejecutivo de una página integrando Fases P, R y O. |
| [`cronograma.md`](cronograma.md) | Planificación | Plan semana por semana de S7 a S13 (Despliegue en Semana 10). |
| [`presentacion_pc1_guion.md`](presentacion_pc1_guion.md) | Sustentación | Guion slide por slide de 10 minutos (13 láminas) para la exposición presencial. |
| [`presentacion_pc1.pdf`](presentacion_pc1.pdf) | Sustentación | Deck oficial de 13 láminas en formato PDF compilado y listo para sustentar. |
| [`Lunetra IA - V3 completo.pptx`](Lunetra%20IA%20-%20V3%20completo.pptx) | Sustentación | Archivo editable de presentación en formato Microsoft PowerPoint. |
| [`Lunetra IA.html`](Lunetra%20IA.html) | Sustentación | Presentación interactiva y animada en formato web autónomo. |
| [`plantillas/plantilla_1_problem_statement.md`](plantillas/plantilla_1_problem_statement.md) | Fase P | Problem Statement Canvas, consecuencia medible y filtro de IA. |
| [`plantillas/plantilla_2_data_readiness.md`](plantillas/plantilla_2_data_readiness.md) | Fase R | Inventario, semáforo transparente, prevención de data leakage y calidad. |
| [`plantillas/plantilla_3_ai_product_canvas.md`](plantillas/plantilla_3_ai_product_canvas.md) | Fase O | AI Product Canvas, diagrama Mermaid, System Prompt, Model Canvas y OKRs. |
| [`analisis/perfilado_datos.py`](analisis/perfilado_datos.py) | Código Analítico | Script reproducible en Python que recalcula métricas y genera figuras. |
| [`analisis/hallazgos.md`](analisis/hallazgos.md) | Evidencia | Análisis profundo de los 10 hallazgos empíricos verificados H1 a H10. |
| [`analisis/figuras/figura_1_dispersion_grifos.png`](analisis/figuras/figura_1_dispersion_grifos.png) | Visualización | Gráfico de densidad y percentiles P10-P90 al 28 de febrero de 2026. |
| [`analisis/figuras/figura_2_serie_historica_lima.png`](analisis/figuras/figura_2_serie_historica_lima.png) | Visualización | Serie histórica mensual de 80 meses Osinergmin (2020–2026). |
| [`analisis/figuras/figura_3_matriz_cambios_7dias.png`](analisis/figuras/figura_3_matriz_cambios_7dias.png) | Visualización | Distribución de variaciones a 7 días y desbalance de clases. |
| [`analisis/figuras/figura_4_estacionalidad_mensual.png`](analisis/figuras/figura_4_estacionalidad_mensual.png) | Visualización | Variación mensual promedio por mes calendario (indicio marzo). |
| [`datos/README_datos.md`](datos/README_datos.md) | Datos | Metadatos, fuentes SCOP Osinergmin, licencias y diccionario. |
| [`.gitignore`](.gitignore) | Control de Versiones | Exclusión de entornos virtuales, cachés y archivos temporales. |

---

## 5. Resumen de Hallazgos Empíricos Verificados (H1 – H10)

Todas las cifras del proyecto han sido verificadas y recalculadas desde cero mediante el script [`analisis/perfilado_datos.py`](analisis/perfilado_datos.py):

1. **H1 — Inercia casi total en grifos:** El **96.02% (~96.1%)** de los pares grifo-día no registran cambio de precio.
2. **H2 — Fuerte desbalance a 7 días:** **80.0% a 80.5%** se mantiene, **12.5% a 12.7%** sube y **6.9% a 7.3%** baja.
3. **H3 — Saltos discretos y asimétricos:** Cuando cambia, sube **+S/ 0.503/galón** y baja solo **−S/ 0.341/galón**.
4. **H4 — Estaciones estáticas:** El **29.7%** de los grifos con $\ge 30$ registros jamás alteró su precio en la muestra.
5. **H5 — La dispersión supera al tiempo:** Al 28-feb-2026, la gasolina regular presenta P10 = S/ 13.39 y P90 = S/ 15.70 (**Brecha de S/ 2.12/galón**). Un conductor que carga 8 galones evita pagar **S/ 16.96 de más por tanqueada** (~S/ 68 al mes).
6. **H6 — Transición regulatoria Osinergmin:** En 2023 se pasó de "Gasohol 90 Plus" a "Gasohol Regular", resuelta mediante equivalencia continua `combine_first`.
7. **H7 — Serie histórica de Lima:** 80 meses continuos reconstruidos (ene 2020 – ago 2026, media S/ 15.65 – 15.67, mín S/ 10.72, máx S/ 22.43).
8. **H8 — Débil inercia autorregresiva:** Autocorrelación intermensual de primer orden de 0.28 – 0.32, justificando variables macro líderes.
9. **H9 — Indicio estacional en marzo:** Presión alcista media de +S/ 0.99 a +S/ 1.01/galón (declarado honestamente como indicio exploratorio al contar con $N=7$).
10. **H10 — Desfase temporal entre fuentes:** El registro diario de grifos concluye en feb 2026; la serie mensual departamental llega a ago 2026.

---

## 6. Reproducibilidad y Ejecución

### 6.1 Perfilado exploratorio (Fase R)

```bash
pip install -r requirements.txt
python analisis/perfilado_datos.py
```

El script verificará la integridad de los datasets en `datos/`, saneará los 16 valores fuera de rango (<S/ 5 o >S/ 30), imprimirá el reporte estadístico y regenerará las imágenes en `analisis/figuras/`.

### 6.2 Entrenamiento y evaluación (Fase M)

```bash
make ayuda        # lista todos los comandos disponibles
make entrenar     # entrena el componente analítico A2 y evalúa sobre el test ciego
make inferir      # ejecuta el pipeline end-to-end y muestra el payload
make auditoria    # mide el KR2 sobre 60 casos
make pruebas      # corre las 17 pruebas del contrato metodológico
make todo         # la cadena completa: entrenar + auditoria + pruebas
```

Sin `make`, cada paso es un script directo:

```bash
python modelado/entrenamiento_a2.py
python pipeline_inferencia.py --departamento LIMA --nivel-tanque bajo
python -m pytest tests/ -v
```

Las métricas quedan en `reportes/*.json` y los modelos en `modelos/*.joblib`. El informe interpretado está en [`analisis/fase_m_resultados.md`](analisis/fase_m_resultados.md).

### 6.3 Variables macroeconómicas (paso complementario)

```bash
python scripts/obtener_macro.py   # requiere conexión a internet
make entrenar                     # reentrenar para incorporarlas
```

Si el archivo `datos/macro_mensual.csv` no existe, el entrenamiento continúa sin estas variables y lo declara explícitamente en `reportes/metricas_a2.json`.

---

## 6.bis Estado Medido de los OKR

Cifras regeneradas y auditadas por `make todo`. Detalle e interpretación en [`analisis/fase_m_resultados.md`](analisis/fase_m_resultados.md).

| KR | Meta Comprometida (Semana 6) | Valor Medido en Test Ciego (2026) | Estado |
|:---:|---|---|:---:|
| **KR1** · Recall en Alzas | $\ge$ 70% | **93.8%** (con umbral $P^* = 0.25$) | ✅ **Cumple (+23.8 pp)** |
| **KR1** · Macro-F1 en Test Ciego | $\ge$ 0.55 | 0.4418 con argmax · 0.2058 con $P^* = 0.25$ | ❌ No alcanzada (supera 5.3x al baseline de persistencia: 0.0833) |
| **KR2** · Recomendaciones sin Alucinación | 100% ($N \ge 50$) | **100%** sobre 60 casos evaluados | ✅ **Cumple** |
| **KR3** · Despliegue Operativo en la Nube | 100% en Semana 10 | Arquitectura definida en Vercel + Supabase | ⚪ Semana 10 |
| **KR4** · Ahorro por Carga frente a Dispersión | $\ge$ S/ 8.00 | **S/ 16.96** (Brecha oficial P90–P10 de S/ 2.12/galón en 8 galones) | ✅ **Cumple** |

Hallazgo destacado: La brecha estructural entre estaciones de servicio en Lima alcanza S/ 2.12 por galón (Hallazgo H5). Un conductor que utiliza la banda referencial evita pagar hasta S/ 16.96 adicionales por tanqueada semanal.

---

## 7. Instrucciones para Publicación en GitHub

Para sincronizar este repositorio en la cuenta de GitHub designada:

```bash
git init
git add .
git commit -m "feat: propuesta de proyecto PC1 — Fases P, R y O (Lunetra IA)"
git branch -M main
git remote add origin https://github.com/Los-1000/tanquelleno-ai.git
git push -u origin main
```
