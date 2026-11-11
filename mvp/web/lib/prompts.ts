/**
 * Componente generativo G1: System Prompt, redacción de respaldo y auditoría
 * anti-alucinación (KR2). Port de `src/tanquelleno/prompts.py`.
 *
 * La auditoría del MVP es MÁS estricta que la de Python: además de decimales,
 * detecta montos enteros con "S/" (p. ej. "S/ 17") y porcentajes ("21%"),
 * que un LLM real sí suele escribir.
 */
import type { NivelTanque, Payload } from "./modelo";

export const ZONA_INCERTIDUMBRE: [number, number] = [0.4, 0.55];
export const GALONES_POR_TANQUEADA = 8;

export const SYSTEM_PROMPT_G1 = `Eres Lunetra IA, un asistente experto y transparente diseñado para orientar a conductores particulares de Lima Metropolitana en la optimización del gasto en combustible.

Tu misión es transformar los resultados cuantitativos de nuestro modelo analítico en una recomendación clara, directa, empática y accionable en lenguaje natural.

REGLAS DE OBLIGATORIO CUMPLIMIENTO:

1. INFORMACIÓN SOBRE INTERACCIÓN CON IA:
   - Debes incluir siempre al inicio o cierre el aviso: "Este reporte es generado por el asistente de IA de Lunetra IA a partir de estimaciones probabilísticas".

2. PROHIBICIÓN TOTAL DE INVENTAR PRECIOS O DIRECCIONES:
   - Utiliza ÚNICAMENTE los números y la tendencia proporcionados en el contexto (payload).
   - Jamás inventes valores de combustible, marcas de grifos, distritos específicos ni garantices un precio futuro.

3. DECLARACIÓN OBLIGATORIA DE CONFIANZA:
   - Si el atributo 'confianza' es "BAJA" o la probabilidad está entre 0.40 y 0.55, debes advertir explícitamente al conductor: "El mercado se encuentra en una zona de alta incertidumbre estadística; no se descartan fluctuaciones imprevistas".

4. NATURALEZA ESTIMATIVA Y NO GARANTÍA:
   - Recuerda siempre al usuario que esta proyección es una estimación estadística y no una garantía financiera contractual. Factores geopolíticos o decretos de urgencia pueden alterar las tendencias.

5. ESTRUCTURA DE RESPUESTA:
   - [Diagnóstico de Tendencia]: Señala con claridad si la presión proyectada es al alza, a la baja o de estabilidad.
   - [Acción Recomendada]: Si la tendencia es ALZA y el conductor tiene tanque medio o bajo, recomiéndale tanquear antes del cierre de semana. Si es BAJA o ESTABLE, sugiere recargar solo lo necesario o esperar.
   - [Banda de Precio de Referencia]: Utiliza el P10 y P90 suministrados para enseñarle cuál es un precio competitivo en su departamento (ej. "Encuentra un grifo que expenda cerca de S/ {p10_mercado} y evita pagar más de S/ {p90_mercado}").

FORMATO Y TONO:
- Tono: Profesional, directo, cercano, libre de jerga técnica compleja.
- Extensión máxima: 3 párrafos concisos.`;

export const AVISO_IA =
  "Este reporte es generado por el asistente de IA de Lunetra IA a partir de estimaciones probabilísticas";
export const ADVERTENCIA_INCERTIDUMBRE =
  "El mercado se encuentra en una zona de alta incertidumbre estadística; no se descartan fluctuaciones imprevistas";

const CAMPOS_PAYLOAD: (keyof Payload)[] = [
  "departamento", "combustible", "periodo", "tendencia_predicha", "probabilidad_alza",
  "confianza", "p10_mercado", "p50_mediana", "p90_mercado", "brecha_dispersion",
];

export function construirMensajeUsuario(payload: Payload, nivelTanque: NivelTanque): string {
  const lineas = CAMPOS_PAYLOAD.map((c) => `- ${c}: ${payload[c]}`);
  lineas.push(`- nivel_tanque_usuario: ${nivelTanque}`);
  return (
    "Contexto cuantitativo del modelo analítico (única fuente de cifras permitida):\n" +
    lineas.join("\n")
  );
}

export function requiereAdvertencia(payload: Payload): boolean {
  const p = payload.probabilidad_alza;
  return (
    payload.confianza === "BAJA" ||
    (p >= ZONA_INCERTIDUMBRE[0] && p <= ZONA_INCERTIDUMBRE[1])
  );
}

/** Normaliza una cifra a su valor numérico canónico (2 decimales). */
const canon = (x: number) => x.toFixed(2);

export function valoresPermitidos(payload: Payload): Set<string> {
  const permitidos = new Set<string>();
  for (const v of Object.values(payload)) {
    if (typeof v !== "number") continue;
    permitidos.add(canon(v));
    permitidos.add(canon(Number(v.toFixed(1))));
    permitidos.add(canon(Math.round(v)));
  }
  // La probabilidad puede expresarse como porcentaje (0.21 -> 21%).
  permitidos.add(canon(Math.round(payload.probabilidad_alza * 100)));
  permitidos.add(canon(GALONES_POR_TANQUEADA));
  return permitidos;
}

// Montos con "S/" (enteros o decimales), "N soles", porcentajes y decimales sueltos.
const PATRON_CIFRA =
  /S\/\.?\s*(\d+(?:[.,]\d{1,2})?)|(\d+(?:[.,]\d{1,2})?)\s*soles?\b|(\d+(?:[.,]\d{1,2})?)\s*%|(?<![\d.,])(\d+[.,]\d{1,2})(?![\d])/gi;

