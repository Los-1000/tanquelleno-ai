# Resumen Ejecutivo: Proyecto Lunetra IA
**Evaluación:** Práctica Calificada 1 (PC1) · Fases P, R y O  
**Curso:** AD5018 — Inteligencia Artificial para Negocios (UTEC, Framework PROMPT v2.0)  
**Equipo:** Stefano Canales · Carlos Flores · Carlos Alcazar · Miguel Ángel Mori  
**Repositorio GitHub:** [github.com/Los-1000/tanquelleno-ai](https://github.com/Los-1000/tanquelleno-ai)  
**Fecha de Entrega:** Semana 6 · 19 de septiembre de 2026  

---

### 1. El Problema y el Usuario Objetivo
Todos los que manejan en Lima se hacen la misma pregunta, y nadie tiene la respuesta: **"¿Lleno hoy o espero?"**. En Lima Metropolitana, los **conductores particulares que utilizan su vehículo propio a gasolina a diario (25 a 40 km/día) y abastecen aproximadamente 8 galones semanales** de su propio presupuesto enfrentan una **elevada e invisible dispersión de precios minoristas entre estaciones de servicio en un mismo período, sumada a la incertidumbre sobre la dirección y el momento de traslado de los ajustes mensuales de precios mayoristas al surtidor**. Esta situación les impide anticipar si les conviene cargar tanque lleno hoy o esperar, así como identificar si la estación donde repostan se ubica en el rango razonable o en la cola cara del mercado. Hoy se carga por costumbre, el precio sube sin aviso y nadie compara tablas densas de datos.

### 2. Consecuencia Medible y Costo Económico Evitable
El análisis empírico oficial al corte del 28 de febrero de 2026 (4,428 estaciones activas con Gasolina Regular) demuestra que la media se sitúa en S/ 14.42/galón, con un Percentil 10 (P10) de **S/ 13.39** y un Percentil 90 (P90) de **S/ 15.70**. Esto evidencia una **brecha estructural de S/ 2.12 por galón** entre estaciones simultáneas (Hallazgo H5).
- **Sobrecosto evitable calculado:** Un conductor particular que carga 8 galones a la semana (`⚠️ SUPUESTO DECLARADO`) y compra en una estación del P90 en lugar del P10 incurre en un sobrecosto evitable de **S/ 16.96 por tanqueada**, equivalente a **S/ 67.84 al mes** (~S/ 814 anuales).
- **Costo de oportunidad por mala anticipación:** Cuando los precios mayoristas suben, el salto promedio en el surtidor es de **+S/ 0.50 por galón** (Hallazgo H3), castigando al conductor con S/ 4.00 adicionales en una sola carga por no abastecer a tiempo.

### 3. Diagnóstico de Datos y Semáforo Honesto
- **Datos Disponibles (🟢):**
  - *Serie Histórica Osinergmin:* 80 meses continuos (ene 2020 – ago 2026) en 24 departamentos (11,227 filas sin nulos). Reconstruida tras resolver la transición normativa de 2023 de Gasohol 90 a Regular (Hallazgo H6 y H7).
  - *Muestra Transversal Minorista:* 497,156 registros diarios de 8,825 grifos en 59 días (ene–feb 2026), donde se identificaron y sanearon 16 valores imposibles (<S/ 5 o >S/ 30), documentando un 80.5% de inercia a 7 días (Hallazgo H2).
- **Datos Pendientes (🔴):** Variables macroeconómicas exógenas líderes (WTI, Brent, tipo de cambio BCRP S//US$ y margen de refinación Costa del Golfo). Se declaran honestamente en rojo con plan de ingestión vía API para la Semana 7.
- **Límites Transparentes:** No se cuenta con coordenadas GPS ni ubicación distrital en el archivo de grifos (datos anonimizados). No existen partes 2 ni 3. Por ende, **el producto no incluye mapas, rutas GPS ni función de "grifo más cercano"**.

### 4. Arquitectura de Solución y Niveles de Componentes
El producto se estructura desacopladamente bajo el **Patrón de Conexión 1 (Modelo $\rightarrow$ Lenguaje)**:
- **Componente Analítico (Nivel A2 — EJE DE AMBICIÓN DECLARADO):** Modelo de Machine Learning basado en **Regresión Logística Regularizada (L2 Ridge / ElasticNet) con Calibración Sigmoide (Platt Scaling)** evaluado formalmente contra el **Baseline Obligatorio de Persistencia** ("próximo mes = mes actual"). Se descartan explícitamente modelos de ensamble no paramétricos (LightGBM/XGBoost) o redes profundas por riesgo severo de sobreajuste en una serie de 80 meses. Incorpora **calibración de umbral asimétrico ($P^* = 0.25$)**, fundamentada en que el costo de no advertir un alza ($FN = \text{S/ } 4.00$) es 5 veces mayor que el costo de una falsa alarma ($FP = \text{S/ } 0.80$).
- **Componente Generativo (Nivel G1 — PISO DE COMPLEJIDAD):** LLM (Gemini Flash API) con System Prompt parametrizado que recibe el payload cuantitativo (tendencia, probabilidad, P10, P50, P90) y responde en una frase clara y empática: **"Carga hoy"** o **"Puedes esperar"**, junto con la banda de precio justo de referencia, sin alucinaciones numéricas.

### 5. Alcance, Plataforma y Compromiso de Despliegue
- **Entregable MVP:** Aplicación web responsiva en **Vercel** (Next.js / React con Serverless Functions) integrada con base de datos en **Supabase** (PostgreSQL Cloud), conectada al repositorio GitHub (`Los-1000/tanquelleno-ai`).
- **Fecha de Despliegue Comprometida:** **Semana 10** (despliegue anticipado para validar con usuarios antes de la fecha límite del curso).

### 6. Resultados Clave Comprometidos (OKRs Inmutables)
1. **KR 1 (Predictivo):** Superar el Macro-F1 del baseline de persistencia (0.33) alcanzando **Macro-F1 $\ge$ 0.55** y **Recall en alzas $\ge$ 70%** en el test set ciego (2026).
2. **KR 2 (Generativo):** Lograr **100% de recomendaciones sin alucinación de precios** en auditoría controlada ($N \ge 50$ evaluaciones).
3. **KR 3 (Operacional):** Aplicación web 100% operativa en producción en **Vercel + Supabase** con latencia inferior a 1.5 segundos en la **Semana 10**.
4. **KR 4 (Negocio):** Habilitar una banda de precios referencial que capture al menos S/ 8.00 de ahorro por carga frente al P90.
