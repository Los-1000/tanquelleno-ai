# Pruebas con usuarios reales — Lunetra IA (PC2)

> **Estado:** protocolo listo y casos límite técnicos ya ejecutados. **Las filas de usuarios
> están vacías a propósito**: deben llenarse con personas reales fuera del equipo. No inventar
> participantes ni respuestas: el jurado puede pedir contactar o ver la grabación.
>
> Meta del checklist: **3 o más** usuarios (≥ 5 para puntaje máximo), al menos **un caso límite**
> y al menos **un hallazgo convertido en cambio** del MVP.

---

## 1. Protocolo

**Perfil a reclutar (usuario de la Plantilla 1):** conductor particular de Lima Metropolitana que
usa su auto a diario para trabajar, carga ~8 galones por semana y paga la gasolina de su bolsillo.
No sirven compañeros del curso ni familiares que conozcan el proyecto.

**Tarea principal (sin ayuda ni instrucciones):**
> "Imagina que hoy vas a pasar por un grifo. Usa esta página para decidir si cargas ahora o esperas."

**Cómo se conduce**
1. Darle el link en *su propio celular*. No explicar la app.
2. Observar en silencio; cronometrar desde que abre el link hasta que dice su decisión.
3. Anotar dónde duda, qué toca primero y qué lee.
4. Al terminar, 4 preguntas:
   - P1. ¿Qué te recomendó la app y por qué? (comprensión)
   - P2. ¿Sabías que era una IA? ¿Dónde lo viste? (transparencia, Ley/ética)
   - P3. ¿Cuánto es un precio justo por galón según la app? (banda P10–P90)
   - P4. Del 1 al 5, ¿le harías caso la próxima vez que cargues? ¿Por qué?
5. Consentimiento verbal: no se registran nombre completo, teléfono ni placa (Ley N.° 29733).
   Identificar al participante solo con un código (U1, U2…), edad aproximada y distrito.

**Criterio de éxito de la tarea:** el usuario llega a una decisión ("cargo hoy" / "espero") y
puede explicar por qué en ≤ 2 minutos, sin pedir ayuda.

---

## 2. Registro de usuarios

| Código | Fecha | Perfil (edad aprox., distrito, km/día, combustible) | Dispositivo | ¿Completó sin ayuda? | Tiempo | P1 comprensión | P2 vio aviso IA | P3 banda correcta | P4 confianza (1-5) | Observaciones / dudas |
|---|---|---|---|:---:|---:|---|:---:|:---:|:---:|---|
| U1 | | | | | | | | | | |
| U2 | | | | | | | | | | |
| U3 | | | | | | | | | | |
| U4 | | | | | | | | | | |
| U5 | | | | | | | | | | |

**Resumen (llenar):** __ de __ completaron la tarea sin ayuda · tiempo mediano __ s · __ de __
vieron el aviso de IA · confianza promedio __ / 5.

---

## 3. Casos límite probados

Ejecutados por el equipo sobre el MVP (build de producción) el 11-nov-2026. Cada uno está cubierto
también por una prueba automática en `mvp/web/lib/__tests__/`.

| # | Caso límite | Cómo respondió el MVP | Resultado |
|---|---|---|:---:|
| L1 | Presionar "¿Lleno hoy o espero?" sin elegir nivel de tanque | Muestra "Elige cómo está tu tanque para darte una recomendación." y no llama al servidor | ✅ |
| L2 | Departamento que no existe (`"MARTE"`) enviado directo a la API | HTTP 400: "Elige un departamento de la lista." | ✅ |
| L3 | Nivel de tanque inválido (`"vacio"`) | HTTP 400: "Indica si tu tanque está bajo, medio o lleno." | ✅ |
| L4 | Cuerpo que no es JSON | HTTP 400: "El cuerpo debe ser JSON." | ✅ |
| L5 | Departamento escrito en minúsculas y con espacios (`" lima "`) | Se normaliza y responde para LIMA | ✅ |
| L6 | Confianza BAJA (Lima, P(máx) = 0.44) | El texto incluye la advertencia obligatoria de alta incertidumbre | ✅ |
| L7 | El LLM inventa un precio (`"S/ 12.50"`, simulado) | La auditoría lo detecta, descarta el texto del LLM y usa la redacción de respaldo | ✅ |
| L8 | El LLM no responde / se cae (simulado) | Respaldo determinista; el usuario igual recibe recomendación | ✅ |
| L9 | El LLM omite el aviso de IA (simulado) | El guardarraíl agrega el aviso al final antes de mostrar | ✅ |
| L10 | Sin `GEMINI_API_KEY` configurada | Funciona con respaldo; `/api/salud` reporta `llm_configurado: false` | ✅ |
| L11 | Pantalla de celular (375 × 812) | Todo visible sin scroll horizontal; aviso de IA arriba | ✅ |
| L12 | *(llenar con un caso límite observado en un usuario real, p. ej. alguien que carga diésel o vive fuera de Lima)* | | |

---

## 4. Hallazgos que se convirtieron en cambios del MVP

| # | Hallazgo (de qué prueba salió) | Cambio aplicado en el MVP | Commit / evidencia |
|---|---|---|---|
| C1 | Pruebas de la auditoría: la auditoría heredada de la Fase M (Python) solo detectaba precios con decimales; un LLM real escribe "S/ 17" o "21%" y eso pasaba sin revisar | La auditoría del MVP ahora también detecta montos enteros con "S/" y porcentajes; un monto derivado como S/ 16.96 (2.12 × 8) que no está en el payload se rechaza | `mvp/web/lib/prompts.ts`, pruebas en `auditoria.test.ts` |
| C2 | *(llenar con un hallazgo de usuario real — p. ej. "U2 no entendió qué es P10" → se cambió la etiqueta a "buen precio")* | | |
| C3 | | | |

> Para el puntaje del criterio C3, **al menos un cambio debe venir de un usuario real** (C2 en
> adelante), no solo de las pruebas técnicas.
