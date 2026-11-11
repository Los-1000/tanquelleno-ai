import { describe, expect, it } from "vitest";
import { DEPARTAMENTOS, predecir, type Payload } from "@/lib/modelo";
import {
  ADVERTENCIA_INCERTIDUMBRE,
  AVISO_IA,
  aplicarGuardarrail,
  auditarAlucinacionNumerica,
  redactarSinLlm,
  titularDecision,
} from "@/lib/prompts";
import { recomendar } from "@/lib/recomendar";

const base: Payload = {
  departamento: "LIMA",
  combustible: "Gasolina Regular",
  periodo: "Setiembre 2026 (t+1)",
  tendencia_predicha: "SUBE",
  probabilidad_alza: 0.31,
  confianza: "MEDIA",
  p10_mercado: 13.39,
  p50_mediana: 14.3,
  p90_mercado: 15.7,
  brecha_dispersion: 2.12,
};

describe("Auditoría anti-alucinación (KR2) — más estricta que la de Python", () => {
  it("acepta cifras del payload en formatos equivalentes", () => {
    const t = `Carga cerca de S/ 13.39, la mediana es S/14.30 y no pases de 15,7 soles. Probabilidad: 31%. ${AVISO_IA}.`;
    const a = auditarAlucinacionNumerica(t, base);
    expect(a.cifras_inventadas).toEqual([]);
    expect(a.cumple_contrato).toBe(true);
  });
  it("detecta un precio decimal inventado", () => {
    const a = auditarAlucinacionNumerica(`El precio será S/ 16.10. ${AVISO_IA}.`, base);
    expect(a.cifras_inventadas).toEqual(["16.10"]);
    expect(a.cumple_contrato).toBe(false);
  });
  it("detecta un monto entero inventado con S/ (la auditoría de Python no lo veía)", () => {
    const a = auditarAlucinacionNumerica(`Ahorrarás S/ 20 por tanqueada. ${AVISO_IA}.`, base);
    expect(a.cifras_inventadas).toEqual(["20"]);
  });
  it("detecta un porcentaje inventado", () => {
    const a = auditarAlucinacionNumerica(`Hay 80% de probabilidad de alza. ${AVISO_IA}.`, base);
    expect(a.cifras_inventadas).toEqual(["80"]);
  });
  it("detecta un cálculo derivado no presente en el payload (2.12 x 8)", () => {
    const a = auditarAlucinacionNumerica(`Puedes ahorrar S/ 16.96. ${AVISO_IA}.`, base);
    expect(a.sin_alucinacion).toBe(false);
  });
  it("no confunde años ni 't+1' con precios", () => {
    const a = auditarAlucinacionNumerica(`Para Setiembre 2026 (t+1). ${AVISO_IA}.`, base);
    expect(a.cifras_detectadas).toEqual([]);
  });
  it("exige la advertencia de incertidumbre cuando la confianza es BAJA", () => {
    const p = { ...base, confianza: "BAJA" as const };
    expect(auditarAlucinacionNumerica(`Todo bien. ${AVISO_IA}.`, p).cumple_contrato).toBe(false);
    expect(
      auditarAlucinacionNumerica(`${ADVERTENCIA_INCERTIDUMBRE}. ${AVISO_IA}.`, p).cumple_contrato,
    ).toBe(true);
  });
  it("el guardarraíl agrega las frases obligatorias que el LLM omitió", () => {
    const p = { ...base, confianza: "BAJA" as const };
    const { texto, aplicado } = aplicarGuardarrail("Carga hoy cerca de S/ 13.39.", p);
    expect(aplicado).toBe(true);
    expect(auditarAlucinacionNumerica(texto, p).cumple_contrato).toBe(true);
  });
});

describe("Redacción de respaldo: cumple el contrato en los 72 casos (24 dptos x 3 niveles)", () => {
  for (const d of DEPARTAMENTOS) {
    for (const nivel of ["bajo", "medio", "lleno"] as const) {
      it(`${d.departamento} / ${nivel}`, () => {
        const { payload } = predecir(d.departamento);
        const a = auditarAlucinacionNumerica(redactarSinLlm(payload, nivel), payload);
        expect(a.cumple_contrato).toBe(true);
      });
    }
  }
});

describe("Titular binario de la promesa de producto", () => {
  it("SUBE + tanque bajo => Carga hoy", () => {
    expect(titularDecision(base, "bajo").titular).toBe("Carga hoy");
  });
  it("SUBE + tanque lleno => Puedes esperar", () => {
    expect(titularDecision(base, "lleno").titular).toBe("Puedes esperar");
  });
  it("BAJA => Puedes esperar", () => {
    expect(titularDecision({ ...base, tendencia_predicha: "BAJA" }, "bajo").titular).toBe(
      "Puedes esperar",
    );
  });
});

describe("Orquestación con LLM simulado", () => {
  it("usa el texto del LLM cuando cumple el contrato", async () => {
    const r = await recomendar("LIMA", "medio", async () =>
      `Se espera una baja. Busca cerca de S/ 13.39. ${ADVERTENCIA_INCERTIDUMBRE}. ${AVISO_IA}.`,
    );
    expect(r.fuente_texto).toBe("gemini");
    expect(r.auditoria.cumple_contrato).toBe(true);
  });
  it("descarta el texto del LLM si inventa un precio y usa el respaldo", async () => {
    const r = await recomendar("LIMA", "medio", async () => `El galón costará S/ 12.50. ${AVISO_IA}.`);
    expect(r.fuente_texto).toBe("respaldo_determinista");
    expect(r.motivo_respaldo).toMatch(/12.50/);
    expect(r.auditoria.cumple_contrato).toBe(true);
  });
  it("cae al respaldo si el LLM falla o se demora", async () => {
    const r = await recomendar("LIMA", "bajo", async () => {
      throw new Error("timeout");
    });
    expect(r.fuente_texto).toBe("respaldo_determinista");
    expect(r.auditoria.cumple_contrato).toBe(true);
  });
  it("funciona sin LLM configurado", async () => {
    const r = await recomendar("CUSCO", "lleno", null);
    expect(r.fuente_texto).toBe("respaldo_determinista");
    expect(r.titular).toBe("Puedes esperar");
  });
});
