"use client";

import { useState } from "react";
import type { Recomendacion } from "@/lib/recomendar";

type Nivel = "bajo" | "medio" | "lleno";

const NIVELES: { valor: Nivel; etiqueta: string; ayuda: string }[] = [
  { valor: "bajo", etiqueta: "Bajo", ayuda: "¼ o menos" },
  { valor: "medio", etiqueta: "Medio", ayuda: "alrededor de ½" },
  { valor: "lleno", etiqueta: "Lleno", ayuda: "¾ o más" },
];

const nombreBonito = (d: string) => d.toLowerCase().replace(/(^|\s)\S/g, (c) => c.toUpperCase());

const TENDENCIA_TEXTO: Record<string, string> = {
  SUBE: "Sube",
  BAJA: "Baja",
  MANTIENE: "Se mantiene",
};

export default function Asistente({ departamentos }: { departamentos: string[] }) {
  const [departamento, setDepartamento] = useState("LIMA");
  const [nivel, setNivel] = useState<Nivel | null>(null);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [resultado, setResultado] = useState<Recomendacion | null>(null);

  async function consultar() {
    if (!nivel) {
      setError("Elige cómo está tu tanque para darte una recomendación.");
      return;
    }
    setCargando(true);
    setError(null);
    setResultado(null);
    try {
      const resp = await fetch("/api/recomendar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ departamento, nivel_tanque: nivel }),
      });
      const datos = await resp.json();
      if (!resp.ok) throw new Error(datos.error ?? "Algo salió mal.");
      setResultado(datos as Recomendacion);
    } catch (e) {
      setError(
        e instanceof TypeError
          ? "No hay conexión. Revisa tu internet e inténtalo otra vez."
          : (e as Error).message,
      );
    } finally {
      setCargando(false);
    }
  }

  return (
    <section className="tarjeta">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          consultar();
        }}
      >
        <label className="campo">
          <span className="campo__etiqueta">¿Dónde cargas?</span>
          <select
            value={departamento}
            onChange={(e) => {
              setDepartamento(e.target.value);
              setResultado(null);
            }}
          >
            {departamentos.map((d) => (
              <option key={d} value={d}>
                {d === "LIMA" ? "Lima Metropolitana" : nombreBonito(d)}
              </option>
            ))}
          </select>
        </label>

        <fieldset className="campo">
          <legend className="campo__etiqueta">¿Cómo está tu tanque?</legend>
          <div className="niveles">
            {NIVELES.map((n) => (
              <button
                type="button"
                key={n.valor}
                className={`nivel ${nivel === n.valor ? "nivel--activo" : ""}`}
                aria-pressed={nivel === n.valor}
                onClick={() => {
                  setNivel(n.valor);
                  setResultado(null);
                  setError(null);
                }}
              >
                <span className={`medidor medidor--${n.valor}`} aria-hidden />
                <span className="nivel__etiqueta">{n.etiqueta}</span>
                <span className="nivel__ayuda">{n.ayuda}</span>
              </button>
            ))}
          </div>
        </fieldset>

        <button className="boton" type="submit" disabled={cargando}>
          {cargando ? "Calculando…" : "¿Lleno hoy o espero?"}
        </button>
        {error && (
          <p className="error" role="alert">
            {error}
          </p>
        )}
      </form>

      {resultado && <Resultado r={resultado} />}
    </section>
  );
}

function Resultado({ r }: { r: Recomendacion }) {
  const p = r.payload;
  const rango = p.p90_mercado - p.p10_mercado || 1;
  const posicion = (v: number) =>
    `${Math.min(100, Math.max(0, ((v - p.p10_mercado) / rango) * 100))}%`;
  return (
    <div className="resultado" aria-live="polite">
      <div className={`veredicto veredicto--${r.tono}`}>
        <p className="veredicto__titular">{r.titular}</p>
        <p className="veredicto__detalle">{r.detalle}</p>
      </div>

      <div className="banda">
        <p className="banda__titulo">Precio justo por galón · {p.combustible}</p>
        <div className="banda__barra">
          <span className="banda__marca" style={{ left: posicion(p.p50_mediana) }} />
        </div>
        <div className="banda__valores">
          <span>
            <strong>S/ {p.p10_mercado.toFixed(2)}</strong>
            <small>buen precio</small>
          </span>
          <span className="centro">
            <strong>S/ {p.p50_mediana.toFixed(2)}</strong>
            <small>precio típico</small>
          </span>
          <span className="derecha">
            <strong>S/ {p.p90_mercado.toFixed(2)}</strong>
            <small>no pagues más</small>
          </span>
        </div>
        <p className="banda__nota">
          Elegir bien el grifo puede ahorrarte hasta{" "}
          <strong>S/ {r.mercado.ahorro_por_tanqueada.toFixed(2)}</strong> en una tanqueada de 8
          galones.
        </p>
      </div>

      <div className="mensaje">
        <p className="mensaje__autor">
          <span aria-hidden>✦</span> Lunetra IA te explica
        </p>
        {r.texto.split(/\n\s*\n/).map((parrafo, i) => (
          <p key={i}>{parrafo}</p>
        ))}
      </div>

      <details className="detalles">
        <summary>¿Cómo se calculó?</summary>
        <ul>
          <li>
            Tendencia proyectada para {p.periodo.replace(" (t+1)", "")}:{" "}
            <strong>{TENDENCIA_TEXTO[p.tendencia_predicha]}</strong> (confianza{" "}
            {p.confianza.toLowerCase()}).
          </li>
          <li>
            Probabilidades del modelo: sube {(r.probabilidades.SUBE * 100).toFixed(0)}%, se
            mantiene {(r.probabilidades.MANTIENE * 100).toFixed(0)}%, baja{" "}
            {(r.probabilidades.BAJA * 100).toFixed(0)}%.
          </li>
          <li>
            Avisamos que sube desde un {Math.round(r.umbral_aplicado * 100)}% de probabilidad:
            no avisar una subida te cuesta 5 veces más que una falsa alarma.
          </li>
          <li>
            Datos: precios oficiales de Osinergmin hasta {r.mes_base.slice(0, 7)}.{" "}
            {r.mercado.n_estaciones > 0
              ? `Banda calculada sobre ${r.mercado.n_estaciones.toLocaleString("es-PE")} grifos.`
              : "Banda calculada con los últimos 12 meses del departamento."}
          </li>
          <li>
            Texto redactado por{" "}
            {r.fuente_texto === "respaldo_determinista"
              ? "la plantilla verificada de respaldo"
              : "Gemini (IA generativa)"}{" "}
            y auditado: {r.auditoria.cumple_contrato ? "sin cifras inventadas ✔" : "revisar ✖"}.
          </li>
        </ul>
      </details>
    </div>
  );
}
