# Fase M — Resultados de Modelado (TanqueLleno AI)

**Curso:** AD5018 — Inteligencia Artificial para Negocios (UTEC)
**Alcance:** Semanas 7 a 9 del cronograma (ingeniería de variables, entrenamiento A2, calibración de umbral e integración G1).
**Reproducibilidad:** todas las cifras de este documento se regeneran con `make todo`. Las fuentes de verdad son `reportes/metricas_a2.json`, `reportes/metricas_posicion.json` y `reportes/auditoria_kr2.json`.

> Este documento reporta lo que los modelos efectivamente lograron, incluyendo aquello que **no** alcanzó la meta comprometida. Las metas de la PC1 se mantienen intactas: no se reescriben para acomodar el resultado.

---

## 1. Qué se construyó

| Componente | Archivo | Estado |
|---|---|:---:|
| Ingeniería de variables con protocolo anti-leakage | `src/tanquelleno/features.py` | ✅ |
| Entrenamiento del componente analítico A2 | `modelado/entrenamiento_a2.py` | ✅ |
| Modelo de posición de precio por grifo (nuevo) | `modelado/entrenamiento_posicion.py` | ✅ |
| Utilidades geoespaciales y "grifo más cercano" | `src/tanquelleno/geo.py` | ✅ |
| Pipeline end-to-end Modelo → Lenguaje | `pipeline_inferencia.py` | ✅ |
| Auditoría anti-alucinación (KR2) | `src/tanquelleno/prompts.py` | ✅ |
| Ingesta de variables macro líderes | `scripts/obtener_macro.py` | ⚠️ escrito, pendiente de ejecución con red |
| Suite de pruebas del contrato | `tests/test_contrato_modelado.py` | ✅ 22/22 |
| Aplicación web en Streamlit | — | ⚪ Semana 10 |

---

## 2. Componente Analítico A2 — Tendencia mensual departamental

### 2.1 Dataset y partición

Panel de **1,824 filas** (24 departamentos × 76 meses utilizables) con 11 variables, todas rezagadas a t-1 o derivadas del calendario.

| Split | Período | N | MANTIENE | SUBE | BAJA |
|:---:|---|---:|---:|---:|---:|
| Train | abr 2020 – dic 2024 | 1,368 | 357 | 513 | 498 |
| Validación | ene 2025 – dic 2025 | 288 | 140 | 30 | 118 |
| Test ciego | ene 2026 – jul 2026 | 168 | 24 | 80 | 64 |

**Dos desviaciones respecto del Model Design Canvas, declaradas:**

1. **El train empieza en abril 2020, no en enero.** Los tres primeros meses se consumen como warm-up de los lags P(t-1), P(t-2) y P(t-3). Son 96 filas (24 departamentos × 4 meses) que no pueden tener features completas. Alternativa descartada: imputarlas, lo que habría inventado historia.
2. **El test tiene 7 meses, no 8.** Agosto 2026 es el último mes observado, así que no existe P(t+1) contra el cual etiquetarlo. Esa fila sí se usa en inferencia (es la base de la predicción vigente), pero no puede evaluarse.

### 2.2 Desbalance no estacionario

La distribución de clases cambia radicalmente entre particiones: en 2025 solo el **10.4%** de los pares departamento-mes fueron alzas; en 2026 lo fueron el **47.6%**. El modelo se sintoniza en un régimen predominantemente bajista y se evalúa en uno alcista. Esto no es un defecto del código sino una propiedad del mercado, y explica buena parte de la brecha entre validación y test.

### 2.3 Resultados sobre el test ciego

| Configuración | Macro-F1 | Recall (SUBE) | Costo esperado |
|---|---:|---:|---:|
| Baseline de persistencia | 0.0833 | 0.0% | S/ 1.905 |
| Baseline de inercia del signo | 0.2278 | 15.0% | S/ 1.848 |
| **Modelo A2, decisión por argmax** | **0.4418** | 66.3% | S/ 0.962 |
| **Modelo A2, umbral P\* = 0.25** | 0.2058 | **93.8%** | **S/ 0.538** |

Modelo seleccionado: **logística regularizada** (Macro-F1 en validación 0.3040 frente a 0.2912 del boosting de árboles). La selección se hizo exclusivamente sobre validación 2025.

### 2.4 Estado de los KR — lectura honesta

| KR | Meta | Obtenido | Estado |
|---|:---:|:---:|:---:|
| KR1 · Macro-F1 (con P\* = 0.25) | ≥ 0.55 | 0.2058 | ❌ **No cumple** |
| KR1 · Macro-F1 (con argmax) | ≥ 0.55 | 0.4418 | ❌ No cumple, pero 5.3× el baseline |
| KR1 · Recall en alzas | ≥ 70% | 93.8% | ✅ **Cumple** |
| Superar el baseline de persistencia | — | sí (0.2058 > 0.0833) | ✅ |
| Superar el baseline de inercia (con P\*) | — | no (0.2058 < 0.2278) | ❌ |
| Superar el baseline de inercia (argmax) | — | sí (0.4418 > 0.2278) | ✅ |

