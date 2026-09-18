# Guion de Sustentación — Deck de Presentación PC1

**Proyecto:** TanqueLleno AI  
**Curso:** AD5018 — Inteligencia Artificial para Negocios (UTEC, Framework PROMPT v2.0)  
**Evaluación:** Práctica Calificada 1 (PC1) · Fases P, R y O  
**Equipo:** `[COMPLETAR: Nombre Completo 1, Nombre Completo 2, Nombre Completo 3, Nombre Completo 4]`  
**Duración Estimada:** 10 minutos (1 minuto por lámina)  

---

### Diapositiva 1: Portada y Presentación del Proyecto
- **Título:** TanqueLleno AI — Optimización Inteligente del Abastecimiento de Combustible
- **Subtítulo:** Propuesta de Producto de IA aplicada al Mercado Minorista de Hidrocarburos (Fases P, R y O)
- **Mensaje Central del Ponente:** "Buenos días profesor y jurado. Hoy presentamos TanqueLleno AI, una solución basada en inteligencia artificial diseñada bajo el marco PROMPT v2.0 para resolver la asimetría informativa y la incertidumbre en los precios de combustibles que sufren los conductores de Lima."
- **Datos en Lámina:** Curso AD5018, Ciclo 2026-II, UTEC, Integrantes del equipo.

---

### Diapositiva 2: El Problema y el Usuario Específico (Fase P)
- **Título:** El Problema: Opacidad en la Dispersión e Incertidumbre de Ajustes
- **Mensaje Central del Ponente:** "No nos dirigimos a 'la gente' ni a 'los conductores en general'. Nuestro usuario es el conductor particular de Lima Metropolitana que usa su vehículo a diario para trabajar, carga 8 galones de gasolina a la semana y paga el combustible de su propio bolsillo. Su problema real no es la falta de una app, sino la incapacidad de saber si hoy le conviene llenar el tanque o esperar, y si su grifo habitual le está cobrando un sobreprecio invisible."
- **Datos de Respaldo:**
  - Segmento: Persona natural, 25–40 km diarios, 8 galones/semana (`⚠️ SUPUESTO DECLARADO`).
  - Problema formulado estrictamente sin mencionar tecnología.
  - Causa raíz: Heterogeneidad de márgenes minoristas y rezagos de 2 a 6 semanas en la transmisión mayorista.

---

### Diapositiva 3: Evidencia Empírica y Consecuencia Medible
- **Título:** La Evidencia: La Brecha Entre Grifos Supera a la Variación en el Tiempo
- **Mensaje Central del Ponente:** "Los datos oficiales de Osinergmin al 28 de febrero de 2026 revelan un hecho contundente: en un mismo día, la diferencia entre el percentil 10 y el percentil 90 de la gasolina regular es de S/ 2.12 por galón. Por ello, comprar en el grifo equivocado le cuesta al conductor S/ 17 por tanqueada, casi S/ 70 al mes. Además, cuando el precio sube, salta en promedio S/ 0.50 de golpe."
- **Datos de Respaldo:**
  - Hallazgo H5: P10 = S/ 13.39, Mediana = S/ 14.30, P90 = S/ 15.70 $\rightarrow$ Brecha de S/ 2.12/galón.
  - Pérdida económica calculada: $8 \text{ gal} \times \text{S/ } 2.12 = \text{S/ } 16.96$ por semana = **S/ 67.84 al mes**.
  - Hallazgo H1: 96.1% de inercia diaria. Hallazgo H3: salto medio al subir de +S/ 0.503/galón.

---

### Diapositiva 4: Diagnóstico de Datos y Semáforo Honesto (Fase R)
- **Título:** Data Readiness: Qué Tenemos y Qué Falta Honestamente
- **Mensaje Central del Ponente:** "En cumplimiento estricto de las reglas de honestidad de la rúbrica, no pintamos un semáforo en verde sin evidencia. Disponemos de 80 meses de serie mensual limpia y 497 mil registros diarios de grifos donde limpiamos 16 valores imposibles. Sin embargo, declaramos en rojo que aún no tenemos las variables macroeconómicas de crudo y tipo de cambio, las cuales ingresarán en la Semana 7 vía API, y dejamos explícito que los datos no tienen GPS."
- **Datos de Respaldo:**
  - 🟢 80 meses Osinergmin continuos (ene 2020 – ago 2026, 24 departamentos).
  - 🟢 497,156 registros diarios (59 días, 8,825 grifos, 93.1% completos).
  - 🟡 Desbalance de clases a 7 días (80.5% neutro, 12.5% sube, 6.9% baja).
  - 🔴 Variables macroeconómicas (WTI, Brent, TC BCRP): Plan de ingestión en Semana 7.
  - 🔴 Ausencia de geolocalización GPS: Delimitación honesta de alcance (sin mapas).

---

