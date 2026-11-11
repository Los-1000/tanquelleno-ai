# Plantilla 4 — Impact Assessment: Riesgos, Regulación e Impacto (Lunetra IA)

**Proyecto:** Lunetra IA — "¿Lleno hoy o espero?"
**Equipo:** Stefano Canales · Carlos Flores · Carlos Alcazar · Miguel Ángel Mori
**Fase:** P2 — Pilotaje e Impacto (PC2)
**Componentes evaluados:** Modelo analítico A2 · Capa de lenguaje G1 · *(no hay agente: el MVP no ejecuta acciones por el usuario)*

---

## 1. Matriz de riesgos y mitigaciones

Escala: Probabilidad / Impacto = Alta · Media · Baja. "Implementado" = ya está en el MVP y se puede
mostrar en la demo.

| # | Componente | Riesgo | Prob. | Impacto | Mitigación concreta | Estado |
|---|---|---|:---:|:---:|---|:---:|
| **R1** | **Modelo A2** | **Cambio de régimen de mercado:** el modelo se entrenó en 2020–2024 y la frecuencia de alzas pasó de 10% (2025) a 48% (2026). Puede no avisar un alza (costo S/ 4.00 por tanqueada) o generar falsas alarmas en serie. | Alta | Media | (a) Umbral asimétrico P\* = 0.25: prioriza no perder alzas (recall 94% en test 2026). (b) La confianza (ALTA/MEDIA/BAJA) se muestra y, si es BAJA, el texto incluye la advertencia obligatoria de incertidumbre. (c) Reentrenamiento mensual con `make entrenar` + `scripts/exportar_modelo_web.py`; el test de paridad bloquea un modelo mal exportado. (d) Pendiente: re-calibrar P\* por régimen e integrar variables macro. | 🟢 a, b, c · 🟡 d |
| **R2** | **Modelo A2** | **Datos desactualizados:** el MVP predice desde el último mes de Osinergmin; si no se actualiza, recomienda sobre información vieja. | Media | Media | El MVP muestra el mes base de los datos ("precios oficiales hasta 2026-08") en el pie y en "¿Cómo se calculó?". Procedimiento de actualización documentado en `mvp/README_mvp.md`. | 🟢 |
| **R3** | **Capa de lenguaje G1** | **Alucinación numérica:** el LLM inventa un precio, un ahorro o una probabilidad que el modelo no dio, y el conductor actúa sobre una cifra falsa. | Media | Alta | (a) System Prompt con contexto cerrado: solo puede usar el payload. (b) **Auditoría de cada respuesta antes de mostrarla**: toda cifra (decimales, montos enteros con "S/", porcentajes) debe existir en el payload. (c) Si hay una cifra inventada, el texto del LLM **se descarta** y se muestra la redacción determinista verificada. (d) Métrica medida: 100% de cumplimiento del respaldo (60/60 y 72/72); Gemini crudo se mide con `npm run auditar-llm`. | 🟢 |
| **R4** | **Capa de lenguaje G1** | **Omisión de avisos obligatorios** (que es IA, que es una estimación, que hay incertidumbre) o tono que suena a garantía. | Media | Media | Auditoría verifica la presencia literal del aviso de IA y de la advertencia de incertidumbre; si faltan, el guardarraíl las agrega. Además, aviso de IA fijo en la parte superior de la pantalla, independiente del LLM. | 🟢 |
| **R5** | **Capa de lenguaje G1** | **Caída o lentitud de la API de Gemini** (cuota gratuita, red). | Media | Baja | Timeout de 6 s y respaldo determinista: el usuario siempre recibe recomendación. `/api/salud` permite monitorear si el LLM está configurado. | 🟢 |
| **R6** | **Acción del usuario** *(no hay agente)* | **Exceso de confianza (automation bias):** el conductor llena el tanque solo porque "la IA lo dijo", incluso con confianza baja, o asume que encontrará el P10 en cualquier grifo. | Media | Media | Titular en una frase pero acompañado de la confianza, la advertencia de incertidumbre y "no es garantía". La banda se presenta como referencia ("no pagues más de"), no como un grifo concreto. El MVP **no ejecuta ninguna acción**: no paga, no reserva, no navega; la decisión es siempre del usuario. | 🟢 |
| **R7** | **Datos personales** | Recolección o filtración de datos del usuario (ubicación, placa, hábitos). | Baja | Alta | El MVP **no pide ni almacena datos personales** (ver sección 2). Los logs del servidor solo guardan departamento, tendencia, fuente del texto, cumplimiento y latencia. | 🟢 |

