# Plantilla 1 — Problem Statement Canvas (Fase P)
**Curso:** AD5018 — Inteligencia Artificial para Negocios  
**Universidad:** Universidad de Ingeniería y Tecnología (UTEC)  
**Departamento:** Administración & Negocios Digitales · Malla 2024 — Ciclo 9  
**Proyecto:** Lunetra IA — Asistente Inteligente de Combustibles  
**Integrantes:** Stefano Canales · Carlos Flores · Carlos Alcazar · Miguel Ángel Mori  
**Fecha de entrega:** Semana 6 · 19 de septiembre de 2026  

---

## 1. Problem Statement Canvas

### 1.1 Usuario Específico (Segmento Objetivo)
**Una persona, no "el mercado" (Conductor particular de Lima Metropolitana):**
- **Lima:** Vive y maneja dentro de la ciudad.
- **Todos los días:** Usa su auto para trabajar, no de paseo (recorridos laborales diarios de 25 a 40 km).
- **8 galones:** Es lo que carga en una semana normal de Gasolina Regular (G90) o Premium.
- **Su propio bolsillo:** Nadie le reembolsa la gasolina ni cuenta con convenios de flota corporativa.

> *Nota metodológica de diseño:* Se descarta explícitamente el uso de categorías genéricas como "los conductores", "la ciudadanía" o "los peruanos". Si el usuario es "todos", el producto no sirve para nadie. El segmento se restringe a la persona natural que asume directamente el costo del combustible.

### 1.2 Problema
Los conductores particulares en Lima Metropolitana enfrentan una **elevada e invisible dispersión de precios minoristas entre estaciones de servicio en un mismo período, sumada a la incertidumbre sobre la dirección y el momento de traslado de los ajustes mensuales de precios mayoristas al surtidor**. Esta situación les impide anticipar si les conviene cargar tanque lleno hoy o esperar, así como identificar si la estación donde repostan se ubica en el rango razonable o en la cola cara del mercado.

> *Regla de diseño PROMPT v2.0:* El problema **no menciona ninguna tecnología**. No se formula como "falta una aplicación", "no tienen un chatbot" o "no usan machine learning", sino como un conflicto económico y decisorio del usuario en su vida real.

### 1.3 Causa Raíz
1. **Asimetría informativa y opacidad comercial:** Aunque los precios mayoristas y los reportes de Osinergmin son públicos, la información se presenta de forma técnica, fragmentada y agregada, dificultando que el usuario final conozca la distribución real de precios de su zona.
2. **Heterogeneidad de márgenes minoristas:** Cada estación de servicio traslada las variaciones de planta con diferente velocidad y magnitud, operando con márgenes comerciales dispares que generan distorsiones persistentes (estaciones estáticas vs. estaciones reactivas).
3. **Complejidad multivariada rezagada:** El precio minorista depende de fluctuaciones internacionales del crudo, refinación y tipo de cambio que tardan entre dos y seis semanas en trasladarse al mercado local, dinámica contraintuitiva para el juicio intuitivo del conductor.

### 1.4 Consecuencia Medible
El impacto económico perjudicial se sustenta en la evidencia cuantitativa del mercado analizado:
- **Dispersión verificada entre grifos (Hallazgo H5):** Al corte del 28 de febrero de 2026 en Lima/nacional, el precio de la gasolina regular presenta una media de S/ 14.35 a S/ 14.42 por galón, con un percentil 10 (P10) de S/ 13.38 – S/ 13.39 y un percentil 90 (P90) de S/ 15.50 – S/ 15.70, lo que arroja una **brecha intercuartil verificada de S/ 2.12 por galón**.
- **Sobrecosto evitable calculado:**
  $$\text{Sobrecosto por carga} = 8 \text{ galones} \times \text{S/ } 2.12/\text{galón} = \text{\textbf{S/ 16.96}}$$
  $$\text{Sobrecosto mensual (4 semanas)} = 4 \times \text{S/ } 16.96 = \text{\textbf{S/ 67.84}}$$
  $$\text{Sobrecosto anual evitable} = 12 \times \text{S/ } 67.84 = \text{\textbf{S/ 814.08}}$$
