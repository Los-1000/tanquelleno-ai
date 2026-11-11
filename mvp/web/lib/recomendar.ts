/**
 * Orquestación del Patrón de Conexión 1 (Modelo -> Lenguaje) en el MVP:
 *
 *   modelo A2 (TS) -> payload -> Gemini con System Prompt G1
 *   -> auditoría anti-alucinación -> guardarraíl o respaldo determinista
 */
import { predecir, type NivelTanque, type Payload, type Clase, type Mercado } from "./modelo";
import {
  SYSTEM_PROMPT_G1,
  aplicarGuardarrail,
  auditarAlucinacionNumerica,
  construirMensajeUsuario,
  redactarSinLlm,
  titularDecision,
  type Auditoria,
} from "./prompts";
import { generarConGemini } from "./gemini";

export type FuenteTexto = "gemini" | "gemini+guardarrail" | "respaldo_determinista";

export interface Recomendacion {
  titular: string;
  tono: "alerta" | "calma" | "neutro";
  detalle: string;
  texto: string;
  fuente_texto: FuenteTexto;
  motivo_respaldo?: string;
  payload: Payload;
  probabilidades: Record<Clase, number>;
  mes_base: string;
  umbral_aplicado: number;
  mercado: Mercado;
  auditoria: Auditoria;
  auditoria_llm_cruda?: Auditoria;
  latencia_ms: number;
}

export type Generador = (system: string, usuario: string) => Promise<string>;

function generadorPorDefecto(): Generador | null {
  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) return null;
  return (s, u) => generarConGemini(s, u, { apiKey, modelo: process.env.GEMINI_MODEL || undefined });
}

export async function recomendar(
  departamento: string,
  nivelTanque: NivelTanque,
  generador: Generador | null = generadorPorDefecto(),
): Promise<Recomendacion> {
  const inicio = Date.now();
  const pred = predecir(departamento);
  const { payload } = pred;

  let texto = "";
  let fuente: FuenteTexto = "respaldo_determinista";
  let motivo: string | undefined;
  let auditoriaCruda: Auditoria | undefined;

  if (generador) {
    try {
      const crudo = await generador(SYSTEM_PROMPT_G1, construirMensajeUsuario(payload, nivelTanque));
      auditoriaCruda = auditarAlucinacionNumerica(crudo, payload);
      if (!auditoriaCruda.sin_alucinacion) {
        motivo = `El LLM citó cifras fuera del payload (${auditoriaCruda.cifras_inventadas.join(", ")}); se descartó su texto.`;
      } else if (auditoriaCruda.cumple_contrato) {
        texto = crudo.trim();
        fuente = "gemini";
      } else {
        texto = aplicarGuardarrail(crudo, payload).texto;
        fuente = "gemini+guardarrail";
      }
    } catch (e) {
      motivo = `No se pudo consultar el LLM: ${(e as Error).message}`;
    }
  } else {
    motivo = "LLM no configurado (falta GEMINI_API_KEY).";
  }

  if (!texto) {
    texto = redactarSinLlm(payload, nivelTanque);
    fuente = "respaldo_determinista";
  }

  const decision = titularDecision(payload, nivelTanque);
  return {
    ...decision,
    texto,
    fuente_texto: fuente,
    motivo_respaldo: fuente === "respaldo_determinista" ? motivo : undefined,
    payload,
    probabilidades: pred.probabilidades,
    mes_base: pred.mes_base,
    umbral_aplicado: pred.umbral_aplicado,
    mercado: pred.mercado,
    auditoria: auditarAlucinacionNumerica(texto, payload),
    auditoria_llm_cruda: auditoriaCruda,
    latencia_ms: Date.now() - inicio,
  };
}