---

## 2. Cumplimiento de la Ley N.° 29733 (Protección de Datos Personales) y su Reglamento

| Exigencia | Cómo lo cumple Lunetra IA | Dónde verificarlo |
|---|---|---|
| **Datos de entrenamiento sin datos personales** | Se usan precios por grifo y por departamento de Osinergmin (datos públicos de personas jurídicas). El archivo diario por grifo está **anonimizado** (`precios_combustibles_anonimizados_*.csv`): sin RUC, razón social ni dirección exacta. | `plantillas/plantilla_2_data_readiness.md` §7, `datos/README_datos.md` |
| **Minimización en el uso del MVP** | Solo se piden 2 datos no personales: departamento y nivel de tanque (bajo/medio/lleno). No hay registro, login, GPS, placa, correo ni teléfono. | `mvp/web/components/Asistente.tsx` |
| **Información al usuario (deber de informar)** | Pie de página: qué datos se usan, que no se guardan asociados a la persona y la referencia a la Ley N.° 29733. | Pantalla principal del MVP |
| **No almacenamiento / no cesión a terceros** | No hay base de datos de usuarios. A Gemini solo se envía el payload del modelo (cifras de mercado + nivel de tanque), nunca datos de la persona. Los logs técnicos no contienen IP ni identificadores. | `mvp/web/app/api/recomendar/route.ts`, `lib/recomendar.ts` |
| **Consentimiento en pruebas con usuarios** | Consentimiento verbal; participantes identificados solo con código (U1…U5), edad aproximada y distrito. | `mvp/evidencia/pruebas_usuario.md` §1 |
| **Secretos** | La clave de Gemini vive solo como variable de entorno en Vercel; nunca llega al navegador ni al repositorio (`.env*` en `.gitignore`). | `mvp/web/.gitignore`, `lib/gemini.ts` |

**Transparencia de IA:** el usuario ve, antes de interactuar, el aviso fijo *"Estás usando un
asistente de Inteligencia Artificial. Sus recomendaciones son estimaciones estadísticas, no
garantías de precio."*, y cada texto generado cierra con *"Este reporte es generado por el asistente
de IA de Lunetra IA a partir de estimaciones probabilísticas"*.

---

## 3. Impacto esperado y medido

| Dimensión | Indicador | Valor | Tipo |
|---|---|---|---|
| Económico (timing) | Costo de error por decisión vs. baseline de persistencia | S/ 1.90 → S/ 0.54 (−72%) | Medido en test ciego 2026 |
| Económico (dónde cargar) | Ahorro potencial por tanqueada de 8 gal (8 × brecha P90–P10) | S/ 16.96 | Medido sobre 4,428 grifos (Osinergmin) |
| Económico anual | Ahorro potencial por dispersión, 52 tanqueadas | hasta ~S/ 882 | Proyección (supuesto: el usuario encuentra grifos cerca del P10) |
| Adopción | Usuarios que completan la tarea sin ayuda / confianza (1–5) | *ver pruebas_usuario.md* | Por medir con usuarios reales |
| Confiabilidad G1 | Respuestas que cumplen el contrato anti-alucinación | 100% (respaldo) · Gemini *pendiente* | Medido / por medir |

**Impactos negativos posibles y respuesta**
- *Sesgo geográfico:* la banda de Lima usa 4,428 grifos; en otros departamentos se usa la serie
  mensual de 12 meses (menos precisa). El MVP lo declara en "¿Cómo se calculó?".
- *Concentración de demanda:* si muchos usuarios cargan el mismo día por un aviso "sube", podría
  haber colas; con la escala de un MVP académico el efecto es despreciable.

---

## 4. Decisión

Con R1–R7 mitigados o en seguimiento, el equipo considera el MVP **apto para piloto académico**
con usuarios reales, no para uso comercial. Condiciones para escalar: medir Gemini crudo (KR2),
recalibrar P\* por régimen (R1) y obtener ≥ 5 pruebas de usuario con al menos un cambio derivado.
