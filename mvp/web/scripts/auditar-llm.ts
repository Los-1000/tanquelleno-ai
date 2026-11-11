/**
 * Métrica propia de la capa de lenguaje (G1), independiente de la del modelo.
 *
 * Recorre los 72 casos (24 departamentos x 3 niveles de tanque), pide a Gemini
 * la recomendación con el System Prompt G1 y mide sobre el texto CRUDO del LLM
 * (antes de guardarraíles):
 *   - % sin cifras inventadas            (KR2: meta 100%, N >= 50)
 *   - % con aviso de IA
 *   - % con advertencia de incertidumbre cuando corresponde
 *   - % que cumple el contrato completo
 *   - % de respuestas que terminan en respaldo determinista
 *   - latencia p50 / p95
 * y escribe ../evidencia/auditoria_llm.json.
 *
 * USO (desde mvp/web):
 *   GEMINI_API_KEY=... npm run auditar-llm
 */
import { writeFileSync, mkdirSync } from "node:fs";
import path from "node:path";
import { DEPARTAMENTOS } from "../lib/modelo";
import { recomendar, type Generador } from "../lib/recomendar";
import { generarConGemini } from "../lib/gemini";

const apiKey = process.env.GEMINI_API_KEY;
if (!apiKey) {
  console.error("Falta GEMINI_API_KEY. Ejemplo:  GEMINI_API_KEY=xxx npm run auditar-llm");
  process.exit(1);
}
const modelo = process.env.GEMINI_MODEL || "gemini-2.5-flash";
const generador: Generador = (s, u) => generarConGemini(s, u, { apiKey, modelo, timeoutMs: 15000 });

const pct = (n: number, d: number) => (d ? Math.round((1000 * n) / d) / 10 : 0);
const percentil = (xs: number[], q: number) => {
  const o = [...xs].sort((a, b) => a - b);
  return o[Math.min(o.length - 1, Math.floor(q * o.length))] ?? 0;
};

async function main() {
  const casos = [];
  for (const d of DEPARTAMENTOS) {
    for (const nivel of ["bajo", "medio", "lleno"] as const) {
      const r = await recomendar(d.departamento, nivel, generador);
      const cruda = r.auditoria_llm_cruda;
      casos.push({
        departamento: d.departamento,
        nivel_tanque: nivel,
        tendencia: r.payload.tendencia_predicha,
        confianza: r.payload.confianza,
        llm_respondio: Boolean(cruda),
        cruda_sin_alucinacion: cruda?.sin_alucinacion ?? null,
        cruda_incluye_aviso_ia: cruda?.incluye_aviso_ia ?? null,
        cruda_requiere_advertencia: cruda?.requiere_advertencia_incertidumbre ?? null,
        cruda_incluye_advertencia: cruda?.incluye_advertencia_incertidumbre ?? null,
        cruda_cumple_contrato: cruda?.cumple_contrato ?? null,
        cifras_inventadas: cruda?.cifras_inventadas ?? [],
        fuente_final: r.fuente_texto,
        final_cumple_contrato: r.auditoria.cumple_contrato,
        motivo_respaldo: r.motivo_respaldo ?? null,
        latencia_ms: r.latencia_ms,
        texto_final: r.texto,
      });
      process.stdout.write(".");
      await new Promise((ok) => setTimeout(ok, 500)); // respeta el rate limit gratuito
    }
  }
  console.log();

  const resp = casos.filter((c) => c.llm_respondio);
  const reqAdv = resp.filter((c) => c.cruda_requiere_advertencia);
  const lat = casos.map((c) => c.latencia_ms);
  const resumen = {
    generado_en: new Date().toISOString(),
    modelo_llm: modelo,
    n_casos: casos.length,
    n_respuestas_llm: resp.length,
    llm_sin_alucinacion_pct: pct(resp.filter((c) => c.cruda_sin_alucinacion).length, resp.length),
    llm_incluye_aviso_ia_pct: pct(resp.filter((c) => c.cruda_incluye_aviso_ia).length, resp.length),
    llm_incluye_advertencia_cuando_corresponde_pct: pct(
      reqAdv.filter((c) => c.cruda_incluye_advertencia).length,
      reqAdv.length,
    ),
    llm_cumple_contrato_crudo_pct: pct(resp.filter((c) => c.cruda_cumple_contrato).length, resp.length),
    final_cumple_contrato_pct: pct(casos.filter((c) => c.final_cumple_contrato).length, casos.length),
    tasa_respaldo_pct: pct(
      casos.filter((c) => c.fuente_final === "respaldo_determinista").length,
      casos.length,
    ),
    tasa_guardarrail_pct: pct(
      casos.filter((c) => c.fuente_final === "gemini+guardarrail").length,
      casos.length,
    ),
    latencia_p50_ms: percentil(lat, 0.5),
    latencia_p95_ms: percentil(lat, 0.95),
    kr2_cumple: resp.length >= 50 && resp.every((c) => c.cruda_sin_alucinacion),
  };

  const salida = path.resolve(__dirname, "..", "..", "evidencia", "auditoria_llm.json");
  mkdirSync(path.dirname(salida), { recursive: true });
  writeFileSync(salida, JSON.stringify({ resumen, casos }, null, 2), "utf-8");
  console.log(JSON.stringify(resumen, null, 2));
  console.log(`Reporte: ${salida}`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
