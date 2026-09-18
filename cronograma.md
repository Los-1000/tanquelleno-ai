# Cronograma de Trabajo: Semanas 7 a 13
**Curso:** AD5018 — Inteligencia Artificial para Negocios (UTEC, Framework PROMPT v2.0)  
**Proyecto:** TanqueLleno AI  
**Equipo:** `[COMPLETAR: Nombre Completo 1, Nombre Completo 2, Nombre Completo 3, Nombre Completo 4]`  
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
- **Responsable:** `[COMPLETAR: Responsable 1 (Ingeniería de Datos)]`
- **Riesgo Principal:** Cambios en los endpoints o credenciales de las APIs externas que retrasen la consolidación del dataset antes del cierre de semana.

### Semana 8 — Fase M: Entrenamiento del Componente Analítico (Nivel A2)
- **Objetivo:** Entrenar los modelos de clasificación supervisada de tendencia mensual y contrastar su desempeño contra el baseline de persistencia.
- **Actividades:**
  - Implementar el esquema de partición cronológica: Train (2020–2024), Val (2025) y Test (2026).
  - Entrenar el Baseline Obligatorio de Persistencia ("próximo mes = mes actual").
  - Ajustar modelos candidatos: Regresión Logística Regularizada con balanceo de pesos (`class_weight='balanced'`) y LightGBM Classifier.
  - Evaluar métricas iniciales: Macro-F1, Precision y Recall por clase.
- **Entregable Verificable:** Notebook/script `modelado/entrenamiento_a2.py` con tabla comparativa de métricas en conjunto de validación.
- **Responsable:** `[COMPLETAR: Responsable 2 (Machine Learning)]`
- **Riesgo Principal:** Sobreajuste (overfitting) en modelos de árboles debido a la muestra acotada de 80 meses si no se aplica regularización estricta.

### Semana 9 — Fase M: Calibración de Umbral Asimétrico e Integración con G1
- **Objetivo:** Optimizar el umbral de corte de probabilidad ($P^*$) según la matriz de costo asimétrico y acoplar el generador en lenguaje natural.
- **Actividades:**
  - Barrido de umbrales en el set de validación (2025) para minimizar la función de costo personalizada ($C_{FN}=4.0$, $C_{FP}=0.8$).
  - Fijar el umbral óptimo de alerta de alza en $P^* \approx 0.25$.
  - Implementar el módulo `generativo/motor_g1.py` con llamadas a la API de Google Gemini Flash utilizando el System Prompt blindado.
  - Ejecutar pruebas de estrés para verificar 0% de alucinaciones en los percentiles inyectados.
- **Entregable Verificable:** Script de inferencia integrada end-to-end `pipeline_inferencia.py` recibiendo payload y retornando recomendación en texto.
- **Responsable:** `[COMPLETAR: Responsable 3 (Integración de Modelos & Prompt Engineering)]`
- **Riesgo Principal:** Variabilidad en la latencia de la API de Gemini que afecte los tiempos de respuesta del pipeline.

### Semana 10 — Fase M: Construcción de Web App y Despliegue en Producción
- **Objetivo:** Publicar la aplicación web interactiva en la nube, asegurando disponibilidad pública antes del límite de la Semana 11.
- **Actividades:**
  - Desarrollar la interfaz en Streamlit (`app.py`) con selectores de departamento y tipo de combustible.
  - Incorporar gráficos interactivos de la banda de dispersión (P10, Mediana, P90).
  - Conectar el repositorio de GitHub con Streamlit Community Cloud.
  - Realizar pruebas de carga en móviles y verificar tiempos de respuesta inferiores a 3 segundos.
- **Entregable Verificable:** URL pública y activa de la aplicación desplegada (`https://tanquelleno-ai.streamlit.app` o equivalente).
- **Responsable:** `[COMPLETAR: Responsable 4 (Despliegue & Frontend Streamlit)]`
- **Riesgo Principal:** Errores de dependencias en el entorno virtual de Streamlit Cloud (falla común de bibliotecas C en Linux). Mitigación: congelar `requirements.txt` en local.

