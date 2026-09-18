# Evidencia Empírica y Perfilado de Datos: Hallazgos H1 – H10

**Proyecto:** TanqueLleno AI — Sistema de Predicción de Tendencia de Precios y Optimización de Carga  
**Curso:** AD5018 — Inteligencia Artificial para Negocios (UTEC, Framework PROMPT v2.0)  
**Fecha de corte analítico:** 2026-03-01  
**Fuentes analizadas:**
1. Archivo A: Registro diario por grifo a nivel nacional (`precios_combustibles_anonimizados_20260301_part1.csv`, 497,156 filas, 8,825 grifos únicos, 59 días).
2. Archivo B y C: Serie histórica mensual por departamento Osinergmin SCOP-DOCS (`precios_combustibles_datos_crudos.csv` y `historico_precios_combustibles_peru_2020_2026.xlsx`, 80 meses continuos: enero 2020 – agosto 2026).

---

## Resumen de Hallazgos y Decisiones de Arquitectura de Producto

| # | Hallazgo | Evidencia Cuantitativa Verificada | Implicancia Directa en Diseño de Producto / IA |
|---|---|---|---|
| **H1** | **Inercia casi total en precios diarios por grifo** | El **96.02% (~96.1%)** de los pares grifo-día no registran cambio en gasolina regular. | Desaconseja un modelo predictivo diario por grifo individual (ruido extremo, target casi invariante). El producto no debe prometer alertas diarias a nivel estación. |
| **H2** | **Fuerte desbalance de clases a 7 días** | A 7 días, **80.0% (~80.5%)** se mantiene, **12.7% (~12.5%)** sube y **7.3% (~6.9%)** baja. | Una métrica de accuracy simple del 80% es trivial (prediciendo siempre "se mantiene"). Exige optimizar métricas con costo asimétrico (Recall en subidas, Macro-F1). |
| **H3** | **Magnitud de saltos es discreta y asimétrica** | Cuando el precio se mueve, salta en promedio **+S/ 0.399 a +S/ 0.503** al subir y **−S/ 0.341 a −S/ 0.358** al bajar. | El costo de no anticipar una subida (+S/ 0.50/galón = S/ 4.00 por tanqueada) es 47% mayor que el beneficio de una bajada promedio. Justifica un umbral de decisión asimétrico. |
| **H4** | **Alta prevalencia de estaciones estáticas** | El **29.7%** de los grifos con $\ge 30$ observaciones jamás cambió su precio en los 59 días (desviación estándar = 0). | Refuerza que la fijación de precios minorista responde a conductas comerciales locales rígidas y no a ajustes dinámicos de mercado diario. |
| **H5** | **La dispersión transversal supera a la volatilidad temporal** | Al 28 feb 2026 (4,428 grifos con regular): Media S/ 14.42, P10 = S/ 13.39, P90 = S/ 15.70. **Brecha intercuartil P90–P10 = S/ 2.12 a S/ 2.31/galón**. | **Pilar central del producto:** La ganancia del usuario no radica en predecir micro-cambios diarios, sino en saber cómo posicionarse frente a la dispersión estructural de S/ 17 por tanqueada combinada con la tendencia mensual. |
| **H6** | **Ruptura de nomenclatura regulatoria (Osinergmin)** | Hasta jun 2023 regía "Gasohol 90/95/97 Plus"; desde mar 2023 se implementó "Gasohol Regular y Premium". Solapamiento formal de 4 meses (mar–jun 2023). | Requiere regla de homología verificada en el preprocesamiento: enlazar Gasohol 90 Plus con Gasohol Regular para construir una serie continua sin saltos artificiales. |
| **H7** | **Serie histórica mensual de Lima reconstruida** | 80 meses continuos (ene 2020 – ago 2026): Media = S/ 15.65 – 15.67, Desv. = S/ 2.70 – 2.71, Mín = S/ 10.72 (mayo 2020), Máx = S/ 22.43 (junio 2022). | Provee la serie macro mensual adecuada para entrenar el modelo analítico A2 de tendencia departamental. Refleja ciclos reales (pandemia, guerra Ucrania 2022, estabilización). |
| **H8** | **Inercia mensual moderada a débil** | Autocorrelación de primeras diferencias mensuales: Lag 1 = **0.28 – 0.32**, Lag 2 = **−0.16**, Lag 3 = **−0.10 a −0.13**. | Un modelo puramente autorregresivo (AR) tiene techo predictivo limitado; se justifica incorporar variables macroeconómicas exógenas (crudo WTI/Brent, tipo de cambio). |
| **H9** | **Señal estacional preliminar en Marzo** | Marzo registra históricamente un incremento medio de **+S/ 0.99 a +S/ 1.01/galón**, pero con solo 7 observaciones anuales. | **Declarado estrictamente como indicio exploratorio**, no como hecho estilizado concluyente. No se debe sobreparametrizar el modelo con factores estacionales rígidos. |
| **H10** | **Hueco temporal entre registros** | El archivo diario de grifos concluye el 28 de febrero de 2026; la serie mensual de Osinergmin se extiende hasta agosto de 2026. | El archivo diario no puede utilizarse como variable contemporánea del target mensual en 2026. Se utiliza exclusivamente como benchmark de dispersión estática. |