**Reducción de costo:** de S/ 1.905 a S/ 0.538 por decisión de tanqueo, un **ahorro de S/ 1.37 por decisión (−71.8%)** frente a no tener modelo.

### 2.5 Hallazgo crítico — el umbral P\* = 0.25 vuelve alarmista al modelo

La matriz de confusión con P\* = 0.25 es contundente. De 168 casos de test, el modelo emitió alerta de alza en **163**:

|  | Predijo MANTIENE | Predijo SUBE | Predijo BAJA |
|---|---:|---:|---:|
| Real MANTIENE (24) | 0 | 24 | 0 |
| Real SUBE (80) | 0 | 75 | 5 |
| Real BAJA (64) | 0 | 64 | 0 |

El recall de 93.8% es real, pero se compra prediciendo "sube" casi siempre. La métrica de costo lo premia —porque C(FN) es cinco veces C(FP)— y sin embargo el producto pierde su utilidad informativa: una app que siempre dice "tanquea ya" no ayuda a decidir.

**Origen del problema:** P\* = 0.25 se derivó de la razón de costos asumiendo un clasificador binario bien calibrado. Aplicado a un problema de tres clases donde la probabilidad de alza rara vez supera 0.40, el umbral queda por debajo de casi toda la distribución. El barrido sobre validación encuentra el mínimo de costo real en **P\* = 0.42** (costo S/ 0.397, Macro-F1 0.3534).

**Recomendación para la PC2:** mantener P\* = 0.25 como valor congelado en la PC1 y documentar esta tensión, presentando el barrido de calibración como evidencia. Es un hallazgo más valioso que un número que cumpla la meta.

### 2.6 Por qué el Macro-F1 no llega a 0.55

Tres causas, en orden de peso:

1. **Faltan las variables macro líderes.** WTI, Brent, tipo de cambio y margen de refinación siguen sin ingestarse; el modelo predice el precio del combustible sin saber el precio del crudo. La Fase R ya anticipó esta limitación al declararlas en rojo. El script `scripts/obtener_macro.py` está listo; falta ejecutarlo.
2. **Débil inercia autorregresiva (H8).** Con autocorrelación intermensual de 0.30, la historia propia de la serie tiene poco poder predictivo. Era el argumento original para incorporar variables exógenas.
3. **Cambio de régimen entre validación y test** (sección 2.2).

---

## 3. Modelo de Posición de Precio — Lima y Callao

Componente nuevo, habilitado por la fuente georreferenciada. Responde *dónde* cargar, mientras A2 responde *cuándo*.

**Cobertura:** 144 estaciones utilizables de 199 (27 distritos, 3 marcas). Las 55 restantes quedan fuera por no alcanzar el mínimo de tres vecinos en 2 km: sin entorno comparable, la variable de referencia local no es calculable.

### 3.1 Resultados (validación cruzada de 5 pliegues)

| Modelo | MAE | RMSE | R² |
|---|---:|---:|---:|
| Baseline: media global | S/ 0.829 | S/ 1.011 | 0.000 |
| Baseline: mediana por marca | S/ 0.822 | S/ 1.035 | −0.047 |
| **Baseline: mediana por distrito** | **S/ 0.506** | **S/ 0.742** | **0.462** |
| Ridge | S/ 0.632 | S/ 0.817 | 0.348 |
| Bosque aleatorio | S/ 0.577 | S/ 0.787 | 0.395 |

### 3.2 Hallazgo — el baseline gana

**La mediana del distrito predice mejor que ambos modelos de aprendizaje automático** (MAE S/ 0.506 contra S/ 0.577 del mejor modelo). Con 144 observaciones y 27 distritos, el modelo gasta capacidad estimando efectos que la mediana captura directamente, y la validación cruzada penaliza ese sobreajuste.

**Consecuencia de producto:** para el MVP, la regla operativa debe ser la comparación contra la mediana distrital, no una predicción del modelo. Es más barata, más explicable ante el usuario y, con los datos actuales, más precisa. El modelo entrenado se conserva como referencia y para reevaluarlo cuando el padrón crezca.

Este resultado es coherente con el filtro de IA de la Fase P: no toda tarea justifica un modelo.

---

## 4. Cuantificación del KR4 — Ahorro por dispersión geográfica

Con coordenadas reales ya es posible medir el ahorro accionable, no solo la brecha estadística P90−P10.

| Radio de búsqueda | Ahorro mediano por tanqueada (8 gal) | P90 | Cobertura |
|:---:|---:|---:|---:|
| 1 km | S/ 4.00 | S/ 12.00 | 89.6% |
| **2 km** | **S/ 9.60** | S/ 23.20 | 99.3% |
| 3 km | S/ 13.60 | S/ 24.00 | 99.3% |
| 5 km | S/ 16.00 | S/ 28.00 | 99.3% |