### Semana 11 — Fase M: Pruebas con Usuarios Piloto y Cierre de Fase M
- **Objetivo:** Ejecutar pruebas de usabilidad con 10 conductores reales de Lima y calibrar los textos generativos con base en el feedback.
- **Actividades:**
  - Someter la app desplegada a sesiones de uso guiadas con usuarios particulares.
  - Recolectar retroalimentación mediante los botones de utilidad [👍 / 👎].
  - Evaluar la claridad de las recomendaciones y verificar que los usuarios comprendan la advertencia de estimación estadística.
  - Congelar los pesos finales del modelo analítico y el System Prompt.
- **Entregable Verificable:** Reporte de pruebas con usuarios piloto (`analisis/feedback_piloto_s11.md`) y confirmación de estabilidad del despliegue.
- **Responsable:** `[COMPLETAR: Responsable 1 & Responsable 3]`
- **Riesgo Principal:** Dificultad para reclutar conductores que realicen pruebas activas en el plazo establecido.

### Semana 12 — Fase P2: Medición de Impacto y Elaboración de la Plantilla 4
- **Objetivo:** Medir el cumplimiento cuantitativo de los OKRs comprometidos en la PC1 y documentar formalmente la Fase P2.
- **Actividades:**
  - Evaluar el modelo analítico sobre el conjunto de prueba ciego final (meses de 2026).
  - Contrastar las métricas obtenidas contra las metas inmutables de los KRs (Macro-F1 $\ge$ 0.55, Recall alzas $\ge$ 70%).
  - Completar la Plantilla 4 (Impact Assessment Canvas) con datos de validación empírica real y estimación del ahorro económico generado.
- **Entregable Verificable:** `plantillas/plantilla_4_impact_assessment.md` completada con métricas auditables y logs de prueba.
- **Responsable:** Equipo Completo
- **Riesgo Principal:** Discrepancia entre las métricas de validación y el test ciego debido a quiebres estructurales en el mercado durante 2026.

### Semana 13 — Fase T: Transferencia, Cierre Técnico y Deck de Sustentación Final
- **Objetivo:** Consolidar el repositorio final de la PC2, redactar el manual de transferencia y preparar la defensa ante el jurado evaluador.
- **Actividades:**
  - Realizar auditoría integral de código, documentación y reproducibilidad de todo el repositorio.
  - Elaborar el deck de diapositivas final y ensayar la presentación oral de 10 minutos.
  - Verificar que el enlace de la aplicación en la nube se mantenga 100% operativo para la demostración en vivo.
- **Entregable Verificable:** Repositorio final cerrado en GitHub, `presentacion_pc2.pdf` y entrega formal en la plataforma de UTEC.
- **Responsable:** Equipo Completo
- **Riesgo Principal:** Fallo de conexión o saturación de cuota de API durante la demostración en vivo de la sustentación presencial. Mitigación: video de respaldo pregrabado en local.

---

## Matriz Resumen de Responsabilidades

| Semana | Hito / Entregable | Fase PROMPT | Responsable | Estado |
|:---:|---|:---:|---|:---:|
| **S7** | Dataset macroeconómico unificado ($t-1$) | M | `[COMPLETAR: Responsable 1]` | Planificado |
| **S8** | Modelos A2 entrenados y comparativa de baseline | M | `[COMPLETAR: Responsable 2]` | Planificado |
| **S9** | Umbral asimétrico $P^* = 0.25$ y motor G1 integrado | M | `[COMPLETAR: Responsable 3]` | Planificado |
| **S10** | **Despliegue de Web App en Streamlit Community Cloud** | **M (Despliegue)** | `[COMPLETAR: Responsable 4]` | **Crítico / Planificado** |
| **S11** | Validación piloto y cierre de Fase M | M | `[COMPLETAR: Responsable 1]` | Planificado |
| **S12** | Evaluación sobre Test ciego y Plantilla 4 | P2 | Equipo Completo | Planificado |
| **S13** | Sustentación final y cierre de proyecto PC2 | T | Equipo Completo | Planificado |