---

## Detalle Técnico de los Hallazgos

### Hallazgo H1: Inercia diaria por grifo
- **Cálculo:** Se ordenó la base de datos de 497,156 filas cronológicamente por código anonimizado de estación (`ANON_CO_LOCAL_VENTA`) y fecha de evaluación (`fe_eval_dt`), calculando la primera diferencia:
  $$\Delta P_{i,t} = P_{i,t} - P_{i,t-1}$$
- **Resultado:** De las observaciones válidas consecutivas para `g_regular`, el 96.02% de los casos registra $\Delta P = 0$.
- **Conclusión de negocio:** Los grifos no ajustan precios al ritmo de los titulares ni de los mercados internacionales. El intento de crear una "IA predictiva diaria por grifo" generaría falsas alertas continuas o predeciría trivialmente cero cambio.

### Hallazgo H2: Fuerte desbalance de clases a horizonte semanal
- **Cálculo:** Diferencia a 7 días $\Delta_7 P_{i,t} = P_{i,t} - P_{i,t-7}$. Clasificación en 3 estados con umbral de sensibilidad de $\pm \text{S/ } 0.01$:
  - Neutro / Se Mantiene: $|\Delta_7| < 0.01 \rightarrow 80.0\% \text{ a } 80.5\%$
  - Sube: $\Delta_7 \ge +0.01 \rightarrow 12.5\% \text{ a } 12.7\%$
  - Baja: $\Delta_7 \le -0.01 \rightarrow 6.9\% \text{ a } 7.3\%$
- **Impacto metodológico:** La clase minoritaria (bajada) representa menos del 8% de los casos. Cualquier algoritmo minimizador de Error Cuadrático Medio o Maximización de Accuracy convergerá a predecir siempre "Se Mantiene". Por tanto, se adopta como métrica obligatoria Macro-F1 y función de pérdida ponderada por costo.

### Hallazgo H3: Asimetría en la magnitud del ajuste
- **Cálculo:** Media condicional de variaciones estrictamente distintas de cero.
  - Media de incrementos: $+ \text{S/ } 0.399 \text{ a } 0.503 \text{ por galón}$.
  - Media de reducciones: $- \text{S/ } 0.341 \text{ a } 0.358 \text{ por galón}$.
- **Implicancia en la decisión del usuario:** Si un conductor no se anticipa a una subida, asume un encarecimiento inmediato de aproximadamente S/ 0.50 por galón (S/ 4.00 en una carga típica de 8 galones). Por el contrario, si anticipa erróneamente una subida y llena el tanque antes, el costo de oportunidad es marginal (el costo financiero de adelantar 3 o 4 días la compra, ~S/ 0.80). Esta asimetría económica de $5:1$ fundamenta la calibración del umbral óptimo de decisión en $P^* = 0.25$ en el Model Design Canvas.

### Hallazgo H4: Estaciones inmóviles
- **Cálculo:** Grifos con al menos 30 días de reporte activo durante enero y febrero de 2026.
  - Total grifos con $N \ge 30$: 4,327 estaciones.
  - Grifos con varianza nula ($\sigma = 0$): 1,283 estaciones (**29.7%**).
- **Interpretación:** Casi un tercio de las estaciones de servicio en el Perú opera con precios completamente fijos durante meses, posiblemente por contratos comerciales cerrados, esquemas de franquicia cautivos o zonas geográficas sin competencia directa.