### Diapositiva 5: Arquitectura de Producto y Patrón de Conexión (Fase O)
- **Título:** Arquitectura Dual: Componentes A2 + G1 (Patrón 1)
- **Mensaje Central del Ponente:** "TanqueLleno AI conecta un modelo analítico de Machine Learning con un modelo generativo de lenguaje mediante el Patrón 1. Nuestro eje de ambición está puesto en el componente analítico A2, mientras que el generativo G1 se mantiene deliberadamente en el piso de complejidad para garantizar cero alucinaciones y foco en el valor para el negocio."
- **Datos de Respaldo:**
  - Diagrama de flujo: Usuario $\rightarrow$ Pipeline A2 $\rightarrow$ Payload cuantitativo validado $\rightarrow$ Motor G1 $\rightarrow$ Salida.
  - Payload exacto: `tendencia`, `probabilidad_alza`, `confianza`, `P10`, `P50`, `P90`.
  - Declaración explícita de ambición: **Componente Analítico (A2)**.

---

### Diapositiva 6: Componente Analítico A2 & Model Design Canvas
- **Título:** El Cerebro Analítico: Umbral Asimétrico y Pérdida Ponderada
- **Mensaje Central del Ponente:** "No usamos accuracy simple porque predecir siempre 'se mantiene' daría 80% de acierto engañoso. Nuestro target es predecir la tendencia mensual departamental. Como no advertir una subida le cuesta S/ 4.00 al conductor y una falsa alarma solo S/ 0.80, calibramos el umbral de decisión en 25% en vez del 50% tradicional. Superamos obligatoriamente el baseline de persistencia."
- **Datos de Respaldo:**
  - Baseline: Persistencia ("el próximo mes será igual").
  - Métrica clave: Macro-F1 y Recall en alzas (Meta $\ge$ 70%).
  - Razón de costos: $C_{FN} / C_{FP} = 5.0 \rightarrow P^* \approx 0.25$.
  - Validación temporal: Train (2020–2024), Val (2025), Test (2026). Jamás K-fold aleatorio.

---

### Diapositiva 7: Componente Generativo G1 & System Prompt
- **Título:** El Interfaz Generativo: Traducción Segura y Empática
- **Mensaje Central del Ponente:** "El modelo generativo recibe la salida del modelo A2 y la traduce a recomendaciones prácticas para el conductor. Su System Prompt está fuertemente restringido: tiene prohibición estricta de inventar precios o grifos, está obligado a avisar si la confianza estadística es baja y recuerda siempre que es una estimación probabilística, no una garantía comercial."
- **Datos de Respaldo:**
  - Modelo: Google Gemini Flash API (latencia < 1s, costo marginal).
  - Reglas éticas: Aviso de interacción con IA, transparencia de incertidumbre, descargo legal.
  - Salida: Diagnóstico de tendencia + Acción sugerida + Banda de precio referencial.

---

### Diapositiva 8: Alcance del MVP y Despliegue en Producción
- **Título:** Alcance Rígido y Despliegue en la Nube
- **Mensaje Central del Ponente:** "Definimos con total claridad los límites del MVP. La aplicación incluye la predicción mensual, la recomendación redactada y el contexto de dispersión de precios. Excluimos tajantemente geolocalización GPS, el 'grifo más cercano' y apps móviles nativas. Nos comprometemos a desplegar la Web App en Streamlit Community Cloud en la Semana 10, mucho antes del cierre del curso."
- **Datos de Respaldo:**
  - Plataforma: Streamlit Community Cloud conectada a GitHub.
  - Fecha comprometida: **Semana 10** (hito temprano para evitar el riesgo de despliegues de último minuto).
  - Exclusiones claras: Sin mapas GPS, sin ruteo, sin cobros ni pagos.

---

### Diapositiva 9: Cronograma y Responsabilidades (Semanas 7 a 13)
- **Título:** Plan de Ejecución: De la Teoría al Impacto
- **Mensaje Central del Ponente:** "Nuestro cronograma alinea cada semana con las fases del curso. Las Semanas 7 a 11 cubren la Fase M de modelado, cerrando con el despliegue en la Semana 10 y pruebas piloto en la Semana 11. La Semana 12 evalúa el impacto real sobre el test set para la Plantilla 4, y la Semana 13 concluye con la transferencia y sustentación de la PC2."
- **Datos de Respaldo:**
  - S7: Ingestión macro ($t-1$).
  - S8: Entrenamiento A2 vs Baseline.
  - S9: Umbral asimétrico y motor G1.
  - S10: **Despliegue público en Streamlit Cloud**.
  - S11: Piloto con conductores.
  - S12: Medición de KRs y Plantilla 4.
  - S13: PC2 y sustentación final.

---

### Diapositiva 10: OKRs Inmutables, Riesgos y Criterio de Éxito
- **Título:** Compromisos Inmutables (OKRs) y Gestión de Riesgos
- **Mensaje Central del Ponente:** "Conforme a la regla del curso, nuestros OKRs quedan congelados hoy en la PC1. Comprometemos un Macro-F1 mayor a 0.55 frente al baseline de 0.33, un Recall en alzas de al menos 70%, cero alucinaciones de precios y un ahorro potencial de S/ 8 por carga. Gestionamos los riesgos de overfitting con regularización y los riesgos de API con caching local. Muchas gracias."
- **Datos de Respaldo:**
  - KR 1: Macro-F1 $\ge$ 0.55 y Recall $\ge$ 70% en test ciego 2026.
  - KR 2: 0% de alucinaciones en recomendaciones evaluadas.
  - KR 3: App desplegada y operativa en Semana 10.
  - KR 4: Ahorro modelado $\ge$ S/ 8.00 por carga típica frente al P90.