- **Declaración estricta de supuestos:**
  - `⚠️ SUPUESTO DECLARADO:` Se asume una carga regular de **8 galones por semana**, representativa del recorrido promedio urbano en Lima para un auto con tanque de 11 a 13 galones que abastece al llegar a un cuarto de tanque.
  - La brecha de S/ 2.12 por galón no es una estimación teórica: es el dato empírico extraído de los 4,428 grifos activos del archivo oficial al 28 de febrero de 2026.

---

## 2. Contexto y Evidencia del Comportamiento Actual

### 2.1 ¿Cómo decide hoy el usuario? (La realidad del día a día)
Todos los que manejan en Lima se hacen la misma pregunta, y nadie tiene la respuesta certera: **"¿Lleno hoy o espero?"**. En la práctica, ocurre esto:
1. **Se carga por costumbre (Inercia):** El conductor acude al grifo de siempre y el día que se acuerda, sin comparar nada, asumiendo el riesgo de repostar en el 29.7% de estaciones estáticas (Hallazgo H4) que mantienen márgenes elevados sin justificación.
2. **El precio sube sin aviso:** No existe alerta previa; el usuario se entera recién cuando ya está frente al surtidor pagando el incremento.
3. **Nadie compara precios:** Aunque los datos existen y son públicos en Osinergmin (SCOP/PRICE), están confinados en tablas densas y reportes PDF que ningún conductor lee antes de salir de casa.
4. **Frustración por consultas engorrosas:** Las herramientas públicas tradicionales (como Facilito) obligan a buscar grifo por grifo manualmente, sin dar contexto de dispersión estadística ni responder si conviene cargar hoy o esperar la próxima semana.

### 2.2 Costo de oportunidad del usuario
El conductor asume un doble perjuicio:
- **Perjuicio directo por dispersión:** Pagar hasta S/ 17 de más por cada llenado de tanque debido a la falta de encuadre probabilístico de precios en su entorno.
- **Perjuicio por mal momento de recarga (Hallazgo H3):** Cuando el precio sube, el salto promedio es de **+S/ 0.40 a +S/ 0.50 por galón**. Si el usuario posterga la carga justo antes del traslado mayorista, absorbe inmediatamente un sobrecosto adicional de S/ 3.20 a S/ 4.00 en esa misma tanqueada.

---

## 3. Filtro de Validación de IA: ¿Por qué esta solución requiere IA?

