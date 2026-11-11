# Resultados medidos vs. OKRs de la PC1 — Lunetra IA

Los KRs son **los mismos congelados en la PC1** (`plantillas/plantilla_3_ai_product_canvas.md`,
sección 8). No se modificó ninguna meta.

**Fuentes de verdad reproducibles**
- Modelo: `reportes/metricas_a2.json` ← `python modelado/entrenamiento_a2.py`
- Capa de lenguaje: `reportes/auditoria_kr2.json` ← `python pipeline_inferencia.py --auditoria-kr2 60`;
  `mvp/web` → `npm test`; `mvp/evidencia/auditoria_llm.json` ← `npm run auditar-llm`
- Despliegue: `https://<url>/api/salud`

**Objetivo:** que el conductor particular de Lima decida cuándo y a qué precio cargar con una
recomendación confiable y sin datos inventados.

---

## Tabla resumen

| KR | Meta PC1 | Resultado real | Estado |
|---|---|---|:---:|
| **KR1a** · Recall en alzas (test ciego 2026) | ≥ 70% | **93.8%** (75 de 80 alzas, P\* = 0.25) | 🟢 Cumple |
| **KR1b** · Macro-F1 (test ciego 2026) | ≥ 0.55 | **0.206** con P\* = 0.25 · 0.442 con argmax | 🔴 No cumple |
| KR1 · Superar baseline de persistencia | Macro-F1 > 0.083 | 0.206 (2.5×) · 0.442 argmax (5.3×) | 🟢 Supera |
| **KR2** · Recomendaciones sin alucinación numérica (N ≥ 50) | 100% | Respaldo determinista: **100%** (60/60 Python, 72/72 MVP) · Gemini 3.5 Flash crudo: **100%** (27/27), pero N = 27 < 50 por la cuota gratuita | 🟡 Parcial |
| **KR3** · App pública en Vercel, respuesta < 1.5 s, Semana 10 | 100% | MVP construido y probado; despliegue **pendiente** | 🟡 Pendiente |
| **KR4** · Ahorro proyectado por carga de 8 galones | ≥ S/ 8.00 | **S/ 16.96** (8 × brecha P90–P10 de S/ 2.12) | 🟢 Cumple |

---

## KR1 — Modelo A2: matriz de confusión leída en costos para el negocio

Test ciego: 168 meses-departamento (ene–jul 2026). Costos del conductor (Plantilla 3):
**no avisar un alza = S/ 4.00** (8 gal × S/ 0.50 de salto medio, H3); **falsa alarma = S/ 0.80**
(adelantar la carga 3–4 días). Solo "SUBE" dispara una acción, así que solo se cobran esos dos errores.

**Modelo con umbral P\* = 0.25 (el que corre en el MVP)** — filas = real, columnas = predicho

| Real \ Predicho | MANTIENE | SUBE | BAJA |
|---|---:|---:|---:|
| MANTIENE (24) | 0 | 24 | 0 |
| SUBE (80) | 0 | **75** | 5 |
| BAJA (64) | 0 | 64 | 0 |

| Error | Casos | Costo unitario | Costo total |
|---|---:|---:|---:|
| Alza no avisada (FN) | 5 | S/ 4.00 | S/ 20.00 |
| Falsa alarma (FP) | 88 | S/ 0.80 | S/ 70.40 |
| **Costo por decisión** | 168 | | **S/ 0.54** |

**Comparación de costo por decisión**

| Regla | Macro-F1 | Recall alzas | Costo / decisión |
|---|---:|---:|---:|
| Baseline de persistencia ("todo se mantiene") | 0.083 | 0% | S/ 1.90 |
| Baseline inercia del signo | 0.228 | 15% | S/ 1.85 |
| Modelo A2, argmax | 0.442 | 66% | S/ 0.96 |
| **Modelo A2, P\* = 0.25 (MVP)** | 0.206 | **94%** | **S/ 0.54** |
| *Referencia: "avisar siempre que sube"* | *0.21* | *100%* | *S/ 0.42* |

**Lectura para el negocio**
- Frente al baseline obligatorio, el modelo reduce el costo de error del conductor de S/ 1.90 a
  S/ 0.54 por decisión (−72%): en 52 tanqueadas al año son ~S/ 71 menos de pérdida por mal timing.
- El Macro-F1 no llega a 0.55 porque el umbral asimétrico sacrifica precisión en MANTIENE/BAJA
  para no perder alzas. Es una decisión de diseño a favor del bolsillo del usuario, no un error.
