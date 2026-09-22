# Plantilla 2 — Data Readiness Assessment (Fase R)
**Curso:** AD5018 — Inteligencia Artificial para Negocios  
**Universidad:** Universidad de Ingeniería y Tecnología (UTEC)  
**Departamento:** Administración & Negocios Digitales · Malla 2024 — Ciclo 9  
**Proyecto:** Lunetra IA — Asistente Inteligente de Combustibles  
**Integrantes:** Stefano Canales · Carlos Flores · Carlos Alcazar · Miguel Ángel Mori  
**Fecha de entrega:** Semana 6 · 19 de septiembre de 2026  

---

## 1. Inventario de Datos

| Conjunto de Datos | Fuente Oficial / Proveedor | Formato | Volumen Verificado | Acceso Real Verificado | Periodicidad | Semáforo |
|---|---|---|---|---|---|:---:|
| **Conjunto 1: Precios diarios por estación de servicio** (Archivo A) | Osinergmin — Registro de Ventas Minoristas anonimizado (`part1.csv`) | CSV | 497,156 filas · 29.6 MB · 8,825 grifos únicos | Archivo descargado localmente y validado en `datos/` | Diario (59 días observados: 01/01/2026 al 28/02/2026) | 🟢 |
| **Conjunto 2: Histórico departamental de combustibles** (Archivos B y C consolidan una sola fuente) | Osinergmin — División de Supervisión Regional (Reportes mensuales SCOP-DOCS / Sistema PRICE) | CSV (`precios_combustibles_datos_crudos.csv`) y XLSX (`historico_precios_combustibles_peru_2020_2026.xlsx`) | 11,227 filas (crudos) · 80 meses continuos en 24 departamentos | Archivos descargados localmente y validados en `datos/` | Mensual (Ene 2020 a Ago 2026) | 🟢 |
| **Conjunto 3: Variables macrofinancieras y de mercado internacional** | BCRP (Tipo de cambio S//US$), EIA / FRED (WTI, Brent, Spot Gasolina US Gulf Coast), Yahoo Finance (VIX) | API REST / CSV | Pendiente de ingestión (estimado ~80 observaciones mensuales alineadas) | Pendiente de descarga automatizada mediante scripts de conexión | Diario / Mensual | 🔴 |

> *Nota metodológica sobre fuentes y destino de componentes:*
> - Los Archivos B y C corresponden exactamente a la misma fuente documental (Osinergmin SCOP-DOCS). Cuentan estrictamente como **un único conjunto de datos con dos presentaciones técnicas**, no como dos fuentes independientes.
> - **Mapeo a la arquitectura del producto:** El Conjunto 2 (80 meses) y las variables macroeconómicas del Conjunto 3 alimentan directamente el **Componente Analítico (Nivel A2)** para predecir la tendencia mensual. Por su parte, el Conjunto 1 (muestra transversal de 497,156 registros de grifos) alimenta el contexto de dispersión estadística (P10, P50, P90) que se inyecta en el prompt del **Componente Generativo (Nivel G1)**.

---

## 2. Data Readiness Checklist

| Criterio de Evaluación | Estado | Evidencia Concreta Verificada |
|---|:---:|---|
| **Disponibilidad física de insumos** | 🟢 | 497,156 registros diarios y serie histórica de 80 meses residen localmente en el entorno de ejecución (`datos/`). |
| **Integridad estructural primaria** | 🟢 | El archivo departamental no contiene nulos en sus 11,227 registros. El archivo diario posee estructura tabular regular de 11 columnas. |
| **Cobertura temporal del target macro** | 🟢 | 80 meses continuos (ene 2020 – ago 2026) cubren períodos de prepandemia, confinamiento, pico inflacionario global 2022 y normalización. |
| **Representatividad muestral minorista** | 🟡 | 8,825 estaciones a nivel nacional, con el 93.1% (8,219 grifos) reportando los 59 días completos. No obstante, **solo se cuenta con 59 días calendario (enero–febrero 2026)** y no existen partes 2 ni 3 en el lote. |
| **Atributos de localización geográfica** | 🔴 | El Archivo A **carece totalmente de variables de ubicación** (sin coordenadas GPS, distrito, provincia ni departamento). El código del local es un hash anonimizado. |
| **Variables macroeconómicas líderes** | 🔴 | Las series exógenas (crudo WTI, Brent, tipo de cambio BCRP, crack spread Costa del Golfo) no se encuentran integradas aún en el repositorio. |
| **Desbalance de clases en la variable objetivo** | 🟡 | Severo desbalance documentado en H2 (80.5% neutro, 12.5% sube, 6.9% baja), lo que descarta el uso de funciones de pérdida estándar y accuracy simple. |

---

## 3. Plan de Mitigación para Elementos en 🔴 y 🟡

Siguiendo el principio de honestidad técnica, se presenta el plan concreto de adquisición y mitigación con fechas perentorias para la Semana 7:

| Elemento Crítico | Semáforo | Acción Técnica de Mitigación | Responsable Designado | Fecha Comprometida |
|---|:---:|---|---|:---:|
| **Variables de mercado internacional** (WTI, Brent, Spot US Gulf Coast) | 🔴 | Ingestión vía API de la U.S. Energy Information Administration (EIA) o FRED mediante script de extracción automatizado `scripts/obtener_macro.py`. | Carlos Flores (Ingeniería de Datos) | Semana 7 (Día 3) |
| **Tipo de cambio bancario S//US$** | 🔴 | Descarga automatizada desde la API pública de series estadísticas del Banco Central de Reserva del Perú (BCRP, serie `PD04638PD`). | Miguel Ángel Mori (Data Pipelines) | Semana 7 (Día 3) |
| **Margen de refinación / Crack Spread** | 🔴 | Construcción de variable sintética: diferencia entre precio spot de gasolina refinada en la Costa del Golfo y crudo WTI, con desfase $t-1$. | Stefano Canales (Estrategia Analítica) | Semana 7 (Día 5) |
| **Ausencia de geolocalización en grifos** | 🔴 | **Decisión de delimitación de alcance:** No se forzará inferencia geográfica ficticia ni scraping no regulado. El producto se delimita a nivel departamental y distribución estadística global. | Equipo Completo | Cerrado en PC1 |
| **Desbalance de clases (H2)** | 🟡 | Implementación de técnicas de ponderación de clases (`class_weight='balanced'`), remuestreo temporal y función de pérdida asimétrica. | Carlos Alcazar (Modelado Predictivo) | Semana 8 |

---

## 4. Diagnóstico de Calidad de Datos

### 4.1 Valores Imposibles / Fuera de Rango (Anomalías Severas)
En el Archivo A (`precios_combustibles_anonimizados_20260301_part1.csv`), el análisis de rangos plausibles para gasolinas y diésel (regla de negocio: entre S/ 5.00 y S/ 30.00 por galón) detectó exactamente **16 valores imposibles**:
- `g_premium`: 2 observaciones atípicas (precios de S/ 1.50).
- `g_regular`: 2 observaciones con digitaciones erróneas extremas (precios de **S/ 1006.795** y **S/ 2000.00**).
- `diesel`: 12 registros anómalos (valores de S/ 4.15 y S/ 4.60 por galón, posiblemente correspondientes a litros o errores de punto decimal).
- **Tratamiento estricto:** El script `analisis/perfilado_datos.py` imputa formalmente `NaN` a estos 16 registros atípicos antes de calcular cualquier métrica estadística, evitando el sesgo de medias y varianzas.

### 4.2 Proporción de Valores Nulos por Combustible (Archivo A)
El análisis exhaustivo de los 497,156 registros arrojó:
- `g_premium`: **55.4%** de nulos (275,644 filas sin expendio de premium).
- `g_regular`: **48.4%** de nulos (240,476 filas).
- `diesel`: **44.3%** de nulos (220,062 filas).
- `gnv`: **96.4%** de nulos (479,368 filas). *El GNV requiere conexión a red troncal de gas natural, solo existente en Lima, Callao, Ica y zonas focalizadas.*
- `glp_g` (GLP Granel/Vehicular): **80.1%** de nulos (398,357 filas).
- `glp_e` (GLP Envasado): **61.8%** de nulos (307,130 filas).
- **Conclusión de producto:** El MVP se concentra exclusivamente en **Gasolina Regular y Premium**, que constituyen los combustibles vehiculares particulares de mayor representatividad y menor dispersión de ausencias.

### 4.3 Transición de Nomenclatura Regulatoria (Hallazgo H6)
- **Diagnóstico:** A raíz de la simplificación dispuesta por Osinergmin, en los datos mensuales coexisten `GASOHOL 90 PLUS` (enero 2020 a junio 2023) y `GASOHOL REGULAR` (marzo 2023 a agosto 2026).
- **Regla de equivalencia técnica verificada:**
  $$\text{Serie Regular Reconstruida} = \text{GASOHOL REGULAR} \cup \text{GASOHOL 90 PLUS}$$
  En el código se aplica: `serie_lima_reg = df_lima['GASOHOL REGULAR'].combine_first(df_lima['GASOHOL 90 PLUS'])`. Se verificó que durante la ventana de solapamiento de 4 meses no existen discrepancias significativas de nivel, permitiendo concatenar 80 meses continuos sin sesgo estructural.

### 4.4 Incompatibilidad Dimensional de Unidades
- `GNV` se comercializa y registra en metros cúbicos ($m^3$) o kilogramos ($kg$), mientras que las gasolinas y el diésel se expenden en galones estadounidenses ($gal$).
- `GLP` registra dualidad operativa: vehicular a granel ($gal$) y envasado en cilindros domésticos ($kg$).
- **Regla de integridad:** Se excluyen GNV y GLP del vector de entrenamiento para evitar distorsiones volumétricas y escalas dimensionales no conmensurables.

### 4.5 Desfase Temporal entre Fuentes (Hallazgo H10)
- El archivo diario de grifos abarca exclusivamente del **1 de enero de 2026 al 28 de febrero de 2026** (59 días).
- La serie histórica mensual departamental se extiende hasta **agosto de 2026** (80 meses).
- **Implicancia:** Es imposible mapear directamente grifos individuales sobre el horizonte mensual posterior a febrero 2026. Por lo tanto, la base de grifos se utiliza como muestra de corte transversal representativa de la estructura de dispersión (H5), no como serie de tiempo extendida.

---

## 5. Prevención de Data Leakage (Fuga de Datos)

El protocolo de modelado implementa medidas estrictas de separación temporal:

### 5.1 Protocolo de Partición Temporal Cronológica
> [!CAUTION]
> **Prohibición expresa de K-Fold aleatorio:**
> En series temporales de precios, la validación cruzada aleatoria tradicional destruye la estructura de autocorrelación e inyecta información del futuro en el pasado. Se prohíbe tajantemente el uso de `train_test_split(shuffle=True)`.

- **Esquema de partición adoptado (Split Cronológico):**
  - **Conjunto de Entrenamiento (Train):** Enero 2020 a Diciembre 2024 (60 meses, 75% de la serie). Permite capturar la dinámica post-COVID y el shock global 2022.
  - **Conjunto de Validación (Val):** Enero 2025 a Diciembre 2025 (12 meses, 15% de la serie). Empleado para sintonización de hiperparámetros y selección del umbral de corte asimétrico.
  - **Conjunto de Prueba Final (Test Out-of-Time):** Enero 2026 a Agosto 2026 (8 meses, 10% de la serie). Evaluación ciega de generalización fuera de muestra.

### 5.2 Análisis de Fuga Variable por Variable
| Variable Candidata | Riesgo de Leakage | Medida Preventiva Obligatoria |
|---|:---:|---|
| **Precio minorista local ($P_{t}$)** | Alto si es contemporáneo | Se emplea estrictamente como valor rezagado: $P_{t-1}, P_{t-2}, \dots$ |
| **Diferencias del precio ($\Delta P_t$)** | Crítico | Se calculan rezagadas: $\Delta P_{t-1} = P_{t-1} - P_{t-2}$ para predecir $\text{signo}(P_{t+1} - P_t)$. |
| **Crudo Internacional (WTI / Brent)** | Alto | Solo se permite ingresar el promedio del mes cerrado anterior ($WTI_{t-1}$) o la variación a $t-1$. |
| **Tipo de cambio (S//US$)** | Alto | Promedio mensual del período cerrado previo ($TC_{t-1}$). |
| **Margen de refinación (Crack Spread)** | Crítico | Al derivarse de precios spot internacionales, **solo puede utilizarse con rezago $t-1$**, dado que los balances de refinación del mes en curso no se conocen ex-ante. |

---

## 6. Suficiencia Muestral por Categoría y Desbalance de Clases

Para evaluar la viabilidad de la clasificación de tendencia, se analizó la frecuencia de eventos a nivel mensual y semanal:

### 6.1 Desbalance a Nivel Semanal en Grifos (Hallazgo H2)
Sobre 446,808 pares de observaciones a 7 días en gasolina regular:
- **Se Mantiene ($|\Delta_7| < \text{S/ } 0.01$):** **357,446 casos (80.0% a 80.5%)**
- **Sube ($\Delta_7 \ge +\text{S/ } 0.01$):** **56,745 casos (12.5% a 12.7%)**
- **Baja ($\Delta_7 \le -\text{S/ } 0.01$):** **32,617 casos (6.9% a 7.3%)**

### 6.2 Distribución en la Serie Mensual Departamental (80 meses en Lima)
Analizando las 79 variaciones mensuales consecutivas ($\Delta P_t = P_t - P_{t-1}$) con umbral de estabilidad neutral de $\pm \text{S/ } 0.15$:
- **Meses al alza ($\Delta P > +0.15$):** ~32 meses (40.5%)
- **Meses a la baja ($\Delta P < -0.15$):** ~24 meses (30.4%)
- **Meses estables ($|\Delta P| \le 0.15$):** ~23 meses (29.1%)

**Diagnóstico:** A nivel mensual departamental la distribución de clases es significativamente más equilibrada que a nivel semanal de grifo individual. Esto ratifica la decisión técnica de situar el componente analítico (A2) sobre la **tendencia mensual departamental** y no sobre el ruido diario de cada grifo.

---

## 7. Cumplimiento Normativo y Protección de Datos Personales (Ley N.° 29733)

### 7.1 Estado de los Datos en Origen
1. **Identificadores de Estaciones:** Las estaciones de servicio registradas ante Osinergmin son personas jurídicas (empresas comercializadoras de hidrocarburos). Conforme a la legislación peruana y la Ley N.° 29733 (Ley de Protección de Datos Personales), la información de personas jurídicas no constituye dato personal.
2. **Anonimización adicional:** El regulador suministró el código del establecimiento bajo un hash criptográfico unidireccional irreversible (`ANON_CO_LOCAL_VENTA`), imposibilitando la reidentificación de los propietarios o representantes legales.
3. **Riesgo en la fuente:** **Nulo / Bajo**.

### 7.2 Tratamiento de Privacidad en el MVP (Privacy by Design)
- **Cero captura de PII (Personally Identifiable Information):** El MVP de Lunetra IA operará sin registro obligatorio de usuarios, sin almacenar nombres, correos electrónicos, placas de vehículos ni números telefónicos.
- **Sin geolocalización GPS activa:** La interacción del usuario consistirá únicamente en seleccionar su departamento en un menú desplegable y definir su tipo de gasolina de interés.
- **Garantía ética:** Al no recopilarse datos personales, el producto se mantiene fuera del ámbito de registro de bancos de datos personales de la Autoridad Nacional de Protección de Datos Personales (ANPDP - MINJUSDH), garantizando un diseño ético y seguro.