**KR4 (ahorro ≥ S/ 8.00 por carga): ✅ cumple a partir de un radio de 2 km**, con S/ 9.60 medianos. Y a diferencia de la brecha P90−P10, este número es alcanzable: describe el ahorro de moverse a un grifo concreto que existe, a una distancia concreta.

### 4.1 Descuentos de aplicativo — variable inédita

| Marca | Descuento | Ahorro por tanqueada | Estaciones |
|---|---:|---:|---:|
| Repsol | S/ 3.00/gal | **S/ 24.00** | 61 |
| COESTI (Primax) | S/ 1.00/gal | S/ 8.00 | 81 |
| Primax afiliada | S/ 1.00/gal | S/ 8.00 | 2 |

El descuento de Repsol (S/ 24.00 por tanqueada) **supera por sí solo tanto el ahorro por elección geográfica como el ahorro por acertar la tendencia mensual** (S/ 4.00 según H3). Es, con diferencia, la palanca de ahorro más grande identificada en todo el proyecto, y no requiere ningún modelo: basta con informarla.

---

## 5. Componente Generativo G1 — KR2

| Métrica | Meta | Obtenido | Estado |
|---|:---:|:---:|:---:|
| Evaluaciones | ≥ 50 | 60 | ✅ |
| Recomendaciones sin alucinación numérica | 100% | **100%** | ✅ **Cumple** |

La verificación es automática: `auditar_alucinacion_numerica()` extrae toda cifra monetaria del texto generado y exige que provenga del payload; además comprueba la presencia literal del aviso de IA y, cuando la confianza es BAJA o la probabilidad cae en la banda 0.40–0.55, de la advertencia de incertidumbre. Evidencia completa en `reportes/auditoria_kr2.json`.

**Nota de alcance:** el generador actual es determinista (`redactar_sin_llm`), no un LLM. Sirve como respaldo ante fallos de API y como referencia de auditoría. La integración con Gemini Flash es trabajo de la Semana 9–10; el instrumento de medición del KR2 ya está listo para aplicarse a su salida sin cambios.

---

## 6. Defecto de datos corregido

El histórico del scraper de Lima/Callao (`historico.csv`) no escribía el salto de línea al cerrar cada snapshot, dejando la última fila de un snapshot concatenada con la primera del siguiente:

```
..."26.99""2026-09-16T22:06:15-0500","158833","Repsol",...
```

Con cuatro snapshots, eran **3 filas corruptas**: el parser aborta o descarta una fila por frontera. `datos.cargar_historico_lima_callao()` repara el patrón al leer, y el test `test_historico_del_scraper_se_lee_completo` verifica que los cuatro snapshots tengan los mismos 199 grifos.

**Acción pendiente aguas arriba:** corregir el scraper para que emita `\n` al cerrar cada escritura. La reparación en el loader es un parche defensivo, no la solución.

---

## 7. Qué falta para cerrar la Fase M

| # | Pendiente | Impacto esperado | Semana |
|:---:|---|---|:---:|
| 1 | Ejecutar `scripts/obtener_macro.py` y reentrenar | Es la palanca principal para acercar el Macro-F1 a 0.55 | S7 (tardío) |
| 2 | Decidir el umbral de producción a la luz de la sección 2.5 | Evita una app que alerta siempre | S9 |
| 3 | Integrar Gemini Flash y auditar su salida con el KR2 ya instrumentado | Cierra el componente G1 | S9 |
| 4 | Construir y desplegar la app en Streamlit Cloud | KR3 | S10 |
| 5 | Programar la captura diaria del padrón de Lima/Callao | Convierte 4 snapshots en una serie temporal por grifo | continuo |
| 6 | Ampliar el padrón más allá de Repsol y Primax | Hoy la cobertura es de 3 marcas; falta Petroperú y los independientes | S11 |
| 7 | Corregir el salto de línea en el scraper | Elimina la necesidad del parche defensivo | S7 |

---

## 8. Actualización del semáforo de datos (Fase R)

| Variable | Semáforo PC1 | Semáforo ahora | Motivo |
|---|:---:|:---:|---|
| Coordenadas GPS por grifo | 🔴 | 🟢 | 199 estaciones con `lat`/`lon` en Lima y Callao |
| Distrito de la estación | 🔴 | 🟢 | 39 distritos identificados |
| Marca comercial | 🔴 | 🟡 | Disponible, pero solo 3 marcas (sin Petroperú ni independientes) |
| Descuento de aplicativo | — | 🟢 | Variable nueva, no contemplada en la PC1 |
| Serie temporal por grifo con GPS | 🔴 | 🔴 | Solo 4 snapshots en 3 días: insuficiente para modelar |
| WTI / Brent / tipo de cambio | 🔴 | 🔴 | Script listo, ingesta pendiente |

**Consecuencia de alcance:** la PC1 declaró que "el producto no incluye mapas, rutas GPS ni función de grifo más cercano". Para **Lima Metropolitana y Callao esa restricción ya no aplica**, y `geo.grifos_cercanos()` la implementa. Para el resto del país sigue vigente.
