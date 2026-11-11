import { describe, expect, it } from "vitest";
import {
  DEPARTAMENTOS,
  clasificarConfianza,
  decidirClase,
  periodoObjetivo,
  predecir,
  predecirProba,
} from "@/lib/modelo";

describe("Paridad del modelo A2: TypeScript reproduce scikit-learn", () => {
  it("exporta los 24 departamentos", () => {
    expect(DEPARTAMENTOS.length).toBe(24);
  });

  for (const d of DEPARTAMENTOS) {
    it(`${d.departamento}: mismas probabilidades, clase, confianza y periodo`, () => {
      const proba = predecirProba(d.features);
      for (const clase of ["MANTIENE", "SUBE", "BAJA"] as const) {
        expect(proba[clase]).toBeCloseTo(d.esperado_python.probabilidades[clase], 6);
      }
      expect(decidirClase(proba)).toBe(d.esperado_python.tendencia_predicha);
      expect(clasificarConfianza(proba)).toBe(d.esperado_python.confianza);
      expect(periodoObjetivo(d.mes_base)).toBe(d.esperado_python.periodo);
    });
  }
});

describe("Regla de decisión con umbral asimétrico P* = 0.25", () => {
  it("avisa SUBE aunque no sea la clase más probable si supera P*", () => {
    expect(decidirClase({ MANTIENE: 0.4, SUBE: 0.26, BAJA: 0.34 })).toBe("SUBE");
  });
  it("no avisa SUBE si está en o por debajo de P*", () => {
    expect(decidirClase({ MANTIENE: 0.3, SUBE: 0.25, BAJA: 0.45 })).toBe("BAJA");
  });
  it("en empate MANTIENE/BAJA elige MANTIENE como numpy.argmax", () => {
    expect(decidirClase({ MANTIENE: 0.4, SUBE: 0.2, BAJA: 0.4 })).toBe("MANTIENE");
  });
});

describe("Casos límite de entrada", () => {
  it("rechaza un departamento inexistente", () => {
    expect(() => predecir("CALLAO-NORTE")).toThrow(RangeError);
  });
  it("acepta minúsculas y espacios", () => {
    expect(predecir("  lima ").payload.departamento).toBe("LIMA");
  });
  it("rechaza features no numéricas", () => {
    expect(() => predecirProba(Array(11).fill(Number.NaN))).toThrow();
  });
  it("rechaza vectores de largo incorrecto", () => {
    expect(() => predecirProba([1, 2, 3])).toThrow();
  });
  it("cambia de año al predecir enero", () => {
    expect(periodoObjetivo("2026-12-01")).toBe("Enero 2027 (t+1)");
  });
});
