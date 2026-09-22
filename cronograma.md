# Cronograma de Trabajo: Semanas 7 a 13
**Curso:** AD5018 — Inteligencia Artificial para Negocios (UTEC, Framework PROMPT v2.0)  
**Proyecto:** Lunetra IA — Asistente Inteligente de Combustibles  
**Equipo:** Stefano Canales · Carlos Flores · Carlos Alcazar · Miguel Ángel Mori  
**Repositorio GitHub:** [github.com/Los-1000/tanquelleno-ai](https://github.com/Los-1000/tanquelleno-ai)  
**Ciclo Académico:** 2026-II  

---

## Estructura por Fases del Framework PROMPT v2.0

- **Fase M (Modelado y Construcción de Solución):** Semanas 7 a 11  
  *(Nota crítica: El despliegue en producción se ejecuta en la **Semana 10**, antes del hito final de la Fase M).*
- **Fase P2 (Pilotaje y Medición de Impacto):** Semana 12  
- **Fase T (Transferencia, Cierre y Sustentación Final):** Semana 13  

---

## Planificación Detallada Semana por Semana

### Semana 7 — Fase M: Ingestión de Datos Macroeconómicos e Ingeniería de Variables
- **Objetivo:** Resolver los semáforos en rojo del checklist de datos (R) integrando las variables macroeconómicas exógenas líderes con rezago riguroso.
- **Actividades:**
  - Desarrollar script automatizado en Python 3.12 para la descarga de series históricas del BCRP (tipo de cambio diario/mensual S//US$).
  - Extraer series de precios internacionales de crudo (WTI, Brent) y derivados spot Costa del Golfo desde FRED/EIA.
  - Generar el dataset maestro unificado con rezagos $t-1$ y $t-2$, garantizando cero fuga de información (*data leakage*).
- **Entregable Verificable:** Archivo consolidado `datos/dataset_maestro_mensual.parquet` y script `scripts/obtener_macro.py` reproducible.
- **Responsable:** Carlos Flores (Ingeniería de Datos)
- **Riesgo Principal:** Cambios en los endpoints o credenciales de las APIs externas que retrasen la consolidación del dataset antes del cierre de semana.

### Semana 8 — Fase M: Entrenamiento del Componente Analítico (Nivel A2)
- **Objetivo:** Entrenar el modelo analítico de clasificación supervisada de tendencia mensual y contrastar su desempeño rigurosamente contra el baseline de persistencia.
- **Actividades:**
  - Implementar el esquema de partición cronológica: Train (2020–2024), Val (2025) y Test (2026).
  - Entrenar el Baseline Obligatorio de Persistencia ("próximo mes = mes actual").
  - Ajustar el modelo propuesto: Regresión Logística Regularizada (L2 Ridge / ElasticNet) con ponderación balanceada (`class_weight='balanced'`) y calibración sigmoide de probabilidades (Platt Scaling). Se descartan modelos de ensamble de árboles complejos (LightGBM/XGBoost) o deep learning por sobreajuste severo en la serie corta de 80 observaciones.
  - Evaluar métricas de clasificación: Macro-F1, Precision y Recall por clase, priorizando el Recall en la clase 'Sube'.
- **Entregable Verificable:** Script reproducible `modelado/entrenamiento_a2.py` con tabla comparativa de métricas en conjunto de validación.
- **Responsable:** Carlos Alcazar (Modelado Predictivo)
- **Riesgo Principal:** Multicolinealidad entre rezagos de precios internacionales y tipo de cambio; mitigación mediante regularización L2 estricta y selección parsimoniosa de rezagos.

### Semana 9 — Fase M: Calibración de Umbral Asimétrico e Integración con G1
- **Objetivo:** Optimizar el umbral de corte de probabilidad ($P^*$) según la matriz de costo asimétrico y acoplar el generador en lenguaje natural.
- **Actividades:**
  - Barrido de umbrales en el set de validación (2025) para minimizar la función de costo personalizada ($C_{FN}=4.0$, $C_{FP}=0.8$).
  - Fijar el umbral óptimo de alerta de alza en $P^* \approx 0.25$.
  - Implementar el módulo `generativo/motor_g1.py` con llamadas a la API de Google Gemini Flash utilizando el System Prompt blindado.
  - Ejecutar pruebas de estrés para verificar 0% de alucinaciones en los percentiles inyectados.
- **Entregable Verificable:** Script de inferencia integrada end-to-end `pipeline_inferencia.py` recibiendo payload y retornando recomendación en texto.
- **Responsable:** Stefano Canales (Estrategia Analítica & Umbrales)
- **Riesgo Principal:** Variabilidad en la latencia de la API de Gemini que afecte los tiempos de respuesta del pipeline.

### Semana 10 — Fase M: Construcción de Web App y Despliegue en Producción (Vercel + Supabase)
- **Objetivo:** Publicar la aplicación web interactiva en la red global de Vercel conectada a Supabase, asegurando disponibilidad pública antes del límite de la Semana 11.
- **Actividades:**
  - Configurar base de datos en Supabase (PostgreSQL Cloud) con series históricas de 80 meses y percentiles P10/P50/P90.
  - Desarrollar la interfaz responsiva en Next.js / React con selectores de departamento y tipo de combustible.
  - Implementar Vercel Serverless/Edge Functions para inferencia analítica A2 y orquestación con Gemini Flash API.
  - Conectar el repositorio de GitHub con Vercel para Continuous Deployment (CI/CD) automático.
  - Realizar pruebas de carga en dispositivos móviles y verificar tiempos de respuesta inferiores a 1.5 segundos.
- **Entregable Verificable:** URL pública y activa de la aplicación desplegada (`https://lunetra-ai.vercel.app`).
- **Responsable:** Miguel Ángel Mori (Frontend Next.js & Infraestructura Vercel + Supabase)
- **Riesgo Principal:** Latencia en conexiones en frío (cold starts) de funciones serverless; mitigación mediante Edge Functions y caching inteligente en Vercel.

### Semana 11 — Fase M: Pruebas con Usuarios Piloto y Cierre de Fase M
- **Objetivo:** Ejecutar pruebas de usabilidad con 10 conductores reales de Lima y calibrar los textos generativos con base en el feedback.
- **Actividades:**
  - Someter la app desplegada a sesiones de uso guiadas con usuarios particulares.
  - Recolectar retroalimentación mediante los botones de utilidad [👍 / 👎].
  - Evaluar la claridad de las recomendaciones y verificar que los usuarios comprendan la advertencia de estimación estadística.
  - Congelar los pesos finales del modelo analítico y el System Prompt.
- **Entregable Verificable:** Reporte de pruebas con usuarios piloto (`analisis/feedback_piloto_s11.md`) y confirmación de estabilidad del despliegue.
- **Responsable:** Stefano Canales & Carlos Flores
- **Riesgo Principal:** Dificultad para reclutar conductores que realicen pruebas activas en el plazo establecido.

### Semana 12 — Fase P2: Medición de Impacto y Elaboración de la Plantilla 4
- **Objetivo:** Medir el cumplimiento cuantitativo de los OKRs comprometidos en la PC1 y documentar formalmente la Fase P2.
- **Actividades:**
  - Evaluar el modelo analítico sobre el conjunto de prueba ciego final (meses de 2026).
  - Contrastar las métricas obtenidas contra las metas inmutables de los KRs (Macro-F1 $\ge$ 0.55, Recall alzas $\ge$ 70%).
  - Completar la Plantilla 4 (Impact Assessment Canvas) con datos de validación empírica real y estimación del ahorro económico generado.
- **Entregable Verificable:** `plantillas/plantilla_4_impact_assessment.md` completada con métricas auditables y logs de prueba.
- **Responsable:** Carlos Alcazar & Miguel Ángel Mori
- **Riesgo Principal:** Discrepancia entre las métricas de validación y el test ciego debido a quiebres estructurales en el mercado durante 2026.

### Semana 13 — Fase T: Transferencia, Cierre Técnico y Deck de Sustentación Final
- **Objetivo:** Consolidar el repositorio final de la PC2, redactar el manual de transferencia y preparar la defensa ante el jurado evaluador.
- **Actividades:**
  - Realizar auditoría integral de código, documentación y reproducibilidad de todo el repositorio.
  - Elaborar el deck de diapositivas final y ensayar la presentación oral de 10 minutos.
  - Verificar que el enlace de la aplicación en la nube se mantenga 100% operativo para la demostración en vivo.
- **Entregable Verificable:** Repositorio final cerrado en GitHub, `presentacion_pc2.pdf` y entrega formal en la plataforma de UTEC.
- **Responsable:** Equipo Completo (Stefano Canales, Carlos Flores, Carlos Alcazar, Miguel Ángel Mori)
- **Riesgo Principal:** Fallo de conexión o saturación de cuota de API durante la demostración en vivo de la sustentación presencial. Mitigación: video de respaldo pregrabado en local.

---

## Matriz Resumen de Responsabilidades

| Semana | Hito / Entregable | Fase PROMPT | Responsable Principal | Estado |
|:---:|---|:---:|---|:---:|
| **S7** | Dataset macroeconómico unificado ($t-1$) | M | Carlos Flores | Planificado |
| **S8** | Modelos A2 entrenados y comparativa de baseline | M | Carlos Alcazar | Planificado |
| **S9** | Umbral asimétrico $P^* = 0.25$ y motor G1 integrado | M | Stefano Canales | Planificado |
| **S10** | **Despliegue de Web App en Vercel + Supabase** | **M (Despliegue)** | Miguel Ángel Mori | **Crítico / Planificado** |
| **S11** | Validación piloto y cierre de Fase M | M | Stefano Canales & Carlos Flores | Planificado |
| **S12** | Evaluación sobre Test ciego y Plantilla 4 | P2 | Carlos Alcazar & Miguel Ángel Mori | Planificado |
| **S13** | Sustentación final y cierre de proyecto PC2 | T | Equipo Completo | Planificado |