### 3.1 ¿Por qué una hoja de cálculo o un sistema de reglas fijas no basta?
1. **Correlaciones dinámicas no lineales y rezagos cruzados:** La traslación de precios de paridad de importación (WTI, spot Costa del Golfo) y tipo de cambio (S//US$) hacia el mercado minorista peruano no es simultánea ni lineal. Presenta desfases temporales (lags de 1 a 2 meses) y relaciones asimétricas (los precios suben más rápido de lo que bajan). Una hoja de cálculo basada en promedios móviles o reglas "si el petróleo sube, sube el grifo" genera errores sistemáticos de predicción.
2. **Optimización de umbrales bajo pérdida asimétrica:** Una fórmula de Excel no puede calibrar dinámicamente un umbral de decisión probabilístico en función de matrices de confusión desbalanceadas (Hallazgo H2: 80.5% neutro vs. 12.5% subida). Un modelo de Machine Learning calibrado permite desplazar la frontera de decisión para penalizar con mayor peso los Falsos Negativos (no alertar una subida inminente).
3. **Traducción contextual generativa:** Una macro de Excel solo arroja números fríos (ej. `+0.42, prob=0.68`), incomprensibles para el conductor en su día a día. El componente generativo traduce la predicción analítica y la dispersión estadística a una narrativa amigable y accionable en lenguaje natural ("Se anticipa presión alcista para la próxima semana; te sugerimos llenar el tanque estos días si tu nivel está bajo").

### 3.2 ¿Qué pasaría si no se hace nada?
Los conductores continuarán perdiendo entre S/ 60 y S/ 80 mensuales por asimetría de información y sesgo de conveniencia. El mercado minorista mantendrá su ineficiencia distributiva, donde grifos caros sostienen márgenes extraordinarios gracias al desconocimiento del consumidor.

### 3.3 Declaración honesta del punto ciego y límites del modelo
> [!WARNING]
> **Límites epistemológicos del modelo:**
> El sistema modela patrones históricos de transmisión y tendencias estadísticas; **NO predice shocks exógenos imprevisibles**, tales como estallidos de conflictos geopolíticos bélicos repentinos, interrupciones no programadas en oleoductos locales, huelgas de transportistas, ni decretos de urgencia gubernamentales que modifiquen de la noche a la mañana los factores de estabilización de precios (FEPC). El usuario debe ser advertido formalmente de esta frontera de incertidumbre.

---

## 4. Definición de los Dos Componentes y Eje de Ambición

El producto integra de forma desacoplada dos componentes complementarios bajo el marco PROMPT v2.0:

```
+-----------------------------------+         +-------------------------------------+
|   COMPONENTE ANALÍTICO (A2)       |         |    COMPONENTE GENERATIVO (G1)       |
|  Modelo predictivo de tendencia   | ------> | Prompt estructurado con contexto    |
|  mensual con umbral asimétrico    | Payload | fijo que redacta la recomendación   |
+-----------------------------------+         +-------------------------------------+
```

### 4.1 Componente Analítico: Nivel A2
- **Definición del componente:** Modelo de clasificación supervisada de Machine Learning que predice la dirección del precio promedio mensual para el departamento seleccionado en el horizonte $t+1$:
  $$\hat{Y}_{t+1} \in \{\text{Sube}, \text{Se Mantiene}, \text{Baja}\}$$
- **Justificación de Nivel A2:**
  - Compara formalmente dos aproximaciones: un **Baseline obligatorio de persistencia** ("el precio del próximo mes será igual al actual") frente a una **Regresión Logística Regularizada (L2 Ridge / ElasticNet)** con calibración sigmoide de probabilidades (Platt Scaling). Se descartan explícitamente arquitecturas complejas de ensamble de árboles o redes neuronales profundas que resultan inviables e implausibles para una serie temporal corta de 80 meses mensuales, priorizando generalización, interpretabilidad de coeficientes y estabilidad en las probabilidades estimadas.
  - Optimiza explícitamente el **umbral de decisión** con base en una matriz de costos asimétricos: equivocarse al no advertir un alza le cuesta al usuario S/ 4.00, mientras que alertar una subida que no ocurre solo genera el costo marginal de adelantar la recarga.
  - La muestra de grifos individuales (Archivo A) se explota analíticamente para calcular y proveer los percentiles de dispersión estructural (P10, P50, P90).

### 4.2 Componente Generativo: Nivel G1
- **Definición del componente:** Módulo de síntesis y redacción en lenguaje natural mediante LLM (Gemini Flash API) operando con **prompt estructurado y contexto fijo**.
- **Justificación de Nivel G1:**
  - Recibe un payload predecible y validado desde el componente A2 (tendencia predicha, probabilidad calibrada, percentiles de dispersión y departamento).
  - No requiere fine-tuning, agentes autónomos ni RAG complejo en esta fase. Se mantiene en el nivel base (G1) para asegurar confiabilidad, nula latencia y cero alucinaciones sobre los datos numéricos.

### 4.3 Declaración Explícita del Eje de Ambición
> [!IMPORTANT]
> **Declaración de Ambición (Regla de Alcance PROMPT v2.0):**
> El **eje donde se concentra la ambición del proyecto es el COMPONENTE ANALÍTICO (A2)**.  
> La sofisticación técnica, el esfuerzo de ingeniería y la experimentación rigurosa se enfocarán en el tratamiento de los rezagos de series temporales, el balanceo de clases, la ingeniería de variables y la calibración del umbral asimétrico de clasificación.  
> El **componente generativo (G1) se mantendrá intencionalmente en el piso de complejidad**, operando estrictamente como un motor determinístico de comunicación y empatía con el usuario.

### 4.4 Patrón de Conexión Elegido: Patrón 1 (Modelo $\rightarrow$ Lenguaje)
- **Razón de elección:** El flujo de valor es unidireccional y secuencial. El modelo analítico procesa la base histórica y las variables de mercado, infiere la probabilidad de movimiento y los percentiles de dispersión, y transfiere este vector cuantitativo estructurado al modelo de lenguaje. El modelo generativo actúa como interfaz de comunicación hacia el conductor humano.