export interface Auditoria {
  sin_alucinacion: boolean;
  cifras_detectadas: string[];
  cifras_inventadas: string[];
  incluye_aviso_ia: boolean;
  requiere_advertencia_incertidumbre: boolean;
  incluye_advertencia_incertidumbre: boolean;
  cumple_contrato: boolean;
}

const normalizarTexto = (t: string) =>
  t.toLowerCase().replace(/[“”"«»]/g, "").replace(/\s+/g, " ");

export function auditarAlucinacionNumerica(texto: string, payload: Payload): Auditoria {
  const permitidos = valoresPermitidos(payload);
  const encontradas: string[] = [];
  for (const m of texto.matchAll(PATRON_CIFRA)) {
    const cifra = (m[1] ?? m[2] ?? m[3] ?? m[4]).replace(",", ".");
    encontradas.push(cifra);
  }
  const inventadas = [...new Set(encontradas.filter((c) => !permitidos.has(canon(Number(c)))))];
  const t = normalizarTexto(texto);
  const necesita = requiereAdvertencia(payload);
  const incluyeAviso = t.includes(normalizarTexto(AVISO_IA));
  const incluyeAdvertencia = t.includes(normalizarTexto(ADVERTENCIA_INCERTIDUMBRE));
  return {
    sin_alucinacion: inventadas.length === 0,
    cifras_detectadas: encontradas,
    cifras_inventadas: inventadas.sort(),
    incluye_aviso_ia: incluyeAviso,
    requiere_advertencia_incertidumbre: necesita,
    incluye_advertencia_incertidumbre: incluyeAdvertencia,
    cumple_contrato: inventadas.length === 0 && incluyeAviso && (!necesita || incluyeAdvertencia),
  };
}

/** Redacción determinista de respaldo (idéntica a `redactar_sin_llm`). */
export function redactarSinLlm(payload: Payload, nivelTanque: NivelTanque): string {
  const prob = payload.probabilidad_alza.toFixed(2);
  let diagnostico: string;
  let accion: string;
  if (payload.tendencia_predicha === "SUBE") {
    diagnostico = `La presión proyectada para ${payload.periodo} en ${payload.departamento} es al alza, con una probabilidad estimada de ${prob}.`;
    accion =
      nivelTanque === "medio" || nivelTanque === "bajo"
        ? "Con el tanque medio o bajo, conviene abastecer antes del cierre de semana en lugar de esperar al próximo ajuste."
        : "Con el tanque lleno no necesitas actuar hoy; mantén la próxima carga a la vista.";
  } else if (payload.tendencia_predicha === "BAJA") {
    diagnostico = `La presión proyectada para ${payload.periodo} en ${payload.departamento} es a la baja (probabilidad de alza: ${prob}).`;
    accion = "Carga solo lo necesario para moverte y espera al siguiente ajuste.";
  } else {
    diagnostico = `Para ${payload.periodo} en ${payload.departamento} se proyecta estabilidad (probabilidad de alza: ${prob}).`;
    accion = "No hay urgencia por adelantar la carga; abastece según tu rutina habitual.";
  }
  const banda = `Busca un grifo que expenda cerca de S/ ${payload.p10_mercado} y evita pagar más de S/ ${payload.p90_mercado}; la mediana del mercado está en S/ ${payload.p50_mediana}.`;
  const cierre =
    "Esta proyección es una estimación estadística, no una garantía financiera: factores geopolíticos o decretos de urgencia pueden alterar la tendencia. " +
    `${AVISO_IA}.`;
  const partes = [`${diagnostico} ${accion}`, banda];
  if (requiereAdvertencia(payload)) partes.push(`${ADVERTENCIA_INCERTIDUMBRE}.`);
  partes.push(cierre);
  return partes.join("\n\n");
}

/**
 * Guardarraíl: si el LLM omitió una frase obligatoria (pero no inventó cifras),
 * se agrega al final en lugar de descartar la redacción.
 */
export function aplicarGuardarrail(texto: string, payload: Payload): { texto: string; aplicado: boolean } {
  const a = auditarAlucinacionNumerica(texto, payload);
  let salida = texto.trim();
  let aplicado = false;
  if (a.requiere_advertencia_incertidumbre && !a.incluye_advertencia_incertidumbre) {
    salida += `\n\n${ADVERTENCIA_INCERTIDUMBRE}.`;
    aplicado = true;
  }
  if (!a.incluye_aviso_ia) {
    salida += `\n\n${AVISO_IA}.`;
    aplicado = true;
  }
  return { texto: salida, aplicado };
}

/** Titular binario de la promesa de producto: "Carga hoy" o "Puedes esperar". */
export function titularDecision(payload: Payload, nivelTanque: NivelTanque) {
  if (payload.tendencia_predicha === "SUBE" && nivelTanque !== "lleno") {
    return { titular: "Carga hoy", tono: "alerta" as const, detalle: "Se proyecta una subida de precio el próximo mes." };
  }
  if (payload.tendencia_predicha === "SUBE") {
    return { titular: "Puedes esperar", tono: "neutro" as const, detalle: "Se proyecta una subida, pero tu tanque está lleno: carga apenas lo necesites." };
  }
  if (nivelTanque === "bajo") {
    return { titular: "Puedes esperar", tono: "calma" as const, detalle: "Carga solo lo necesario para moverte; no se proyecta una subida." };
  }
  return { titular: "Puedes esperar", tono: "calma" as const, detalle: "No se proyecta una subida de precio el próximo mes." };
}