### Hallazgo H5: La dispersión transversal como fuente primaria de ahorro
- **Cálculo al corte del 28 de febrero de 2026 (4,247 a 4,428 grifos activos con gasolina regular):**
  - Media: S/ 14.35 a S/ 14.42 por galón.
  - Desviación estándar: S/ 0.83 a S/ 0.91 por galón.
  - Percentil 10 (P10): S/ 13.38 a S/ 13.39.
  - Mediana (P50): S/ 14.30.
  - Percentil 90 (P90): S/ 15.50 a S/ 15.70.
  - **Brecha P90 − P10:** **S/ 2.12 a S/ 2.31 por galón**.
- **Impacto en el valor de la solución:**
  $$\text{Diferencial por carga (8 galones)} = 8 \times \text{S/ } 2.12 = \text{\textbf{S/ 16.96}}$$
  $$\text{Diferencial mensual (4 cargas)} = 4 \times \text{S/ } 16.96 = \text{\textbf{S/ 67.84}}$$
  La variación mensual esperada del mercado ronda los S/ 0.20 – S/ 0.50/galón, mientras que la brecha simultánea entre grifos alcanza los S/ 2.12/galón. Por ello, la propuesta de valor integra la tendencia con el encuadre de dispersión.

### Hallazgo H6: Homogeneización de la serie histórica
- **Antecedente normativo:** Decreto Supremo N.° 014-2021-EM y Resoluciones complementarias de Osinergmin dispusieron la simplificación de gasolinas en dos tipos: Regular y Premium, dejando de expenderse las denominaciones por octanaje (84, 90, 95, 97, 98).
- **Evidencia en datos:** En la base departamental de Lima, hasta junio de 2023 se registraba `GASOHOL 90 PLUS`. Desde marzo de 2023 apareció `GASOHOL REGULAR`.
- **Regla técnica adoptada:** `serie_regular = GASOHOL REGULAR.combine_first(GASOHOL 90 PLUS)`. Se valida que no existen distorsiones de nivel ni saltos de varianza durante la ventana de solapamiento.

### Hallazgo H7: Serie de 80 meses de Lima
- **Propiedades estadísticas (2020-01 a 2026-08):**
  - Mínimo histórico: S/ 10.72 (Mayo 2020, colapso de demanda por COVID-19 y confinamiento estricto).
  - Máximo histórico: S/ 22.43 (Junio 2022, shock geopolítico y crisis energética global por conflicto Rusia-Ucrania).
  - Promedio de 80 meses: S/ 15.65 a S/ 15.67.
  - Desviación estándar: S/ 2.70 a S/ 2.71.
- **Utilidad:** Serie mensual limpia para validación temporal con Train (2020–2024), Val (2025) y Test (2026).

### Hallazgo H8: Dinámica autoregresiva débil
- **Coeficientes de autocorrelación de $\Delta P_t$:**
  - $\rho_1 \approx 0.28 - 0.32$
  - $\rho_2 \approx -0.16$
  - $\rho_3 \approx -0.10 \text{ a } -0.13$
- **Diagnóstico:** El precio no sigue un paseo aleatorio puro, pero la inercia autorregresiva se disipa casi por completo después del primer rezago. Esto demuestra empíricamente por qué un analista o una hoja de cálculo con promedios móviles simples yerra sistemáticamente: se requieren variables líderes externas (crudo internacional y tipo de cambio).

### Hallazgo H9: Indicio estacional en Marzo
- **Observación empírica:** El cambio intermensual promedio registrado en los meses de marzo a lo largo de la muestra es de $+ \text{S/ } 0.99 \text{ a } + \text{S/ } 1.01$ por galón.
- **Rigor metodológico:** Al disponerse únicamente de 7 observaciones de marzo en la serie de 80 meses, este patrón se clasifica formalmente como **indicio exploratorio preliminar**. No constituye una regla determinística, pues los shocks globales de 2022 distorsionaron fuertemente la media de dicho mes.

### Hallazgo H10: Desalineación temporal entre conjuntos de datos
- **Divergencia identificada:** El archivo de precios a nivel de estación individual finaliza el 28 de febrero de 2026. Por su parte, la serie histórica consolidada de Osinergmin (`historico_precios_combustibles_peru_2020_2026.xlsx`) contiene reportes mensuales hasta agosto de 2026.
- **Decisión de modelado:** Ambos conjuntos operan en niveles de agregación y ventanas distintas. Por ende, la base diaria se utiliza exclusivamente para contextualizar la dispersión transversal (H5) y documentar la inercia de corto plazo (H1–H4), mientras que la base de 80 meses es el insumo de modelado para el componente analítico A2.

---

*Figuras de respaldo generadas por `analisis/perfilado_datos.py` disponibles en el directorio `analisis/figuras/`.*
