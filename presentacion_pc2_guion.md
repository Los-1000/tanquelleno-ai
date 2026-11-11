# Guion de sustentación PC2 — Lunetra IA (20 minutos con demo en vivo)

> Borrador para armar `presentacion_pc2.pdf`. Tiempos en minutos acumulados. Cada integrante debe
> poder responder sobre **cualquier** fase: ver la sección "Preguntas probables" al final y
> ensayar rotando quién responde.
>
> **Rubricas cubiertas:** C1 MVP funciona solo · C2 resuelve el problema · C3 pruebas con usuarios ·
> C4 resultados medidos · C5 riesgos y regulación · C6 sustentación.

| # | Lámina | Min | Quién | Mensaje clave | Evidencia a mostrar |
|---|---|---:|---|---|---|
| 1 | Portada | 0:00–0:30 | *(asignar)* | "¿Lleno hoy o espero?" Una pregunta, respondida bien. | URL pública + QR |
| 2 | El problema y el usuario | 0:30–2:00 | | Conductor particular de Lima, 8 gal/semana, paga de su bolsillo. Brecha de S/ 2.12/galón entre grifos el mismo día (H5). | Plantilla 1, figura 1 |
| 3 | La solución en una frase | 2:00–3:00 | | Modelo que predice la tendencia del próximo mes + banda de precio justo + explicación en lenguaje claro. | Diagrama de arquitectura (README_mvp) |
| 4 | **DEMO EN VIVO** | 3:00–8:00 | | Abrir la URL **desde un celular**. Lima + tanque bajo → titular, banda, explicación, "¿Cómo se calculó?". Luego un caso límite: botón sin tanque. Mostrar el aviso de IA. | MVP en vivo; plan B: video grabado de 60 s |
| 5 | El modelo por dentro | 8:00–10:00 | | Regresión logística regularizada, 11 features rezagadas t−1, split cronológico sin leakage. Por qué no XGBoost/LSTM: 80 meses. | `analisis/fase_m_resultados.md` |
| 6 | Resultados del modelo en costos | 10:00–12:00 | | Matriz de confusión en soles: costo por decisión S/ 1.90 → S/ 0.54 (−72%). Recall de alzas 94%. Macro-F1 0.21 < 0.55: lo decimos de frente y explicamos el trade-off. | `mvp/evidencia/resultados_okr.md` |
| 7 | La capa de lenguaje y su métrica | 12:00–13:30 | | Gemini solo ve el payload; cada respuesta se audita; si inventa una cifra se descarta. % de cumplimiento crudo vs. final. | `auditoria_llm.json`, test L7 |
| 8 | Pruebas con usuarios | 13:30–15:30 | | N usuarios reales, cuántos completaron sin ayuda, citas textuales, caso límite real y el cambio que hicimos por ellos. | `mvp/evidencia/pruebas_usuario.md` |
| 9 | OKRs: meta vs. real | 15:30–16:30 | | Tabla de los 4 KR de la PC1 sin cambiar metas: 2 cumplen, 1 no, 1 parcial. | `resultados_okr.md` |
| 10 | Riesgos y Ley N.° 29733 | 16:30–18:00 | | 3 riesgos: modelo (cambio de régimen), lenguaje (alucinación), acción (exceso de confianza). No pedimos datos personales; datos de entrenamiento anonimizados. | Plantilla 4 |
| 11 | Qué sigue y cierre | 18:00–19:00 | | Variables macro, recalibrar P\* por régimen, feedback anónimo. Frase final. | — |
| — | Margen | 19:00–20:00 | | Colchón para la demo. | — |

## Checklist del día de la demo
- [ ] URL abre en un celular que **no** es del equipo (datos móviles, no wifi de la universidad).
- [ ] `/api/salud` responde `"estado": "ok"` y `"llm_configurado": true`.
- [ ] Video de respaldo de la demo descargado en la laptop.
- [ ] Tabla de usuarios y de OKRs llena con datos reales (sin celdas "pendiente").

## Preguntas probables (todos deben poder responder)
1. **¿Por qué el Macro-F1 no llega a 0.55?** Umbral asimétrico: preferimos 94% de alzas detectadas aunque suban las falsas alarmas; el costo para el usuario baja 72%.
2. **¿Una regla "avisar siempre" no sería igual?** En 2026 casi sí (S/ 0.42 vs S/ 0.54) por ser un año alcista; en 2025 esa regla daba falsa alarma 9 de cada 10 meses. Es la mejora pendiente (recalibrar por régimen).
3. **¿El modelo de verdad está dentro de la app?** Sí: los coeficientes de scikit-learn se ejecutan en el servidor de Vercel; un test exige que TypeScript dé las mismas probabilidades que Python (24/24 departamentos).
4. **¿Qué pasa si Gemini inventa un precio?** La auditoría lo detecta y se muestra la redacción determinista verificada. Mostrar test L7.
5. **¿Qué datos personales guardan?** Ninguno. Solo departamento y nivel de tanque, sin login ni GPS.
6. **¿Por qué no usaron Supabase como dijeron en la PC1?** Los datos de inferencia son estáticos y mensuales; una base de datos agregaba un punto de falla sin valor para el usuario.
7. **¿Cómo se actualiza con un mes nuevo?** `make entrenar` + `python scripts/exportar_modelo_web.py` + commit; Vercel redepliega.