- **Límite honesto:** en 2026 (régimen alcista, 48% de alzas) el modelo con P\* = 0.25 casi siempre
  avisa "sube" y una regla trivial de "avisar siempre" habría costado aún menos (S/ 0.42). El valor
  del modelo está en que *no* avisa siempre: en 2025 (10% de alzas) esa regla trivial habría
  generado falsas alarmas en 9 de cada 10 meses. Mejora pendiente: re-calibrar P\* por régimen y
  agregar las variables macro (WTI, Brent, tipo de cambio) que aún no se integraron.

## KR2 — Capa de lenguaje: métrica propia, separada de la del modelo

La métrica de G1 no es la exactitud del modelo sino la **fidelidad del texto al payload**: % de
recomendaciones sin cifras inventadas, con aviso de IA y con advertencia de incertidumbre cuando
corresponde. Se mide con `auditar_alucinacion_numerica` (Python) y su versión más estricta en el MVP
(`mvp/web/lib/prompts.ts`, que además detecta montos enteros y porcentajes).

| Generador | N | Sin cifras inventadas | Con aviso IA | Cumple contrato | Fuente |
|---|---:|---:|---:|---:|---|
| Respaldo determinista (Python, Fase M) | 60 | 100% | 100% | 100% | `reportes/auditoria_kr2.json` |
| Respaldo determinista (MVP, TypeScript) | 72 | 100% | 100% | 100% | `npm test` |
| **Gemini 3.5 Flash, texto crudo** | 27 | **100%** | 100% | 100% | `mvp/evidencia/auditoria_llm.json` |
| Texto final que ve el usuario (Gemini + guardarraíl/respaldo) | 72 | 100% | 100% | 100% | ídem |

Medición real del 11/11/2026 (`npm run auditar-llm`, modelo `gemini-3.5-flash`, plan gratuito):

- De los 72 casos, Gemini respondió **27** (14 departamentos). Los otros 45 recibieron HTTP 429:
  la cuota gratuita es de **20 peticiones por día y por modelo**. Esos casos pasaron al respaldo
  determinista, así que el usuario igual recibió un texto que cumple el contrato (72/72).
- En las 27 respuestas crudas: **0 cifras inventadas**, 27/27 con aviso de IA y 11/11 con la
  advertencia de incertidumbre cuando correspondía. El guardarraíl no tuvo que corregir ninguna.
- **El KR2 queda parcial:** la tasa es de 100%, pero N = 27 no llega al mínimo de 50. Para cerrarlo
  hay que repetir la auditoría con una clave con facturación activa o sumando corridas de días
  distintos. No se declara cumplido.
- Nota técnica: `gemini-2.5-flash` ya no está disponible para claves nuevas (HTTP 404), por eso el
  MVP usa ahora `gemini-3.5-flash` por defecto.

## KR3 — Despliegue

| Ítem | Estado |
|---|---|
| App Next.js con el modelo y la capa de lenguaje integrados | ✅ `mvp/web`, build de producción OK |
| Respuesta del servidor con respaldo determinista (local) | ✅ ~1 ms de cómputo del modelo |
| URL pública en Vercel | ⏳ *pendiente: pegar URL y fecha* |
| Latencia con Gemini (p50/p95) | 🔴 **2.9 s / 6.0 s** en las 27 respuestas reales: por encima de la meta de 1.5 s. Sin Gemini (respaldo) responde en < 0.5 s |
| Fecha de despliegue vs. meta Semana 10 | ⏳ *pendiente* — si fue después de S10, declararlo |

**Desviación declarada:** la PC1 previó Supabase como base de datos. El MVP no la necesita: los
datos de inferencia son estáticos y se actualizan con un commit al reentrenar. Se mantiene como
mejora futura para registrar feedback anónimo de usuarios.

## KR4 — Ahorro por dispersión

Muestra oficial de Osinergmin (4,428 grifos con gasolina regular en Lima, 28-feb-2026):
P10 = S/ 13.39 · P50 = S/ 14.30 · P90 = S/ 15.70 → brecha S/ 2.12/galón →
**8 × 2.12 = S/ 16.96 por tanqueada** (meta ≥ S/ 8.00). Es ahorro **potencial**: depende de que el
usuario encuentre un grifo cerca del P10; las pruebas con usuarios deben registrar si la banda
cambió dónde cargan.
