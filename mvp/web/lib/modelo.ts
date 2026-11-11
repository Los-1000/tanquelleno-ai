/**
 * Componente analítico A2 ejecutado dentro del MVP.
 *
 * Reproduce exactamente el Pipeline de scikit-learn entrenado por el equipo
 * (`modelado/entrenamiento_a2.py`): StandardScaler -> LogisticRegression
 * multinomial -> umbral asimétrico P* = 0.25 para la clase SUBE.
 * Los parámetros vienen de `data/modelo_a2.json`, exportado por
 * `scripts/exportar_modelo_web.py`. La paridad con Python se verifica en
 * `lib/__tests__/paridad.test.ts`.
 */
import modeloJson from "@/data/modelo_a2.json";
import departamentosJson from "@/data/departamentos.json";

export type Clase = "MANTIENE" | "SUBE" | "BAJA";
export type Confianza = "ALTA" | "MEDIA" | "BAJA";
export type NivelTanque = "bajo" | "medio" | "lleno";

export interface Mercado {
  p10_mercado: number;
  p50_mediana: number;
  p90_mercado: number;
  brecha_dispersion: number;
  n_estaciones: number;
  ahorro_por_tanqueada: number;
  fuente_percentiles: string;
}

export interface Departamento {
  departamento: string;
  mes_base: string;
  features: number[];
  mercado: Mercado;
  esperado_python: {
    probabilidades: Record<Clase, number>;
    tendencia_predicha: Clase;
    confianza: Confianza;
    periodo: string;
  };
}

/** Los 10 campos del contrato Modelo -> Lenguaje (plantilla 3, Patrón 1). */
export interface Payload {
  departamento: string;
  combustible: string;
  periodo: string;
  tendencia_predicha: Clase;
  probabilidad_alza: number;
  confianza: Confianza;
  p10_mercado: number;
  p50_mediana: number;
  p90_mercado: number;
  brecha_dispersion: number;
}

export interface Prediccion {
  payload: Payload;
  probabilidades: Record<Clase, number>;
  mes_base: string;
  umbral_aplicado: number;
  mercado: Mercado;
}

export const MODELO = modeloJson;
export const DEPARTAMENTOS = departamentosJson as Departamento[];

const MESES_ES = [
  "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
  "Julio", "Agosto", "Setiembre", "Octubre", "Noviembre", "Diciembre",
];

const NOMBRES_COMBUSTIBLE: Record<string, string> = {
  REGULAR: "Gasolina Regular",
  PREMIUM: "Gasolina Premium",
  DIESEL: "Diésel B5",
};

/** Probabilidades por clase, idéntico a `Pipeline.predict_proba`. */
export function predecirProba(features: number[]): Record<Clase, number> {
  const { media, escala, coeficientes, interceptos, clases } = MODELO;
  if (features.length !== media.length) {
    throw new Error(`Se esperaban ${media.length} features y llegaron ${features.length}.`);
  }
  if (!features.every(Number.isFinite)) {
    throw new Error("Las features contienen valores no numéricos.");
  }
  const z = features.map((x, i) => (x - media[i]) / escala[i]);
  const logits = coeficientes.map(
    (fila, k) => fila.reduce((acc, w, i) => acc + w * z[i], 0) + interceptos[k],
  );
  const max = Math.max(...logits);
  const exps = logits.map((l) => Math.exp(l - max));
  const suma = exps.reduce((a, b) => a + b, 0);
  const proba = {} as Record<Clase, number>;
  clases.forEach((c, k) => {
    proba[c as Clase] = exps[k] / suma;
  });
  return proba;
}

/** Regla de decisión con umbral asimétrico (C_FN = 5 x C_FP => P* = 0.25). */
export function decidirClase(proba: Record<Clase, number>, umbral = MODELO.umbral_sube): Clase {
  if (proba.SUBE > umbral) return "SUBE";
  return proba.MANTIENE >= proba.BAJA ? "MANTIENE" : "BAJA";
}

/** Igual que `clasificar_confianza` de pipeline_inferencia.py. */
export function clasificarConfianza(proba: Record<Clase, number>): Confianza {
  const pMax = Math.max(proba.MANTIENE, proba.SUBE, proba.BAJA);
  if (pMax >= 0.6) return "ALTA";
  if (pMax >= 0.45) return "MEDIA";
  return "BAJA";
}

export function periodoObjetivo(mesBase: string): string {
  const [anio, mes] = mesBase.split("-").map(Number);
  const siguiente = mes === 12 ? { a: anio + 1, m: 1 } : { a: anio, m: mes + 1 };
  return `${MESES_ES[siguiente.m - 1]} ${siguiente.a} (t+1)`;
}

const redondear = (x: number, d = 2) => Math.round(x * 10 ** d) / 10 ** d;

export function buscarDepartamento(nombre: string): Departamento | undefined {
  const clave = nombre.trim().toUpperCase();
  return DEPARTAMENTOS.find((d) => d.departamento === clave);
}

/** Ejecuta el modelo A2 para un departamento y arma el payload del contrato. */
export function predecir(departamento: string): Prediccion {
  const depto = buscarDepartamento(departamento);
  if (!depto) {
    throw new RangeError(`Departamento no disponible: ${departamento}`);
  }
  const proba = predecirProba(depto.features);
  const clase = decidirClase(proba);
  const m = depto.mercado;
  const payload: Payload = {
    departamento: depto.departamento,
    combustible: NOMBRES_COMBUSTIBLE[MODELO.familia] ?? "Gasolina Regular",
    periodo: periodoObjetivo(depto.mes_base),
    tendencia_predicha: clase,
    probabilidad_alza: redondear(proba.SUBE),
    confianza: clasificarConfianza(proba),
    p10_mercado: m.p10_mercado,
    p50_mediana: m.p50_mediana,
    p90_mercado: m.p90_mercado,
    brecha_dispersion: m.brecha_dispersion,
  };
  return {
    payload,
    probabilidades: proba,
    mes_base: depto.mes_base,
    umbral_aplicado: MODELO.umbral_sube,
    mercado: m,
  };
}
