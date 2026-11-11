# Lunetra IA — MVP (PC2)

> **¿Lleno hoy o espero?** Un asistente de IA que le dice al conductor particular de Lima si conviene
> cargar gasolina hoy o esperar, y cuál es un precio justo por galón.

## URL pública del MVP

**➡️ https://lunetra-ai.vercel.app** &nbsp;·&nbsp; chequeo de disponibilidad: `/api/salud`

> ⚠️ **Pendiente del equipo:** confirmar esta URL después del primer despliegue en Vercel (ver
> [Despliegue](#despliegue-en-vercel)). Si Vercel asigna otro dominio, reemplazarlo aquí, en el
> `README.md` raíz y en el checklist.

---

## Instrucciones para el evaluador

No necesitas cuenta, instalación ni datos personales. Funciona en celular y laptop.

1. Abre la URL pública.
2. En **¿Dónde cargas?** deja *Lima Metropolitana* (el usuario objetivo) o elige otro departamento.
3. En **¿Cómo está tu tanque?** toca *Bajo*, *Medio* o *Lleno*.
4. Presiona **¿Lleno hoy o espero?**

Verás:

| Bloque | Qué es | De dónde sale |
|---|---|---|
| Titular **"Carga hoy"** / **"Puedes esperar"** | La decisión, en una frase | Modelo A2 (tendencia del próximo mes) + nivel de tanque |
| Banda **P10 · P50 · P90** | Precio justo por galón: "buen precio", "precio típico", "no pagues más" | Percentiles oficiales Osinergmin |
| **Lunetra IA te explica** | Explicación en lenguaje natural | Capa de lenguaje G1 (Gemini) usando *solo* las cifras del modelo |
| **¿Cómo se calculó?** | Probabilidades, umbral P\* = 0.25, fuente de datos y resultado de la auditoría anti-alucinación | Trazabilidad del pipeline |

Arriba de todo, siempre visible, el aviso: **"Estás usando un asistente de Inteligencia Artificial"**.

**Casos para probar en la demo**
- Presionar el botón sin elegir tanque → mensaje de ayuda, no se rompe.
- *Lima + Bajo* vs. *Lima + Lleno* → misma tendencia, acción adaptada al tanque.
- *Madre de Dios* → confianza ALTA; *Lima* → confianza BAJA con advertencia de incertidumbre obligatoria.

---

## Qué hay dentro (arquitectura)

```
Navegador (Next.js / React)
   │  POST /api/recomendar {departamento, nivel_tanque}
   ▼
Función serverless en Vercel (Node.js)
   1. Modelo A2 entrenado por el equipo  ── lib/modelo.ts
      StandardScaler → Regresión logística multinomial → umbral asimétrico P* = 0.25
      (parámetros exportados de scikit-learn: data/modelo_a2.json)
   2. Payload de 10 campos (contrato Modelo → Lenguaje, Plantilla 3)
   3. Gemini Flash con el System Prompt G1 congelado ── lib/gemini.ts, lib/prompts.ts
   4. Auditoría anti-alucinación de cada respuesta (KR2)
        ├─ cifras inventadas      → se descarta el texto del LLM → redacción determinista de respaldo
        ├─ falta aviso/advertencia → guardarraíl las agrega
        └─ LLM caído o > 6 s      → redacción determinista de respaldo
   ▼
Respuesta JSON: titular + banda + texto + trazabilidad + auditoría
```

- **El modelo del equipo está dentro del MVP:** la inferencia corre en el servidor con los mismos
  coeficientes que entrenó `modelado/entrenamiento_a2.py`. El test
  `web/lib/__tests__/paridad.test.ts` exige que TypeScript reproduzca las probabilidades de
  scikit-learn en los 24 departamentos (tolerancia 1e-6).
- **La capa de lenguaje usa su resultado:** Gemini solo recibe el payload del modelo; toda cifra
  que escriba se audita contra ese payload.
- **Sin base de datos en esta versión:** los datos de inferencia (última fila de features por
  departamento y percentiles) se empaquetan como JSON estático. Supabase, previsto en la PC1, no
  fue necesario para la demo y se documenta como desviación en `evidencia/resultados_okr.md`.

## Actualizar el modelo con datos nuevos

```bash
# desde la raíz del repositorio
python modelado/entrenamiento_a2.py
python scripts/exportar_modelo_web.py   # regenera mvp/web/data/*.json
cd mvp/web && npm test                  # verifica paridad Python ↔ TypeScript
```

Hacer commit de `mvp/web/data/*.json`; Vercel redepliega solo.

## Ejecutar en local

```bash
cd mvp/web
npm install
cp .env.example .env.local   # opcional: pegar GEMINI_API_KEY
npm run dev                  # http://localhost:3000
npm test                     # 120 pruebas: paridad, auditoría, casos límite
```

Sin `GEMINI_API_KEY` el MVP funciona igual con la redacción determinista de respaldo.

## Despliegue en Vercel

1. En [vercel.com/new](https://vercel.com/new) importar `Los-1000/tanquelleno-ai`.
2. **Root Directory:** `mvp/web` (Framework: Next.js, se detecta solo).
3. **Environment Variables:** `GEMINI_API_KEY` = clave de [Google AI Studio](https://aistudio.google.com/apikey)
   (opcional `GEMINI_MODEL`, por defecto `gemini-3.5-flash`).
4. Deploy. Cada push a `main` redepliega.
5. Verificar `https://<dominio>/api/salud` → `"llm_configurado": true`.

## Medir la capa de lenguaje (métrica propia de G1)

```bash
cd mvp/web
GEMINI_API_KEY=xxx npm run auditar-llm
```

Recorre 72 casos (24 departamentos × 3 niveles de tanque) contra Gemini real y guarda
`mvp/evidencia/auditoria_llm.json` con: % de respuestas crudas sin cifras inventadas, % con aviso
de IA, % con advertencia de incertidumbre cuando corresponde, tasa de respaldo y latencia p50/p95.

## Evidencia de la PC2

| Archivo | Contenido |
|---|---|
| [`evidencia/pruebas_usuario.md`](evidencia/pruebas_usuario.md) | Protocolo y registro de pruebas con usuarios reales, casos límite y cambios derivados |
| [`evidencia/resultados_okr.md`](evidencia/resultados_okr.md) | Resultado real de cada KR frente a su meta de la PC1 |
| [`../plantillas/plantilla_4_impact_assessment.md`](../plantillas/plantilla_4_impact_assessment.md) | Riesgos, mitigaciones y cumplimiento de la Ley N.° 29733 |
| [`../presentacion_pc2_guion.md`](../presentacion_pc2_guion.md) | Guion de la sustentación de 20 minutos con demo en vivo |
